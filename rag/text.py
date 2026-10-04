"""Text helpers shared by chunking, encoders and analysis."""
from __future__ import annotations

import re
import unicodedata

_WHITESPACE = re.compile(r"\s+")


def normalize_for_match(text: str) -> str:
    """Same normalization as the grader (evaluar.norm): NFKC, lowercase, collapsed whitespace."""
    return _WHITESPACE.sub(" ", unicodedata.normalize("NFKC", text).lower())
