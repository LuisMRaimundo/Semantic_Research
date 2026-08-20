# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from semantic.onto_ili_export import export_onto_ili_report
from semantic.sense_index import SenseIndex
from semantic.workspace import ClassWorkspace


def test_onto_ili_export_writes_md_json_with_cili_links(tmp_path: Path, monkeypatch):
    classes = tmp_path / "classes"
    classes.mkdir()
    monkeypatch.setattr("semantic.settings.CLASSES_DIR", classes)
    monkeypatch.setattr("semantic.workspace.settings.CLASSES_DIR", classes)
    idx = tmp_path / "sense.sqlite"
    monkeypatch.setattr(
        "semantic.onto_ili.SenseIndex",
        lambda *a, **k: SenseIndex(idx),
    )
    ws = ClassWorkspace.create("DemoOntoIli", pref_label="w", axis="a")
    with SenseIndex(idx) as si:
        si.save_onto_proposal(
            onto_key="onto:ontopt06:10",
            ili="i1",
            score=0.56,
            method="lemma+gloss",
            evidence={"lemma_score": 0.5},
            class_id="DemoOntoIli",
            status="accepted",
        )
        si.save_onto_proposal(
            onto_key="onto:papel35:SINONIMIA:x",
            ili="i2",
            score=0.40,
            method="lemma+gloss",
            class_id="DemoOntoIli",
            status="proposed",
        )
    out = export_onto_ili_report(ws)
    assert out["total"] == 2
    assert out["accepted"] == 1
    assert out["proposed"] == 1
    md = Path(out["md"]).read_text(encoding="utf-8")
    js = Path(out["json"]).read_text(encoding="utf-8")
    assert "i1" in md and "onto:ontopt06:10" in md
    assert "globalwordnet.github.io/cili/i1" in md
    assert "cili/i1.html" not in md
    assert "accepted" in js and "proposed" in js


def test_reject_all_includes_accepted(tmp_path: Path, monkeypatch):
    from semantic.onto_ili import list_proposals, reject_all

    classes = tmp_path / "classes"
    classes.mkdir()
    monkeypatch.setattr("semantic.settings.CLASSES_DIR", classes)
    monkeypatch.setattr("semantic.workspace.settings.CLASSES_DIR", classes)
    idx = tmp_path / "sense.sqlite"
    monkeypatch.setattr(
        "semantic.onto_ili.SenseIndex",
        lambda *a, **k: SenseIndex(idx),
    )
    ClassWorkspace.create("DemoReject", pref_label="w", axis="a")
    with SenseIndex(idx) as si:
        si.save_onto_proposal(
            onto_key="onto:ontopt06:1", ili="i1", score=0.9,
            method="lemma+gloss", class_id="DemoReject", status="accepted",
        )
        si.save_onto_proposal(
            onto_key="onto:ontopt06:2", ili="i2", score=0.4,
            method="lemma+gloss", class_id="DemoReject", status="proposed",
        )
        si.save_onto_proposal(
            onto_key="onto:ontopt06:3", ili="i3", score=0.3,
            method="lemma+gloss", class_id="DemoReject", status="rejected",
        )
    out = reject_all("DemoReject")
    assert out["n"] == 2
    by_status = {p["ili"]: p["status"] for p in list_proposals("DemoReject")}
    assert by_status["i1"] == "rejected"
    assert by_status["i2"] == "rejected"
    assert by_status["i3"] == "rejected"
