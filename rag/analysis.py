"""Numbers that explain the experiments: where the evidence lands in a ranking and how sure we can be."""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from rag.selection import ScoredChunk
from rag.text import normalize_for_match


def gold_rank(ranking: Sequence[ScoredChunk], evidence: Sequence[str]) -> int | None:
    """1-based rank of the first chunk containing an evidence phrase, matched the way the grader does."""
    phrases = [normalize_for_match(phrase) for phrase in evidence]
    for rank, scored in enumerate(ranking, start=1):
        text = normalize_for_match(scored.text)
        if any(phrase in text for phrase in phrases):
            return rank
    return None


def hit_rate(ranks: Sequence[int | None], k: int) -> float:
    return sum(rank is not None and rank <= k for rank in ranks) / len(ranks)


def mean_reciprocal_rank(ranks: Sequence[int | None]) -> float:
    return sum(1 / rank for rank in ranks if rank) / len(ranks)


def paired_bootstrap(differences: Sequence[float], resamples: int = 10_000, seed: int = 0) -> tuple[float, float]:
    """95% interval for the mean of paired per-question differences, resampling questions with replacement."""
    values = np.asarray(differences, dtype=float)
    rng = np.random.default_rng(seed)
    means = values[rng.integers(0, len(values), size=(resamples, len(values)))].mean(axis=1)
    low, high = np.percentile(means, [2.5, 97.5])
    return float(low), float(high)
