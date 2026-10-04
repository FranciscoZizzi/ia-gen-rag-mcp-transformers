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
    """Cut a ranking (best first). The best candidate always stays: zero fragments score zero."""
    best, rest = list(ranked[:1]), list(ranked[1: config.top_k])
    if config.min_score is not None:
        rest = [scored for scored in rest if scored.score >= config.min_score]
    if config.max_margin is not None and best:
        rest = [scored for scored in rest if best[0].score - scored.score <= config.max_margin]
    return best + rest
