"""select: how many of the ranked chunks the retriever returns (precision vs recall in the grader)."""
from rag.chunking import Chunk
from rag.config import SelectionConfig
from rag.selection import ScoredChunk, select


def ranked(*scores: float) -> list[ScoredChunk]:
    return [ScoredChunk(Chunk(f"doc#{i}", "doc", "Doc", None, f"text {i}"), score, f"text {i}")
            for i, score in enumerate(scores)]


def selected_ids(selection: list[ScoredChunk]) -> list[str]:
    return [scored.chunk.chunk_id for scored in selection]


def test_keeps_the_top_k_best_in_order():
    assert selected_ids(select(ranked(0.9, 0.8, 0.7, 0.6), SelectionConfig(top_k=2))) == ["doc#0", "doc#1"]


def test_drops_candidates_below_min_score():
    assert selected_ids(select(ranked(0.9, 0.8, 0.5), SelectionConfig(top_k=3, min_score=0.7))) == ["doc#0", "doc#1"]


def test_always_keeps_the_best_candidate_even_below_min_score():
    assert selected_ids(select(ranked(0.4, 0.3), SelectionConfig(top_k=3, min_score=0.7))) == ["doc#0"]


def test_drops_candidates_further_than_max_margin_below_the_best():
    assert selected_ids(select(ranked(0.90, 0.88, 0.80), SelectionConfig(top_k=3, max_margin=0.05))) == ["doc#0", "doc#1"]
