#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CILI resolver — resolução canónica de identificadores CILI (lookup puro).

Fontes (offline, vendorizadas):
  * data/cili/ili-map-pwn30.tab  — PWN 3.0 offset → CILI ``i…``
  * data/cili/ili-map-pwn31.tab  — PWN 3.1 offset → CILI ``i…``
  * optional ``wn.ili.get``     — validate bare ``i…`` against the CILI
    catalogue bundled with the ``wn`` package (OEWN-native ids)

Contrato:
  * lookup puro — sem efeitos laterais de escrita, sem rede em runtime;
  * nunca levanta excepção; id desconhecido/lixo → None (nunca CILI fabricado);
  * aceita: "i123", "pwn30-…", bare offset, legacy OMW ``ili-30-…``/``por-30-…``
    (legacy strings are PWN 3.0 pivots, **not** CILI ids — used only as map keys);
  * normalização a↔s para adjectivos satélite.
  * Nunca sintetiza ``ili-30-…`` nem ``i…`` por concatenação.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

CILI_VERSION = "cili@upstream-master+pwn30+pwn31+wn.ili"
_DIR = Path(__file__).resolve().parent / "data" / "cili"
_MAPS = (
    _DIR / "ili-map-pwn30.tab",
    _DIR / "ili-map-pwn31.tab",
)

_ILI_ID_RE = re.compile(r"^i\d+$")
_OMW_RE = re.compile(r"^[a-z]{2,4}-(\d{2})-(\d{8}-[a-z])$")
_PWN30_RE = re.compile(r"^pwn30-(\d{8}-[a-z])$", re.I)
_BARE_OFFSET_RE = re.compile(r"^\d{8}-[a-z]$")

_by_offset: Optional[dict] = None   # offset -> ili
_by_ili: Optional[dict] = None      # ili -> preferred offset (pwn30 first)
_map_files: list[str] = []
_wn_ili_ok: Optional[bool] = None


def _load() -> None:
    global _by_offset, _by_ili, _map_files
    if _by_offset is not None:
        return
    by_off: dict = {}
    by_ili: dict = {}
    loaded: list[str] = []
    for path in _MAPS:
        if not path.exists():
            continue
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) != 2:
                        continue
                    ili, off = parts[0].strip(), parts[1].strip()
                    if not ili or not off:
                        continue
                    by_off[off] = ili
                    # Prefer first map's offset for ili→offset (pwn30 before pwn31)
                    by_ili.setdefault(ili, off)
            loaded.append(str(path))
        except OSError:
            continue
    _by_offset, _by_ili, _map_files = by_off, by_ili, loaded


def _wn_ili_known(ili_id: str) -> bool:
    """True if ``wn.ili`` catalogue knows this id (OEWN-native CILI)."""
    global _wn_ili_ok
    try:
        import wn.ili as wn_ili  # type: ignore
        obj = wn_ili.get(ili_id)
        _wn_ili_ok = True
        return obj is not None
    except Exception:  # noqa: BLE001
        _wn_ili_ok = False
        return False


def cili_counts() -> dict:
    """Contagens carregadas (para relatório/diagnóstico)."""
    _load()
    return {
        "version": CILI_VERSION,
        "ili_ids": len(_by_ili or {}),
        "pwn_offsets": len(_by_offset or {}),
        "pwn30_offsets": len(_by_offset or {}),  # back-compat key
        "data_files": list(_map_files),
        "data_file": _map_files[0] if _map_files else str(_MAPS[0]),
        "wn_ili_bridge": _wn_ili_ok,
    }


def _lookup_offset(off: str) -> Optional[str]:
    """Exact offset lookup, then a↔s satellite normalisation."""
    hit = (_by_offset or {}).get(off)
    if hit:
        return hit
    if off.endswith("-a"):
        return (_by_offset or {}).get(off[:-1] + "s")
    if off.endswith("-s"):
        return (_by_offset or {}).get(off[:-1] + "a")
    return None


def cili_resolve(identifier) -> Optional[str]:
    """Resolve um identificador para o CILI canónico ("i…"), ou None.

    ``ili-30-…`` / ``por-30-…`` are accepted only as *legacy PWN 3.0 map keys*
    (OMW/MCR pivot spelling). The return value is always a real CILI ``i…``
    from the official table — never the input string rewritten as CILI.
    """
    try:
        _load()
        s = str(identifier or "").strip()
        if not s:
            return None
        if s.startswith("oewn-ili:"):
            s = s.split(":", 1)[1].strip()
        if s.startswith("cili:"):
            s = s.split(":", 1)[1].strip()
        if _ILI_ID_RE.match(s):
            if s in (_by_ili or {}):
                return s
            # OEWN 2024 may carry CILI ids absent from the offset TSVs;
            # accept only if the wn.ili catalogue confirms the id.
            return s if _wn_ili_known(s) else None
        m = _PWN30_RE.match(s)
        if m:
            return _lookup_offset(m.group(1).lower())
        m = _OMW_RE.match(s)
        if m:
            return _lookup_offset(m.group(2).lower())
        if _BARE_OFFSET_RE.match(s):
            return _lookup_offset(s.lower())
        return None
    except Exception:  # noqa: BLE001 — contrato: nunca levanta
        return None


def cili_offset(ili_id) -> Optional[str]:
    """Offset preferido (PWN-3.0 se existir) de um id CILI, ou None."""
    try:
        _load()
        s = str(ili_id or "").strip()
        return (_by_ili or {}).get(s)
    except Exception:  # noqa: BLE001
        return None
