"""Central engine / lexicon import boundary (no ad-hoc sys.path in callers).

Engines still live under ``engines/`` and ``WordNet/`` as plain modules; this
loader adds those directories once and caches imports.
"""

from __future__ import annotations

import importlib
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any

from .settings import ROOT, load_config


def _ensure_on_path(directory: Path) -> None:
    s = str(directory.resolve())
    if s not in sys.path:
        sys.path.insert(0, s)


@lru_cache(maxsize=1)
def engine_paths() -> dict[str, Path]:
    cfg = load_config()
    return {
        "pulo_engine": Path(cfg["pulo_engine_dir"]),
        "onto_engine": Path(cfg["onto_engine_dir"]),
        "lexwarrant": Path(cfg["lexwarrant_dir"]),
        "wordnet": Path(cfg.get("wordnet_dir") or (ROOT / "WordNet")),
        "pulo_sqlite": Path(cfg["pulo_sqlite"]),
        "onto_sqlite": Path(cfg["onto_sqlite"]),
        "cili_map": Path(cfg["cili_map"]),
        "sense_index": Path(cfg["sense_index"]),
    }


def ensure_engine_paths() -> dict[str, Path]:
    paths = engine_paths()
    for key in ("pulo_engine", "onto_engine", "lexwarrant", "wordnet"):
        if not paths[key].exists():
            raise FileNotFoundError(f"Engine path missing ({key}): {paths[key]}")
    return paths


@lru_cache(maxsize=1)
def load_phase0_pulo() -> ModuleType:
    paths = ensure_engine_paths()
    _ensure_on_path(paths["pulo_engine"])
    return importlib.import_module("phase0_pulo")


@lru_cache(maxsize=1)
def load_phase0_skos() -> ModuleType:
    paths = ensure_engine_paths()
    _ensure_on_path(paths["onto_engine"])
    return importlib.import_module("phase0_skos")


@lru_cache(maxsize=1)
def load_lexwarrant() -> ModuleType:
    paths = ensure_engine_paths()
    _ensure_on_path(paths["lexwarrant"])
    return importlib.import_module("lexwarrant")


@lru_cache(maxsize=1)
def load_cili_resolver() -> ModuleType:
    paths = ensure_engine_paths()
    _ensure_on_path(paths["lexwarrant"])
    return importlib.import_module("cili_resolver")


@lru_cache(maxsize=1)
def load_oewn_backend() -> ModuleType:
    paths = ensure_engine_paths()
    _ensure_on_path(paths["wordnet"])
    return importlib.import_module("oewn_backend")


def cili_api() -> tuple[str, Any, Any, Any]:
    """Return (version, counts_fn, resolve_fn, offset_fn)."""
    mod = load_cili_resolver()
    return (
        getattr(mod, "CILI_VERSION", "unknown"),
        mod.cili_counts,
        mod.cili_resolve,
        getattr(mod, "cili_offset", None),
    )


def clear_engine_caches() -> None:
    """Test helper — drop cached imports/paths."""
    engine_paths.cache_clear()
    load_phase0_pulo.cache_clear()
    load_phase0_skos.cache_clear()
    load_lexwarrant.cache_clear()
    load_cili_resolver.cache_clear()
    load_oewn_backend.cache_clear()
