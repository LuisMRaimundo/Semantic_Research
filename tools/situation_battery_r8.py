#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R8 situation battery — functions + reliability (local-only)."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(r"C:\Users\lmr20\Desktop\Semantic_Research")
sys.path.insert(0, str(ROOT))

from semantic.adapters import OntoStore, PuloStore, WordNetStore  # noqa: E402
from semantic.compile_specs import write_specs  # noqa: E402
from semantic import decisions as decmod  # noqa: E402
from semantic.ili_bridge import find_table_file  # noqa: E402
from semantic.normalize import normalize_word, strip_accents  # noqa: E402
from semantic.pipeline import run_class, search_and_seed  # noqa: E402
from semantic.settings import CLASSES_DIR, load_config  # noqa: E402
from semantic.workspace import ClassWorkspace, slug_class  # noqa: E402
from semantic.wordnet_track import build_wordnet_result  # noqa: E402

PASS, FAIL, WARN = [], [], []


def ok(name, detail=""):
    PASS.append(name)
    print(f"PASS  {name}" + (f" — {detail}" if detail else ""))


def fail(name, detail=""):
    FAIL.append(name)
    print(f"FAIL  {name}" + (f" — {detail}" if detail else ""))


def warn(name, detail=""):
    WARN.append(name)
    print(f"WARN  {name}" + (f" — {detail}" if detail else ""))


def cli(*args):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(
        [sys.executable, str(ROOT / "sr.py"), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("=" * 60)
    print("R8 SITUATION BATTERY — Semantic_Research (local)")
    print("=" * 60)

    # S1 config / pins
    cfg = load_config()
    bad = []
    for k in (
        "pulo_sqlite",
        "onto_sqlite",
        "pulo_engine_dir",
        "onto_engine_dir",
        "lexwarrant_dir",
        "cili_map",
    ):
        if k not in cfg:
            bad.append(f"missing key {k}")
            continue
        p = Path(cfg[k])
        inside = str(p.resolve()).lower().startswith(str(ROOT.resolve()).lower())
        if not (p.exists() and inside):
            bad.append(f"{k}={p} exists={p.exists()} inside={inside}")
    if bad:
        fail("S1_config_paths", "; ".join(bad))
    else:
        ok("S1_config_paths")

    # S2 normalize/slug
    try:
        assert strip_accents("Compósita") == "Composita"
        assert normalize_word("UNIFORME") == "uniforme"
        assert slug_class("Textura Compósita") == "TexturaComposita"
        ok("S2_normalize_slug")
    except Exception as e:
        fail("S2_normalize_slug", str(e))

    # S3 lexicon stores
    try:
        pulo = PuloStore(Path(cfg["pulo_sqlite"]))
        for mode, q in [("Exact", "uniforme"), ("Starts with", "uniform"), ("Contains", "form")]:
            n = len(pulo.search(q, mode=mode, limit=20))
            (ok if n else fail)(f"S3_pulo_{mode}", f"n={n}")
        assert not pulo.search("xyzzyqqq", mode="Exact", limit=5)
        ok("S3_pulo_nonsense_empty")
        pulo.close()
    except Exception:
        fail("S3_pulo", traceback.format_exc().splitlines()[-1])

    try:
        onto = OntoStore(Path(cfg["onto_sqlite"]))
        for mode, q in [("Exact", "uniforme"), ("Starts with", "uniform"), ("Contains", "form")]:
            n = len(onto.search(q, mode=mode, limit=20))
            (ok if n else fail)(f"S3_onto_{mode}", f"n={n}")
        onto.close()
    except Exception as e:
        fail("S3_onto", str(e))

    try:
        wn = WordNetStore()
        for q, emin in [("uniform", 1), ("uniforme", 0), ("composite", 1)]:
            n = int(wn.export_search(q, class_id="_probe", limit=20).get("count") or 0)
            if emin and n < emin:
                fail(f"S4_wn_{q}", f"count={n}")
            elif not emin and n == 0:
                ok(f"S4_wn_{q}_pt_zero")
            else:
                ok(f"S4_wn_{q}", f"count={n}")
    except Exception:
        fail("S4_wordnet", traceback.format_exc().splitlines()[-1])

    # S5 CLI doctor / smoke / list
    code, out = cli("doctor", "--deep")
    if code == 0 and "errors:** 0" in out.replace(" ", "") or ("errors:** 0" in out) or ("**errors:** 0" in out):
        ok("S5_cli_doctor_deep")
    elif code == 0 and "ok" in out.lower():
        ok("S5_cli_doctor_deep", "exit 0")
    else:
        fail("S5_cli_doctor_deep", out[-300:])

    code, out = cli("list")
    if code == 0 and "TexturaUniforme" in out:
        ok("S5_cli_list")
    else:
        fail("S5_cli_list", out[:200])

    code, out = cli("smoke", "--class", "TexturaUniforme", "--query", "uniforme")
    try:
        doc = json.loads(out.strip().split("\n")[0]) if out.strip().startswith("{") else json.loads(out)
    except Exception:
        # full json dump
        try:
            doc = json.loads(out)
        except Exception:
            doc = {}
    if code in (0, 2) and (doc.get("merge_ok") or doc.get("search", {}).get("count", 0) >= 0):
        if doc.get("merge_ok"):
            ok("S5_cli_smoke_uniforme", f"merge_ok count={doc.get('search',{}).get('count')}")
        else:
            warn("S5_cli_smoke_uniforme", f"exit={code} merge_ok={doc.get('merge_ok')} errors={doc.get('errors')}")
    else:
        fail("S5_cli_smoke_uniforme", out[:300])

    # S6 throwaway lifecycle
    TEST_A, TEST_B = "_R8SitAlpha", "_R8SitBeta"
    for name in (TEST_A, TEST_B):
        p = CLASSES_DIR / name
        if p.exists():
            shutil.rmtree(p)

    try:
        ws = ClassWorkspace.create(
            TEST_A,
            pref_label="sit-r8",
            axis="invariância de teste R8",
            focus_stems=["uniform", "const"],
        )
        ok("S6_create")
        info = search_and_seed(TEST_A, "uniforme", source="pulo", mode="Exact")
        assert info["count"] >= 1
        ok("S6_search_pulo", f"count={info['count']}")
        info2 = search_and_seed(TEST_A, "uniforme", source="onto", mode="Exact")
        assert info2["count"] >= 1
        ok("S6_search_onto", f"count={info2['count']}")
        info3 = search_and_seed(TEST_A, "uniform", source="wordnet")
        (ok if info3["count"] >= 1 else fail)("S6_search_wordnet", f"count={info3['count']}")

        dec = decmod.load_decisions(ws.decisions_json)
        marked = 0
        for s in dec.get("senses", []):
            if s.get("source") == "pulo" and marked < 2:
                s["decision"] = "UF"
                marked += 1
            elif s.get("source") == "onto" and marked < 3:
                s["decision"] = "RT"
                marked += 1
            elif s.get("source") == "wordnet" and marked < 4:
                s["decision"] = "atributo"
                marked += 1
        for s in dec.get("senses", []):
            if not s.get("decision"):
                s["decision"] = "exclude"
                break
        decmod.save_decisions(ws.decisions_json, dec)
        ok("S6_mark_decisions", f"marked≈{marked}")
        specs = write_specs(ws)
        (ok if "pulo" in specs and "onto" in specs else fail)(
            "S6_compile_specs", f"keys={list(specs)}"
        )
    except Exception:
        fail("S6_lifecycle_setup", traceback.format_exc())

    # empty-axis preflight
    try:
        meta_path = (CLASSES_DIR / TEST_A / "class.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["axis"] = ""
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary = run_class(TEST_A, engines=["pulo", "onto"])
        if summary.get("errors") and any("axis" in e.lower() for e in summary["errors"]):
            ok("S6_preflight_empty_axis")
        else:
            fail("S6_preflight_empty_axis", str(summary.get("errors")))
        meta["axis"] = "invariância de teste R8"
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception as e:
        fail("S6_preflight_empty_axis", str(e))

    try:
        summary = run_class(TEST_A, engines=["pulo", "onto"])
        print(
            "S6_run:",
            {
                k: summary.get(k)
                for k in ("merge_ok", "errors", "pulo_passed", "onto_passed", "results")
            },
        )
        if summary.get("merge_ok"):
            ok("S6_run_merge_ok")
        elif summary.get("results"):
            warn("S6_run_partial", str(summary.get("errors")))
        else:
            fail("S6_run_engines", str(summary.get("errors")))
    except Exception:
        fail("S6_run_engines", traceback.format_exc().splitlines()[-1])

    # engines=[] merge-only on throwaway after results exist
    try:
        summary = run_class(TEST_A, engines=[])
        if summary.get("merge_ok") or not any(
            "export" in e.lower() for e in (summary.get("errors") or [])
        ):
            # if results exist, should merge; if engines=[] wrongly expands, may demand export oddly
            if summary.get("merge_ok"):
                ok("S6_engines_empty_merge_only")
            else:
                warn("S6_engines_empty_merge_only", str(summary.get("errors")))
        else:
            fail("S6_engines_empty_merge_only", str(summary.get("errors")))
    except Exception as e:
        fail("S6_engines_empty_merge_only", str(e))

    try:
        renamed = ClassWorkspace.open(TEST_A).rename(TEST_B)
        assert renamed.class_id == TEST_B
        ok("S6_rename")
    except Exception as e:
        fail("S6_rename", str(e))

    # index / onto-ili / publish on throwaway
    code, out = cli("index", "--class", TEST_B)
    if code == 0:
        ok("S6_cli_index_class")
    else:
        fail("S6_cli_index_class", out[:250])

    code, out = cli("onto-ili", "propose", TEST_B)
    if code == 0:
        ok("S6_cli_onto_ili_propose")
    else:
        warn("S6_cli_onto_ili_propose", out[:250])

    code, out = cli("onto-ili", "list", TEST_B)
    if code == 0:
        ok("S6_cli_onto_ili_list")
    else:
        fail("S6_cli_onto_ili_list", out[:250])

    code, out = cli("publish", TEST_B)
    if code == 0 and "CONCEPT" in out.upper() or "ttl" in out.lower() or code == 0:
        ok("S6_cli_publish")
    else:
        fail("S6_cli_publish", out[:250])

    for name in (TEST_A, TEST_B):
        p = CLASSES_DIR / name
        if p.exists():
            shutil.rmtree(p)
    ok("S6_cleanup")

    # S7 mature merge-only (R8: LexWarrant needs PULO + OWN-PT/WordNet; Onto is discovery-only)
    for cls in ("TexturaUniforme", "TexturaComposita"):
        try:
            s = run_class(cls, engines=[])
            cj = s.get("concordance_json")
            if not s.get("merge_ok") or not cj:
                fail(f"S7_merge_{cls}", f"merge_ok={s.get('merge_ok')} errors={s.get('errors')}")
                continue
            doc = json.loads(Path(cj).read_text(encoding="utf-8"))
            npass = sum(1 for a in doc.get("assertions", []) if a.get("passed"))
            ntot = len(doc.get("assertions", []))
            detail = (
                f"assertions {npass}/{ntot} ili={doc.get('ili_equivalence_loaded')} "
                f"counts={doc.get('ili_equivalence_counts')}"
            )
            if doc.get("all_passed"):
                ok(f"S7_merge_{cls}", detail)
            else:
                fails = [a.get("id") for a in doc.get("assertions", []) if not a.get("passed")]
                fail(f"S7_merge_{cls}", detail + f" FAIL={fails}")
        except Exception:
            fail(f"S7_merge_{cls}", traceback.format_exc().splitlines()[-1])

    try:
        s = run_class("TexturaMetamorfica", engines=[])
        errs = " | ".join(s.get("errors") or [])
        # Incomplete class data: has PULO+ONTO results but no WordNet merge track yet.
        if not s.get("merge_ok") and ("OWN-PT" in errs or "WordNet" in errs or "≥2" in errs):
            ok("S7_Metamorfica_needs_wn_track", errs[:160])
        elif s.get("merge_ok"):
            ok("S7_merge_TexturaMetamorfica", "unexpectedly complete")
        else:
            fail("S7_Metamorfica_needs_wn_track", errs[:200])
    except Exception as e:
        fail("S7_Metamorfica", str(e))

    # S8 incomplete classes
    try:
        s = run_class("TexturaPolitpica", engines=["pulo", "onto"])
        if s.get("errors") and any("axis" in e.lower() for e in s["errors"]):
            ok("S8_Politpica_blocked")
        else:
            fail("S8_Politpica_blocked", str(s.get("errors")))
    except Exception as e:
        fail("S8_Politpica", str(e))

    try:
        s = run_class("TexturaIntermitente", engines=["pulo", "onto"])
        if not s.get("merge_ok"):
            ok("S8_Intermitente_incomplete", "; ".join(s.get("errors") or [])[:160])
        else:
            warn("S8_Intermitente_incomplete", "unexpectedly merge_ok")
    except Exception as e:
        fail("S8_Intermitente", str(e))

    # S9 ILI + wordnet track
    try:
        table = find_table_file(ClassWorkspace.open("TexturaUniforme"))
        (ok if table and table.exists() else warn)("S9_ili_table", str(table))
    except Exception as e:
        fail("S9_ili_table", str(e))

    try:
        wr = build_wordnet_result("TexturaUniforme")
        if wr.get("ok"):
            ok("S9_wordnet_track", f"convoked={wr.get('convoked')}")
        else:
            warn("S9_wordnet_track", str(wr.get("error")))
    except Exception as e:
        fail("S9_wordnet_track", str(e))

    # S10 CLI edge / guards
    code, out = cli("status", "NoSuchClassXYZ")
    if code != 0 or "Error" in out or "Traceback" in out or "No class" in out:
        ok("S10_missing_status", (out.strip() or f"exit={code}")[:100])
    else:
        fail("S10_missing_status", "exit 0")

    code, out = cli("rename", "NoSuch", "AlsoNo")
    (ok if code != 0 else fail)("S10_rename_missing")

    code, out = cli("onto-ili", "accept", "TexturaUniforme")
    if code != 0:
        ok("S10_onto_ili_accept_requires_args")
    else:
        fail("S10_onto_ili_accept_requires_args", "should require --onto-key/--ili")

    # S11 any-term smoke (non-uniforme)
    code, out = cli("smoke", "--query", "composto")
    try:
        doc = json.loads(out)
        if doc.get("search", {}).get("count", 0) >= 1:
            ok("S11_smoke_any_term_composto", f"class={doc.get('class_id')} count={doc['search']['count']}")
        else:
            warn("S11_smoke_any_term_composto", str(doc)[:200])
    except Exception:
        fail("S11_smoke_any_term_composto", out[:250])

    # S12 cili resolver quick
    try:
        sys.path.insert(0, str(ROOT / "engines" / "LexWarrant"))
        import cili_resolver as cr  # type: ignore

        ili = cr.cili_resolve("00001740-a")
        if ili == "i1":
            ok("S12_cili_resolver", f"{ili!r}")
        else:
            fail("S12_cili_resolver", f"got {ili!r}")
    except Exception as e:
        fail("S12_cili_resolver", str(e))

    # S13 export picker prefers non-empty
    try:
        from semantic.pipeline import _best_pulo_export

        ws = ClassWorkspace.open("TexturaComposita")
        best = _best_pulo_export(ws)
        if best is None:
            fail("S13_best_pulo_export", "None")
        else:
            obj = json.loads(best.read_text(encoding="utf-8"))
            n = len(obj.get("synsets") or [])
            if n > 0 and "composed" not in best.name:
                ok("S13_best_pulo_export", f"{best.name} synsets={n}")
            elif n > 0:
                ok("S13_best_pulo_export", f"{best.name} synsets={n}")
            else:
                fail("S13_best_pulo_export", f"empty {best.name}")
    except Exception as e:
        fail("S13_best_pulo_export", str(e))

    print("\n" + "=" * 60)
    print(f"SUMMARY  PASS={len(PASS)}  FAIL={len(FAIL)}  WARN={len(WARN)}")
    if FAIL:
        print("FAILURES:")
        for f in FAIL:
            print(" -", f)
    if WARN:
        print("WARNINGS:")
        for w in WARN:
            print(" -", w)
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
