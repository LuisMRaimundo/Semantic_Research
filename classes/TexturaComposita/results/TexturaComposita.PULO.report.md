# Fase 0 (PULO / WordNet.PT) — **TexturaCompósita** (`TexturaComposita`)

- **Eixo definidor:** heterogeneidade / composição de materiais ou partes distintas
- **Fonte:** PULO / WordNet.PT export (âncora ILI; sem porta estatística)
- **Gerado:** 2026-07-18T19:59:09
- **Estado global:** ❌ EXISTEM ASSERÇÕES FALHADAS

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido tem ili_offset e glosa mapeada ao eixo. | FAIL ❌ | glosa não-ancorada/incompleta: ['ili-30-14818238-n'] |
| Etapa 1 | Nenhum synset off-axis (exclude) figura na lista branca admitida. | PASS ✅ | OK |
| Etapa 1 | A lista branca é persistida por offset ILI e os offsets são únicos. | PASS ✅ | OK |
| ILI | Nenhum id oewn-/por- é usado como chave de junção; a chave é o ILI. | PASS ✅ | OK |
| ILI | Synsets sem ili_offset são sinalizados (não descartados em silêncio). | PASS ✅ | nenhum synset sem ILI no export |
| Etapa 2 | Os sinónimos colhidos provêm exclusivamente de synsets admitidos. | PASS ✅ | OK |
| Etapa 3 | Alvos de relação são tipados pelo mapeamento; «(no lemma)» nunca admitido. | PASS ✅ | OK (267 alvos «(no lemma)» descartados) |
| Etapa 4 | «(no lemma)», colocações e termos só de relação não-nomeada (sem corroboração) são excluídos. | PASS ✅ | OK |
| Etapa 5 | Cada admitido tem estatuto∈{UF,RT,contraste,BT,NT,atributo}, teste decisivo e ≥1 garantia; nomes de qualidade em attribute_bucket. | PASS ✅ | OK |
| Garantia | Termos com garantia «estipulativa» têm definição E relação estrutural. | PASS ✅ | OK |
| Consistência | Nenhum termo é UF de duas classes com owl:disjointWith entre si. | PASS ✅ | OK |
| Consistência | Contrastantes não são serializados como skos:related. | PASS ✅ | OK |
| Serialização | X.skos.ttl analisa com rdflib e tem a contagem de triplos esperada. | PASS ✅ | triplos esperados=4, analisados=4 |

## Etapa 1 — Selecção de acepções (lista branca ILI)
- **UF** `ili-30-14818238-n` — (Química) uma substância formada por união química de duas ou mais elementos ou ingredientes na proporção definida por peso

- Excluídos (off-axis): `['ili-30-02424254-a', 'ili-30-09947232-n']`

## Etapa 2 — Sementes (sinónimos de synsets admitidos)
Total: **1** — composto

## Etapa 3 — Colheita de relações tipadas
- **Contraste (antonym):** —
- **RT/UF (similar-to):** —
- **BT (hypernym):** —
- **NT (hyponym):** azida, base, cianamida, cloreto, complexo, conservante, formulação, fórmula, hidrato, hidróxido, nitrato, nitreto, preparação, quinona, sal, ácido, óxido
- **Atributo:** —
- **Família derivada:** compor
- Alvos «(no lemma)» descartados: 267

### Sinalização (revisão humana — NÃO admitidos)
- acetilação — relação não-nomeada / #NN (via «relation #61»)
- ácido — relação não-nomeada / #NN (via «relation #61»)
- álcool — relação não-nomeada / #NN (via «relation #61»)
- alizarina — relação não-nomeada / #NN (via «relation #61»)
- aminotransferase — relação não-nomeada / #NN (via «relation #61»)
- azida — relação não-nomeada / #NN (via «relation #61»)
- base — relação não-nomeada / #NN (via «relation #61»)
- capsaicina — relação não-nomeada / #NN (via «relation #61»)
- cianamida — relação não-nomeada / #NN (via «relation #61»)
- cíclico — relação não-nomeada / #NN (via «relation #61»)
- cloreto — relação não-nomeada / #NN (via «relation #61»)
- complexo — relação não-nomeada / #NN (via «relation #61»)
- compor — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- conservante — relação não-nomeada / #NN (via «relation #61»)
- constituir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- descarboxilação — relação não-nomeada / #NN (via «relation #61»)
- dimensão — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- elemento — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- fazer — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- formar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- glicosídeos — relação não-nomeada / #NN (via «relation #61»)
- hidrato — relação não-nomeada / #NN (via «relation #61»)
- hidróxido — relação não-nomeada / #NN (via «relation #61»)
- ingrediente — relação não-nomeada / #NN (via «relation #61»)
- inorganicamente — relação não-nomeada / #NN (via «relation #61»)
- isomerização — relação não-nomeada / #NN (via «relation #61»)
- molécula — relação não-nomeada / #NN (via «relation #61»)
- nitrato — relação não-nomeada / #NN (via «relation #61»)
- nitreto — relação não-nomeada / #NN (via «relation #61»)
- organicamente — relação não-nomeada / #NN (via «relation #61»)
- orgânico — relação não-nomeada / #NN (via «relation #61»)
- óxido — relação não-nomeada / #NN (via «relation #61»)
- peso — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- proporção — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- química — relação não-nomeada / #NN (via «domain topic»)
- quinona — relação não-nomeada / #NN (via «relation #61»)
- sal — relação não-nomeada / #NN (via «relation #61»)
- síntese — relação não-nomeada / #NN (via «relation #61»)

## Etapa 4 — Exclusão automática
Nenhum termo descartado.

## Etapa 5 — Adjudicação + §7 proveniência
Admitidos: **0**  ·  Pendentes: **18**  ·  Atributos: **0**

| termo | estatuto | via | offset/ILI | teste decisivo | garantia | definição |
|-------|----------|-----|------------|----------------|----------|-----------|

### Pendentes (necessitam de decisão na spec `adjudication`)
azida, base, cianamida, cloreto, complexo, composto, conservante, formulação, fórmula, hidrato, hidróxido, nitrato, nitreto, preparação, quinona, sal, ácido, óxido

## §6 — Mapeamento SKOS-XL / OWL
- `skos:prefLabel` → **TexturaCompósita**
- `skosxl:altLabel` (UF) → —
- `skos:related` (RT) → —
- `skos:broader` (BT) → —
- `skos:narrower` (NT) → —
- `:temAtributo` (nomes de qualidade) → —
- `:contrastaCom` + `scopeNote` (contraste) → —

_Nomes de qualidade NÃO são `skosxl:altLabel`; contrastantes NÃO são `skos:related` (o SKOS não modela antonímia)._
