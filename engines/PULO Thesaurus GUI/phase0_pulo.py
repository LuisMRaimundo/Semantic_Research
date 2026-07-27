#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fase 0 — Selecção lexical e controlo terminológico (camada SKOS) para PULO / WordNet.PT.

Motor genérico e independente do termo (nada codificado para «uniforme»), análogo
ao `phase0_skos.py` do Onto.PT mas adaptado à natureza do PULO. Importável + CLI.

DIFERENÇA CRÍTICA face ao motor ONTO
------------------------------------
O PULO é DESAMBIGUADO por sentido e ancorado no ILI (1 synset = 1 acepção, como a
entrada numerada de um dicionário). Os seus sinónimos NÃO têm pesos. A sua função
é a de ÂNCORA: PRODUZ a lista branca de ILI que o motor ONTO consome como fonte de
corroboração. É a montante, não a jusante.

Por isso NÃO existe porta estatística (peso/coocorrência). O equivalente da
«Etapa 3» é a COLHEITA de relações tipadas (WordNet), não filtragem estatística.

Chave canónica
--------------
Toda a decisão é ancorada no `ili_offset` (ili-30-…), a chave interlingual. O
`synset_offset` (por-30-…) é um id local e qualquer id `oewn-` é estrangeiro — nunca
usados como chave de junção directa. Synsets sem `ili_offset` são SINALIZADOS.

Uso:
    python phase0_pulo.py <spec.json> [--pulo-export <pulo.json>] [--outdir fase0]

Saídas (mesmos nomes do motor ONTO), para a classe X:
    X.report.md       relatório humano + quadro de ASSERTs (PASS/FAIL)
    X.result.json     admitidos[]/sinalizacao[]/attribute[]/family[]/descartados[]
    X.skos.ttl        SKOS-XL/OWL (construído e validado com rdflib)
    X.whitelist.json  lista branca por ILI, no esquema que o phase0_skos.py lê

Requer: biblioteca padrão + rdflib (para construir/validar o Turtle).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# contraste / oposicao / vizinha / atributo are evidence-only (never admitted).
STATUSES = ("UF", "RT", "BT", "NT")
DECISION_ADMIT = ("UF", "RT")

NO_LEMMA = "(no lemma)"

DEFAULT_EXCLUSION_PATTERNS = [
    r"^maneira\s+sem\b",
    r"\bpor\s+meio\s+de\b",
]

# Relation label (substring, lower/no-accent) -> bucket
RELATION_BUCKETS = [
    ("antonym", "contrast"),
    ("antonimo", "contrast"),
    ("similar", "rt_uf"),
    ("deriv", "family"),
    ("hyponym", "NT"),
    ("narrower", "NT"),
    ("hiponimo", "NT"),
    ("hypernym", "BT"),
    ("broader", "BT"),
    ("hiperonimo", "BT"),
    ("attribute", "attribute"),
    ("atributo", "attribute"),
]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def normalize_word(word: str) -> str:
    return strip_accents(word).lower().strip().replace(" ", "_")


def pretty_word(word: str) -> str:
    return (word or "").replace("_", " ")


def fold(text: str) -> str:
    """Accent/caseless fold for substring matching in glosses."""
    return strip_accents(text or "").lower()


def is_multiword(word: str) -> bool:
    return (" " in (word or "")) or ("_" in (word or ""))


def classify_relation(label: str) -> str:
    f = fold(label)
    for needle, bucket in RELATION_BUCKETS:
        if needle in f:
            return bucket
    if re.search(r"relation\s*#\s*\d+", f) or not f:
        return "unnamed"
    return "unnamed"


# ---------------------------------------------------------------------------
# Spec
# ---------------------------------------------------------------------------
class SpecError(ValueError):
    pass


@dataclass
class ClassSpec:
    class_id: str
    pref_label: str
    axis: str
    axis_terms: list[str] = field(default_factory=list)
    stage1_whitelist: list[dict] = field(default_factory=list)
    dictionary_attestations: list[str] = field(default_factory=list)
    manual_terms: list[dict] = field(default_factory=list)
    attribute_bucket: list[str] = field(default_factory=list)
    exclude_terms: list[str] = field(default_factory=list)
    exclusion_patterns: list[str] = field(default_factory=list)
    adjudication: dict[str, dict] = field(default_factory=dict)
    disjoint_classes: dict[str, list[str]] = field(default_factory=dict)

    @staticmethod
    def load(path: Path) -> "ClassSpec":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        required = ("class_id", "pref_label", "axis")
        missing = [k for k in required if not raw.get(k)]
        if missing:
            raise SpecError(f"Spec sem campos obrigatórios: {', '.join(missing)}")
        return ClassSpec(
            class_id=str(raw["class_id"]),
            pref_label=str(raw["pref_label"]),
            axis=str(raw["axis"]),
            axis_terms=[fold(t) for t in raw.get("axis_terms", [])],
            stage1_whitelist=list(raw.get("stage1_whitelist", [])),
            dictionary_attestations=list(raw.get("dictionary_attestations", [])),
            manual_terms=list(raw.get("manual_terms", [])),
            attribute_bucket=[normalize_word(w) for w in raw.get("attribute_bucket", [])],
            exclude_terms=[normalize_word(w) for w in raw.get("exclude_terms", [])],
            exclusion_patterns=list(raw.get("exclusion_patterns", [])),
            adjudication={normalize_word(k): v for k, v in raw.get("adjudication", {}).items()},
            disjoint_classes=dict(raw.get("disjoint_classes", {})),
        )


@dataclass
class Assertion:
    stage: str
    text: str
    passed: bool
    evidence: str = ""


# ---------------------------------------------------------------------------
# PULO export model
# ---------------------------------------------------------------------------
def load_pulo_export(path: Optional[Path], data: Optional[dict]) -> dict:
    if data is not None:
        return data
    if path is None:
        raise SpecError("É necessário um export PULO (--pulo-export) ou dados em memória.")
    return json.loads(Path(path).read_text(encoding="utf-8"))


def synset_ili(syn: dict) -> Optional[str]:
    for item in syn.get("ili", []) or []:
        off = (item.get("ili_offset") or "").strip()
        if off:
            return off
    return None


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
class PuloPhase0Engine:
    def __init__(self, spec: ClassSpec, export: dict):
        self.spec = spec
        self.export = export
        self.assertions: list[Assertion] = []
        # index export synsets by ILI (canonical) — never by por-/oewn- id.
        self.by_ili: dict[str, dict] = {}
        self.no_ili: list[dict] = []
        for syn in export.get("synsets", []):
            ili = synset_ili(syn)
            if ili:
                self.by_ili.setdefault(ili, syn)
            else:
                self.no_ili.append(syn)

    def _assert(self, stage, text, passed, evidence=""):
        self.assertions.append(Assertion(stage, text, bool(passed), evidence))

    def _gloss_on_axis(self, gloss: str) -> bool:
        if not self.spec.axis_terms:
            return bool(gloss)
        g = fold(gloss)
        return any(term in g for term in self.spec.axis_terms)

    # -- Etapa 1 -------------------------------------------------------
    def stage1(self) -> dict:
        admitted, excluded, invalid = [], [], []
        offsets_admitted: list[str] = []
        for entry in self.spec.stage1_whitelist:
            ili = (entry.get("ili_offset") or "").strip()
            decision = str(entry.get("decision", "")).strip()
            glosa = (entry.get("glosa") or "").strip()
            if decision == "exclude":
                excluded.append(entry)
                continue
            if decision not in DECISION_ADMIT:
                invalid.append((entry, "decisão desconhecida"))
                continue
            if not ili or not glosa:
                invalid.append((entry, "sem ili_offset ou glosa"))
            # cross-check glosa against actual PULO export gloss (audit)
            exp = self.by_ili.get(ili)
            entry = {**entry, "_export_gloss": (exp or {}).get("gloss", "")}
            admitted.append(entry)
            offsets_admitted.append(ili)

        # A1.1 — cada synset admitido tem ili_offset e glosa mapeada ao eixo.
        bad = []
        for e in admitted:
            if not e.get("ili_offset") or not e.get("glosa"):
                bad.append(e.get("ili_offset") or "?")
                continue
            # UF must be on-axis by gloss; RT may be adjacent (gloss present suffices)
            if e.get("decision") == "UF" and not self._gloss_on_axis(e.get("glosa", "")):
                bad.append(e.get("ili_offset"))
        self._assert("Etapa 1",
                     "Todo o synset admitido tem ili_offset e glosa mapeada ao eixo.",
                     not bad,
                     "OK" if not bad else f"glosa não-ancorada/incompleta: {bad}")

        # A1.2 — nenhum synset off-axis figura na lista branca admitida.
        excl_offsets = {e.get("ili_offset") for e in excluded}
        overlap = excl_offsets & set(offsets_admitted)
        self._assert("Etapa 1",
                     "Nenhum synset off-axis (exclude) figura na lista branca admitida.",
                     not overlap,
                     "OK" if not overlap else f"offsets em conflito: {sorted(overlap)}")

        # A1.3 — lista branca persistida por offset ILI; offsets únicos.
        dups = sorted({o for o in offsets_admitted if offsets_admitted.count(o) > 1})
        self._assert("Etapa 1",
                     "A lista branca é persistida por offset ILI e os offsets são únicos.",
                     not dups and all(offsets_admitted),
                     "OK" if not dups else f"offsets duplicados: {dups}")
        return {"admitted": admitted, "excluded": excluded, "invalid": invalid,
                "offsets_admitted": offsets_admitted}

    # -- ILI canonical-key checks -------------------------------------
    def assert_ili(self, s1: dict):
        offs = s1["offsets_admitted"]
        non_ili = [o for o in offs if not o.lower().startswith("ili")]
        self._assert("ILI",
                     "Nenhum id oewn-/por- é usado como chave de junção; a chave é o ILI.",
                     not non_ili,
                     "OK" if not non_ili else f"offsets não-ILI na lista branca: {non_ili}")
        flagged = [s.get("synset_offset", "?") for s in self.no_ili]
        # synsets without ili are flagged (they land in self.no_ili -> sinalização)
        self._assert("ILI",
                     "Synsets sem ili_offset são sinalizados (não descartados em silêncio).",
                     True,
                     f"sinalizados por falta de ILI: {flagged}" if flagged
                     else "nenhum synset sem ILI no export")

    # -- Etapa 2 -------------------------------------------------------
    def stage2(self, s1: dict) -> dict:
        seeds: dict[str, dict] = {}
        for entry in s1["admitted"]:
            ili = entry.get("ili_offset", "")
            exp = self.by_ili.get(ili)
            # Corte 2: sense-card members (PASSO 3) are authoritative seeds;
            # export synonyms enlarge coverage but never replace adjudication.
            words = list(entry.get("members") or [])
            if exp:
                for syn in exp.get("synonyms") or []:
                    if syn and syn not in words:
                        words.append(syn)
            for w in words:
                if not w or w == NO_LEMMA:
                    continue
                nw = normalize_word(w)
                rec = seeds.setdefault(nw, {"display": pretty_word(w), "offsets": set(),
                                            "decision_synset": entry.get("decision")})
                rec["offsets"].add(ili)
        excl_offsets = {e.get("ili_offset") for e in s1["excluded"]}
        leaked = {nw for nw, r in seeds.items() if r["offsets"] & excl_offsets}
        self._assert("Etapa 2",
                     "Os sinónimos colhidos provêm exclusivamente de synsets admitidos.",
                     not leaked,
                     "OK" if not leaked else f"origem off-axis: {sorted(leaked)}")
        return {"seeds": seeds}

    # -- Etapa 3 — colheita de relações tipadas ------------------------
    def stage3(self, s1: dict) -> dict:
        buckets: dict[str, dict[str, dict]] = {
            "contrast": {}, "rt_uf": {}, "family": {}, "BT": {}, "NT": {},
            "attribute": {},
        }
        sinalizacao: dict[str, dict] = {}
        dropped_no_lemma = 0
        typed_ok = True

        for entry in s1["admitted"]:
            ili = entry.get("ili_offset", "")
            exp = self.by_ili.get(ili)
            if not exp:
                continue
            for rel in exp.get("relations", []):
                label = rel.get("relation", "")
                bucket = classify_relation(label)
                for tgt in rel.get("targets", []):
                    tgt_gloss = tgt.get("gloss", "")
                    words = [w.strip() for w in re.split(r"[;,]", tgt.get("words", "")) if w.strip()]
                    for w in words:
                        if not w or w == NO_LEMMA:
                            dropped_no_lemma += 1
                            continue
                        nw = normalize_word(w)
                        rec = {"display": pretty_word(w), "via": label,
                               "source_ili": ili, "target_gloss": tgt_gloss}
                        if bucket == "unnamed":
                            sinalizacao.setdefault(nw, {**rec, "reason":
                                                        "relação não-nomeada / #NN"})
                        elif bucket == "rt_uf":
                            # axis-check similar-to targets via their own gloss
                            if self._gloss_on_axis(tgt_gloss):
                                buckets["rt_uf"].setdefault(nw, rec)
                            else:
                                sinalizacao.setdefault(nw, {**rec, "reason":
                                                            "similar-to fora do eixo (glosa)"})
                        else:
                            buckets[bucket].setdefault(nw, rec)

        # A3.1 — alvos são tipados pelo mapeamento; "(no lemma)" nunca admitido.
        no_lemma_admitted = any(
            NO_LEMMA in r.get("display", "") for b in buckets.values() for r in b.values()
        )
        self._assert("Etapa 3",
                     "Alvos de relação são tipados pelo mapeamento; «(no lemma)» nunca admitido.",
                     typed_ok and not no_lemma_admitted,
                     f"OK ({dropped_no_lemma} alvos «(no lemma)» descartados)")
        return {"buckets": buckets, "sinalizacao": sinalizacao,
                "dropped_no_lemma": dropped_no_lemma}

    # -- Etapa 4 — exclusão --------------------------------------------
    def _compile_exclusions(self):
        pats = list(DEFAULT_EXCLUSION_PATTERNS) + list(self.spec.exclusion_patterns)
        return [re.compile(p, re.IGNORECASE) for p in pats]

    def stage4(self, pool: dict[str, dict], corroboration: set[str]) -> dict:
        regexes = self._compile_exclusions()
        excluded: dict[str, dict] = {}
        exclude_set = set(self.spec.exclude_terms)
        for nw, rec in list(pool.items()):
            disp = rec.get("display", pretty_word(nw))
            reason = None
            if nw in exclude_set:
                reason = "eixo ortogonal / termo excluído por especificação"
            if reason is None:
                for rx in regexes:
                    if rx.search(disp) or rx.search(nw):
                        reason = f"assinatura de ruído /{rx.pattern}/"
                        break
            if reason is None and is_multiword(disp) and nw not in corroboration:
                reason = "colocação multipalavra sem corroboração"
            if reason is None and rec.get("only_unnamed") and nw not in corroboration:
                reason = "apenas relação não-nomeada, sem corroboração"
            if reason:
                excluded[nw] = {**rec, "reason": reason}
                pool.pop(nw, None)

        remaining = [nw for nw in pool
                     if is_multiword(pool[nw].get("display", nw)) and nw not in corroboration]
        remaining += [nw for nw in pool if nw in exclude_set]
        self._assert("Etapa 4",
                     "«(no lemma)», colocações e termos só de relação não-nomeada "
                     "(sem corroboração) são excluídos.",
                     not remaining,
                     "OK" if not remaining else f"ainda na pool: {remaining}")
        return {"excluded": excluded}

    # -- Etapa 5 — adjudicação -----------------------------------------
    def stage5(self, pool: dict[str, dict], attribute_terms: set[str]) -> dict:
        admitted, pending = {}, {}
        estipulativa_bad = []
        attr_not_bucket = []

        for nw, rec in pool.items():
            adj = dict(self.spec.adjudication.get(nw, {}) or {})
            status = adj.get("status")
            # Quality nouns via attribute relation are evidence-only UNLESS the
            # analyst already assigned UF/RT on a sense (Corte 2 — sense wins).
            if nw in attribute_terms and status not in STATUSES:
                pending[nw] = {
                    **rec,
                    "adjudication": {
                        **adj,
                        "status": adj.get("status") or "atributo",
                        "test": adj.get("test")
                        or "Evidência (atributo) — não serializado",
                    },
                }
                continue

            # Corte 2: admission = sense-derived status only (no test/guarantee gate).
            complete = bool(status in STATUSES)
            if complete and "estipulativa" in (adj.get("guarantee") or []):
                if not adj.get("definition") or not adj.get("structural"):
                    complete = False
                    estipulativa_bad.append(nw)

            if complete:
                adj.setdefault("test", "derivado do sentido (PASSO 3)")
                adj.setdefault("guarantee", ["sense_decision"])
                admitted[nw] = {**rec, **adj}
            else:
                pending[nw] = {**rec, "adjudication": adj or None}

        bad = [nw for nw, r in admitted.items() if r.get("status") not in STATUSES]
        self._assert("Etapa 5",
                     "Cada admitido tem estatuto∈{UF,RT,BT,NT} "
                     "(garantia calculada a jusante; atributo = evidência).",
                     not bad and not attr_not_bucket,
                     "OK" if (not bad and not attr_not_bucket)
                     else f"incompletos: {bad}; atributo fora do bucket: {attr_not_bucket}")

        self._assert("Garantia",
                     "Termos com garantia «estipulativa» têm definição E relação estrutural.",
                     not estipulativa_bad,
                     "OK" if not estipulativa_bad else f"estipulativa incompleta: {estipulativa_bad}")
        return {"admitted": admitted, "pending": pending}

    # -- consistência --------------------------------------------------
    def finalize(self, admitted: dict[str, dict]) -> dict:
        by_status = defaultdict(set)
        for nw, r in admitted.items():
            by_status[r["status"]].add(nw)

        def disp(keys):
            return sorted(admitted[nw].get("display", pretty_word(nw)) for nw in keys)

        uf = by_status["UF"]
        conflicts = {}
        for other_class, terms in self.spec.disjoint_classes.items():
            overlap = uf & {normalize_word(t) for t in terms}
            if overlap:
                conflicts[other_class] = sorted(overlap)
        self._assert("Consistência",
                     "Nenhum termo é UF de duas classes com owl:disjointWith entre si.",
                     not conflicts,
                     "OK" if not conflicts else f"conflitos: {conflicts}")

        # Evidence statuses must never reach admitted provenance.
        evidence_leak = by_status.get("contraste") or by_status.get("atributo") or set()
        self._assert("Consistência",
                     "Nenhum estatuto de evidência (contraste/atributo) em admitidos.",
                     not evidence_leak,
                     "OK" if not evidence_leak else f"fuga: {sorted(evidence_leak)}")

        return {k: disp(v) for k, v in by_status.items()}

    # -- orquestração --------------------------------------------------
    def run(self) -> dict:
        spec = self.spec
        s1 = self.stage1()
        self.assert_ili(s1)
        s2 = self.stage2(s1)
        seeds = s2["seeds"]

        corroboration = set(seeds.keys()) | {
            normalize_word(w) for w in spec.dictionary_attestations
        }

        s3 = self.stage3(s1)
        buckets = s3["buckets"]

        # attribute terms = spec bucket ∪ terms reached via 'attribute' relation
        attribute_terms = set(spec.attribute_bucket) | set(buckets["attribute"].keys())

        # build adjudication pool
        pool: dict[str, dict] = {}

        def add(nw, rec, origin):
            if nw in pool:
                pool[nw]["origin"] += " + " + origin
                pool[nw].update({k: v for k, v in rec.items() if k not in pool[nw]})
            else:
                pool[nw] = {**rec, "origin": origin}

        for nw, r in seeds.items():
            add(nw, {"display": r["display"], "offsets": sorted(r["offsets"]),
                     "attested": True}, "seed (Etapa 1/2)")
        bucket_origin = {
            "contrast": "relação antonym (contraste)",
            "rt_uf": "relação similar-to (RT/UF)",
            "BT": "relação hypernym (BT)",
            "NT": "relação hyponym (NT)",
            "attribute": "relação attribute",
            "family": "forma derivada (família)",
        }
        for b, origin in bucket_origin.items():
            for nw, r in buckets[b].items():
                add(nw, {"display": r["display"], "via": r.get("via", ""),
                         "attested": nw in corroboration}, origin)
        for item in spec.manual_terms:
            w = item.get("term", "")
            if not w:
                continue
            nw = normalize_word(w)
            add(nw, {"display": pretty_word(w), "attested": nw in corroboration,
                     "offset": item.get("offset", "")},
                "manual (" + ", ".join(item.get("provenance", [])) + ")")

        # Families are not equivalence — but never drop sense-derived seeds
        # (Corte 2: PASSO 3 members / adjudication win over family filter).
        family = {nw: r for nw, r in buckets["family"].items()}
        for nw in family:
            if nw in seeds or nw in spec.adjudication:
                continue
            pool.pop(nw, None)

        # Pref label stays when it carries a sense-derived status (Corte 2).
        pref_nw = normalize_word(spec.pref_label)
        if pref_nw and pref_nw not in spec.adjudication and pref_nw not in seeds:
            pool.pop(pref_nw, None)

        s4 = self.stage4(pool, corroboration)      # mutates pool
        s5 = self.stage5(pool, attribute_terms)
        skos = self.finalize(s5["admitted"])

        provenance = []
        for nw, r in s5["admitted"].items():
            provenance.append({
                "termo": r.get("display", pretty_word(nw)),
                "estatuto": r["status"],
                "eixo": spec.axis,
                "via": r.get("via", r.get("origin", "")),
                "offsets_ili": r.get("offsets", []),
                "teste_decisivo": r.get("test", ""),
                "garantia": r.get("guarantee", []),
                "definicao": r.get("definition", ""),
                "estrutural": r.get("structural", ""),
            })

        return {
            "class_id": spec.class_id,
            "pref_label": spec.pref_label,
            "axis": spec.axis,
            "generated": datetime.now().isoformat(timespec="seconds"),
            "source": "PULO / WordNet.PT export",
            "stage1": {"admitted": [{"ili_offset": e.get("ili_offset"),
                                     "glosa": e.get("glosa"), "decision": e.get("decision"),
                                     "export_gloss": e.get("_export_gloss", "")}
                                    for e in s1["admitted"]],
                       "admitted_offsets": s1["offsets_admitted"],
                       "excluded_offsets": [e.get("ili_offset") for e in s1["excluded"]],
                       "invalid": [{"entry": e, "why": w} for e, w in s1["invalid"]],
                       "flagged_no_ili": [s.get("synset_offset") for s in self.no_ili]},
            "stage2_seeds": {nw: {"display": r["display"], "offsets": sorted(r["offsets"])}
                             for nw, r in seeds.items()},
            "stage3": {b: {nw: r for nw, r in buckets[b].items()} for b in buckets},
            "dropped_no_lemma": s3["dropped_no_lemma"],
            "sinalizacao": s3["sinalizacao"],
            "stage4_excluded": s4["excluded"],
            "stage5": {"admitted": s5["admitted"], "pending": s5["pending"]},
            "family": family,
            "skos": skos,
            "provenance": provenance,
            "attribute_terms": sorted(attribute_terms),
            "assertions": [a.__dict__ for a in self.assertions],
            "all_passed": all(a.passed for a in self.assertions),
        }


# ---------------------------------------------------------------------------
# SKOS-XL / OWL serialization (built + validated with rdflib)
# ---------------------------------------------------------------------------
def build_graph(result: dict, disjoint_classes: list[str]):
    from rdflib import Graph, Literal, BNode, Namespace, URIRef
    from rdflib.namespace import RDF, SKOS, OWL

    SKOSXL = Namespace("http://www.w3.org/2008/05/skos-xl#")
    TEX = Namespace("http://example.org/textura#")
    g = Graph()
    g.bind("skos", SKOS)
    g.bind("skosxl", SKOSXL)
    g.bind("owl", OWL)
    g.bind("tex", TEX)

    cls = TEX[result["class_id"]]
    g.add((cls, RDF.type, SKOS.Concept))
    g.add((cls, RDF.type, OWL.Class))
    g.add((cls, SKOS.prefLabel, Literal(result["pref_label"], lang="pt")))
    g.add((cls, SKOS.scopeNote, Literal(f"Eixo definidor: {result['axis']}", lang="pt")))

    prov = result["provenance"]

    def by(status):
        return [p for p in prov if p["estatuto"] == status]

    for p in by("UF"):
        node = BNode()
        g.add((cls, SKOSXL.altLabel, node))
        g.add((node, SKOSXL.literalForm, Literal(p["termo"], lang="pt")))
    for p in by("RT"):
        # tex:termoRelacionado ⊑ skosxl:labelRelation (not skos:related)
        g.add((cls, TEX["termoRelacionado"], TEX[normalize_word(p["termo"])]))
    for p in by("BT"):
        g.add((cls, SKOS.broader, TEX[normalize_word(p["termo"])]))
    for p in by("NT"):
        g.add((cls, SKOS.narrower, TEX[normalize_word(p["termo"])]))
    # atributo / contraste / oposicao / vizinha → never serialised (Bloco B only).
    # :contrastaCom and :temAtributo are intentionally absent — no emission path.
    for other in disjoint_classes:
        g.add((cls, OWL.disjointWith, TEX[other]))
    # Hard stop if a future edit reintroduces the banned predicates.
    banned = (TEX["contrastaCom"], TEX["temAtributo"])
    for _s, p, _o in g:
        if p in banned:
            raise RuntimeError(
                f"SKOS emitiu predicado proibido {p} — evidência não serializa."
            )
    return g


def render_markdown(result: dict) -> str:
    r = result
    L: list[str] = []
    ap = L.append
    status = ("✅ TODAS AS ASSERÇÕES PASSARAM" if r["all_passed"]
              else "❌ EXISTEM ASSERÇÕES FALHADAS")
    ap(f"# Fase 0 (PULO / WordNet.PT) — **{r['pref_label']}** (`{r['class_id']}`)")
    ap("")
    ap(f"- **Eixo definidor:** {r['axis']}")
    ap(f"- **Fonte:** {r['source']} (âncora ILI; sem porta estatística)")
    ap(f"- **Gerado:** {r['generated']}")
    ap(f"- **Estado global:** {status}")
    ap("")
    ap("## Quadro de asserções (protocolo)")
    ap("")
    ap("| Etapa | Asserção | Resultado | Evidência |")
    ap("|-------|----------|-----------|-----------|")
    for a in r["assertions"]:
        mark = "PASS ✅" if a["passed"] else "FAIL ❌"
        ev = (a["evidence"] or "").replace("|", "\\|")
        ap(f"| {a['stage']} | {a['text']} | {mark} | {ev} |")
    ap("")

    ap("## Etapa 1 — Selecção de acepções (lista branca ILI)")
    for e in r["stage1"]["admitted"]:
        ap(f"- **{e['decision']}** `{e['ili_offset']}` — {e['glosa']}")
    ap(f"- Excluídos (off-axis): `{r['stage1']['excluded_offsets']}`")
    if r["stage1"]["flagged_no_ili"]:
        ap(f"- ⚑ Sinalizados por falta de ILI: `{r['stage1']['flagged_no_ili']}`")
    ap("")

    ap("## Etapa 2 — Sementes (sinónimos de synsets admitidos)")
    seeds = r["stage2_seeds"]
    ap(f"Total: **{len(seeds)}** — " + ", ".join(sorted(s["display"] for s in seeds.values())))
    ap("")

    ap("## Etapa 3 — Colheita de relações tipadas")
    b = r["stage3"]
    for name, key in (("Contraste (antonym)", "contrast"), ("RT/UF (similar-to)", "rt_uf"),
                      ("BT (hypernym)", "BT"), ("NT (hyponym)", "NT"),
                      ("Atributo", "attribute"), ("Família derivada", "family")):
        vals = ", ".join(sorted(x["display"] for x in b[key].values())) or "—"
        ap(f"- **{name}:** {vals}")
    ap(f"- Alvos «(no lemma)» descartados: {r['dropped_no_lemma']}")
    ap("")
    if r["sinalizacao"]:
        ap("### Sinalização (revisão humana — NÃO admitidos)")
        for nw, x in sorted(r["sinalizacao"].items()):
            ap(f"- {x['display']} — {x.get('reason','')} (via «{x.get('via','')}»)")
        ap("")

    ap("## Etapa 4 — Exclusão automática")
    exc = r["stage4_excluded"]
    if exc:
        ap("| Termo | Motivo |")
        ap("|-------|--------|")
        for nw, c in sorted(exc.items()):
            ap(f"| {c.get('display', nw)} | {c['reason']} |")
    else:
        ap("Nenhum termo descartado.")
    ap("")

    ap("## Etapa 5 — Adjudicação + §7 proveniência")
    ap(f"Admitidos: **{len(r['provenance'])}**  ·  "
       f"Pendentes: **{len(r['stage5']['pending'])}**  ·  "
       f"(atributo/oposicao/vizinha = evidência, fora de provenance)")
    ap("")
    ap("| termo | estatuto | via | offset/ILI | teste decisivo | garantia | definição |")
    ap("|-------|----------|-----|------------|----------------|----------|-----------|")
    for p in r["provenance"]:
        ap(f"| {p['termo']} | {p['estatuto']} | {p['via']} | "
           f"{', '.join(p['offsets_ili']) or '—'} | {p['teste_decisivo']} | "
           f"{', '.join(p['garantia'])} | {p['definicao'] or '—'} |")
    ap("")
    if r["stage5"]["pending"]:
        ap("### Pendentes (necessitam de decisão na spec `adjudication`)")
        ap(", ".join(sorted(v.get("display", k) for k, v in r["stage5"]["pending"].items())))
        ap("")

    ap("## §6 — Mapeamento SKOS-XL / OWL (só Bloco A)")
    sk = r["skos"]
    ap(f"- `skos:prefLabel` → **{r['pref_label']}**")
    ap(f"- `skosxl:altLabel` (UF) → {', '.join(sk.get('UF', [])) or '—'}")
    ap(f"- `:termoRelacionado` (RT) → {', '.join(sk.get('RT', [])) or '—'}")
    ap(f"- `skos:broader` (BT) → {', '.join(sk.get('BT', [])) or '—'}")
    ap(f"- `skos:narrower` (NT) → {', '.join(sk.get('NT', [])) or '—'}")
    ap("")
    ap("_Evidência (`atributo`, oposição, vizinha, sinalização) NÃO é serializada "
       "como relação SKOS/SKOS-XL._")
    ap("")
    return "\n".join(L)


def emit_whitelist(result: dict, spec: ClassSpec) -> dict:
    """Whitelist in the schema phase0_skos.py consumes as `stage1_whitelist`."""
    stage1 = []
    for e in spec.stage1_whitelist:
        decision = str(e.get("decision", ""))
        members = e.get("members", [])
        # for admitted senses, prefer the export's own synonyms as members
        ili = (e.get("ili_offset") or "").strip()
        stage1.append({"ili_offset": ili, "glosa": e.get("glosa", ""),
                       "decision": decision, "members": members})
    seed_members = sorted({m for e in spec.stage1_whitelist
                           if e.get("decision") in DECISION_ADMIT
                           for m in e.get("members", [])})
    return {
        "class_id": result["class_id"],
        "pref_label": result["pref_label"],
        "axis": result["axis"],
        "stage1_whitelist": stage1,
        "dictionary_attestations": seed_members,
        "admitted_offsets": result["stage1"]["admitted_offsets"],
        "excluded_offsets": result["stage1"]["excluded_offsets"],
    }


# ---------------------------------------------------------------------------
# API + CLI
# ---------------------------------------------------------------------------
def run_spec(spec_path: Path, outdir: Path,
             export_path: Optional[Path] = None,
             export_data: Optional[dict] = None) -> dict:
    spec = ClassSpec.load(spec_path)
    export = load_pulo_export(export_path, export_data)
    engine = PuloPhase0Engine(spec, export)
    result = engine.run()

    # Build + validate SKOS graph with rdflib, then serialize.
    graph = build_graph(result, list(spec.disjoint_classes.keys()))
    ttl = graph.serialize(format="turtle")
    expected_triples = len(graph)
    # parse-check: the serialized Turtle must round-trip with the same triple count
    from rdflib import Graph as _G
    parsed = _G().parse(data=ttl, format="turtle")
    result["skos_triples"] = len(parsed)
    result["_ttl_ok"] = (len(parsed) == expected_triples and expected_triples > 0)
    result["assertions"].append({
        "stage": "Serialização", "passed": bool(result["_ttl_ok"]),
        "text": "X.skos.ttl analisa com rdflib e tem a contagem de triplos esperada.",
        "evidence": f"triplos esperados={expected_triples}, analisados={len(parsed)}",
    })
    result["all_passed"] = all(a["passed"] for a in result["assertions"])

    outdir.mkdir(parents=True, exist_ok=True)
    base = outdir / spec.class_id
    base.with_suffix(".result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    base.with_suffix(".report.md").write_text(render_markdown(result), encoding="utf-8")
    base.with_suffix(".skos.ttl").write_text(ttl, encoding="utf-8")
    base.with_suffix(".whitelist.json").write_text(
        json.dumps(emit_whitelist(result, spec), ensure_ascii=False, indent=2),
        encoding="utf-8")
    result["_report_path"] = str(base.with_suffix(".report.md"))
    return result


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Fase 0 — selecção lexical PULO (camada SKOS).")
    ap.add_argument("spec", help="ficheiro JSON de especificação da classe")
    ap.add_argument("--pulo-export", default=None,
                    help="export JSON do PULO Thesaurus GUI (obrigatório se não em memória)")
    ap.add_argument("--outdir", default=str(here / "fase0"),
                    help="pasta de saída (predef.: ./fase0)")
    args = ap.parse_args()

    spec_path = Path(args.spec)
    export_path = Path(args.pulo_export) if args.pulo_export else None
    if export_path is None:
        print("ERRO: forneça --pulo-export <pulo.json> (exportado no PULO Thesaurus GUI).")
        return 2
    result = run_spec(spec_path, Path(args.outdir), export_path=export_path)
    passed = sum(1 for a in result["assertions"] if a["passed"])
    total = len(result["assertions"])
    print(f"Relatório: {result['_report_path']}")
    print(f"Asserções: {passed}/{total} PASS — "
          + ("TODAS PASSARAM" if result["all_passed"] else "EXISTEM FALHAS"))
    for a in result["assertions"]:
        print(("  [PASS] " if a["passed"] else "  [FAIL] ") + f"{a['stage']}: {a['text']}")
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
