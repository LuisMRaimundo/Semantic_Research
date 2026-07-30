#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sense / synset identity helpers (WN-LMF aligned).

Rules
-----
* ``cili`` is only an official Collaborative Interlingual Index id (``iNNNNN``),
  obtained from OEWN ``ili=…``, the CILI catalogue, or an official offset map.
* Never fabricate CILI by concatenation.
* Princeton WordNet 3.0 offsets are local ids: ``pwn30-XXXXXXXX-p``.
* Legacy OMW/MCR strings ``ili-30-XXXXXXXX-p`` are **not** CILI — they are
  PWN 3.0 pivots mislabelled as "ILI". Parse them into ``pwn_id`` and resolve
  ``cili`` via the official map (or leave ``cili`` null).

See: https://globalwordnet.github.io/cili/
     https://globalwordnet.github.io/schemas/
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Optional

_CILI_RE = re.compile(r"^i\d+$")
_BARE_OFFSET_RE = re.compile(r"^(\d{8})-([a-z])$")
_PWN30_RE = re.compile(r"^pwn30-(\d{8})-([a-z])$", re.I)
# Legacy OMW / MCR pivot (NOT CILI): ili-30-…, por-30-…, eng-30-…
_OMW30_RE = re.compile(r"^([a-z]{2,4})-30-(\d{8})-([a-z])$", re.I)
_OEWN_ID_RE = re.compile(r"^oewn-(\d{8})-([a-z])$", re.I)


@dataclass
class SenseIdentity:
    source: str = ""
    source_version: Optional[str] = None
    source_synset_id: Optional[str] = None
    pwn_version: Optional[str] = None
    pwn_offset: Optional[str] = None  # 8 digits
    part_of_speech: Optional[str] = None
    pwn_id: Optional[str] = None  # pwn30-XXXXXXXX-p
    cili: Optional[str] = None  # iNNNNN only
    oewn_id: Optional[str] = None  # oewn-XXXXXXXX-p
    mapping_status: str = "unverified"
    legacy_omw_ili: Optional[str] = None  # deprecated ili-30-… if seen

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_pwn30_id(offset8: str, pos: str) -> str:
    """Local PWN 3.0 identifier — not a CILI id."""
    off = str(offset8 or "").strip()
    p = str(pos or "").strip().lower()
    if not re.fullmatch(r"\d{8}", off):
        raise ValueError(f"invalid PWN offset: {offset8!r}")
    if not re.fullmatch(r"[a-z]", p):
        raise ValueError(f"invalid POS: {pos!r}")
    return f"pwn30-{off}-{p}"


def bare_offset(offset8: str, pos: str) -> str:
    return f"{str(offset8).strip()}-{str(pos).strip().lower()}"


def is_cili(value: Any) -> bool:
    s = str(value or "").strip()
    if s.startswith("oewn-ili:"):
        s = s.split(":", 1)[1].strip()
    if s.startswith("cili:"):
        s = s.split(":", 1)[1].strip()
    return bool(_CILI_RE.match(s))


def strip_cili_prefix(value: str) -> str:
    s = str(value or "").strip()
    if s.startswith("oewn-ili:"):
        return s.split(":", 1)[1].strip()
    if s.startswith("cili:"):
        return s.split(":", 1)[1].strip()
    return s


def _resolve_cili(raw: str) -> Optional[str]:
    """Official map / catalogue only — never synthesise."""
    try:
        from cili_resolver import cili_resolve
    except ImportError:
        return None
    return cili_resolve(raw)


def _oewn_id_for_cili(cili: str) -> Optional[str]:
    """Best-effort OEWN synset id for a CILI id (optional enrichment)."""
    if not cili:
        return None
    try:
        import wn  # type: ignore

        for s in wn.synsets(ili=cili, lexicon="oewn:2024"):
            sid = str(getattr(s, "id", "") or "")
            if sid.startswith("oewn-"):
                return sid
    except Exception:  # noqa: BLE001
        return None
    return None


def parse_identifier(
    raw: Any,
    *,
    source: str = "",
    source_version: Optional[str] = None,
    source_synset_id: Optional[str] = None,
    resolve_cili: bool = True,
    enrich_oewn: bool = False,
) -> SenseIdentity:
    """Parse any known id string into separated identity fields."""
    ident = SenseIdentity(
        source=source or "",
        source_version=source_version,
        source_synset_id=source_synset_id,
    )
    s = str(raw or "").strip()
    if not s:
        return ident

    # OEWN synset id
    m = _OEWN_ID_RE.match(s)
    if m:
        ident.oewn_id = s if s.startswith("oewn-") else f"oewn-{m.group(1)}-{m.group(2)}"
        ident.pwn_version = None  # OEWN ≠ PWN 3.0 offset numbering
        ident.part_of_speech = m.group(2).lower()
        if resolve_cili:
            # Prefer ili attribute via wn when available; else map by PWN31 offset
            cid = None
            try:
                import wn  # type: ignore

                syn = wn.synset(ident.oewn_id)
                ili_obj = getattr(syn, "ili", None)
                if ili_obj is not None:
                    cid = str(getattr(ili_obj, "id", ili_obj) or "") or None
            except Exception:  # noqa: BLE001
                cid = None
            if not cid:
                cid = _resolve_cili(f"{m.group(1)}-{m.group(2)}")
            if cid and _CILI_RE.match(cid):
                ident.cili = cid
                ident.mapping_status = "official"
                # Also attach PWN30 if the official map has it
                try:
                    from cili_resolver import cili_offset

                    off = cili_offset(cid)
                    bm = _BARE_OFFSET_RE.match(off or "")
                    if bm:
                        ident.pwn_version = "3.0"
                        ident.pwn_offset = bm.group(1)
                        ident.part_of_speech = bm.group(2)
                        ident.pwn_id = make_pwn30_id(bm.group(1), bm.group(2))
                except Exception:  # noqa: BLE001
                    pass
        return ident

    # Bare / prefixed CILI
    cili_cand = strip_cili_prefix(s)
    if _CILI_RE.match(cili_cand):
        if resolve_cili:
            # Accept only if catalogue/map knows it (cili_resolve enforces this)
            cid = _resolve_cili(cili_cand)
            if cid:
                ident.cili = cid
                ident.mapping_status = "official"
                try:
                    from cili_resolver import cili_offset

                    off = cili_offset(cid)
                    bm = _BARE_OFFSET_RE.match(off or "")
                    if bm:
                        ident.pwn_version = "3.0"
                        ident.pwn_offset = bm.group(1)
                        ident.part_of_speech = bm.group(2)
                        ident.pwn_id = make_pwn30_id(bm.group(1), bm.group(2))
                except Exception:  # noqa: BLE001
                    pass
                if enrich_oewn and not ident.oewn_id:
                    ident.oewn_id = _oewn_id_for_cili(cid)
            else:
                ident.mapping_status = "unverified"
        else:
            ident.cili = cili_cand
            ident.mapping_status = "official"
        return ident

    # Local pwn30-…
    m = _PWN30_RE.match(s)
    if m:
        ident.pwn_version = "3.0"
        ident.pwn_offset = m.group(1)
        ident.part_of_speech = m.group(2).lower()
        ident.pwn_id = make_pwn30_id(m.group(1), m.group(2))
        if resolve_cili:
            cid = _resolve_cili(bare_offset(m.group(1), m.group(2)))
            if cid:
                ident.cili = cid
                ident.mapping_status = "official"
                if enrich_oewn:
                    ident.oewn_id = _oewn_id_for_cili(cid)
            else:
                ident.mapping_status = "unverified"
        return ident

    # Legacy OMW/MCR ili-30- / por-30- / eng-30-…
    m = _OMW30_RE.match(s)
    if m:
        ns = m.group(1).lower()
        off8, pos = m.group(2), m.group(3).lower()
        ident.pwn_version = "3.0"
        ident.pwn_offset = off8
        ident.part_of_speech = pos
        ident.pwn_id = make_pwn30_id(off8, pos)
        if ns == "ili":
            ident.legacy_omw_ili = f"ili-30-{off8}-{pos}"
        if ns == "por" and not ident.source_synset_id:
            ident.source_synset_id = f"por-30-{off8}-{pos}"
            if not ident.source:
                ident.source = "PULO"
            if not ident.source_version:
                ident.source_version = "MCR-3.0-2016"
        if resolve_cili:
            cid = _resolve_cili(bare_offset(off8, pos))
            if cid:
                ident.cili = cid
                ident.mapping_status = "official"
                if enrich_oewn:
                    ident.oewn_id = _oewn_id_for_cili(cid)
            else:
                ident.mapping_status = "unverified"
        return ident

    # Bare PWN offset XXXXXXXX-p
    m = _BARE_OFFSET_RE.match(s)
    if m:
        ident.pwn_version = "3.0"
        ident.pwn_offset = m.group(1)
        ident.part_of_speech = m.group(2).lower()
        ident.pwn_id = make_pwn30_id(m.group(1), m.group(2))
        if resolve_cili:
            cid = _resolve_cili(s)
            if cid:
                ident.cili = cid
                ident.mapping_status = "official"
            else:
                ident.mapping_status = "unverified"
        return ident

    return ident


def from_pulo_to_ili(
    ili_offset: Any = None,
    *,
    synset_offset: Any = None,
    ili_wn_id: Any = None,
    resolve_cili: bool = True,
    enrich_oewn: bool = False,
) -> SenseIdentity:
    """Build identity from a PULO ``to_ili`` row / export ``ili`` item.

    PULO/MCR stores historical ``ili-30-…`` pivots (= PWN 3.0), not modern CILI.
    """
    raw = str(ili_offset or "").strip()
    src = str(synset_offset or "").strip()
    base = parse_identifier(
        raw or src,
        source="PULO",
        source_version="MCR-3.0-2016",
        source_synset_id=src or None,
        resolve_cili=resolve_cili,
        enrich_oewn=enrich_oewn,
    )
    if src and not base.source_synset_id:
        base.source_synset_id = src
    # If only por-30-… was present, ensure pwn fields filled
    if not base.pwn_id and src:
        alt = parse_identifier(
            src,
            source="PULO",
            source_version="MCR-3.0-2016",
            source_synset_id=src,
            resolve_cili=resolve_cili,
            enrich_oewn=enrich_oewn,
        )
        for field in (
            "pwn_id", "pwn_offset", "part_of_speech", "pwn_version",
            "cili", "mapping_status", "legacy_omw_ili", "oewn_id",
        ):
            if getattr(base, field) in (None, "", "unverified"):
                val = getattr(alt, field)
                if val not in (None, ""):
                    setattr(base, field, val)
    if ili_wn_id and not base.legacy_omw_ili and raw.startswith("ili-30-"):
        base.legacy_omw_ili = raw
    return base


def to_pwn30(raw: Any) -> Optional[str]:
    """Convert legacy ili-30-/por-30-/bare offset to ``pwn30-…`` (or None)."""
    ident = parse_identifier(raw, resolve_cili=False)
    return ident.pwn_id


def stable_key(raw: Any) -> str:
    """Match key across ili-30- / pwn30- / bare offset spellings."""
    ident = parse_identifier(raw, resolve_cili=False)
    if ident.pwn_id:
        return ident.pwn_id
    if ident.cili:
        return ident.cili
    if ident.oewn_id:
        return ident.oewn_id
    return str(raw or "").strip()


def join_key(raw: Any, *, resolve_cili: bool = True) -> tuple[Optional[str], bool]:
    """LexWarrant join key: prefer official CILI, else local pwn30.

    Returns ``(key, mapped)``. CILI keys use the existing ``oewn-ili:i…``
    namespace so OEWN rows and PULO rows that share a CILI id unify without
    fabricating ``ili-30-…``.
    """
    s = str(raw or "").strip()
    if not s:
        return None, False
    ident = parse_identifier(s, resolve_cili=resolve_cili)
    if ident.cili:
        return f"oewn-ili:{ident.cili}", True
    if ident.pwn_id:
        return ident.pwn_id, True
    if ident.oewn_id:
        return ident.oewn_id, True
    if is_cili(s):
        # Unknown to map — do not invent; leave unmapped
        return None, False
    return None, False


def export_ili_item(ident: SenseIdentity) -> dict[str, Any]:
    """Shape written into PULO/search export ``synsets[].ili[]``."""
    return {
        # Local PWN 3.0 id (replaces fabricated / legacy ili-30- as primary)
        "ili_offset": ident.pwn_id or ident.source_synset_id or "",
        "pwn_id": ident.pwn_id,
        "pwn_version": ident.pwn_version,
        "pwn_offset": ident.pwn_offset,
        "part_of_speech": ident.part_of_speech,
        "cili": ident.cili,
        "oewn_id": ident.oewn_id,
        "mapping_status": ident.mapping_status,
        "legacy_omw_ili": ident.legacy_omw_ili,
        "ili_wn_id": "eng-30" if ident.pwn_version == "3.0" else None,
    }
