"""Health checks for a ~95-reliable Semantic Research install."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from . import settings
from .engines import cili_api, clear_engine_caches, engine_paths, load_oewn_backend


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""
    level: str = "error"  # error | warn | info


@dataclass
class DoctorReport:
    checks: list[Check] = field(default_factory=list)

    @property
    def errors(self) -> list[Check]:
        return [c for c in self.checks if c.level == "error" and not c.ok]

    @property
    def warnings(self) -> list[Check]:
        return [c for c in self.checks if c.level == "warn" and not c.ok]

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "n_ok": sum(1 for c in self.checks if c.ok),
            "n_error": len(self.errors),
            "n_warn": len(self.warnings),
            "checks": [
                {"name": c.name, "ok": c.ok, "level": c.level, "detail": c.detail}
                for c in self.checks
            ],
        }


def _under_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(settings.ROOT.resolve())
        return True
    except ValueError:
        return False


def _own_pt_bridge_smoke(backend) -> tuple[bool, str]:
    """Return (ok, detail) if OWN-PT translate works for any probe lemma.

    Uses ``backend.synsets`` (SynsetAdapter) — not raw ``wn.Wordnet`` objects.
    Probe lemmas are high-frequency English closed-set items, not research targets.
    """
    if not hasattr(backend, "synsets"):
        return False, "backend.synsets missing"
    probes = ("able", "time", "water", "good", "person", "make", "see")
    tried = 0
    for lemma in probes:
        try:
            synsets = list(backend.synsets(lemma) or [])
        except Exception:  # noqa: BLE001
            continue
        for ss in synsets[:5]:
            tried += 1
            try:
                name = ss.name() if callable(getattr(ss, "name", None)) else str(ss)
                pt = list(ss.pt_lemmas() or [])
            except Exception as exc:  # noqa: BLE001
                return False, f"pt_lemmas raised on {lemma}: {exc}"
            if pt:
                return True, f"{name} → {pt[:4]} (probe lemma={lemma!r})"
    return False, f"no OWN-PT lemmas for probe set ({tried} synsets tried)"


def _append_cili_engine_checks(
    report: DoctorReport, cfg: dict[str, Any], root: Path, *, deep: bool
) -> None:
    """WP4 — one line per CILI lexicographical-engine check."""
    from engines.CILI.cili_engine import (
        CiliEngine,
        CONCEPT_RE,
        EXPECTED_CONCEPTS,
        fts5_available,
        load_pwn30_map,
        sha256_file,
    )

    missing_keys = [
        k for k in ("cili_root", "cili_omw_dir", "cili_pwn30_map")
        if not cfg.get(k)
    ]
    report.checks.append(Check(
        "cili_config",
        not missing_keys,
        "ok" if not missing_keys else f"missing keys: {missing_keys}",
        "error" if missing_keys else "info",
    ))

    try:
        eng = CiliEngine.from_config(cfg)
    except Exception as exc:  # noqa: BLE001
        report.checks.append(Check("cili_engine", False, str(exc), "error"))
        return

    ttl = eng.ili_ttl
    if not eng.root.is_dir():
        report.checks.append(Check(
            "cili_root", False,
            f"{eng.root} missing — [cili] root must be the folder that contains ili.ttl",
            "error",
        ))
    elif not ttl.exists():
        report.checks.append(Check(
            "cili_root", False,
            f"ili.ttl missing under {eng.root}",
            "error",
        ))
    else:
        report.checks.append(Check("cili_root", True, str(eng.root), "info"))

    if ttl.exists():
        if deep:
            try:
                text = ttl.read_text(encoding="utf-8")
                n = sum(1 for _ in CONCEPT_RE.finditer(text))
                lo, hi = EXPECTED_CONCEPTS * 0.99, EXPECTED_CONCEPTS * 1.01
                in_band = lo <= n <= hi
                report.checks.append(Check(
                    "cili_ili_ttl",
                    True,
                    f"{n} concepts (expect ~{EXPECTED_CONCEPTS})"
                    + ("" if in_band else " — newer/older release; reported, not failed"),
                    "info" if in_band else "warn",
                ))
            except Exception as exc:  # noqa: BLE001
                report.checks.append(Check(
                    "cili_ili_ttl", False, f"unparseable: {exc}", "error",
                ))
        else:
            report.checks.append(Check(
                "cili_ili_ttl", True, f"{ttl.name} present", "info",
            ))

    pwn = Path(cfg.get("cili_pwn30_map") or cfg.get("cili_map") or "")
    if not pwn.is_absolute():
        pwn = settings.resolve_path(pwn)
    if not pwn.exists():
        report.checks.append(Check(
            "cili_pwn30_map", False, f"{pwn} missing", "error",
        ))
    else:
        off2ili, _ = load_pwn30_map(pwn)
        report.checks.append(Check(
            "cili_pwn30_map",
            bool(off2ili),
            f"{pwn.name} · {len(off2ili)} pairs",
            "error" if not off2ili else "info",
        ))

    dump_map = eng.dump_pwn30_map
    if pwn.exists() and dump_map.exists() and dump_map.resolve() != pwn.resolve():
        live_h = sha256_file(pwn)
        dump_h = sha256_file(dump_map)
        if live_h != dump_h:
            report.checks.append(Check(
                "cili_pwn30_map_hash",
                False,
                f"live {pwn} ({live_h[:12]}) ≠ dump {dump_map} ({dump_h[:12]}) "
                "— identity joins use the configured live map",
                "warn",
            ))
        else:
            report.checks.append(Check(
                "cili_pwn30_map_hash", True, "live and dump pwn30 maps match", "info",
            ))

    if eng.index_is_fresh():
        report.checks.append(Check(
            "cili_index", True, str(eng.index_path), "info",
        ))
    elif eng.index_path.exists():
        report.checks.append(Check(
            "cili_index",
            False,
            f"stale {eng.index_path} — run `python sr.py cili index`",
            "warn",
        ))
    else:
        report.checks.append(Check(
            "cili_index",
            False,
            f"missing — run `python sr.py cili index` ({eng.index_path})",
            "error" if ttl.exists() else "warn",
        ))

    pin = str(cfg.get("cili") or "").strip()
    meta = eng.meta() if eng.index_path.exists() else {}
    current = meta.get("ili_ttl_sha256_prefix") or (
        sha256_file(ttl)[:12] if ttl.exists() else ""
    )
    if not pin:
        report.checks.append(Check(
            "cili_pin",
            True,
            "unset — will be written on first `sr cili index`",
            "info",
        ))
    elif current and pin != current:
        report.checks.append(Check(
            "cili_pin",
            False,
            f"pin {pin} ≠ ili.ttl {current} (not auto-updated)",
            "warn",
        ))
    else:
        report.checks.append(Check(
            "cili_pin", True, pin or current, "info",
        ))

    langs = []
    if eng.index_path.exists():
        try:
            langs = list(eng.stats().get("languages") or [])
        except Exception:  # noqa: BLE001
            langs = eng.discovered_languages()
    else:
        langs = eng.discovered_languages()
    report.checks.append(Check(
        "cili_languages",
        bool(langs),
        ", ".join(langs) if langs else "none found",
        "warn" if not langs else "info",
    ))

    fts = fts5_available()
    report.checks.append(Check(
        "cili_fts5",
        fts,
        "available" if fts else "SQLite FTS5 missing in this Python build",
        "error" if not fts else "info",
    ))


def run_doctor(*, deep: bool = False) -> DoctorReport:
    """Run install / pin / lexicon checks. ``deep`` hits SQLite + wn translate."""
    clear_engine_caches()
    report = DoctorReport()
    cfg = settings.load_config()
    root = settings.ROOT

    report.checks.append(Check(
        "config", True, f"source={cfg.get('_config_source')}", "info",
    ))

    paths = engine_paths()
    for key in (
        "pulo_sqlite", "onto_sqlite", "pulo_engine", "onto_engine",
        "lexwarrant", "wordnet", "cili_map",
    ):
        p = paths[key]
        exists = p.exists()
        inside = _under_root(p)
        if not exists:
            report.checks.append(Check(f"path:{key}", False, f"{p} (missing)", "error"))
        elif not inside:
            report.checks.append(Check(
                f"path:{key}", True,
                f"{p} (outside repo — prefer relative paths)", "warn",
            ))
        else:
            report.checks.append(Check(f"path:{key}", True, str(p), "info"))

    _append_cili_engine_checks(report, cfg, root, deep=deep)

    dup = root / "cili-master"
    qdup = root / "_quarantine" / "cili-master"
    cili_root_cfg = Path(cfg.get("cili_root") or "")
    dump_is_engine_root = False
    try:
        dump_is_engine_root = bool(
            cili_root_cfg
            and cili_root_cfg.resolve().is_relative_to((root / "cili-master").resolve())
        )
    except Exception:  # noqa: BLE001
        dump_is_engine_root = "cili-master" in str(cili_root_cfg).replace("\\", "/")
    if dump_is_engine_root and dup.exists():
        report.checks.append(Check(
            "cili_duplicate", True,
            f"cili-master/ is the configured [cili] root ({cili_root_cfg})",
            "info",
        ))
    elif dup.exists():
        report.checks.append(Check(
            "cili_duplicate", False,
            f"{dup} still present — move to _quarantine/ or delete "
            "(live identity map is engines/LexWarrant/data/cili/)",
            "warn",
        ))
    elif qdup.exists():
        report.checks.append(Check(
            "cili_duplicate", True, f"quarantined at {qdup}", "info",
        ))
    else:
        report.checks.append(Check(
            "cili_duplicate", True, "no stray cili-master/ dump", "info",
        ))

    try:
        version, counts_fn, resolve_fn, _ = cili_api()
        counts = counts_fn()
        n = int(counts.get("ili_ids") or 0)
        min_pairs = int(cfg.get("cili_min_pairs") or 117000)
        report.checks.append(Check(
            "cili_pairs", n >= min_pairs,
            f"{version} · {n} ili_ids (min {min_pairs})",
            "error" if n < min_pairs else "info",
        ))
        sample = resolve_fn("00001740-a")
        report.checks.append(Check(
            "cili_resolve", sample == "i1",
            f"00001740-a → {sample!r} (expect 'i1')", "error",
        ))
    except Exception as exc:  # noqa: BLE001
        report.checks.append(Check("cili", False, str(exc), "error"))

    pin_oewn = str(cfg.get("oewn") or "oewn:2025")
    companions = list(cfg.get("oewn_companions") or [])
    pin_own = str(cfg.get("own_pt") or "own-pt:1.0.0")
    try:
        import wn  # type: ignore

        installed = {f"{l.id}:{l.version}" for l in wn.lexicons()}
        report.checks.append(Check(
            "oewn_pin", pin_oewn in installed,
            f"want {pin_oewn}; installed="
            f"{sorted(x for x in installed if x.startswith('oewn:'))}",
            "error" if pin_oewn not in installed else "info",
        ))
        missing_comp = [c for c in companions if c not in installed]
        present_comp = [c for c in companions if c in installed]
        report.checks.append(Check(
            "oewn_companions",
            not missing_comp,
            (
                f"runtime={pin_oewn}; companions ok={present_comp}"
                + (f"; missing={missing_comp}" if missing_comp else "")
            ),
            "warn" if missing_comp else "info",
        ))
        unexpected = sorted(
            x for x in installed
            if x.startswith("oewn:") and x != pin_oewn and x not in companions
        )
        if unexpected:
            report.checks.append(Check(
                "oewn_unexpected", True,
                f"extra OEWN releases not listed as companions: {unexpected}",
                "info",
            ))
        report.checks.append(Check(
            "own_pt_pin", pin_own in installed,
            f"want {pin_own}; present={pin_own in installed}",
            "error" if pin_own not in installed else "info",
        ))
        backend = load_oewn_backend()
        if hasattr(backend, "set_oewn_pin"):
            backend.set_oewn_pin(pin_oewn, hard=True)
        active = backend.ensure_oewn()
        report.checks.append(Check(
            "oewn_active", active == pin_oewn,
            f"ensure_oewn() → {active} (runtime pin; companions kept installed)",
            "error" if active != pin_oewn else "info",
        ))
        if deep and pin_own in installed:
            # Concept-agnostic: OWN-PT translate must yield lemmas for *some* OEWN synset.
            ok_bridge, detail = _own_pt_bridge_smoke(backend)
            report.checks.append(Check(
                "own_pt_bridge", ok_bridge, detail,
                "error" if not ok_bridge else "info",
            ))
    except Exception as exc:  # noqa: BLE001
        report.checks.append(Check("wn", False, str(exc), "error"))

    idx = paths["sense_index"]
    if idx.exists():
        try:
            from .sense_index import SenseIndex

            with SenseIndex(idx) as si:
                stats = si.stats()
            report.checks.append(Check(
                "sense_index", True, f"{idx.name} · {stats}", "info",
            ))
        except Exception as exc:  # noqa: BLE001
            report.checks.append(Check("sense_index", False, str(exc), "warn"))
    else:
        report.checks.append(Check(
            "sense_index", False,
            f"missing — run `python sr.py index` ({idx})", "warn",
        ))

    # Bundled source dumps (Onto RDF, PULO SQL, PAPEL, OWN-PT clone)
    try:
        from .resources import inventory

        inv = inventory()
        for item in inv["items"]:
            if item["id"] in ("pulo_sqlite", "onto_sqlite", "ownpt_wn"):
                continue  # already covered above
            level = "error" if item["required"] and not item["exists"] else (
                "warn" if not item["exists"] else "info"
            )
            report.checks.append(Check(
                f"resource:{item['id']}",
                bool(item["exists"]) or not item["required"],
                f"{item['path']} — {item.get('note') or item['role']}",
                level,
            ))
    except Exception as exc:  # noqa: BLE001
        report.checks.append(Check("resources", False, str(exc), "warn"))

    if deep:
        import sqlite3

        for key, label in (("pulo_sqlite", "PULO"), ("onto_sqlite", "ONTO")):
            try:
                db = paths[key]
                con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
                n = con.execute("SELECT COUNT(*) FROM synset").fetchone()[0]
                con.close()
                report.checks.append(Check(
                    f"db_rows:{label}", n > 0, f"{n} synset rows", "info",
                ))
            except Exception as exc:  # noqa: BLE001
                report.checks.append(Check(
                    f"db_rows:{label}", False, str(exc), "error",
                ))
        papel_db = Path(cfg.get("papel_sqlite") or (root / "data" / "papel.sqlite"))
        if not papel_db.is_absolute():
            papel_db = settings.resolve_path(papel_db)
        if papel_db.exists():
            try:
                con = sqlite3.connect(f"file:{papel_db}?mode=ro", uri=True)
                n = con.execute("SELECT COUNT(*) FROM triple").fetchone()[0]
                con.close()
                report.checks.append(Check(
                    "db_rows:PAPEL", n > 0, f"{n} triples", "info",
                ))
            except Exception as exc:  # noqa: BLE001
                report.checks.append(Check(
                    "db_rows:PAPEL", False, str(exc), "warn",
                ))

    try:
        from .compile_specs import axis_terms_exclusive_to_exclude
        from .decisions import load_decisions
        from .workspace import ClassWorkspace

        for cid in ClassWorkspace.list_classes():
            try:
                ws = ClassWorkspace.open(cid)
                bad = axis_terms_exclusive_to_exclude(
                    ws.load_meta(), load_decisions(ws.decisions_json)
                )
            except Exception as exc:  # noqa: BLE001
                report.checks.append(Check(
                    f"axis_terms:{cid}", False, str(exc), "warn",
                ))
                continue
            if bad:
                report.checks.append(Check(
                    f"axis_terms:{cid}",
                    False,
                    f"termos só de acepções exclude: {bad[:16]}",
                    "warn",
                ))
    except Exception as exc:  # noqa: BLE001
        report.checks.append(Check("axis_terms", False, str(exc), "warn"))

    return report


def format_report(report: DoctorReport) -> str:
    lines = ["# Semantic Research doctor", ""]
    for c in report.checks:
        mark = "OK  " if c.ok else ("WARN" if c.level == "warn" else "FAIL")
        lines.append(f"- [{mark}] {c.name}: {c.detail}")
    lines += [
        "",
        f"**errors:** {len(report.errors)} · **warnings:** {len(report.warnings)} · "
        f"**ok:** {report.ok}",
        "",
    ]
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="sr doctor")
    ap.add_argument("--deep", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    report = run_doctor(deep=args.deep)
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(report))
    return 0 if report.ok else 1
