"""Optional second stage: a cross-encoder reads query and passage together and re-scores the best candidates."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from typing import Protocol

from rag.config import RerankerConfig
from rag.selection import ScoredChunk


class Reranker(Protocol):
    def rerank(self, query: str, candidates: Sequence[ScoredChunk]) -> list[ScoredChunk]: ...


class CrossEncoderReranker:
    def __init__(self, model: str, revision: str | None = None, batch_size: int = 16):
        from sentence_transformers import CrossEncoder

        self._model = CrossEncoder(model, revision=revision, device="cpu")
        self.batch_size = batch_size

    def rerank(self, query: str, candidates: Sequence[ScoredChunk]) -> list[ScoredChunk]:
        """Candidates re-scored by the cross-encoder, best first (ties keep the bi-encoder order)."""
        scores = self._model.predict([(query, scored.text) for scored in candidates], batch_size=self.batch_size,
                                     show_progress_bar=False)
        rescored = [replace(scored, score=float(score)) for scored, score in zip(candidates, scores)]
        return sorted(rescored, key=lambda scored: -scored.score)


def build_reranker(config: RerankerConfig) -> Reranker:
    return CrossEncoderReranker(config.model, config.revision, config.batch_size)
