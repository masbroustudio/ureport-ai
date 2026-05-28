import asyncio
import json
import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.model.report import Report, ReportSection
from app.model.user import User
from app.report.planner import plan_report_outline
from app.report.renderer import STORAGE_DIR, render_pdf
from app.report.writer import write_section
from app.schema.report import (
    OutlineUpdate,
    ReportCreate,
    ReportListResponse,
    ReportResponse,
    SectionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    body: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new report and generate outline using LLM planner."""
    # Create report record
    report = Report(
        user_id=current_user.id,
        title=body.title,
        template_id=body.template_id,
        status="planning",
        conversation_id=uuid.UUID(body.conversation_id) if body.conversation_id else None,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    # Plan the outline
    try:
        # Build user_request from title and custom_instructions
        user_request = body.title
        if body.custom_instructions:
            user_request = f"{body.title}\n\nAdditional instructions: {body.custom_instructions}"

        outline = await plan_report_outline(
            user_request=user_request,
            file_profiles=None,  # TODO: Resolve file_ids to file profiles in a future iteration
            kb_doc_summaries=None,  # TODO: Resolve kb_document_ids to document summaries in a future iteration
            template_id=body.template_id,
        )

        report.outline_json = outline
        report.status = "created"

        # Create section records from outline
        section_order = 0
        for chapter in outline.get("chapters", []):
            for section in chapter.get("sections", []):
                db_section = ReportSection(
                    report_id=report.id,
                    chapter_number=chapter["number"],
                    chapter_title=chapter["title"],
                    section_order=section_order,
                    section_title=section["title"],
                    status="pending",
                )
                db.add(db_section)
                section_order += 1

        await db.commit()
        await db.refresh(report)

    except Exception as e:
        logger.error(f"Failed to plan report outline: {e}", exc_info=True)
        report.status = "failed"
        report.error_message = "Report planning failed. Please try again."
        await db.commit()
        await db.refresh(report)

    return ReportResponse.model_validate(report)


@router.get("/", response_model=list[ReportListResponse])
async def list_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all reports for the current user."""
    result = await db.execute(
        select(Report)
        .where(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
    )
    reports = result.scalars().all()
    return [ReportListResponse.model_validate(r) for r in reports]


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get report detail with outline."""
    result = await db.execute(
        select(Report).where(
            Report.id == report_id,
            Report.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )
    return ReportResponse.model_validate(report)


@router.put("/{report_id}/outline", response_model=ReportResponse)
async def update_outline(
    report_id: uuid.UUID,
    body: OutlineUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the report outline."""
    result = await db.execute(
        select(Report).where(
            Report.id == report_id,
            Report.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    report.outline_json = body.outline_json

    # Recreate sections from new outline
    await db.execute(
        delete(ReportSection).where(ReportSection.report_id == report_id)
    )

    section_order = 0
    for chapter in body.outline_json.get("chapters", []):
        for section in chapter.get("sections", []):
            db_section = ReportSection(
                report_id=report.id,
                chapter_number=chapter["number"],
                chapter_title=chapter["title"],
                section_order=section_order,
                section_title=section["title"],
                status="pending",
            )
            db.add(db_section)
            section_order += 1

    await db.commit()
    await db.refresh(report)
    return ReportResponse.model_validate(report)


@router.post("/{report_id}/start")
async def start_report_generation(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start report generation with SSE streaming progress."""

    result = await db.execute(
        select(Report).where(
            Report.id == report_id,
            Report.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    if not report.outline_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report has no outline. Create outline first.",
        )

    if report.status != "created":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Report generation cannot start: report is already in '{report.status}' state.",
        )

    async def event_stream():
        nonlocal report

        try:
            # Set status to writing
            report.status = "writing"
            report.progress_pct = 0
            await db.commit()

            outline = report.outline_json
            sections_result = await db.execute(
                select(ReportSection)
                .where(ReportSection.report_id == report_id)
                .order_by(ReportSection.section_order)
            )
            db_sections = sections_result.scalars().all()
            total_sections = len(db_sections)

            # Build section info map from outline
            section_info_map: dict[int, tuple[dict, dict]] = {}
            order = 0
            for chapter in outline.get("chapters", []):
                for section in chapter.get("sections", []):
                    section_info_map[order] = (section, chapter)
                    order += 1

            completed = 0
            for db_section in db_sections:
                info = section_info_map.get(db_section.section_order)
                if not info:
                    completed += 1
                    continue

                section_data, chapter_data = info

                db_section.status = "writing"
                await db.commit()

                try:
                    report_context = {
                        "report_title": report.title,
                        "chapter_title": chapter_data.get("title", ""),
                    }

                    if section_data.get("use_rag"):
                        try:
                            from app.rag.retriever import retrieve

                            results = await retrieve(
                                user_id=str(current_user.id),
                                query=f"{chapter_data.get('title', '')} {section_data['title']}",
                                top_k=5,
                            )
                            if results:
                                materials = "\n---\n".join([r.text for r in results])
                                report_context["materials"] = materials
                        except Exception as e:
                            logger.warning(f"RAG retrieval failed: {e}")

                    content = await write_section(section_data, report_context)

                    db_section.content_markdown = content
                    db_section.word_count = len(content.split())
                    db_section.status = "done"

                except Exception as e:
                    logger.error(f"Failed to write section {db_section.id}: {e}")
                    db_section.status = "failed"

                completed += 1
                pct = int((completed / total_sections) * 90)
                report.progress_pct = pct
                await db.commit()

                # Yield progress event
                progress_data = json.dumps({
                    "section": db_section.section_title,
                    "completed": completed,
                    "total": total_sections,
                    "pct": pct,
                })
                yield f"event: progress\ndata: {progress_data}\n\n"

                # Small delay to avoid overwhelming the client
                await asyncio.sleep(0.1)

            # Render phase
            yield f"event: render\ndata: {json.dumps({'message': 'Rendering PDF...'})}\n\n"

            try:
                report.status = "rendering"
                await db.commit()

                output_path = await render_pdf(str(report_id), db)

                report.pdf_path = output_path
                report.status = "done"
                report.progress_pct = 100
                await db.commit()

                done_data = json.dumps({
                    "report_id": str(report_id),
                    "pdf_path": output_path,
                    "total_sections": total_sections,
                })
                yield f"event: done\ndata: {done_data}\n\n"

            except Exception as e:
                logger.error(f"Rendering failed: {e}")
                report.status = "failed"
                report.error_message = f"Rendering failed: {e}"
                await db.commit()

                error_data = json.dumps({"error": str(e)})
                yield f"event: error\ndata: {error_data}\n\n"

        finally:
            # If client disconnects or an unhandled error occurs while the report
            # is still in an intermediate state, mark it as failed.
            if report.status in ("writing", "rendering"):
                report.status = "failed"
                report.error_message = "Report generation was interrupted."
                try:
                    await db.commit()
                except Exception:
                    logger.warning("Failed to commit zombie report cleanup")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )


@router.get("/{report_id}/sections", response_model=list[SectionResponse])
async def list_sections(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all sections for a report."""
    # Verify report ownership
    result = await db.execute(
        select(Report).where(
            Report.id == report_id,
            Report.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    sections_result = await db.execute(
        select(ReportSection)
        .where(ReportSection.report_id == report_id)
        .order_by(ReportSection.section_order)
    )
    sections = sections_result.scalars().all()
    return [SectionResponse.model_validate(s) for s in sections]


@router.post(
    "/{report_id}/sections/{section_id}/regenerate",
    response_model=SectionResponse,
)
async def regenerate_section(
    report_id: uuid.UUID,
    section_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Regenerate a single section's content."""
    # Verify report ownership
    result = await db.execute(
        select(Report).where(
            Report.id == report_id,
            Report.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    # Get section
    section_result = await db.execute(
        select(ReportSection).where(
            ReportSection.id == section_id,
            ReportSection.report_id == report_id,
        )
    )
    db_section = section_result.scalar_one_or_none()
    if not db_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Section not found"
        )

    # Find section info from outline
    outline = report.outline_json or {}
    section_data = {"title": db_section.section_title, "instruction": "", "target_words": 300}

    order = 0
    for chapter in outline.get("chapters", []):
        for section in chapter.get("sections", []):
            if order == db_section.section_order:
                section_data = section
                break
            order += 1

    report_context = {
        "report_title": report.title,
        "chapter_title": db_section.chapter_title,
    }

    try:
        db_section.status = "writing"
        await db.commit()

        content = await write_section(section_data, report_context)
        db_section.content_markdown = content
        db_section.word_count = len(content.split())
        db_section.status = "done"
        await db.commit()
        await db.refresh(db_section)
    except Exception as e:
        db_section.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate section: {e}",
        )

    return SectionResponse.model_validate(db_section)


@router.get("/{report_id}/pdf")
async def download_pdf(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download the generated PDF/HTML file."""
    result = await db.execute(
        select(Report).where(
            Report.id == report_id,
            Report.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    if not report.pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not generated yet",
        )

    # Validate that the resolved path is within STORAGE_DIR to prevent path traversal
    resolved_path = Path(report.pdf_path).resolve()
    storage_dir_resolved = STORAGE_DIR.resolve()
    if not str(resolved_path).startswith(str(storage_dir_resolved)):
        logger.error(
            f"Path traversal attempt detected: {report.pdf_path} resolves outside STORAGE_DIR"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    if not os.path.exists(report.pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found on disk",
        )

    # Determine media type
    if report.pdf_path.endswith(".pdf"):
        media_type = "application/pdf"
        filename = f"{report.title}.pdf"
    else:
        media_type = "text/html"
        filename = f"{report.title}.html"

    return FileResponse(
        path=report.pdf_path,
        media_type=media_type,
        filename=filename,
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a report, its sections, and generated file."""
    result = await db.execute(
        select(Report).where(
            Report.id == report_id,
            Report.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    # Delete PDF file if exists
    if report.pdf_path and os.path.exists(report.pdf_path):
        try:
            os.remove(report.pdf_path)
        except OSError as e:
            logger.warning(f"Failed to delete report file: {e}")

    # Delete sections
    await db.execute(
        delete(ReportSection).where(ReportSection.report_id == report_id)
    )

    # Delete report
    await db.delete(report)
    await db.commit()
