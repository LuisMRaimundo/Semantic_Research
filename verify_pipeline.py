#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the consolidated layout: unit tests from engines/ + full merge."""
import json
import subprocess
import sys
from pathlib import Path

SR = Path(r"C:\Users\lmr20\Desktop\Semantic_Research")
LEX = SR / "engines" / "LexWarrant"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    # engines importable from the NEW location only
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                       cwd=str(LEX), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("== unittest discover (engines/LexWarrant/tests) ==")
    tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
    print("\n".join(tail[-6:]))
    if r.returncode != 0:
        print("UNIT TESTS FAILED")
        return 1

    sys.path.insert(0, str(SR))
    from semantic.settings import load_config
    cfg = load_config()
    for k in ("pulo_sqlite", "onto_sqlite", "pulo_engine_dir",
              "onto_engine_dir", "lexwarrant_dir"):
        p = Path(cfg[k])
        inside = str(p).lower().startswith(str(SR).lower())
        print(f"{'OK ' if p.exists() and inside else 'BAD'} {k}: {p}")
        if not (p.exists() and inside):
            return 1

    from semantic.pipeline import run_class, search_and_seed
    # live search against the consolidated DBs (read-only sanity)
    info = search_and_seed("TexturaUniforme", "uniforme", source="pulo",
                           mode="Exact")
    print(f"search pulo 'uniforme': {info['count']} synsets")

    s = run_class("TexturaUniforme", engines=[])
    print("merge_ok:", s.get("merge_ok"), "| errors:", s.get("errors"))
    doc = json.loads(Path(s["concordance_json"]).read_text(encoding="utf-8"))
    print("equiv loaded:", doc.get("ili_equivalence_loaded"),
          "| counts:", doc.get("ili_equivalence_counts"))
    npass = sum(1 for a in doc["assertions"] if a["passed"])
    print(f"asserções: {npass}/{len(doc['assertions'])} PASS "
          f"| all_passed={doc['all_passed']}")
    for a in doc["assertions"]:
        if not a["passed"]:
            print("  FAIL:", a["id"], a["text"])
    return 0 if doc["all_passed"] and s.get("merge_ok") else 1


if __name__ == "__main__":
    sys.exit(main())
