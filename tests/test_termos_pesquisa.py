"""TERMOS.html — regras R1–R7 (genéricas; regressão TexturaUniforme)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from semantic.compile_specs import compile_pulo_spec
from semantic.termos_pesquisa import (
    HTML_MAX_BYTES,
    assert_termos_coherence,
    build_termos_pesquisa,
    render_termos_md,
    write_termos_pesquisa,
)
from semantic.workspace import ClassWorkspace
import semantic.settings as settings


class TermosPesquisaRulesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        settings.CLASSES_DIR = Path(self.tmp.name) / "classes"
        settings.CLASSES_DIR.mkdir()

        # Neighbor class (R3b target) — no hardcodes of production class names in engine
        self.other = ClassWorkspace.create(
            "ClasseVizinha", pref_label="vizinho", axis="eixo vizinho"
        )
        other_dec = {
            "class_id": "ClasseVizinha",
            "senses": [],
            "terms": [],
            "manual_terms": [
                {
                    "term": "pluriforma",
                    "definition": "princípio da classe vizinha",
                    "structural": "ClasseVizinha",
                }
            ],
            "exclude_terms": [],
        }
        self.other.decisions_json.write_text(
            json.dumps(other_dec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        self.ws = ClassWorkspace.create(
            "DemoTermos", pref_label="alvo", axis="invariância"
        )
        meta = self.ws.load_meta()
        meta["focus_stems"] = ["seedone", "seedtwo"]
        meta["axis_terms"] = ["seedone", "seedtwo", "seedthree"]
        meta["disjoint_classes"] = {"ClasseOwlInterna": []}
        meta["control_axes"] = [
            {
                "eixo": "ClasseOwlInterna",
                "termos": [],
                "nota": "classe disjunta",
            },
            {
                "eixo": "eixoexcluido",
                "termos": ["controllemma"],
                "lingua": "en",
                "nota": "controlo",
            },
        ]
        meta["search_lang"] = "en"
        meta["label_lang"] = "pt-PT"
        self.ws.save_meta(meta)
        dec = {
            "class_id": "DemoTermos",
            "senses": [
                {
                    "source": "pulo",
                    "key": "ili-30-1-a",
                    "ili": "ili-30-1-a",
                    "members": ["alvo", "constante"],
                    "decision": "UF",
                    "gloss": "eixo adjectival",
                    "note": "",
                },
                {
                    "source": "pulo",
                    "key": "ili-30-9-n",
                    "ili": "ili-30-9-n",
                    "members": ["nomeum", "nomedois", "nometres"],
                    "decision": "RT",
                    "gloss": "acepção nominal partilhada",
                    "note": "",
                },
                {
                    "source": "pulo",
                    "key": "ili-30-2-a",
                    "ili": "ili-30-2-a",
                    "members": ["excluido"],
                    "decision": "exclude",
                    "gloss": "fora do domínio",
                    "note": "",
                },
            ],
            "terms": [
                {
                    "term": "pluriforma",
                    "status": "oposicao",
                    "destino": "evidencia",
                    "structural": "ClasseVizinha",
                    "definition": "pertence à vizinha",
                }
            ],
            "manual_terms": [
                {
                    "term": "pluriforma",
                    "definition": "pertence à vizinha",
                    "structural": "ClasseVizinha",
                }
            ],
            "exclude_terms": [],
        }
        self.ws.decisions_json.write_text(
            json.dumps(dec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        concordance = {
            "concepts": [
                {
                    "term": "alvo",
                    "proposta_final": "UF",
                    "veredicto": "convergência (sentido)",
                    "ili": ["ili-30-1-a", "oewn-ili:i10771"],
                    "sources": {"PULO": "UF"},
                },
                {
                    "term": "constante",
                    "proposta_final": "UF",
                    "veredicto": "fonte única",
                    "ili": ["ili-30-1-a"],
                    "sources": {"PULO": "UF"},
                },
                {
                    "term": "nomeum",
                    "proposta_final": "RT",
                    "veredicto": "fonte única",
                    "ili": ["ili-30-9-n"],
                    "sources": {"PULO": "RT"},
                },
                {
                    "term": "nomedois",
                    "proposta_final": "RT",
                    "veredicto": "fonte única",
                    "ili": ["ili-30-9-n"],
                    "sources": {"PULO": "RT"},
                },
                {
                    "term": "nometres",
                    "proposta_final": "RT",
                    "veredicto": "fonte única",
                    "ili": ["ili-30-9-n"],
                    "sources": {"PULO": "RT"},
                },
            ]
        }
        self.ws.concordance_json().parent.mkdir(parents=True, exist_ok=True)
        self.ws.concordance_json().write_text(
            json.dumps(concordance, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.ws.root / "termos_manuais.yaml").write_text(
            "termos:\n"
            "  - forma: uniform\n"
            "    wildcard: uniform*\n"
            "    polo: alvo\n"
            "    lingua: en\n"
            "    fonte: teste\n"
            "    nota: manual\n"
            "  - forma: multiform\n"
            "    polo: contrastante\n"
            "    lingua: en\n"
            "    fonte: teste\n"
            "  - forma: controllemma\n"
            "    polo: controlo\n"
            "    lingua: en\n"
            "    fonte: teste\n",
            encoding="utf-8",
        )

    def test_scope_note_in_header(self):
        meta = self.ws.load_meta()
        meta["scope_note"] = "acepção schaefferiana; exclui o composto químico"
        self.ws.save_meta(meta)
        doc = build_termos_pesquisa(self.ws)
        self.assertEqual(
            doc["scope_note"],
            "acepção schaefferiana; exclui o composto químico",
        )
        md = render_termos_md(doc)
        self.assertIn(
            "**Nota de âmbito:** acepção schaefferiana; exclui o composto químico",
            md,
        )

    def test_manual_not_auto_uf(self):
        spec = compile_pulo_spec(self.ws)
        self.assertNotIn("pluriforma", spec["adjudication"])

    def test_r1_r2_search_lang_and_manual(self):
        doc = build_termos_pesquisa(self.ws)
        self.assertEqual(doc["search_lang"], "en")
        self.assertEqual(doc["label_lang"], "pt-PT")
        a_forms = {r["forma"] for r in doc["A_polo_alvo"]}
        self.assertIn("uniform", a_forms)
        self.assertTrue(all(r.get("lingua") == "en" for r in doc["A_polo_alvo"]))
        # F is label_lang vocabulary
        f_forms = {r["forma"] for r in doc["F_vocabulario_pt"]}
        self.assertEqual(
            f_forms, {"alvo", "constante", "nomeum", "nomedois", "nometres"}
        )
        self.assertNotIn("uniform", f_forms)

    def test_r3a_no_owl_in_term_sections(self):
        doc = build_termos_pesquisa(self.ws)
        for rows in (
            doc["A_polo_alvo"],
            doc["B_polo_contrastante"],
            doc["C_termos"],
            doc["D_descritores_adjacentes"],
            doc["F_vocabulario_pt"],
        ):
            for r in rows:
                self.assertNotEqual(r.get("forma"), "ClasseOwlInterna")
        for r in doc["C_conjunto_controlo"]:
            self.assertFalse(
                str(r.get("eixo") or "").startswith("ClasseOwl"),
                msg=r,
            )

    def test_r5_sheet_metadata_excluded(self):
        doc = build_termos_pesquisa(self.ws)
        all_forms = []
        for key in (
            "A_polo_alvo", "B_polo_contrastante", "C_termos",
            "D_descritores_adjacentes", "F_vocabulario_pt",
        ):
            all_forms.extend(r["forma"] for r in doc[key])
        for seed in ("seedone", "seedtwo", "seedthree"):
            self.assertNotIn(seed, all_forms)

    def test_r4_r6_a_resolver_anomalies_only(self):
        doc = build_termos_pesquisa(self.ws)
        reasons = " ".join(
            ";".join(x["razoes"]) for x in doc["a_resolver"]
        )
        # fonte única must NOT appear as anomaly reason
        self.assertNotIn("fonte única", reasons.lower().replace("ú", "u"))
        # shared noun sense (≥3) on adjectival anchor
        self.assertTrue(
            any("três ou mais" in ";".join(x["razoes"]) for x in doc["a_resolver"])
        )
        # POS divergence
        self.assertTrue(
            any("diverge" in ";".join(x["razoes"]) for x in doc["a_resolver"])
        )

    def test_r7_write_and_assertions(self):
        paths = write_termos_pesquisa(self.ws, dest_dir=self.ws.final_results)
        html = Path(paths["html"]).read_text(encoding="utf-8")
        self.assertLessEqual(len(html.encode("utf-8")), HTML_MAX_BYTES)
        doc = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
        assert_termos_coherence(doc, html)
        self.assertNotIn("ClasseOwlInterna", html)
        # R5: seeds must not appear as tokens (syntax line may use near_stem)
        for sec_id in ("A", "B", "C", "D", "F"):
            chunk = html.split(f'id="{sec_id}"', 1)[1].split("<section", 1)[0]
            self.assertNotIn("seedone", chunk)
            self.assertNotIn("seedtwo", chunk)
        if doc["a_resolver"]:
            self.assertIn("A resolver antes de fixar os rótulos", html)
        from semantic.termos_pesquisa import _quote_copy_token
        self.assertEqual(_quote_copy_token("de maneira justa"), '"de maneira justa"')


@unittest.skipUnless(
    (ROOT / "classes" / "TexturaUniforme" / "class.json").exists(),
    "TexturaUniforme workspace not present",
)
class TexturaUniformeRegressionTests(unittest.TestCase):
    """Regression cases — not rules."""

    def test_regression_surface(self):
        # Restore CLASSES_DIR to real project for this test
        settings.CLASSES_DIR = ROOT / "classes"
        ws = ClassWorkspace.open("TexturaUniforme")
        doc = build_termos_pesquisa(ws)
        all_search = []
        for key in (
            "A_polo_alvo", "B_polo_contrastante", "C_termos",
            "D_descritores_adjacentes",
        ):
            all_search.extend(r["forma"] for r in doc[key])
        f_forms = {r["forma"] for r in doc["F_vocabulario_pt"]}
        # R5
        for seed in ("fixos", "intervalos", "variacao", "variacoes"):
            self.assertNotIn(seed, all_search)
            self.assertNotIn(seed, f_forms)
        # R3a
        self.assertNotIn("TexturaHeterogenea", all_search)
        for r in doc["C_conjunto_controlo"]:
            self.assertNotEqual(r.get("eixo"), "TexturaHeterogenea")
        # R3b — if still in F, must be flagged; after compile fix should leave admits
        if "politípica" in f_forms:
            hit = [x for x in doc["a_resolver"] if x["forma"] == "politípica"]
            self.assertTrue(hit)
            self.assertTrue(
                any("princípio organizador" in r for r in hit[0]["razoes"])
            )
        # R4 shared nominal sense
        shared = [
            x for x in doc["a_resolver"]
            if "ili-30-04745370-n" in ";".join(x["razoes"])
            or "três ou mais" in ";".join(x["razoes"])
        ]
        self.assertTrue(shared)


if __name__ == "__main__":
    unittest.main()
