# Fase 0 (PULO / WordNet.PT) — **textura compósita** (`TexturaComposita`)

- **Eixo definidor:** heterogeneidade / composição de materiais ou partes distintas
- **Fonte:** PULO / WordNet.PT export (âncora ILI; sem porta estatística)
- **Gerado:** 2026-07-31T04:21:26
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
| Etapa 3 | Alvos de relação são tipados pelo mapeamento; «(no lemma)» nunca admitido. | PASS ✅ | OK (0 alvos «(no lemma)» descartados) |
| Etapa 4 | «(no lemma)», colocações e termos só de relação não-nomeada (sem corroboração) são excluídos. | PASS ✅ | OK |
| Etapa 5 | Cada admitido tem estatuto∈{UF,RT,BT,NT} (garantia calculada a jusante; atributo = evidência). | PASS ✅ | OK |
| Garantia | Termos com garantia «estipulativa» têm definição E relação estrutural. | PASS ✅ | OK |
| Consistência | Nenhum termo é UF de duas classes com owl:disjointWith entre si. | PASS ✅ | OK |
| Consistência | Nenhum estatuto de evidência (contraste/atributo) em admitidos. | PASS ✅ | OK |
| Serialização | X.skos.ttl analisa com rdflib e tem a contagem de triplos esperada. | PASS ✅ | triplos esperados=4, analisados=4 |

## Etapa 1 — Selecção de acepções (lista branca ILI)
- Excluídos (off-axis): `['ili-30-14818238-n', 'ili-30-02424254-a', 'ili-30-09947232-n', 'ili-30-00237078-n', 'ili-30-00378985-n', 'ili-30-04341686-n', 'ili-30-06788785-n', 'ili-30-00929718-n', 'ili-30-00939452-n', 'ili-30-03081660-n', 'ili-30-04933544-n', 'ili-30-05076472-n', 'ili-30-07037465-n', 'ili-30-14588492-n', 'ili-30-07331400-n', 'ili-30-11444643-n', 'ili-30-00576680-a', 'ili-30-01754421-a', 'ili-30-00583239-a', 'ili-30-00592222-a', 'ili-30-00595299-a', 'ili-30-00595863-a', 'ili-30-00754393-a', 'ili-30-01990653-a', 'ili-30-02506029-a', 'ili-30-00959244-a', 'ili-30-13585429-n', 'ili-30-05858936-n']`

## Etapa 2 — Sementes (sinónimos de synsets admitidos)
Total: **0** — 

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
Admitidos: **0**  ·  Pendentes: **0**  ·  (atributo/oposicao/vizinha = evidência, fora de provenance)

| termo | estatuto | via | offset/ILI | teste decisivo | garantia | definição |
|-------|----------|-----|------------|----------------|----------|-----------|

## §6 — Mapeamento SKOS / OWL (só Bloco A)
- `skos:prefLabel` → **textura compósita**
- `skos:altLabel` (UF) → —
- `:termoRelacionado` (RT) → —
- `skos:broader` (BT) → —
- `skos:narrower` (NT) → —

_Evidência (`atributo`, oposição, vizinha, sinalização) NÃO é serializada como relação SKOS._
