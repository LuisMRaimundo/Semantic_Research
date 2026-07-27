"""R4/R5 — Bloco A/B split and non-serialisation of evidence."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from semantic.export_blocks import (
    assert_blocks_disjoint,
    build_export_blocks,
    evidence_terms,
    render_blocks_markdown,
    skos_serializable_terms,
)
from semantic.workspace import ClassWorkspace
import semantic.settings as settings


def _fake_turtle_from_bloco_a(blocks: dict) -> str:
    """Minimal Turtle consumer of Bloco A only (mirrors engine contract)."""
    v = blocks["vocabulario"]
    lines = [
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix skosxl: <http://www.w3.org/2008/05/skos-xl#> .",
        "@prefix : <http://example.org/textura#> .",
        "",
        f':X a skos:Concept ;',
        f'    skos:prefLabel "{v["prefLabel"]["termo"]}"@pt ;',
    ]
    for row in v.get("altLabel") or []:
        t = row["termo"].replace('"', '\\"')
        lines.append(
            f'    skosxl:altLabel [ skosxl:literalForm "{t}"@pt ] ;'
        )
    for row in v.get("termoRelacionado") or []:
        lines.append(f'    :termoRelacionado :{row["termo"]} ;')
    if lines[-1].endswith(";"):
        lines[-1] = lines[-1][:-1].rstrip() + " ."
    return "\n".join(lines) + "\n"


class ExportBlocksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        settings.CLASSES_DIR = Path(self.tmp.name) / "classes"
        settings.CLASSES_DIR.mkdir()
        self.ws = ClassWorkspace.create(
            "DemoClass", pref_label="uniforme", axis="invariância"
        )
        dec = {
            "class_id": "DemoClass",
            "senses": [
                {
                    "source": "pulo",
                    "key": "ili-30-1-a",
                    "ili": "ili-30-1-a",
                    "members": ["invariável"],
                    "decision": "UF",
                    "gloss": "g",
                    "note": "",
                },
                {
                    "source": "pulo",
                    "key": "ili-30-2-a",
                    "ili": "ili-30-2-a",
                    "members": ["periódico"],
                    "decision": "RT",
                    "gloss": "g",
                    "note": "",
                },
                {
                    "source": "onto",
                    "key": "clip:1",
                    "ili": None,
                    "members": ["farda"],
                    "decision": "exclude",
                    "gloss": "",
                    "note": "",
                },
            ],
            "terms": [
                {
                    "term": "uniformidade",
                    "status": "atributo",
                    "note": "qualidade",
                    "guarantee": ["lexical"],
                },
                {
                    "term": "politípica",
                    "status": "oposicao",
                    "note": "Teste 3",
                    "guarantee": ["estipulativa"],
                    "migrado_de": "contraste",
                    "revisao_pendente": True,
                    "structural": "TexturaHeterogenea",
                },
                {
                    "term": "heterogénea",
                    "status": "vizinha",
                    "note": "manual",
                    "guarantee": ["estipulativa"],
                    "structural": "TexturaHeterogenea",
                },
            ],
            "manual_terms": [],
            "exclude_terms": [],
        }
        self.ws.decisions_json.write_text(
            json.dumps(dec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        # WordNet-like auto contrast signal
        self.ws.results.mkdir(parents=True, exist_ok=True)
        (self.ws.results / "DemoClass.WordNet.result.json").write_text(
            json.dumps(
                {
                    "class_id": "DemoClass",
                    "sinalizacao": {
                        "multiform": {
                            "display": "multiform",
                            "reason": (
                                "material de contraste (antonym) de i10771 "
                                "(oewn-01973553-a) — sem estatuto"
                            ),
                            "offsets_ili": ["i10773"],
                        },
                        "single": {
                            "display": "single",
                            "reason": (
                                "vizinho similar_to de i10771 "
                                "(oewn-01973553-a) — sem estatuto"
                            ),
                            "offsets_ili": ["i10772"],
                        },
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def test_blocks_split_and_md_titles(self):
        blocks = build_export_blocks(self.ws)
        self.assertEqual(blocks["vocabulario"]["prefLabel"]["termo"], "uniforme")
        alts = [r["termo"] for r in blocks["vocabulario"]["altLabel"]]
        self.assertIn("invariável", alts)
        rts = [r["termo"] for r in blocks["vocabulario"]["termoRelacionado"]]
        self.assertIn("periódico", rts)
        evid = blocks["evidencia_delimitacao"]
        self.assertEqual(
            evid["nota"],
            "Registos documentais. Não constituem relações do vocabulário.",
        )
        self.assertTrue(evid["exclude"])
        self.assertEqual(len(evid["material_contraste_auto"]), 1)
        self.assertEqual(len(evid["vizinhos_similar_to_auto"]), 1)
        self.assertTrue(any(r.get("termo") == "uniformidade" for r in evid["atributo"]))
        self.assertTrue(any(r.get("termo") == "politípica" for r in evid["oposicao"]))
        self.assertTrue(any(r.get("termo") == "heterogénea" for r in evid["vizinha"]))
        md = render_blocks_markdown(blocks)
        self.assertIn("## Vocabulário (SKOS-XL)", md)
        self.assertIn("## Evidência de delimitação (não serializada)", md)
        self.assertIn(
            "Registos documentais. Não constituem relações do vocabulário.", md
        )
        ok, ev = assert_blocks_disjoint(blocks)
        self.assertTrue(ok, ev)

    def test_t12_allows_lemma_overlap_under_polysemy(self):
        """Same lemma may be UF in one sense and member of an exclude sense."""
        dec = json.loads(self.ws.decisions_json.read_text(encoding="utf-8"))
        dec["senses"].append({
            "source": "onto",
            "key": "clip:poly",
            "ili": None,
            "members": ["invariável", "outro"],
            "decision": "exclude",
            "gloss": "",
            "note": "",
        })
        self.ws.decisions_json.write_text(
            json.dumps(dec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        blocks = build_export_blocks(self.ws)
        ok, ev = assert_blocks_disjoint(blocks)
        self.assertTrue(ok, ev)
        # lemma overlap exists, but records are still disjoint
        self.assertIn("invariável", skos_serializable_terms(blocks))
        self.assertIn("invariável", evidence_terms(blocks))

    def test_evidence_never_in_serialized_turtle(self):
        blocks = build_export_blocks(self.ws)
        ttl = _fake_turtle_from_bloco_a(blocks)
        # Also ban legacy predicates
        self.assertNotIn("contrastaCom", ttl)
        self.assertNotIn("temAtributo", ttl)
        self.assertNotIn("skos:related", ttl)
        # Bloco B terms that are NOT in Bloco A must not appear in Turtle
        only_evidence = evidence_terms(blocks) - skos_serializable_terms(blocks)
        for term in only_evidence:
            self.assertNotIn(term, ttl.casefold())


if __name__ == "__main__":
    unittest.main()
