#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Open English WordNet backend for the GUI.

Uses the official Open English Wordnet release (globalwordnet/english-wordnet)
through the `wn` Python library.

Source: https://github.com/globalwordnet/english-wordnet
"""

from __future__ import annotations

import logging
import math
import warnings
from functools import lru_cache
from typing import Any, Callable, Iterable, Optional

import wn
from wn.ic import Freq, information_content
from wn.morphy import Morphy
from wn.similarity import jcn, lch, lin, path as path_sim, res, wup
import wn.taxonomy

logger = logging.getLogger(__name__)

# PINNED version first. When several OEWN releases are installed (e.g. 2024 AND
# 2025), lookup AND translate() must run on the SAME pinned version so the oewn-…
# ids in an export resolve consistently and the ILI→own-pt bridge is deterministic.
OEWN_PINNED_VERSION = "oewn:2024"
OEWN_LEXICON_CANDIDATES = ("oewn:2024", "oewn:2025", "oewn:2023")
OEWN_LEXICON: str | None = None

# own-pt (OpenWordNet-PT) is the ILI-mediated Portuguese bridge.
OWN_PT_SPECIFIER = "own-pt:1.0.0"
# A synset used for the PT-alignment self-check (invariável/uniforme).
PT_SELFCHECK_SYNSET = "oewn-01973553-a"

NOUN = "n"
VERB = "v"
ADJ = "a"
ADV = "r"

# BCP-like code -> wn lexicon specifier (verified against wn.download).
TRANSLATION_LEXICONS: dict[str, str] = {
    "spa": "omw-es:1.4",
    "por": "own-pt:1.0.0",
    "ita": "omw-it:1.4",
    "fra": "omw-fr:1.4",
    "deu": "odenet:1.4",
    "jpn": "omw-ja:1.4",
    "nld": "omw-nl:1.4",
    "pol": "omw-pl:1.4",
}

LANGUAGE_LABELS: dict[str, str] = {
    "eng": "English",
    "spa": "Spanish",
    "por": "Portuguese",
    "ita": "Italian",
    "fra": "French",
    "deu": "German",
    "jpn": "Japanese",
    "nld": "Dutch",
    "pol": "Polish",
}

_LEXICON_WORDNET_CACHE: dict[str, wn.Wordnet] = {}
OMW_EN_DEPENDENCY = "omw-en:1.4"

try:
    WnWarning = wn.WnWarning
except AttributeError:  # pragma: no cover
    WnWarning = Warning


def format_score(value: Optional[float]) -> str:
    """Format a similarity/IC float for GUI display."""
    if value is None:
        return "N/A"
    if math.isinf(value):
        return "inf"
    return f"{value:.4f}"


def _wrap_list(items: Iterable[Any]) -> list["SynsetAdapter"]:
    return [SynsetAdapter(item) for item in items]


def _lexicon_base(specifier: str) -> str:
    return specifier.split(":")[0]


def _lexicon_installed(specifier: str) -> bool:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=WnWarning)
        try:
            return bool(wn.lexicons(lexicon=specifier))
        except Exception:
            base = _lexicon_base(specifier)
            try:
                return any(lex.id == base for lex in wn.lexicons(lexicon=f"{base}:*"))
            except Exception:
                return False


class LemmaAdapter:
    """NLTK-like lemma wrapper around a wn Sense."""

    def __init__(self, sense: Any):
        self._sense = sense

    def name(self) -> str:
        return self._sense.word().lemma()

    def synset(self) -> "SynsetAdapter":
        return SynsetAdapter(self._sense.synset())

    def antonyms(self) -> list["LemmaAdapter"]:
        try:
            return [LemmaAdapter(s) for s in self._sense.get_related("antonym")]
        except Exception:
            return []

    def derivationally_related_forms(self) -> list["LemmaAdapter"]:
        try:
            return [LemmaAdapter(s) for s in self._sense.get_related("derivation")]
        except Exception:
            return []

    def pertainyms(self) -> list["LemmaAdapter"]:
        try:
            return [LemmaAdapter(s) for s in self._sense.get_related("pertainym")]
        except Exception:
            return []

    def frame_strings(self) -> list[str]:
        return []


class SynsetAdapter:
    """NLTK-like synset wrapper around a wn Synset."""

    def __init__(self, synset: Any):
        self._ss = synset

    def _rel(self, relation: str) -> list["SynsetAdapter"]:
        try:
            return _wrap_list(self._ss.get_related(relation))
        except Exception as exc:
            logger.debug("Relation %s unavailable for %s: %s", relation, self.name(), exc)
            return []

    def name(self) -> str:
        return self._ss.id

    def pos(self) -> str:
        return self._ss.pos

    def definition(self) -> str:
        return self._ss.definition() or ""

    def examples(self) -> list[str]:
        return list(self._ss.examples())

    def lemmas(self) -> list[LemmaAdapter]:
        return [LemmaAdapter(sense) for sense in self._ss.senses()]

    def lemma_names(self, lang: str = "eng") -> list[str]:
        return get_translation_lemmas(self, lang)

    def ili(self) -> str | None:
        """Interlingual index id (canonical cross-resource key), or None.

        `name()` (the oewn id) stays the LOCAL id; this is the value that may be
        joined against other resources. Never synthesised from the oewn id.
        """
        try:
            ili = self._ss.ili
            if ili is None:
                return None
            # wn>=1.x may expose the ILI as a plain string ("i10771") or as an
            # ILI object with an `.id`. Read whichever the library returns; never
            # build it from the oewn id.
            return getattr(ili, "id", ili)
        except Exception:
            return None

    def pt_lemmas(self) -> list[str]:
        """Portuguese lemmas via ILI-mediated translation to own-pt (OpenWordNet-PT).

        Uses the EXACT proven-working call: `self._ss.translate(lexicon=OWN_PT_SPECIFIER)`
        on a synset opened under the pinned OEWN version. Returns [] only when
        translate() is genuinely empty for THIS synset (logged at debug) — never as
        a blanket "own-pt missing" fallback. Never raises.
        """
        try:
            targets = self._ss.translate(lexicon=OWN_PT_SPECIFIER)
            names: list[str] = []
            for t in targets:
                names.extend(t.lemmas())          # wn: Synset.lemmas() -> list[str]
            out = list(dict.fromkeys(names))       # order-preserving dedupe
            if not out:
                logger.debug("own-pt: no PT synset for %s (translate empty)", self.name())
            return out
        except Exception as exc:  # noqa: BLE001
            logger.warning("own-pt translate failed for %s: %s", self.name(), exc)
            return []

    def hypernyms(self) -> list["SynsetAdapter"]:
        return _wrap_list(self._ss.hypernyms())

    def instance_hypernyms(self) -> list["SynsetAdapter"]:
        return self._rel("instance_hypernym")

    def hyponyms(self) -> list["SynsetAdapter"]:
        return self._rel("hyponym")

    def instance_hyponyms(self) -> list["SynsetAdapter"]:
        return self._rel("instance_hyponym")

    def similar_tos(self) -> list["SynsetAdapter"]:
        return self._rel("similar")

    def entailments(self) -> list["SynsetAdapter"]:
        return self._rel("entailment")

    def causes(self) -> list["SynsetAdapter"]:
        return self._rel("cause")

    def also_sees(self) -> list["SynsetAdapter"]:
        return self._rel("also")

    def verb_groups(self) -> list["SynsetAdapter"]:
        return self._rel("verb_group")

    def member_holonyms(self) -> list["SynsetAdapter"]:
        return self._rel("holo_member")

    def part_holonyms(self) -> list["SynsetAdapter"]:
        return self._rel("holo_part")

    def substance_holonyms(self) -> list["SynsetAdapter"]:
        return self._rel("holo_substance")

    def member_meronyms(self) -> list["SynsetAdapter"]:
        return self._rel("mero_member")

    def part_meronyms(self) -> list["SynsetAdapter"]:
        return self._rel("mero_part")

    def substance_meronyms(self) -> list["SynsetAdapter"]:
        return self._rel("mero_substance")

    def attributes(self) -> list["SynsetAdapter"]:
        return self._rel("attribute")

    def topic_domains(self) -> list["SynsetAdapter"]:
        return self._rel("has_domain_topic")

    def region_domains(self) -> list["SynsetAdapter"]:
        return self._rel("has_domain_region")

    def usage_domains(self) -> list["SynsetAdapter"]:
        return self._rel("has_domain_usage")

    def min_depth(self) -> int:
        return self._ss.min_depth()

    def max_depth(self) -> int:
        return self._ss.max_depth()

    def hypernym_paths(self) -> list[list["SynsetAdapter"]]:
        return [
            _wrap_list(reversed([self._ss] + list(path)))
            for path in self._ss.hypernym_paths()
        ]

    def root_hypernyms(self) -> list["SynsetAdapter"]:
        paths = self.hypernym_paths()
        if not paths:
            return [self]
        return [path[-1] for path in paths]

    def closure(self, relation: Callable[["SynsetAdapter"], list["SynsetAdapter"]], depth: int = -1):
        seen = {self.name()}
        agenda = [(self, 0)]
        out = []
        while agenda:
            node, level = agenda.pop(0)
            out.append(node)
            if depth >= 0 and level >= depth:
                continue
            for related in relation(node):
                key = related.name()
                if key not in seen:
                    seen.add(key)
                    agenda.append((related, level + 1))
        return out[1:]

    def tree(self, relation: Callable[["SynsetAdapter"], list["SynsetAdapter"]], depth: int = -1):
        if depth == 0:
            return self
        children = relation(self)
        if not children:
            return self
        return [self, [child.tree(relation, depth - 1) for child in children]]

    def common_hypernyms(self, other: "SynsetAdapter") -> list["SynsetAdapter"]:
        return _wrap_list(self._ss.common_hypernyms(other._ss))

    def lowest_common_hypernyms(self, other: "SynsetAdapter") -> list["SynsetAdapter"]:
        return _wrap_list(self._ss.lowest_common_hypernyms(other._ss))

    def shortest_path_distance(self, other: "SynsetAdapter") -> Optional[int]:
        try:
            return len(self._ss.shortest_path(other._ss)) - 1
        except Exception:
            return None

    def path_similarity(self, other: "SynsetAdapter") -> Optional[float]:
        try:
            return path_sim(self._ss, other._ss)
        except Exception:
            return None

    def lch_similarity(self, other: "SynsetAdapter") -> Optional[float]:
        try:
            max_depth = wn.taxonomy.taxonomy_depth(get_wordnet(), self.pos())
            return lch(self._ss, other._ss, max_depth)
        except Exception:
            return None

    def wup_similarity(self, other: "SynsetAdapter") -> Optional[float]:
        try:
            return wup(self._ss, other._ss)
        except Exception:
            return None

    def res_similarity(self, other: "SynsetAdapter", ic: Freq) -> Optional[float]:
        try:
            return res(self._ss, other._ss, ic)
        except Exception:
            return None

    def jcn_similarity(self, other: "SynsetAdapter", ic: Freq) -> Optional[float]:
        try:
            value = jcn(self._ss, other._ss, ic)
            return None if (value is not None and math.isinf(value)) else value
        except Exception:
            return None

    def lin_similarity(self, other: "SynsetAdapter", ic: Freq) -> Optional[float]:
        try:
            return lin(self._ss, other._ss, ic)
        except Exception:
            return None


class WordNetLemmatizer:
    """Minimal NLTK-compatible lemmatizer backed by wn Morphy."""

    def __init__(self):
        self._morphy = Morphy(get_wordnet())

    def lemmatize(self, word: str, pos: str = NOUN) -> str:
        result = self._morphy(word, pos=pos)
        lemmas = result.get(pos) or set()
        return next(iter(lemmas), word) if lemmas else word


class _WordnetICModule:
    """Brown-corpus IC weights for Open English Wordnet (main thread only)."""

    _cache: Freq | None = None

    @classmethod
    def ic(cls, _filename: str | None = None) -> Freq:
        if cls._cache is not None:
            return cls._cache
        try:
            import nltk

            nltk.download("brown", quiet=True)
            from nltk.corpus import brown

            en = get_wordnet()
            morphy = Morphy(en)
            en.lemmatizer = morphy  # type: ignore[attr-defined]
            tokens = [w.lower() for w in brown.words() if w.isalpha()]
            cls._cache = wn.ic.compute(tokens, en)
            return cls._cache
        except Exception as exc:
            raise RuntimeError(
                "Information Content indisponível para Open English Wordnet. "
                "Instale NLTK e o corpus Brown: pip install nltk && python -m nltk.downloader brown"
            ) from exc

    @classmethod
    def is_ready(cls) -> bool:
        return cls._cache is not None


wordnet_ic = _WordnetICModule()


def _ensure_lexicon(specifier: str) -> None:
    if not _lexicon_installed(specifier):
        wn.download(specifier)
    if specifier.startswith("omw-") and specifier != OMW_EN_DEPENDENCY:
        if not _lexicon_installed(OMW_EN_DEPENDENCY):
            try:
                wn.download(OMW_EN_DEPENDENCY)
            except Exception as exc:
                logger.debug("Optional OMW dependency %s unavailable: %s", OMW_EN_DEPENDENCY, exc)


def ensure_oewn() -> str:
    """Return the pinned Open English Wordnet lexicon id (download if needed).

    Prefers an ALREADY-INSTALLED candidate (pinned 2024 first) and never silently
    jumps to a newer release when the pinned one is present — otherwise the export
    ids and the translate() bridge could resolve under different versions.
    """
    global OEWN_LEXICON
    if OEWN_LEXICON:
        return OEWN_LEXICON

    for candidate in OEWN_LEXICON_CANDIDATES:
        if _lexicon_installed(candidate):
            OEWN_LEXICON = candidate
            logger.info("OEWN pinned to installed lexicon %s", candidate)
            return candidate

    last_error: Exception | None = None
    for candidate in OEWN_LEXICON_CANDIDATES:
        try:
            wn.download(candidate)
            OEWN_LEXICON = candidate
            logger.info("OEWN downloaded and pinned to %s", candidate)
            return candidate
        except Exception as exc:
            last_error = exc

    raise RuntimeError(
        "Não foi possível descarregar Open English Wordnet.\n"
        "Verifique a ligação à Internet e execute:\n"
        "  pip install wn\n"
        "  python -c \"import wn; wn.download('oewn:2024')\""
    ) from last_error


@lru_cache(maxsize=1)
def get_wordnet() -> wn.Wordnet:
    return wn.Wordnet(ensure_oewn())


def own_pt_installed() -> bool:
    """True iff the OpenWordNet-PT bridge lexicon is installed."""
    return _lexicon_installed(OWN_PT_SPECIFIER)


def pt_alignment_selfcheck(log: bool = True) -> list[str]:
    """Return (and log) the PT lemmas for the canonical self-check synset.

    Makes a translate() regression immediately visible: with own-pt installed and
    the pinned OEWN version, `oewn-01973553-a` must yield ['invariável', 'uniforme'].
    """
    pt: list[str] = []
    try:
        pt = synset(PT_SELFCHECK_SYNSET).pt_lemmas()
    except Exception as exc:  # noqa: BLE001
        logger.warning("PT self-check failed for %s: %s", PT_SELFCHECK_SYNSET, exc)
    if log:
        version = OEWN_LEXICON or "?"
        msg = (f"[pt-selfcheck] {PT_SELFCHECK_SYNSET} @ {version} "
               f"(own-pt installed={own_pt_installed()}): {pt}")
        logger.info(msg)
        print(msg)
    return pt


def get_translation_wordnet(lang: str) -> wn.Wordnet:
    """Return a cached Wordnet handle for a translation lexicon."""
    if lang in ("eng", "en"):
        return get_wordnet()

    specifier = TRANSLATION_LEXICONS.get(lang)
    if not specifier:
        raise KeyError(f"Idioma não suportado: {lang}")

    if specifier not in _LEXICON_WORDNET_CACHE:
        _ensure_lexicon(specifier)
        expand = ensure_oewn()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=WnWarning)
            _LEXICON_WORDNET_CACHE[specifier] = wn.Wordnet(specifier, expand=expand)

    return _LEXICON_WORDNET_CACHE[specifier]


def ensure_translation_lexicon(lang: str) -> str:
    """Ensure a translation lexicon is installed; return its specifier."""
    if lang in ("eng", "en"):
        return ensure_oewn()
    specifier = TRANSLATION_LEXICONS[lang]
    _ensure_lexicon(specifier)
    get_translation_wordnet(lang)
    return specifier


def get_translation_lemmas(synset: SynsetAdapter, lang: str) -> list[str]:
    """Return unique translated lemmas for a synset, or [] if unavailable."""
    if lang in ("eng", "en"):
        return list(synset._ss.lemmas())

    specifier = TRANSLATION_LEXICONS.get(lang)
    if not specifier:
        return []

    try:
        _ensure_lexicon(specifier)
        translated = synset._ss.translate(lexicon=specifier)
        names: list[str] = []
        for target in translated:
            names.extend(target.lemmas())
        # Preserve order, drop duplicates.
        return list(dict.fromkeys(names))
    except Exception as exc:
        logger.warning("Translation failed for %s -> %s: %s", synset.name(), lang, exc)
        return []


def get_available_languages() -> dict[str, str]:
    """Languages offered by the GUI (English always available)."""
    available = {"eng": LANGUAGE_LABELS["eng"]}
    for code, label in LANGUAGE_LABELS.items():
        if code == "eng":
            continue
        specifier = TRANSLATION_LEXICONS.get(code)
        if not specifier:
            continue
        suffix = "" if _lexicon_installed(specifier) else " *"
        available[code] = f"{label}{suffix}"
    return available


def list_installed_translation_languages() -> list[str]:
    return [
        code
        for code in TRANSLATION_LEXICONS
        if _lexicon_installed(TRANSLATION_LEXICONS[code])
    ]


def synsets(
    word: str,
    pos: str | None = None,
    lang: str | None = None,
) -> list[SynsetAdapter]:
    if lang and lang not in ("eng", "en"):
        try:
            target = get_translation_wordnet(lang)
            return _wrap_list(target.synsets(word, pos=pos))
        except Exception as exc:
            logger.warning("Search failed for %r in %s: %s", word, lang, exc)
            return []
    return _wrap_list(get_wordnet().synsets(word, pos=pos))


def synset(name: str) -> SynsetAdapter:
    return SynsetAdapter(get_wordnet().synset(name))


def lemmas(word: str, lang: str = "eng") -> list[LemmaAdapter]:
    try:
        if lang in ("eng", "en"):
            net = get_wordnet()
        else:
            net = get_translation_wordnet(lang)
        return [LemmaAdapter(sense) for w in net.words(word) for sense in w.senses()]
    except Exception as exc:
        logger.warning("Lemma lookup failed for %r (%s): %s", word, lang, exc)
        return []


def morphy(word: str, pos: str | None = None) -> str | None:
    morphy_engine = Morphy(get_wordnet())
    if pos is None:
        for candidate_pos in (NOUN, VERB, ADJ, ADV):
            forms = morphy_engine(word, pos=candidate_pos).get(candidate_pos, set())
            if forms:
                return next(iter(forms))
        return None
    forms = morphy_engine(word, pos=pos).get(pos, set())
    return next(iter(forms), None) if forms else None


def langs() -> list[str]:
    return sorted({lex.language for lex in wn.lexicons(lexicon="*")})


def information_content_value(synset: SynsetAdapter, ic: Freq) -> float:
    return information_content(synset._ss, ic)
