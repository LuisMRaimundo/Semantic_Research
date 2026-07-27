"""R8 — Diagnose Onto.PT sqlite resources (empty vs populated)."""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from semantic.settings import load_config

    cfg = load_config()
    db = Path(cfg["onto_sqlite"])
    report: dict = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "db": str(db),
        "exists": db.exists(),
        "resources": [],
        "notes": [],
    }
    if not db.exists():
        report["notes"].append("onto_sqlite missing")
        out = ROOT / "ONTO_RESOURCES_DIAGNOSIS.json"
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print(out)
        return 1

    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    tables = [
        r[0]
        for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1"
        )
    ]
    report["tables"] = tables

    # Catalogue from resource table (includes empty registrations).
    catalogue: list[tuple[str, str, str]] = []
    if "resource" in tables:
        cols = {r[1] for r in con.execute("PRAGMA table_info(resource)")}
        code_col = "code" if "code" in cols else ("res" if "res" in cols else None)
        name_col = "name" if "name" in cols else None
        kind_col = "kind" if "kind" in cols else None
        if code_col:
            for row in con.execute(
                f"SELECT {code_col}"
                + (f", {name_col}" if name_col else ", ''")
                + (f", {kind_col}" if kind_col else ", ''")
                + " FROM resource ORDER BY 1"
            ):
                catalogue.append((str(row[0]), str(row[1] or ""), str(row[2] or "")))

    syn_counts: dict[str, int] = {}
    mem_counts: dict[str, int] = {}
    if "synset" in tables:
        for row in con.execute(
            "SELECT res, COUNT(*) AS n FROM synset GROUP BY res"
        ):
            syn_counts[str(row["res"])] = int(row["n"])
    if "member" in tables:
        for row in con.execute(
            "SELECT res, COUNT(*) AS n FROM member GROUP BY res"
        ):
            mem_counts[str(row["res"])] = int(row["n"])

    # Also include any res that appear in synset/member but not in catalogue
    codes = {c for c, _n, _k in catalogue} | set(syn_counts) | set(mem_counts)
    if not catalogue:
        catalogue = [(c, "", "") for c in sorted(codes)]

    rows = []
    empty = []
    for code, name, kind in catalogue:
        syn = syn_counts.get(code, 0)
        mem = mem_counts.get(code, 0)
        if syn == 0 and mem == 0:
            status = "empty"
        elif syn == 0:
            status = "empty_synsets"
        else:
            status = "ok"
        item = {
            "res": code,
            "name": name,
            "kind": kind,
            "synsets": syn,
            "members": mem,
            "status": status,
        }
        rows.append(item)
        if status != "ok":
            empty.append(item)
    # orphan data rows not in catalogue
    for code in sorted(codes - {c for c, _, _ in catalogue}):
        syn = syn_counts.get(code, 0)
        mem = mem_counts.get(code, 0)
        status = "ok" if syn else "empty"
        item = {
            "res": code,
            "name": "",
            "kind": "",
            "synsets": syn,
            "members": mem,
            "status": status,
        }
        rows.append(item)
        if status != "ok":
            empty.append(item)

    report["resources"] = rows
    report["empty_or_degenerate"] = empty
    report["notes"].append(
        "Fuzzy path in phase0_skos defaults to contopt; empty resources are "
        "harmless if not listed in fuzzy_resources / not used as seeds."
    )
    # Which resources appear in class specs
    used: set[str] = set()
    for spec in (ROOT / "classes").glob("*/_specs/*.onto.json"):
        try:
            data = json.loads(spec.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for r in data.get("fuzzy_resources") or []:
            used.add(str(r))
    report["fuzzy_resources_in_specs"] = sorted(used)
    report["empty_but_referenced_in_specs"] = [
        e["res"] for e in empty if e["res"] in used
    ]

    con.close()
    out_json = ROOT / "ONTO_RESOURCES_DIAGNOSIS.json"
    out_md = ROOT / "ONTO_RESOURCES_DIAGNOSIS.md"
    out_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Diagnóstico de recursos Onto.PT",
        "",
        f"- DB: `{db}`",
        f"- Gerado: {report['generated']}",
        "",
        "| recurso | nome | kind | synsets | members | estado |",
        "|---|---|---|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| `{r['res']}` | {r.get('name') or '—'} | {r.get('kind') or '—'} | "
            f"{r['synsets']} | {r['members']} | {r['status']} |"
        )
    lines += [
        "",
        f"**Vazios / degenerados:** {len(empty)}",
        f"**Referenciados em specs e vazios:** "
        f"{report['empty_but_referenced_in_specs'] or '—'}",
        "",
        report["notes"][0],
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(f"empty={len(empty)} referenced_empty={report['empty_but_referenced_in_specs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
