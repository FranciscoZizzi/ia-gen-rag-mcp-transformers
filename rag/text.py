"""Text helpers shared by chunking, encoders and analysis."""
from __future__ import annotations

import re
import unicodedata

_WHITESPACE = re.compile(r"\s+")
_LIST_ITEM = re.compile(r"^\s*[-*]\s+")
# A sentence ends at . ! or ? followed by whitespace and something that can open a sentence.
# "2.500 pesos" and "12:00" survive because no whitespace follows their inner punctuation.
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[¿¡(\"'«A-ZÁÉÍÓÚÜÑ0-9])")


def normalize_for_match(text: str) -> str:
    """Same normalization as the grader (evaluar.norm): NFKC, lowercase, collapsed whitespace."""
    return _WHITESPACE.sub(" ", unicodedata.normalize("NFKC", text).lower())


def split_sentences(block: str) -> list[str]:
    """Sentences of a paragraph or list block. Each list item is a unit, without its marker."""
    units: list[str] = []
    paragraph: list[str] = []
    for line in block.splitlines():
        if _LIST_ITEM.match(line):
            if paragraph:
                units.append(" ".join(paragraph))
                paragraph = []
            units.append(_LIST_ITEM.sub("", line, count=1).strip())
        elif line.strip():
            paragraph.append(line.strip())
    if paragraph:
        units.append(" ".join(paragraph))
    return [sentence for unit in units for sentence in _SENTENCE_END.split(unit) if sentence]
