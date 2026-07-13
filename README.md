# Semantic Research — Fase 0 workbench

Thin daily interface over your existing Portuguese lexicon stack
(**PULO**, **Onto.PT / CONTO.PT**, **LexWarrant**). Same science; one screen.

## Daily path (only this)

1. Open a **class** (or create one).
2. **Search** a lemma in PULO and/or Onto.PT → sense cards appear.
3. Mark each sense: **UF · RT · exclude · atributo · contraste**.
4. Click **Run** → engines + LexWarrant.
5. Read `classes/<Class>/out/<Class>.concordance.md`.

You should not need to open export / skeleton / spec / whitelist files.

## Layout per class

```
classes/<Class>/
  class.json
  decisions.json          # curated choices
  FINAL_RESULTS__Onto_plus_PULO/   # DELIVERABLE (open OPEN_ME__FINAL_RESULTS.html)
  exports/ results/ out/  # scratch (signals, engine dumps)
  _specs/                 # compiled engine specs
```

## Run

```powershell
cd "C:\Users\lmr20\Desktop\Semantic_Research"
pip install -r requirements.txt
python sr.py gui
# or double-click start_workbench.bat
```

CLI:

```powershell
python sr.py new TexturaUniforme --pref uniforme --axis "invariância face a um parâmetro" --stems uniform,invari,constant
python sr.py search TexturaUniforme uniforme --source pulo
python sr.py search TexturaUniforme uniforme --source onto
python sr.py status TexturaUniforme
python sr.py run TexturaUniforme
```

## Config

Everything essential now lives **inside this folder** — `config.json` points at
`engines\` (self-contained; the old `Tesaurus e Dicionários` folder is archive):

| Key | Points to |
|-----|-----------|
| `pulo_sqlite` | `engines\PULO Thesaurus GUI\pulo.sqlite` (~104 MB) |
| `onto_sqlite` | `engines\ONTO\ontopt.sqlite` (~340 MB) |
| `pulo_engine_dir` | `engines\PULO Thesaurus GUI` (`phase0_pulo.py`) |
| `onto_engine_dir` | `engines\ONTO` (`phase0_skos.py`) |
| `lexwarrant_dir` | `engines\LexWarrant` (`lexwarrant.py` + tests) |

This project does **not** reimplement the engines; it compiles `decisions.json`
into their specs and calls them. Sanity check any time:

```powershell
python verify_pipeline.py
```

## Why this exists

The previous ecosystem was correct but had three UIs, many artefact types, and
scattered outputs. Here: **one decisions file, one Run, one concordance**.
