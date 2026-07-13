"""Accent/case folding shared by search adapters."""

from __future__ import annotations

import re
import unicodedata


def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_word(word: str) -> str:
    w = strip_accents(word.strip()).casefold()
    w = w.replace(" ", "_")
    return re.sub(r"_+", "_", w)


def pretty_word(word: str) -> str:
    return (word or "").replace("_", " ")


def fold(text: str) -> str:
    return normalize_word(text)
