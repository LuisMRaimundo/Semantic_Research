#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CONCEPT.ttl: no auto SKOS matches from resolved PULO CILI; SKOS integrity."""
from __future__ import annotations

import json
from pathlib import Path

from semantic.concept_model import (
    build_class_concept_graph,
    build_t16,
    render_skos_owl,
)
from semantic.workspace import ClassWorkspace


def test_no_auto_exact_match_from_pulo_uf(tmp_path: Path, monkeypatch):
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
                "members": ["compósito", "heterogéneo", "mesclado", "dissimilar"],
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
    assert graph["cili_exact"] == []
    assert graph["cili_related"] == []
    assert graph["mapping_status"] == "no_validated_cili"
    # Exclude-sense CILIs stay in inventory, not auto-inflated excluded_cili RDF
    assert not any(e.get("cili") == "i11970" for e in graph["excluded_cili"])
    inv = {(row["cili"], row.get("role")) for row in graph["ili_inventory"]}
    assert ("i114921", "uf_pulo_candidate") in inv
    assert ("i97733", "rt_candidate") in inv
    assert ("i11970", "exclude_sense") in inv

    ttl = render_skos_owl(graph)
    assert "skos:exactMatch <" not in ttl
    assert "skos:relatedMatch <" not in ttl
    assert "skos:hiddenLabel" not in ttl
    assert "sr:excludedCandidate" in ttl
    assert "ili.globalwordnet.org/ili/" in ttl or "exactMatch" not in ttl
    # Onto co-members must not all become altLabel
    assert 'skos:altLabel "mesclado"' not in ttl
    assert 'skos:altLabel "dissimilar"' not in ttl


def test_concept_mapping_drives_matches_and_alts(tmp_path: Path, monkeypatch):
    classes = tmp_path / "classes"
    classes.mkdir()
    monkeypatch.setattr("semantic.settings.CLASSES_DIR", classes)
    monkeypatch.setattr("semantic.workspace.settings.CLASSES_DIR", classes)
    ws = ClassWorkspace.create("Mapped", pref_label="textura compósita", axis="y")
    meta = ws.load_meta()
    meta["concept_mapping"] = {
        "cili_exact": [],
        "cili_close": [],
        "cili_related": [],
        "validated_alt_labels": ["compósito"],
        "excluded_cili": [
            {"cili": "i114921", "reason": "aceção química: chemical compound"},
            {"cili": "i97733", "reason": "aceção biológica: decay/decomposition"},
        ],
        "mapping_status": "no_validated_cili",
    }
    ws.save_meta(meta)
    ws.decisions_json.write_text(
        json.dumps({
            "class_id": "Mapped",
            "senses": [
                {
                    "source": "pulo", "key": "a", "ili": "i114921",
                    "members": ["composto"], "decision": "UF", "gloss": "química",
                },
                {
                    "source": "onto", "key": "b",
                    "members": ["compósito", "bom", "doido"], "decision": "UF",
                },
            ],
            "terms": [], "manual_terms": [], "exclude_terms": [],
        }),
        encoding="utf-8",
    )
    graph = build_class_concept_graph(ws)
    assert graph["cili_exact"] == []
    assert graph["validated_alt_labels"] == ["compósito"]
    assert {e["cili"] for e in graph["excluded_cili"]} >= {"i114921", "i97733"}
    ttl = render_skos_owl(graph)
    assert 'skos:altLabel "compósito"@pt-PT' in ttl
    assert 'skos:altLabel "bom"' not in ttl
    assert "sr:excludedCili" in ttl
    assert "ili.globalwordnet.org/ili/i114921" in ttl
    assert "skos:exactMatch" not in ttl


def test_skos_label_disjointness(tmp_path: Path, monkeypatch):
    classes = tmp_path / "classes"
    classes.mkdir()
    monkeypatch.setattr("semantic.settings.CLASSES_DIR", classes)
    monkeypatch.setattr("semantic.workspace.settings.CLASSES_DIR", classes)
    ws = ClassWorkspace.create("Disjoint", pref_label="x", axis="y")
    meta = ws.load_meta()
    meta["concept_mapping"] = {"validated_alt_labels": ["compósito"]}
    ws.save_meta(meta)
    ws.decisions_json.write_text(
        json.dumps({
            "class_id": "Disjoint",
            "senses": [
                {
                    "source": "onto", "key": "u", "members": ["compósito"],
                    "decision": "UF",
                },
                {
                    "source": "pulo", "key": "e", "members": ["compósito", "ruído"],
                    "decision": "exclude", "gloss": "excluído",
                },
            ],
            "terms": [], "manual_terms": [], "exclude_terms": [],
        }),
        encoding="utf-8",
    )
    ttl = render_skos_owl(build_class_concept_graph(ws))
    assert ttl.count('skos:altLabel "compósito"') == 1
    assert 'rdf:value "compósito"' not in ttl  # not also excludedCandidate
    assert 'rdf:value "ruído"' in ttl


def test_t16_flags_cili_in_rt_and_exclude():
    """T16 — o mesmo CILI não pode estar em rt_candidates e exclude_records."""
    graph = {
        "discovery_evidence": {
            "uf_candidates": [],
            "rt_candidates": [{"ili": "i6556", "members": ["x"], "key": "ontopt06:6214"}],
            "exclude_records": [{"ili": "i6556", "members": ["y"], "key": "pwn30-01199083-a"}],
        }
    }
    t16 = build_t16(graph)
    assert t16["id"] == "T16"
    assert t16["passed"] is False
    assert "i6556" in t16["evidence"]
    clean = {
        "discovery_evidence": {
            "uf_candidates": [{"ili": "i1", "members": ["a"]}],
            "rt_candidates": [{"ili": "i2", "members": ["b"]}],
            "exclude_records": [{"ili": "i3", "members": ["c"]}],
        }
    }
    assert build_t16(clean)["passed"] is True
