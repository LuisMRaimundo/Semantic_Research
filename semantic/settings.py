"""Load shared config pointing at lexicon databases and engines.

R8 — Prefer ``config.toml`` when present; fall back to ``config.json``.
Paths may be relative to the repo root (preferred) or absolute.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONFIG_TOML = ROOT / "config.toml"
CONFIG_JSON = ROOT / "config.json"
CONFIG_PATH = CONFIG_TOML if CONFIG_TOML.exists() else CONFIG_JSON
CLASSES_DIR = ROOT / "classes"
DATA_DIR = ROOT / "data"

_PATH_KEYS = (
    "legacy_root",
    "pulo_sqlite",
    "onto_sqlite",
    "pulo_engine_dir",
    "onto_engine_dir",
    "lexwarrant_dir",
    "wordnet_dir",
    "sense_index",
    "cili_map",
    # Source dumps / optional indexes (repo-local)
    "pulo_sql_primary",
    "pulo_sql_secondary",
    "onto_rdf",
    "contopt_dir",
    "clip21_dir",
    "ownpt_dir",
    "papel_dir",
    "papel_sqlite",
)
_RUNTIME_KEYS = (
    "default_policy",
    "hide_pulo_signals",
    "sense_index_on_run",
    "weak_term_mode",
    "gloss_min",
    "publish_concept_model",
    "onto_ili_auto_accept",
    "onto_ili_auto_accept_min",
    "onto_ili_auto_accept_margin",
    "onto_ili_emit_min",
    "gloss_use_embeddings",
)
_PIN_KEYS = (
    "oewn",
    "oewn_companions",
    "own_pt",
    "cili_commit",
    "cili_min_pairs",
)
_LANGUAGE_KEYS = ("search_lang", "label_lang")
_DEFAULT_SEARCH_LANG = "en"
_DEFAULT_LABEL_LANG = "pt-PT"

_DEFAULTS: dict[str, Any] = {
    "pulo_sqlite": "engines/PULO Thesaurus GUI/pulo.sqlite",
    "onto_sqlite": "engines/ONTO/ontopt.sqlite",
    "pulo_engine_dir": "engines/PULO Thesaurus GUI",
    "onto_engine_dir": "engines/ONTO",
    "lexwarrant_dir": "engines/LexWarrant",
    "wordnet_dir": "WordNet",
    "sense_index": "data/sense_index.sqlite",
    "cili_map": "engines/LexWarrant/data/cili/ili-map-pwn30.tab",
    "pulo_sql_primary": "pulo.20160508.sql/pulo.20160508.sql",
    "pulo_sql_secondary": "pulo.20150502.sql/pulo.20150502.sql",
    "onto_rdf": "OntoPTv0.6_rdf/OntoPTv0.6.rdfs",
    "contopt_dir": "CONTO.PT/CONTO.PT.01",
    "clip21_dir": "CONTO.PT/clip21",
    "ownpt_dir": "openWordnet-PT",
    "papel_dir": "PAPEL.v.3.5_utf8",
    "papel_sqlite": "data/papel.sqlite",
    "default_policy": "conservative",
    "hide_pulo_signals": True,
    "sense_index_on_run": True,
    # weak(term): gloss_gated | off | legacy
    "weak_term_mode": "gloss_gated",
    "gloss_min": 0.12,
    "publish_concept_model": True,
    # Default off: weak Onto→ILI must not look like independent corroboration
    "onto_ili_auto_accept": False,
    "onto_ili_auto_accept_min": 0.85,
    "onto_ili_auto_accept_margin": 0.12,
    # Only emit Onto→ILI rows into LexWarrant at/above this score
    "onto_ili_emit_min": 0.85,
    # Opt-in: sentence-transformers multilingual MiniLM (may download weights)
    "gloss_use_embeddings": False,
    "oewn": "oewn:2025",
    # Comma-separated OEWN releases kept installed alongside the runtime pin
    "oewn_companions": "oewn:2024,oewn:2025+",
    "own_pt": "own-pt:1.0.0",
    "cili_commit": "eeab8003a3200e6293e8f7569de7d15a7a426d76",
    "cili_min_pairs": 117000,
    "search_lang": _DEFAULT_SEARCH_LANG,
    "label_lang": _DEFAULT_LABEL_LANG,
}


def resolve_path(raw: str | Path | None, *, root: Path | None = None) -> Path:
    """Resolve a config path: absolute stays; relative is under repo root."""
    base = Path(root) if root else ROOT
    if raw is None or str(raw).strip() == "":
        raise ValueError("empty path")
    p = Path(str(raw).strip())
    if p.is_absolute():
        return p
    return (base / p).resolve()


def _parse_simple_toml(text: str) -> dict[str, Any]:
    """Minimal TOML subset: [section] + key = \"str\" | true/false | int."""
    data: dict[str, Any] = {}
    section: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^\[([^\]]+)\]$", line)
        if m:
            section = m.group(1).strip()
            data.setdefault(section, {})
            continue
        if "=" not in line or section is None:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if val.startswith('"') and val.endswith('"'):
            parsed: Any = val[1:-1].replace("\\\\", "\\")
        elif val.lower() in ("true", "false"):
            parsed = val.lower() == "true"
        else:
            try:
                parsed = int(val) if "." not in val else float(val)
            except ValueError:
                try:
                    parsed = float(val)
                except ValueError:
                    parsed = val
        data[section][key] = parsed
    return data


def _from_toml(path: Path) -> dict[str, Any]:
    raw = _parse_simple_toml(path.read_text(encoding="utf-8"))
    paths = raw.get("paths") or {}
    runtime = raw.get("runtime") or {}
    pins = raw.get("pins") or {}
    languages = raw.get("languages") or {}
    out: dict[str, Any] = dict(_DEFAULTS)
    for k in _PATH_KEYS:
        if k in paths:
            out[k] = paths[k]
    for k in _RUNTIME_KEYS:
        if k in runtime:
            out[k] = runtime[k]
    for k in _PIN_KEYS:
        if k in pins:
            out[k] = pins[k]
    # cili_map may live under [pins] or [paths]
    if "cili_map" in pins:
        out["cili_map"] = pins["cili_map"]
    for k in _LANGUAGE_KEYS:
        if k in languages:
            out[k] = languages[k]
    out["_config_source"] = str(path)
    return out


def _normalize_loaded(data: dict[str, Any], source: Path) -> dict[str, Any]:
    out = dict(_DEFAULTS)
    out.update({k: v for k, v in data.items() if not str(k).startswith("_")})
    out["_config_source"] = str(source)
    # Resolve path keys to absolute Paths stored as strings for back-compat
    for k in _PATH_KEYS:
        if k in out and out[k]:
            try:
                out[k] = str(resolve_path(out[k]))
            except ValueError:
                pass
    try:
        out["gloss_min"] = float(out.get("gloss_min", 0.12))
    except (TypeError, ValueError):
        out["gloss_min"] = 0.12
    out["weak_term_mode"] = str(out.get("weak_term_mode") or "gloss_gated")
    out["publish_concept_model"] = bool(out.get("publish_concept_model", True))
    out["onto_ili_auto_accept"] = bool(out.get("onto_ili_auto_accept", False))
    try:
        out["onto_ili_auto_accept_min"] = float(
            out.get("onto_ili_auto_accept_min", 0.85)
        )
        out["onto_ili_auto_accept_margin"] = float(
            out.get("onto_ili_auto_accept_margin", 0.12)
        )
        out["onto_ili_emit_min"] = float(out.get("onto_ili_emit_min", 0.85))
    except (TypeError, ValueError):
        out["onto_ili_auto_accept_min"] = 0.85
        out["onto_ili_auto_accept_margin"] = 0.12
        out["onto_ili_emit_min"] = 0.85
    # Normalise companion OEWN pins to a list (TOML stores a CSV string).
    raw_comp = out.get("oewn_companions") or ""
    if isinstance(raw_comp, (list, tuple)):
        companions = [str(x).strip() for x in raw_comp if str(x).strip()]
    else:
        companions = [
            x.strip() for x in str(raw_comp).split(",") if x.strip()
        ]
    pin = str(out.get("oewn") or "oewn:2025").strip()
    companions = [c for c in companions if c != pin]
    out["oewn"] = pin
    out["oewn_companions"] = companions
    return out


def load_config() -> dict[str, Any]:
    if CONFIG_TOML.exists():
        return _normalize_loaded(_from_toml(CONFIG_TOML), CONFIG_TOML)
    if CONFIG_JSON.exists():
        data = json.loads(CONFIG_JSON.read_text(encoding="utf-8"))
        return _normalize_loaded(data, CONFIG_JSON)
    raise FileNotFoundError(
        f"Missing config.toml / config.json under {ROOT}"
    )


def resolve_languages(meta: dict[str, Any] | None = None) -> dict[str, str]:
    """Global languages with optional per-class override from class.json."""
    cfg = load_config()
    meta = meta or {}
    return {
        "search_lang": (
            (meta.get("search_lang") or cfg.get("search_lang") or _DEFAULT_SEARCH_LANG)
            .strip()
        ),
        "label_lang": (
            (meta.get("label_lang") or cfg.get("label_lang") or _DEFAULT_LABEL_LANG)
            .strip()
        ),
    }


def _rel_or_abs(path_str: str) -> str:
    """Prefer repo-relative form when path is under ROOT."""
    p = Path(path_str)
    try:
        return str(p.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p).replace("\\", "/")


def save_config(data: dict[str, Any]) -> None:
    """Persist to config.json and refresh config.toml (relative paths preferred)."""
    payload = {k: v for k, v in data.items() if not str(k).startswith("_")}
    for k in _PATH_KEYS:
        if k in payload and payload[k]:
            payload[k] = _rel_or_abs(str(payload[k]))

    CONFIG_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Semantic Research — path / runtime configuration (R8 / ~95)",
        "# Auto-synced from save_config(); prefer editing this file.",
        "# Paths are relative to the repo root unless absolute.",
        "",
        "[paths]",
    ]
    for k in _PATH_KEYS:
        if k == "legacy_root":
            continue
        if k in payload and payload[k]:
            val = str(payload[k]).replace("\\", "/")
            lines.append(f'{k} = "{val}"')
    lines += ["", "[runtime]"]
    pol = payload.get("default_policy", "conservative")
    hide = bool(payload.get("hide_pulo_signals", True))
    idx = bool(payload.get("sense_index_on_run", True))
    lines.append(f'default_policy = "{pol}"')
    lines.append(f"hide_pulo_signals = {'true' if hide else 'false'}")
    lines.append(f"sense_index_on_run = {'true' if idx else 'false'}")
    lines += ["", "[pins]"]
    lines.append(f'oewn = "{payload.get("oewn", "oewn:2025")}"')
    comps = payload.get("oewn_companions") or ["oewn:2024", "oewn:2025+"]
    if isinstance(comps, (list, tuple)):
        comps_s = ",".join(str(x).strip() for x in comps if str(x).strip())
    else:
        comps_s = str(comps).strip()
    lines.append(f'oewn_companions = "{comps_s}"')
    lines.append(f'own_pt = "{payload.get("own_pt", "own-pt:1.0.0")}"')
    cili_map = payload.get("cili_map", _DEFAULTS["cili_map"])
    lines.append(f'cili_map = "{_rel_or_abs(str(cili_map))}"')
    lines.append(f'cili_commit = "{payload.get("cili_commit", _DEFAULTS["cili_commit"])}"')
    lines.append(f'cili_min_pairs = {int(payload.get("cili_min_pairs", 117000))}')
    lines += ["", "[languages]"]
    lines.append(
        f'search_lang = "{payload.get("search_lang", _DEFAULT_SEARCH_LANG)}"'
    )
    lines.append(
        f'label_lang = "{payload.get("label_lang", _DEFAULT_LABEL_LANG)}"'
    )
    lines.append("")
    CONFIG_TOML.write_text("\n".join(lines), encoding="utf-8")


def path_from_config(key: str) -> Path:
    cfg = load_config()
    raw = cfg.get(key)
    if not raw:
        raise KeyError(f"config missing key: {key}")
    return Path(raw)
