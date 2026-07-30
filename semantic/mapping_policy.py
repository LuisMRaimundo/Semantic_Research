"""Single source of truth for adjudicated CILI / label mapping.

``class.json`` → ``concept_mapping`` overrides automatic promotion of
formally resolved PULO CILIs into vocabulary, anchors, TERMOS, and SKOS.
"""

from __future__ import annotations

from typing import Any, Optional


def concept_mapping(meta: dict[str, Any], dec: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    cm = meta.get("concept_mapping") if isinstance(meta, dict) else None
    if not isinstance(cm, dict) and isinstance(dec, dict):
        cm = dec.get("concept_mapping")
    return dict(cm) if isinstance(cm, dict) else {}


def excluded_cili_ids(
    meta: dict[str, Any],
    dec: Optional[dict[str, Any]] = None,
) -> set[str]:
    cm = concept_mapping(meta, dec)
    out: set[str] = set()
    for item in cm.get("excluded_cili") or []:
        if isinstance(item, dict):
            cid = str(item.get("cili") or item.get("ili") or "").strip()
        else:
            cid = str(item or "").strip()
        if cid.startswith(("oewn-ili:", "ili:", "cili:")) and not cid.startswith("ili-30-"):
            cid = cid.rsplit(":", 1)[-1]
        if cid.startswith("i") and cid[1:].isdigit():
            out.add(cid)
    return out


def excluded_cili_reasons(
    meta: dict[str, Any],
    dec: Optional[dict[str, Any]] = None,
) -> dict[str, str]:
    cm = concept_mapping(meta, dec)
    out: dict[str, str] = {}
    for item in cm.get("excluded_cili") or []:
        if isinstance(item, dict):
            cid = str(item.get("cili") or item.get("ili") or "").strip()
            reason = str(item.get("reason") or item.get("motivo") or "").strip()
        else:
            cid = str(item or "").strip()
            reason = ""
        if cid.startswith(("oewn-ili:", "ili:", "cili:")) and not cid.startswith("ili-30-"):
            cid = cid.rsplit(":", 1)[-1]
        if cid.startswith("i") and cid[1:].isdigit():
            out[cid] = reason
    return out


def resolve_to_cili(raw: Any) -> Optional[str]:
    """Resolve bare CILI / pwn30 / legacy ili-30 to official ``i…`` (or None)."""
    s = str(raw or "").strip()
    if not s:
        return None
    if s.startswith(("oewn-ili:", "ili:", "cili:")) and not s.startswith("ili-30-"):
        s = s.rsplit(":", 1)[-1]
    if s.startswith("i") and s[1:].isdigit() and not s[1:].startswith("0"):
        # Prefer catalogue when available
        try:
            from .engines import load_identifiers
            return load_identifiers().try_normalize_cili_id(s) or s
        except Exception:  # noqa: BLE001
            return s
    try:
        from .engines import load_identifiers
        ident = load_identifiers().parse_identifier(s, resolve_cili=True)
        return ident.cili_id or ident.cili
    except Exception:  # noqa: BLE001
        return None


def sense_cili(sense: dict[str, Any]) -> Optional[str]:
    for fld in ("cili_id", "cili", "ili", "key", "pwn_id"):
        cid = resolve_to_cili(sense.get(fld))
        if cid:
            return cid
    return None


def sense_excluded(
    sense: dict[str, Any],
    excluded: set[str],
) -> bool:
    if not excluded:
        return False
    cid = sense_cili(sense)
    return bool(cid and cid in excluded)


def sync_decisions_with_excluded_cili(
    decisions: dict[str, Any],
    meta: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Force UF/RT → exclude when sense CILI is in ``excluded_cili``.

    Returns (updated_decisions, list of applied flips).
    """
    excluded = excluded_cili_ids(meta, decisions)
    reasons = excluded_cili_reasons(meta, decisions)
    if not excluded:
        return decisions, []
    flips: list[dict[str, str]] = []
    senses = list(decisions.get("senses") or [])
    for s in senses:
        decision = (s.get("decision") or "").strip()
        if decision not in ("UF", "RT"):
            continue
        cid = sense_cili(s)
        if not cid or cid not in excluded:
            continue
        reason = reasons.get(cid) or "excluded_cili (concept_mapping)"
        note = (s.get("note") or "").strip()
        if reason and reason not in note:
            s["note"] = f"{note}; {reason}".strip("; ").strip()
        s["decision"] = "exclude"
        s["destino"] = "evidencia"
        flips.append({
            "key": str(s.get("key") or ""),
            "cili": cid,
            "from": decision,
            "to": "exclude",
            "reason": reason,
        })
    decisions = dict(decisions)
    decisions["senses"] = senses
    return decisions, flips


def cili_ids_from_matrix_row(row: dict[str, Any]) -> set[str]:
    """Extract resolved CILI ids from a LexWarrant concept / matrix row."""
    out: set[str] = set()
    raw = row.get("ili") or row.get("ilis") or []
    if isinstance(raw, str):
        raw = [raw] if raw else []
    for item in raw:
        cid = resolve_to_cili(item)
        if cid:
            out.add(cid)
    return out
