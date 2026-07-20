#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI for Semantic Research workbench.

  sr new <Class> [--pref LABEL] [--axis TEXT]
  sr rename <OldClass> <NewClass>
  sr search <Class> <query> [--source pulo|onto|wordnet]
  sr status <Class>
  sr run <Class>
  sr list
  sr gui
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from semantic.pipeline import run_class, search_and_seed
from semantic.workspace import ClassWorkspace


def cmd_new(args):
    ws = ClassWorkspace.create(
        args.cls, pref_label=args.pref or "", axis=args.axis or "",
        focus_stems=[x.strip() for x in (args.stems or "").split(",") if x.strip()] or None,
    )
    print(f"Created {ws.root}")
    print(json.dumps(ws.status(), ensure_ascii=False, indent=2))
    return 0


def cmd_list(_args):
    for name in ClassWorkspace.list_classes():
        print(name)
    return 0


def cmd_rename(args):
    ws = ClassWorkspace.open(args.old)
    try:
        renamed = ws.rename(args.new)
    except (FileExistsError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Renamed {args.old} → {renamed.class_id}")
    print(json.dumps(renamed.status(), ensure_ascii=False, indent=2))
    return 0


def cmd_status(args):
    ws = ClassWorkspace.open(args.cls)
    print(json.dumps(ws.status(), ensure_ascii=False, indent=2))
    return 0


def cmd_search(args):
    info = search_and_seed(
        args.cls, args.query, source=args.source, mode=args.mode
    )
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


def cmd_run(args):
    engines = None
    if args.engine:
        engines = [args.engine]
    summary = run_class(args.cls, policy=args.policy, engines=engines)
    print(json.dumps(
        {k: v for k, v in summary.items() if k != "status"},
        ensure_ascii=False, indent=2,
    ))
    if summary.get("errors"):
        return 1
    return 0 if summary.get("merge_ok") else 2


def cmd_gui(_args):
    from semantic.workbench import main as gui_main
    return gui_main()


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(prog="sr", description="Semantic Research Fase 0")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new", help="create class workspace")
    p.add_argument("cls")
    p.add_argument("--pref", default="")
    p.add_argument("--axis", default="")
    p.add_argument("--stems", default="")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("list", help="list classes")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("rename", help="rename class (folder + id only)")
    p.add_argument("old", help="current class_id")
    p.add_argument("new", help="new class_id")
    p.set_defaults(func=cmd_rename)

    p = sub.add_parser("status", help="show next step")
    p.add_argument("cls")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("search", help="search lexicon and seed sense cards")
    p.add_argument("cls")
    p.add_argument("query")
    p.add_argument("--source", choices=("pulo", "onto", "wordnet"), default="pulo")
    p.add_argument("--mode", default="Starts with")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("run", help="compile + engines + LexWarrant")
    p.add_argument("cls")
    p.add_argument("--policy", default=None)
    p.add_argument("--engine", choices=("pulo", "onto"), default=None)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("gui", help="open workbench")
    p.set_defaults(func=cmd_gui)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
