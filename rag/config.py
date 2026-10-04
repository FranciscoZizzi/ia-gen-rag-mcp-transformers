"""Retriever configuration, read from config/retriever.json or built by the experiment runner."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EncoderConfig:
    type: str  # "mean_pooling" | "sentence_transformer" | "hashing_bow"
    model: str | None = None
    revision: str | None = None  # Hugging Face commit; pin it in the delivered config
    query_prefix: str = ""
    passage_prefix: str = ""
    max_seq_length: int | None = None  # None keeps the model's own limit
    batch_size: int = 16


@dataclass(frozen=True)
class ChunkingConfig:
    strategy: str = "paragraph"
    max_chars: int = 700
    overlap_sentences: int = 0
    metadata: bool = False


@dataclass(frozen=True)
class SelectionConfig:
    top_k: int = 1
    min_score: float | None = None
    max_margin: float | None = None


@dataclass(frozen=True)
class RetrieverConfig:
    encoder: EncoderConfig
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    selection: SelectionConfig = field(default_factory=SelectionConfig)
    corpus_dir: str = "datos/corpus"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RetrieverConfig:
        parts = {"encoder": EncoderConfig, "chunking": ChunkingConfig, "selection": SelectionConfig}
        data = {key: _build(parts[key], value, key) if key in parts else value for key, value in data.items()}
        return _build(cls, data, "retriever")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_config(path: Path) -> RetrieverConfig:
    return RetrieverConfig.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def _build(cls, data: dict[str, Any], where: str):
    """Instantiate a config dataclass, rejecting unknown keys so that a typo never passes silently."""
    unknown = set(data) - {f.name for f in fields(cls)}
    if unknown:
        raise ValueError(f"unknown {where} config keys: {', '.join(sorted(unknown))}")
    return cls(**data)
