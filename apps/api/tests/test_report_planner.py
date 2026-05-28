import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.report.planner import plan_report_outline


def _make_model_response(content: str):
    """Create a mock litellm ModelResponse with the given content."""
    response = MagicMock()
    choice = MagicMock()
    choice.message.content = content
    response.choices = [choice]
    return response


VALID_OUTLINE = {
    "chapters": [
        {
            "number": "BAB I",
            "title": "Pendahuluan",
            "sections": [
                {
                    "id": "1.1",
                    "title": "Latar Belakang",
                    "instruction": "Write background section",
                    "use_rag": False,
                    "use_data": False,
                    "target_words": 300,
                },
                {
                    "id": "1.2",
                    "title": "Tujuan",
                    "instruction": "Write objectives section",
                    "use_rag": True,
                    "use_data": False,
                    "target_words": 200,
                },
            ],
        },
        {
            "number": "BAB II",
            "title": "Pembahasan",
            "sections": [
                {
                    "id": "2.1",
                    "title": "Analisis Data",
                    "instruction": "Analyze the data",
                    "use_rag": False,
                    "use_data": True,
                    "target_words": 500,
                },
            ],
        },
    ]
}


@pytest.mark.asyncio
class TestPlanReportOutline:
    @patch("app.report.planner.litellm.acompletion", new_callable=AsyncMock)
    async def test_returns_valid_outline(self, mock_acompletion):
        """Test that plan_report_outline returns proper structure with chapters and sections."""
        mock_acompletion.return_value = _make_model_response(
            json.dumps(VALID_OUTLINE)
        )

        result = await plan_report_outline(
            user_request="Laporan penjualan Q1 2025",
            file_profiles=None,
            kb_doc_summaries=None,
            template_id="business_report_v1",
        )

        assert "chapters" in result
        assert len(result["chapters"]) == 2
        assert result["chapters"][0]["number"] == "BAB I"
        assert result["chapters"][0]["title"] == "Pendahuluan"
        assert len(result["chapters"][0]["sections"]) == 2
        assert result["chapters"][0]["sections"][0]["title"] == "Latar Belakang"
        assert result["chapters"][0]["sections"][1]["use_rag"] is True
        assert result["chapters"][1]["sections"][0]["use_data"] is True

    @patch("app.report.planner.litellm.acompletion", new_callable=AsyncMock)
    async def test_strips_markdown_code_fences(self, mock_acompletion):
        """Test that markdown code fences around JSON are stripped."""
        content_with_fences = f"```json\n{json.dumps(VALID_OUTLINE)}\n```"
        mock_acompletion.return_value = _make_model_response(content_with_fences)

        result = await plan_report_outline(
            user_request="Test report",
            file_profiles=None,
            kb_doc_summaries=None,
            template_id="business_report_v1",
        )

        assert "chapters" in result
        assert len(result["chapters"]) == 2

    @patch("app.report.planner.litellm.acompletion", new_callable=AsyncMock)
    async def test_sets_defaults_for_optional_fields(self, mock_acompletion):
        """Test that optional section fields get defaults if not present."""
        outline_minimal = {
            "chapters": [
                {
                    "number": "BAB I",
                    "title": "Introduction",
                    "sections": [
                        {
                            "id": "1.1",
                            "title": "Background",
                            "instruction": "Write intro",
                        }
                    ],
                }
            ]
        }
        mock_acompletion.return_value = _make_model_response(
            json.dumps(outline_minimal)
        )

        result = await plan_report_outline(
            user_request="Test report",
            file_profiles=None,
            kb_doc_summaries=None,
            template_id="business_report_v1",
        )

        section = result["chapters"][0]["sections"][0]
        assert section["use_rag"] is False
        assert section["use_data"] is False
        assert section["target_words"] == 300

    @patch("app.report.planner.litellm.acompletion", new_callable=AsyncMock)
    async def test_invalid_json_raises_error(self, mock_acompletion):
        """Test that invalid JSON from LLM raises an error."""
        mock_acompletion.return_value = _make_model_response(
            "This is not valid JSON at all"
        )

        with pytest.raises(json.JSONDecodeError):
            await plan_report_outline(
                user_request="Test report",
                file_profiles=None,
                kb_doc_summaries=None,
                template_id="business_report_v1",
            )

    @patch("app.report.planner.litellm.acompletion", new_callable=AsyncMock)
    async def test_missing_chapters_key_raises_error(self, mock_acompletion):
        """Test that JSON without 'chapters' key raises ValueError."""
        mock_acompletion.return_value = _make_model_response(
            json.dumps({"sections": []})
        )

        with pytest.raises(ValueError, match="must contain 'chapters' key"):
            await plan_report_outline(
                user_request="Test report",
                file_profiles=None,
                kb_doc_summaries=None,
                template_id="business_report_v1",
            )

    @patch("app.report.planner.litellm.acompletion", new_callable=AsyncMock)
    async def test_passes_file_profiles_and_kb_summaries(self, mock_acompletion):
        """Test that file_profiles and kb_doc_summaries are included in the prompt."""
        mock_acompletion.return_value = _make_model_response(
            json.dumps(VALID_OUTLINE)
        )

        await plan_report_outline(
            user_request="Report about sales",
            file_profiles=[{"name": "sales.xlsx", "rows": 100}],
            kb_doc_summaries=[{"title": "Company Policy", "summary": "..."}],
            template_id="business_report_v1",
        )

        # Verify the LLM was called with a prompt containing file info
        call_args = mock_acompletion.call_args
        messages = call_args.kwargs["messages"]
        user_msg = messages[1]["content"]
        assert "sales.xlsx" in user_msg
        assert "Company Policy" in user_msg

    async def test_invalid_template_id_raises_error(self):
        """Test that a template_id with path traversal chars raises ValueError."""
        from app.report.planner import validate_template_id

        with pytest.raises(ValueError, match="Invalid template_id"):
            validate_template_id("../../etc")

        with pytest.raises(ValueError, match="Invalid template_id"):
            validate_template_id("../passwd")

        with pytest.raises(ValueError, match="Invalid template_id"):
            validate_template_id("template/../../secret")

        # Valid template_ids should not raise
        validate_template_id("business_report_v1")
        validate_template_id("my-template-2")
