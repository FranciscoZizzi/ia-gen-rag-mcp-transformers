"""Retriever: chunks the corpus, embeds it once and answers queries with ranked, cut-off fragments."""
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np

from rag.chunking import Chunk, chunk_corpus
from rag.config import RetrieverConfig
from rag.corpus import load_corpus
from rag.encoders import Encoder, build_encoder
from rag.selection import ScoredChunk, select


class Retriever:
    def __init__(self, chunks: Sequence[Chunk], encoder: Encoder, config: RetrieverConfig):
        self.chunks = list(chunks)
        self.config = config
        self._encoder = encoder
        self._passages = [chunk.text for chunk in self.chunks]
        self._embeddings = encoder.encode_passages(self._passages)

    @classmethod
    def from_config(cls, config: RetrieverConfig, base_dir: Path) -> Retriever:
        documents = load_corpus(Path(base_dir) / config.corpus_dir)
        return cls(chunk_corpus(documents, config.chunking), build_encoder(config.encoder), config)

    def rank_many(self, queries: Sequence[str]) -> list[list[ScoredChunk]]:
        """Every chunk for every query, by descending cosine similarity (ties in corpus order)."""
        scores = self._encoder.encode_queries(list(queries)) @ self._embeddings.T
        return [
            [ScoredChunk(self.chunks[i], float(row[i]), self._passages[i]) for i in np.argsort(-row, kind="stable")]
            for row in scores
        ]

    def search_many(self, queries: Sequence[str]) -> list[list[ScoredChunk]]:
        return [select(ranking, self.config.selection) for ranking in self.rank_many(queries)]

    def search(self, query: str) -> list[ScoredChunk]:
        return self.search_many([query])[0]
