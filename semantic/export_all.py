"""Bundle FINAL_RESULTS and full class workspaces for one-click export."""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path
from typing import Any, Iterable, Optional

from .workspace import ClassWorkspace, FINAL_DIR_NAME

# Not re-exported into the bundle (self / OS noise)
_SKIP_NAMES = frozenset({
    "export_payload.js",
    "EXPORT_ALL.zip",
    "CLASS_EXPORT.zip",
    "desktop.ini",
    "Thumbs.db",
})

# Full-class export: everything the workbench shows / produces for a class
_CLASS_ROOT_FILES = (
    "class.json",
    "decisions.json",
    "termos_manuais.yaml",
    "termos_manuais.yml",
)
_CLASS_SUBDIRS = (
    "exports",          # PULO / Onto / WordNet search cards
    "results",          # engine result.json (+ ONTO-ILI if emitted)
    "out",              # concordance, ili_migration, onto_ili_proposals, …
    "_specs",           # compiled engine specs
    FINAL_DIR_NAME,     # deliverable TERMOS / CONCEPT / blocos
)


def list_final_files(folder: Path) -> list[Path]:
    """Sorted text deliverables under FINAL_RESULTS (non-recursive).

    Skips stale ``FINAL__….md/.json`` copies that lack ``.concordance`` —
    those pre-adjudication aliases contradict the current concordance.
    """
    if not folder.is_dir():
        return []
    out: list[Path] = []
    for p in sorted(folder.iterdir(), key=lambda x: x.name.lower()):
        if not p.is_file():
            continue
        if p.name in _SKIP_NAMES or p.name.startswith("."):
            continue
        # Stale alias: FINAL__Class.md / FINAL__Class.json (no .concordance)
        if p.name.startswith("FINAL__") and ".concordance." not in p.name:
            continue
        out.append(p)
    return out


def build_bundle_payload(folder: Path, *, class_id: str = "") -> dict[str, Any]:
    files: list[dict[str, str]] = []
    for path in list_final_files(folder):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # rare binary — skip rather than corrupt the JS payload
            continue
        except OSError:
            continue
        files.append({"name": path.name, "text": text})
    cid = class_id or folder.parent.name
    return {
        "class_id": cid,
        "folder_name": f"{cid}_{FINAL_DIR_NAME}",
        "source_dir": FINAL_DIR_NAME,
        "n_files": len(files),
        "files": files,
    }


def write_export_zip(folder: Path, *, class_id: str = "") -> Path:
    """Write ``EXPORT_ALL.zip`` next to TERMOS.html."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    zip_path = folder / "EXPORT_ALL.zip"
    files = list_final_files(folder)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, arcname=path.name)
        # include a tiny README inside the zip
        cid = class_id or folder.parent.name
        readme = (
            f"Semantic Research — export de {cid}\n"
            f"Pasta de origem: {FINAL_DIR_NAME}\n"
            f"Ficheiros: {len(files)}\n"
        )
        zf.writestr("00_README_EXPORT.txt", readme)
    return zip_path


def write_export_payload_js(folder: Path, *, class_id: str = "") -> Path:
    """Write ``export_payload.js`` loaded by TERMOS.html (works on file://)."""
    folder = Path(folder)
    payload = build_bundle_payload(folder, class_id=class_id)
    js_path = folder / "export_payload.js"
    body = (
        "/* Auto-generated — do not edit. Loaded by TERMOS.html for folder export. */\n"
        "window.SR_EXPORT_BUNDLE = "
        + json.dumps(payload, ensure_ascii=False)
        + ";\n"
    )
    js_path.write_text(body, encoding="utf-8")
    return js_path


def write_export_all(
    ws: ClassWorkspace,
    dest_dir: Optional[Path] = None,
) -> dict[str, str]:
    """Create ZIP + JS payload for the class FINAL_RESULTS folder."""
    folder = Path(dest_dir) if dest_dir else ws.final_results
    folder.mkdir(parents=True, exist_ok=True)
    zip_path = write_export_zip(folder, class_id=ws.class_id)
    js_path = write_export_payload_js(folder, class_id=ws.class_id)
    return {
        "zip": str(zip_path),
        "payload_js": str(js_path),
        "n_files": str(len(list_final_files(folder))),
    }


def copy_final_to_directory(
    ws: ClassWorkspace,
    dest_parent: Path,
) -> Path:
    """Copy FINAL_RESULTS into ``dest_parent/<Class>_FINAL_RESULTS__…``."""
    src = ws.final_results
    if not src.is_dir():
        raise FileNotFoundError(f"No FINAL_RESULTS folder: {src}")
    dest = Path(dest_parent) / f"{ws.class_id}_{FINAL_DIR_NAME}"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        src,
        dest,
        ignore=shutil.ignore_patterns(*_SKIP_NAMES, "desktop.ini"),
    )
    return dest


def _skip_path(path: Path) -> bool:
    name = path.name
    if name in _SKIP_NAMES or name.startswith("."):
        return True
    if name in {"__pycache__", ".git"}:
        return True
    return False


def iter_class_export_files(ws: ClassWorkspace) -> list[tuple[Path, str]]:
    """Return ``(absolute_path, archive_relative_posix)`` for a full class dump.

    Includes pref_label/axis (``class.json``), decisions, search exports
    (PULO/Onto/WordNet), engine results, ``out/`` (Onto→ILI, migration,
    concordance), ``_specs/``, and ``FINAL_RESULTS``.
    """
    root = ws.root
    pairs: list[tuple[Path, str]] = []
    seen: set[str] = set()

    def _add(abs_path: Path, rel: str) -> None:
        key = rel.replace("\\", "/")
        if key in seen or _skip_path(abs_path):
            return
        if not abs_path.is_file():
            return
        seen.add(key)
        pairs.append((abs_path, key))

    for name in _CLASS_ROOT_FILES:
        p = root / name
        if p.is_file():
            _add(p, name)

    for sub in _CLASS_SUBDIRS:
        folder = root / sub
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*")):
            if not path.is_file() or _skip_path(path):
                continue
            # skip nested noise dirs
            if any(part in _SKIP_NAMES or part == "__pycache__" for part in path.parts):
                continue
            rel = path.relative_to(root).as_posix()
            _add(path, rel)

    pairs.sort(key=lambda t: t[1].lower())
    return pairs


def class_export_manifest(ws: ClassWorkspace, files: Iterable[tuple[Path, str]]) -> str:
    rows = list(files)
    sections = {
        "meta": [r for _, r in rows if r in _CLASS_ROOT_FILES],
        "exports": [r for _, r in rows if r.startswith("exports/")],
        "results": [r for _, r in rows if r.startswith("results/")],
        "out": [r for _, r in rows if r.startswith("out/")],
        "specs": [r for _, r in rows if r.startswith("_specs/")],
        "final": [r for _, r in rows if r.startswith(f"{FINAL_DIR_NAME}/")],
    }
    lines = [
        f"Semantic Research — export completo da classe {ws.class_id}",
        "",
        "Conteúdo (espelho do workbench):",
        "  class.json / decisions.json     → pref_label, axis, concept_mapping, UF/RT",
        "  exports/                        → pesquisas PULO / Onto.PT / WordNet",
        "  results/                        → result.json dos motores (+ Onto→ILI se emitido)",
        "  out/                            → concordância, ili_migration, onto_ili_proposals, …",
        f"  {FINAL_DIR_NAME}/ → TERMOS, CONCEPT, blocos, coverage",
        "",
        f"Total de ficheiros: {len(rows)}",
        "",
    ]
    for title, keys in sections.items():
        lines.append(f"[{title}] {len(keys)}")
        for k in keys[:80]:
            lines.append(f"  - {k}")
        if len(keys) > 80:
            lines.append(f"  … (+{len(keys) - 80})")
        lines.append("")
    return "\n".join(lines)


def copy_class_workspace(
    ws: ClassWorkspace,
    dest_parent: Path,
) -> Path:
    """Copy the full class workspace into ``dest_parent/<Class>_FULL_EXPORT``."""
    dest = Path(dest_parent) / f"{ws.class_id}_FULL_EXPORT"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    files = iter_class_export_files(ws)
    if not files:
        raise FileNotFoundError(
            f"Classe {ws.class_id} sem conteúdos exportáveis "
            "(class.json / exports / results / FINAL)."
        )
    for src, rel in files:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    (dest / "00_README_CLASS_EXPORT.txt").write_text(
        class_export_manifest(ws, files), encoding="utf-8"
    )
    return dest


def write_class_workspace_zip(
    ws: ClassWorkspace,
    zip_path: Optional[Path] = None,
) -> Path:
    """Write a ZIP of the full class workspace (default: ``out/CLASS_EXPORT.zip``)."""
    files = iter_class_export_files(ws)
    if not files:
        raise FileNotFoundError(f"Classe {ws.class_id} sem conteúdos exportáveis.")
    out = Path(zip_path) if zip_path else (ws.out / "CLASS_EXPORT.zip")
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("00_README_CLASS_EXPORT.txt", class_export_manifest(ws, files))
        for src, rel in files:
            zf.write(src, arcname=rel)
    return out


def export_class_bundle(
    ws: ClassWorkspace,
    dest_parent: Path,
    *,
    also_zip: bool = True,
) -> dict[str, str]:
    """Full-class export (folder + optional ZIP) — independent of FINAL-only export."""
    folder = copy_class_workspace(ws, dest_parent)
    out: dict[str, str] = {
        "folder": str(folder),
        "n_files": str(len(iter_class_export_files(ws))),
    }
    if also_zip:
        zip_path = write_class_workspace_zip(
            ws,
            zip_path=Path(dest_parent) / f"{ws.class_id}_FULL_EXPORT.zip",
        )
        out["zip"] = str(zip_path)
    return out
