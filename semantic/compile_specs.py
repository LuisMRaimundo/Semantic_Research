"""Compile decisions.json + class.json → engine specs (PULO / ONTO).

Corte 2: adjudication is DERIVED from sense-level decisions (UF > RT).
terms[].status is read for legacy only — never required for admission.
test/guarantee are not admission gates (filled as placeholders for engines).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from .decisions import EVIDENCIA, VOCABULARIO, load_decisions
from .normalize import fold, normalize_word
from .workspace import ClassWorkspace

_ENGINE_SENSE = frozenset({"UF", "RT", "exclude"})
_ENGINE_TERM = frozenset({"UF", "RT", "BT", "NT"})
_RANK = {"UF": 2, "RT": 1}


def _derive_axis_terms(meta: dict, decisions: dict) -> list[str]:
    """focus_stems + membros das acepções actualmente UF/RT."""
    stems = [fold(s) for s in meta.get("focus_stems") or []]
    for s in decisions.get("senses", []):
        if (s.get("decision") or "").upper() in ("UF", "RT"):
            for m in s.get("members") or []:
                stems.append(fold(m))
    seen: set[str] = set()
    out: list[str] = []
    for t in stems:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def axis_terms_exclusive_to_exclude(meta: dict, decisions: dict) -> list[str]:
    """Termos de ``axis_terms`` que só ocorrem em acepções exclude."""
    axis = {fold(t) for t in meta.get("axis_terms") or [] if t}
    live = {fold(s) for s in meta.get("focus_stems") or [] if s}
    for s in decisions.get("senses") or []:
        if (s.get("decision") or "").upper() in ("UF", "RT"):
            for m in s.get("members") or []:
                live.add(fold(m))
    exclusive: list[str] = []
    seen: set[str] = set()
    for s in decisions.get("senses") or []:
        if (s.get("decision") or "").upper() != "EXCLUDE":
            continue
        for m in s.get("members") or []:
            n = fold(m)
            if n and n in axis and n not in live and n not in seen:
                seen.add(n)
                exclusive.append(n)
    return exclusive


def _axis_terms(
    meta: dict,
    decisions: dict,
    ws: Optional[ClassWorkspace] = None,
) -> list[str]:
    """Deriva axis_terms a cada compilação, salvo ``axis_terms_locked``."""
    derived = _derive_axis_terms(meta, decisions)
    existing = [fold(t) for t in meta.get("axis_terms") or []]
    if meta.get("axis_terms_locked"):
        return existing
    if existing != derived:
        meta["axis_terms_previous"] = list(existing)
        meta["axis_terms"] = list(derived)
        if ws is not None:
            ws.save_meta(meta)
    return derived


def _derive_adjudication_from_senses(
    senses: list[dict],
    source_filter: str,
) -> dict[str, dict]:
    """Build engine adjudication from sense members. UF beats RT on conflict."""
    adjudication: dict[str, dict] = {}
    for s in senses:
        if (s.get("source") or "").lower() != source_filter:
            continue
        decision = (s.get("decision") or "").strip()
        if decision not in VOCABULARIO:
            continue
        for m in s.get("members") or []:
            term = (m or "").strip()
            if not term:
                continue
            key = normalize_word(term)
            prev = adjudication.get(key)
            if prev and _RANK.get(prev["status"], 0) > _RANK.get(decision, 0):
                continue
            adjudication[key] = {
                "status": decision,
                "test": "derivado do sentido (PASSO 3)",
                "guarantee": ["sense_decision"],
                "definition": "",
                "structural": "",
                "from_sense": s.get("key"),
            }
    return adjudication


def _merge_legacy_terms(adjudication: dict, dec: dict) -> None:
    """Read-only legacy terms[]: fill gaps only, never override sense-derived UF."""
    for t in dec.get("terms") or []:
        term = t.get("term") or ""
        status = (t.get("status") or "").strip()
        if not term or not status or status not in _ENGINE_TERM:
            continue
        if status in EVIDENCIA:
            continue
        key = normalize_word(term)
        if key in adjudication:
            continue  # sense-derived wins
        adjudication[key] = {
            "status": status,
            "test": t.get("note") or "legado terms[] (somente leitura)",
            "guarantee": t.get("guarantee") or ["legacy"],
            "definition": t.get("definition") or "",
            "structural": t.get("structural") or "",
        }


def _known_class_ids(meta: dict) -> set[str]:
    """Class registry ids referenced from this class sheet (no hardcodes)."""
    out = {fold(meta.get("class_id") or "")}
    for k in (meta.get("disjoint_classes") or {}):
        out.add(fold(str(k)))
    sc = meta.get("superclass")
    if sc:
        out.add(fold(str(sc)))
    for t in meta.get("control_axes") or []:
        if isinstance(t, dict) and t.get("eixo"):
            out.add(fold(str(t["eixo"])))
        elif isinstance(t, str):
            out.add(fold(t))
    # Also scan sibling class folders when available
    try:
        from . import settings as _settings
        root = _settings.CLASSES_DIR
        if root.exists():
            for p in root.glob("*/class.json"):
                out.add(fold(p.parent.name))
    except OSError:
        pass
    out.discard("")
    return out


def _enrich_manual(adjudication: dict, dec: dict, meta: Optional[dict] = None) -> list:
    """Manual terms are NOT auto-UF. Only explicit admit status enters adjudication.

    Evidence statuses, or structural links to another ontology class, stay out
    of the admit pool (they surface later as R3 cross-checks if needed).
    """
    meta = meta or {}
    class_ids = _known_class_ids(meta)
    evidence_keys = set()
    for t in dec.get("terms") or []:
        st = (t.get("status") or "").strip()
        if st in EVIDENCIA or (t.get("destino") or "") == "evidencia":
            evidence_keys.add(normalize_word(t.get("term") or ""))

    manual = []
    for m in dec.get("manual_terms") or []:
        manual.append(m)
        term = m.get("term") or ""
        if not term:
            continue
        key = normalize_word(term)
        status = (m.get("status") or "").strip()
        structural = fold(m.get("structural") or "")
        if key in evidence_keys or status in EVIDENCIA:
            continue
        if structural and structural in class_ids and structural != fold(
            meta.get("class_id") or ""
        ):
            # Stipulated against another class — evidence, not UF.
            continue
        if status not in _ENGINE_TERM:
            # No silent default to UF.
            continue
        if key not in adjudication:
            adjudication[key] = {
                "status": status,
                "test": "manual_terms",
                "guarantee": (
                    ["estipulativa"]
                    if (m.get("definition") and m.get("structural"))
                    else ["manual"]
                ),
                "definition": m.get("definition") or "",
                "structural": m.get("structural") or "",
            }
        else:
            adjudication[key].setdefault("definition", m.get("definition") or "")
            adjudication[key].setdefault("structural", m.get("structural") or "")
            if m.get("definition") and m.get("structural"):
                adjudication[key]["guarantee"] = ["estipulativa"]
    return manual


def compile_pulo_spec(ws: ClassWorkspace) -> dict[str, Any]:
    meta = ws.load_meta()
    dec = load_decisions(ws.decisions_json)
    whitelist = []
    for s in dec.get("senses", []):
        if s.get("source") != "pulo":
            continue
        decision = (s.get("decision") or "").strip()
        if not decision:
            continue
        if decision in EVIDENCIA and decision != "exclude":
            continue
        if decision not in _ENGINE_SENSE:
            continue
        # Pivot for the PULO engine = local PWN 3.0 id (pwn30-… / legacy ili-30-…).
        # Official CILI (i…) is carried separately — never as ili_offset.
        key = str(s.get("key") or "")
        pwn = (
            s.get("pwn_id")
            or (key if key.startswith(("pwn30-", "ili-30-", "por-30-")) else None)
            or s.get("legacy_omw_ili")
        )
        cili = s.get("cili") or (
            s.get("ili") if str(s.get("ili") or "").startswith("i")
            and str(s.get("ili") or "")[1:].isdigit()
            else None
        )
        whitelist.append({
            "ili_offset": pwn,
            "pwn_id": pwn if pwn and str(pwn).startswith("pwn30-") else None,
            "cili": cili,
            "glosa": s.get("gloss") or "",
            "decision": decision,
            "members": list(s.get("members") or []),
        })

    adjudication = _derive_adjudication_from_senses(dec.get("senses") or [], "pulo")
    _merge_legacy_terms(adjudication, dec)
    manual = _enrich_manual(adjudication, dec, meta)

    return {
        "class_id": ws.class_id,
        "pref_label": meta.get("pref_label") or ws.class_id,
        "axis": meta.get("axis") or "",
        "focus_stems": list(meta.get("focus_stems") or []),
        "axis_terms": _axis_terms(meta, dec, ws=ws),
        "stage1_whitelist": whitelist,
        "dictionary_attestations": [],
        "manual_terms": manual,
        "attribute_bucket": [],
        "exclude_terms": [normalize_word(x) for x in (dec.get("exclude_terms") or [])],
        "adjudication": adjudication,
        "disjoint_classes": dict(meta.get("disjoint_classes") or {}),
        "_provenance": {
            "finalizer": "semantic_research.compile_pulo_spec",
            "source": "decisions.json senses (Corte 2)",
        },
    }


def compile_onto_spec(ws: ClassWorkspace) -> dict[str, Any]:
    """Onto.PT discovery-only (Corte 3): whitelist for triage artefacts.

    Adjudication is still compiled so local reports work, but the pipeline
    does not feed ONTO admits into LexWarrant / TERMOS convergencia.
    """
    meta = ws.load_meta()
    dec = load_decisions(ws.decisions_json)
    whitelist = []
    for s in dec.get("senses", []):
        if s.get("source") != "onto":
            continue
        decision = (s.get("decision") or "").strip()
        if not decision:
            continue
        if decision in EVIDENCIA and decision != "exclude":
            continue
        if decision not in _ENGINE_SENSE:
            continue
        whitelist.append({
            "ili_offset": s.get("key"),
            "glosa": s.get("gloss") or "",
            "decision": decision,
            "members": list(s.get("members") or []),
        })

    adjudication = _derive_adjudication_from_senses(dec.get("senses") or [], "onto")
    _merge_legacy_terms(adjudication, dec)

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
            "source": "decisions.json senses (Onto discovery)",
            "admission": False,
        },
    }


def write_specs(ws: ClassWorkspace) -> dict[str, Path]:
    ws.ensure()
    paths = {}
    pulo = compile_pulo_spec(ws)
    if pulo.get("stage1_whitelist"):
        p = ws.specs / f"{ws.class_id}.pulo.json"
        p.write_text(
            json.dumps(pulo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        paths["pulo"] = p
    onto = compile_onto_spec(ws)
    if onto.get("stage1_whitelist"):
        p = ws.specs / f"{ws.class_id}.onto.json"
        p.write_text(
            json.dumps(onto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        paths["onto"] = p
    return paths
