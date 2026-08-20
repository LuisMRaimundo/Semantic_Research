"""PASSO 7 — TERMOS_PESQUISA.md/.csv + TERMOS.html (regras R1–R7).

Listas de pesquisa (A–D) em ``search_lang``; vocabulário de rótulos (F) em
``label_lang``. Sem hardcodes de classe, termo ou identificador.
"""

from __future__ import annotations

import csv
import html
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .export_blocks import _collect_auto_signals, _ili_anchor
from .mapping_policy import resolve_to_cili
from .normalize import fold, normalize_word
from . import settings as _settings
from .settings import load_config, resolve_languages
from .termos_focus import (
    corpus_near_stem as _corpus_near_stem,
    focus_morph_roots as _focus_morph_roots,
    search_syntax_line as _search_syntax_line,
    text_related_to_focus as _text_related_to_focus,
    wildcard as _wildcard,
)
from .workspace import ClassWorkspace

ADMIT_STATUSES = frozenset({"UF", "RT", "BT", "NT"})
HTML_MAX_BYTES = 100_000

_POLO_TO_SECTION = {
    "alvo": "A",
    "contrastante": "B",
    "controlo": "C",
    "adjacente": "D",
}

# Internal / ontology-class identifiers (CamelCase compound), not lexical forms.
_OWL_CLASS_RE = re.compile(r"^[A-Z][A-Za-z0-9]*(?:[A-Z][A-Za-z0-9]*)+$")
_POS_FROM_ILI = re.compile(r"-([anvr])(?:$|[^a-z])", re.I)
_TEX_CURIE_RE = re.compile(r"^tex:", re.I)


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------
def _is_registry_designation(name: str) -> bool:
    """R3(a): ontology class designations are never lexical candidates."""
    s = (name or "").strip()
    if not s:
        return False
    if _TEX_CURIE_RE.match(s):
        return True
    if " " in s:
        return False
    return bool(_OWL_CLASS_RE.match(s))


def _quote_copy_token(form: str) -> str:
    s = (form or "").strip()
    if not s:
        return ""
    if any(ch.isspace() for ch in s) or '"' in s:
        return '"' + s.replace('"', '\\"') + '"'
    return s


def _copy_payload(forms: list[str]) -> str:
    bits: list[str] = []
    seen: set[str] = set()
    for f in forms:
        tok = _quote_copy_token(f)
        if not tok:
            continue
        key = fold(f)
        if key in seen:
            continue
        seen.add(key)
        bits.append(tok)
    return " ".join(bits)


def _lang_matches(entry_lang: str, wanted: str) -> bool:
    a = (entry_lang or "").strip().lower().replace("_", "-")
    b = (wanted or "").strip().lower().replace("_", "-")
    if not a or not b:
        return True
    return a == b or a.split("-", 1)[0] == b.split("-", 1)[0]


def _pos_from_identifier(ident: str) -> Optional[str]:
    """R4: category from ILI / offset suffix (-a/-n/-v/-r)."""
    s = (ident or "").strip().lower()
    m = _POS_FROM_ILI.search(s)
    if m:
        return m.group(1).lower()
    # bare CILI id has no POS — unknown
    return None


# ---------------------------------------------------------------------------
# Class registry (R3)
# ---------------------------------------------------------------------------
def build_class_registry(
    classes_dir: Optional[Path] = None,
) -> dict[str, dict[str, Any]]:
    """Map class_id → labels / stipulated terms / designations."""
    root = Path(classes_dir) if classes_dir else _settings.CLASSES_DIR
    registry: dict[str, dict[str, Any]] = {}
    if not root.exists():
        return registry
    for meta_path in sorted(root.glob("*/class.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        cid = meta.get("class_id") or meta_path.parent.name
        designations = {cid}
        for k in (meta.get("disjoint_classes") or {}):
            designations.add(str(k))
        if meta.get("superclass"):
            designations.add(str(meta["superclass"]))
        # R3(b): preferred / stipulated labels only — NEVER synset member dumps.
        labels: set[str] = set()
        stipulated: set[str] = set()
        pref = (meta.get("pref_label") or "").strip()
        if pref and not _is_registry_designation(pref):
            labels.add(normalize_word(pref))
        dec_path = meta_path.parent / "decisions.json"
        if dec_path.exists():
            try:
                dec = json.loads(dec_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                dec = {}
            for t in dec.get("terms") or []:
                term = (t.get("term") or "").strip()
                if not term or _is_registry_designation(term):
                    continue
                st = (t.get("status") or "").strip()
                if st in ADMIT_STATUSES:
                    labels.add(normalize_word(term))
                if t.get("definition") or t.get("structural"):
                    stipulated.add(normalize_word(term))
            for m in dec.get("manual_terms") or []:
                term = (m.get("term") or "").strip()
                if not term or _is_registry_designation(term):
                    continue
                if m.get("definition") or m.get("structural"):
                    stipulated.add(normalize_word(term))
                if (m.get("status") or "").strip() in ADMIT_STATUSES:
                    labels.add(normalize_word(term))
        registry[cid] = {
            "class_id": cid,
            "pref_label": pref,
            "designations": {fold(d) for d in designations if d},
            "labels": labels,
            "stipulated": stipulated,
            "meta": meta,
        }
    return registry


def _soft_belongs_to_other_class(
    term: str, this_class: str, registry: dict[str, dict[str, Any]]
) -> Optional[str]:
    """R3(b): term is preferred/variant/stipulated (or soft id match) of another class."""
    tn = normalize_word(term)
    if not tn:
        return None
    this_f = fold(this_class)
    for cid, info in registry.items():
        if fold(cid) == this_f:
            continue
        if tn in info.get("labels") or tn in info.get("stipulated"):
            return cid
        # Soft: lexical stem contained in another class_id (e.g. politípica ⊂ …Politpica)
        cid_f = fold(cid)
        if len(tn) >= 4 and tn in cid_f:
            return cid
    return None


def _structural_other_class(
    term: str, dec: dict[str, Any], this_class: str, registry: dict[str, dict[str, Any]]
) -> Optional[str]:
    tn = normalize_word(term)
    this_f = fold(this_class)
    for m in dec.get("manual_terms") or []:
        if normalize_word(m.get("term") or "") != tn:
            continue
        structural = (m.get("structural") or "").strip()
        if not structural:
            continue
        sf = fold(structural)
        if sf == this_f:
            continue
        if sf in {fold(c) for c in registry} or _is_registry_designation(structural):
            return structural
    for t in dec.get("terms") or []:
        if normalize_word(t.get("term") or "") != tn:
            continue
        structural = (t.get("structural") or "").strip()
        if structural and fold(structural) != this_f:
            return structural
    return None


# ---------------------------------------------------------------------------
# Concordance / EN equivalents / manuals
# ---------------------------------------------------------------------------
def _load_concordance(ws: ClassWorkspace) -> Optional[dict[str, Any]]:
    path = ws.concordance_json()
    if not path.exists():
        alt = ws.out / f"{ws.class_id}.concordance.json"
        path = alt if alt.exists() else path
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def admitted_matrix_rows(
    concordance: Optional[dict[str, Any]],
    *,
    excluded_cilis: Optional[set[str]] = None,
) -> list[dict[str, Any]]:
    if not concordance:
        return []
    from .mapping_policy import cili_ids_from_matrix_row

    excl = excluded_cilis or set()
    out: list[dict[str, Any]] = []
    for c in concordance.get("concepts") or []:
        if (c.get("proposta_final") or "").strip() not in ADMIT_STATUSES:
            continue
        if excl and (cili_ids_from_matrix_row(c) & excl):
            continue
        notes = " ".join(c.get("notes") or [])
        if "excluded_cili:" in notes:
            continue
        out.append(c)
    return out


def _garantia_label(veredicto: str) -> str:
    v = (veredicto or "").lower()
    if "converg" in v:
        return "convergencia"
    if "fonte" in v and "nica" in v.replace("ú", "u"):
        return "fonte_unica"
    if "diverg" in v:
        return "divergencia"
    if "sinal" in v:
        return "sinalizacao"
    return "fonte_unica"


def _fontes_activas(sources: dict[str, Any]) -> list[str]:
    out = []
    for src, st in (sources or {}).items():
        s = (st or "").strip()
        if not s or s in ("—", "-", "–"):
            continue
        out.append(str(src).lower())
    return sorted(set(out))


def _cili_resolve(ident: str) -> Optional[str]:
    try:
        from .engines import cili_api
        _, _, resolve, _ = cili_api()
        return resolve(ident)
    except Exception:  # noqa: BLE001
        return None


def _extract_cili_ids(ili_list: Any) -> list[str]:
    """Bare CILI ids only — strip contextual CURIEs like ``oewn-ili:``."""
    out: list[str] = []
    seen: set[str] = set()
    try:
        from .engines import load_identifiers
        try_norm = load_identifiers().try_normalize_cili_id
    except Exception:  # noqa: BLE001
        try_norm = None
    for raw in ili_list or []:
        s = str(raw or "").strip()
        if not s:
            continue
        cand = try_norm(s) if try_norm else None
        if not cand:
            if s.startswith(("oewn-ili:", "ili:", "cili:")):
                cand = s.rsplit(":", 1)[-1]
            elif re.match(r"^i\d+$", s):
                cand = s
            else:
                cand = _cili_resolve(s)
        if cand and cand not in seen:
            seen.add(cand)
            out.append(cand)
    return out


def _en_lemmas_from_wn_direct(cili_id: str) -> list[str]:
    """Lookup OEWN/omw-en lemmas for a CILI id (same-thread only for `wn`)."""
    import wn  # type: ignore

    lemmas: list[str] = []
    seen: set[str] = set()
    for s in wn.synsets(ili=cili_id):
        sid = str(getattr(s, "id", "") or "")
        if not (sid.startswith("oewn-") or sid.startswith("omw-en-")):
            continue
        for w in s.lemmas():
            form = (w if isinstance(w, str) else str(w)).replace("_", " ").strip()
            k = fold(form)
            if form and k not in seen:
                seen.add(k)
                lemmas.append(form)
    return lemmas


def _en_lemmas_from_wn_subprocess(cili_id: str) -> list[str]:
    """Thread-safe fallback: `wn` SQLite connections are sticky to one thread."""
    import subprocess

    code = (
        "import json,wn\n"
        f"cid={cili_id!r}\n"
        "out=[]; seen=set()\n"
        "for s in wn.synsets(ili=cid):\n"
        "    sid=str(getattr(s,'id','') or '')\n"
        "    if not (sid.startswith('oewn-') or sid.startswith('omw-en-')): continue\n"
        "    for w in s.lemmas():\n"
        "        f=(w if isinstance(w,str) else str(w)).replace('_',' ').strip()\n"
        "        k=f.lower()\n"
        "        if f and k not in seen:\n"
        "            seen.add(k); out.append(f)\n"
        "print(json.dumps(out, ensure_ascii=False))\n"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        if proc.returncode != 0 or not (proc.stdout or "").strip():
            return []
        data = json.loads(proc.stdout.strip().splitlines()[-1])
        return [str(x) for x in data] if isinstance(data, list) else []
    except Exception:  # noqa: BLE001
        return []


def _en_lemmas_from_wn(cili_id: str) -> list[str]:
    """English lemmas for a CILI id — safe from Tk worker threads."""
    if not cili_id:
        return []
    try:
        return _en_lemmas_from_wn_direct(cili_id)
    except Exception as exc:  # noqa: BLE001
        msg = str(exc).lower()
        if "thread" in msg or "sqlite" in msg:
            return _en_lemmas_from_wn_subprocess(cili_id)
        # Other failures (missing lexicon, etc.) — still try subprocess once
        via = _en_lemmas_from_wn_subprocess(cili_id)
        return via


def _en_lemmas_from_wordnet_result(ws: ClassWorkspace) -> dict[str, list[str]]:
    """cili_id → English lemmas from *.WordNet.result.json synsets."""
    path = ws.results / f"{ws.class_id}.WordNet.result.json"
    out: dict[str, list[str]] = {}
    if not path.exists():
        return out
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return out
    for s in data.get("synsets") or []:
        ili = (s.get("ili") or "").strip()
        if not ili:
            continue
        lemmas = [
            (w or "").replace("_", " ").strip()
            for w in (s.get("lemmas") or [])
            if (w or "").strip()
        ]
        if lemmas:
            out[ili] = lemmas
    return out


def _load_termos_manuais(ws: ClassWorkspace) -> tuple[list[dict[str, Any]], bool]:
    """R2: return (entries, file_exists)."""
    path = ws.root / "termos_manuais.yaml"
    if not path.exists():
        return [], False
    try:
        import yaml  # type: ignore
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001
        return [], True
    entries = raw.get("termos") if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        return [], True
    out = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        forma = (e.get("forma") or "").strip()
        if not forma:
            continue
        out.append({
            "forma": forma,
            "wildcard": _wildcard(e.get("wildcard") or forma),
            "polo": (e.get("polo") or "").strip().lower(),
            "lingua": (e.get("lingua") or "").strip(),
            "fonte": (e.get("fonte") or "").strip(),
            "nota": (e.get("nota") or "").strip(),
            "manual": True,
        })
    return out, True


def _sheet_metadata_norms(meta: dict[str, Any]) -> set[str]:
    """R5: values from the class sheet that must never enter term lists."""
    out: set[str] = set()
    for key in ("pref_label", "axis"):
        v = meta.get(key)
        if isinstance(v, str) and v.strip():
            out.add(fold(v))
            out.add(normalize_word(v))
    for key in ("focus_stems", "axis_terms"):
        for t in meta.get(key) or []:
            if t:
                out.add(fold(str(t)))
                out.add(normalize_word(str(t)))
    out.add(fold(meta.get("class_id") or ""))
    return {x for x in out if x}


def _excluded_axis_norms(meta: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for t in meta.get("control_axes") or meta.get("excluded_axes") or []:
        if isinstance(t, str):
            out.add(fold(t))
            out.add(normalize_word(t))
        elif isinstance(t, dict):
            if t.get("eixo"):
                out.add(fold(str(t["eixo"])))
                out.add(normalize_word(str(t["eixo"])))
            for x in t.get("termos") or []:
                out.add(fold(str(x)))
                out.add(normalize_word(str(x)))
    for k, terms in (meta.get("disjoint_classes") or {}).items():
        out.add(fold(str(k)))
        for x in terms or []:
            out.add(fold(str(x)))
            out.add(normalize_word(str(x)))
    return {x for x in out if x}


def _anchor_pos(dec: dict[str, Any], ancora: list[str]) -> Optional[str]:
    for ili in ancora:
        pos = _pos_from_identifier(ili)
        if pos:
            return pos
    for s in dec.get("senses") or []:
        if (s.get("decision") or "").strip() != "UF":
            continue
        if (s.get("source") or "").lower() != "pulo":
            continue
        pos = _pos_from_identifier(s.get("ili") or s.get("key") or "")
        if pos:
            return pos
    return None


def _sense_pos_for_term(term: str, dec: dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    """Return (pos, sense_key) for an admitted term's primary adjudicated sense."""
    tn = normalize_word(term)
    best = None
    for s in dec.get("senses") or []:
        decision = (s.get("decision") or "").strip()
        if decision not in ADMIT_STATUSES:
            continue
        members = [normalize_word(m) for m in (s.get("members") or [])]
        if tn not in members:
            continue
        key = s.get("ili") or s.get("key")
        pos = _pos_from_identifier(str(key or ""))
        # Prefer UF sense; else first RT
        rank = 2 if decision == "UF" else 1
        if best is None or rank > best[0]:
            best = (rank, pos, str(key or ""))
    if not best:
        return None, None
    return best[1], best[2]


def _shared_sense_groups(
    vocab_forms: list[str], dec: dict[str, Any]
) -> dict[str, list[str]]:
    """sense_key → terms in F that share that adjudicated sense."""
    groups: dict[str, list[str]] = {}
    wanted = {normalize_word(f): f for f in vocab_forms}
    for s in dec.get("senses") or []:
        decision = (s.get("decision") or "").strip()
        if decision not in ADMIT_STATUSES:
            continue
        key = str(s.get("ili") or s.get("key") or "")
        if not key:
            continue
        hit = []
        for m in s.get("members") or []:
            nw = normalize_word(m)
            if nw in wanted:
                hit.append(wanted[nw])
        if hit:
            groups.setdefault(key, [])
            for h in hit:
                if h not in groups[key]:
                    groups[key].append(h)
    return groups


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------
def build_termos_pesquisa(ws: ClassWorkspace) -> dict[str, Any]:
    from .decisions import load_decisions

    meta = ws.load_meta()
    dec = load_decisions(ws.decisions_json)
    langs = resolve_languages(meta)
    search_lang = langs["search_lang"]
    label_lang = langs["label_lang"]
    pref = meta.get("pref_label") or ws.class_id
    axis = meta.get("axis") or ""
    ancora = _ili_anchor(dec, meta)
    cm = meta.get("concept_mapping") if isinstance(meta.get("concept_mapping"), dict) else {}
    excluded_cili_ids = {
        str(x.get("cili") if isinstance(x, dict) else x).strip().rsplit(":", 1)[-1]
        for x in (cm.get("excluded_cili") or [])
        if x
    }
    near_stem = _corpus_near_stem(meta, pref)
    generated = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    registry = build_class_registry()
    registry_designations = set()
    for info in registry.values():
        registry_designations |= set(info.get("designations") or [])
    # Also designations declared on this sheet
    for k in (meta.get("disjoint_classes") or {}):
        registry_designations.add(fold(str(k)))
    if meta.get("superclass"):
        registry_designations.add(fold(str(meta["superclass"])))
    registry_designations.add(fold(ws.class_id))

    sheet_meta = _sheet_metadata_norms(meta)
    focus_seed_norms = {
        normalize_word(str(t))
        for t in list(meta.get("focus_stems") or []) + list(meta.get("axis_terms") or [])
        if t
    } | {
        fold(str(t))
        for t in list(meta.get("focus_stems") or []) + list(meta.get("axis_terms") or [])
        if t
    }
    excluded_axes = _excluded_axis_norms(meta)
    anchor_pos = _anchor_pos(dec, ancora)

    concordance = _load_concordance(ws)
    admits = admitted_matrix_rows(concordance, excluded_cilis=excluded_cili_ids)
    n_admitidos_matriz = len(admits)

    # ---- F — label_lang vocabulary from matrix -----------------------------
    # R5 applies to *sourcing from the sheet*, not to suppressing admits whose
    # surface form coincides with pref_label (that is the normal case).
    admits_filtered = [
        c for c in admits
        if (c.get("term") or "").strip()
        and not _is_registry_designation(c.get("term") or "")
        and fold(c.get("term") or "") not in registry_designations
    ]
    n_admitidos_matriz = len(admits_filtered)

    vocab_f: list[dict[str, Any]] = []
    for c in sorted(admits_filtered, key=lambda x: fold(x.get("term") or "")):
        term = (c.get("term") or "").strip()
        estatuto = (c.get("proposta_final") or "").strip()
        ili = c.get("ili") or []
        if isinstance(ili, str):
            ili = [ili] if ili else []
        # Drop CILI ids that are domain-excluded even if still present on the row
        ili = [x for x in ili if resolve_to_cili(x) not in excluded_cili_ids]
        sense_pos, sense_key = _sense_pos_for_term(term, dec)
        other = _soft_belongs_to_other_class(term, ws.class_id, registry)
        structural_other = _structural_other_class(term, dec, ws.class_id, registry)
        cross_class = other or structural_other
        vocab_f.append({
            "forma": term,
            "wildcard": _wildcard(term),
            "lingua": label_lang,
            "estatuto": estatuto,
            "ili": ili or None,
            "fontes": _fontes_activas(c.get("sources") or {}),
            "garantia": _garantia_label(c.get("veredicto") or ""),
            "ancora_ili": "presente" if ili else "ausente",
            "em_espera": _garantia_label(c.get("veredicto") or "") == "fonte_unica",
            "sense_key": sense_key,
            "sense_pos": sense_pos,
            "cross_class": cross_class,
            "nota": "",
        })

    # Adjudicated alt labels (concept_mapping) enter F even with empty matrix
    have_f = {fold(r["forma"]) for r in vocab_f}
    for alt in cm.get("validated_alt_labels") or []:
        forma = str(alt or "").strip()
        if not forma or fold(forma) in have_f:
            continue
        if fold(forma) in registry_designations or _is_registry_designation(forma):
            continue
        have_f.add(fold(forma))
        vocab_f.append({
            "forma": forma,
            "wildcard": _wildcard(forma),
            "lingua": label_lang,
            "estatuto": "UF",
            "ili": None,
            "fontes": ["concept_mapping"],
            "garantia": "adjudicada",
            "ancora_ili": "ausente",
            "em_espera": False,
            "sense_key": None,
            "sense_pos": None,
            "cross_class": None,
            "nota": "validated_alt_labels",
        })
    vocab_f.sort(key=lambda x: fold(x.get("forma") or ""))

    # ---- Search-lang forms from OEWN equivalents of adjudicated senses -----
    wn_by_ili = _en_lemmas_from_wordnet_result(ws)
    search_by_status: dict[str, list[dict[str, Any]]] = {"UF": [], "RT": []}
    seen_search: set[str] = set()

    def _add_search(forma: str, status: str, ili: Optional[str], fonte: str) -> None:
        f = (forma or "").strip()
        if not f or _is_registry_designation(f):
            return
        # R5 blocks copying sheet seeds into lists; OEWN equivalents of
        # adjudicated senses are results, even when they coincide with a stem.
        if fold(f) in registry_designations:
            return
        k = fold(f)
        if k in seen_search:
            return
        seen_search.add(k)
        bucket = "UF" if status == "UF" else "RT"
        search_by_status.setdefault(bucket, []).append({
            "forma": f,
            "wildcard": _wildcard(f),
            "lingua": search_lang,
            "ili": ili,
            "fonte": fonte,
            "estatuto": status,
            "manual": False,
        })

    if _lang_matches(search_lang, "en"):
        for c in admits_filtered:
            status = (c.get("proposta_final") or "").strip()
            if status not in ("UF", "RT"):
                continue
            for cili in _extract_cili_ids(c.get("ili")):
                if cili in excluded_cili_ids:
                    continue
                lemmas = wn_by_ili.get(cili) or _en_lemmas_from_wn(cili)
                for lem in lemmas:
                    _add_search(lem, status, cili, "OEWN")
            # Also resolve PULO ilis via CILI when concept ili lacks oewn-ili:
            for raw in c.get("ili") or []:
                cili = _cili_resolve(str(raw))
                if not cili or cili in excluded_cili_ids:
                    continue
                lemmas = wn_by_ili.get(cili) or _en_lemmas_from_wn(cili)
                for lem in lemmas:
                    _add_search(lem, status, cili, "OEWN")

    polo_alvo = list(search_by_status.get("UF") or [])
    descritores = list(search_by_status.get("RT") or [])

    # ---- B — contrast (auto signals in search_lang) ------------------------
    polo_contraste: list[dict[str, Any]] = []
    seen_b: set[str] = set()
    if _lang_matches(search_lang, "en"):
        auto = _collect_auto_signals(ws)
        for rel, rows in (
            ("antonym", auto.get("antonym") or []),
            ("similar_to", auto.get("similar_to") or []),
        ):
            for row in rows:
                forma = (row.get("termo") or "").strip()
                if not forma or _is_registry_designation(forma):
                    continue
                k = fold(forma)
                if k in seen_b or k in seen_search or k in sheet_meta:
                    continue
                if k in registry_designations:
                    continue
                seen_b.add(k)
                ili = row.get("ili")
                polo_contraste.append({
                    "forma": forma,
                    "wildcard": _wildcard(forma),
                    "lingua": search_lang,
                    "ili": (ili[0] if isinstance(ili, list) and ili else ili) or None,
                    "fonte": row.get("fonte"),
                    "relacao": rel,
                    "manual": False,
                })

    # ---- C — control (lexical only; never registry designations) -----------
    controlo_meta: list[dict[str, Any]] = []
    control_forms: list[dict[str, Any]] = []
    seen_c: set[str] = set()

    def _add_control(
        forma: str, *, nota: str = "", eixo: str = "", lingua: str = ""
    ) -> None:
        f = (forma or "").strip()
        if not f or _is_registry_designation(f):
            return
        if fold(f) in registry_designations:
            return
        # Control tokens in A–D require search_lang; sheet terms without an
        # explicit lingua stay as notes only (R1).
        entry_lang = (lingua or "").strip()
        if entry_lang:
            if not _lang_matches(entry_lang, search_lang):
                return
        else:
            # No lingua tag → do not invent a search-lang token from the sheet.
            return
        k = fold(f)
        if k in seen_c:
            return
        seen_c.add(k)
        control_forms.append({
            "forma": f,
            "wildcard": _wildcard(f),
            "lingua": search_lang,
            "ili": None,
            "eixo": eixo,
            "nota": nota,
            "manual": False,
        })

    for other, terms in (meta.get("disjoint_classes") or {}).items():
        # Record axis note without emitting the OWL designation as a term.
        if not _is_registry_designation(str(other)):
            controlo_meta.append({
                "eixo": other,
                "termos": [t for t in (terms or []) if not _is_registry_designation(str(t))],
                "nota": "classe disjunta — separar na análise",
            })
        else:
            controlo_meta.append({
                "eixo": "(classe disjunta)",
                "termos": [t for t in (terms or []) if not _is_registry_designation(str(t))],
                "nota": "eixo excluído no registo da ontologia",
            })
        for t in terms or []:
            # disjoint term lists rarely carry lingua — notes only unless tagged
            if isinstance(t, dict):
                _add_control(
                    str(t.get("forma") or t.get("term") or ""),
                    eixo=str(other),
                    nota="classe disjunta",
                    lingua=str(t.get("lingua") or ""),
                )

    for t in meta.get("control_axes") or meta.get("excluded_axes") or []:
        if isinstance(t, str):
            if _is_registry_designation(t):
                controlo_meta.append({
                    "eixo": "(eixo excluído)",
                    "termos": [],
                    "nota": "classe / eixo do registo — não é termo",
                })
            else:
                controlo_meta.append({
                    "eixo": t, "termos": [t], "nota": "eixo excluído",
                })
                # bare string → note only (no lingua)
        elif isinstance(t, dict):
            eixo = t.get("eixo") or ""
            terms = [
                x for x in (t.get("termos") or [])
                if not _is_registry_designation(str(x))
            ]
            eixo_display = (
                "(eixo excluído)" if _is_registry_designation(str(eixo)) else eixo
            )
            controlo_meta.append({
                "eixo": eixo_display,
                "termos": terms,
                "nota": t.get("nota") or "eixo excluído",
            })
            axis_lang = str(t.get("lingua") or "")
            for x in terms:
                if isinstance(x, dict):
                    _add_control(
                        str(x.get("forma") or x.get("term") or ""),
                        eixo=str(eixo),
                        nota=t.get("nota") or "",
                        lingua=str(x.get("lingua") or axis_lang),
                    )
                elif axis_lang:
                    # plain string allowed only when the axis declares lingua
                    _add_control(
                        str(x),
                        eixo=str(eixo),
                        nota=t.get("nota") or "",
                        lingua=axis_lang,
                    )

    # ---- R2 manuals --------------------------------------------------------
    manuals, manuals_present = _load_termos_manuais(ws)
    manual_by_sec: dict[str, list[dict[str, Any]]] = {
        "A": [], "B": [], "C": [], "D": [],
    }
    for e in manuals:
        if not _lang_matches(e.get("lingua") or search_lang, search_lang):
            continue
        if _is_registry_designation(e["forma"]) or fold(e["forma"]) in sheet_meta:
            continue
        sec = _POLO_TO_SECTION.get(e.get("polo") or "")
        if not sec:
            continue
        row = {
            "forma": e["forma"],
            "wildcard": e["wildcard"],
            "lingua": e.get("lingua") or search_lang,
            "ili": None,
            "fonte": e.get("fonte") or "manual",
            "nota": e.get("nota") or "",
            "manual": True,
            "relacao": "manual",
        }
        manual_by_sec[sec].append(row)

    def _merge_manual(base: list[dict], extra: list[dict]) -> list[dict]:
        seen = {fold(r["forma"]) for r in base}
        out = list(base)
        for r in extra:
            k = fold(r["forma"])
            if k in seen:
                continue
            seen.add(k)
            out.append(r)
        return out

    polo_alvo = _merge_manual(polo_alvo, manual_by_sec["A"])
    control_forms = _merge_manual(control_forms, manual_by_sec["C"])
    descritores = _merge_manual(descritores, manual_by_sec["D"])
    # Do not advertise a PT stem as EN NEAR syntax when A is empty
    if not polo_alvo:
        near_stem = ""
    # B after C: control lemmas must not also appear as contrast
    control_norms = {fold(r["forma"]) for r in control_forms}
    polo_contraste = [
        r for r in polo_contraste if fold(r["forma"]) not in control_norms
    ]
    polo_contraste = _merge_manual(polo_contraste, [
        r for r in manual_by_sec["B"] if fold(r["forma"]) not in control_norms
    ])

    # ---- E — excluded acepções (focus-related only; drop other-class residue)
    fronteiras = []
    focus_roots = _focus_morph_roots(meta, pref)
    try:
        from .engines import load_identifiers
        _ids = load_identifiers()
    except Exception:  # noqa: BLE001
        _ids = None
    for s in dec.get("senses") or []:
        if (s.get("decision") or "").strip() != "exclude":
            continue
        src = (s.get("source") or "").lower()
        if src == "onto":
            continue
        ili = (s.get("ili") or s.get("cili") or "").strip() or None
        key = (s.get("key") or "").strip()
        if not ili and not key:
            continue
        members = [m for m in (s.get("members") or []) if (m or "").strip()]
        raw = ili or key
        cili_id = None
        pwn30 = None
        legacy_key = None
        if _ids is not None:
            ident = _ids.parse_identifier(raw, resolve_cili=True)
            cili_id = ident.cili_id or ident.cili
            pwn30 = ident.pwn_id
            legacy_key = ident.legacy_omw_ili
        if str(raw).startswith("ili-30-"):
            legacy_key = legacy_key or raw
        # Keep adjudicated excluded_cili always; else require morphological proximity
        on_topic = bool(cili_id and cili_id in excluded_cili_ids)
        if not on_topic:
            blob = " ".join([key] + members)
            on_topic = _text_related_to_focus(blob, focus_roots)
        if not on_topic:
            continue
        related = [m for m in members if _text_related_to_focus(m, focus_roots)]
        lema = related[0] if related else (members[0] if members else key)
        fronteiras.append({
            "chave": key,
            "chave_legada": legacy_key or (raw if str(raw).startswith("ili-30-") else None),
            "pwn30": pwn30,
            "cili": cili_id,
            # Display field: never label ili-30- as CILI
            "ili": cili_id or pwn30 or legacy_key or raw,
            "lema": lema,
            "motivo": ((s.get("note") or s.get("gloss") or "").strip())[:200],
            "fonte": src,
        })

    # ---- R6 — a_resolver (anomalies only) ----------------------------------
    a_resolver: list[dict[str, Any]] = []
    shared = _shared_sense_groups([r["forma"] for r in vocab_f], dec)

    def _push(forma: str, razoes: list[str], **extra: Any) -> None:
        if not razoes:
            return
        a_resolver.append({
            "forma": forma,
            "estatuto": extra.get("estatuto"),
            "garantia": extra.get("garantia"),
            "razoes": razoes,
        })

    for r in vocab_f:
        razoes: list[str] = []
        # R3(b)
        if r.get("cross_class"):
            razoes.append(
                f"designa o princípio organizador de {r['cross_class']}; "
                "verificar antes de admitir"
            )
        # R4 — POS divergence
        if anchor_pos and r.get("sense_pos") and r["sense_pos"] != anchor_pos:
            razoes.append(
                f"categoria da acepção ({r['sense_pos']}) diverge da âncora "
                f"da classe ({anchor_pos})"
            )
        # excluded axis
        if normalize_word(r["forma"]) in excluded_axes or fold(r["forma"]) in excluded_axes:
            razoes.append("termo ligado a eixo declarado como excluído na ficha")
        if razoes:
            _push(r["forma"], razoes, estatuto=r.get("estatuto"), garantia=r.get("garantia"))

    # R4 — ≥3 terms share a sense whose POS ≠ anchor
    for sense_key, forms in shared.items():
        if len(forms) < 3:
            continue
        spos = _pos_from_identifier(sense_key)
        if anchor_pos and spos and spos != anchor_pos:
            for forma in forms:
                _push(
                    forma,
                    [
                        f"três ou mais termos partilham a acepção {sense_key} "
                        f"(categoria {spos} ≠ âncora {anchor_pos})"
                    ],
                )

    # Adjudicated senses with no matrix row
    matrix_norms = {normalize_word(r["forma"]) for r in vocab_f}
    descartado_onto: list[dict[str, Any]] = []
    for s in dec.get("senses") or []:
        decision = (s.get("decision") or "").strip()
        if decision not in ADMIT_STATUSES:
            continue
        if (s.get("source") or "").lower() == "onto":
            # Onto.PT discovery-only — declared drop, never silent
            descartado_onto.append({
                "key": s.get("key"),
                "membros": [m for m in (s.get("members") or []) if (m or "").strip()],
                "decision": decision,
                "motivo": "Onto.PT discovery-only — não admite na matriz LexWarrant",
            })
            continue
        key = s.get("ili") or s.get("key")
        members = [m for m in (s.get("members") or []) if (m or "").strip()]
        # representative: if NONE of the members appear in matrix, flag the sense
        if members and not any(normalize_word(m) in matrix_norms for m in members):
            _push(
                members[0],
                [f"acepção adjudicada ({key}) sem correspondência na matriz"],
                estatuto=decision,
            )

    # Dedupe a_resolver by forma+razoes
    dedup: dict[str, dict[str, Any]] = {}
    for item in a_resolver:
        k = normalize_word(item["forma"])
        if k not in dedup:
            dedup[k] = item
        else:
            for rz in item["razoes"]:
                if rz not in dedup[k]["razoes"]:
                    dedup[k]["razoes"].append(rz)
    a_resolver = sorted(dedup.values(), key=lambda x: fold(x["forma"]))

    doc = {
        "class_id": ws.class_id,
        "pref_label": pref,
        "axis": axis,
        "scope_note": (meta.get("scope_note") or "").strip(),
        "acepcao_a_separar": axis or pref,
        "ancora_ili": ancora,
        "anchor_pos": anchor_pos,
        "near_stem": near_stem,
        "generated": generated,
        "search_lang": search_lang,
        "label_lang": label_lang,
        "termos_manuais_presentes": manuals_present,
        "n_admitidos_matriz": n_admitidos_matriz,
        "n_validated_alt_labels": sum(
            1 for r in vocab_f if r.get("nota") == "validated_alt_labels"
        ),
        "A_polo_alvo": polo_alvo,
        "B_polo_contrastante": polo_contraste,
        "C_conjunto_controlo": controlo_meta,
        "C_termos": control_forms,
        "D_descritores_adjacentes": descritores,
        "E_fronteiras_dominio": fronteiras,
        "F_vocabulario_pt": vocab_f,
        "a_resolver": a_resolver,
        "descartado_onto_discovery": descartado_onto,
        "D_vocabulario_pt": vocab_f,
        "_sheet_meta_norms": sorted(sheet_meta),
        "_focus_seed_norms": sorted(focus_seed_norms),
        "_registry_designations": sorted(registry_designations),
    }
    from .cili_export import build_cili_blocks, export_cili_block_enabled

    if export_cili_block_enabled(meta):
        try:
            doc["cili_blocks"] = build_cili_blocks(dec.get("senses") or [], meta)
        except Exception:  # noqa: BLE001 — export must not fail the TERMOS write
            doc["cili_blocks"] = []
    return doc


def assert_termos_coherence(doc: dict[str, Any], html_text: str) -> None:
    """R7 — valid for any class."""
    n_f = len(doc.get("F_vocabulario_pt") or [])
    n_m = int(doc.get("n_admitidos_matriz") or 0)
    n_val = int(doc.get("n_validated_alt_labels") or 0)
    # F = matrix admits + adjudicated validated_alt_labels (may exceed matrix)
    if n_f != n_m + n_val:
        raise AssertionError(
            f"TERMOS F ({n_f}) ≠ matriz ({n_m}) + validated_alt_labels ({n_val})"
        )
    designations = set(doc.get("_registry_designations") or [])
    seeds = set(doc.get("_focus_seed_norms") or [])
    for sec_name, rows in (
        ("A", doc.get("A_polo_alvo") or []),
        ("B", doc.get("B_polo_contrastante") or []),
        ("C", doc.get("C_termos") or []),
        ("D", doc.get("D_descritores_adjacentes") or []),
        ("F", doc.get("F_vocabulario_pt") or []),
    ):
        for r in rows:
            forma = r.get("forma") or ""
            if _is_registry_designation(forma) or fold(forma) in designations:
                raise AssertionError(
                    f"Secção {sec_name} contém designação do registo: {forma!r}"
                )
            # R5: sheet seeds must not appear *as sheet copies*. OEWN / manual
            # results may legitimately coincide with a stem (e.g. en "uniform").
            if fold(forma) in seeds or normalize_word(forma) in seeds:
                fonte = (r.get("fonte") or "").lower()
                if r.get("manual") or "oewn" in fonte or fonte in (
                    "wordnet", "pulo", "own-pt", "ownpt"
                ):
                    continue
                if sec_name == "F" and r.get("estatuto") in ADMIT_STATUSES:
                    continue
                raise AssertionError(
                    f"Secção {sec_name} contém focus_stems/axis_terms da ficha: "
                    f"{forma!r}"
                )
    for r in doc.get("C_conjunto_controlo") or []:
        eixo = r.get("eixo") or ""
        if _is_registry_designation(eixo):
            raise AssertionError(
                f"Secção C expõe designação de classe como eixo: {eixo!r}"
            )
    nbytes = len(html_text.encode("utf-8"))
    if nbytes > HTML_MAX_BYTES:
        raise AssertionError(
            f"TERMOS.html tem {nbytes} bytes (máx. {HTML_MAX_BYTES})"
        )
    # Multi-word copy preservation
    sample = _quote_copy_token("alpha beta")
    if " " in sample and not (sample.startswith('"') and sample.endswith('"')):
        raise AssertionError("lemas multipalavra não preservados na cópia")


# ---------------------------------------------------------------------------
# Markdown / CSV
# ---------------------------------------------------------------------------
def _empty_note(lang: str, role: str) -> str:
    return f"_(nenhuma forma em {lang} para {role})_"


def render_termos_md(doc: dict[str, Any]) -> str:
    L: list[str] = []
    ap = L.append
    search_lang = doc.get("search_lang") or "en"
    label_lang = doc.get("label_lang") or "pt-PT"
    ap(f"# Termos de pesquisa — {doc.get('pref_label') or doc.get('class_id')}")
    ap("")
    ap(f"**Classe:** {doc.get('class_id')}")
    if doc.get("axis"):
        ap(f"**Eixo / acepção a separar:** {doc['axis']}")
    if doc.get("scope_note"):
        ap(f"**Nota de âmbito:** {doc['scope_note']}")
    if doc.get("ancora_ili"):
        cili_a, pwn_a, leg_a = [], [], []
        for a in doc["ancora_ili"]:
            s = str(a)
            if s.startswith("i") and s[1:].isdigit():
                cili_a.append(s)
            elif s.startswith("pwn30-"):
                pwn_a.append(s)
            elif s.startswith("ili-30-"):
                leg_a.append(s)
            else:
                cili_a.append(s)
        if cili_a:
            ap(f"**Âncora CILI:** {', '.join(cili_a)}")
        if pwn_a:
            ap(f"**Synset PWN 3.0 de origem:** {', '.join(pwn_a)}")
        if leg_a:
            ap(f"**Chave legada (offset PWN 3.0):** {', '.join(leg_a)}")
    ap(f"**Língua de pesquisa:** `{search_lang}` · **Língua de rótulos:** `{label_lang}`")
    ap(f"**Sintaxe de pesquisa:** {_search_syntax_line(doc)}")
    ap(f"**Gerado:** {doc.get('generated') or '—'}")
    if not doc.get("termos_manuais_presentes"):
        ap("**Termos manuais:** ficheiro `termos_manuais.yaml` ausente nesta classe.")
    ap("")

    def _tok_table(rows: list[dict], cols: list[str]) -> None:
        if not rows:
            return
        ap("| " + " | ".join(cols) + " |")
        ap("|" + "|".join(["---"] * len(cols)) + "|")
        for r in rows:
            ap("| " + " | ".join(str(r.get(c, "—") or "—") for c in cols) + " |")

    ap(f"## A — Pólo alvo (`{search_lang}`)")
    ap("")
    if not doc["A_polo_alvo"]:
        ap(_empty_note(search_lang, "pólo alvo"))
    else:
        _tok_table(doc["A_polo_alvo"], ["forma", "wildcard", "fonte", "ili"])
    ap("")

    ap(f"## B — Pólo contrastante (`{search_lang}`)")
    ap("")
    if not doc["B_polo_contrastante"]:
        ap(_empty_note(search_lang, "pólo contrastante"))
    else:
        _tok_table(
            doc["B_polo_contrastante"],
            ["forma", "wildcard", "relacao", "fonte", "ili"],
        )
    ap("")

    ap(f"## C — Conjunto de controlo (`{search_lang}`)")
    ap("")
    if not doc.get("C_termos") and not doc.get("C_conjunto_controlo"):
        ap(_empty_note(search_lang, "controlo"))
    else:
        for r in doc.get("C_conjunto_controlo") or []:
            terms = ", ".join(r.get("termos") or []) or "—"
            ap(f"- **{r.get('eixo')}** — {r.get('nota') or ''} · termos: {terms}")
        if doc.get("C_termos"):
            _tok_table(doc["C_termos"], ["forma", "wildcard", "nota"])
    ap("")

    ap(f"## D — Descritores adjacentes (`{search_lang}`)")
    ap("")
    if not doc.get("D_descritores_adjacentes"):
        ap(_empty_note(search_lang, "descritores adjacentes"))
    else:
        _tok_table(
            doc["D_descritores_adjacentes"],
            ["forma", "wildcard", "estatuto", "fonte", "ili"],
        )
    ap("")

    ap("## E — Fronteiras de domínio")
    ap("")
    if not doc["E_fronteiras_dominio"]:
        ap("_(nenhuma)_")
    else:
        ap("| chave legada (PWN 3.0) | pwn30 | CILI | lema | motivo |")
        ap("|---|---|---|---|---|")
        for r in doc["E_fronteiras_dominio"]:
            ap(
                f"| `{r.get('chave_legada') or r.get('chave') or '—'}` | "
                f"`{r.get('pwn30') or '—'}` | "
                f"`{r.get('cili') or '—'}` | "
                f"{r.get('lema') or '—'} | {r.get('motivo') or '—'} |"
            )
    ap("")

    ap(f"## F — Vocabulário (`{label_lang}`)")
    ap("")
    vocab = doc.get("F_vocabulario_pt") or []
    if not vocab:
        ap(_empty_note(label_lang, "vocabulário"))
    else:
        ap("| forma | wildcard | estatuto | garantia | âncora ILI | fontes |")
        ap("|---|---|---|---|---|---|")
        for r in vocab:
            fontes = ", ".join(r.get("fontes") or []) or "—"
            ap(
                f"| {r['forma']} | {r['wildcard']} | {r.get('estatuto')} | "
                f"{r.get('garantia')} | {r.get('ancora_ili')} | {fontes} |"
            )
    ap("")
    dropped = doc.get("descartado_onto_discovery") or []
    if dropped:
        ap("## Descartado (Onto.PT discovery-only)")
        ap("")
        ap("Acepções Onto.PT adjudicadas UF/RT — por desenho nunca entram na "
           "matriz LexWarrant (Corte 3). Listadas para rastreabilidade.")
        ap("")
        ap("| chave | decisão | membros |")
        ap("|---|---|---|")
        for r in dropped:
            mems = ", ".join(r.get("membros") or []) or "—"
            ap(f"| {r.get('key')} | {r.get('decision')} | {mems} |")
        ap("")
    from .cili_export import render_cili_md

    cili_md = render_cili_md(doc.get("cili_blocks") or [])
    if cili_md:
        ap(cili_md.rstrip())
        ap("")
    return "\n".join(L)


def render_termos_csv(doc: dict[str, Any]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow([
        "secao", "forma", "wildcard", "lingua", "estatuto", "garantia",
        "ancora_ili", "ili", "fontes", "relacao", "nota",
    ])
    for r in doc["A_polo_alvo"]:
        w.writerow([
            "A", r["forma"], r["wildcard"], r.get("lingua"), r.get("estatuto"),
            "", "", r.get("ili") or "", r.get("fonte") or "", "",
            "manual" if r.get("manual") else "",
        ])
    for r in doc["B_polo_contrastante"]:
        w.writerow([
            "B", r.get("forma"), r.get("wildcard"), r.get("lingua"), "", "",
            "", r.get("ili") or "", r.get("fonte") or "", r.get("relacao") or "",
            "manual" if r.get("manual") else "",
        ])
    for r in doc.get("C_termos") or []:
        w.writerow([
            "C", r.get("forma"), r.get("wildcard"), r.get("lingua"), "", "",
            "", "", r.get("eixo") or "", "", r.get("nota") or "",
        ])
    for r in doc.get("D_descritores_adjacentes") or []:
        w.writerow([
            "D", r["forma"], r["wildcard"], r.get("lingua"), r.get("estatuto"),
            "", "", r.get("ili") or "", r.get("fonte") or "", "",
            "manual" if r.get("manual") else "",
        ])
    for r in doc["E_fronteiras_dominio"]:
        w.writerow([
            "E", r.get("lema") or "", "", "", "exclude", "",
            "", r.get("ili") or r.get("chave") or "", r.get("fonte") or "", "",
            r.get("motivo") or "",
        ])
    for r in doc.get("F_vocabulario_pt") or []:
        w.writerow([
            "F", r["forma"], r["wildcard"], r.get("lingua"), r.get("estatuto"),
            r.get("garantia"), r.get("ancora_ili"),
            ";".join(r["ili"]) if isinstance(r.get("ili"), list) else (r.get("ili") or ""),
            ", ".join(r.get("fontes") or []), "", "",
        ])
    return buf.getvalue()


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
def _esc(s: Any) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def _token_html(
    forma: str, wildcard: str, ili: Any = None, *, flag: bool = False, manual: bool = False
) -> str:
    ili_s = ""
    if isinstance(ili, list):
        ili_s = ili[0] if ili else ""
    elif ili:
        ili_s = str(ili)
    ili_bit = (
        f'<span class="tok-ili" title="Identificador CILI ou chave PWN 3.0">{_esc(ili_s)}</span>'
        if ili_s else ""
    )
    cls = "tok"
    if flag:
        cls += " flag"
    if manual:
        cls += " manual"
    copy_val = _quote_copy_token(wildcard or forma)
    man_bit = '<span class="tok-src">manual</span>' if manual else ""
    return (
        f'<span class="{cls}" data-wc="{_esc(copy_val)}" tabindex="0">'
        f'<span class="tok-wc">{_esc(wildcard)}</span>'
        f'<span class="tok-lemma">{_esc(forma)}</span>'
        f"{ili_bit}{man_bit}"
        f"</span>"
    )


def render_termos_html(doc: dict[str, Any]) -> str:
    pref = doc.get("pref_label") or doc.get("class_id") or ""
    class_id = doc.get("class_id") or ""
    axis = doc.get("acepcao_a_separar") or doc.get("axis") or ""
    ancora = doc.get("ancora_ili") or []
    near = doc.get("near_stem") or "…*"
    generated = doc.get("generated") or ""
    search_lang = doc.get("search_lang") or "en"
    label_lang = doc.get("label_lang") or "pt-PT"
    a_resolver = doc.get("a_resolver") or []
    flagged = {r["forma"] for r in a_resolver}

    def section_tokens(
        sid: str, title: str, blurb: str, rows: list[dict], *, copy: bool = True
    ) -> str:
        forms = [r.get("wildcard") or r.get("forma") or "" for r in rows]
        payload = _copy_payload(forms)
        if not rows:
            body = (
                f'<p class="empty">Nenhuma forma em <code>{_esc(search_lang)}</code> '
                f"para esta secção.</p>"
            )
        else:
            toks = [
                _token_html(
                    r.get("forma") or "",
                    r.get("wildcard") or _wildcard(r.get("forma") or ""),
                    r.get("ili"),
                    flag=(r.get("forma") or "") in flagged,
                    manual=bool(r.get("manual")),
                )
                for r in rows
            ]
            body = f'<div class="tok-row" role="list">{"".join(toks)}</div>'
        btn = ""
        if copy and rows:
            btn = (
                f'<button type="button" class="btn-copy" data-copy="{_esc(payload)}" '
                f'aria-label="Copiar termos da secção {_esc(title)}">Copiar linha</button>'
            )
        return f"""
<section class="sec" id="{_esc(sid)}" aria-labelledby="h-{_esc(sid)}">
  <header class="sec-head">
    <h2 id="h-{_esc(sid)}">{_esc(title)}</h2>
    {btn}
  </header>
  <p class="blurb">{_esc(blurb)}</p>
  {body}
</section>
"""

    sec_a = section_tokens(
        "A", f"A — Pólo alvo ({search_lang})",
        "Equivalentes de pesquisa das acepções UF + consulta manual.",
        doc.get("A_polo_alvo") or [],
    )
    sec_b = section_tokens(
        "B", f"B — Pólo contrastante ({search_lang})",
        "Antónimos e vizinhos com sinalização própria + consulta manual.",
        doc.get("B_polo_contrastante") or [],
    )
    sec_c = section_tokens(
        "C", f"C — Conjunto de controlo ({search_lang})",
        "Formas de controlo em língua de pesquisa (nunca designações de classe).",
        doc.get("C_termos") or [],
    )
    sec_d = section_tokens(
        "D", f"D — Descritores adjacentes ({search_lang})",
        "Equivalentes de pesquisa das acepções RT + consulta manual.",
        doc.get("D_descritores_adjacentes") or [],
    )

    e_bits = []
    for r in doc.get("E_fronteiras_dominio") or []:
        e_bits.append(
            "<li>"
            f"<code>{_esc(r.get('ili') or r.get('chave') or '—')}</code> · "
            f"<strong>{_esc(r.get('lema') or '—')}</strong> — "
            f"{_esc(r.get('motivo') or '—')}"
            "</li>"
        )
    e_body = (
        f'<ul class="acepcoes">{"".join(e_bits)}</ul>'
        if e_bits else '<p class="empty">_(nenhuma)_</p>'
    )
    sec_e = f"""
<section class="sec" id="E" aria-labelledby="h-E">
  <header class="sec-head"><h2 id="h-E">E — Fronteiras de domínio</h2></header>
  <p class="blurb">Acepções excluídas (chave/ILI + lema representativo + motivo).</p>
  {e_body}
</section>
"""

    vocab = doc.get("F_vocabulario_pt") or []
    f_payload = _copy_payload([r.get("wildcard") or r.get("forma") or "" for r in vocab])
    f_rows_html = []
    for r in vocab:
        ili = (
            "; ".join(r["ili"]) if isinstance(r.get("ili"), list)
            else (r.get("ili") or "—")
        )
        fontes = ", ".join(r.get("fontes") or []) or "—"
        flag_cls = ' class="row-flag"' if r["forma"] in flagged else ""
        f_rows_html.append(
            f"<tr{flag_cls}>"
            f"<td><code>{_esc(r.get('wildcard'))}</code><br>"
            f"<span class=\"lemma\">{_esc(r.get('forma'))}</span></td>"
            f"<td>{_esc(r.get('estatuto'))}</td>"
            f"<td>{_esc(r.get('garantia'))}</td>"
            f"<td>{_esc(fontes)}</td>"
            f"<td><code>{_esc(ili)}</code></td>"
            f"</tr>"
        )
    f_body = (
        f'<p class="empty">Nenhuma forma em <code>{_esc(label_lang)}</code> '
        f"para o vocabulário.</p>"
        if not vocab
        else f"""<div class="table-wrap"><table>
    <thead><tr>
      <th scope="col">Termo</th><th scope="col">Estatuto</th>
      <th scope="col">Garantia</th><th scope="col">Fontes</th>
      <th scope="col">Âncora</th>
    </tr></thead>
    <tbody>{''.join(f_rows_html)}</tbody></table></div>"""
    )
    sec_f = f"""
<section class="sec" id="F" aria-labelledby="h-F">
  <header class="sec-head">
    <h2 id="h-F">F — Vocabulário ({_esc(label_lang)})</h2>
    {"<button type='button' class='btn-copy' data-copy='" + _esc(f_payload) + "' aria-label='Copiar vocabulário'>Copiar linha</button>" if vocab else ""}
  </header>
    <p class="blurb">Termos admitidos na matriz (língua de rótulos).</p>
  {f_body}
</section>
"""
    from .cili_export import render_cili_html

    sec_cili = render_cili_html(doc.get("cili_blocks") or [])

    descartado_onto = doc.get("descartado_onto_discovery") or []
    if a_resolver or descartado_onto:
        items = "".join(
            "<li><strong>{f}</strong>"
            "{meta} — {r}</li>".format(
                f=_esc(x["forma"]),
                meta=(
                    f" ({_esc(x.get('estatuto'))})" if x.get("estatuto") else ""
                ),
                r=_esc("; ".join(x.get("razoes") or [])),
            )
            for x in a_resolver
        )
        onto_items = "".join(
            "<li><strong>{m}</strong> ({d}) — {k}</li>".format(
                m=_esc(", ".join(x.get("membros") or []) or "—"),
                d=_esc(x.get("decision")),
                k=_esc(x.get("key")),
            )
            for x in descartado_onto
        )
        onto_block = (
            "<h3>Descartado (Onto.PT discovery-only)</h3>"
            "<p>Acepções Onto.PT adjudicadas UF/RT — por desenho nunca entram "
            "na matriz LexWarrant (Corte 3).</p>"
            f"<ul>{onto_items}</ul>"
        ) if descartado_onto else ""
        list_block = f"<ul>{items}</ul>" if a_resolver else ""
        resolve_box = f"""
<aside class="resolve" aria-labelledby="h-resolve">
  <h2 id="h-resolve">A resolver antes de fixar os rótulos</h2>
  <p>Anomalias que pedem decisão humana (não inclui «fonte única»).</p>
  {list_block}
  {onto_block}
</aside>
"""
    else:
        resolve_box = ""

    manuals_note = ""
    if not doc.get("termos_manuais_presentes"):
        manuals_note = (
            '<p class="meta"><strong>Termos manuais:</strong> '
            "<code>termos_manuais.yaml</code> ausente nesta classe.</p>"
        )

    ancora_txt = ", ".join(ancora) if ancora else "—"
    syntax_plain = _search_syntax_line(doc)
    # Strip markdown backticks for HTML display
    syntax = _esc(syntax_plain.replace("`", ""))

    return f"""<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TERMOS — {_esc(pref)} ({_esc(class_id)})</title>
<style>
:root {{
  --bg: #f7f4ef; --ink: #1c1a17; --muted: #5c564c; --line: #d9d0c4;
  --card: #fffdf8; --accent: #0b5f4b; --accent-ink: #083c30;
  --warn-bg: #fff3e0; --warn-ink: #6b3a00; --warn-line: #e0a86a;
  --flag: #8b2e1f; --focus: #0b5f4b;
  --mono: "Cascadia Mono", "Consolas", "Menlo", ui-monospace, monospace;
  --sans: "Segoe UI", "IBM Plex Sans", system-ui, sans-serif;
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
@media (prefers-reduced-motion: reduce) {{
  html {{ scroll-behavior: auto; }}
  * {{ transition: none !important; animation: none !important; }}
}}
body {{
  margin: 0; padding: 0 1rem 3rem; font-family: var(--sans); color: var(--ink);
  background:
    radial-gradient(1200px 600px at 10% -10%, #e7efe9 0%, transparent 55%),
    radial-gradient(900px 500px at 100% 0%, #efe6d8 0%, transparent 50%),
    var(--bg);
  line-height: 1.45;
}}
.wrap {{ max-width: 960px; margin: 0 auto; }}
header.page {{ padding: 1.75rem 0 1rem; border-bottom: 1px solid var(--line); margin-bottom: 1.25rem; }}
header.page h1 {{ margin: 0 0 .35rem; font-size: clamp(1.5rem, 3vw, 2rem); letter-spacing: -.02em; }}
.meta {{ color: var(--muted); font-size: .95rem; }}
.meta strong {{ color: var(--ink); font-weight: 600; }}
.syntax {{
  margin: 1rem 0 0; padding: .75rem 1rem; background: var(--card);
  border: 1px solid var(--line); border-radius: 6px; font-family: var(--mono); font-size: .95rem;
}}
.syntax code {{ color: var(--accent-ink); }}
.sec {{
  margin: 1.5rem 0; padding: 1rem 1.1rem 1.2rem; background: var(--card);
  border: 1px solid var(--line); border-radius: 8px;
}}
.sec-head {{
  display: flex; flex-wrap: wrap; align-items: center;
  justify-content: space-between; gap: .75rem; margin-bottom: .35rem;
}}
.sec h2 {{ margin: 0; font-size: 1.15rem; }}
.blurb {{ margin: 0 0 .85rem; color: var(--muted); font-size: .92rem; }}
.btn-copy, .btn-export {{
  font: inherit; font-size: .85rem; font-weight: 600;
  padding: .4rem .75rem; border-radius: 999px; cursor: pointer;
  border: 1px solid var(--accent); color: var(--accent-ink); background: #e8f5f0;
}}
.btn-copy:hover, .btn-export:hover {{ background: #d5eee5; }}
.btn-copy:focus-visible, .btn-export:focus-visible {{
  outline: 3px solid var(--focus); outline-offset: 2px;
}}
.btn-copy.ok, .btn-export.ok {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
.btn-export {{ border-radius: 6px; text-decoration: none; display: inline-block; }}
.btn-export.secondary {{
  background: #fff; border-color: var(--line); color: var(--ink); font-weight: 600;
}}
.export-bar {{
  display: flex; flex-wrap: wrap; gap: .55rem; align-items: center;
  margin: 1rem 0 0; padding: .75rem 1rem; background: var(--card);
  border: 1px solid var(--line); border-radius: 6px;
}}
.export-bar .hint {{ color: var(--muted); font-size: .85rem; flex: 1 1 12rem; }}
#export-status {{ color: var(--accent-ink); font-size: .85rem; font-weight: 600; }}
.tok-row {{ display: flex; flex-wrap: wrap; gap: .55rem; }}
.tok {{
  display: inline-flex; flex-direction: column; gap: .1rem;
  min-width: 5.5rem; padding: .45rem .55rem .4rem;
  border: 1px solid var(--line); border-radius: 6px;
  background: #fff; font-family: var(--mono); font-size: .82rem;
}}
.tok:focus-visible {{ outline: 3px solid var(--focus); outline-offset: 2px; }}
.tok-wc {{ font-weight: 700; color: var(--accent-ink); }}
.tok-lemma {{ color: var(--muted); font-size: .78rem; }}
.tok-ili {{ margin-top: .15rem; font-size: .68rem; color: #3d5a80; word-break: break-all; }}
.tok-src {{ margin-top: .1rem; font-size: .65rem; color: #6b4f2a; text-transform: uppercase; letter-spacing: .04em; }}
.tok.flag {{ border-color: var(--flag); box-shadow: inset 3px 0 0 var(--flag); }}
.tok.manual {{ background: #fffaf0; }}
.acepcoes {{ margin: .75rem 0 0; padding-left: 1.2rem; color: var(--muted); font-size: .9rem; }}
.acepcoes strong {{ color: var(--ink); }}
.empty {{ color: var(--muted); font-style: italic; }}
.table-wrap {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: .9rem; }}
th, td {{ text-align: left; padding: .45rem .5rem; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font-size: .78rem; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); }}
td code {{ font-family: var(--mono); font-size: .85rem; }}
td .lemma {{ color: var(--muted); font-size: .82rem; }}
tr.row-flag td {{ background: #fff6f4; }}
.resolve {{
  margin: 1.5rem 0; padding: 1rem 1.15rem; border-radius: 8px;
  border: 1px solid var(--warn-line); background: var(--warn-bg); color: var(--warn-ink);
}}
.resolve h2 {{ margin: 0 0 .4rem; font-size: 1.1rem; }}
.resolve ul {{ margin: .5rem 0 0; padding-left: 1.2rem; }}
footer.page {{
  margin-top: 2rem; color: var(--muted); font-size: .8rem;
  border-top: 1px solid var(--line); padding-top: .75rem;
}}
@media (max-width: 560px) {{ body {{ padding: 0 .7rem 2rem; }} .tok {{ min-width: 45%; }} }}
</style>
</head>
<body>
<div class="wrap">
<header class="page">
  <h1>TERMOS — {_esc(pref)}</h1>
  <p class="meta">
    <strong>Classe:</strong> {_esc(class_id)} ·
    <strong>Âncora CILI:</strong> {_esc(ancora_txt)} ·
    <strong>Acepção a separar:</strong> {_esc(axis)} ·
    <strong>Pesquisa:</strong> {_esc(search_lang)} ·
    <strong>Rótulos:</strong> {_esc(label_lang)} ·
    <strong>Execução:</strong> {_esc(generated)}
  </p>
  {manuals_note}
  <p class="syntax">Sintaxe de pesquisa: <code>{syntax}</code></p>
  <div class="export-bar" role="group" aria-label="Exportar outputs">
    <button type="button" class="btn-export" id="btn-export-folder">
      Exportar tudo para pasta…
    </button>
    <a class="btn-export secondary" id="btn-export-zip" href="EXPORT_ALL.zip" download>
      Descarregar ZIP
    </a>
    <span class="hint">Copia TERMOS, concordância, CONCEPT, coverage, etc. para a pasta que escolher (Chrome / Edge).</span>
    <span id="export-status" aria-live="polite"></span>
  </div>
</header>

{resolve_box}
{sec_a}
{sec_b}
{sec_c}
{sec_d}
{sec_e}
{sec_f}{sec_cili}

<footer class="page">
  Página gerada localmente — sem rede. Irmãos: TERMOS_PESQUISA.md / .csv · EXPORT_ALL.zip.
</footer>
</div>
<textarea id="clip-fallback" aria-hidden="true" tabindex="-1"
  style="position:fixed;left:-9999px;top:0"></textarea>
<script src="export_payload.js"></script>
<script>
(function () {{
  function fallbackCopy(text) {{
    var ta = document.getElementById("clip-fallback");
    ta.value = text; ta.hidden = false; ta.focus(); ta.select();
    try {{ return document.execCommand("copy"); }}
    catch (e) {{ return false; }}
    finally {{ ta.hidden = true; }}
  }}
  function copyText(text, btn) {{
    function done(ok) {{
      if (!btn) return;
      var prev = btn.textContent;
      btn.textContent = ok ? "Copiado" : "Falhou";
      btn.classList.toggle("ok", !!ok);
      setTimeout(function () {{ btn.textContent = prev; btn.classList.remove("ok"); }}, 1400);
    }}
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(text).then(function () {{ done(true); }},
        function () {{ done(fallbackCopy(text)); }});
    }} else {{ done(fallbackCopy(text)); }}
  }}
  document.addEventListener("click", function (ev) {{
    var btn = ev.target.closest(".btn-copy");
    if (!btn) return;
    copyText(btn.getAttribute("data-copy") || "", btn);
  }});
  document.addEventListener("keydown", function (ev) {{
    if (ev.key !== "Enter" && ev.key !== " ") return;
    var t = ev.target.closest(".tok");
    if (!t) return;
    ev.preventDefault();
    var wc = t.getAttribute("data-wc") || "";
    if (wc) copyText(wc, null);
  }});

  function setExportStatus(msg, ok) {{
    var el = document.getElementById("export-status");
    if (!el) return;
    el.textContent = msg || "";
    el.style.color = ok === false ? "#8b2e1f" : "";
  }}

  async function exportAllToFolder() {{
    var bundle = window.SR_EXPORT_BUNDLE;
    var btn = document.getElementById("btn-export-folder");
    if (!bundle || !bundle.files || !bundle.files.length) {{
      setExportStatus("Pacote em falta — volte a correr o pipeline (Run).", false);
      return;
    }}
    if (!window.showDirectoryPicker) {{
      setExportStatus("Seletor de pasta indisponível neste browser — use «Descarregar ZIP».", false);
      var zip = document.getElementById("btn-export-zip");
      if (zip) zip.focus();
      return;
    }}
    try {{
      var root = await window.showDirectoryPicker({{ mode: "readwrite" }});
      var folderName = bundle.folder_name || (bundle.class_id + "_FINAL_RESULTS");
      var target = await root.getDirectoryHandle(folderName, {{ create: true }});
      for (var i = 0; i < bundle.files.length; i++) {{
        var f = bundle.files[i];
        var fh = await target.getFileHandle(f.name, {{ create: true }});
        var w = await fh.createWritable();
        await w.write(f.text);
        await w.close();
      }}
      setExportStatus("Exportados " + bundle.files.length + " ficheiros → " + folderName, true);
      if (btn) {{
        btn.classList.add("ok");
        setTimeout(function () {{ btn.classList.remove("ok"); }}, 1600);
      }}
    }} catch (err) {{
      if (err && err.name === "AbortError") {{
        setExportStatus("Exportação cancelada.");
        return;
      }}
      setExportStatus("Falha: " + (err && err.message ? err.message : err), false);
    }}
  }}

  var exportBtn = document.getElementById("btn-export-folder");
  if (exportBtn) exportBtn.addEventListener("click", exportAllToFolder);
}})();
</script>
</body>
</html>
"""


def write_termos_pesquisa(
    ws: ClassWorkspace,
    dest_dir: Optional[Path] = None,
) -> dict[str, str]:
    doc = build_termos_pesquisa(ws)
    folder = Path(dest_dir) if dest_dir else ws.final_results
    folder.mkdir(parents=True, exist_ok=True)
    md_path = folder / "TERMOS_PESQUISA.md"
    csv_path = folder / "TERMOS_PESQUISA.csv"
    json_path = folder / "TERMOS_PESQUISA.json"
    html_path = folder / "TERMOS.html"
    serial = json.loads(
        json.dumps(doc, default=lambda o: sorted(o) if isinstance(o, set) else o)
    )
    html_text = render_termos_html(doc)
    assert_termos_coherence(doc, html_text)
    md_path.write_text(render_termos_md(doc), encoding="utf-8")
    csv_path.write_text(render_termos_csv(doc), encoding="utf-8")
    json_path.write_text(
        json.dumps(serial, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    html_path.write_text(html_text, encoding="utf-8")
    # ZIP + JS payload for «Exportar tudo para pasta…» on TERMOS.html
    from .export_all import write_export_all

    bundle = write_export_all(ws, dest_dir=folder)
    return {
        "md": str(md_path),
        "csv": str(csv_path),
        "json": str(json_path),
        "html": str(html_path),
        "zip": bundle.get("zip", ""),
        "payload_js": bundle.get("payload_js", ""),
    }
