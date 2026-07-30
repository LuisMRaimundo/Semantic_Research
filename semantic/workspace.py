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

from . import settings
from .normalize import strip_accents


_SAFE = re.compile(r"[^A-Za-z0-9_\-]+")
# Clear folder name — sorts/looks like the deliverable, no emoji gimmicks.
FINAL_DIR_NAME = "FINAL_RESULTS__Onto_plus_PULO"
LEGACY_FINAL_DIR_NAMES = ("FINAL_RESULTS", "FINAL_RESULTS__Onto_plus_PULO")


def slug_class(name: str) -> str:
    """Folder-safe class id: accents fold to ASCII (Compósita → Composita)."""
    # Fold diacritics first — otherwise ó is dropped and Compósita → Compsita.
    s = strip_accents(name.strip()).replace(" ", "")
    s = _SAFE.sub("", s)
    if not s:
        raise ValueError("class name is empty")
    return s


def final_concordance_stem(class_id: str) -> str:
    return f"FINAL__Onto_plus_PULO__{class_id}"


def _renamed_artifact_name(name: str, old_id: str, new_id: str) -> Optional[str]:
    """If *name* is an artefact keyed by *old_id*, return the new filename."""
    final_prefix = f"FINAL__Onto_plus_PULO__{old_id}."
    if name.startswith(final_prefix):
        return f"FINAL__Onto_plus_PULO__{new_id}." + name[len(final_prefix):]
    prefix = f"{old_id}."
    if name.startswith(prefix):
        return f"{new_id}." + name[len(prefix):]
    return None


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
    ready = (
        (folder / "TERMOS.html").exists()
        or (folder / "TERMOS_PESQUISA.md").exists()
        or (folder / md_name).exists()
        or (folder / f"{(class_id or folder.parent.name)}.concordance.md").exists()
    )

    # Bright HTML — green when ready, amber when the folder is only a placeholder
    html = folder / "OPEN_ME__FINAL_RESULTS.html"
    try:
        if ready:
            banner_bg, border, tag_bg, tag_fg = (
                "#1B5E20", "#A5D6A7", "#C8E6C9", "#1B5E20"
            )
            tag, sub = "DELIVERABLE", (
                "TERMOS.html + TERMOS_PESQUISA.md/.csv — lista para o corpus "
                "(concordância = diagnóstico)"
            )
            body = (
                "<p><b>Produto final:</b></p><ul>"
                "<li><a href='TERMOS.html'>TERMOS.html</a> — "
                "consulta (secções A–F)</li>"
                "<li><a href='TERMOS_PESQUISA.md'>TERMOS_PESQUISA.md</a> — "
                "processamento</li>"
                "<li><a href='TERMOS_PESQUISA.csv'>TERMOS_PESQUISA.csv</a></li>"
                "</ul>"
                "<p><b>Diagnóstico:</b></p><ul>"
                f"<li><a href='{md_name}'>{md_name}</a></li>"
                f"<li><a href='{json_name}'>{json_name}</a></li>"
                "</ul>"
                "<p>Scratch: <code>out/</code> e <code>results/</code>.</p>"
            )
            tip = "FINAL RESULTS — TERMOS (DELIVERABLE)"
            local_name = "!!! FINAL RESULTS — TERMOS"
        else:
            banner_bg, border, tag_bg, tag_fg = (
                "#6D4C00", "#FFE082", "#FFE082", "#6D4C00"
            )
            tag, sub = "NOT READY", (
                "Folder exists, but no concordance yet — run the pipeline first"
            )
            body = (
                "<p><b>Why is this empty?</b></p>"
                "<ol>"
                "<li>Search lemmas in <b>PULO</b> and <b>Onto.PT</b> "
                "(needs an export under <code>exports/</code>).</li>"
                "<li>Mark senses (UF / RT / exclude / …) and Save.</li>"
                "<li>Click <b>Run</b> — LexWarrant needs <b>≥2</b> engine "
                "results (PULO + ONTO) before it writes the concordance here.</li>"
                "</ol>"
                f"<p>Expected files after a successful Run:</p><ul>"
                f"<li><code>{md_name}</code></li>"
                f"<li><code>{json_name}</code></li>"
                "</ul>"
            )
            tip = "FINAL RESULTS — empty until you Run (needs PULO + ONTO)"
            local_name = "… FINAL RESULTS (not ready)"
        html.write_text(
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>FINAL RESULTS — {class_id or 'class'}</title>"
            "<style>"
            "body{margin:0;font-family:Segoe UI,Arial,sans-serif;"
            f"background:{banner_bg};color:#fff}}"
            f".banner{{background:{banner_bg};padding:28px 32px;"
            f"border-bottom:8px solid {tag_bg}}}"
            "h1{margin:0 0 8px;font-size:28px;letter-spacing:.02em}"
            ".sub{opacity:.95;font-size:16px}"
            ".box{margin:28px;padding:20px 24px;background:#fff;color:#111;"
            f"border-radius:8px;border:4px solid {border}}}"
            f"a{{color:{tag_fg};font-weight:700;font-size:18px}}"
            "li{margin:10px 0}"
            f".tag{{display:inline-block;background:{tag_bg};color:{tag_fg};"
            "padding:4px 10px;border-radius:4px;font-weight:700;"
            "margin-bottom:12px}"
            "</style></head><body>"
            "<div class='banner'>"
            f"<div class='tag'>{tag}</div>"
            f"<h1>FINAL RESULTS — {class_id or 'class'}</h1>"
            f"<div class='sub'>{sub}</div>"
            "</div>"
            f"<div class='box'>{body}</div></body></html>\n",
            encoding="utf-8",
        )
    except OSError:
        pass

    start_here = folder / "00_OPEN_ME_FIRST.txt"
    try:
        if ready:
            start_here.write_text(
                "FINAL RESULTS — Onto.PT + PULO\n"
                "==============================\n\n"
                "This folder is the class DELIVERABLE.\n\n"
                f"1) Open:  OPEN_ME__FINAL_RESULTS.html  (green page)\n"
                f"2) Or open:  {md_name}\n\n"
                "WordNet/OEWN may be queried as a corroboration track;\n"
                "it only appears in the matrix when it contributes admitted forms.\n"
                "(source_available ≠ source_contributed_results)\n",
                encoding="utf-8",
            )
        else:
            start_here.write_text(
                "FINAL RESULTS — NOT READY YET\n"
                "==============================\n\n"
                "This folder is only a placeholder.\n"
                "There is no concordance until you:\n"
                "  1) Search in PULO + Onto.PT\n"
                "  2) Mark senses and Save\n"
                "  3) Click Run (needs ≥2 engine results)\n\n"
                f"Then look for:  {md_name}\n",
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
            f"InfoTip={tip}\n"
            "IconResource=%SystemRoot%\\System32\\imageres.dll,105\n"
            f"LocalizedResourceName={local_name}\n",
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
        root = settings.CLASSES_DIR / cid
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
        root = settings.CLASSES_DIR / cid
        if not root.exists():
            raise FileNotFoundError(f"No class workspace: {root}")
        return cls(cid, root)

    @classmethod
    def list_classes(cls) -> list[str]:
        if not settings.CLASSES_DIR.exists():
            return []
        return sorted(
            p.name for p in settings.CLASSES_DIR.iterdir()
            if p.is_dir() and (p / "class.json").exists()
        )

    def rename(self, new_class_id: str) -> "ClassWorkspace":
        """Rename this class (folder + identity) without touching curated content.

        Updates ``class_id`` / filename prefixes only. Leaves senses, terms,
        ``pref_label``, ``axis``, exports, and engine payloads unchanged
        (aside from the identity field inside JSON so merge still matches).
        """
        new_id = slug_class(new_class_id)
        old_id = self.class_id
        if new_id == old_id:
            return self
        dest = settings.CLASSES_DIR / new_id
        if dest.exists():
            raise FileExistsError(f"Class already exists: {dest}")
        if not self.root.exists():
            raise FileNotFoundError(f"No class workspace: {self.root}")

        self._rename_artifact_filenames(old_id, new_id)
        self._rewrite_identity_in_json(old_id, new_id)

        shutil.move(str(self.root), str(dest))
        ws = ClassWorkspace(new_id, dest)
        ws.ensure()  # refresh FINAL_RESULTS splash with new name
        return ws

    def _rename_artifact_filenames(self, old_id: str, new_id: str) -> None:
        """Rename files whose names are prefixed with the old class_id."""
        # deepest paths first so nested renames stay valid
        paths = sorted(
            (p for p in self.root.rglob("*") if p.is_file()),
            key=lambda p: len(p.parts),
            reverse=True,
        )
        for path in paths:
            new_name = _renamed_artifact_name(path.name, old_id, new_id)
            if new_name and new_name != path.name:
                target = path.with_name(new_name)
                if not target.exists():
                    path.rename(target)

    def _rewrite_identity_in_json(self, old_id: str, new_id: str) -> None:
        """Set class_id/class fields that still equal old_id — nothing else."""
        for path in self.root.rglob("*.json"):
            if not path.is_file():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(data, dict):
                continue
            changed = False
            if data.get("class_id") == old_id:
                data["class_id"] = new_id
                changed = True
            if data.get("class") == old_id:
                data["class"] = new_id
                changed = True
            if changed:
                path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
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
        adjud = [s for s in senses
                 if (s.get("source") or "").lower() in ("pulo", "onto")]
        decided = sum(1 for s in adjud if (s.get("decision") or "").strip())
        senses = adjud  # status totals ignore WordNet corroboration cards
        exports = list(self.exports.glob("*.json")) + list(
            self.exports.glob("*.facets.json")
        )
        # de-dupe if a file matched both globs
        exports = list({p.resolve(): p for p in exports}.values())
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
