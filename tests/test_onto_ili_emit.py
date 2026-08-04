#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Onto→ILI emit must not promote weak scores as atestado."""
from __future__ import annotations

import json
from pathlib import Path

from semantic.onto_ili import emit_onto_ili_result
from semantic.sense_index import SenseIndex
from semantic.workspace import ClassWorkspace


def test_weak_accepted_not_emitted(tmp_path: Path, monkeypatch):
    classes = tmp_path / "classes"
    classes.mkdir()
    monkeypatch.setattr("semantic.settings.CLASSES_DIR", classes)
    monkeypatch.setattr("semantic.workspace.settings.CLASSES_DIR", classes)
    idx = tmp_path / "sense.sqlite"
    monkeypatch.setattr(
        "semantic.settings.load_config",
        lambda: {
            "sense_index": str(idx),
            "onto_ili_emit_min": 0.85,
            "onto_ili_auto_accept": False,
            "pulo_sqlite": "x",
            "onto_sqlite": "x",
            "pulo_engine_dir": "x",
            "onto_engine_dir": "x",
            "lexwarrant_dir": str(tmp_path),
            "wordnet_dir": "x",
            "cili_map": "x",
        },
    )
    # sense_index default_index_path uses load_config — patch SenseIndex path
    ws = ClassWorkspace.create("WeakOnto", pref_label="w", axis="a")
    with SenseIndex(idx) as si:
        si.save_onto_proposal(
            onto_key="onto:clip21:13381",
            ili="i114921",
            score=0.3633,
            method="lemma+gloss",
            evidence={"lemma_score": 0.4},
            class_id="WeakOnto",
            status="accepted",
        )
        si.upsert({
            "sense_key": "onto:clip21:13381",
            "source": "onto",
            "local_id": "clip21:13381",
            "ili": None,
            "lemmas": ["composto", "empatia", "alquimia"],
            "gloss": "",
            "class_id": "WeakOnto",
        })

    # Force emit to use our index path
    monkeypatch.setattr(
        "semantic.onto_ili.SenseIndex",
        lambda *a, **k: SenseIndex(idx),
    )
    out = emit_onto_ili_result("WeakOnto")
    assert out is None
    assert not (ws.results / "WeakOnto.ONTO-ILI.result.json").exists()
