#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LexWarrant — relator de garantia/concordância cruzada ancorado no ILI.

Esta é a etapa FINAL, de RELATO, do Protocolo Fase 0. NÃO admite nem classifica
termos. Ingere os `result.json` por-fonte produzidos pelos motores existentes
(phase0_skos = ONTO, phase0_pulo = PULO e, mais tarde, o export enriquecido da
WordNet), junta os veredictos POR ILI e produz uma matriz de concordância + um
veredicto por termo que um humano usa para atribuir a garantia final por
convergência. RELATA; nunca decide.

Não existe qualquer mecanismo que promova um termo a um estatuto por CONTAGEM de
fontes — isso reintroduziria a fronteira métrica UF/RT que o protocolo rejeita.
`proposta_final` é sempre uma SUGESTÃO para o humano, nunca uma auto-admissão.

Uso:
    python lexwarrant.py <a.result.json> <b.result.json> [...]
                         [--source ROTULO=ficheiro.json]...
                         [--policy conservative|informed] [--outdir .]

Saídas (para a classe X):
    X.concordance.md     matriz legível + contagens por veredicto
    X.concordance.json   máquina: por-conceito {term, ili, sources, join,
                         veredicto, proposta_final, divergences, union_of_provenance}

Sem dependências além da biblioteca padrão.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# Fixed columns — OWN-PT is distinct from WordNet/OEWN (different authorship).
SOURCE_COLUMNS = ["ONTO", "PULO", "OWN-PT", "WordNet"]
ABSENT = "—"

ADMIT_STATUSES = {"UF", "RT", "BT", "NT"}
SIGNAL = "sinalizacao"
PENDING = "pendente"           # ONTO/PULO stage5 seeds awaiting human adjudication
ATESTATO = "atestado"          # OWN-PT entry warrant — NOT an admit status
# Evidence-only / legacy (never counted as admitted; never proposta_final).
EVIDENCE_STATUSES = frozenset({
    "atributo", "oposicao", "vizinha", "contraste",
})
NONADMIT = frozenset({SIGNAL, PENDING, ATESTATO}) | EVIDENCE_STATUSES
# Resources that project Princeton WordNet's conceptual structure (PWN-derived).
PWN_DERIVED_SOURCES = frozenset({"PULO", "OWN-PT"})
PWN_DERIVED_NOTE = (
    "concordância entre recursos derivados da mesma estrutura conceptual; "
    "não constitui atestação independente do português"
)

# --- Reticulado de estatutos para COMPARAÇÃO de veredicto --------------------
# Vocabulário admitido: {UF,RT,BT,NT}. atributo/oposicao/vizinha = evidência
# (não entram em ADMIT_STATUSES). BT/NT neutros na comparação.
STATUS_COMPAT: dict = {
    "UF": frozenset({"UF"}),
    "RT": frozenset({"RT"}),
    "BT": None,     # neutro — omitido da comparação
    "NT": None,     # neutro — omitido da comparação
}


def project_status_for_comparison(status: str):
    """Projecção de um estatuto rico no reticulado comparável.

    Devolve um frozenset de estatutos compatíveis, ou None quando o estatuto é
    neutro para comparação (BT/NT). Estatutos desconhecidos projectam-se em si
    mesmos (comparação estrita). NUNCA reescreve dados — serve só o veredicto.
    """
    if status in STATUS_COMPAT:
        return STATUS_COMPAT[status]
    return frozenset({status})


class SourceError(ValueError):
    """A source file could not be used; the message is user-facing/actionable."""

# --- Declared identity join keys (NEVER fabricate CILI) --------------------
# Prefer official CILI ``i…`` (surfaced as ``oewn-ili:i…`` for back-compat).
# PWN 3.0 offsets use local ``pwn30-…`` — never ``ili-30-…`` as if it were CILI.
# Legacy OMW/MCR ``ili-30-…`` / ``por-30-…`` are parsed as PWN 3.0 pivots only.
OMW30_NAMESPACES = {
    "ili-30", "por-30", "eng-30", "spa-30", "ita-30", "fra-30",
    "deu-30", "jpn-30", "nld-30", "pol-30",
}
_OMW30_RE = re.compile(r"^([a-z]{2,4})-30-(\d{8}-[a-z])$")
_OEWN_ILI_RE = re.compile(r"^i\d+$")


def canonical_ili(offset: str) -> tuple[Optional[str], bool]:
    """Map a source identifier to a join key without fabricating CILI.

    Returns (canonical_key, mapped). Prefer official CILI via the vendored
    map / OEWN ``ili`` attribute. Fall back to local ``pwn30-…`` for PWN 3.0
    pivots that lack a CILI row. Never emits ``ili-30-…`` as a join key.
    """
    if not offset:
        return (None, False)
    try:
        from identifiers import join_key
        return join_key(offset, resolve_cili=True)
    except Exception:  # noqa: BLE001 — keep LexWarrant import-hardy
        s = str(offset).strip()
        if s.startswith("oewn-ili:"):
            s = s.split(":", 1)[1].strip()
        if _OEWN_ILI_RE.match(s):
            return (f"oewn-ili:{s}", True)
        m = _OMW30_RE.match(s)
        if m and f"{m.group(1)}-30" in OMW30_NAMESPACES:
            return (f"pwn30-{m.group(2)}", True)
        if s.lower().startswith("pwn30-"):
            return (s.lower(), True)
        return (None, False)


class EquivMap:
    """Declared cross-namespace ILI equivalence (READ-ONLY; built elsewhere).

    LexWarrant never fabricates or extends this map — it only reads the `map`
    (high-confidence) rows of an ili_equivalence.json and unifies the canonical
    Identity keys they declare equal (e.g. oewn-ili:i10771 ↔ pwn30-00744506-a).
    Two entries join iff their canonical keys are equal OR unified here.
    """

    def __init__(self) -> None:
        self._parent: dict[str, str] = {}
        self.pairs: list[tuple[str, str]] = []   # (canonical_oewn, canonical_pulo)
        # counts read verbatim from the table so startup can prove it loaded
        self.n_map = 0
        self.n_review = 0
        self.n_unmatched = 0
        self.source_path: Optional[str] = None

    def _find(self, k: str) -> str:
        self._parent.setdefault(k, k)
        root = k
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[k] != root:      # path compression
            self._parent[k], k = root, self._parent[k]
        return root

    def add_equiv(self, a: Optional[str], b: Optional[str]) -> None:
        if not a or not b or a == b:
            return
        self.pairs.append((a, b))
        self._parent[self._find(a)] = self._find(b)

    def rep(self, key: str) -> str:
        return self._find(key) if key in self._parent else key

    def linked(self, k1: str, k2: str) -> bool:
        return k1 != k2 and self.rep(k1) == self.rep(k2)

    @property
    def empty(self) -> bool:
        return not self._parent

    @classmethod
    def load(cls, path: Path) -> "EquivMap":
        m = cls()
        m.source_path = str(path)
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        m.n_map = len(data.get("map", []) or [])
        m.n_review = len(data.get("review", []) or [])
        m.n_unmatched = len(data.get("unmatched", []) or [])
        for row in data.get("map", []):   # ONLY high-confidence rows enable joins
            a, a_ok = canonical_ili(row.get("oewn_ili", ""))
            b, b_ok = canonical_ili(row.get("pulo_ili", ""))
            if a_ok and b_ok:
                m.add_equiv(a, b)
        return m


def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def norm_term(term: str) -> str:
    """Casefold + strip diacritics FOR MATCHING ONLY (display keeps original)."""
    return strip_accents(term or "").casefold().strip().replace("_", " ")


class ClassMismatch(ValueError):
    pass


# ---------------------------------------------------------------------------
# Ingest — accept the REAL schema emitted by phase0_skos.py / phase0_pulo.py
# ---------------------------------------------------------------------------
@dataclass
class Entry:
    source: str
    term: str
    term_norm: str
    estatuto: str
    eixo: str = ""
    guarantee: list = field(default_factory=list)
    decisive_test: str = ""
    canon_ilis: frozenset = frozenset()
    raw_offsets: list = field(default_factory=list)
    unmapped_offsets: list = field(default_factory=list)
    resources: list = field(default_factory=list)
    reason: str = ""
    gloss: str = ""  # optional; gates weak(term) joins under gloss_gated mode


@dataclass
class Source:
    label: str
    class_id: str
    entries: list


def infer_label(path: Path) -> str:
    name = path.name.lower()
    low = str(path).lower()
    # OWN-PT before WordNet — filename contains both patterns otherwise.
    if "own-pt" in name or "ownpt" in name or ".own-pt." in name:
        return "OWN-PT"
    if "pulo" in low:
        return "PULO"
    if "onto" in low:
        return "ONTO"
    if "wordnet" in low or "oewn" in low:
        return "WordNet"
    stem = path.name
    for suffix in (".result.json", ".json"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return path.stem


def _offsets_to_canon(offsets: list) -> tuple[frozenset, list]:
    canon, unmapped = set(), []
    for off in offsets or []:
        key, mapped = canonical_ili(off)
        if mapped:
            canon.add(key)
        else:
            unmapped.append(off)
    return frozenset(canon), unmapped


def _pending_dict(data: dict) -> dict:
    """ONTO/PULO store un-adjudicated seeds under stage5.pending (name→info)."""
    st5 = data.get("stage5")
    if isinstance(st5, dict) and isinstance(st5.get("pending"), dict):
        return st5["pending"]
    return {}


def _detect_kind(data) -> str:
    """Best-effort label of what a loaded JSON actually is (for guidance)."""
    if not isinstance(data, dict):
        return "não-objecto"
    if any(k in data for k in ("provenance", "sinalizacao", "stage5", "assertions")):
        return "result"
    if "synsets" in data:
        return "export de tesauro"
    if "admitted_offsets" in data and "stage1_whitelist" not in data:
        return "whitelist"
    if "stage1_whitelist" in data:
        return "esqueleto" if data.get("_scaffold") else "spec"
    return "desconhecido"


def count_usable(data: dict) -> tuple[int, int, int]:
    """(admitted, signalled, pending) term counts a source would contribute."""
    prov = data.get("provenance") or []
    n_admit = sum(1 for p in prov if (p.get("termo") or p.get("term")))
    sina = data.get("sinalizacao") or {}
    n_signal = len(sina) if isinstance(sina, dict) else 0
    n_pending = len(_pending_dict(data))
    return n_admit, n_signal, n_pending


def find_result_sibling(path: Path, class_id: Optional[str] = None) -> Optional[Path]:
    """If `path` isn't a usable result.json, find a sibling one that IS."""
    folder = Path(path).parent
    if not folder.exists():
        return None
    cands = sorted(folder.glob("*.result.json"))
    if not cands:
        return None
    best = None
    for c in cands:
        try:
            d = json.loads(c.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if class_id and (d.get("class_id") or d.get("class")) != class_id:
            continue
        if sum(count_usable(d)) > 0:
            return c
        best = best or c
    return best or (cands[0] if cands else None)


def describe_source(path: Path) -> dict:
    """Non-raising probe: what is this file, is it usable, and if not, what to use.

    Returns keys: exists, ok, kind, error, class_id, n_admit, n_signal,
    n_pending, suggestion (a sibling *.result.json Path or None).
    """
    p = Path(path)
    base = {"exists": False, "ok": False, "kind": "em falta", "error": None,
            "class_id": None, "n_admit": 0, "n_signal": 0, "n_pending": 0,
            "suggestion": None}
    if not p.exists():
        base["error"] = "ficheiro não encontrado"
        return base
    base["exists"] = True
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        base["kind"] = "não-JSON"
        base["error"] = (f"não é JSON válido ({exc}). "
                         "Ficheiros .md/.png/.txt não servem.")
        base["suggestion"] = find_result_sibling(p)
        return base
    except OSError as exc:
        base["error"] = f"não foi possível ler ({exc})"
        return base
    base["ok"] = True
    base["kind"] = _detect_kind(data)
    base["class_id"] = data.get("class_id") or data.get("class")
    base["n_admit"], base["n_signal"], base["n_pending"] = count_usable(data)
    total = base["n_admit"] + base["n_signal"] + base["n_pending"]
    if base["kind"] != "result" or total == 0:
        sug = find_result_sibling(p, base["class_id"])
        if sug and sug.resolve() != p.resolve():
            base["suggestion"] = sug
    return base


def load_source(path: Path, label: Optional[str] = None) -> Source:
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SourceError(f"Ficheiro não encontrado:\n{p}")
    except json.JSONDecodeError as exc:
        raise SourceError(
            f"«{p.name}» não é um JSON válido ({exc}).\n"
            "Escolha o ficheiro «<classe>.result.json» gerado pelo motor Fase 0 "
            "(não .md, .png, .txt, .whitelist.json nem .skeleton.json).")
    except OSError as exc:
        raise SourceError(f"Não foi possível ler «{p.name}»: {exc}")

    class_id = data.get("class_id") or data.get("class") or "?"
    label = label or infer_label(p)
    entries: list[Entry] = []
    seen: set[str] = set()   # dedupe within a source (admit > signal > pending)

    for prov in data.get("provenance", []):
        term = prov.get("termo") or prov.get("term") or ""
        if not term:
            continue
        offsets = prov.get("offsets_ili") or prov.get("offsets") or []
        canon, unmapped = _offsets_to_canon(offsets)
        resources = []
        for r in prov.get("recursos_atestacao", []) or []:
            resources.append(f"{label}:{r}")
        for key in ("origem", "via"):
            if prov.get(key):
                resources.append(f"{label}:{prov[key]}")
        seen.add(norm_term(term))
        entries.append(Entry(
            source=label, term=term, term_norm=norm_term(term),
            estatuto=prov.get("estatuto", ""), eixo=prov.get("eixo", ""),
            guarantee=list(prov.get("garantia", []) or prov.get("guarantee", [])),
            decisive_test=prov.get("teste_decisivo", "") or prov.get("decisive_test", ""),
            canon_ilis=canon, raw_offsets=list(offsets), unmapped_offsets=unmapped,
            resources=resources,
            gloss=str(prov.get("gloss") or prov.get("definition") or ""),
        ))

    # OWN-PT attestation (entry warrant, never UF/RT)
    atest = data.get("atestacao", {})
    if isinstance(atest, dict):
        lex = data.get("lexicon") or ""
        for nw, s in atest.items():
            term = s.get("display", nw)
            tn = norm_term(term)
            if tn in seen:
                continue
            seen.add(tn)
            offsets = s.get("offsets_ili") or s.get("offsets") or []
            canon, unmapped = _offsets_to_canon(offsets)
            lex_s = s.get("lexicon") or lex
            resources = [f"{label}:atestado"]
            if lex_s:
                resources.append(f"{label}:lexicon={lex_s}")
            if s.get("reason"):
                resources.append(f"{label}:{s['reason']}")
            entries.append(Entry(
                source=label, term=term, term_norm=tn,
                estatuto=ATESTATO, reason=s.get("reason", ""),
                canon_ilis=canon, raw_offsets=list(offsets),
                unmapped_offsets=unmapped, resources=resources))

    # flagged senses (present in PULO as top-level `sinalizacao`)
    sina = data.get("sinalizacao", {})
    if isinstance(sina, dict):
        for nw, s in sina.items():
            term = s.get("display", nw)
            tn = norm_term(term)
            if tn in seen:
                continue
            seen.add(tn)
            # WordNet exports its signals ILI-anchored (`offsets_ili`); keep the ILI
            # so a signalled lemma can still line up interlingually, not only by term.
            offsets = s.get("offsets_ili") or s.get("offsets") or []
            canon, unmapped = _offsets_to_canon(offsets)
            entries.append(Entry(
                source=label, term=term, term_norm=tn,
                estatuto=SIGNAL, reason=s.get("reason", ""),
                canon_ilis=canon, raw_offsets=list(offsets), unmapped_offsets=unmapped,
                resources=[f"{label}:sinalização({s.get('reason','')})"],
                gloss=str(s.get("gloss") or s.get("definition") or ""),
            ))

    # un-adjudicated seeds (ONTO/PULO stage5.pending) — reported, never admitted.
    # Without this, a class where nothing was admitted yet (e.g. ONTO here) would
    # contribute zero rows and the whole report would look empty.
    for nw, s in _pending_dict(data).items():
        term = s.get("display", nw)
        tn = norm_term(term)
        if tn in seen:
            continue
        seen.add(tn)
        offsets = s.get("offsets") or []
        canon, unmapped = _offsets_to_canon(offsets)
        dec = s.get("decision_synset") or s.get("decision") or ""
        entries.append(Entry(
            source=label, term=term, term_norm=tn, estatuto=PENDING,
            reason=(f"pendente (sugestão: {dec})" if dec else "pendente de adjudicação"),
            canon_ilis=canon, raw_offsets=list(offsets), unmapped_offsets=unmapped,
            resources=[f"{label}:pendente"]))

    return Source(label, class_id, entries)


def assert_same_class(sources: list[Source]) -> str:
    classes = {s.class_id for s in sources}
    if len(classes) != 1:
        raise ClassMismatch(
            "Classes-alvo diferentes entre as fontes: "
            + ", ".join(f"{s.label}={s.class_id}" for s in sources))
    return next(iter(classes))


# ---------------------------------------------------------------------------
# Merge — ILI primary (confirmed), term secondary (weak); never silent
# ---------------------------------------------------------------------------
def _components(entries: list[Entry], key=None):
    """Connected components where two ILI-bearing entries link iff their ILI keys
    intersect. `key(entry)` yields the set of keys to compare — by default the raw
    canonical ILIs, but callers pass an equivalence-folded set so declared-equal
    ILIs across namespaces are treated as one concept."""
    if key is None:
        key = lambda e: e.canon_ilis  # noqa: E731
    parent = list(range(len(entries)))
    keys = [key(e) for e in entries]

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        parent[find(i)] = find(j)

    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            if keys[i] & keys[j]:
                union(i, j)
    groups = defaultdict(list)
    for i, e in enumerate(entries):
        groups[find(i)].append(e)
    return list(groups.values())


@dataclass
class Concept:
    term: str
    ilis: list
    sources: dict           # label -> estatuto
    join: str
    veredicto: str
    proposta_final: Optional[str]
    divergences: list
    union_of_provenance: list
    notes: list
    term_norm: str = ""
    ili_by_source: dict = field(default_factory=dict)  # label -> [canonical ILIs]
    unmapped_flag: bool = False   # True iff unmapped offsets blocked an ILI join
    status_projection: dict = field(default_factory=dict)  # label -> "rico→projectado"
    # Qualifier (not a verdict label): set when PULO↔OWN-PT ILI pair is PWN-derived.
    recursos_derivados: Optional[str] = None


def _pick_display(entries: list[Entry]) -> str:
    ili_bearing = [e for e in entries if e.canon_ilis]
    pool = ili_bearing or entries
    counts = Counter(e.term for e in pool)
    return counts.most_common(1)[0][0]


def build_concept(entries: list[Entry], join_kind: str, policy: str,
                  equiv: Optional[EquivMap] = None) -> Concept:
    # Pendente entries are treated as NOT-present (same as '—'); they never reach
    # here as a source status (build_concordance filters them) but guard anyway.
    statuses: dict[str, str] = {}
    for e in entries:
        if e.estatuto == PENDING:
            continue
        statuses.setdefault(e.source, e.estatuto)

    admit = {s: st for s, st in statuses.items() if st in ADMIT_STATUSES}
    signal = {s: st for s, st in statuses.items() if st == SIGNAL}
    atestado = {s: st for s, st in statuses.items() if st == ATESTATO}
    distinct = set(admit.values())

    # Projecção declarada no reticulado — alimenta SÓ a comparação do veredicto.
    # Os estatutos ricos originais (admit/statuses) seguem intactos para a saída.
    projections = {s: project_status_for_comparison(st) for s, st in admit.items()}
    comparable = {s: p for s, p in projections.items() if p is not None}
    if len(comparable) >= 2:
        proj_inter = frozenset.intersection(*comparable.values())
    else:
        proj_inter = None   # <2 fontes comparáveis (BT/NT neutros) → sem desacordo

    # registo de auditoria: onde a projecção difere do estatuto bruto
    status_projection = {
        s: f"{st}→" + ("neutro" if projections[s] is None
                       else "/".join(sorted(projections[s])))
        for s, st in admit.items()
        if projections[s] is None or projections[s] != frozenset({st})
    }

    # join label (computed first — the veredicto depends on it)
    n_sources = len(statuses)
    if join_kind == "ili":
        join = "ili" if n_sources >= 2 else "single"
    elif join_kind == "single":
        join = "single"
    else:
        join = "weak(term)" if n_sources >= 2 else "single"

    if not admit and (signal or atestado):
        veredicto = "sinalização"
    elif len(admit) >= 2 and (proj_inter is None or proj_inter):
        # «convergência plena» is the most defensible tier and REQUIRES a genuine
        # ILI join (equal or declared-equivalent). Multi-source agreement that
        # rests only on a term match is the weaker «convergência (termo)».
        veredicto = "convergência plena" if join == "ili" else "convergência (termo)"
    elif len(admit) >= 2:
        veredicto = "divergência de relação"
    elif len(admit) == 1:
        veredicto = "fonte única"
    else:
        veredicto = "sinalização"

    # Opção C: PULO admitido + OWN-PT atestado, junção ILI → convergência (sentido).
    # OWN-PT NÃO recebe estatuto admissivo; o qualificador PWN regista a distinção.
    pulo_ownpt_ili = (
        join == "ili"
        and "PULO" in admit
        and statuses.get("OWN-PT") == ATESTATO
    )
    if pulo_ownpt_ili and veredicto in ("fonte única", "sinalização"):
        veredicto = "convergência (sentido)"

    # proposta_final — a suggestion only; never auto-admission
    proposta: Optional[str] = None
    proposta_dual_note: Optional[str] = None
    if policy == "conservative":
        if veredicto in ("convergência plena", "convergência (termo)",
                         "convergência (sentido)"):
            if len(distinct) == 1:
                proposta = next(iter(distinct))
            elif distinct:
                cands = [st for st in admit.values()
                         if project_status_for_comparison(st) is not None
                         and (proj_inter is None
                              or project_status_for_comparison(st) & proj_inter)]
                cands.sort(key=lambda st: (len(project_status_for_comparison(st)), st))
                proposta = cands[0] if cands else next(iter(distinct))
        elif veredicto == "fonte única":
            proposta = next(iter(admit.values()))
        else:
            proposta = None
    else:  # informed
        if admit:
            cnt = Counter(admit.values())
            top, n = cnt.most_common(1)[0]
            ties = [k for k, v in cnt.items() if v == n]
            proposta = top if len(ties) == 1 else None
    # Guard: never propose evidence-only / atestado / legacy contraste.
    if (proposta in EVIDENCE_STATUSES or proposta == "contraste"
            or proposta == ATESTATO or proposta == SIGNAL):
        proposta = None

    divergences = []
    if veredicto == "divergência de relação":
        divergences = [{"source": s, "estatuto": st} for s, st in sorted(admit.items())]

    ilis = sorted({i for e in entries for i in e.canon_ilis})
    provenance = sorted({r for e in entries for r in e.resources})
    ili_by_source: dict[str, list] = {}
    for e in entries:
        if e.canon_ilis:
            ili_by_source.setdefault(e.source, set()).update(e.canon_ilis)
    ili_by_source = {s: sorted(v) for s, v in ili_by_source.items()}

    # Did the declared equivalence table enable this join? (raw ILI keys differ by
    # namespace but the map unified them.)
    via_table_pairs = []
    if equiv is not None and join == "ili":
        raw_keys = sorted({i for e in entries for i in e.canon_ilis})
        for a in raw_keys:
            for b in raw_keys:
                if a < b and equiv.linked(a, b):
                    via_table_pairs.append(f"{a} ↔ {b}")

    notes: list[str] = []
    # Emenda 2 — marca obrigatória em toda convergência ILI PULO↔OWN-PT.
    recursos_derivados: Optional[str] = None
    present = set(statuses)
    if join == "ili" and PWN_DERIVED_SOURCES <= present:
        recursos_derivados = "PWN"
        notes.append(f"recursos_derivados: PWN — {PWN_DERIVED_NOTE}")

    if join == "ili" and via_table_pairs:
        notes.append("junção por ILI via tabela de equivalência: "
                     + "; ".join(sorted(set(via_table_pairs))))
    if join == "weak(term)":
        if ilis:
            notes.append("junção por termo — as fontes não partilham um ILI comum "
                         "(fiabilidade menor)")
        else:
            notes.append("junção fraca por termo (sem ILI) — fiabilidade menor")
    if signal and admit:
        notes.append("sinalizado por " + ", ".join(sorted(signal)) +
                     " enquanto admitido por " + ", ".join(sorted(admit)))
    if atestado and admit and veredicto != "convergência (sentido)":
        notes.append("atestado por " + ", ".join(sorted(atestado)) +
                     " enquanto admitido por " + ", ".join(sorted(admit)))
    if status_projection:
        notes.append("projecção p/ comparação: "
                     + "; ".join(f"{s}: {p}" for s, p
                                 in sorted(status_projection.items())))
    if proposta_dual_note:
        notes.append(proposta_dual_note)
    unmapped = sorted({o for e in entries for o in e.unmapped_offsets})
    unmapped_flag = bool(unmapped) and join != "ili"
    if unmapped_flag:
        notes.append("namespace não-mapeada (não-juntável): " + ", ".join(unmapped))
    for e in entries:
        if e.estatuto in NONADMIT and e.reason:
            notes.append(f"{e.source}: {e.reason}")

    return Concept(term=_pick_display(entries), ilis=ilis, sources=statuses,
                   join=join, veredicto=veredicto, proposta_final=proposta,
                   divergences=divergences, union_of_provenance=provenance,
                   notes=notes,
                   term_norm=(entries[0].term_norm if entries else ""),
                   ili_by_source=ili_by_source, unmapped_flag=unmapped_flag,
                   status_projection=status_projection,
                   recursos_derivados=recursos_derivados)


def _gloss_jaccard(a: str, b: str) -> float:
    """Minimal content-token Jaccard (no external deps) for weak-join gating."""
    import re
    import unicodedata

    def toks(text: str) -> set[str]:
        if not text:
            return set()
        nfkd = unicodedata.normalize("NFKD", text)
        folded = "".join(c for c in nfkd if not unicodedata.combining(c)).casefold()
        stop = {
            "a", "o", "os", "as", "um", "uma", "de", "do", "da", "dos", "das",
            "e", "ou", "em", "no", "na", "the", "an", "of", "and", "or", "in",
            "on", "to", "for", "with", "that", "this", "is", "are", "be", "as",
        }
        return {
            t for t in re.findall(r"[a-z0-9]+", folded)
            if len(t) > 2 and t not in stop
        }

    ta, tb = toks(a), toks(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _weak_term_allowed(
    entries: list[Entry],
    *,
    weak_term_mode: str,
    gloss_min: float,
) -> bool:
    """Gate weak(term) merges to reduce polysemy false joins.

    Modes:
      * ``off`` — never weak-join across sources
      * ``gloss_gated`` (default) — require gloss Jaccard ≥ gloss_min between
        at least one pair of entries from different sources (both glosses non-empty)
      * ``legacy`` — always allow (old behaviour)
    """
    mode = (weak_term_mode or "gloss_gated").strip().lower()
    if mode in ("off", "none", "false", "0"):
        return False
    if mode in ("legacy", "always", "on"):
        return True
    # gloss_gated
    by_src: dict[str, list[Entry]] = defaultdict(list)
    for e in entries:
        by_src[e.source].append(e)
    sources = list(by_src)
    if len(sources) < 2:
        return False
    for i, sa in enumerate(sources):
        for sb in sources[i + 1 :]:
            for ea in by_src[sa]:
                for eb in by_src[sb]:
                    ga, gb = (ea.gloss or "").strip(), (eb.gloss or "").strip()
                    if not ga or not gb:
                        continue
                    if _gloss_jaccard(ga, gb) >= gloss_min:
                        return True
    return False


def _emit_singles(entries: list[Entry], policy: str, equiv: Optional[EquivMap],
                  concepts: list) -> None:
    """Emit one concept per source (no cross-source weak merge)."""
    by_src: dict[str, list[Entry]] = defaultdict(list)
    for e in entries:
        by_src[e.source].append(e)
    for group in by_src.values():
        kind = "ili" if any(e.canon_ilis for e in group) else "single"
        concepts.append(build_concept(group, kind, policy, equiv))


def build_concordance(sources: list[Source], policy: str,
                      equiv: Optional[EquivMap] = None,
                      *,
                      weak_term_mode: str = "gloss_gated",
                      gloss_min: float = 0.12) -> tuple[list[Concept], int]:
    """Returns (concepts, descartados_pendentes). Concepts supported ONLY by
    'pendente' statuses across every source are dropped and counted, never listed.

    ``weak_term_mode``: ``gloss_gated`` (default) | ``off`` | ``legacy``.
    """
    by_term: dict[str, list[Entry]] = defaultdict(list)
    for src in sources:
        for e in src.entries:
            by_term[e.term_norm].append(e)

    def folded(e: Entry) -> frozenset:
        if not equiv or equiv.empty or not e.canon_ilis:
            return e.canon_ilis
        return frozenset(equiv.rep(k) for k in e.canon_ilis)

    concepts: list[Concept] = []
    descartados_pendentes = 0
    for _term_norm, all_entries in by_term.items():
        # PENDING seeds are treated as not-present. A term that is ONLY pendente
        # (everywhere) is dropped into a count instead of flooding the matrix.
        entries = [e for e in all_entries if e.estatuto != PENDING]
        if not entries:
            descartados_pendentes += 1
            continue

        ili_entries = [e for e in entries if e.canon_ilis]
        noili_entries = [e for e in entries if not e.canon_ilis]

        # Components use equivalence-FOLDED keys, so oewn-ili:i… and ili-30-…
        # declared equal in the table merge into one interlingual concept.
        comps = _components(ili_entries, key=folded)
        multi_src = [c for c in comps if len({e.source for e in c}) >= 2]
        single_src = [c for c in comps if len({e.source for e in c}) < 2]
        for comp in multi_src:
            concepts.append(build_concept(comp, "ili", policy, equiv))

        leftover = [e for comp in single_src for e in comp] + noili_entries
        if leftover:
            if len({e.source for e in leftover}) >= 2:
                if _weak_term_allowed(
                    leftover, weak_term_mode=weak_term_mode, gloss_min=gloss_min
                ):
                    concepts.append(
                        build_concept(leftover, "weak(term)", policy, equiv)
                    )
                else:
                    _emit_singles(leftover, policy, equiv, concepts)
            else:
                for comp in single_src:
                    concepts.append(build_concept(comp, "ili", policy, equiv))
                if noili_entries:
                    if len({e.source for e in noili_entries}) >= 2:
                        if _weak_term_allowed(
                            noili_entries,
                            weak_term_mode=weak_term_mode,
                            gloss_min=gloss_min,
                        ):
                            concepts.append(
                                build_concept(noili_entries, "weak(term)", policy, equiv)
                            )
                        else:
                            _emit_singles(noili_entries, policy, equiv, concepts)
                    else:
                        concepts.append(
                            build_concept(noili_entries, "weak(term)", policy, equiv)
                        )

    concepts.sort(key=lambda c: (c.veredicto, c.term.casefold()))
    return concepts, descartados_pendentes


# ---------------------------------------------------------------------------
# ASSERT harness (T1–T9) — CLI exits non-zero on any failure
# ---------------------------------------------------------------------------
@dataclass
class Assertion:
    id: str
    text: str
    passed: bool
    evidence: str = ""


def run_asserts(concepts, sources, source_labels, policy, raw_entries,
                json_path: Path) -> list[Assertion]:
    A: list[Assertion] = []

    def add(i, text, ok, ev=""):
        A.append(Assertion(i, text, bool(ok), ev))

    # T1 — no two ILI-bearing entries merged by term alone (ILI-join precedence).
    # By construction, ILI concepts are formed only via ILI-set intersection, so a
    # multi-source ILI concept must carry a shared ILI thread. Flag any that don't.
    bad_t1 = []
    for c in concepts:
        if c.join == "ili" and len(c.sources) >= 2 and not c.ilis:
            bad_t1.append(c.term)
    add("T1", "Nenhuma junção por termo quando ambos têm ILI (ILI tem precedência).",
        not bad_t1, "OK" if not bad_t1 else f"suspeitos: {bad_t1}")

    # T2 — a weak(term) join happens only when sources do NOT share an ILI.
    # (Weak concepts may list per-source ILIs, but none may be common to ≥2
    # sources — otherwise ILI-join precedence would have applied.)
    def _cross_source_shared_ili(c):
        cnt = Counter()
        for _src, ilis in c.ili_by_source.items():
            for i in set(ilis):
                cnt[i] += 1
        return [i for i, v in cnt.items() if v >= 2]
    weak = [c for c in concepts if c.join == "weak(term)"]
    bad_weak = [c.term for c in weak if _cross_source_shared_ili(c)]
    add("T2", "Junção weak(term) só ocorre sem ILI partilhado entre fontes "
        "(caso contrário aplicar-se-ia a junção por ILI).",
        not bad_weak,
        f"{len(weak)} conceito(s) weak(term)" if not bad_weak
        else f"ILI partilhado indevidamente: {bad_weak}")

    # T3 — no fabricated ILI; unmapped flagged not force-joined
    fake = canonical_ili("zzz-99-12345678-a")
    unmapped_flagged = any("namespace não-mapeada" in n for c in concepts for n in c.notes)
    all_offsets = {o for e in raw_entries for o in e.raw_offsets}
    mapped_universe = {canonical_ili(o)[0] for o in all_offsets if canonical_ili(o)[1]}
    no_invention = all(i in mapped_universe for c in concepts for i in c.ilis)
    add("T3", "Nenhum ILI é fabricado; junção OEWN↔PULO só via CILI; "
        "pares sem âncora CILI ficam sem junção ILI (não fabricados).",
        fake == (None, False) and no_invention,
        f"bogus→{fake}; unmapped_flag={unmapped_flagged}")

    # T4 — every divergence recorded per-source (no collapse to a count)
    div = [c for c in concepts if c.veredicto == "divergência de relação"]
    t4 = all(
        c.divergences
        and len(c.divergences) == len({s for s, st in c.sources.items()
                                       if st in ADMIT_STATUSES})
        for c in div
    ) if div else True
    add("T4", "Cada divergência de estatuto é registada por-fonte (sem colapso em contagem).",
        t4, f"{len(div)} divergência(s)")

    # T5 — every motor admit appears in the matrix (Onto fora da admissão).
    # OWN-PT atestado / junção ILI podem mudar o veredicto sem ser «fonte única».
    admit_pairs_in = {(e.source, e.term_norm) for e in raw_entries
                      if e.estatuto in ADMIT_STATUSES}
    admit_pairs_out = {(s, c.term_norm) for c in concepts
                       for s, st in c.sources.items() if st in ADMIT_STATUSES}
    missing = admit_pairs_in - admit_pairs_out
    n_admit = len(admit_pairs_in)
    n_matrix_admit = len(admit_pairs_out)
    t5_ok = not missing
    add(
        "T5",
        "Nenhum termo admitido pelos motores é descartado da matriz "
        "(PULO; OWN-PT/WordNet corroboram; Onto = descoberta)",
        t5_ok,
        (
            f"{n_admit} admitidos / {n_matrix_admit} em matriz"
            if t5_ok
            else f"em falta={sorted(missing)}"
        ),
    )

    # T6 — absent WordNet ⇒ column all '—'
    if "WordNet" not in source_labels:
        t6 = all("WordNet" not in c.sources for c in concepts)
        add("T6", "Fonte WordNet ausente ⇒ coluna toda «—»; execução continua (exit 0).",
            t6, "coluna WordNet ausente e uniformemente «—»")
    else:
        add("T6", "Fonte WordNet ausente ⇒ coluna toda «—».", True,
            "WordNet presente — N/A")

    # T7 — proposta_final never a status the sources didn't support; conservative ⇒ null on divergence
    t7_bad = []
    for c in concepts:
        present = set(c.sources.values())
        if c.proposta_final is not None and c.proposta_final not in present:
            t7_bad.append((c.term, c.proposta_final))
        if policy == "conservative" and c.veredicto == "divergência de relação" \
                and c.proposta_final is not None:
            t7_bad.append((c.term, "divergência!=null"))
    add("T7", "proposta_final nunca é um estatuto não suportado; conservador ⇒ null em divergência.",
        not t7_bad, "OK" if not t7_bad else f"violações: {t7_bad}")

    # T8 — mixed-class inputs refused
    try:
        assert_same_class([Source("A", "X", []), Source("B", "Y", [])])
        t8 = False
    except ClassMismatch:
        t8 = True
    add("T8", "Entradas de classes diferentes são recusadas com erro claro.", t8,
        "ClassMismatch levantada para classes mistas")

    # T10 — ILI-tier verdicts require an ILI join (equal or table-declared).
    t10_bad = [c.term for c in concepts
               if c.veredicto in ("convergência plena", "convergência (sentido)")
               and c.join != "ili"]
    add("T10", "«Convergência plena» / «convergência (sentido)» exigem junção "
        "por ILI (nunca só weak(term)).",
        not t10_bad, "OK" if not t10_bad else f"violações: {t10_bad}")

    # T10b — PULO↔OWN-PT ILI pairs always carry recursos_derivados:PWN.
    t10b_bad = [
        c.term for c in concepts
        if c.join == "ili"
        and PWN_DERIVED_SOURCES <= set(c.sources)
        and c.recursos_derivados != "PWN"
    ]
    add("T10b", "Convergência ILI PULO↔OWN-PT marca sempre "
        "recursos_derivados:«PWN».",
        not t10b_bad, "OK" if not t10b_bad else f"sem marca: {t10b_bad}")

    # T11 — no pendente-only concept survives as a matrix row (they're counted).
    t11_bad = [c.term for c in concepts if not c.sources]
    add("T11", "Nenhum conceito só-pendente figura como linha da matriz "
        "(são contados em «descartados_pendentes»).",
        not t11_bad, "OK" if not t11_bad else f"linhas vazias: {t11_bad}")

    # T9 — concordance.json round-trips
    try:
        reparsed = json.loads(Path(json_path).read_text(encoding="utf-8"))
        terms_a = sorted(c.term for c in concepts)
        terms_b = sorted(c["term"] for c in reparsed["concepts"])
        ilis_a = sorted(i for c in concepts for i in c.ilis)
        ilis_b = sorted(i for c in reparsed["concepts"] for i in c["ili"])
        t9 = (terms_a == terms_b and ilis_a == ilis_b)
    except Exception as exc:  # noqa: BLE001
        t9 = False
        add("T9", "concordance.json faz round-trip.", False, f"erro: {exc}")
        return A
    add("T9", "concordance.json faz round-trip (contagens de term/ili estáveis).",
        t9, f"{len(concepts)} conceitos")

    # T13 (light) — matrix must not retain legacy «contraste» cells / proposals.
    # Full migration check (decisions.json) lives in unit tests, not here.
    t13_hits = []
    for c in concepts:
        for src, st in c.sources.items():
            if st == "contraste":
                t13_hits.append(f"{c.term}/{src}")
        if c.proposta_final == "contraste":
            t13_hits.append(f"{c.term}/proposta_final")
    add("T13",
        "Nenhuma célula nem proposta_final com valor «contraste» na matriz "
        "(migração completa: ver teste unitário de decisions).",
        not t13_hits,
        "OK" if not t13_hits else f"resíduos: {t13_hits}")
    return A


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------
def concept_to_json(c: Concept) -> dict:
    extra_cols = sorted(set(c.sources) - set(SOURCE_COLUMNS))
    out = {
        "term": c.term,
        "ili": c.ilis,
        "sources": {col: c.sources.get(col, ABSENT)
                    for col in SOURCE_COLUMNS + extra_cols},
        "join": c.join,
        "veredicto": c.veredicto,
        "proposta_final": c.proposta_final,
        "unmapped_flag": c.unmapped_flag,
        "status_projection": c.status_projection,
        "divergences": c.divergences,
        "union_of_provenance": c.union_of_provenance,
        "notes": c.notes,
    }
    if c.recursos_derivados:
        out["recursos_derivados"] = c.recursos_derivados
    return out


_ANTONYM_REASON_RE = re.compile(r"material de contraste\s*\(antonym\)", re.I)
# Sources known not to expose a consultable antonymy relation for harvest.
_NO_ANTONYMY_SOURCES = frozenset({"ONTO", "PULO"})


def summarize_auto_contrast(sources: list[Source]) -> dict:
    """R6 — coverage of automatic antonym harvest (read-only; no collection change)."""
    per_source: dict[str, dict] = {}
    anchored_with_contrast: set[str] = set()
    anchored_ilis: set[str] = set()

    for src in sources:
        ants = [
            e for e in src.entries
            if e.estatuto == SIGNAL and _ANTONYM_REASON_RE.search(e.reason or "")
        ]
        exposes = src.label not in _NO_ANTONYMY_SOURCES
        per_source[src.label] = {
            "antonyms_auto": len(ants),
            "exposes_antonymy": exposes,
            "note": (
                "antonímia consultável (OEWN)" if exposes
                else "fonte sem antonímia consultável (esperado)"
            ),
            "terms": sorted({e.term for e in ants}),
        }
        for e in ants:
            for ili in e.canon_ilis:
                anchored_with_contrast.add(ili)
            # also parse «de iNNNN» from reason when offsets empty
            m = re.search(r"\b(i\d+)\b", e.reason or "")
            if m:
                anchored_with_contrast.add(f"oewn-ili:{m.group(1)}")

        for e in src.entries:
            if e.estatuto in ADMIT_STATUSES:
                anchored_ilis.update(e.canon_ilis)

    missing = sorted(anchored_ilis - anchored_with_contrast)
    return {
        "per_source": per_source,
        "anchored_ilis_total": len(anchored_ilis),
        "anchored_ilis_with_auto_contrast": sorted(anchored_with_contrast),
        "anchored_ilis_without_auto_contrast": missing,
        "sources_without_antonymy": sorted(
            s for s in per_source if not per_source[s]["exposes_antonymy"]
        ),
    }


def render_json(class_id, policy, source_labels, concepts, assertions,
                descartados_pendentes: int = 0, map_path: Optional[str] = None,
                equiv: Optional["EquivMap"] = None,
                auto_contrast: Optional[dict] = None) -> dict:
    totals = Counter(c.veredicto for c in concepts)
    equiv_counts = ({"mapped": equiv.n_map, "review": equiv.n_review,
                     "unmatched": equiv.n_unmatched} if equiv is not None
                    else {"mapped": 0, "review": 0, "unmatched": 0})
    return {
        "class": class_id,
        "policy": policy,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "columns": SOURCE_COLUMNS,
        "sources": source_labels,
        "ili_equivalence_map": map_path,
        "ili_equivalence_counts": equiv_counts,
        "ili_equivalence_loaded": bool(equiv is not None and equiv.n_map > 0),
        "concepts": [concept_to_json(c) for c in concepts],
        "summary": {
            "veredicto_totals": dict(totals),
            "descartados_pendentes": descartados_pendentes,
            "convergencia_plena": sorted(c.term for c in concepts
                                         if c.veredicto == "convergência plena"),
            "convergencia_sentido": sorted(c.term for c in concepts
                                           if c.veredicto == "convergência (sentido)"),
            "convergencia_termo": sorted(c.term for c in concepts
                                         if c.veredicto == "convergência (termo)"),
            "divergences": [{"term": c.term, "sources": c.sources}
                            for c in concepts if c.veredicto == "divergência de relação"],
            "fonte_unica": sorted(c.term for c in concepts
                                  if c.veredicto == "fonte única"),
            "auto_contrast_coverage": auto_contrast or {},
        },
        "assertions": [a.__dict__ for a in assertions],
        "all_passed": all(a.passed for a in assertions),
    }


def render_markdown(doc: dict, concepts) -> str:
    L, ap = [], lambda s: L.append(s)
    passed = sum(1 for a in doc["assertions"] if a["passed"])
    total = len(doc["assertions"])
    ap(f"# LexWarrant — concordância cruzada (**{doc['class']}**)")
    ap("")
    ap(f"- **Política de divergência:** {doc['policy']}")
    ap(f"- **Fontes:** {', '.join(doc['sources']) or '—'}  (colunas: "
       f"{', '.join(doc['columns'])})")
    mp = doc.get("ili_equivalence_map")
    ec = doc.get("ili_equivalence_counts") or {}
    if doc.get("ili_equivalence_loaded"):
        src = mp or "CILI"
        ap(f"- **Junção ILI (CILI automático):** {src}  "
           f"({ec.get('mapped', 0)} pares CILI; "
           f"{ec.get('unmatched', 0)} sem âncora partilhada)")
    else:
        ap("- **Junção ILI (CILI):** ⚠ sem pares — junções OEWN↔PULO por ILI "
           "indisponíveis; só weak(term).")
    ap(f"- **Gerado:** {doc['generated']}")
    ap(f"- **Descartados (só pendentes):** "
       f"{doc['summary'].get('descartados_pendentes', 0)} "
       "(termos ainda por adjudicar; contados, não listados)")
    ap(f"- **Asserções:** {passed}/{total} PASS "
       + ("✅" if doc["all_passed"] else "❌"))
    ap("")
    ap("> Esta etapa **relata**; não admite nem reclassifica. `proposta_final` é "
       "uma sugestão para adjudicação humana, nunca uma auto-admissão.")
    ap("")

    ap("## Matriz de concordância")
    ap("")
    cols = doc["columns"]
    header = "| termo | ili | " + " | ".join(cols) + " | join | veredicto | proposta | notas |"
    sep = "|" + "---|" * (len(cols) + 6)
    ap(header)
    ap(sep)
    for c in concepts:
        cells = [c.sources.get(col, ABSENT) for col in cols]
        cell_disp = []
        for v in cells:
            if v == SIGNAL:
                cell_disp.append("sinalização")
            elif v == ATESTATO:
                cell_disp.append("atestado")
            else:
                cell_disp.append(v)
        ili = ", ".join(c.ilis) or ABSENT
        notes = "; ".join(c.notes).replace("|", "\\|") or ""
        prop = c.proposta_final or "—"
        verd = c.veredicto
        if c.recursos_derivados:
            verd = f"{verd} 〔recursos_derivados:{c.recursos_derivados}〕"
        ap(f"| {c.term} | {ili} | " + " | ".join(cell_disp)
           + f" | {c.join} | {verd} | {prop} | {notes} |")
    ap("")

    ap("## Resumo por veredicto")
    ap("")
    for k, v in sorted(doc["summary"]["veredicto_totals"].items()):
        ap(f"- **{k}:** {v}")
    ap("")

    cov = doc["summary"].get("auto_contrast_coverage") or {}
    ap("## Cobertura da recolha automática de contraste (R6)")
    ap("")
    ap("_Verificação apenas — a lógica de recolha não é alterada nesta etapa._")
    ap("")
    if cov:
        for src, info in sorted((cov.get("per_source") or {}).items()):
            ap(f"- **{src}:** {info.get('antonyms_auto', 0)} antónimo(s) auto "
               f"— {info.get('note', '')}")
            terms = info.get("terms") or []
            if terms:
                ap(f"  - termos: {', '.join(terms)}")
        missing = cov.get("anchored_ilis_without_auto_contrast") or []
        ap(f"- **ILIs ancorados (admitidos) sem material de contraste auto:** "
           f"{', '.join(missing) if missing else '—(nenhum ou sem âncoras)'}")
        no_ant = cov.get("sources_without_antonymy") or []
        ap(f"- **Fontes sem antonímia consultável (esperado):** "
           f"{', '.join(no_ant) if no_ant else '—'}")
    else:
        ap("_(sumário indisponível)_")
    ap("")

    ap("## Conjunto mais defensável — «convergência plena» (requer junção por ILI)")
    conv = doc["summary"]["convergencia_plena"]
    ap(", ".join(conv) if conv else "_(nenhum — nenhuma convergência ancorada em ILI)_")
    ap("")

    cs = doc["summary"].get("convergencia_sentido", [])
    ap("## Convergência (sentido) — PULO admitido + OWN-PT atestado (ILI partilhado)")
    ap("_Sem estatuto simulado no OWN-PT. Pares PULO↔OWN-PT: "
       "`recursos_derivados: PWN`._")
    ap(", ".join(cs) if cs else "_(nenhum)_")
    ap("")

    ct = doc["summary"].get("convergencia_termo", [])
    ap("## Convergência por termo (acordo de ≥2 fontes, mas sem ILI comum)")
    ap(", ".join(ct) if ct else "_(nenhum)_")
    ap("")

    ap("## Lista de trabalho humano — divergências")
    div = doc["summary"]["divergences"]
    if div:
        ap("| termo | " + " | ".join(cols) + " |")
        ap("|" + "---|" * (len(cols) + 1))
        for d in div:
            row = [d["sources"].get(col, ABSENT) for col in cols]
            row = [("sinalização" if v == SIGNAL else v) for v in row]
            ap(f"| {d['term']} | " + " | ".join(row) + " |")
    else:
        ap("_(nenhuma divergência)_")
    ap("")

    fu = doc["summary"]["fonte_unica"]
    ap("## Fonte única (aguarda segunda fonte)")
    ap(", ".join(fu) if fu else "_(nenhum)_")
    ap("")

    ap("## Asserções")
    ap("")
    ap("| # | Asserção | Resultado | Evidência |")
    ap("|---|----------|-----------|-----------|")
    for a in doc["assertions"]:
        mark = "PASS ✅" if a["passed"] else "FAIL ❌"
        ev = (a["evidence"] or "").replace("|", "\\|")
        ap(f"| {a['id']} | {a['text']} | {mark} | {ev} |")
    ap("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# API + CLI
# ---------------------------------------------------------------------------
def _discover_map(input_specs, outdir: Path) -> Optional[Path]:
    """Find an ili_equivalence.json next to the sources, outdir, or class root."""
    seen = []
    for _label, path in input_specs:
        seen.append(Path(path).parent)
    seen.append(Path(outdir))
    # class root (parent of out/ or results/) — common place people drop the file
    try:
        seen.append(Path(outdir).parent)
    except Exception:  # noqa: BLE001
        pass
    for folder in seen:
        folder = Path(folder)
        cand = folder / "ili_equivalence.json"
        if cand.exists():
            return cand
        if folder.exists():
            hits = sorted(folder.glob("*ili_equivalence*.json"))
            if hits:
                return hits[0]
    return None


def _report_equiv_load(equiv: Optional["EquivMap"], map_path: Optional[Path]) -> None:
    """Make the equivalence-table load VISIBLE at run time (never silent).

    Prints the ili_equivalence counts so it is provable the table was ingested,
    and a LOUD warning when there is nothing to join by (absent or 0 mapped) — so
    weak(term) fallback is never mistaken for the normal, healthy path."""
    if equiv is not None and equiv.n_map > 0:
        print(f"ili_equivalence: {equiv.n_map} mapped, {equiv.n_review} review, "
              f"{equiv.n_unmatched} unmatched  (tabela: {equiv.source_path})")
        return
    print("=" * 72)
    print("AVISO: TABELA DE EQUIVALENCIA NAO CARREGADA (0 pares ILI utilizaveis).")
    if map_path is None:
        print("   Nenhum ili_equivalence.json encontrado junto as fontes/saida.")
    elif equiv is None:
        print(f"   Ficheiro nao encontrado: {map_path}")
    else:
        print(f"   {map_path}: {equiv.n_map} mapped, {equiv.n_review} review, "
              f"{equiv.n_unmatched} unmatched.")
        print("   Ha 0 pares de ALTA confianca — as juncoes OEWN<->PULO por ILI NAO "
              "estao disponiveis.")
    print("   As fontes so poderao juntar-se por TERMO (weak) — fiabilidade menor.")
    print("=" * 72)


def run_report(input_specs: list[tuple[Optional[str], Path]], outdir: Path,
               policy: str = "conservative",
               map_path: Optional[Path] = None,
               equiv: Optional["EquivMap"] = None,
               weak_term_mode: str = "gloss_gated",
               gloss_min: float = 0.12) -> dict:
    sources = [load_source(path, label) for label, path in input_specs]
    if len(sources) < 2:
        raise ValueError("São necessárias pelo menos 2 fontes (result.json).")
    class_id = assert_same_class(sources)
    source_labels = [s.label for s in sources]
    raw_entries = [e for s in sources for e in s.entries]

    if equiv is None:
        if map_path is None:
            map_path = _discover_map(input_specs, outdir)
        equiv = EquivMap.load(map_path) if map_path and Path(map_path).exists() else None
    elif map_path is None and getattr(equiv, "source_path", None):
        map_path = Path(equiv.source_path)
    _report_equiv_load(equiv, Path(map_path) if map_path else None)

    concepts, descartados_pendentes = build_concordance(
        sources, policy, equiv,
        weak_term_mode=weak_term_mode, gloss_min=gloss_min,
    )
    auto_contrast = summarize_auto_contrast(sources)

    outdir.mkdir(parents=True, exist_ok=True)
    json_path = outdir / f"{class_id}.concordance.json"
    md_path = outdir / f"{class_id}.concordance.md"

    # write JSON first (T9 re-parses it), then run asserts, then rewrite with asserts.
    doc = render_json(class_id, policy, source_labels, concepts, assertions=[],
                      descartados_pendentes=descartados_pendentes,
                      map_path=str(map_path) if map_path else None, equiv=equiv,
                      auto_contrast=auto_contrast)
    json_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    assertions = run_asserts(concepts, sources, source_labels, policy,
                             raw_entries, json_path)
    doc = render_json(class_id, policy, source_labels, concepts, assertions,
                      descartados_pendentes=descartados_pendentes,
                      map_path=str(map_path) if map_path else None, equiv=equiv,
                      auto_contrast=auto_contrast)
    json_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(doc, concepts), encoding="utf-8")

    doc["_md_path"] = str(md_path)
    doc["_json_path"] = str(json_path)
    doc["_concepts"] = concepts
    return doc


def _parse_source_arg(value: str) -> tuple[str, Path]:
    if "=" in value:
        label, path = value.split("=", 1)
        return label.strip(), Path(path.strip())
    return (None, Path(value))  # type: ignore[return-value]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="LexWarrant — relator de concordância ILI.")
    ap.add_argument("inputs", nargs="*", help="ficheiros result.json (rótulo inferido)")
    ap.add_argument("--source", action="append", default=[],
                    help="ROTULO=ficheiro.json (rótulo explícito; repetível)")
    ap.add_argument("--policy", choices=["conservative", "informed"],
                    default="conservative", help="política de divergência (predef.: conservative)")
    ap.add_argument("--map", dest="map_path", default=None,
                    help="ili_equivalence.json (tabela OEWN↔PULO; auto-detetada se omitida)")
    ap.add_argument("--outdir", default=".", help="pasta de saída")
    args = ap.parse_args()

    specs: list[tuple[Optional[str], Path]] = []
    for value in args.source:
        specs.append(_parse_source_arg(value))
    for value in args.inputs:
        specs.append((None, Path(value)))

    if len(specs) < 2:
        print("ERRO: forneça ≥2 result.json (posicionais ou via --source ROTULO=ficheiro).")
        return 2

    try:
        doc = run_report(specs, Path(args.outdir), policy=args.policy,
                         map_path=Path(args.map_path) if args.map_path else None)
    except ClassMismatch as exc:
        print(f"ERRO (classes mistas): {exc}")
        return 3
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERRO: {exc}")
        return 2

    passed = sum(1 for a in doc["assertions"] if a["passed"])
    total = len(doc["assertions"])
    print(f"Matriz:   {doc['_md_path']}")
    print(f"JSON:     {doc['_json_path']}")
    print(f"Classe:   {doc['class']}  ·  política: {doc['policy']}  ·  "
          f"fontes: {', '.join(doc['sources'])}")
    print("Veredictos: " + ", ".join(f"{k}={v}"
          for k, v in sorted(doc["summary"]["veredicto_totals"].items())))
    print(f"Descartados (só pendentes): {doc['summary'].get('descartados_pendentes', 0)}")
    print(f"Tabela ILI: {doc.get('ili_equivalence_map') or '— (nenhuma)'}")
    print(f"Asserções: {passed}/{total} PASS "
          + ("— TODAS PASSARAM" if doc["all_passed"] else "— EXISTEM FALHAS"))
    for a in doc["assertions"]:
        print(("  [PASS] " if a["passed"] else "  [FAIL] ") + f"{a['id']}: {a['text']}")
    return 0 if doc["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
