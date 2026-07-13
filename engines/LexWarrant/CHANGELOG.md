# CHANGELOG — LexWarrant

## [versão a fixar] — 2026-07-13 — CILI Tarefa 1: vendor + resolver

- Vendorizado o catálogo canónico CILI (GWA) em `data/cili/ili-map-pwn30.tab`
  (117 659 pares `i-id ↔ offset PWN-3.0`; TSV 2 colunas sem cabeçalho), com
  `HEADER.txt` a registar URL, commit (`eeab8003`, master) e data. Offline —
  zero rede em runtime.
- Novo `cili_resolver.py`: `cili_resolve(id) -> "i…" | None` e
  `cili_offset("i…") -> offset`. Lookup puro (aceita `i…`, `ili-30-…`/`por-30-…`
  e offset nu `XXXXXXXX-p`); sem inferência, sem efeitos laterais, nunca
  levanta; desconhecido/lixo → None (nunca ILI fabricado).
- 6 testes novos (`tests/test_cili_resolver.py`): round-trip de i-code OEWN,
  resolução de offset PWN-3.0, lixo→None, nunca-levanta. Suíte total: 22 OK.

## [versão a fixar] — 2026-07-13 — Tarefa B: faixa WordNet na fusão

- Novo `semantic/wordnet_track.py`: adapta o export OEWN de facetas
  (`uniform.facets.json`) a `<Classe>.WordNet.result.json`, consumido pelo
  `run_report` como TERCEIRA fonte (rótulo WordNet), ao lado de PULO e ONTO.
- Disciplina: a faixa CORROBORA — todas as entradas em `sinalizacao`, nunca
  estatutos; só são convocados os OEWN ILIs com linha `map` human-adjudicated
  na tabela (i10771, i4126); vestuário/verbo (i60712, i33388) explicitamente
  não convocados (`skipped_ilis`).
- Relações tipadas do OEWN (antonym: multiform/differentiated; similar_to)
  entram como material de contraste ancorado em ILI, sem estatuto.
- `pipeline.run_class` (re)gera a faixa quando existem facets + adjudicações e
  junta-a à fusão se o ficheiro existir; sem faixa, T6 continua no ramo
  «coluna toda —».
- Resultado TexturaUniforme: coluna WordNet preenchida (8/18), T6 passa a
  «WordNet presente — N/A», T1–T11 = 11/11 PASS; sem junções ILI novas —
  ver nota no relatório (faixa é sinalização-só e as pernas PULO/ONTO não
  transportam os ILIs mapeados nos mesmos termos).

## [versão a fixar] — 2026-07-13 — Tarefa A: geração NÃO-destrutiva da tabela ILI (GUI)

- Botão «Ponte ILI…» no workbench (`semantic/ili_bridge.py` + painel em
  `semantic/workbench.py`): (re)gera `classes/<Classe>/out/ili_equivalence.json`
  — o caminho exacto que `run_report/_discover_map` lê.
- MERGE, nunca overwrite: linhas `map` existentes são preservadas; linhas com
  `source: "human-adjudicated…"` são imutáveis (não rebaixadas nem reescritas);
  linhas antigas sem proveniência são transportadas como `legacy`.
- O gerador PROPÕE, nunca decide: toda a linha automática (mesmo par único)
  entra em `review` com `source: "auto: shared-lemma (par único|ambíguo)"`;
  a promoção review→map é exclusivamente humana (checkbox no painel, com
  glosa PULO visível; `source: "human-adjudicated (GUI Ponte ILI) — nota"`).
- `coverage` recalculado após o merge; um `oewn_ili` mapeado por decisão
  humana deixa de figurar em `unmatched`.
- Aceitação: partir de 3 mapeados → botão → continua 3 mapeados, humanas
  intactas byte a byte, 0 autos em map, coverage coerente.

## [versão a fixar] — 2026-07-13 — Tarefa 1: reticulado de estatutos no veredicto

- `project_status_for_comparison(status)` + tabela declarada `STATUS_COMPAT`:
  a comparação do veredicto passa a usar conjuntos de compatibilidade
  (atributo↔{UF,RT}; BT/NT neutros; UF/RT/contraste eles próprios; contraste
  isolado). Convergência = intersecção não-vazia dos projectados; divergência
  = intersecção vazia. Elimina divergências-artefacto por granularidade
  (PULO=atributo vs ONTO=RT/UF) sem mascarar oposição genuína
  (atributo/UF/RT vs contraste continua divergência).
- O estatuto RICO original permanece intacto na matriz, no JSON e nas colunas
  por-fonte; a projecção alimenta apenas a comparação.
- Auditoria: novo campo `status_projection` por conceito (ex.:
  `{"PULO": "atributo→RT/UF"}`) + nota humana «projecção p/ comparação: …».
- `proposta_final` (conservative) em convergência com brutos distintos propõe
  o estatuto mais específico realmente presente numa fonte (nunca inventado);
  divergência continua ⇒ null.
- T1–T11 sem regressões (16 testes unitários + fusão TexturaUniforme +
  fixtures de divergência genuína: 11/11 PASS).

### Correcção (opção iii) — proposta_final com dupla natureza
- Em convergência projectada com estatutos brutos mistos envolvendo «atributo»
  (ex.: PULO=atributo ∩ ONTO=RT), a proposta continua a ser o estatuto mais
  específico realmente presente, MAS regista-se nota explícita:
  «proposta “RT” com dupla natureza: PULO via “atributo”
  (destino :temAtributo preservado)». Nada é inventado; T1–T11 PASS.

