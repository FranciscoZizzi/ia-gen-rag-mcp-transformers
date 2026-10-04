"""Chunking strategies: how documents are cut into the fragments the retriever returns."""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from rag.config import ChunkingConfig
from rag.corpus import Document


@dataclass(frozen=True)
class Chunk:
    chunk_id: str  # "<doc_id>#<position in the document>"
    doc_id: str
    title: str
    section: str | None
    text: str


def chunk_corpus(documents: Iterable[Document], config: ChunkingConfig) -> list[Chunk]:
    try:
        strategy = _STRATEGIES[config.strategy]
    except KeyError:
        raise ValueError(f"unknown chunking strategy {config.strategy!r}; expected one of {sorted(_STRATEGIES)}") from None
    chunks = []
    for document in documents:
        for position, (section, text) in enumerate(strategy(document, config)):
            chunks.append(Chunk(f"{document.doc_id}#{position}", document.doc_id, document.title, section, text))
    return chunks


def _paragraphs(document: Document, config: ChunkingConfig) -> Iterator[tuple[str | None, str]]:
    for section in document.sections:
        for block in section.blocks:
            yield section.heading, block


_STRATEGIES = {"paragraph": _paragraphs}
