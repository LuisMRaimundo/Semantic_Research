"""Concept-agnostic smoke helpers — any class / any lemma."""

from __future__ import annotations

import json
import re
import sqlite3
from typing import Any, Optional

from .engines import engine_paths
from .normalize import normalize_word
from .workspace import ClassWorkspace

_CLASSISH = re.compile(r"^(textura|classe|class|concept)", re.I)


def pick_pulo_probe_lemma(*, exclude: Optional[set[str]] = None) -> str:
    """Return any PULO lemma that has an ILI row (read-only, arbitrary)."""
    exclude = {normalize_word(x) for x in (exclude or set())}
    db = engine_paths()["pulo_sqlite"]
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT v.word FROM variant v "
            "JOIN to_ili t ON t.offset = v.offset "
            "WHERE v.word IS NOT NULL AND TRIM(v.word) != '' "
            "ORDER BY v.word_norm LIMIT 400"
        ).fetchall()
        for (word,) in rows:
            w = (word or "").replace("_", " ").strip()
            if w and normalize_word(w) not in exclude and " " not in w:
                return w
    finally:
        con.close()
    raise RuntimeError("PULO has no ILI-linked lemmas to probe")


def _looks_like_lemma(text: str, class_id: str = "") -> bool:
    """False for empty strings, class ids, and 'Textura…' style labels."""
    t = (text or "").strip()
    if not t or len(t) < 2:
        return False
    if normalize_word(t) == normalize_word(class_id):
        return False
    if _CLASSISH.match(t.replace(" ", "")):
        return False
    if t[:1].isupper() and any(ch.isupper() for ch in t[1:]) and " " not in t:
        # CamelCase class ids (TexturaComposita) — not citation forms
        return False
    return True


def _lemma_from_workspace(ws: ClassWorkspace) -> str:
    meta = ws.load_meta()
    pref = (meta.get("pref_label") or "").strip()
    if _looks_like_lemma(pref, ws.class_id):
        return pref
    stems = meta.get("focus_stems") or []
    for stem in stems:
        s = str(stem).strip()
        if _looks_like_lemma(s, ws.class_id):
            return s
    dec_path = ws.decisions_json
    if not dec_path.exists():
        return ""
    try:
        data = json.loads(dec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    for sense in data.get("senses") or []:
        for m in sense.get("members") or []:
            s = str(m).strip()
            if _looks_like_lemma(s, ws.class_id):
                return s
    return ""


def pick_smoke_target(
    class_id: Optional[str] = None,
    query: Optional[str] = None,
) -> tuple[str, str]:
    """Choose ``(class_id, query)`` for a live smoke run.

    Prefer an existing workspace + a real citation lemma from meta/decisions.
    Never treat a CamelCase class id as the search query.
    """
    classes = ClassWorkspace.list_classes()
    if class_id:
        if class_id not in classes:
            raise FileNotFoundError(f"class not found: {class_id}")
        ws = ClassWorkspace.open(class_id)
        # Explicit --query always wins (user may probe any string).
        if query and str(query).strip():
            return class_id, str(query).strip()
        q = _lemma_from_workspace(ws) or pick_pulo_probe_lemma()
        return class_id, q

    if not classes:
        raise RuntimeError(
            "No classes/ workspaces — create one with "
            "`python sr.py new <Class> --pref <lemma> --axis \"…\"`"
        )

    for name in classes:
        ws = ClassWorkspace.open(name)
        has_conc = False
        if ws.final_results.exists() and list(ws.final_results.glob("*.concordance.json")):
            has_conc = True
        elif ws.out.exists() and list(ws.out.glob("*.concordance.json")):
            has_conc = True
        lemma = (query if query and _looks_like_lemma(query, name) else None) or _lemma_from_workspace(ws)
        if has_conc and lemma:
            return name, lemma

    name = classes[0]
    ws = ClassWorkspace.open(name)
    lemma = (
        (query if query and _looks_like_lemma(query, name) else None)
        or _lemma_from_workspace(ws)
        or pick_pulo_probe_lemma()
    )
    return name, lemma


def run_smoke(
    class_id: Optional[str] = None,
    query: Optional[str] = None,
) -> dict[str, Any]:
    """Search + merge-only run for an arbitrary class/lemma."""
    from .pipeline import run_class, search_and_seed

    cls, q = pick_smoke_target(class_id, query)
    info = search_and_seed(cls, q, source="pulo", mode="Exact")
    if int(info.get("count") or 0) == 0:
        info = search_and_seed(cls, q, source="pulo", mode="Starts with")
    summary = run_class(cls, engines=[])
    return {
        "class_id": cls,
        "query": q,
        "search": info,
        "merge_ok": summary.get("merge_ok"),
        "errors": summary.get("errors"),
        "concordance_json": summary.get("concordance_json"),
        "sense_index": summary.get("sense_index"),
        "legacy_equivalence_counts": summary.get("legacy_equivalence_counts"),
    }
