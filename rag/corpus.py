"""Hospital corpus: Markdown documents split into titled sections of blank-line separated blocks."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_BLANK_LINE = re.compile(r"\n\s*\n")


@dataclass(frozen=True)
class Section:
    heading: str | None  # None for the text before the first '##' heading
    blocks: tuple[str, ...]  # paragraphs and lists, verbatim


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    sections: tuple[Section, ...]


def load_corpus(corpus_dir: Path) -> list[Document]:
    paths = sorted(Path(corpus_dir).glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"no Markdown documents in {corpus_dir}")
    return [parse_document(path.stem, path.read_text(encoding="utf-8")) for path in paths]


def parse_document(doc_id: str, markdown: str) -> Document:
    title: str | None = None
    sections: list[Section] = []
    heading: str | None = None
    body: list[str] = []

    def close_section() -> None:
        blocks = tuple(block.strip() for block in _BLANK_LINE.split("\n".join(body)) if block.strip())
        if blocks:
            sections.append(Section(heading, blocks))

    for line in markdown.splitlines():
        if title is None and line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            close_section()
            heading, body = line[3:].strip(), []
        else:
            body.append(line)
    close_section()

    if title is None:
        raise ValueError(f"{doc_id}: missing '# ' title")
    return Document(doc_id, title, tuple(sections))
