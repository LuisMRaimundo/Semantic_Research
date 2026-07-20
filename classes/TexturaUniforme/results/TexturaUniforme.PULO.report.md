# Fase 0 (PULO / WordNet.PT) — **uniforme** (`TexturaUniforme`)

- **Eixo definidor:** invariância face a um parâmetro
- **Fonte:** PULO / WordNet.PT export (âncora ILI; sem porta estatística)
- **Gerado:** 2026-07-20T16:51:20
- **Estado global:** ✅ TODAS AS ASSERÇÕES PASSARAM

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido tem ili_offset e glosa mapeada ao eixo. | PASS ✅ | OK |
| Etapa 1 | Nenhum synset off-axis (exclude) figura na lista branca admitida. | PASS ✅ | OK |
| Etapa 1 | A lista branca é persistida por offset ILI e os offsets são únicos. | PASS ✅ | OK |
| ILI | Nenhum id oewn-/por- é usado como chave de junção; a chave é o ILI. | PASS ✅ | OK |
| ILI | Synsets sem ili_offset são sinalizados (não descartados em silêncio). | PASS ✅ | nenhum synset sem ILI no export |
| Etapa 2 | Os sinónimos colhidos provêm exclusivamente de synsets admitidos. | PASS ✅ | OK |
| Etapa 3 | Alvos de relação são tipados pelo mapeamento; «(no lemma)» nunca admitido. | PASS ✅ | OK (23 alvos «(no lemma)» descartados) |
| Etapa 4 | «(no lemma)», colocações e termos só de relação não-nomeada (sem corroboração) são excluídos. | PASS ✅ | OK |
| Etapa 5 | Cada admitido tem estatuto∈{UF,RT,contraste,BT,NT,atributo}, teste decisivo e ≥1 garantia; nomes de qualidade em attribute_bucket. | PASS ✅ | OK |
| Garantia | Termos com garantia «estipulativa» têm definição E relação estrutural. | PASS ✅ | OK |
| Consistência | Nenhum termo é UF de duas classes com owl:disjointWith entre si. | PASS ✅ | OK |
| Consistência | Contrastantes não são serializados como skos:related. | PASS ✅ | OK |
| Serialização | X.skos.ttl analisa com rdflib e tem a contagem de triplos esperada. | PASS ✅ | triplos esperados=7, analisados=7 |

## Etapa 1 — Selecção de acepções (lista branca ILI)
- **UF** `ili-30-01200095-a` — que se mantém o mesmo; constante e invariável ao longo do parâmetro
- **UF** `ili-30-01966488-a` — sempre o mesmo parâmetro; imutável e uniforme
- Excluídos (off-axis): `['ili-30-00909545-a', 'ili-30-04745370-n', 'ili-30-02302187-a', 'ili-30-00910101-a', 'ili-30-04509592-n', 'ili-30-00744506-a', None]`

## Etapa 2 — Sementes (sinónimos de synsets admitidos)
Total: **2** — coerente, uniforme

## Etapa 3 — Colheita de relações tipadas
- **Contraste (antonym):** —
- **RT/UF (similar-to):** homogéneo
- **BT (hypernym):** —
- **NT (hyponym):** —
- **Atributo:** —
- **Família derivada:** uniformidade
- Alvos «(no lemma)» descartados: 23

### Sinalização (revisão humana — NÃO admitidos)
- afetar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- afigurar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- apresentar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- assumir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- badalar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- casta — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- classe — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- comparar — relação não-nomeada / #NN (via «relation #61»)
- compensar — relação não-nomeada / #NN (via «relation #61»)
- composição — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- condição — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- constituição — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- descobrir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- desenfardar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- desfraldar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- desinternar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- divulgar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- empatar — relação não-nomeada / #NN (via «relation #61»)
- ensinar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- equiparar — relação não-nomeada / #NN (via «relation #61»)
- espécie — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- estampar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- estrutura — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- estruturação — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- exibir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- existência — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- expandir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- exteriorizar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- fazer ver — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- forma — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- franquear — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- género — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- homogéneo — relação não-nomeada / #NN (via «see also»)
- igualar — relação não-nomeada / #NN (via «relation #61»)
- inércia — relação não-nomeada / #NN (via «relation #61»)
- manifestar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- mostrar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- nação — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- nivelação — relação não-nomeada / #NN (via «relation #61»)
- nivelamento — relação não-nomeada / #NN (via «relation #61»)
- nivelar — relação não-nomeada / #NN (via «relation #61»)
- patentear — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- raça — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- representar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- reproduzir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- revelar-se — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- revestir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- simulacro — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- simular — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- soltar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- sorte — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- suar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- tipo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- vestir — relação não-nomeada / #NN (via «relation #61 (inverse)»)

## Etapa 4 — Exclusão automática
Nenhum termo descartado.

## Etapa 5 — Adjudicação + §7 proveniência
Admitidos: **1**  ·  Pendentes: **2**  ·  Atributos: **0**

| termo | estatuto | via | offset/ILI | teste decisivo | garantia | definição |
|-------|----------|-----|------------|----------------|----------|-----------|
| politípica | contraste | manual (estipulativa) | — | Teste 3 | estipulativa | textura composta por múltiplos tipos simultâneos |

### Pendentes (necessitam de decisão na spec `adjudication`)
coerente, homogéneo

## §6 — Mapeamento SKOS-XL / OWL
- `skos:prefLabel` → **uniforme**
- `skosxl:altLabel` (UF) → —
- `skos:related` (RT) → —
- `skos:broader` (BT) → —
- `skos:narrower` (NT) → —
- `:temAtributo` (nomes de qualidade) → —
- `:contrastaCom` + `scopeNote` (contraste) → politípica

_Nomes de qualidade NÃO são `skosxl:altLabel`; contrastantes NÃO são `skos:related` (o SKOS não modela antonímia)._
