"""Bundle FINAL_RESULTS for one-click export (ZIP + HTML folder picker)."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any, Optional

from .workspace import ClassWorkspace, FINAL_DIR_NAME

# Not re-exported into the bundle (self / OS noise)
_SKIP_NAMES = frozenset({
    "export_payload.js",
    "EXPORT_ALL.zip",
    "desktop.ini",
    "Thumbs.db",
})


def list_final_files(folder: Path) -> list[Path]:
    """Sorted text deliverables under FINAL_RESULTS (non-recursive)."""
    if not folder.is_dir():
        return []
    out: list[Path] = []
    for p in sorted(folder.iterdir(), key=lambda x: x.name.lower()):
        if not p.is_file():
            continue
        if p.name in _SKIP_NAMES or p.name.startswith("."):
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
    import shutil

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
