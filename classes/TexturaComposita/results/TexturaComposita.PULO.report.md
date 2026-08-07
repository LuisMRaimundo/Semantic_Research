# Fase 0 (PULO / WordNet.PT) — **textura compósita** (`TexturaComposita`)

- **Eixo definidor:** heterogeneidade / composição de materiais ou partes distintas
- **Fonte:** PULO / WordNet.PT export (âncora ILI; sem porta estatística)
- **Gerado:** 2026-08-04T22:45:34
- **Estado global:** ❌ EXISTEM ASSERÇÕES FALHADAS

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido tem ili_offset e glosa mapeada ao eixo. | PASS ✅ | OK |
| Etapa 1 | Nenhum synset off-axis (exclude) figura na lista branca admitida. | PASS ✅ | OK |
| Etapa 1 | A lista branca é persistida por offset ILI e os offsets são únicos. | PASS ✅ | OK |
| ILI | Nenhum id oewn-/por- é usado como chave de junção; a chave é o ILI. | FAIL ❌ | offsets não-ILI na lista branca: ['pwn30-01199083-a'] |
| ILI | Synsets sem ili_offset são sinalizados (não descartados em silêncio). | PASS ✅ | nenhum synset sem ILI no export |
| Etapa 2 | Os sinónimos colhidos provêm exclusivamente de synsets admitidos. | PASS ✅ | OK |
| Etapa 3 | Alvos de relação são tipados pelo mapeamento; «(no lemma)» nunca admitido. | PASS ✅ | OK (43 alvos «(no lemma)» descartados) |
| Etapa 4 | «(no lemma)», colocações e termos só de relação não-nomeada (sem corroboração) são excluídos. | PASS ✅ | OK |
| Etapa 5 | Cada admitido tem estatuto∈{UF,RT,BT,NT} (garantia calculada a jusante; atributo = evidência). | PASS ✅ | OK |
| Garantia | Termos com garantia «estipulativa» têm definição E relação estrutural. | PASS ✅ | OK |
| Consistência | Nenhum termo é UF de duas classes com owl:disjointWith entre si. | PASS ✅ | OK |
| Consistência | Nenhum estatuto de evidência (contraste/atributo) em admitidos. | PASS ✅ | OK |
| Serialização | X.skos.ttl analisa com rdflib e tem a contagem de triplos esperada. | PASS ✅ | triplos esperados=16, analisados=16 |

## Etapa 1 — Selecção de acepções (lista branca ILI)
- **RT** `ili-30-00378985-n` — o ato de combinar as coisas para formar um todo novo

- **RT** `ili-30-03081660-n` — algo que é criado por providenciar várias coisas de modo a formar um todo unificado

- **RT** `ili-30-04933544-n` — a maneira em que alguém ou alguma coisa é composto

- **RT** `pwn30-01199083-a` — que consiste em uma variedade aleatória de diferentes tipos

- Excluídos (off-axis): `['ili-30-14818238-n', 'ili-30-02424254-a', 'ili-30-09947232-n', 'ili-30-00237078-n', 'ili-30-04341686-n', 'ili-30-06788785-n', 'ili-30-00929718-n', 'ili-30-00939452-n', 'ili-30-05076472-n', 'ili-30-06409752-n', 'ili-30-07037465-n', 'ili-30-14588492-n', 'ili-30-07331400-n', 'ili-30-11444643-n', 'ili-30-00576680-a', 'ili-30-01754421-a', 'ili-30-00583239-a', 'ili-30-00592222-a', 'ili-30-00594413-a', 'ili-30-00595299-a', 'ili-30-00595863-a', 'ili-30-00754393-a', 'ili-30-01990653-a', 'ili-30-02301560-a', 'ili-30-02506029-a', 'ili-30-00959244-a', 'ili-30-13585429-n', 'ili-30-05858936-n']`

## Etapa 2 — Sementes (sinónimos de synsets admitidos)
Total: **12** — amalgamado, cabrito, combinação, composição, constituição, diverso, híbrido, mesclado, mestiço, misto, misturado, mulato

## Etapa 3 — Colheita de relações tipadas
- **Contraste (antonym):** —
- **RT/UF (similar-to):** —
- **BT (hypernym):** criação, propriedade
- **NT (hyponym):** consolidação, estrutura, estruturação, fusão, integração, mistura, unificação, união
- **Atributo:** —
- **Família derivada:** agrupar, combinar, compor, constitucional, constituir, corresponder a, denotar, fazer, formar, misturar, representar, ser, significar, unir
- Alvos «(no lemma)» descartados: 43

### Sinalização (revisão humana — NÃO admitidos)
- abrir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- alma — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- arranjar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- associação — relação não-nomeada / #NN (via «relation #61»)
- calcar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- caldear — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- cidadão — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- coerente — relação não-nomeada / #NN (via «relation #61»)
- coisa — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- colocar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- combinar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- compor — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- configurar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- conformar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- conjunto — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- constitucional — relação não-nomeada / #NN (via «relation #61»)
- constituição — relação não-nomeada / #NN (via «relation #61»)
- constituinte — relação não-nomeada / #NN (via «relation #61»)
- constituir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- constitutivo — relação não-nomeada / #NN (via «relation #61»)
- corpo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- criar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- eclesiologia — relação não-nomeada / #NN (via «relation #61»)
- equipamento — relação não-nomeada / #NN (via «relation #61»)
- estilo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- fazer — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- físico — relação não-nomeada / #NN (via «relation #61»)
- forjar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- forma — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- formar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- fusão — relação não-nomeada / #NN (via «relation #61»)
- humano — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- individualidade — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- indivíduo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- inventar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- matéria — relação não-nomeada / #NN (via «relation #61»)
- material — relação não-nomeada / #NN (via «relation #61»)
- modelar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- modo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- moldar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- mortal — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- orgânico — relação não-nomeada / #NN (via «relation #61»)
- pessoa — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- plasmar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- produzir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- resistência — relação não-nomeada / #NN (via «relation #61»)
- sintético — relação não-nomeada / #NN (via «relation #61»)
- sujeito — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- todo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- tornar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- totalidade — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- tudo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- unidade — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- uniforme — relação não-nomeada / #NN (via «relation #61»)
- vazar — relação não-nomeada / #NN (via «relation #61 (inverse)»)

## Etapa 4 — Exclusão automática
Nenhum termo descartado.

## Etapa 5 — Adjudicação + §7 proveniência
Admitidos: **12**  ·  Pendentes: **10**  ·  (atributo/oposicao/vizinha = evidência, fora de provenance)

| termo | estatuto | via | offset/ILI | teste decisivo | garantia | definição |
|-------|----------|-----|------------|----------------|----------|-----------|
| combinação | RT | seed (Etapa 1/2) | ili-30-00378985-n | derivado do sentido (PASSO 3) | sense_decision | — |
| composição | RT | seed (Etapa 1/2) | ili-30-00378985-n, ili-30-03081660-n, ili-30-04933544-n | derivado do sentido (PASSO 3) | sense_decision | — |
| constituição | RT | seed (Etapa 1/2) | ili-30-04933544-n | derivado do sentido (PASSO 3) | sense_decision | — |
| amalgamado | RT | seed (Etapa 1/2) | pwn30-01199083-a | derivado do sentido (PASSO 3) | sense_decision | — |
| cabrito | RT | seed (Etapa 1/2) | pwn30-01199083-a | derivado do sentido (PASSO 3) | sense_decision | — |
| diverso | RT | seed (Etapa 1/2) | pwn30-01199083-a | derivado do sentido (PASSO 3) | sense_decision | — |
| híbrido | RT | seed (Etapa 1/2) | pwn30-01199083-a | derivado do sentido (PASSO 3) | sense_decision | — |
| mesclado | RT | seed (Etapa 1/2) | pwn30-01199083-a | derivado do sentido (PASSO 3) | sense_decision | — |
| mestiço | RT | seed (Etapa 1/2) | pwn30-01199083-a | derivado do sentido (PASSO 3) | sense_decision | — |
| misto | RT | seed (Etapa 1/2) | pwn30-01199083-a | derivado do sentido (PASSO 3) | sense_decision | — |
| misturado | RT | seed (Etapa 1/2) | pwn30-01199083-a | derivado do sentido (PASSO 3) | sense_decision | — |
| mulato | RT | seed (Etapa 1/2) | pwn30-01199083-a | derivado do sentido (PASSO 3) | sense_decision | — |

### Pendentes (necessitam de decisão na spec `adjudication`)
consolidação, criação, estrutura, estruturação, fusão, integração, mistura, propriedade, unificação, união

## §6 — Mapeamento SKOS / OWL (só Bloco A)
- `skos:prefLabel` → **textura compósita**
- `skos:altLabel` (UF) → —
- `:termoRelacionado` (RT) → amalgamado, cabrito, combinação, composição, constituição, diverso, híbrido, mesclado, mestiço, misto, misturado, mulato
- `skos:broader` (BT) → —
- `skos:narrower` (NT) → —

_Evidência (`atributo`, oposição, vizinha, sinalização) NÃO é serializada como relação SKOS._
