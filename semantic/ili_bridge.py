"""Legacy ILI equivalence table — read-only helpers for migration / WordNet track.

Corte 1 removed the Ponte ILI GUI. Runtime joins use CILI (`cili_auto.py`).
This module only locates and reads old `ili_equivalence.json` files so that:
  * human rows can be reported in `ili_migration_report`;
  * `wordnet_track` can still discover previously mapped OEWN ILIs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .workspace import ClassWorkspace

HUMAN_SOURCE = "human-adjudicated (GUI Ponte ILI)"


def is_human_row(row: dict) -> bool:
    return str(row.get("source", "")).startswith("human")


def table_path(ws: ClassWorkspace) -> Path:
    """Canonical location of a legacy ili_equivalence.json (if any)."""
    return ws.out / "ili_equivalence.json"


def find_table_file(ws: ClassWorkspace) -> Optional[Path]:
    """Locate ili_equivalence.json even if dropped outside ``out/``.

    Search order (first hit wins):
      1. ``out/ili_equivalence.json`` (canonical)
      2. class root / ``results/`` / ``FINAL_RESULTS__…/``
      3. any ``*ili_equivalence*.json`` under those folders (shallow)
    Prefer ``ili_equivalence.json`` over ``ili_equivalence.cili.json``.
    """
    canonical = table_path(ws)
    if canonical.exists():
        return canonical

    candidates: list[Path] = [
        ws.root / "ili_equivalence.json",
        ws.results / "ili_equivalence.json",
        ws.final_results / "ili_equivalence.json",
    ]
    for folder in (ws.root, ws.out, ws.results, ws.final_results, ws.exports):
        if folder.exists():
            candidates.extend(sorted(folder.glob("*ili_equivalence*.json")))

    seen: set[Path] = set()
    for cand in candidates:
        try:
            resolved = cand.resolve()
        except OSError:
            continue
        if resolved in seen or not cand.is_file():
            continue
        seen.add(resolved)
        # Prefer human/legacy table over the auto CILI dump.
        if cand.name.endswith(".cili.json"):
            continue
        try:
            data = json.loads(cand.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        if not any(k in data for k in ("map", "review", "unmatched")):
            continue
        return cand
    # Fall back to CILI dump only if nothing else exists
    cili_dump = ws.out / "ili_equivalence.cili.json"
    if cili_dump.exists():
        return cili_dump
    return None


def load_table(ws: ClassWorkspace) -> Optional[dict]:
    p = find_table_file(ws)
    if p is None:
        return None
    return json.loads(p.read_text(encoding="utf-8"))
