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


class MeanPoolingEncoder:
    """A raw transformer encoder (BERT, not trained for similarity): masked mean of the last hidden layer.

    The mission's mandatory baseline. Padding positions are excluded from the mean.
    """

    def __init__(self, model: str, revision: str | None = None, query_prefix: str = "", passage_prefix: str = "",
                 max_seq_length: int | None = None, batch_size: int = 16):
        import torch
        from transformers import AutoModel, AutoTokenizer
        from transformers.utils import logging as transformers_logging

        # Loading only the encoder leaves the masked-LM head unused, which transformers reports at length.
        transformers_logging.set_verbosity_error()
        self._torch = torch
        self._tokenizer = AutoTokenizer.from_pretrained(model, revision=revision)
        self._model = AutoModel.from_pretrained(model, revision=revision).eval()
        # Some tokenizers report a huge sentinel instead of their real limit; BERT's is 512 positions.
        self.max_seq_length = max_seq_length or min(512, self._tokenizer.model_max_length)
        self.query_prefix, self.passage_prefix, self.batch_size = query_prefix, passage_prefix, batch_size

    def encode_queries(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode([self.query_prefix + text for text in texts])

    def encode_passages(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode([self.passage_prefix + text for text in texts])

    def passage_token_counts(self, texts: Sequence[str]) -> list[int]:
        return [len(self._tokenizer(self.passage_prefix + text)["input_ids"]) for text in texts]

    def _encode(self, texts: list[str]) -> np.ndarray:
        pooled = []
        for start in range(0, len(texts), self.batch_size):
            tokens = self._tokenizer(texts[start:start + self.batch_size], padding=True, truncation=True,
                                     max_length=self.max_seq_length, return_tensors="pt")
            with self._torch.inference_mode():
                hidden = self._model(**tokens).last_hidden_state  # (batch, tokens, dim)
            mask = tokens["attention_mask"].unsqueeze(-1).to(hidden.dtype)
            pooled.append(((hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)).float().numpy())
        return l2_normalize(np.vstack(pooled))


class SentenceTransformerEncoder:
    """A model trained for sentence embeddings (MiniLM, E5, BGE-M3), through sentence-transformers.

    E5 models expect "query: " and "passage: " prefixes; they come from the encoder config.
    """

    def __init__(self, model: str, revision: str | None = None, query_prefix: str = "", passage_prefix: str = "",
                 max_seq_length: int | None = None, batch_size: int = 16):
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model, revision=revision, device="cpu")
        if max_seq_length:
            self._model.max_seq_length = max_seq_length
        self.max_seq_length = self._model.max_seq_length
        self.query_prefix, self.passage_prefix, self.batch_size = query_prefix, passage_prefix, batch_size

    def encode_queries(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode([self.query_prefix + text for text in texts])

    def encode_passages(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode([self.passage_prefix + text for text in texts])

    def passage_token_counts(self, texts: Sequence[str]) -> list[int]:
        return [len(self._model.tokenizer(self.passage_prefix + text)["input_ids"]) for text in texts]

    def _encode(self, texts: list[str]) -> np.ndarray:
        vectors = self._model.encode(texts, batch_size=self.batch_size, normalize_embeddings=True,
                                     convert_to_numpy=True, show_progress_bar=False)
        return np.asarray(vectors, dtype=np.float32)


def l2_normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.maximum(norms, 1e-12)


def build_encoder(config: EncoderConfig) -> Encoder:
    if config.type == "hashing_bow":
        return HashingBowEncoder()
    transformer_encoders = {"mean_pooling": MeanPoolingEncoder, "sentence_transformer": SentenceTransformerEncoder}
    if config.type not in transformer_encoders:
        raise ValueError(f"unknown encoder type {config.type!r}; expected hashing_bow or one of {sorted(transformer_encoders)}")
    if not config.model:
        raise ValueError(f"encoder type {config.type!r} needs a model")
    return transformer_encoders[config.type](config.model, config.revision, config.query_prefix, config.passage_prefix,
                                             config.max_seq_length, config.batch_size)
