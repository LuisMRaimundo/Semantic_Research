#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the consolidated layout: unit tests + doctor + concept-agnostic smoke."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

SR = Path(__file__).resolve().parent
LEX = SR / "engines" / "LexWarrant"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verify Semantic Research pipeline")
    ap.add_argument("--class", dest="cls", default=None, help="class_id to smoke")
    ap.add_argument("--query", default=None, help="lemma to search (any term)")
    args = ap.parse_args(argv)

    sys.stdout.reconfigure(encoding="utf-8")
    r = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=str(LEX), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    print("== unittest discover (engines/LexWarrant/tests) ==")
    tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
    print("\n".join(tail[-6:]))
    if r.returncode != 0:
        print("UNIT TESTS FAILED")
        return 1

    sys.path.insert(0, str(SR))
    from semantic.doctor import format_report, run_doctor
    from semantic.settings import ROOT, load_config
    from semantic.smoke import run_smoke

    assert ROOT.resolve() == SR.resolve(), (ROOT, SR)
    cfg = load_config()
    for k in (
        "pulo_sqlite", "onto_sqlite", "pulo_engine_dir",
        "onto_engine_dir", "lexwarrant_dir", "cili_map",
    ):
        p = Path(cfg[k])
        inside = str(p.resolve()).lower().startswith(str(SR.resolve()).lower())
        print(f"{'OK ' if p.exists() and inside else 'BAD'} {k}: {p}")
        if not (p.exists() and inside):
            return 1

    report = run_doctor(deep=True)
    print(format_report(report))
    if not report.ok:
        print("DOCTOR FAILED")
        return 1

    smoke = run_smoke(class_id=args.cls, query=args.query)
    print(
        f"smoke class={smoke['class_id']!r} query={smoke['query']!r} "
        f"→ {smoke['search'].get('count')} synsets"
    )
    print("merge_ok:", smoke.get("merge_ok"), "| errors:", smoke.get("errors"))
    if smoke.get("sense_index"):
        print("sense_index:", smoke["sense_index"])

    conc = smoke.get("concordance_json")
    if not conc or not Path(conc).exists():
        print("No concordance produced (need ≥2 mergeable sources on that class).")
        return 0 if smoke.get("merge_ok") else 1

    doc = json.loads(Path(conc).read_text(encoding="utf-8"))
    print(
        "legacy_equivalence loaded:",
        doc.get("legacy_equivalence_loaded", doc.get("ili_equivalence_loaded")),
        "| counts:",
        doc.get("legacy_equivalence_counts") or doc.get("ili_equivalence_counts"),
        "| join_counts:",
        doc.get("join_counts"),
    )
    npass = sum(1 for a in doc["assertions"] if a["passed"])
    print(
        f"asserções: {npass}/{len(doc['assertions'])} PASS "
        f"| all_passed={doc['all_passed']}"
    )
    for a in doc["assertions"]:
        if not a["passed"]:
            print("  FAIL:", a["id"], a["text"])
    return 0 if doc["all_passed"] and smoke.get("merge_ok") else 1


if __name__ == "__main__":
    sys.exit(main())
