#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CILI resolver — resolução canónica de identificadores ILI (lookup puro).

Fonte: data/cili/ili-map-pwn30.tab (vendorizado; ver data/cili/HEADER.txt).
Relação: <ili-id> TAB <pwn30-offset-pos>  (ex.: "i1\t00001740-a").

Contrato:
  * lookup puro — sem inferência, sem efeitos laterais, sem rede;
  * nunca levanta excepção; id desconhecido/lixo → None (nunca ILI fabricado);
  * aceita: "i123" (id CILI), "ili-30-XXXXXXXX-p" / "por-30-…" / "eng-30-…"
    (offsets PWN-3.0 com namespace OMW), ou "XXXXXXXX-p" (offset nu).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

CILI_VERSION = "cili@eeab8003 (master, 2016-01-26)"
_DATA = Path(__file__).resolve().parent / "data" / "cili" / "ili-map-pwn30.tab"

_ILI_ID_RE = re.compile(r"^i\d+$")
_OMW30_RE = re.compile(r"^[a-z]{2,4}-30-(\d{8}-[a-z])$")
_BARE_OFFSET_RE = re.compile(r"^\d{8}-[a-z]$")

_by_offset: Optional[dict] = None   # "00001740-a" -> "i1"
_by_ili: Optional[dict] = None      # "i1" -> "00001740-a"


def _load() -> None:
    global _by_offset, _by_ili
    if _by_offset is not None:
        return
    by_off: dict = {}
    by_ili: dict = {}
    try:
        with open(_DATA, encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) != 2:
                    continue
                ili, off = parts[0].strip(), parts[1].strip()
                if not ili or not off:
                    continue
                by_ili[ili] = off
                by_off[off] = ili
    except OSError:
        pass  # sem dados → resolver devolve None para tudo (nunca fabrica)
    _by_offset, _by_ili = by_off, by_ili


def cili_counts() -> dict:
    """Contagens carregadas (para relatório/diagnóstico)."""
    _load()
    return {"version": CILI_VERSION, "ili_ids": len(_by_ili or {}),
            "pwn30_offsets": len(_by_offset or {}),
            "data_file": str(_DATA)}


def cili_resolve(identifier) -> Optional[str]:
    """Resolve um identificador para o ILI canónico CILI ("i…"), ou None.

    Lookup puro na tabela vendorizada. Nunca levanta; nunca fabrica.
    """
    try:
        _load()
        s = str(identifier or "").strip()
        if not s:
            return None
        if _ILI_ID_RE.match(s):
            return s if s in (_by_ili or {}) else None
        m = _OMW30_RE.match(s)
        if m:
            return (_by_offset or {}).get(m.group(1))
        if _BARE_OFFSET_RE.match(s):
            return (_by_offset or {}).get(s)
        return None
    except Exception:  # noqa: BLE001 — contrato: nunca levanta
        return None


def cili_offset(ili_id) -> Optional[str]:
    """Offset PWN-3.0 de um id CILI ("i1" → "00001740-a"), ou None."""
    try:
        _load()
        s = str(ili_id or "").strip()
        return (_by_ili or {}).get(s)
    except Exception:  # noqa: BLE001
        return None
