"""One class = one folder.

Daily curated file: decisions.json
Deliverable:       FINAL_RESULTS/  (Onto + PULO concordance)
Scratch:           out/ · exports/ · results/ · _specs/
"""

from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .settings import CLASSES_DIR


_SAFE = re.compile(r"[^A-Za-z0-9_\-]+")
# Clear folder name — sorts/looks like the deliverable, no emoji gimmicks.
FINAL_DIR_NAME = "FINAL_RESULTS__Onto_plus_PULO"
LEGACY_FINAL_DIR_NAMES = ("FINAL_RESULTS", "FINAL_RESULTS__Onto_plus_PULO")


def slug_class(name: str) -> str:
    s = _SAFE.sub("", name.strip().replace(" ", ""))
    if not s:
        raise ValueError("class name is empty")
    return s


def final_concordance_stem(class_id: str) -> str:
    return f"FINAL__Onto_plus_PULO__{class_id}"


def _write_final_folder_marker(folder: Path, class_id: str = "") -> None:
    """Highlight FINAL_RESULTS: clear names + bright HTML splash + Explorer tip."""
    folder.mkdir(parents=True, exist_ok=True)
    # Remove old gimmick readme if present
    for old in folder.glob("*READ ME*"):
        try:
            old.unlink()
        except OSError:
            pass
    for old in folder.glob("*★*"):
        try:
            old.unlink()
        except OSError:
            pass

    stem = final_concordance_stem(class_id or folder.parent.name)
    md_name = f"{stem}.concordance.md"
    json_name = f"{stem}.concordance.json"

    # Bright HTML — opens in browser with unmistakable green banner
    html = folder / "OPEN_ME__FINAL_RESULTS.html"
    try:
        html.write_text(
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>FINAL RESULTS — {class_id or 'class'}</title>"
            "<style>"
            "body{margin:0;font-family:Segoe UI,Arial,sans-serif;"
            "background:#0d3b1e;color:#fff}"
            ".banner{background:#1B5E20;padding:28px 32px;"
            "border-bottom:8px solid #C8E6C9}"
            "h1{margin:0 0 8px;font-size:28px;letter-spacing:.02em}"
            ".sub{opacity:.95;font-size:16px}"
            ".box{margin:28px;padding:20px 24px;background:#fff;color:#111;"
            "border-radius:8px;border:4px solid #A5D6A7}"
            "a{color:#1B5E20;font-weight:700;font-size:18px}"
            "li{margin:10px 0}"
            ".tag{display:inline-block;background:#C8E6C9;color:#1B5E20;"
            "padding:4px 10px;border-radius:4px;font-weight:700;"
            "margin-bottom:12px}"
            "</style></head><body>"
            "<div class='banner'>"
            "<div class='tag'>DELIVERABLE</div>"
            f"<h1>FINAL RESULTS — {class_id or 'class'}</h1>"
            "<div class='sub'>Onto.PT + PULO concordance "
            "(this is the result that matters)</div>"
            "</div>"
            "<div class='box'><p><b>Open the concordance:</b></p><ul>"
            f"<li><a href='{md_name}'>{md_name}</a> — human-readable</li>"
            f"<li><a href='{json_name}'>{json_name}</a> — machine JSON</li>"
            "</ul>"
            "<p>Scratch files (signals, engine dumps) are <b>not</b> here — "
            "they live in <code>out/</code> and <code>results/</code>.</p>"
            "</div></body></html>\n",
            encoding="utf-8",
        )
    except OSError:
        pass

    start_here = folder / "00_OPEN_ME_FIRST.txt"
    try:
        start_here.write_text(
            "FINAL RESULTS — Onto.PT + PULO\n"
            "==============================\n\n"
            "This folder is the class DELIVERABLE.\n\n"
            f"1) Open:  OPEN_ME__FINAL_RESULTS.html  (green page)\n"
            f"2) Or open:  {md_name}\n\n"
            "WordNet is not included unless you add it later.\n",
            encoding="utf-8",
        )
    except OSError:
        pass

    desktop = folder / "desktop.ini"
    try:
        os.system(f'attrib -h -s -r "{desktop}" >NUL 2>&1')
        os.system(f'attrib -r "{folder}" >NUL 2>&1')
        desktop.write_text(
            "[.ShellClassInfo]\n"
            "ConfirmFileOp=0\n"
            "InfoTip=FINAL RESULTS — Onto.PT + PULO concordance (DELIVERABLE)\n"
            "IconResource=%SystemRoot%\\System32\\imageres.dll,105\n"
            "LocalizedResourceName=!!! FINAL RESULTS — Onto + PULO\n",
            encoding="utf-8",
        )
        os.system(f'attrib +s "{folder}" >NUL 2>&1')
        os.system(f'attrib +h +s "{desktop}" >NUL 2>&1')
    except OSError:
        pass


@dataclass
class ClassWorkspace:
    class_id: str
    root: Path

    @classmethod
    def create(cls, class_id: str, pref_label: str = "", axis: str = "",
               focus_stems: Optional[list[str]] = None) -> "ClassWorkspace":
        cid = slug_class(class_id)
        root = CLASSES_DIR / cid
        for sub in ("exports", "results", "out", "_specs", FINAL_DIR_NAME):
            (root / sub).mkdir(parents=True, exist_ok=True)
        _write_final_folder_marker(root / FINAL_DIR_NAME, cid)
        meta = {
            "class_id": cid,
            "pref_label": pref_label or cid,
            "axis": axis or "",
            "focus_stems": focus_stems or [],
            "axis_terms": [],
            "disjoint_classes": {},
        }
        meta_path = root / "class.json"
        if not meta_path.exists():
            meta_path.write_text(
                json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        dec_path = root / "decisions.json"
        if not dec_path.exists():
            blank = {
                "class_id": cid,
                "senses": [],
                "terms": [],
                "manual_terms": [],
                "exclude_terms": [],
            }
            dec_path.write_text(
                json.dumps(blank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        return cls(cid, root)

    @classmethod
    def open(cls, class_id: str) -> "ClassWorkspace":
        cid = slug_class(class_id)
        root = CLASSES_DIR / cid
        if not root.exists():
            raise FileNotFoundError(f"No class workspace: {root}")
        return cls(cid, root)

    @classmethod
    def list_classes(cls) -> list[str]:
        if not CLASSES_DIR.exists():
            return []
        return sorted(
            p.name for p in CLASSES_DIR.iterdir()
            if p.is_dir() and (p / "class.json").exists()
        )

    def ensure(self) -> None:
        self._migrate_legacy_final()
        for sub in ("exports", "results", "out", "_specs", FINAL_DIR_NAME):
            (self.root / sub).mkdir(parents=True, exist_ok=True)
        _write_final_folder_marker(self.final_results, self.class_id)

    def _migrate_legacy_final(self) -> None:
        """Move old FINAL_RESULTS → FINAL_RESULTS__Onto_plus_PULO if needed."""
        new = self.root / FINAL_DIR_NAME
        old = self.root / "FINAL_RESULTS"
        if old.exists() and old.resolve() != new.resolve():
            new.mkdir(parents=True, exist_ok=True)
            for p in old.iterdir():
                if p.name.lower() == "desktop.ini":
                    continue
                dest = new / p.name
                if not dest.exists():
                    try:
                        shutil.move(str(p), str(dest))
                    except OSError:
                        try:
                            shutil.copy2(p, dest)
                        except OSError:
                            pass
            # leave empty old folder or remove if empty
            try:
                if not any(old.iterdir()):
                    old.rmdir()
            except OSError:
                pass

    @property
    def class_json(self) -> Path:
        return self.root / "class.json"

    @property
    def decisions_json(self) -> Path:
        return self.root / "decisions.json"

    @property
    def exports(self) -> Path:
        return self.root / "exports"

    @property
    def results(self) -> Path:
        return self.root / "results"

    @property
    def out(self) -> Path:
        return self.root / "out"

    @property
    def specs(self) -> Path:
        return self.root / "_specs"

    @property
    def final_results(self) -> Path:
        return self.root / FINAL_DIR_NAME

    def concordance_md(self) -> Path:
        """Preferred: FINAL highlighted name, else plain, else out/."""
        stem = final_concordance_stem(self.class_id)
        for cand in (
            self.final_results / f"{stem}.concordance.md",
            self.final_results / f"{self.class_id}.concordance.md",
            self.out / f"{self.class_id}.concordance.md",
        ):
            if cand.exists():
                return cand
        return self.final_results / f"{stem}.concordance.md"

    def concordance_json(self) -> Path:
        stem = final_concordance_stem(self.class_id)
        for cand in (
            self.final_results / f"{stem}.concordance.json",
            self.final_results / f"{self.class_id}.concordance.json",
            self.out / f"{self.class_id}.concordance.json",
        ):
            if cand.exists():
                return cand
        return self.final_results / f"{stem}.concordance.json"

    def publish_final_results(self, md_path: Path, json_path: Path) -> dict[str, str]:
        """Copy Onto+PULO concordance into the highlighted FINAL folder."""
        self.ensure()
        stem = final_concordance_stem(self.class_id)
        dest_md = self.final_results / f"{stem}.concordance.md"
        dest_json = self.final_results / f"{stem}.concordance.json"
        if Path(md_path).exists():
            shutil.copy2(md_path, dest_md)
        if Path(json_path).exists():
            shutil.copy2(json_path, dest_json)
        # also keep short aliases for convenience
        alias_md = self.final_results / f"{self.class_id}.concordance.md"
        alias_json = self.final_results / f"{self.class_id}.concordance.json"
        try:
            shutil.copy2(dest_md, alias_md)
            shutil.copy2(dest_json, alias_json)
        except OSError:
            pass
        _write_final_folder_marker(self.final_results, self.class_id)
        return {
            "md": str(dest_md),
            "json": str(dest_json),
            "html": str(self.final_results / "OPEN_ME__FINAL_RESULTS.html"),
            "folder": str(self.final_results),
        }

    def load_meta(self) -> dict[str, Any]:
        return json.loads(self.class_json.read_text(encoding="utf-8"))

    def save_meta(self, data: dict[str, Any]) -> None:
        data = dict(data)
        data["class_id"] = self.class_id
        self.class_json.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def status(self) -> dict[str, Any]:
        self.ensure()
        meta = self.load_meta()
        senses = []
        terms = []
        if self.decisions_json.exists():
            dec = json.loads(self.decisions_json.read_text(encoding="utf-8"))
            senses = dec.get("senses") or []
            terms = dec.get("terms") or []
        decided = sum(1 for s in senses if (s.get("decision") or "").strip())
        exports = list(self.exports.glob("*.json"))
        results = {
            "PULO": next(self.results.glob("*.PULO.result.json"), None)
                    or next(self.results.glob("PULO/*.result.json"), None),
            "ONTO": next(self.results.glob("*.ONTO.result.json"), None)
                    or next(self.results.glob("ONTO/*.result.json"), None),
        }
        for label, alt in (
            ("PULO", self.results / f"{self.class_id}.PULO.result.json"),
            ("ONTO", self.results / f"{self.class_id}.ONTO.result.json"),
        ):
            if alt.exists():
                results[label] = alt
        for p in self.results.glob("*.result.json"):
            name = p.name.upper()
            if "PULO" in name and results["PULO"] is None:
                results["PULO"] = p
            if "ONTO" in name and results["ONTO"] is None:
                results["ONTO"] = p
        concordance = self.concordance_md()
        return {
            "class_id": self.class_id,
            "pref_label": meta.get("pref_label"),
            "axis": meta.get("axis"),
            "exports": len(exports),
            "senses_total": len(senses),
            "senses_decided": decided,
            "terms": len(terms),
            "has_pulo_result": results["PULO"] is not None
            and Path(results["PULO"]).exists(),
            "has_onto_result": results["ONTO"] is not None
            and Path(results["ONTO"]).exists(),
            "has_concordance": concordance.exists(),
            "final_results": str(self.final_results),
            "next_step": self._next(decided, len(senses), results, concordance),
        }

    def _next(self, decided, total, results, concordance: Path) -> str:
        if total == 0:
            return "Search a term (PULO and/or ONTO) and mark senses."
        if decided < total:
            return f"Mark remaining senses ({decided}/{total} decided), then Run."
        if not (results["PULO"] and Path(results["PULO"]).exists()):
            return "Click Run (needs at least a PULO track with ILI)."
        if concordance.exists():
            return (
                "Done — open FINAL_RESULTS/ "
                f"({self.class_id}.concordance.md = Onto+PULO deliverable)."
            )
        return "Click Run to compile specs, run engines, and merge."
