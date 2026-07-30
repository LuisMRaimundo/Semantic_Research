#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""concept_mapping.excluded_cili is authoritative over stale UF/RT decisions."""
from __future__ import annotations

import json
from pathlib import Path

from semantic.mapping_policy import (
    excluded_cili_ids,
    sync_decisions_with_excluded_cili,
)
from semantic.workspace import ClassWorkspace


def test_sync_flips_excluded_uf_rt(tmp_path: Path, monkeypatch):
    classes = tmp_path / "classes"
    classes.mkdir()
    monkeypatch.setattr("semantic.settings.CLASSES_DIR", classes)
    monkeypatch.setattr("semantic.workspace.settings.CLASSES_DIR", classes)
    ws = ClassWorkspace.create("SyncMap", pref_label="x", axis="y")
    meta = ws.load_meta()
    meta["concept_mapping"] = {
        "excluded_cili": [
            {"cili": "i114921", "reason": "química"},
            {"cili": "i97733", "reason": "decay"},
        ],
        "cili_exact": [],
        "mapping_status": "no_validated_cili",
    }
    ws.save_meta(meta)
    dec = {
        "class_id": "SyncMap",
        "senses": [
            {
                "source": "pulo",
                "key": "ili-30-14818238-n",
                "ili": "ili-30-14818238-n",
                "members": ["composto"],
                "decision": "UF",
                "destino": "vocabulario",
            },
            {
                "source": "pulo",
                "key": "ili-30-11444643-n",
                "ili": "ili-30-11444643-n",
                "members": ["decomposição"],
                "decision": "RT",
                "destino": "vocabulario",
            },
        ],
        "terms": [],
        "manual_terms": [],
    }
    dec2, flips = sync_decisions_with_excluded_cili(dec, meta)
    assert len(flips) == 2
    assert excluded_cili_ids(meta) == {"i114921", "i97733"}
    by_key = {s["key"]: s for s in dec2["senses"]}
    assert by_key["ili-30-14818238-n"]["decision"] == "exclude"
    assert by_key["ili-30-11444643-n"]["decision"] == "exclude"
    assert by_key["ili-30-14818238-n"]["destino"] == "evidencia"
