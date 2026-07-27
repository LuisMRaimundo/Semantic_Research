"""Gloss / definitional similarity for hard cases.

Layers (best available wins for ``score``; components always reported):
  1. **embedding** — optional ``sentence-transformers`` cosine (if installed)
  2. **tfidf** — character + word n-gram TF-IDF cosine (pure Python, default)
  3. **jaccard** — content-token Jaccard (legacy baseline)
  + lemma-in-gloss boost
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable, Optional

from .normalize import normalize_word, strip_accents

_TOKEN_RE = re.compile(r"[a-z0-9]+", re.I)

_STOP = frozenset({
    "a", "o", "os", "as", "um", "uma", "de", "do", "da", "dos", "das",
    "e", "ou", "em", "no", "na", "nos", "nas", "por", "para", "com",
    "que", "se", "ao", "à", "às", "aos", "lhe", "lhes", "não", "mais",
    "the", "an", "of", "and", "or", "in", "on", "to", "for", "with",
    "that", "this", "is", "are", "be", "as", "by", "from", "not",
    "its", "his", "her", "their", "into", "than",
})

_EMBED_MODEL = None
_EMBED_TRIED = False


def tokenize_gloss(text: str) -> set[str]:
    if not text:
        return set()
    folded = strip_accents(text).casefold()
    return {t for t in _TOKEN_RE.findall(folded) if len(t) > 2 and t not in _STOP}


def gloss_jaccard(a: str, b: str) -> float:
    ta, tb = tokenize_gloss(a), tokenize_gloss(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _char_ngrams(text: str, n: int = 3) -> list[str]:
    s = strip_accents(text or "").casefold()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = f" {s.strip()} "
    if len(s) < n:
        return [s] if s.strip() else []
    return [s[i : i + n] for i in range(len(s) - n + 1)]


def _features(text: str) -> Counter:
    """Word tokens + character trigrams for a cheap distributional vector."""
    feats: Counter = Counter()
    for t in tokenize_gloss(text):
        feats[f"w:{t}"] += 1
    for g in _char_ngrams(text, 3):
        feats[f"c:{g}"] += 1
    return feats


def _cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    keys = set(a) | set(b)
    # idf-ish: downweight features that appear in both with same raw count only
    # Simple TF cosine (L2); good enough for short glosses.
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / (na * nb)


def gloss_tfidf_cosine(a: str, b: str) -> float:
    """TF cosine over word + char-trigram features (0..1)."""
    return _cosine(_features(a), _features(b))


def _embeddings_enabled() -> bool:
    """Opt-in only — avoids surprise HuggingFace downloads."""
    try:
        from .settings import load_config
        return bool(load_config().get("gloss_use_embeddings", False))
    except Exception:  # noqa: BLE001
        return False


def _embedding_cosine(a: str, b: str) -> Optional[float]:
    """Optional sentence-transformers cosine; None unless explicitly enabled."""
    global _EMBED_MODEL, _EMBED_TRIED
    a, b = (a or "").strip(), (b or "").strip()
    if not a or not b or not _embeddings_enabled():
        return None
    if not _EMBED_TRIED:
        _EMBED_TRIED = True
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            _EMBED_MODEL = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2"
            )
        except Exception:  # noqa: BLE001
            _EMBED_MODEL = None
    if _EMBED_MODEL is None:
        return None
    try:
        import numpy as np  # type: ignore
        va, vb = _EMBED_MODEL.encode([a, b], normalize_embeddings=True)
        return float(np.dot(va, vb))
    except Exception:  # noqa: BLE001
        return None


def lemma_in_gloss_boost(lemmas: Iterable[str], gloss: str) -> float:
    if not gloss:
        return 0.0
    g = tokenize_gloss(gloss)
    if not g:
        return 0.0
    hits = 0
    for lem in lemmas or []:
        n = normalize_word(lem).replace("_", "")
        if n and n in g:
            hits += 1
    if hits <= 0:
        return 0.0
    return min(0.2, 0.08 * hits)


def sense_similarity(
    gloss_a: str,
    gloss_b: str,
    lemmas_a: Optional[Iterable[str]] = None,
    lemmas_b: Optional[Iterable[str]] = None,
) -> dict:
    """Combined definitional score with transparent components."""
    jac = gloss_jaccard(gloss_a, gloss_b)
    tfidf = gloss_tfidf_cosine(gloss_a, gloss_b)
    emb = _embedding_cosine(gloss_a, gloss_b)
    boost = 0.0
    boost += lemma_in_gloss_boost(lemmas_a or [], gloss_b)
    boost += lemma_in_gloss_boost(lemmas_b or [], gloss_a)

    if emb is not None:
        # embeddings dominate when present; still mix a little surface signal
        base = 0.75 * max(0.0, emb) + 0.15 * tfidf + 0.10 * jac
        method = "embedding+tfidf+jaccard"
    else:
        base = 0.65 * tfidf + 0.35 * jac
        method = "tfidf+jaccard"

    score = min(1.0, base + boost)
    return {
        "score": round(score, 4),
        "method": method,
        "jaccard": round(jac, 4),
        "tfidf_cosine": round(tfidf, 4),
        "embedding_cosine": None if emb is None else round(emb, 4),
        "lemma_boost": round(boost, 4),
        "shared_tokens": sorted(tokenize_gloss(gloss_a) & tokenize_gloss(gloss_b))[:20],
    }


def passes_gloss_gate(
    gloss_a: str,
    gloss_b: str,
    *,
    min_score: float = 0.12,
    lemmas_a: Optional[Iterable[str]] = None,
    lemmas_b: Optional[Iterable[str]] = None,
) -> bool:
    """Empty gloss → False (safer for weak joins)."""
    if not (gloss_a or "").strip() or not (gloss_b or "").strip():
        return False
    return sense_similarity(gloss_a, gloss_b, lemmas_a, lemmas_b)["score"] >= min_score
