#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CONCEPT.ttl must not dump every harvested ILI as skos:exactMatch."""
from __future__ import annotations

import json
from pathlib import Path

from semantic.concept_model import build_class_concept_graph, render_skos_owl
from semantic.workspace import ClassWorkspace


def test_exact_match_only_primary_pulo_uf(tmp_path: Path, monkeypatch):
    classes = tmp_path / "classes"
    classes.mkdir()
    monkeypatch.setattr("semantic.settings.CLASSES_DIR", classes)
    monkeypatch.setattr("semantic.workspace.settings.CLASSES_DIR", classes)
    ws = ClassWorkspace.create("AuditClass", pref_label="compósito", axis="heterogeneidade")
    decisions = {
        "class_id": "AuditClass",
        "senses": [
            {
                "source": "pulo",
                "key": "pwn30-14818238-n",
                "ili": "i114921",
                "cili": "i114921",
                "members": ["composto"],
                "gloss": "química",
                "decision": "UF",
            },
            {
                "source": "onto",
                "key": "ontopt06:7120",
                "ili": None,
                "members": ["compósito", "heterogéneo", "mesclado"],
                "gloss": "diverso género",
                "decision": "UF",
            },
            {
                "source": "pulo",
                "key": "pwn30-11444643-n",
                "ili": "i97733",
                "cili": "i97733",
                "members": ["decomposição"],
                "decision": "RT",
            },
            {
                "source": "pulo",
                "key": "pwn30-00378985-n",
                "ili": "i11970",
                "members": ["combinação"],
                "decision": "exclude",
            },
        ],
        "terms": [],
        "manual_terms": [],
        "exclude_terms": [],
    }
    ws.decisions_json.write_text(
        json.dumps(decisions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    graph = build_class_concept_graph(ws)
    assert graph["cili_exact"] == ["i114921"]
    assert "i97733" in graph["cili_related"]
    assert "i11970" not in graph["cili_exact"]
    assert "i11970" not in graph["cili_close"]
    assert "i11970" not in graph["cili_related"]

    ttl = render_skos_owl(graph)
    assert ttl.count("skos:exactMatch <") == 1
    assert "i114921" in ttl
    assert "skos:relatedMatch <" in ttl
    assert "i11970" not in ttl  # exclude must not appear as a match
    # Onto UF lemmas surface as altLabel
    assert "compósito" in ttl or "heterogéneo" in ttl


def test_no_exact_match_when_multiple_pulo_uf(tmp_path: Path, monkeypatch):
    classes = tmp_path / "classes"
    classes.mkdir()
    monkeypatch.setattr("semantic.settings.CLASSES_DIR", classes)
    monkeypatch.setattr("semantic.workspace.settings.CLASSES_DIR", classes)
    ws = ClassWorkspace.create("Multi", pref_label="x", axis="y")
    ws.decisions_json.write_text(
        json.dumps({
            "class_id": "Multi",
            "senses": [
                {
                    "source": "pulo", "key": "a", "ili": "i114921",
                    "members": ["a"], "decision": "UF",
                },
                {
                    "source": "pulo", "key": "b", "ili": "i97733",
                    "members": ["b"], "decision": "UF",
                },
            ],
            "terms": [], "manual_terms": [], "exclude_terms": [],
        }),
        encoding="utf-8",
    )
    graph = build_class_concept_graph(ws)
    assert graph["cili_exact"] == []
    assert set(graph["cili_close"]) == {"i114921", "i97733"}
    ttl = render_skos_owl(graph)
    assert "skos:exactMatch <" not in ttl
    assert ttl.count("skos:closeMatch <") == 2
