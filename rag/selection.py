"""Cut-off: how many of the ranked chunks the retriever returns."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from rag.chunking import Chunk
from rag.config import SelectionConfig


@dataclass(frozen=True)
class ScoredChunk:
    chunk: Chunk
    score: float
    text: str  # the rendered fragment: what was embedded and what gets returned


def select(ranked: Sequence[ScoredChunk], config: SelectionConfig) -> list[ScoredChunk]:
    return list(ranked[: config.top_k])
