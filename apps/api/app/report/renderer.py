import logging
import uuid
from datetime import datetime
from pathlib import Path

import markdown as md
from jinja2 import Template
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.report import Report, ReportSection
from app.report.planner import validate_template_id

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
STORAGE_DIR = Path("./storage/reports")


async def render_pdf(report_id: str, db: AsyncSession) -> str:
    """Render report sections into PDF (or HTML fallback).

    Args:
        report_id: UUID of the report.
        db: Database session.

    Returns:
        Path to the generated file (PDF or HTML).
    """
    # Get report
    result = await db.execute(
        select(Report).where(Report.id == uuid.UUID(report_id))
    )
    report = result.scalar_one_or_none()
    if not report:
        raise ValueError(f"Report {report_id} not found")

    template_id = report.template_id or "business_report_v1"
    validate_template_id(template_id)
    template_dir = TEMPLATE_DIR / template_id

    # Load template files
    layout_path = template_dir / "layout.html.j2"
    styles_path = template_dir / "styles.css"

    with open(layout_path) as f:
        layout_template = Template(f.read())
    with open(styles_path) as f:
        styles_css = f.read()

    # Get all sections ordered
    sections_result = await db.execute(
        select(ReportSection)
        .where(ReportSection.report_id == uuid.UUID(report_id))
        .order_by(ReportSection.section_order)
    )
    sections = sections_result.scalars().all()

    # Build chapters data for template
    chapters_data: list[dict] = []
    current_chapter: dict | None = None

    for section in sections:
        if (
            current_chapter is None
            or current_chapter["number"] != section.chapter_number
        ):
            current_chapter = {
                "number": section.chapter_number,
                "title": section.chapter_title,
                "sections": [],
            }
            chapters_data.append(current_chapter)

        # Convert markdown to HTML
        content_html = ""
        if section.content_markdown:
            content_html = md.markdown(
                section.content_markdown,
                extensions=["tables", "fenced_code"],
            )

        current_chapter["sections"].append(
            {
                "title": section.section_title,
                "content_html": content_html,
            }
        )

    # Render full HTML
    html_content = layout_template.render(
        title=report.title,
        subtitle=report.subtitle,
        author=report.author,
        date=datetime.now().strftime("%d %B %Y"),
        chapters=chapters_data,
        styles_css=styles_css,
    )

    # Ensure storage directory exists
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    # Try WeasyPrint for PDF generation
    try:
        from weasyprint import HTML

        output_path = STORAGE_DIR / f"{report_id}.pdf"
        HTML(string=html_content).write_pdf(str(output_path))
        logger.info(f"PDF generated: {output_path}")
        return str(output_path)
    except ImportError:
        logger.warning("WeasyPrint not available, falling back to HTML output")
    except Exception as e:
        logger.warning(f"WeasyPrint failed: {e}, falling back to HTML output")

    # Fallback: save as HTML
    output_path = STORAGE_DIR / f"{report_id}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"HTML generated (fallback): {output_path}")
    return str(output_path)
