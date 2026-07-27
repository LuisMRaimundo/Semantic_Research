"""R6/V4 — VERSION_MANIFEST.json (SHA-256 of critical artefacts)."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from . import settings

RELATIVE_TARGETS = [
    "sr.py",
    "config.json",
    "config.toml",
    "semantic/pipeline.py",
    "semantic/reconcile.py",
    "semantic/decisions.py",
    "semantic/export_blocks.py",
    "semantic/compile_specs.py",
    "semantic/cili_auto.py",
    "semantic/termos_pesquisa.py",
    "semantic/workbench.py",
    "semantic/wordnet_track.py",
    "semantic/settings.py",
    "semantic/manifest.py",
    "semantic/engines.py",
    "semantic/sense_index.py",
    "semantic/doctor.py",
    "semantic/onto_ili.py",
    "engines/LexWarrant/lexwarrant.py",
    "engines/LexWarrant/build_ili_equivalence.py",
    "engines/LexWarrant/cili_resolver.py",
    "engines/LexWarrant/data/cili/ili-map-pwn30.tab",
    "engines/ONTO/phase0_skos.py",
    "engines/PULO Thesaurus GUI/phase0_pulo.py",
]

CONFIG_PATH_KEYS = ("pulo_sqlite", "onto_sqlite")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_version_manifest(
    root: Optional[Path] = None,
    dest: Optional[Path] = None,
) -> dict[str, Any]:
    """Write VERSION_MANIFEST.json and return the manifest dict."""
    root = Path(root) if root else settings.ROOT
    cfg = settings.load_config()
    entries: list[dict[str, Any]] = []

    for rel in RELATIVE_TARGETS:
        path = root / rel
        if not path.exists():
            entries.append({"path": rel, "status": "missing"})
            continue
        entries.append({
            "path": rel.replace("\\", "/"),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "status": "ok",
        })

    for key in CONFIG_PATH_KEYS:
        raw = cfg.get(key)
        if not raw:
            entries.append({"path": f"config:{key}", "status": "missing_key"})
            continue
        path = Path(raw)
        rel_label = f"config:{key}"
        if not path.exists():
            entries.append({
                "path": rel_label,
                "resolved": str(path),
                "status": "missing",
            })
            continue
        entries.append({
            "path": rel_label,
            "resolved": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "status": "ok",
        })

    packages: dict[str, str] = {}
    try:
        import wn  # type: ignore
        packages["wn"] = getattr(wn, "__version__", "unknown")
    except Exception as exc:  # noqa: BLE001
        packages["wn"] = f"unavailable ({exc.__class__.__name__})"

    try:
        from .engines import cili_api
        version, counts_fn, _, _ = cili_api()
        packages["cili"] = version
        packages["cili_pairs"] = str(counts_fn().get("ili_ids", 0))
    except Exception as exc:  # noqa: BLE001
        packages["cili"] = f"unavailable ({exc.__class__.__name__})"

    packages["oewn_pin"] = str(cfg.get("oewn") or "")
    packages["own_pt_pin"] = str(cfg.get("own_pt") or "")

    manifest = {
        "schema": "semantic_research.version_manifest/2",
        "generated": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "packages": packages,
        "config_keys": {k: cfg.get(k) for k in (
            "pulo_sqlite", "onto_sqlite", "pulo_engine_dir",
            "onto_engine_dir", "lexwarrant_dir", "sense_index",
            "default_policy", "oewn", "own_pt",
        )},
        "artefacts": entries,
    }
    out = Path(dest) if dest else root / "VERSION_MANIFEST.json"
    out.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest["_path"] = str(out)
    manifest["_ok_count"] = sum(1 for e in entries if e.get("status") == "ok")
    return manifest
