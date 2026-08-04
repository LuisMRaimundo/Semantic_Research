"""Bundled lexical resource inventory (dumps + runtime DBs).

Runtime engines use SQLite / ``wn`` pins. Source dumps under the repo root are
registered here so ``sr doctor`` and ``sr resources`` can verify them.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

from . import settings

OWNPT_GITHUB = "https://github.com/own-pt/openWordnet-PT.git"


@dataclass
class ResourceSpec:
    id: str
    role: str  # runtime | dump | clone | index
    path_key: str
    default_rel: str
    required: bool
    note: str


CATALOG: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        "pulo_sqlite", "runtime", "pulo_sqlite",
        "engines/PULO Thesaurus GUI/pulo.sqlite", True,
        "PULO runtime DB (built from pulo.20160508.sql).",
    ),
    ResourceSpec(
        "pulo_sql_20160508", "dump", "pulo_sql_primary",
        "pulo.20160508.sql/pulo.20160508.sql", True,
        "MySQL dump — preferred PULO source.",
    ),
    ResourceSpec(
        "pulo_sql_20150502", "dump", "pulo_sql_secondary",
        "pulo.20150502.sql/pulo.20150502.sql", False,
        "Older PULO MySQL dump (reference only).",
    ),
    ResourceSpec(
        "onto_sqlite", "runtime", "onto_sqlite",
        "engines/ONTO/ontopt.sqlite", True,
        "Onto.PT / CONTO.PT runtime DB (includes ontopt06 = Onto.PT v0.6).",
    ),
    ResourceSpec(
        "onto_rdf", "dump", "onto_rdf",
        "OntoPTv0.6_rdf/OntoPTv0.6.rdfs", True,
        "Onto.PT v0.6 RDF/OWL dump (source; runtime uses ontopt.sqlite).",
    ),
    ResourceSpec(
        "ownpt_wn", "runtime", "own_pt",
        "own-pt:1.0.0", True,
        "OpenWordNet-PT via Python ``wn`` pin (not a filesystem path).",
    ),
    ResourceSpec(
        "ownpt_clone", "clone", "ownpt_dir",
        "openWordnet-PT", False,
        "Git clone of https://github.com/own-pt/openWordnet-PT (source/reference).",
    ),
    ResourceSpec(
        "papel_dir", "dump", "papel_dir",
        "PAPEL.v.3.5_utf8", True,
        "PAPEL 3.5 relation files (discovery source).",
    ),
    ResourceSpec(
        "papel_sqlite", "index", "papel_sqlite",
        "data/papel.sqlite", False,
        "Indexed PAPEL triples for workbench search (built on demand).",
    ),
)


def _cfg_path(cfg: dict[str, Any], key: str, default_rel: str) -> Path:
    raw = cfg.get(key) or default_rel
    if key == "own_pt":
        # pin string, not a path
        return settings.ROOT / "openWordnet-PT"
    return settings.resolve_path(raw)


def resolve_resource_paths(cfg: Optional[dict[str, Any]] = None) -> dict[str, Path]:
    cfg = cfg or settings.load_config()
    out: dict[str, Path] = {}
    for spec in CATALOG:
        if spec.id == "ownpt_wn":
            continue
        out[spec.id] = _cfg_path(cfg, spec.path_key, spec.default_rel)
    return out


def ensure_ownpt_clone(*, update: bool = False) -> dict[str, Any]:
    """Clone OpenWordNet-PT next to the code if missing."""
    cfg = settings.load_config()
    dest = _cfg_path(cfg, "ownpt_dir", "openWordnet-PT")
    if dest.exists() and (dest / ".git").exists():
        if update:
            try:
                subprocess.run(
                    ["git", "-C", str(dest), "pull", "--ff-only"],
                    check=False, capture_output=True, text=True, timeout=120,
                )
            except (OSError, subprocess.SubprocessError) as exc:
                return {"ok": True, "path": str(dest), "action": "present", "warn": str(exc)}
        return {"ok": True, "path": str(dest), "action": "present"}
    if dest.exists() and any(dest.iterdir()):
        return {"ok": True, "path": str(dest), "action": "present_no_git"}
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", OWNPT_GITHUB, str(dest)],
            check=True, capture_output=True, text=True, timeout=600,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "path": str(dest), "action": "clone_failed", "error": str(exc)}
    return {"ok": True, "path": str(dest), "action": "cloned"}


def ensure_papel_index(*, force: bool = False) -> dict[str, Any]:
    """Build ``data/papel.sqlite`` from PAPEL.v.3.5_utf8 if needed."""
    from .adapters.papel import build_papel_sqlite, PapelStore

    cfg = settings.load_config()
    src = _cfg_path(cfg, "papel_dir", "PAPEL.v.3.5_utf8")
    db = _cfg_path(cfg, "papel_sqlite", "data/papel.sqlite")
    if not src.is_dir():
        return {"ok": False, "error": f"PAPEL dir missing: {src}"}
    if db.exists() and not force:
        try:
            store = PapelStore(db)
            n = store.triple_count()
            store.close()
            if n > 0:
                return {"ok": True, "path": str(db), "action": "present", "n_triples": n}
        except Exception:  # noqa: BLE001
            pass
    info = build_papel_sqlite(src, db)
    info["action"] = "built"
    return info


def inventory(*, build_papel: bool = False, ensure_ownpt: bool = False) -> dict[str, Any]:
    cfg = settings.load_config()
    paths = resolve_resource_paths(cfg)
    items: list[dict[str, Any]] = []

    # wn pin
    own_pin = str(cfg.get("own_pt") or "own-pt:1.0.0")
    wn_ok = False
    wn_detail = ""
    try:
        import wn  # type: ignore
        installed = {f"{lex.id}:{lex.version}" for lex in wn.lexicons()}
        wn_ok = own_pin in installed
        wn_detail = f"pin={own_pin}; installed={wn_ok}"
    except Exception as exc:  # noqa: BLE001
        wn_detail = str(exc)
    items.append({
        "id": "ownpt_wn",
        "role": "runtime",
        "path": own_pin,
        "exists": wn_ok,
        "required": True,
        "integrated": True,
        "note": f"OpenWordNet-PT via wn — {wn_detail}",
    })

    if ensure_ownpt:
        clone_info = ensure_ownpt_clone()
    else:
        clone_info = None

    if build_papel:
        papel_info = ensure_papel_index()
    else:
        papel_info = None

    for spec in CATALOG:
        if spec.id == "ownpt_wn":
            continue
        p = paths[spec.id]
        exists = p.exists()
        integrated = False
        extra = ""
        if spec.id == "pulo_sqlite" and exists:
            integrated = True
            extra = "runtime PULO engine"
        elif spec.id == "onto_sqlite" and exists:
            integrated = True
            extra = "runtime Onto.PT engine (ontopt06 + CONTO/…)"
        elif spec.id.startswith("pulo_sql") and exists:
            integrated = True
            extra = "dump registered; runtime = pulo.sqlite"
        elif spec.id == "onto_rdf" and exists:
            integrated = True
            extra = "dump registered; runtime = ontopt.sqlite (ontopt06)"
        elif spec.id == "ownpt_clone":
            integrated = exists
            extra = "source clone; runtime still uses wn pin"
            if clone_info:
                extra += f" · {clone_info.get('action')}"
        elif spec.id == "papel_dir" and exists:
            integrated = True
            extra = "discovery via PapelStore when papel.sqlite built"
        elif spec.id == "papel_sqlite":
            integrated = exists
            if papel_info:
                extra = f"{papel_info.get('action')} n={papel_info.get('n_triples', papel_info.get('error'))}"
            elif exists:
                extra = "indexed"
            else:
                extra = "run: python sr.py resources --build-papel"

        items.append({
            "id": spec.id,
            "role": spec.role,
            "path": str(p),
            "exists": exists,
            "required": spec.required,
            "integrated": integrated and exists,
            "note": f"{spec.note} {extra}".strip(),
        })

    missing_req = [i for i in items if i["required"] and not i["exists"]]
    return {
        "root": str(settings.ROOT),
        "ok": not missing_req,
        "n_ok": sum(1 for i in items if i["exists"]),
        "n_missing_required": len(missing_req),
        "items": items,
        "ownpt_clone": clone_info,
        "papel_index": papel_info,
    }


def format_inventory(inv: dict[str, Any]) -> str:
    lines = ["# Lexical resources", "", f"root: `{inv['root']}`", ""]
    for i in inv["items"]:
        mark = "OK" if i["exists"] else ("MISS" if i["required"] else "opt ")
        integ = "integrated" if i.get("integrated") else "not-wired"
        lines.append(
            f"- [{mark}] `{i['id']}` ({i['role']}, {integ}): {i['path']}"
        )
        if i.get("note"):
            lines.append(f"    {i['note']}")
    lines += [
        "",
        f"**ok:** {inv['ok']} · present={inv['n_ok']} · "
        f"missing_required={inv['n_missing_required']}",
        "",
    ]
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="sr resources")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--build-papel", action="store_true")
    ap.add_argument("--ensure-ownpt", action="store_true")
    args = ap.parse_args(argv)
    inv = inventory(build_papel=args.build_papel, ensure_ownpt=args.ensure_ownpt)
    if args.json:
        print(json.dumps(inv, ensure_ascii=False, indent=2))
    else:
        print(format_inventory(inv))
    return 0 if inv["ok"] else 1
