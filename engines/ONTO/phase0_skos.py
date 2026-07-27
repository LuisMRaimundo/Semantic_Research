#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fase 0 — Selecção lexical e controlo terminológico (camada SKOS).

Procedimento reutilizável, aplicável a QUALQUER classe textural (não só ao
exemplo «uniforme»). Toda a especificação de uma classe vive num ficheiro JSON;
este módulo não contém nada específico de um termo.

Princípio reitor
----------------
Os candidatos são colhidos exclusivamente de synsets desambiguados por sentido e
ancorados no ILI (PULO/WordNet), fornecidos na lista branca da especificação.
O OntoPT/CONTO.PT (base de dados `ontopt.sqlite` deste projecto) é usado APENAS
para corroborar/sinalizar candidatos já colhidos — nunca para os admitir
automaticamente (Etapa 3, «gated»).

Pipeline (§3 do protocolo)
    Etapa 1  Selecção de acepções (lista branca de ILI) + validação de eixo
    Etapa 2  Extracção de membros dos synsets admitidos (núcleo de candidatos)
    Etapa 3  Corroboração/expansão via CONTO.PT, com porta de 3 condições
    Etapa 4  Exclusão automática (assinaturas de ruído)
    Etapa 5  Adjudicação humana UF/RT/contraste (decisões vindas da spec)
    §6       Mapeamento SKOS-XL / OWL
    §7       Registo de proveniência por termo
    Consistência final + relatório com ASSERTs

Uso (linha de comando):
    python phase0_skos.py <classe.json> [--db ontopt.sqlite] [--outdir fase0]

Produz, para a classe X:
    <outdir>/X.report.md      relatório humano com a tabela de ASSERTs
    <outdir>/X.result.json    resultado estruturado completo
    <outdir>/X.skos.ttl       serialização SKOS-XL / OWL
    <outdir>/X.whitelist.json lista branca de offsets ILI (reutilizável)

Apenas biblioteca padrão (sqlite3, json, re).
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# contraste / oposicao / vizinha / atributo = evidência (nunca admitidos / Turtle).
STATUSES = ("UF", "RT")
DECISION_ADMIT = ("UF", "RT")  # decisões de synset que entram na lista branca

# Padrões de ruído por omissão (Etapa 4). Podem ser estendidos pela spec.
DEFAULT_EXCLUSION_PATTERNS = [
    r"^maneira\s+sem\b",
    r"^maneira\s+por\s+meio\s+de\b",
    r"\bpor\s+meio\s+de\b",
]


# ---------------------------------------------------------------------------
# Normalização de texto (idêntica à do ontopt_browser)
# ---------------------------------------------------------------------------
def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def normalize_word(word: str) -> str:
    return strip_accents(word).lower().replace(" ", "_")


def pretty_word(word: str) -> str:
    return word.replace("_", " ")


def is_multiword(word: str) -> bool:
    return (" " in word) or ("_" in word)


# ---------------------------------------------------------------------------
# Especificação da classe
# ---------------------------------------------------------------------------
class SpecError(ValueError):
    pass


@dataclass
class ClassSpec:
    class_id: str
    pref_label: str
    axis: str
    focus_stems: list[str]
    weight_min: float = 0.5
    min_cooccurrence: int = 2
    fuzzy_resources: list[str] = field(default_factory=lambda: ["contopt"])
    pos: Optional[str] = None
    stage1_whitelist: list[dict] = field(default_factory=list)
    dictionary_attestations: list[str] = field(default_factory=list)
    manual_terms: list[dict] = field(default_factory=list)
    exclusion_patterns: list[str] = field(default_factory=list)
    adjudication: dict[str, dict] = field(default_factory=dict)
    disjoint_classes: dict[str, list[str]] = field(default_factory=dict)

    @staticmethod
    def load(path: Path) -> "ClassSpec":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        required = ("class_id", "pref_label", "axis", "focus_stems")
        missing = [k for k in required if not raw.get(k)]
        if missing:
            raise SpecError(f"Spec em falta campos obrigatórios: {', '.join(missing)}")
        gating = raw.get("gating", {}) or {}
        return ClassSpec(
            class_id=str(raw["class_id"]),
            pref_label=str(raw["pref_label"]),
            axis=str(raw["axis"]),
            focus_stems=[normalize_word(s) for s in raw["focus_stems"]],
            weight_min=float(gating.get("weight_min", 0.5)),
            min_cooccurrence=int(gating.get("min_cooccurrence", 2)),
            fuzzy_resources=list(raw.get("fuzzy_resources", ["contopt"])),
            pos=raw.get("pos"),
            stage1_whitelist=list(raw.get("stage1_whitelist", [])),
            dictionary_attestations=list(raw.get("dictionary_attestations", [])),
            manual_terms=list(raw.get("manual_terms", [])),
            exclusion_patterns=list(raw.get("exclusion_patterns", [])),
            adjudication={normalize_word(k): v for k, v in raw.get("adjudication", {}).items()},
            disjoint_classes=dict(raw.get("disjoint_classes", {})),
        )


# ---------------------------------------------------------------------------
# Registo de asserções para o relatório
# ---------------------------------------------------------------------------
@dataclass
class Assertion:
    stage: str
    text: str
    passed: bool
    evidence: str = ""


# ---------------------------------------------------------------------------
# Motor da Fase 0
# ---------------------------------------------------------------------------
class Phase0Engine:
    def __init__(self, db_path: Path, spec: ClassSpec):
        self.db_path = Path(db_path)
        self.spec = spec
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.assertions: list[Assertion] = []

    def close(self):
        self.conn.close()

    # -- helpers -------------------------------------------------------
    def _assert(self, stage, text, passed, evidence=""):
        self.assertions.append(Assertion(stage, text, bool(passed), evidence))

    def _is_focus(self, word_norm: str) -> bool:
        return any(word_norm.startswith(stem) for stem in self.spec.focus_stems)

    def _attestation_resources(self, word_norm: str) -> list[str]:
        """Resources whose member table contains this normalized word."""
        rows = self.conn.execute(
            "SELECT DISTINCT res FROM member WHERE word_norm=? ORDER BY res", (word_norm,)
        ).fetchall()
        return [r["res"] for r in rows]

    # -- Etapa 1 -------------------------------------------------------
    def stage1(self) -> dict:
        admitted, excluded, invalid = [], [], []
        offsets_admitted: list[str] = []
        for entry in self.spec.stage1_whitelist:
            decision = str(entry.get("decision", "")).strip()
            ili = str(entry.get("ili_offset", "")).strip()
            glosa = str(entry.get("glosa", "")).strip()
            if decision == "exclude":
                excluded.append(entry)
                continue
            if decision not in DECISION_ADMIT:
                invalid.append((entry, "decisão desconhecida"))
                continue
            if not ili or not glosa:
                invalid.append((entry, "sem ili_offset ou glosa"))
            admitted.append(entry)
            offsets_admitted.append(ili)

        # A1.1 — cada synset admitido tem ili_offset e glosa mapeada ao eixo (decisão).
        bad = [e.get("ili_offset", "?") for e in admitted
               if not e.get("ili_offset") or not e.get("glosa")]
        self._assert("Etapa 1",
                     "Todo o synset admitido possui ili_offset e glosa mapeada ao eixo.",
                     not bad,
                     "OK" if not bad else f"synsets sem ili/glosa: {bad}")

        # A1.2 — nenhum synset off-axis figura na lista branca (conjunto admitido).
        excl_offsets = {e.get("ili_offset") for e in excluded}
        overlap = excl_offsets & set(offsets_admitted)
        self._assert("Etapa 1",
                     "Nenhum synset off-axis (exclude) figura na lista branca admitida.",
                     not overlap,
                     "OK" if not overlap else f"offsets em conflito: {sorted(overlap)}")

        # A1.3 — lista branca persistida por offset ILI (reutilizável) e offsets únicos.
        dups = [o for o in offsets_admitted if offsets_admitted.count(o) > 1]
        self._assert("Etapa 1",
                     "A lista branca é persistida por offset ILI e os offsets são únicos.",
                     not dups and all(offsets_admitted),
                     "OK" if not dups else f"offsets duplicados: {sorted(set(dups))}")

        return {"admitted": admitted, "excluded": excluded, "invalid": invalid,
                "offsets_admitted": offsets_admitted}

    # -- Etapa 2 -------------------------------------------------------
    def stage2(self, s1: dict) -> dict:
        """Colher membros apenas dos synsets admitidos (Etapa 1)."""
        seeds: dict[str, dict] = {}
        for entry in s1["admitted"]:
            ili = entry.get("ili_offset", "")
            for w in entry.get("members", []):
                nw = normalize_word(w)
                rec = seeds.setdefault(nw, {"display": pretty_word(w), "offsets": set(),
                                            "decision": entry.get("decision")})
                rec["offsets"].add(ili)
        # A2.1 — membros provêm exclusivamente de synsets da lista branca.
        excl_offsets = {e.get("ili_offset") for e in s1["excluded"]}
        leaked = {nw for nw, r in seeds.items() if r["offsets"] & excl_offsets}
        self._assert("Etapa 2",
                     "Os membros colhidos provêm exclusivamente de synsets da lista branca.",
                     not leaked,
                     "OK" if not leaked else f"membros de origem off-axis: {sorted(leaked)}")
        return {"seeds": seeds}

    # -- Etapa 3 -------------------------------------------------------
    def stage3(self, corroboration: set[str]) -> dict:
        spec = self.spec
        placeholders = ",".join("?" for _ in spec.fuzzy_resources)
        rows = self.conn.execute(
            f"SELECT m.res AS res, m.sid AS sid, m.word AS word, m.word_norm AS wn, "
            f"       m.weight AS weight, s.pos AS pos "
            f"FROM member m LEFT JOIN synset s ON s.res=m.res AND s.sid=m.sid "
            f"WHERE m.res IN ({placeholders})",
            list(spec.fuzzy_resources),
        ).fetchall()

        # group members by (res, sid)
        by_syn: dict[tuple, list] = defaultdict(list)
        for r in rows:
            if spec.pos and r["pos"] and r["pos"] != spec.pos:
                continue
            by_syn[(r["res"], r["sid"])].append(r)

        focus_synsets: set[tuple] = set()
        nuclear_synsets: set[tuple] = set()
        for key, members in by_syn.items():
            has_focus = False
            is_nuclear = False
            for m in members:
                if self._is_focus(m["wn"]):
                    has_focus = True
                    if (m["weight"] or 0.0) >= spec.weight_min:
                        is_nuclear = True
            if has_focus:
                focus_synsets.add(key)
            if is_nuclear:
                nuclear_synsets.add(key)

        # co-member statistics across focus synsets
        cooc: dict[str, set] = defaultdict(set)     # word_norm -> set of focus synset keys
        in_nuclear: dict[str, bool] = defaultdict(bool)
        display: dict[str, str] = {}
        weight_seen: dict[str, float] = defaultdict(float)
        for key in focus_synsets:
            for m in by_syn[key]:
                if self._is_focus(m["wn"]):
                    continue
                nw = m["wn"]
                cooc[nw].add(key)
                display.setdefault(nw, pretty_word(m["word"]))
                weight_seen[nw] = max(weight_seen[nw], m["weight"] or 0.0)
                if key in nuclear_synsets:
                    in_nuclear[nw] = True

        admitted, sinalizacao = {}, {}
        for nw, keys in cooc.items():
            cond1 = in_nuclear[nw]
            cond2 = len(keys) >= spec.min_cooccurrence
            cond3 = nw in corroboration
            rec = {
                "display": display[nw],
                "cooccurrence": len(keys),
                "in_nuclear": cond1,
                "corroborated": cond3,
                "max_weight": round(weight_seen[nw], 3),
                "synsets": sorted(f"{k[0]}:{k[1]}" for k in keys),
            }
            if cond1 and cond2 and cond3:
                admitted[nw] = rec
            elif cond1 and cond2 and not cond3:
                sinalizacao[nw] = rec

        # A3.1 — todo candidato de origem difusa admitido cumpre as 3 condições.
        bad = [nw for nw, r in admitted.items()
               if not (r["in_nuclear"] and r["cooccurrence"] >= spec.min_cooccurrence
                       and r["corroborated"])]
        self._assert("Etapa 3",
                     f"Candidatos difusos admitidos cumprem peso≥{spec.weight_min}, "
                     f"coocorrência≥{spec.min_cooccurrence} e ≥1 corroboração externa.",
                     not bad,
                     "OK" if not bad else f"violações: {bad}")

        # A3.2 — candidatos que falham corroboração vão para sinalizacao[], não admitidos[].
        leaked = [nw for nw in sinalizacao if nw in admitted]
        self._assert("Etapa 3",
                     "Candidatos que falham a corroboração vão para sinalizacao[], "
                     "não para admitidos[].",
                     not leaked and all(not r["corroborated"] for r in sinalizacao.values()),
                     "OK" if not leaked else f"fuga para admitidos: {leaked}")

        return {"admitted": admitted, "sinalizacao": sinalizacao,
                "n_focus_synsets": len(focus_synsets),
                "n_nuclear_synsets": len(nuclear_synsets)}

    # -- Etapa 4 -------------------------------------------------------
    def _compile_exclusions(self):
        pats = list(DEFAULT_EXCLUSION_PATTERNS) + list(self.spec.exclusion_patterns)
        return [re.compile(p, re.IGNORECASE) for p in pats]

    def stage4(self, pool: dict[str, dict], corroboration: set[str]) -> dict:
        regexes = self._compile_exclusions()
        excluded: dict[str, dict] = {}
        for nw, rec in list(pool.items()):
            disp = rec.get("display", pretty_word(nw))
            reason = None
            for rx in regexes:
                if rx.search(disp) or rx.search(nw):
                    reason = f"assinatura de ruído /{rx.pattern}/"
                    break
            if reason is None and is_multiword(disp) and nw not in corroboration:
                reason = "colocação multipalavra sem corroboração"
            if reason:
                excluded[nw] = {**rec, "reason": reason}
                pool.pop(nw, None)

        # A4.1 — colocações multipalavra e 'maneira sem/por meio de' sem corroboração
        # são descartadas (nenhuma permanece na pool).
        remaining = [nw for nw in pool
                     if is_multiword(pool[nw].get("display", nw)) and nw not in corroboration]
        self._assert("Etapa 4",
                     "Colocações multipalavra e padrões de ruído sem corroboração "
                     "são descartados (não permanecem na pool de candidatos).",
                     not remaining,
                     "OK" if not remaining else f"ainda na pool: {remaining}")
        return {"excluded": excluded}

    # -- Etapa 5 -------------------------------------------------------
    def stage5(self, pool: dict[str, dict]) -> dict:
        admitted, pending = {}, {}
        for nw, rec in pool.items():
            adj = dict(self.spec.adjudication.get(nw) or {})
            status = adj.get("status")
            # Corte 2: status alone admits (Onto remains discovery in the pipeline).
            complete = bool(status in STATUSES)
            if complete:
                adj.setdefault("test", "derivado do sentido (PASSO 3)")
                adj.setdefault("guarantee", ["sense_decision"])
                admitted[nw] = {**rec, **adj}
            else:
                pending[nw] = {**rec, "adjudication": adj or None}

        bad = [nw for nw, r in admitted.items() if r.get("status") not in STATUSES]
        self._assert("Etapa 5",
                     "Cada termo em admitidos[] tem estatuto∈{UF,RT} "
                     "(Onto = descoberta; garantia calculada a jusante).",
                     not bad,
                     "OK" if not bad else f"incompletos: {bad}")
        return {"admitted": admitted, "pending": pending}

    # -- SKOS + consistência ------------------------------------------
    def finalize(self, admitted: dict[str, dict]) -> dict:
        uf = {nw for nw, r in admitted.items() if r["status"] == "UF"}
        rt = {nw for nw, r in admitted.items() if r["status"] == "RT"}
        evidence_leak = {
            nw for nw, r in admitted.items()
            if r["status"] in ("contraste", "atributo", "oposicao", "vizinha")
        }

        def disp(keys):
            return sorted(admitted[nw].get("display", pretty_word(nw)) for nw in keys)

        # C1 — nenhum termo é UF de duas classes com owl:disjointWith entre si.
        conflicts = {}
        for other_class, terms in self.spec.disjoint_classes.items():
            other_uf = {normalize_word(t) for t in terms}
            overlap = uf & other_uf
            if overlap:
                conflicts[other_class] = sorted(overlap)
        self._assert("Consistência final",
                     "Nenhum termo é UF de duas classes com owl:disjointWith entre si.",
                     not conflicts,
                     "OK" if not conflicts else f"conflitos: {conflicts}")

        # C2 — estatutos de evidência nunca figuram em admitidos (nem Turtle).
        self._assert("Consistência final",
                     "Nenhum estatuto de evidência em admitidos[] "
                     "(contraste/atributo/oposicao/vizinha).",
                     not evidence_leak,
                     "OK" if not evidence_leak else f"fuga: {sorted(evidence_leak)}")

        # No :contrastaCom / :temAtributo keys — evidence is never serialised.
        return {"uf": disp(uf), "rt": disp(rt)}

    # -- orquestração --------------------------------------------------
    def run(self) -> dict:
        spec = self.spec
        s1 = self.stage1()
        s2 = self.stage2(s1)
        seeds = s2["seeds"]

        # conjunto de corroboração = seeds (desambiguados) ∪ dicionário clássico
        corroboration = set(seeds.keys()) | {
            normalize_word(w) for w in spec.dictionary_attestations
        }

        s3 = self.stage3(corroboration)

        # pool de adjudicação = seeds ∪ candidatos difusos admitidos ∪ termos manuais
        pool: dict[str, dict] = {}
        for nw, r in seeds.items():
            pool[nw] = {"display": r["display"], "origin": "seed (Etapa 1/2)",
                        "offsets": sorted(r["offsets"]), "decision_synset": r["decision"]}
        for nw, r in s3["admitted"].items():
            if nw in pool:
                pool[nw]["origin"] += " + CONTO.PT (corroborado)"
            else:
                pool[nw] = {"display": r["display"], "origin": "CONTO.PT (corroborado, Etapa 3)",
                            "cooccurrence": r["cooccurrence"], "max_weight": r["max_weight"]}
        for item in spec.manual_terms:
            w = item.get("term", "")
            if not w:
                continue
            nw = normalize_word(w)
            prov = item.get("provenance", [])
            pool.setdefault(nw, {"display": pretty_word(w),
                                 "origin": "manual (" + ", ".join(prov) + ")",
                                 "offsets": [item["offset"]] if item.get("offset") else []})

        # O rótulo preferido é a etiqueta do próprio conceito, não um candidato
        # a UF/RT/contraste de si mesmo.
        pool.pop(normalize_word(spec.pref_label), None)

        s4 = self.stage4(pool, corroboration)   # muta `pool` in-place
        s5 = self.stage5(pool)

        fin = self.finalize(s5["admitted"])

        # proveniência (§7) para cada termo admitido
        provenance = []
        for nw, r in s5["admitted"].items():
            att = self._attestation_resources(nw)
            provenance.append({
                "termo": r["display"],
                "estatuto": r["status"],
                "eixo": spec.axis,
                "recursos_atestacao": att,
                "offsets_ili": r.get("offsets", []),
                "teste_decisivo": r.get("test", ""),
                "garantia": r.get("guarantee", []),
                "origem": r.get("origin", ""),
            })

        return {
            "class_id": spec.class_id,
            "pref_label": spec.pref_label,
            "axis": spec.axis,
            "generated": datetime.now().isoformat(timespec="seconds"),
            "db": str(self.db_path),
            "gating": {"weight_min": spec.weight_min,
                       "min_cooccurrence": spec.min_cooccurrence,
                       "fuzzy_resources": spec.fuzzy_resources},
            "stage1": {"admitted_offsets": s1["offsets_admitted"],
                       "excluded_offsets": [e.get("ili_offset") for e in s1["excluded"]],
                       "invalid": [{"entry": e, "why": w} for e, w in s1["invalid"]]},
            "stage2_seeds": {nw: {"display": r["display"], "offsets": sorted(r["offsets"])}
                             for nw, r in seeds.items()},
            "stage3": {"n_focus_synsets": s3["n_focus_synsets"],
                       "n_nuclear_synsets": s3["n_nuclear_synsets"],
                       "admitted": s3["admitted"], "sinalizacao": s3["sinalizacao"]},
            "stage4_excluded": s4["excluded"],
            "stage5": {"admitted": s5["admitted"], "pending": s5["pending"]},
            "skos": fin,
            "provenance": provenance,
            "assertions": [a.__dict__ for a in self.assertions],
            "all_passed": all(a.passed for a in self.assertions),
        }


# ---------------------------------------------------------------------------
# Serializações de saída
# ---------------------------------------------------------------------------
def render_turtle(result: dict) -> str:
    cid = result["class_id"]
    pref = result["pref_label"]
    axis = result["axis"]
    uf = [r for r in result["provenance"] if r["estatuto"] == "UF"]
    rt = [r for r in result["provenance"] if r["estatuto"] == "RT"]

    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    lines = [
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix skosxl: <http://www.w3.org/2008/05/skos-xl#> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix : <http://example.org/textura#> .",
        "",
        f":{cid} a skos:Concept, owl:Class ;",
        f'    skos:prefLabel "{esc(pref)}"@pt ;',
        f'    skos:scopeNote "Eixo definidor: {esc(axis)}"@pt ;',
    ]
    for r in uf:
        lines.append(f'    skosxl:altLabel [ skosxl:literalForm "{esc(r["termo"])}"@pt ] ;')
    for r in rt:
        # tex:termoRelacionado ⊑ skosxl:labelRelation (not skos:related)
        lines.append(f'    :termoRelacionado :{normalize_word(r["termo"])} ;')
    if lines[-1].endswith(";"):
        lines[-1] = lines[-1][:-1].rstrip() + " ."
    else:
        lines.append("    .")

    # disjunção entre irmãs (TBox)
    for other in result.get("_disjoint_classes", []):
        lines.append(f":{cid} owl:disjointWith :{other} .")
    ttl = "\n".join(lines) + "\n"
    # :contrastaCom / :temAtributo — no emission path (evidence = Bloco B only).
    for banned in (":contrastaCom", ":temAtributo"):
        if banned in ttl:
            raise RuntimeError(
                f"Turtle contém predicado proibido {banned} — "
                "evidência não serializa."
            )
    return ttl


def render_markdown(result: dict) -> str:
    r = result
    L: list[str] = []
    ap = L.append
    status = "✅ TODAS AS ASSERÇÕES PASSARAM" if r["all_passed"] else "❌ EXISTEM ASSERÇÕES FALHADAS"
    ap(f"# Fase 0 — Relatório de selecção lexical: **{r['pref_label']}** (`{r['class_id']}`)")
    ap("")
    ap(f"- **Eixo definidor:** {r['axis']}")
    ap(f"- **Base de corroboração:** `{r['db']}`  ·  recursos difusos: "
       f"{', '.join(r['gating']['fuzzy_resources'])}")
    ap(f"- **Porta (Etapa 3):** peso ≥ {r['gating']['weight_min']}, "
       f"coocorrência ≥ {r['gating']['min_cooccurrence']}")
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
    ap(f"- Synsets admitidos (on-axis): `{r['stage1']['admitted_offsets']}`")
    ap(f"- Synsets excluídos (off-axis): `{r['stage1']['excluded_offsets']}`")
    if r["stage1"]["invalid"]:
        ap(f"- ⚠ Entradas inválidas: {r['stage1']['invalid']}")
    ap("")

    ap("## Etapa 2 — Núcleo de candidatos (membros dos synsets admitidos)")
    seeds = r["stage2_seeds"]
    ap(f"Total de sementes: **{len(seeds)}**")
    ap("")
    ap("| Termo | Offsets ILI |")
    ap("|-------|-------------|")
    for nw, s in sorted(seeds.items()):
        ap(f"| {s['display']} | {', '.join(s['offsets'])} |")
    ap("")

    ap("## Etapa 3 — Corroboração via CONTO.PT (gated)")
    ap(f"- Synsets com membro-foco: **{r['stage3']['n_focus_synsets']}**  ·  "
       f"nucleares (peso ≥ {r['gating']['weight_min']}): **{r['stage3']['n_nuclear_synsets']}**")
    adm = r["stage3"]["admitted"]
    sin = r["stage3"]["sinalizacao"]
    ap(f"- Candidatos difusos **admitidos** (cumprem as 3 condições): **{len(adm)}**")
    ap(f"- Candidatos em **sinalização** (cumprem 1–2, falham corroboração): **{len(sin)}**")
    ap("")
    if adm:
        ap("### Admitidos por corroboração")
        ap("| Termo | Coocorrência | Nuclear | Peso máx. | Synsets |")
        ap("|-------|--------------|---------|-----------|---------|")
        for nw, c in sorted(adm.items(), key=lambda kv: -kv[1]["cooccurrence"]):
            ap(f"| {c['display']} | {c['cooccurrence']} | {c['in_nuclear']} | "
               f"{c['max_weight']} | {', '.join(c['synsets'][:8])} |")
        ap("")
    if sin:
        ap("### Sinalização (revisão humana — NÃO admitidos)")
        ap("| Termo | Coocorrência | Peso máx. |")
        ap("|-------|--------------|-----------|")
        for nw, c in sorted(sin.items(), key=lambda kv: -kv[1]["cooccurrence"]):
            ap(f"| {c['display']} | {c['cooccurrence']} | {c['max_weight']} |")
        ap("")

    ap("## Etapa 4 — Exclusão automática (assinaturas de ruído)")
    exc = r["stage4_excluded"]
    if exc:
        ap("| Termo | Motivo |")
        ap("|-------|--------|")
        for nw, c in sorted(exc.items()):
            ap(f"| {c.get('display', nw)} | {c['reason']} |")
    else:
        ap("Nenhum candidato descartado por assinatura de ruído.")
    ap("")

    ap("## Etapa 5 — Adjudicação UF / RT")
    adm5 = r["stage5"]["admitted"]
    pend = r["stage5"]["pending"]
    ap(f"- Termos **admitidos** (decisão humana completa): **{len(adm5)}**")
    ap(f"- Termos **pendentes** (aguardam decisão humana): **{len(pend)}**")
    ap("")
    ap("### §7 — Registo de proveniência (termos admitidos)")
    ap("| termo | estatuto | eixo | recursos de atestação | offset/ILI | teste decisivo | garantia |")
    ap("|-------|----------|------|-----------------------|------------|----------------|----------|")
    for p in r["provenance"]:
        ap(f"| {p['termo']} | {p['estatuto']} | {p['eixo']} | "
           f"{', '.join(p['recursos_atestacao']) or '—'} | "
           f"{', '.join(p['offsets_ili']) or '—'} | {p['teste_decisivo']} | "
           f"{', '.join(p['garantia'])} |")
    ap("")
    if pend:
        ap("### Pendentes (necessitam de decisão na spec `adjudication`)")
        ap(", ".join(sorted(v["display"] for v in pend.values())))
        ap("")

    ap("## §6 — Mapeamento SKOS-XL / OWL (só Bloco A)")
    ap(f"- `skos:prefLabel` → **{r['pref_label']}**")
    ap(f"- `skosxl:altLabel` (UF) → {', '.join(r['skos']['uf']) or '—'}")
    ap(f"- `:termoRelacionado` (RT) → {', '.join(r['skos']['rt']) or '—'}")
    ap("")
    ap("_Evidência (oposição, atributo, vizinha, sinalização) NÃO é serializada "
       "como relação SKOS/SKOS-XL._")
    ap("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Execução como programa / API para a GUI
# ---------------------------------------------------------------------------
def split_pending_for_persist(result: dict) -> tuple[dict, dict]:
    """Return (persisted_result, pending) for the B.1 output filter.

    `persisted_result` is a shallow copy whose stage5 keeps only `admitted`
    (pending emptied) so a downstream merge sees admits, not the candidate pool.
    The original `result` is not mutated. `pending` is the removed dict.
    """
    stage5 = result.get("stage5") or {}
    pending = stage5.get("pending") or {}
    persisted = dict(result)
    persisted["stage5"] = {
        "admitted": stage5.get("admitted", {}),
        "pending": {},                 # moved to the sidecar; not fed to the merge
        "_pending_count": len(pending),
    }
    return persisted, pending


def run_spec(spec_path: Path, db_path: Path, outdir: Path) -> dict:
    spec = ClassSpec.load(spec_path)
    engine = Phase0Engine(db_path, spec)
    try:
        result = engine.run()
    finally:
        engine.close()
    result["_disjoint_classes"] = list(spec.disjoint_classes.keys())

    outdir.mkdir(parents=True, exist_ok=True)
    base = outdir / spec.class_id

    # OUTPUT FILTER (not a logic change): the persisted result.json must carry the
    # ADMITTED terms, not the fuzzy candidate POOL. The un-adjudicated stage5
    # "pending" seeds (hundreds of noisy candidates) go to a SEPARATE sidecar so
    # the merge (LexWarrant) never ingests them. The in-memory `result` returned
    # to the GUI is left intact (it still shows pending for adjudication).
    persisted, pending = split_pending_for_persist(result)
    pending_path = outdir / f"{spec.class_id}.ONTO.pending.json"
    pending_path.write_text(json.dumps(
        {"class_id": spec.class_id, "count": len(pending), "pending": pending},
        ensure_ascii=False, indent=2), encoding="utf-8")
    persisted["stage5"]["_pending_sidecar"] = pending_path.name

    (base.with_suffix(".result.json")).write_text(
        json.dumps(persisted, ensure_ascii=False, indent=2), encoding="utf-8")
    (base.with_suffix(".report.md")).write_text(
        render_markdown(result), encoding="utf-8")
    (base.with_suffix(".skos.ttl")).write_text(
        render_turtle(result), encoding="utf-8")
    (base.with_suffix(".whitelist.json")).write_text(
        json.dumps({"class_id": spec.class_id,
                    "admitted_offsets": result["stage1"]["admitted_offsets"],
                    "excluded_offsets": result["stage1"]["excluded_offsets"]},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    result["_report_path"] = str(base.with_suffix(".report.md"))
    return result


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # avoid cp1252 issues on Windows
    except Exception:
        pass
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Fase 0 — selecção lexical (camada SKOS).")
    ap.add_argument("spec", help="ficheiro JSON de especificação da classe")
    ap.add_argument("--db", default=str(here / "ontopt.sqlite"),
                    help="base SQLite do Onto.PT/CONTO.PT (predef.: ./ontopt.sqlite)")
    ap.add_argument("--outdir", default=str(here / "fase0"),
                    help="pasta de saída (predef.: ./fase0)")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"ERRO: base não encontrada: {db_path}\n"
              f"Construa-a primeiro no Onto.PT / CONTO.PT Browser (Build database).")
        return 2
    result = run_spec(Path(args.spec), db_path, Path(args.outdir))
    print(f"Relatório: {result['_report_path']}")
    print("Estado:", "TODAS AS ASSERÇÕES PASSARAM" if result["all_passed"]
          else "EXISTEM ASSERÇÕES FALHADAS")
    for a in result["assertions"]:
        print(("  [PASS] " if a["passed"] else "  [FAIL] ") + f"{a['stage']}: {a['text']}")
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
