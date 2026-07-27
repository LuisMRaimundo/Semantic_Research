# Fase 0 (PULO / WordNet.PT) — **TexturaCompósita** (`TexturaComposita`)

- **Eixo definidor:** heterogeneidade / composição de materiais ou partes distintas
- **Fonte:** PULO / WordNet.PT export (âncora ILI; sem porta estatística)
- **Gerado:** 2026-07-27T12:39:24
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
| Etapa 3 | Alvos de relação são tipados pelo mapeamento; «(no lemma)» nunca admitido. | PASS ✅ | OK (0 alvos «(no lemma)» descartados) |
| Etapa 4 | «(no lemma)», colocações e termos só de relação não-nomeada (sem corroboração) são excluídos. | PASS ✅ | OK |
| Etapa 5 | Cada admitido tem estatuto∈{UF,RT,BT,NT} (garantia calculada a jusante; atributo = evidência). | PASS ✅ | OK |
| Garantia | Termos com garantia «estipulativa» têm definição E relação estrutural. | PASS ✅ | OK |
| Consistência | Nenhum termo é UF de duas classes com owl:disjointWith entre si. | PASS ✅ | OK |
| Consistência | Nenhum estatuto de evidência (contraste/atributo) em admitidos. | PASS ✅ | OK |
| Serialização | X.skos.ttl analisa com rdflib e tem a contagem de triplos esperada. | PASS ✅ | triplos esperados=6, analisados=6 |

## Etapa 1 — Selecção de acepções (lista branca ILI)
- **UF** `ili-30-14818238-n` — (Química) uma substância formada por união química de duas ou mais elementos ou ingredientes na proporção definida por peso

- Excluídos (off-axis): `['ili-30-02424254-a', 'ili-30-09947232-n']`

## Etapa 2 — Sementes (sinónimos de synsets admitidos)
Total: **1** — composto

## Etapa 3 — Colheita de relações tipadas
- **Contraste (antonym):** —
- **RT/UF (similar-to):** —
- **BT (hypernym):** —
- **NT (hyponym):** —
- **Atributo:** —
- **Família derivada:** —
- Alvos «(no lemma)» descartados: 0

## Etapa 4 — Exclusão automática
Nenhum termo descartado.

## Etapa 5 — Adjudicação + §7 proveniência
Admitidos: **1**  ·  Pendentes: **0**  ·  (atributo/oposicao/vizinha = evidência, fora de provenance)

| termo | estatuto | via | offset/ILI | teste decisivo | garantia | definição |
|-------|----------|-----|------------|----------------|----------|-----------|
| composto | UF | seed (Etapa 1/2) | ili-30-14818238-n | derivado do sentido (PASSO 3) | sense_decision | — |

## §6 — Mapeamento SKOS-XL / OWL (só Bloco A)
- `skos:prefLabel` → **TexturaCompósita**
- `skosxl:altLabel` (UF) → composto
- `:termoRelacionado` (RT) → —
- `skos:broader` (BT) → —
- `skos:narrower` (NT) → —

_Evidência (`atributo`, oposição, vizinha, sinalização) NÃO é serializada como relação SKOS/SKOS-XL._
