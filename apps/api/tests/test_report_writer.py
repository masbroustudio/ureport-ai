from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.report.writer import write_section


def _make_model_response(content: str):
    """Create a mock litellm ModelResponse with the given content."""
    response = MagicMock()
    choice = MagicMock()
    choice.message.content = content
    response.choices = [choice]
    return response


@pytest.mark.asyncio
class TestWriteSection:
    @patch("app.report.writer.litellm.acompletion", new_callable=AsyncMock)
    async def test_returns_markdown_content(self, mock_acompletion):
        """Test write_section returns the markdown string from LLM."""
        expected_content = "### Overview\n\nThis section covers the analysis."
        mock_acompletion.return_value = _make_model_response(expected_content)

        section = {
            "title": "Analisis Data",
            "instruction": "Analyze quarterly data",
            "target_words": 300,
        }
        report_context = {
            "report_title": "Q1 2025 Report",
            "chapter_title": "Pembahasan",
        }

        result = await write_section(section, report_context)

        assert result == expected_content
        mock_acompletion.assert_called_once()

    @patch("app.report.writer.litellm.acompletion", new_callable=AsyncMock)
    async def test_strips_whitespace_from_content(self, mock_acompletion):
        """Test that leading/trailing whitespace is stripped."""
        mock_acompletion.return_value = _make_model_response(
            "  \n\nSome content here\n\n  "
        )

        section = {
            "title": "Introduction",
            "instruction": "Write intro",
            "target_words": 200,
        }
        report_context = {
            "report_title": "Test",
            "chapter_title": "Chapter 1",
        }

        result = await write_section(section, report_context)
        assert result == "Some content here"

    @patch("app.report.writer.litellm.acompletion", new_callable=AsyncMock)
    async def test_includes_materials_in_prompt(self, mock_acompletion):
        """Test that RAG materials are passed to the LLM prompt."""
        mock_acompletion.return_value = _make_model_response("Content with references")

        section = {
            "title": "Literature Review",
            "instruction": "Review existing work",
            "target_words": 400,
        }
        report_context = {
            "report_title": "Research Report",
            "chapter_title": "Tinjauan Pustaka",
            "materials": "Reference doc 1 content\n---\nReference doc 2 content",
        }

        await write_section(section, report_context)

        call_args = mock_acompletion.call_args
        messages = call_args.kwargs["messages"]
        user_msg = messages[1]["content"]
        assert "Reference doc 1 content" in user_msg
        assert "Reference doc 2 content" in user_msg

    @patch("app.report.writer.litellm.acompletion", new_callable=AsyncMock)
    async def test_prompt_contains_section_info(self, mock_acompletion):
        """Test that section title, instruction, and context are in the prompt."""
        mock_acompletion.return_value = _make_model_response("Content")

        section = {
            "title": "Metodologi Penelitian",
            "instruction": "Describe the methodology used",
            "target_words": 350,
        }
        report_context = {
            "report_title": "Annual Report",
            "chapter_title": "Metodologi",
        }

        await write_section(section, report_context)

        call_args = mock_acompletion.call_args
        messages = call_args.kwargs["messages"]
        user_msg = messages[1]["content"]
        assert "Annual Report" in user_msg
        assert "Metodologi" in user_msg
        assert "Metodologi Penelitian" in user_msg
        assert "Describe the methodology used" in user_msg
        assert "350" in user_msg


@pytest.mark.asyncio
class TestWriteSectionWithRAG:
    @patch("app.report.writer.litellm.acompletion", new_callable=AsyncMock)
    async def test_use_rag_section_includes_materials(self, mock_acompletion):
        """Test that when materials are provided (from RAG), they appear in the prompt."""
        mock_acompletion.return_value = _make_model_response(
            "Content based on retrieved docs"
        )

        section = {
            "title": "Background",
            "instruction": "Write using retrieved documents",
            "use_rag": True,
            "target_words": 300,
        }
        # Simulating what the caller does when use_rag=True - passes retrieved materials
        report_context = {
            "report_title": "Test Report",
            "chapter_title": "Introduction",
            "materials": "Retrieved chunk 1: Important finding about X.\n---\nRetrieved chunk 2: Data shows Y.",
        }

        result = await write_section(section, report_context)

        assert result == "Content based on retrieved docs"
        call_args = mock_acompletion.call_args
        messages = call_args.kwargs["messages"]
        user_msg = messages[1]["content"]
        assert "Retrieved chunk 1" in user_msg
        assert "Retrieved chunk 2" in user_msg

    @patch("app.report.writer.litellm.acompletion", new_callable=AsyncMock)
    async def test_no_materials_does_not_include_reference_section(self, mock_acompletion):
        """Test that without materials, no reference section appears in prompt."""
        mock_acompletion.return_value = _make_model_response("Plain content")

        section = {
            "title": "Summary",
            "instruction": "Summarize",
            "target_words": 200,
        }
        report_context = {
            "report_title": "Test Report",
            "chapter_title": "Conclusion",
        }

        await write_section(section, report_context)

        call_args = mock_acompletion.call_args
        messages = call_args.kwargs["messages"]
        user_msg = messages[1]["content"]
        assert "Reference materials" not in user_msg
