"""Focus-stem / search-syntax helpers for TERMOS (kept out of termos_pesquisa)."""

from __future__ import annotations

from typing import Any, Optional

from .normalize import normalize_word


def wildcard(form: str) -> str:
    form = (form or "").strip()
    if not form:
        return ""
    return form if form.endswith("*") else f"{form}*"


def corpus_near_stem(meta: dict[str, Any], pref: str) -> str:
    for key in ("corpus_near_stem", "near_stem", "corpus_stem"):
        raw = (meta.get(key) or "").strip()
        if raw:
            return raw if raw.endswith("*") else f"{raw}*"
    stems = meta.get("focus_stems") or []
    if stems:
        return wildcard(str(stems[0]))
    return wildcard(pref)


def focus_morph_roots(meta: dict[str, Any], pref: str) -> set[str]:
    """Short normalised roots used to keep domain frontiers on-topic."""
    roots: set[str] = set()
    for t in list(meta.get("focus_stems") or []) + [pref]:
        n = normalize_word(str(t or ""))
        if len(n) < 4:
            continue
        roots.add(n)
        for k in (5, 6, 7, 8):
            if len(n) >= k:
                roots.add(n[:k])
    return {r for r in roots if len(r) >= 5}


def text_related_to_focus(text: str, roots: set[str]) -> bool:
    n = normalize_word(text or "")
    if not n or not roots:
        return False
    return any(r in n for r in roots)


def search_syntax_line(doc: dict[str, Any]) -> str:
    """NEAR syntax only when a search-lang target form is adjudicated."""
    search_lang = doc.get("search_lang") or "en"
    polo = doc.get("A_polo_alvo") or []
    near = (doc.get("near_stem") or "").strip()
    if not polo:
        return f"não disponível — pólo-alvo `{search_lang}` por adjudicar"
    wc = (polo[0].get("wildcard") or "").strip()
    if not wc and polo[0].get("forma"):
        wc = wildcard(str(polo[0]["forma"]))
    if not wc:
        wc = near
    if not wc:
        return f"não disponível — pólo-alvo `{search_lang}` por adjudicar"
    return f"`{wc} NEAR/4 <termo>`"

