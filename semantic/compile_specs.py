"""Compile decisions.json + class.json → engine specs (PULO / ONTO)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .normalize import fold, normalize_word
from .workspace import ClassWorkspace


def _axis_terms(meta: dict, decisions: dict) -> list[str]:
    existing = [fold(t) for t in meta.get("axis_terms") or []]
    if existing:
        return existing
    stems = [fold(s) for s in meta.get("focus_stems") or []]
    for s in decisions.get("senses", []):
        if (s.get("decision") or "").upper() in ("UF", "RT"):
            for m in s.get("members") or []:
                stems.append(fold(m))
    # unique preserve order
    seen = set()
    out = []
    for t in stems:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def compile_pulo_spec(ws: ClassWorkspace) -> dict[str, Any]:
    meta = ws.load_meta()
    dec = json.loads(ws.decisions_json.read_text(encoding="utf-8"))
    whitelist = []
    for s in dec.get("senses", []):
        if s.get("source") != "pulo":
            continue
        decision = (s.get("decision") or "").strip()
        if not decision:
            continue
        # map atributo on sense → UF on sense + attribute terms handled below
        eng_decision = decision
        if decision == "atributo":
            eng_decision = "UF"
        elif decision == "contraste":
            eng_decision = "exclude"  # contrast via term adjudication / relations
        whitelist.append({
            "ili_offset": s.get("ili") or (s["key"] if str(s["key"]).startswith("ili-") else None),
            "glosa": s.get("gloss") or "",
            "decision": eng_decision if eng_decision in ("UF", "RT", "exclude") else "exclude",
            "members": list(s.get("members") or []),
        })

    attribute_bucket = []
    adjudication = {}
    for t in dec.get("terms", []):
        term = t.get("term") or ""
        status = (t.get("status") or "").strip()
        if not term or not status:
            continue
        if status == "atributo":
            attribute_bucket.append(normalize_word(term))
        adjudication[normalize_word(term)] = {
            "status": status if status != "exclude" else "exclude",
            "test": t.get("note") or "",
            "guarantee": t.get("guarantee") or ["lexical"],
            "definition": t.get("definition") or "",
            "structural": t.get("structural") or "",
        }

    # promote sense-level atributo members into attribute_bucket
    for s in dec.get("senses", []):
        if s.get("source") == "pulo" and (s.get("decision") or "") == "atributo":
            for m in s.get("members") or []:
                attribute_bucket.append(normalize_word(m))

    # dedupe attribute bucket
    seen = set()
    attr = []
    for a in attribute_bucket:
        if a and a not in seen:
            seen.add(a)
            attr.append(a)

    manual = []
    for m in dec.get("manual_terms") or []:
        manual.append(m)
        term = m.get("term") or ""
        if not term:
            continue
        key = normalize_word(term)
        if key not in adjudication:
            adjudication[key] = {
                "status": "contraste",
                "test": "",
                "guarantee": list(m.get("provenance") or ["estipulativa"]),
                "definition": m.get("definition") or "",
                "structural": m.get("structural") or "",
            }
        else:
            adjudication[key].setdefault("definition", m.get("definition") or "")
            adjudication[key].setdefault("structural", m.get("structural") or "")

    return {
        "class_id": ws.class_id,
        "pref_label": meta.get("pref_label") or ws.class_id,
        "axis": meta.get("axis") or "",
        "focus_stems": list(meta.get("focus_stems") or []),
        "axis_terms": _axis_terms(meta, dec),
        "stage1_whitelist": whitelist,
        "dictionary_attestations": [],
        "manual_terms": manual,
        "attribute_bucket": attr,
        "exclude_terms": [normalize_word(x) for x in (dec.get("exclude_terms") or [])],
        "adjudication": adjudication,
        "disjoint_classes": dict(meta.get("disjoint_classes") or {}),
        "_provenance": {
            "finalizer": "semantic_research.compile_pulo_spec",
            "source": "decisions.json",
        },
    }


def compile_onto_spec(ws: ClassWorkspace) -> dict[str, Any]:
    meta = ws.load_meta()
    dec = json.loads(ws.decisions_json.read_text(encoding="utf-8"))
    whitelist = []
    for s in dec.get("senses", []):
        if s.get("source") != "onto":
            continue
        decision = (s.get("decision") or "").strip()
        if not decision:
            continue
        # Onto engine uses UF / RT / contraste / exclude (no atributo)
        eng = decision
        if decision == "atributo":
            eng = "UF"
        whitelist.append({
            "ili_offset": s.get("key"),  # resource:sid convention in Onto specs
            "glosa": s.get("gloss") or "",
            "decision": eng if eng in ("UF", "RT", "contraste", "exclude") else "exclude",
            "members": list(s.get("members") or []),
        })

    adjudication = {}
    for t in dec.get("terms", []):
        term = t.get("term") or ""
        status = (t.get("status") or "").strip()
        if not term or not status:
            continue
        st = "contraste" if status == "contraste" else status
        if st == "atributo":
            st = "UF"
        adjudication[normalize_word(term)] = {
            "status": st,
            "test": t.get("note") or "",
            "guarantee": t.get("guarantee") or ["lexical"],
            "definition": t.get("definition") or "",
            "structural": t.get("structural") or "",
        }

    stems = list(meta.get("focus_stems") or [])
    if not stems:
        stems = [meta.get("pref_label") or ws.class_id]

    return {
        "class_id": ws.class_id,
        "pref_label": meta.get("pref_label") or ws.class_id,
        "axis": meta.get("axis") or "",
        "focus_stems": stems,
        "gating": {"weight_min": 0.5, "min_cooccurrence": 2},
        "fuzzy_resources": ["contopt"],
        "stage1_whitelist": whitelist,
        "dictionary_attestations": [],
        "manual_terms": list(dec.get("manual_terms") or []),
        "exclusion_patterns": [],
        "adjudication": adjudication,
        "disjoint_classes": dict(meta.get("disjoint_classes") or {}),
        "_provenance": {
            "finalizer": "semantic_research.compile_onto_spec",
            "source": "decisions.json",
        },
    }


def write_specs(ws: ClassWorkspace) -> dict[str, Path]:
    ws.ensure()
    paths = {}
    pulo = compile_pulo_spec(ws)
    if pulo.get("stage1_whitelist"):
        p = ws.specs / f"{ws.class_id}.pulo.json"
        p.write_text(json.dumps(pulo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths["pulo"] = p
    onto = compile_onto_spec(ws)
    if onto.get("stage1_whitelist"):
        p = ws.specs / f"{ws.class_id}.onto.json"
        p.write_text(json.dumps(onto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths["onto"] = p
    return paths
