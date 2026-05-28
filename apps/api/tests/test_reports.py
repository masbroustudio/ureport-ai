import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


VALID_OUTLINE = {
    "chapters": [
        {
            "number": "BAB I",
            "title": "Pendahuluan",
            "sections": [
                {
                    "id": "1.1",
                    "title": "Latar Belakang",
                    "instruction": "Write background",
                    "use_rag": False,
                    "use_data": False,
                    "target_words": 300,
                }
            ],
        }
    ]
}


def _make_report_mock(
    report_id=None,
    user_id=None,
    title="Test Report",
    status="created",
    progress_pct=0,
):
    """Create a mock Report object."""
    report = MagicMock()
    report.id = report_id or uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
    report.user_id = user_id or uuid.UUID("12345678-1234-5678-1234-567812345678")
    report.conversation_id = None
    report.title = title
    report.subtitle = None
    report.author = None
    report.template_id = "business_report_v1"
    report.outline_json = VALID_OUTLINE
    report.status = status
    report.progress_pct = progress_pct
    report.error_message = None
    report.pdf_path = None
    report.created_at = datetime(2025, 1, 15, tzinfo=timezone.utc)
    report.updated_at = datetime(2025, 1, 15, tzinfo=timezone.utc)
    return report


def _make_section_mock(
    report_id=None,
    section_order=0,
    chapter_number="BAB I",
    chapter_title="Pendahuluan",
    section_title="Latar Belakang",
    status="pending",
    content_markdown=None,
):
    """Create a mock ReportSection object."""
    section = MagicMock()
    section.id = uuid.uuid4()
    section.report_id = report_id or uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
    section.chapter_number = chapter_number
    section.chapter_title = chapter_title
    section.section_order = section_order
    section.section_title = section_title
    section.content_markdown = content_markdown
    section.status = status
    section.word_count = len(content_markdown.split()) if content_markdown else 0
    section.created_at = datetime(2025, 1, 15, tzinfo=timezone.utc)
    section.updated_at = datetime(2025, 1, 15, tzinfo=timezone.utc)
    return section


@pytest.mark.asyncio
class TestCreateReport:
    @patch("app.router.reports.plan_report_outline", new_callable=AsyncMock)
    async def test_create_report_success(self, mock_planner, client, mock_db):
        """Test POST /api/v1/reports returns 201 with valid outline."""
        mock_planner.return_value = VALID_OUTLINE

        report_id = uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")

        mock_db.commit = AsyncMock()

        call_count = [0]

        async def fake_refresh(obj):
            call_count[0] += 1
            # First refresh is after initial commit, second after outline commit
            obj.id = report_id
            obj.user_id = user_id
            obj.conversation_id = None
            obj.title = "Sales Report Q1"
            obj.subtitle = None
            obj.author = None
            obj.template_id = "business_report_v1"
            obj.outline_json = VALID_OUTLINE
            obj.status = "created"
            obj.progress_pct = 0
            obj.error_message = None
            obj.pdf_path = None
            obj.created_at = datetime(2025, 1, 15, tzinfo=timezone.utc)
            obj.updated_at = datetime(2025, 1, 15, tzinfo=timezone.utc)

        mock_db.refresh = AsyncMock(side_effect=fake_refresh)

        response = await client.post(
            "/api/v1/reports/",
            json={"title": "Sales Report Q1", "template_id": "business_report_v1"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Sales Report Q1"
        assert data["status"] == "created"
        assert data["outline_json"] == VALID_OUTLINE
        mock_planner.assert_called_once()

    @patch("app.router.reports.plan_report_outline", new_callable=AsyncMock)
    async def test_create_report_planner_fails(self, mock_planner, client, mock_db):
        """Test POST /api/v1/reports handles planner failure gracefully."""
        mock_planner.side_effect = ValueError("LLM returned invalid JSON")

        report_id = uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")

        mock_db.commit = AsyncMock()

        async def fake_refresh(obj):
            obj.id = report_id
            obj.user_id = user_id
            obj.conversation_id = None
            obj.title = "Bad Report"
            obj.subtitle = None
            obj.author = None
            obj.template_id = "business_report_v1"
            obj.outline_json = None
            obj.status = "failed"
            obj.progress_pct = 0
            obj.error_message = "Report planning failed. Please try again."
            obj.pdf_path = None
            obj.created_at = datetime(2025, 1, 15, tzinfo=timezone.utc)
            obj.updated_at = datetime(2025, 1, 15, tzinfo=timezone.utc)

        mock_db.refresh = AsyncMock(side_effect=fake_refresh)

        response = await client.post(
            "/api/v1/reports/",
            json={"title": "Bad Report"},
        )

        # The endpoint still returns 201 but with "failed" status
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "failed"
        assert data["error_message"] == "Report planning failed. Please try again."


@pytest.mark.asyncio
class TestListReports:
    async def test_list_reports_empty(self, client, mock_db):
        """Test GET /api/v1/reports returns empty list."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get("/api/v1/reports/")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_reports_with_items(self, client, mock_db):
        """Test GET /api/v1/reports returns list of reports."""
        report1 = _make_report_mock(title="Report One", status="done")
        report2 = _make_report_mock(
            report_id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            title="Report Two",
            status="created",
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [report1, report2]
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get("/api/v1/reports/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Report One"
        assert data[0]["status"] == "done"
        assert data[1]["title"] == "Report Two"


@pytest.mark.asyncio
class TestGetReport:
    async def test_get_report_found(self, client, mock_db):
        """Test GET /api/v1/reports/{id} returns report details."""
        report = _make_report_mock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = report
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get(
            f"/api/v1/reports/{report.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Report"
        assert data["outline_json"] == VALID_OUTLINE
        assert data["status"] == "created"

    async def test_get_report_not_found(self, client, mock_db):
        """Test GET /api/v1/reports/{id} returns 404 when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get(
            f"/api/v1/reports/{uuid.uuid4()}"
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestUpdateOutline:
    async def test_update_outline_success(self, client, mock_db):
        """Test PUT /api/v1/reports/{id}/outline updates the outline."""
        report = _make_report_mock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = report
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        new_outline = {
            "chapters": [
                {
                    "number": "BAB I",
                    "title": "Updated Chapter",
                    "sections": [
                        {
                            "id": "1.1",
                            "title": "New Section",
                            "instruction": "Updated instruction",
                            "use_rag": False,
                            "target_words": 200,
                        }
                    ],
                }
            ]
        }

        async def fake_refresh(obj):
            obj.id = report.id
            obj.user_id = report.user_id
            obj.conversation_id = None
            obj.title = report.title
            obj.subtitle = None
            obj.author = None
            obj.template_id = "business_report_v1"
            obj.outline_json = new_outline
            obj.status = "created"
            obj.progress_pct = 0
            obj.error_message = None
            obj.pdf_path = None
            obj.created_at = report.created_at
            obj.updated_at = report.updated_at

        mock_db.refresh = AsyncMock(side_effect=fake_refresh)

        response = await client.put(
            f"/api/v1/reports/{report.id}/outline",
            json={"outline_json": new_outline},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["outline_json"]["chapters"][0]["title"] == "Updated Chapter"

    async def test_update_outline_not_found(self, client, mock_db):
        """Test PUT /api/v1/reports/{id}/outline returns 404."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.put(
            f"/api/v1/reports/{uuid.uuid4()}/outline",
            json={"outline_json": {"chapters": []}},
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestDeleteReport:
    async def test_delete_report_success(self, client, mock_db):
        """Test DELETE /api/v1/reports/{id} returns 204."""
        report = _make_report_mock()
        report.pdf_path = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = report
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        response = await client.delete(
            f"/api/v1/reports/{report.id}"
        )
        assert response.status_code == 204

    async def test_delete_report_not_found(self, client, mock_db):
        """Test DELETE /api/v1/reports/{id} returns 404 when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.delete(
            f"/api/v1/reports/{uuid.uuid4()}"
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestListSections:
    async def test_list_sections_success(self, client, mock_db):
        """Test GET /api/v1/reports/{id}/sections returns section list."""
        report = _make_report_mock()
        section1 = _make_section_mock(section_order=0, section_title="Section A")
        section2 = _make_section_mock(
            section_order=1,
            section_title="Section B",
            status="done",
            content_markdown="Some content",
        )

        # First execute: verify report ownership
        report_result = MagicMock()
        report_result.scalar_one_or_none.return_value = report

        # Second execute: get sections
        sections_result = MagicMock()
        sections_result.scalars.return_value.all.return_value = [section1, section2]

        mock_db.execute = AsyncMock(
            side_effect=[report_result, sections_result]
        )

        response = await client.get(
            f"/api/v1/reports/{report.id}/sections"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["section_title"] == "Section A"
        assert data[0]["status"] == "pending"
        assert data[1]["section_title"] == "Section B"
        assert data[1]["status"] == "done"
        assert data[1]["content_markdown"] == "Some content"

    async def test_list_sections_report_not_found(self, client, mock_db):
        """Test GET /api/v1/reports/{id}/sections returns 404."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get(
            f"/api/v1/reports/{uuid.uuid4()}/sections"
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestStartReport:
    async def test_start_report_no_outline(self, client, mock_db):
        """Test POST /api/v1/reports/{id}/start returns 400 when no outline."""
        report = _make_report_mock(status="created")
        report.outline_json = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = report
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.post(
            f"/api/v1/reports/{report.id}/start"
        )
        assert response.status_code == 400
        assert "no outline" in response.json()["detail"].lower()

    async def test_start_report_wrong_status(self, client, mock_db):
        """Test POST /api/v1/reports/{id}/start returns 409 when already writing."""
        report = _make_report_mock(status="writing")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = report
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.post(
            f"/api/v1/reports/{report.id}/start"
        )
        assert response.status_code == 409


@pytest.mark.asyncio
class TestDownloadPdf:
    async def test_download_pdf_no_file(self, client, mock_db):
        """Test GET /api/v1/reports/{id}/pdf returns 404 when pdf_path is None."""
        report = _make_report_mock(status="done")
        report.pdf_path = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = report
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get(
            f"/api/v1/reports/{report.id}/pdf"
        )
        assert response.status_code == 404
        assert "not generated" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestRegenerateSection:
    @patch("app.router.reports.write_section", new_callable=AsyncMock)
    async def test_regenerate_section_not_found(self, mock_write, client, mock_db):
        """Test POST /regenerate returns 404 when section doesn't exist."""
        report = _make_report_mock(status="done")

        # First execute: report ownership
        report_result = MagicMock()
        report_result.scalar_one_or_none.return_value = report

        # Second execute: section lookup returns None
        section_result = MagicMock()
        section_result.scalar_one_or_none.return_value = None

        mock_db.execute = AsyncMock(
            side_effect=[report_result, section_result]
        )

        bad_section_id = uuid.uuid4()
        response = await client.post(
            f"/api/v1/reports/{report.id}/sections/{bad_section_id}/regenerate"
        )
        assert response.status_code == 404
        assert "section not found" in response.json()["detail"].lower()
