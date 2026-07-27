"""R9 — List likely-dead Python modules before deletion (report only)."""

from __future__ import annotations

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "cili-master",
    "WordNet",  # sibling toolkit; keep intact
    "tools",    # intentional CLI entry points (R6–R9)
}


def iter_py() -> list[Path]:
    out = []
    for p in ROOT.rglob("*.py"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    return out


def module_stem(path: Path) -> str:
    return path.stem


def collect_imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split(".")[0])
    return names


def main() -> int:
    files = iter_py()
    all_imports: set[str] = set()
    for f in files:
        all_imports |= collect_imports(f)

    # Also scan bat/md for script names
    text_blob = ""
    for pat in ("*.bat", "*.md", "sr.py"):
        for p in ROOT.glob(pat):
            try:
                text_blob += p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                pass
    for p in (ROOT / "README.md", ROOT / "start_workbench.bat"):
        if p.exists():
            text_blob += p.read_text(encoding="utf-8", errors="ignore")

    candidates = []
    # Focus on top-level / tools / engines helpers not imported by name
    watch = []
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith("tests/") or "/tests/" in rel:
            continue
        if rel.startswith("semantic/"):
            continue  # package modules — imported relatively
        if f.name in ("phase0_pulo.py", "phase0_skos.py", "lexwarrant.py",
                      "build_ili_equivalence.py", "cili_resolver.py",
                      "sr.py", "workbench.py"):
            continue
        watch.append(f)

    for f in watch:
        stem = f.stem
        rel = f.relative_to(ROOT).as_posix()
        imported = stem in all_imports
        mentioned = stem in text_blob or f.name in text_blob
        # heuristic: never imported and not mentioned → candidate
        if not imported and not mentioned:
            reason = "não importado nem referido em README/bat"
        elif not imported and mentioned:
            reason = "referido em docs/bat mas sem import Python (CLI?) — rever"
            # still list as review, not auto-delete
        else:
            continue
        candidates.append({
            "path": rel,
            "bytes": f.stat().st_size,
            "imported_as_module": imported,
            "mentioned_in_docs_or_bat": mentioned,
            "recommendation": (
                "candidato a remoção" if not mentioned else "rever antes de remover"
            ),
            "reason": reason,
        })

    # Explicit known orphans from recent work
    explicit = [
        "export_final.py",  # planned then abandoned; may be absent
    ]
    for name in explicit:
        hits = list(ROOT.rglob(name))
        for h in hits:
            if any(part in SKIP_DIRS for part in h.parts):
                continue
            rel = h.relative_to(ROOT).as_posix()
            if not any(c["path"] == rel for c in candidates):
                candidates.append({
                    "path": rel,
                    "bytes": h.stat().st_size,
                    "imported_as_module": False,
                    "mentioned_in_docs_or_bat": name in text_blob,
                    "recommendation": "candidato a remoção",
                    "reason": "módulo de export legado não ligado ao pipeline actual",
                })

    candidates.sort(key=lambda c: c["path"])
    report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "note": (
            "R9 — lista antes de remover. Nada foi apagado por este script. "
            "Confirmar cada item; CLI tools e finalizers podem ser invocados "
            "manualemente sem import."
        ),
        "candidates": candidates,
    }
    out = ROOT / "DEAD_CODE_CANDIDATES.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    md = ROOT / "DEAD_CODE_CANDIDATES.md"
    lines = [
        "# R9 — Candidatos a código morto (lista antes de remover)",
        "",
        report["note"],
        "",
        "| ficheiro | bytes | recomendação | motivo |",
        "|---|---:|---|---|",
    ]
    for c in candidates:
        lines.append(
            f"| `{c['path']}` | {c['bytes']} | {c['recommendation']} | {c['reason']} |"
        )
    if not candidates:
        lines.append("| _(nenhum)_ | | | |")
    lines.append("")
    md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out} ({len(candidates)} candidates)")
    for c in candidates:
        print(f"  - {c['path']}: {c['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
