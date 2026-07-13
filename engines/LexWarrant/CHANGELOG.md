# CHANGELOG — LexWarrant

## [versão a fixar] — 2026-07-13 — CILI Tarefa 2: geração ancorada no catálogo canónico

- `build_ili_equivalence.py`: novo passo CILI antes da inferência por lema —
  quando `cili_resolve(oewn i-code)` e `cili_resolve(pulo ili-30-…)` devolvem a
  MESMA identidade canónica, o par sai como alta confiança com
  `source: "cili:<versão>"` e `evidence.cili_identity`; a inferência por lema
  é suprimida para esse synset (o catálogo substitui a heurística onde existe
  mapeamento autoritativo). Sem identidade CILI, mantém-se o comportamento
  por lema, agora com proveniência explícita (`auto: shared-lemma …`).
- Ponte GUI (`semantic/ili_bridge.py`): linhas `cili:` são a única excepção
  autorizada a entrar em `map` sem promoção humana (identidade directa
  id↔offset); linhas humanas continuam imutáveis e VENCEM duplicados CILI
  (o CILI passa a corroboração reportada); linhas legacy confirmadas pelo
  CILI são substituídas pela versão canónica (upgrade, nunca downgrade).
- Aceitação TexturaUniforme: 3 mapeados mantidos — 2 humanos intactos e
  CORROBORADOS pelo CILI (i10771↔01966488-a; i4126↔00744506-a), 1 legacy
  promovido a `cili:` (i60712↔04509592-n); as 5 candidatas ambíguas de
  i10771 saem de `review` (a identidade canónica dispensa-as); round-trip
  JSON ✓; suíte 22 testes OK; fusão 11/11 PASS.

## [registo] — 2026-07-13 — Tarefa 3 NÃO executada: limitação estrutural do ONTO

- Descoberta documentada: no `ontopt.sqlite` real, os `sid` de TODOS os
  recursos ONTO (`contopt`, `clip21`, `fuzzythes`, `thes5rec`, `top01`,
  `clip01`, `polaridades`, `ontopt06`) são inteiros sequenciais SEM traço
  PWN-3.0 (esquema `synset(res,sid,pos,gloss)`, sem campo de mapeamento).
  «Sentidos ONTO com offset PWN resolvível» = conjunto vazio nesta base.
- Consequência: o lado ONTO é corroboração-só POR NATUREZA DO RECURSO, não
  por tabela em falta. Ancorá-lo exigiria uma distribuição do Onto.PT/ECO
  que exporte o mapeamento para PWN, ou re-projecção própria dos synsets —
  projectos autónomos, fora de âmbito. Os namespaces continuam flagueados
  como não-juntáveis (T3 preservada).

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

