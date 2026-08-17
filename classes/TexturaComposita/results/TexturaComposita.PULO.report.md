# Fase 0 (PULO / WordNet.PT) — **textura compósita** (`TexturaComposita`)

- **Eixo definidor:** heterogeneidade / composição de materiais ou partes distintas
- **Fonte:** PULO / WordNet.PT export (âncora ILI; sem porta estatística)
- **Gerado:** 2026-08-17T06:35:15
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
| Etapa 3 | Alvos de relação são tipados pelo mapeamento; «(no lemma)» nunca admitido. | PASS ✅ | OK (192 alvos «(no lemma)» descartados) |
| Etapa 4 | «(no lemma)», colocações e termos só de relação não-nomeada (sem corroboração) são excluídos. | PASS ✅ | OK |
| Etapa 5 | Cada admitido tem estatuto∈{UF,RT,BT,NT} (garantia calculada a jusante; atributo = evidência). | PASS ✅ | OK |
| Garantia | Termos com garantia «estipulativa» têm definição E relação estrutural. | PASS ✅ | OK |
| Consistência | Nenhum termo é UF de duas classes com owl:disjointWith entre si. | PASS ✅ | OK |
| Consistência | Nenhum estatuto de evidência (contraste/atributo) em admitidos. | PASS ✅ | OK |
| Serialização | X.skos.ttl analisa com rdflib e tem a contagem de triplos esperada. | PASS ✅ | triplos esperados=10, analisados=10 |

## Etapa 1 — Selecção de acepções (lista branca ILI)
- **RT** `ili-30-04341686-n` — uma coisa construída; uma entidade complexa construída de muitas partes

- **RT** `ili-30-03081660-n` — algo que é criado por providenciar várias coisas de modo a formar um todo unificado

- **RT** `ili-30-04933544-n` — a maneira em que alguém ou alguma coisa é composto

- **RT** `ili-30-05076472-n` — a propriedade espacial resultante do acordo das partes em relação às outras e a toda

- Excluídos (off-axis): `['ili-30-14818238-n', 'ili-30-02424254-a', 'ili-30-09947232-n', 'ili-30-00237078-n', 'ili-30-00378985-n', 'ili-30-06788785-n', 'ili-30-00929718-n', 'ili-30-00939452-n', 'ili-30-06409752-n', 'ili-30-07037465-n', 'ili-30-14588492-n', 'ili-30-07331400-n', 'ili-30-11444643-n', 'ili-30-00576680-a', 'ili-30-01754421-a', 'ili-30-00583239-a', 'ili-30-00592222-a', 'ili-30-00594413-a', 'ili-30-00595299-a', 'ili-30-00595863-a', 'ili-30-00754393-a', 'ili-30-01990653-a', 'ili-30-02301560-a', 'ili-30-02506029-a', 'ili-30-00959244-a', 'ili-30-13585429-n', 'ili-30-05858936-n', 'pwn30-01199083-a']`

## Etapa 2 — Sementes (sinónimos de synsets admitidos)
Total: **6** — composição, constituição, construção, contextura, edifício, estrutura

## Etapa 3 — Colheita de relações tipadas
- **Contraste (antonym):** —
- **RT/UF (similar-to):** —
- **BT (hypernym):** artefacto, artefato, criação, propriedade
- **NT (hyponym):** abrigo, altar, andar, arco, asilo, casco, coluna, complexo, defesa, edifício, equilíbrio, estabelecimento, estrutura, estruturação, estádio, fonte, imóvel, monumento, piso, planta, ponte, prédio, refúgio, superstrutura, torre, zona, área
- **Atributo:** —
- **Família derivada:** compor, constitucional, constituir, corresponder a, denotar, fazer, formar, representar, ser, significar
- Alvos «(no lemma)» descartados: 192

### Sinalização (revisão humana — NÃO admitidos)
- abrigo — relação não-nomeada / #NN (via «relation #61»)
- abrir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- alicerce — relação não-nomeada / #NN (via «relation #61»)
- alma — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- altar — relação não-nomeada / #NN (via «relation #61»)
- andar — relação não-nomeada / #NN (via «relation #61»)
- arco — relação não-nomeada / #NN (via «relation #61»)
- área — relação não-nomeada / #NN (via «relation #61»)
- armação — relação não-nomeada / #NN (via «relation #61»)
- armadura — relação não-nomeada / #NN (via «relation #61»)
- arranjar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- arsenal — relação não-nomeada / #NN (via «relation #61»)
- asilo — relação não-nomeada / #NN (via «relation #61»)
- barreira — relação não-nomeada / #NN (via «relation #61»)
- base — relação não-nomeada / #NN (via «relation #61»)
- cave — relação não-nomeada / #NN (via «relation #61»)
- cena — relação não-nomeada / #NN (via «relation #61»)
- cenário — relação não-nomeada / #NN (via «relation #61»)
- cidadão — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- coerente — relação não-nomeada / #NN (via «relation #61»)
- coisa — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- colocar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- coluna — relação não-nomeada / #NN (via «relation #61»)
- complexo — relação não-nomeada / #NN (via «relation #61»)
- compor — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- conjunto — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- constitucional — relação não-nomeada / #NN (via «relation #61»)
- constituição — relação não-nomeada / #NN (via «relation #61»)
- constituinte — relação não-nomeada / #NN (via «relation #61»)
- constituir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- constitutivo — relação não-nomeada / #NN (via «relation #61»)
- corpo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- criar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- defesa — relação não-nomeada / #NN (via «relation #61»)
- dique — relação não-nomeada / #NN (via «relation #61»)
- eclesiologia — relação não-nomeada / #NN (via «relation #61»)
- edifício — relação não-nomeada / #NN (via «relation #61»)
- elemento — relação não-nomeada / #NN (via «relation #61»)
- entidade — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- equipamento — relação não-nomeada / #NN (via «relation #61»)
- estabelecimento — relação não-nomeada / #NN (via «relation #61»)
- estádio — relação não-nomeada / #NN (via «relation #61»)
- estilo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- estrutura — relação não-nomeada / #NN (via «relation #61»)
- estrutural — relação não-nomeada / #NN (via «relation #61»)
- estruturar — relação não-nomeada / #NN (via «relation #61»)
- falda — relação não-nomeada / #NN (via «relation #61»)
- fazer — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- físico — relação não-nomeada / #NN (via «relation #61»)
- fonte — relação não-nomeada / #NN (via «relation #61»)
- forma — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- formar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- funcional — relação não-nomeada / #NN (via «relation #61»)
- fundamento — relação não-nomeada / #NN (via «relation #61»)
- humano — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- imóvel — relação não-nomeada / #NN (via «relation #61»)
- individualidade — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- indivíduo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- instalação — relação não-nomeada / #NN (via «relation #61»)
- matéria — relação não-nomeada / #NN (via «relation #61»)
- material — relação não-nomeada / #NN (via «relation #61»)
- mecanismo — relação não-nomeada / #NN (via «relation #61»)
- modo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- monumento — relação não-nomeada / #NN (via «relation #61»)
- mortal — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- muro — relação não-nomeada / #NN (via «relation #61»)
- obstáculo — relação não-nomeada / #NN (via «relation #61»)
- orgânico — relação não-nomeada / #NN (via «relation #61»)
- palco — relação não-nomeada / #NN (via «relation #61»)
- parede — relação não-nomeada / #NN (via «relation #61»)
- pé — relação não-nomeada / #NN (via «relation #61»)
- peanha — relação não-nomeada / #NN (via «relation #61»)
- pedestal — relação não-nomeada / #NN (via «relation #61»)
- pessoa — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- pintura — relação não-nomeada / #NN (via «relation #61»)
- piso — relação não-nomeada / #NN (via «relation #61»)
- plano — relação não-nomeada / #NN (via «relation #61»)
- planta — relação não-nomeada / #NN (via «relation #61»)
- ponte — relação não-nomeada / #NN (via «relation #61»)
- prédio — relação não-nomeada / #NN (via «relation #61»)
- produzir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- quadro — relação não-nomeada / #NN (via «relation #61»)
- refúgio — relação não-nomeada / #NN (via «relation #61»)
- resistência — relação não-nomeada / #NN (via «relation #61»)
- rígido — relação não-nomeada / #NN (via «relation #61»)
- sopé — relação não-nomeada / #NN (via «relation #61»)
- sujeito — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- superstrutura — relação não-nomeada / #NN (via «relation #61»)
- todo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- tornar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- torre — relação não-nomeada / #NN (via «relation #61»)
- totalidade — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- tudo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- unidade — relação não-nomeada / #NN (via «relation #61»)
- uniforme — relação não-nomeada / #NN (via «relation #61»)
- zona — relação não-nomeada / #NN (via «relation #61»)

## Etapa 4 — Exclusão automática
Nenhum termo descartado.

## Etapa 5 — Adjudicação + §7 proveniência
Admitidos: **6**  ·  Pendentes: **29**  ·  (atributo/oposicao/vizinha = evidência, fora de provenance)

| termo | estatuto | via | offset/ILI | teste decisivo | garantia | definição |
|-------|----------|-----|------------|----------------|----------|-----------|
| composição | RT | seed (Etapa 1/2) | ili-30-03081660-n, ili-30-04341686-n, ili-30-04933544-n, ili-30-05076472-n | derivado do sentido (PASSO 3) | sense_decision | — |
| contextura | RT | seed (Etapa 1/2) | ili-30-04341686-n | derivado do sentido (PASSO 3) | sense_decision | — |
| edifício | RT | hyponym | ili-30-04341686-n | derivado do sentido (PASSO 3) | sense_decision | — |
| estrutura | RT | hyponym | ili-30-04341686-n | derivado do sentido (PASSO 3) | sense_decision | — |
| construção | RT | seed (Etapa 1/2) | ili-30-04341686-n | derivado do sentido (PASSO 3) | sense_decision | — |
| constituição | RT | seed (Etapa 1/2) | ili-30-04933544-n | derivado do sentido (PASSO 3) | sense_decision | — |

### Pendentes (necessitam de decisão na spec `adjudication`)
abrigo, altar, andar, arco, artefacto, artefato, asilo, casco, coluna, complexo, criação, defesa, equilíbrio, estabelecimento, estruturação, estádio, fonte, imóvel, monumento, piso, planta, ponte, propriedade, prédio, refúgio, superstrutura, torre, zona, área

## §6 — Mapeamento SKOS / OWL (só Bloco A)
- `skos:prefLabel` → **textura compósita**
- `skos:altLabel` (UF) → —
- `:termoRelacionado` (RT) → composição, constituição, construção, contextura, edifício, estrutura
- `skos:broader` (BT) → —
- `skos:narrower` (NT) → —

_Evidência (`atributo`, oposição, vizinha, sinalização) NÃO é serializada como relação SKOS._
