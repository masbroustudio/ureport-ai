from __future__ import annotations

import re
from dataclasses import dataclass

import tiktoken

_encoding = tiktoken.get_encoding("cl100k_base")


@dataclass
class Chunk:
    text: str
    page: int | None
    section: str | None
    chunk_index: int
    token_count: int


def _count_tokens(text: str) -> int:
    return len(_encoding.encode(text))


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation boundaries."""
    parts = re.split(r"(?<=[.!?])(?:\s|\n)+", text)
    return [p for p in parts if p.strip()]


def chunk_text(
    pages: list[dict], target_tokens: int = 512, overlap_tokens: int = 77
) -> list[Chunk]:
    """Split pages into overlapping chunks respecting paragraph and sentence boundaries."""
    chunks: list[Chunk] = []
    chunk_index = 0

    # Flatten all text segments with their metadata
    segments: list[dict] = []
    for page_info in pages:
        text = page_info["text"]
        # Split by paragraph boundaries first
        paragraphs = text.split("\n\n")
        for para in paragraphs:
            para = para.strip()
            if para:
                segments.append({
                    "text": para,
                    "page": page_info.get("page"),
                    "section": page_info.get("section"),
                })

    if not segments:
        return []

    current_text_parts: list[str] = []
    current_page = segments[0].get("page")
    current_section = segments[0].get("section")
    overlap_text = ""

    for seg in segments:
        seg_text = seg["text"]
        seg_tokens = _count_tokens(seg_text)

        # If a single segment exceeds target, split by sentences
        if seg_tokens > target_tokens:
            sentences = _split_into_sentences(seg_text)
            for sentence in sentences:
                sent_tokens = _count_tokens(sentence)
                current_count = _count_tokens(" ".join(current_text_parts)) if current_text_parts else 0

                if current_count + sent_tokens > target_tokens and current_text_parts:
                    # Emit current chunk
                    chunk_text_str = " ".join(current_text_parts)
                    token_count = _count_tokens(chunk_text_str)
                    chunks.append(Chunk(
                        text=chunk_text_str,
                        page=current_page,
                        section=current_section,
                        chunk_index=chunk_index,
                        token_count=token_count,
                    ))
                    chunk_index += 1

                    # Build overlap from end of current chunk
                    overlap_text = _build_overlap(chunk_text_str, overlap_tokens)
                    current_text_parts = [overlap_text] if overlap_text else []
                    current_page = seg.get("page")
                    current_section = seg.get("section")

                current_text_parts.append(sentence)
        else:
            current_count = _count_tokens(" ".join(current_text_parts)) if current_text_parts else 0

            if current_count + seg_tokens > target_tokens and current_text_parts:
                # Emit current chunk
                chunk_text_str = " ".join(current_text_parts)
                token_count = _count_tokens(chunk_text_str)
                chunks.append(Chunk(
                    text=chunk_text_str,
                    page=current_page,
                    section=current_section,
                    chunk_index=chunk_index,
                    token_count=token_count,
                ))
                chunk_index += 1

                # Build overlap
                overlap_text = _build_overlap(chunk_text_str, overlap_tokens)
                current_text_parts = [overlap_text] if overlap_text else []
                current_page = seg.get("page")
                current_section = seg.get("section")

            current_text_parts.append(seg_text)
            if not current_text_parts or current_count == 0:
                current_page = seg.get("page")
                current_section = seg.get("section")

    # Flush remaining
    if current_text_parts:
        chunk_text_str = " ".join(current_text_parts)
        token_count = _count_tokens(chunk_text_str)
        if token_count > 0:
            chunks.append(Chunk(
                text=chunk_text_str,
                page=current_page,
                section=current_section,
                chunk_index=chunk_index,
                token_count=token_count,
            ))

    return chunks


def _build_overlap(text: str, overlap_tokens: int) -> str:
    """Get the last `overlap_tokens` tokens of text as overlap for next chunk."""
    tokens = _encoding.encode(text)
    if len(tokens) <= overlap_tokens:
        return text
    overlap = tokens[-overlap_tokens:]
    return _encoding.decode(overlap)
