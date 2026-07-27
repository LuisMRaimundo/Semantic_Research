# Fase 0 (PULO / WordNet.PT) — **TexturaDensa** (`TexturaDensa`)

- **Eixo definidor:** densidade
- **Fonte:** PULO / WordNet.PT export (âncora ILI; sem porta estatística)
- **Gerado:** 2026-07-27T10:52:45
- **Estado global:** ❌ EXISTEM ASSERÇÕES FALHADAS

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido tem ili_offset e glosa mapeada ao eixo. | FAIL ❌ | glosa não-ancorada/incompleta: ['ili-30-00539009-a', 'ili-30-01513776-a', 'ili-30-02416390-a', 'ili-30-04941453-n'] |
| Etapa 1 | Nenhum synset off-axis (exclude) figura na lista branca admitida. | PASS ✅ | OK |
| Etapa 1 | A lista branca é persistida por offset ILI e os offsets são únicos. | PASS ✅ | OK |
| ILI | Nenhum id oewn-/por- é usado como chave de junção; a chave é o ILI. | PASS ✅ | OK |
| ILI | Synsets sem ili_offset são sinalizados (não descartados em silêncio). | PASS ✅ | nenhum synset sem ILI no export |
| Etapa 2 | Os sinónimos colhidos provêm exclusivamente de synsets admitidos. | PASS ✅ | OK |
| Etapa 3 | Alvos de relação são tipados pelo mapeamento; «(no lemma)» nunca admitido. | PASS ✅ | OK (80 alvos «(no lemma)» descartados) |
| Etapa 4 | «(no lemma)», colocações e termos só de relação não-nomeada (sem corroboração) são excluídos. | PASS ✅ | OK |
| Etapa 5 | Cada admitido tem estatuto∈{UF,RT,BT,NT} (garantia calculada a jusante; atributo = evidência). | PASS ✅ | OK |
| Garantia | Termos com garantia «estipulativa» têm definição E relação estrutural. | PASS ✅ | OK |
| Consistência | Nenhum termo é UF de duas classes com owl:disjointWith entre si. | PASS ✅ | OK |
| Consistência | Nenhum estatuto de evidência (contraste/atributo) em admitidos. | PASS ✅ | OK |
| Serialização | X.skos.ttl analisa com rdflib e tem a contagem de triplos esperada. | PASS ✅ | triplos esperados=9, analisados=9 |

## Etapa 1 — Selecção de acepções (lista branca ILI)
- **UF** `ili-30-00539009-a` — tendo componentes de perto amontoados

- **UF** `ili-30-01185264-a` — com alta densidade relativa ou gravidade específica

- **UF** `ili-30-01513776-a` — (das Trevas) muito intensa

- **RT** `ili-30-01771839-a` — difícil porque passam através do crescimento denso

- **UF** `ili-30-02416390-a` — permitindo pouco se toda a luz passar por causa da espessura da matéria

- **UF** `ili-30-04941453-n` — o valor por unidade de tamanho

- **RT** `ili-30-05088804-n` — a propriedade espacial de sendo amontoados

- Excluídos (off-axis): `['ili-30-00016135-a']`

## Etapa 2 — Sementes (sinónimos de synsets admitidos)
Total: **3** — concentração, densidade, denso

## Etapa 3 — Colheita de relações tipadas
- **Contraste (antonym):** —
- **RT/UF (similar-to):** —
- **BT (hypernym):** —
- **NT (hyponym):** absorvância
- **Atributo:** —
- **Família derivada:** denso
- Alvos «(no lemma)» descartados: 80

### Sinalização (revisão humana — NÃO admitidos)
- calibre — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- concentração — relação não-nomeada / #NN (via «relation #61»)
- denso — relação não-nomeada / #NN (via «relation #61»)
- dimensão — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- formato — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- gás — relação não-nomeada / #NN (via «relation #61»)
- hipogamaglobulinemia — relação não-nomeada / #NN (via «relation #61»)
- ligeiro — relação não-nomeada / #NN (via «relation #61»)
- medida — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- meter — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- tamanho — relação não-nomeada / #NN (via «relation #61 (inverse)»)

## Etapa 4 — Exclusão automática
Nenhum termo descartado.

## Etapa 5 — Adjudicação + §7 proveniência
Admitidos: **3**  ·  Pendentes: **1**  ·  (atributo/oposicao/vizinha = evidência, fora de provenance)

| termo | estatuto | via | offset/ILI | teste decisivo | garantia | definição |
|-------|----------|-----|------------|----------------|----------|-----------|
| denso | UF | derivationally related form | ili-30-00539009-a, ili-30-01185264-a, ili-30-01513776-a, ili-30-01771839-a, ili-30-02416390-a | derivado do sentido (PASSO 3) | sense_decision | — |
| densidade | UF | seed (Etapa 1/2) | ili-30-04941453-n, ili-30-05088804-n | derivado do sentido (PASSO 3) | sense_decision | — |
| concentração | RT | seed (Etapa 1/2) | ili-30-05088804-n | derivado do sentido (PASSO 3) | sense_decision | — |

### Pendentes (necessitam de decisão na spec `adjudication`)
absorvância

## §6 — Mapeamento SKOS-XL / OWL (só Bloco A)
- `skos:prefLabel` → **TexturaDensa**
- `skosxl:altLabel` (UF) → densidade, denso
- `:termoRelacionado` (RT) → concentração
- `skos:broader` (BT) → —
- `skos:narrower` (NT) → —

_Evidência (`atributo`, oposição, vizinha, sinalização) NÃO é serializada como relação SKOS/SKOS-XL._
