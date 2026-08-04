"""Download and unpack required lexical dumps into the repo root.

Fetches:
  - PAPEL.v.3.5_utf8.zip  → PAPEL.v.3.5_utf8/
  - OntoPTv0.6_rdf.zip    → OntoPTv0.6_rdf/
Optionally builds data/papel.sqlite and clones openWordnet-PT.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "SemanticResearch-fetch/1.0"}

PAPEL_ZIP = "https://www.linguateca.pt/PAPEL/PAPEL.v.3.5_utf8.zip"
ONTO_RDF_ZIP = "https://ontopt.dei.uc.pt/recursos/OntoPTv0.6_rdf.zip"


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"GET {url}")
    req = Request(url, headers=UA)
    with urlopen(req, timeout=180) as resp, dest.open("wb") as out:
        shutil.copyfileobj(resp, out)
    print(f"  -> {dest} ({dest.stat().st_size:,} bytes)")
    return dest


def _looks_like_papel(dir_path: Path) -> bool:
    return bool(list(dir_path.glob("relacoes_final*.txt")))


def _looks_like_onto_rdf(dir_path: Path) -> bool:
    return (dir_path / "OntoPTv0.6.rdfs").is_file() or bool(
        list(dir_path.glob("*.rdfs"))
    )


def unpack_zip(zip_path: Path, target_dir: Path, kind: str) -> Path:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="sr_unpack_") as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp_path)
        # Prefer a single top-level folder if present
        children = [p for p in tmp_path.iterdir() if not p.name.startswith("__")]
        payload = children[0] if len(children) == 1 and children[0].is_dir() else tmp_path

        checker = _looks_like_papel if kind == "papel" else _looks_like_onto_rdf
        # Sometimes nested one more level
        if not checker(payload):
            nested = [p for p in payload.iterdir() if p.is_dir()]
            for cand in nested:
                if checker(cand):
                    payload = cand
                    break

        if not checker(payload):
            listing = ", ".join(sorted(p.name for p in payload.iterdir())[:20])
            raise RuntimeError(
                f"{kind}: unexpected zip layout under {payload} [{listing}]"
            )

        for item in payload.iterdir():
            dest = target_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    print(f"UNPACKED {kind} -> {target_dir}")
    return target_dir


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--papel", action="store_true", help="fetch PAPEL 3.5 utf8")
    ap.add_argument("--onto-rdf", action="store_true", help="fetch Onto.PT v0.6 RDF")
    ap.add_argument("--build-papel", action="store_true", help="index papel.sqlite")
    ap.add_argument("--ownpt", action="store_true", help="clone openWordnet-PT")
    ap.add_argument("--all", action="store_true", help="fetch all + build + clone")
    args = ap.parse_args()
    if args.all:
        args.papel = args.onto_rdf = args.build_papel = args.ownpt = True
    if not any((args.papel, args.onto_rdf, args.build_papel, args.ownpt)):
        args.all = True
        args.papel = args.onto_rdf = args.build_papel = args.ownpt = True

    sys.path.insert(0, str(ROOT))
    cache = ROOT / "_resource_cache"
    cache.mkdir(exist_ok=True)

    if args.papel:
        z = download(PAPEL_ZIP, cache / "PAPEL.v.3.5_utf8.zip")
        unpack_zip(z, ROOT / "PAPEL.v.3.5_utf8", "papel")

    if args.onto_rdf:
        z = download(ONTO_RDF_ZIP, cache / "OntoPTv0.6_rdf.zip")
        unpack_zip(z, ROOT / "OntoPTv0.6_rdf", "onto_rdf")

    if args.build_papel:
        from semantic.resources import ensure_papel_index

        info = ensure_papel_index(force=True)
        print("BUILD papel.sqlite:", info)
        if not info.get("ok"):
            return 1

    if args.ownpt:
        from semantic.resources import ensure_ownpt_clone

        info = ensure_ownpt_clone()
        print("OWN-PT clone:", info)

    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
