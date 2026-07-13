#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke test for the enriched WordNet JSON export.

Runs the query 'uniform' and prints a per-synset BEFORE/AFTER field-count table
so the enrichment (ILI + pt_lemmas + typed relations) is auditable. Not a unit
test (name does not match test_*.py), so run_tests.py does not pick it up.

Run:  python tests/smoke_export.py
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import oewn_backend as backend

with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    import wordnet_gui_v2 as gui

ORIGINAL_FIELDS = 9  # name,pos,definition,examples,lemmas,hypernyms,hyponyms,min_depth,max_depth
RELATION_KEYS = ("antonym", "derivationally_related_form", "similar_to", "attribute", "also_see")


class _Var:
    def __init__(self, v): self._v = v
    def get(self): return self._v


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    backend.ensure_oewn()
    try:
        backend.ensure_translation_lexicon("por")
    except Exception:
        pass

    synsets = backend.synsets("uniform")
    exporter = gui.WordNetCompleteGUI.__new__(gui.WordNetCompleteGUI)
    exporter.term_var, exporter.pos_var, exporter.lang_var = _Var("uniform"), _Var("Todas"), _Var("English")
    exporter.current_synsets = synsets

    tmp = Path(tempfile.mkdtemp()) / "uniform.json"
    exporter._export_json(str(tmp))
    data = json.loads(tmp.read_text(encoding="utf-8"))

    print("=" * 92)
    print("SMOKE TEST — enriched JSON export for 'uniform'")
    print(f"source: {data['source']}")
    print("=" * 92)
    print(f"{'synset':<20}{'pos':<4}{'ili':<9}{'before':<8}{'after':<7}"
          f"{'pt_lemmas':<26}relations (non-empty)")
    print("-" * 92)
    for s in data["synsets"]:
        after = len(s)
        rels = [k for k in RELATION_KEYS if s["relations"][k]]
        rel_counts = ", ".join(f"{k}={len(s['relations'][k])}" for k in rels) or "—"
        pt = ", ".join(s["pt_lemmas"]) or "—"
        print(f"{s['name']:<20}{s['pos']:<4}{str(s['ili']):<9}"
              f"{ORIGINAL_FIELDS:<8}{after:<7}{pt[:24]:<26}{rel_counts}")
        print(f"    def: {s['definition']}")
    print("-" * 92)
    print(f"Total synsets: {len(data['synsets'])}  ·  fields/synset: "
          f"{ORIGINAL_FIELDS} → {len(data['synsets'][0]) if data['synsets'] else 0} "
          f"(+ili, +pt_lemmas, +relations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
