"""Retriever: chunks the corpus, embeds it once and answers queries with ranked, cut-off fragments."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Sequence
from dataclasses import asdict
from pathlib import Path

import numpy as np

from rag.chunking import Chunk, chunk_corpus
from rag.config import RetrieverConfig
from rag.corpus import load_corpus
from rag.encoders import Encoder, build_encoder
from rag.reranking import Reranker, build_reranker
from rag.selection import ScoredChunk, select


class Retriever:
    def __init__(self, chunks: Sequence[Chunk], encoder: Encoder, config: RetrieverConfig,
                 cache_dir: Path | None = None, reranker: Reranker | None = None):
        self.chunks = list(chunks)
        self.config = config
        self._encoder = encoder
        self._reranker = reranker
        self._passages = [chunk.render(config.chunking.metadata) for chunk in self.chunks]
        self._embeddings = _cached(cache_dir, asdict(config.encoder), self._passages, encoder.encode_passages)

    @classmethod
    def from_config(cls, config: RetrieverConfig, base_dir: Path, cache_dir: Path | None = None) -> Retriever:
        documents = load_corpus(Path(base_dir) / config.corpus_dir)
        reranker = build_reranker(config.reranker) if config.reranker else None
        return cls(chunk_corpus(documents, config.chunking), build_encoder(config.encoder), config, cache_dir, reranker)

    def rank_many(self, queries: Sequence[str]) -> list[list[ScoredChunk]]:
        """Every chunk for every query, by descending cosine similarity (ties in corpus order).

        With a reranker, only the bi-encoder's best `candidates` chunks, ordered by the reranker's scores.
        """
        scores = self._encoder.encode_queries(list(queries)) @ self._embeddings.T
        rankings = [
            [ScoredChunk(self.chunks[i], float(row[i]), self._passages[i]) for i in np.argsort(-row, kind="stable")]
            for row in scores
        ]
        if self._reranker is None:
            return rankings
        candidates = self.config.reranker.candidates
        return [self._reranker.rerank(query, ranking[:candidates]) for query, ranking in zip(queries, rankings)]

    def search_many(self, queries: Sequence[str]) -> list[list[ScoredChunk]]:
        return [select(ranking, self.config.selection) for ranking in self.rank_many(queries)]

    def search(self, query: str) -> list[ScoredChunk]:
        return self.search_many([query])[0]


def _cached(cache_dir: Path | None, encoder_identity: dict, texts: list[str],
            encode: Callable[[list[str]], np.ndarray]) -> np.ndarray:
    """Passage embeddings stored on disk under a hash of the encoder config and the exact texts.

    Any change to the corpus, the chunking or the encoder yields a new key, so the cache cannot go stale.
    """
    if cache_dir is None:
        return encode(texts)
    payload = json.dumps([encoder_identity, texts], ensure_ascii=False, sort_keys=True).encode("utf-8")
    path = Path(cache_dir) / f"{hashlib.sha256(payload).hexdigest()}.npy"
    if path.exists():
        return np.load(path)
    embeddings = encode(texts)
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(f"{path.stem}.partial.npy")
    np.save(partial, embeddings)
    partial.replace(path)
    return embeddings
