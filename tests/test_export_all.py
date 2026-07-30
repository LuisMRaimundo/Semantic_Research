#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FINAL_RESULTS one-click export bundle."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

from semantic.export_all import (
    copy_final_to_directory,
    write_export_all,
    write_export_payload_js,
    write_export_zip,
)
from semantic.workspace import ClassWorkspace, FINAL_DIR_NAME


def test_export_zip_and_payload(tmp_path: Path):
    folder = tmp_path / FINAL_DIR_NAME
    folder.mkdir()
    (folder / "TERMOS.html").write_text("<html>ok</html>\n", encoding="utf-8")
    (folder / "TERMOS_PESQUISA.md").write_text("# termos\n", encoding="utf-8")
    (folder / "CONCEPT.ttl").write_text("@prefix : <#> .\n", encoding="utf-8")

    zip_path = write_export_zip(folder, class_id="Demo")
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    assert "TERMOS.html" in names
    assert "TERMOS_PESQUISA.md" in names
    assert "00_README_EXPORT.txt" in names
    assert "EXPORT_ALL.zip" not in names

    js_path = write_export_payload_js(folder, class_id="Demo")
    text = js_path.read_text(encoding="utf-8")
    assert text.startswith("/* Auto-generated")
    assert "window.SR_EXPORT_BUNDLE" in text
    payload = json.loads(text.split("=", 1)[1].rstrip().rstrip(";"))
    assert payload["class_id"] == "Demo"
    assert payload["n_files"] == 3
    names = {f["name"] for f in payload["files"]}
    assert names == {"TERMOS.html", "TERMOS_PESQUISA.md", "CONCEPT.ttl"}


def test_write_export_all_and_copy(tmp_path: Path, monkeypatch):
    classes = tmp_path / "classes"
    classes.mkdir()
    monkeypatch.setattr("semantic.settings.CLASSES_DIR", classes)
    monkeypatch.setattr("semantic.workspace.settings.CLASSES_DIR", classes)
    ws = ClassWorkspace.create("DemoClass", pref_label="demo", axis="x")
    (ws.final_results / "TERMOS.html").write_text("<html/>\n", encoding="utf-8")
    (ws.final_results / "a.md").write_text("a\n", encoding="utf-8")

    out = write_export_all(ws)
    assert Path(out["zip"]).exists()
    assert Path(out["payload_js"]).exists()

    dest_parent = tmp_path / "outbox"
    dest_parent.mkdir()
    copied = copy_final_to_directory(ws, dest_parent)
    assert copied.name == f"DemoClass_{FINAL_DIR_NAME}"
    assert (copied / "TERMOS.html").exists()
    assert (copied / "a.md").exists()
