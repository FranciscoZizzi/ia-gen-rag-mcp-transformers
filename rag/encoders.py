"""Encoders turn texts into L2-normalized vectors, so a dot product is a cosine similarity."""
from __future__ import annotations

import re
import zlib
from collections.abc import Sequence
from typing import Protocol

import numpy as np

from rag.config import EncoderConfig
from rag.text import normalize_for_match


class Encoder(Protocol):
    def encode_queries(self, texts: Sequence[str]) -> np.ndarray: ...

    def encode_passages(self, texts: Sequence[str]) -> np.ndarray: ...


class HashingBowEncoder:
    """Lexical bag of words: hashed term presence compared by cosine. Not a transformer.

    Serves as the offline test double and as the lexical sanity row of the experiments. Presence,
    not counts: with counts, stopwords dominate the vectors (CR 0.20 instead of the mission's 0.35).
    Terms are hashed with crc32 because Python's hash() is salted per process.
    """

    _TOKEN = re.compile(r"\w+")

    def __init__(self, dimensions: int = 2**14):
        self.dimensions = dimensions

    def encode_queries(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode(texts)

    def encode_passages(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode(texts)

    def _encode(self, texts: Sequence[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dimensions), dtype=np.float32)
        for row, text in enumerate(texts):
            for token in self._TOKEN.findall(normalize_for_match(text)):
                vectors[row, zlib.crc32(token.encode("utf-8")) % self.dimensions] = 1.0
        return l2_normalize(vectors)


def l2_normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.maximum(norms, 1e-12)


def build_encoder(config: EncoderConfig) -> Encoder:
    if config.type == "hashing_bow":
        return HashingBowEncoder()
    raise ValueError(f"unknown encoder type {config.type!r}")
