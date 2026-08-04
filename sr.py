#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI for Semantic Research workbench (R8 / ~95).

  sr new <Class> [--pref LABEL] [--axis TEXT]
  sr rename <OldClass> <NewClass>
  sr search <Class> <query> [--source pulo|onto|papel|wordnet]
  sr status <Class>
  sr run <Class>
  sr index [--class Class] [--pulo-limit N]
  sr doctor [--deep] [--json]
  sr resources [--build-papel] [--ensure-ownpt] [--json]
  sr smoke [--class Class] [--query LEMMA]
  sr onto-ili list|accept|reject|accept-top <Class> ...
  sr publish [<Class>|--all]
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
    try:
        ws = ClassWorkspace.open(args.cls)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(ws.status(), ensure_ascii=False, indent=2))
    return 0


def cmd_search(args):
    try:
        info = search_and_seed(
            args.cls, args.query, source=args.source, mode=args.mode
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


def cmd_run(args):
    engines = None
    if args.engine:
        engines = [args.engine]
    try:
        summary = run_class(args.cls, policy=args.policy, engines=engines)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
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


def cmd_doctor(args):
    from semantic.doctor import format_report, run_doctor
    report = run_doctor(deep=args.deep)
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(report))
    return 0 if report.ok else 1


def cmd_resources(args):
    from semantic.resources import format_inventory, inventory
    inv = inventory(
        build_papel=args.build_papel,
        ensure_ownpt=args.ensure_ownpt,
    )
    if args.json:
        print(json.dumps(inv, ensure_ascii=False, indent=2))
    else:
        print(format_inventory(inv))
    return 0 if inv["ok"] else 1


def cmd_smoke(args):
    from semantic.smoke import run_smoke
    out = run_smoke(class_id=args.cls, query=args.query)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if out.get("errors"):
        return 1
    return 0 if out.get("merge_ok") else 2


def cmd_onto_ili(args):
    from semantic.onto_ili import (
        accept_top,
        list_proposals,
        propose_for_class,
        set_proposal_status,
    )

    if args.action == "propose":
        out = propose_for_class(args.cls)
    elif args.action == "list":
        out = {
            "class_id": args.cls,
            "proposals": list_proposals(args.cls, status=args.status),
        }
    elif args.action == "accept":
        if not args.onto_key or not args.ili:
            print("accept requires --onto-key and --ili", file=sys.stderr)
            return 2
        out = set_proposal_status(args.cls, args.onto_key, args.ili, "accepted")
    elif args.action == "reject":
        if not args.onto_key or not args.ili:
            print("reject requires --onto-key and --ili", file=sys.stderr)
            return 2
        out = set_proposal_status(args.cls, args.onto_key, args.ili, "rejected")
    elif args.action == "accept-top":
        out = accept_top(args.cls, n=args.n, min_score=args.min_score)
    else:
        print(f"unknown action: {args.action}", file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_publish(args):
    from semantic.concept_model import publish_class_concept, update_global_registry

    if args.all:
        out = {"registry": str(update_global_registry()), "classes": []}
        for name in ClassWorkspace.list_classes():
            out["classes"].append(
                publish_class_concept(name, update_registry=False)
            )
        out["registry"] = str(update_global_registry())
    elif args.cls:
        out = publish_class_concept(args.cls)
    else:
        out = {"registry": str(update_global_registry())}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_index(args):
    from semantic.onto_ili import propose_for_class
    from semantic.sense_index import (
        SenseIndex,
        build_index_from_pulo_db,
        ingest_class_exports,
    )

    with SenseIndex() as si:
        out: dict = {"index": str(si.path)}
        if args.pulo_limit is not None or args.full_pulo:
            limit = None if args.full_pulo else args.pulo_limit
            out["pulo_bulk"] = build_index_from_pulo_db(limit=limit, index=si)
        if args.cls:
            out["class"] = ingest_class_exports(args.cls, index=si)
            out["onto_ili"] = propose_for_class(args.cls, index=si)
        elif not args.full_pulo and args.pulo_limit is None:
            # default: ingest every class workspace
            classes = ClassWorkspace.list_classes()
            out["classes"] = {}
            for name in classes:
                out["classes"][name] = ingest_class_exports(name, index=si)
                propose_for_class(name, index=si)
            out["stats"] = si.stats()
        else:
            out["stats"] = si.stats()
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(prog="sr", description="Semantic Research R8 (~95)")
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
    p.add_argument(
        "--source",
        choices=("pulo", "onto", "papel", "wordnet"),
        default="pulo",
    )
    p.add_argument("--mode", default="Starts with")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("run", help="compile + engines + SenseIndex + LexWarrant")
    p.add_argument("cls")
    p.add_argument("--policy", default=None)
    p.add_argument("--engine", choices=("pulo", "onto"), default=None)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("doctor", help="health / pin / path checks")
    p.add_argument("--deep", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser(
        "resources",
        help="inventory lexical dumps (Onto RDF, PULO SQL, PAPEL, OWN-PT)",
    )
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--build-papel",
        action="store_true",
        help="index PAPEL.v.3.5_utf8 → data/papel.sqlite",
    )
    p.add_argument(
        "--ensure-ownpt",
        action="store_true",
        help="clone https://github.com/own-pt/openWordnet-PT if missing",
    )
    p.set_defaults(func=cmd_resources)

    p = sub.add_parser(
        "smoke",
        help="concept-agnostic search+merge probe (any class / any lemma)",
    )
    p.add_argument("--class", dest="cls", default=None)
    p.add_argument("--query", default=None, help="any lemma to search")
    p.set_defaults(func=cmd_smoke)

    p = sub.add_parser("index", help="build / refresh SenseIndex")
    p.add_argument("--class", dest="cls", default=None, help="one class_id")
    p.add_argument(
        "--pulo-limit", type=int, default=None,
        help="bulk-load first N PULO synsets into the index",
    )
    p.add_argument(
        "--full-pulo", action="store_true",
        help="bulk-load entire PULO lexicon (slow, ~118k synsets)",
    )
    p.set_defaults(func=cmd_index)

    p = sub.add_parser("gui", help="open workbench")
    p.set_defaults(func=cmd_gui)

    p = sub.add_parser(
        "onto-ili",
        help="Onto→ILI proposals: propose / list / accept / reject / accept-top",
    )
    p.add_argument(
        "action",
        choices=("propose", "list", "accept", "reject", "accept-top"),
    )
    p.add_argument("cls", help="class_id")
    p.add_argument("--onto-key", default=None, help="sense_key e.g. onto:TEP:42")
    p.add_argument("--ili", default=None, help="CILI id e.g. i12345")
    p.add_argument("--status", default=None, help="filter for list: proposed|accepted|rejected")
    p.add_argument("--n", type=int, default=5, help="accept-top count")
    p.add_argument("--min-score", type=float, default=0.6, help="accept-top min score")
    p.set_defaults(func=cmd_onto_ili)

    p = sub.add_parser("publish", help="write SKOS/OWL CONCEPT.ttl (+ registry)")
    p.add_argument("cls", nargs="?", default=None, help="class_id (omit = registry only)")
    p.add_argument("--all", action="store_true", help="publish every class + registry")
    p.set_defaults(func=cmd_publish)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
