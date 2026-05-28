import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.report.renderer import render_pdf


def _make_report_mock(report_id: str, title: str = "Test Report"):
    """Create a mock Report object."""
    report = MagicMock()
    report.id = uuid.UUID(report_id)
    report.title = title
    report.subtitle = "Subtitle"
    report.author = "Test Author"
    report.template_id = "business_report_v1"
    return report


def _make_section_mock(
    report_id: str,
    chapter_number: str,
    chapter_title: str,
    section_order: int,
    section_title: str,
    content_markdown: str,
):
    """Create a mock ReportSection object."""
    section = MagicMock()
    section.id = uuid.uuid4()
    section.report_id = uuid.UUID(report_id)
    section.chapter_number = chapter_number
    section.chapter_title = chapter_title
    section.section_order = section_order
    section.section_title = section_title
    section.content_markdown = content_markdown
    section.status = "done"
    section.word_count = len(content_markdown.split()) if content_markdown else 0
    return section


@pytest.mark.asyncio
class TestRenderPdf:
    async def test_render_generates_html_fallback(self, tmp_path):
        """Test render_pdf generates an HTML file (fallback when weasyprint is unavailable)."""
        report_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        report = _make_report_mock(report_id)

        section1 = _make_section_mock(
            report_id=report_id,
            chapter_number="BAB I",
            chapter_title="Pendahuluan",
            section_order=0,
            section_title="Latar Belakang",
            content_markdown="## Background\n\nThis is the background section.",
        )
        section2 = _make_section_mock(
            report_id=report_id,
            chapter_number="BAB I",
            chapter_title="Pendahuluan",
            section_order=1,
            section_title="Tujuan",
            content_markdown="## Objectives\n\nThese are the objectives.",
        )
        section3 = _make_section_mock(
            report_id=report_id,
            chapter_number="BAB II",
            chapter_title="Pembahasan",
            section_order=2,
            section_title="Analisis",
            content_markdown="## Analysis\n\nData analysis results.",
        )

        # Mock DB session
        mock_db = AsyncMock()

        # First execute: get report
        report_result = MagicMock()
        report_result.scalar_one_or_none.return_value = report

        # Second execute: get sections
        sections_result = MagicMock()
        sections_result.scalars.return_value.all.return_value = [
            section1, section2, section3
        ]

        mock_db.execute = AsyncMock(
            side_effect=[report_result, sections_result]
        )

        # Patch STORAGE_DIR and make weasyprint import fail inside the function
        with patch("app.report.renderer.STORAGE_DIR", tmp_path):
            output_path = await render_pdf(report_id, mock_db)

        # Since weasyprint can't load (no pango), it will fall back to HTML
        assert output_path.endswith(".html")
        with open(output_path) as f:
            html_content = f.read()

        assert "Test Report" in html_content
        assert "Pendahuluan" in html_content
        assert "Pembahasan" in html_content
        assert "Background" in html_content
        assert "Objectives" in html_content
        assert "Analysis" in html_content

    async def test_render_report_not_found(self):
        """Test render_pdf raises ValueError when report doesn't exist."""
        report_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        mock_db = AsyncMock()

        report_result = MagicMock()
        report_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=report_result)

        with pytest.raises(ValueError, match="not found"):
            await render_pdf(report_id, mock_db)

    async def test_render_handles_empty_content(self, tmp_path):
        """Test render_pdf handles sections with no content markdown."""
        report_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        report = _make_report_mock(report_id)

        section = _make_section_mock(
            report_id=report_id,
            chapter_number="BAB I",
            chapter_title="Chapter One",
            section_order=0,
            section_title="Empty Section",
            content_markdown="",
        )

        mock_db = AsyncMock()

        report_result = MagicMock()
        report_result.scalar_one_or_none.return_value = report

        sections_result = MagicMock()
        sections_result.scalars.return_value.all.return_value = [section]

        mock_db.execute = AsyncMock(
            side_effect=[report_result, sections_result]
        )

        with patch("app.report.renderer.STORAGE_DIR", tmp_path):
            output_path = await render_pdf(report_id, mock_db)

        assert output_path.endswith(".html")
        with open(output_path) as f:
            html_content = f.read()
        assert "Test Report" in html_content
        assert "Chapter One" in html_content

    async def test_render_groups_sections_by_chapter(self, tmp_path):
        """Test render_pdf correctly groups sections into their chapters."""
        report_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        report = _make_report_mock(report_id)

        section1 = _make_section_mock(
            report_id=report_id,
            chapter_number="BAB I",
            chapter_title="Introduction",
            section_order=0,
            section_title="Overview",
            content_markdown="Overview content.",
        )
        section2 = _make_section_mock(
            report_id=report_id,
            chapter_number="BAB II",
            chapter_title="Methods",
            section_order=1,
            section_title="Approach",
            content_markdown="Methods approach content.",
        )

        mock_db = AsyncMock()

        report_result = MagicMock()
        report_result.scalar_one_or_none.return_value = report

        sections_result = MagicMock()
        sections_result.scalars.return_value.all.return_value = [section1, section2]

        mock_db.execute = AsyncMock(
            side_effect=[report_result, sections_result]
        )

        with patch("app.report.renderer.STORAGE_DIR", tmp_path):
            output_path = await render_pdf(report_id, mock_db)

        with open(output_path) as f:
            html_content = f.read()

        # Both chapters should appear
        assert "BAB I" in html_content
        assert "Introduction" in html_content
        assert "BAB II" in html_content
        assert "Methods" in html_content
        assert "Overview content" in html_content
        assert "Methods approach content" in html_content
