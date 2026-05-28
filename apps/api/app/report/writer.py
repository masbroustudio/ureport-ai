import logging
import uuid

import litellm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.report import Report, ReportSection
from app.settings import settings

logger = logging.getLogger(__name__)

WRITER_SYSTEM_PROMPT = """You are a professional report writer. Write high-quality content for a specific section of a report.

Rules:
- Write in a professional, academic tone
- Use clear and concise language
- Structure content with appropriate subheadings (use ### for subsections)
- Include relevant analysis and insights
- Write in the language matching the section title (Indonesian if titles are Indonesian)
- Do not include the section title itself - it will be added automatically
- Return ONLY the markdown content, no extra commentary
"""


async def write_section(
    section: dict,
    report_context: dict,
) -> str:
    """Write content for a single report section using LLM.

    Args:
        section: Dict with id, title, instruction, use_rag, use_data, target_words.
        report_context: Dict with report_title, chapter_title, materials (RAG chunks).

    Returns:
        Markdown text content for the section.
    """
    prompt_parts = [
        f"Report title: {report_context.get('report_title', '')}",
        f"Chapter: {report_context.get('chapter_title', '')}",
        f"Section: {section['title']}",
        f"Instruction: {section.get('instruction', 'Write this section')}",
        f"Target word count: {section.get('target_words', 300)}",
    ]

    materials = report_context.get("materials")
    if materials:
        prompt_parts.append(f"\nReference materials:\n{materials}")

    user_prompt = "\n".join(prompt_parts)

    api_key = settings.CEREBRAS_API_KEY or None

    response = await litellm.acompletion(
        model="cerebras/llama-3.3-70b",
        messages=[
            {"role": "system", "content": WRITER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        api_key=api_key,
    )

    content = response.choices[0].message.content
    return content.strip()


async def write_full_report(
    report_id: str,
    outline: dict,
    db: AsyncSession,
    user_id: str,
) -> None:
    """Write all sections of a report, updating DB as each completes.

    Args:
        report_id: UUID of the report.
        outline: The outline dict with chapters and sections.
        db: Database session.
        user_id: UUID of the user (for RAG retrieval).
    """
    # Get the report
    result = await db.execute(
        select(Report).where(Report.id == uuid.UUID(report_id))
    )
    report = result.scalar_one_or_none()
    if not report:
        raise ValueError(f"Report {report_id} not found")

    # Get all sections ordered
    sections_result = await db.execute(
        select(ReportSection)
        .where(ReportSection.report_id == uuid.UUID(report_id))
        .order_by(ReportSection.section_order)
    )
    db_sections = sections_result.scalars().all()

    total_sections = len(db_sections)
    completed = 0

    chapters = outline.get("chapters", [])

    # Build a mapping from section order to outline section info
    section_info_map: dict[int, tuple[dict, dict]] = {}
    order = 0
    for chapter in chapters:
        for section in chapter.get("sections", []):
            section_info_map[order] = (section, chapter)
            order += 1

    for db_section in db_sections:
        info = section_info_map.get(db_section.section_order)
        if not info:
            continue

        section_data, chapter_data = info

        # Update section status to writing
        db_section.status = "writing"
        await db.commit()

        try:
            # Build context for writer
            report_context = {
                "report_title": report.title,
                "chapter_title": chapter_data.get("title", ""),
            }

            # Optionally retrieve RAG materials
            if section_data.get("use_rag"):
                try:
                    from app.rag.retriever import retrieve

                    results = await retrieve(
                        user_id=user_id,
                        query=f"{chapter_data.get('title', '')} {section_data['title']}",
                        top_k=5,
                    )
                    if results:
                        materials = "\n---\n".join(
                            [r.text for r in results]
                        )
                        report_context["materials"] = materials
                except Exception as e:
                    logger.warning(f"RAG retrieval failed for section: {e}")

            # Write the section
            content = await write_section(section_data, report_context)

            # Update DB
            db_section.content_markdown = content
            db_section.word_count = len(content.split())
            db_section.status = "done"

        except Exception as e:
            logger.error(f"Failed to write section {db_section.id}: {e}")
            db_section.status = "failed"
            db_section.content_markdown = None

        completed += 1
        # Update report progress
        report.progress_pct = int((completed / total_sections) * 90)
        await db.commit()

    # Final progress before rendering
    report.progress_pct = 90
    await db.commit()
