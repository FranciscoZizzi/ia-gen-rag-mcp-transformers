"""Chunking strategies: how documents are cut into the fragments the retriever returns."""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from rag.config import ChunkingConfig
from rag.corpus import Document
from rag.text import split_sentences


@dataclass(frozen=True)
class Chunk:
    chunk_id: str  # "<doc_id>#<position in the document>"
    doc_id: str
    title: str
    section: str | None
    text: str

    def render(self, with_metadata: bool) -> str:
        """The fragment as embedded and returned, optionally headed by "<title> — <section>"."""
        if not with_metadata:
            return self.text
        header = f"{self.title} — {self.section}" if self.section else self.title
        return f"{header}\n{self.text}"


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


def _sentences(document: Document, config: ChunkingConfig) -> Iterator[tuple[str | None, str]]:
    for section in document.sections:
        for block in section.blocks:
            for sentence in split_sentences(block):
                yield section.heading, sentence


def _sections(document: Document, config: ChunkingConfig) -> Iterator[tuple[str | None, str]]:
    """One chunk per section; a long section is packed block by block, a long block sentence by sentence."""
    for section in document.sections:
        blocks = list(section.blocks)
        for start, end in _pack(blocks, config.max_chars, "\n\n"):
            if end - start == 1 and len(blocks[start]) > config.max_chars:
                sentences = split_sentences(blocks[start])
                for first, last in _pack(sentences, config.max_chars, " "):
                    yield section.heading, " ".join(sentences[first:last])
            else:
                yield section.heading, "\n\n".join(blocks[start:end])


def _fixed(document: Document, config: ChunkingConfig) -> Iterator[tuple[str | None, str]]:
    """Structure-agnostic windows: the document's sentences packed up to max_chars."""
    headed = list(_sentences(document, config))
    sentences = [sentence for _, sentence in headed]
    for start, end in _pack(sentences, config.max_chars, " ", config.overlap_sentences):
        yield headed[start][0], " ".join(sentences[start:end])


def _pack(units: list[str], max_chars: int, separator: str, overlap: int = 0) -> list[tuple[int, int]]:
    """Greedy [start, end) windows of consecutive units whose joined length fits in max_chars.

    A unit longer than max_chars gets a window of its own: units are never cut. The next window
    repeats up to `overlap` trailing units, never a whole window, and only while a new unit still fits.
    """
    windows = []
    start = 0
    while start < len(units):
        end = start + 1
        while end < len(units) and len(separator.join(units[start:end + 1])) <= max_chars:
            end += 1
        windows.append((start, end))
        if end == len(units):
            break
        start = next(
            (end - carried for carried in range(min(overlap, end - start - 1), 0, -1)
             if len(separator.join(units[end - carried:end + 1])) <= max_chars),
            end,
        )
    return windows


_STRATEGIES = {"paragraph": _paragraphs, "section": _sections, "sentence": _sentences, "fixed": _fixed}
