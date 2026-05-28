from __future__ import annotations

import fitz  # pymupdf
from docx import Document


def load_pdf(path: str) -> list[dict]:
    """Load a PDF file and extract text per page."""
    pages = []
    doc = fitz.open(path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            pages.append({"text": text, "page": page_num + 1, "section": None})
    doc.close()
    return pages


def load_docx(path: str) -> list[dict]:
    """Load a DOCX file and extract text grouped by consecutive non-empty paragraphs."""
    doc = Document(path)
    results = []
    current_group: list[str] = []
    section_index = 0

    for para in doc.paragraphs:
        if para.text.strip():
            current_group.append(para.text)
        else:
            if current_group:
                section_index += 1
                results.append({
                    "text": "\n".join(current_group),
                    "page": None,
                    "section": f"section_{section_index}",
                })
                current_group = []

    # Flush remaining group
    if current_group:
        section_index += 1
        results.append({
            "text": "\n".join(current_group),
            "page": None,
            "section": f"section_{section_index}",
        })

    return results


def load_txt(path: str) -> list[dict]:
    """Load a plain text file and return as a single entry."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    return [{"text": text, "page": None, "section": None}]
