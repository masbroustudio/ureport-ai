import json
import logging
import re
from pathlib import Path

import litellm
import yaml

from app.settings import settings

logger = logging.getLogger(__name__)

# Regex for valid template_id: only alphanumeric, underscore, hyphen
TEMPLATE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

PLANNER_SYSTEM_PROMPT = """You are a professional report planner. Given a user request and optional context about their data/documents, generate a detailed report outline in JSON format.

The outline must follow this exact structure:
{
  "chapters": [
    {
      "number": "BAB I",
      "title": "Chapter Title",
      "sections": [
        {
          "id": "1.1",
          "title": "Section Title",
          "instruction": "Brief instruction on what to write in this section",
          "use_rag": false,
          "use_data": false,
          "target_words": 300
        }
      ]
    }
  ]
}

Rules:
- Use Indonesian chapter numbering (BAB I, BAB II, etc.)
- Each chapter should have 2-4 sections
- Section IDs should be hierarchical (1.1, 1.2, 2.1, etc.)
- Instructions should be specific and actionable
- Set use_rag=true if the section needs information from uploaded documents
- Set use_data=true if the section needs data analysis
- target_words should be between 200-500 per section
- Return ONLY valid JSON, no markdown fencing or extra text
"""


def validate_template_id(template_id: str) -> None:
    """Validate template_id to prevent path traversal.

    Raises:
        ValueError: If template_id contains invalid characters.
    """
    if not TEMPLATE_ID_PATTERN.match(template_id):
        raise ValueError(
            f"Invalid template_id '{template_id}': must contain only "
            "alphanumeric characters, underscores, and hyphens"
        )


def _load_template_meta(template_id: str) -> dict:
    """Load template meta.yaml file."""
    validate_template_id(template_id)
    template_dir = Path(__file__).parent / "templates" / template_id
    meta_path = template_dir / "meta.yaml"
    if not meta_path.exists():
        raise ValueError(f"Template '{template_id}' not found")
    with open(meta_path) as f:
        return yaml.safe_load(f)


def _validate_outline(outline: dict) -> dict:
    """Validate outline structure and return cleaned version."""
    if "chapters" not in outline:
        raise ValueError("Outline must contain 'chapters' key")

    chapters = outline["chapters"]
    if not isinstance(chapters, list) or len(chapters) == 0:
        raise ValueError("Outline must have at least one chapter")

    for chapter in chapters:
        if "number" not in chapter or "title" not in chapter:
            raise ValueError("Each chapter must have 'number' and 'title'")
        if "sections" not in chapter or not isinstance(chapter["sections"], list):
            raise ValueError("Each chapter must have a 'sections' list")
        for section in chapter["sections"]:
            required_keys = ["id", "title", "instruction"]
            for key in required_keys:
                if key not in section:
                    raise ValueError(f"Each section must have '{key}'")
            # Set defaults for optional fields
            section.setdefault("use_rag", False)
            section.setdefault("use_data", False)
            section.setdefault("target_words", 300)

    return outline


async def plan_report_outline(
    user_request: str,
    file_profiles: list[dict] | None = None,
    kb_doc_summaries: list[dict] | None = None,
    template_id: str = "business_report_v1",
) -> dict:
    """Generate a report outline using Gemini LLM.

    Args:
        user_request: The user's description of the report they want.
        file_profiles: Optional list of file metadata dicts.
        kb_doc_summaries: Optional list of knowledge base document summaries.
        template_id: The template to use for chapter defaults.

    Returns:
        A validated outline dict with chapters and sections.
    """
    meta = _load_template_meta(template_id)
    default_chapters = meta.get("default_chapters", [])

    user_prompt_parts = [
        f"User request: {user_request}",
        f"\nSuggested chapter structure (adapt as needed): {default_chapters}",
    ]

    if file_profiles:
        user_prompt_parts.append(
            f"\nAvailable data files: {json.dumps(file_profiles, ensure_ascii=False)}"
        )

    if kb_doc_summaries:
        user_prompt_parts.append(
            f"\nKnowledge base documents: {json.dumps(kb_doc_summaries, ensure_ascii=False)}"
        )

    user_prompt = "\n".join(user_prompt_parts)

    api_key = settings.GEMINI_API_KEY or None

    response = await litellm.acompletion(
        model="gemini/gemini-2.0-flash",
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        api_key=api_key,
    )

    content = response.choices[0].message.content
    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        # Remove first and last line (code fences)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines)

    outline = json.loads(content)
    validated = _validate_outline(outline)
    return validated
