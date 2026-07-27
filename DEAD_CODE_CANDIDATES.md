# Candidatos a código morto (após limpeza dos 3 cortes)

Gerado por `tools/find_dead_code.py`. **Decisão: manter** — são CLIs manuais / smoke-check, não imports do pipeline.

| ficheiro | decisão |
|---|---|
| `engines/ONTO/spec_finalize_skos.py` | manter — finalizador Onto (CLI) |
| `engines/PULO Thesaurus GUI/spec_finalize_pulo.py` | manter — finalizador PULO (CLI) |
| `verify_pipeline.py` | manter — smoke-check do README |

## Removido nesta limpeza

- UI / API morta da Ponte ILI (`ILI_BRIDGE_HELP_TEXT`, `_open_ili_*`; `ili_bridge` reduzido a leitura legada)
- `cili-master/` (~57 MB) — CILI já em `engines/LexWarrant/data/cili/`
- `classes/DemoClass/` — residual de testes
- Docs regeneráveis / obsoletos: `RELATORIO_PIPELINE_ONTO_PULO.md`,
  `ONTO_RESOURCES_DIAGNOSIS.*`, `VERSION_MANIFEST.json` (raiz)
