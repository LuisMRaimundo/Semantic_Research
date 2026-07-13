# Fase 0 (PULO / WordNet.PT) — **uniforme** (`TexturaUniforme`)

- **Eixo definidor:** invariância face a um parâmetro
- **Fonte:** PULO / WordNet.PT export (âncora ILI; sem porta estatística)
- **Gerado:** 2026-07-13T12:40:02
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
| Etapa 3 | Alvos de relação são tipados pelo mapeamento; «(no lemma)» nunca admitido. | PASS ✅ | OK (72 alvos «(no lemma)» descartados) |
| Etapa 4 | «(no lemma)», colocações e termos só de relação não-nomeada (sem corroboração) são excluídos. | PASS ✅ | OK |
| Etapa 5 | Cada admitido tem estatuto∈{UF,RT,contraste,BT,NT,atributo}, teste decisivo e ≥1 garantia; nomes de qualidade em attribute_bucket. | PASS ✅ | OK |
| Garantia | Termos com garantia «estipulativa» têm definição E relação estrutural. | PASS ✅ | OK |
| Consistência | Nenhum termo é UF de duas classes com owl:disjointWith entre si. | PASS ✅ | OK |
| Consistência | Contrastantes não são serializados como skos:related. | PASS ✅ | OK |
| Serialização | X.skos.ttl analisa com rdflib e tem a contagem de triplos esperada. | PASS ✅ | triplos esperados=14, analisados=14 |

## Etapa 1 — Selecção de acepções (lista branca ILI)
- **UF** `ili-30-01200095-a` — que se mantém o mesmo; constante e invariável ao longo do parâmetro
- **UF** `ili-30-01966488-a` — sempre o mesmo parâmetro; imutável e uniforme
- **UF** `ili-30-00909545-a` — sem variações; regular e uniforme face ao parâmetro
- **UF** `ili-30-04745370-n` — ausência de variação; invariância e uniformidade de um parâmetro
- Excluídos (off-axis): `['ili-30-02302187-a', 'ili-30-00910101-a', 'ili-30-04509592-n', 'ili-30-00744506-a', None]`

## Etapa 2 — Sementes (sinónimos de synsets admitidos)
Total: **5** — coerente, igual, regular, uniforme, uniformidade

## Etapa 3 — Colheita de relações tipadas
- **Contraste (antonym):** desigual, irregular
- **RT/UF (similar-to):** homogéneo
- **BT (hypernym):** afinidade, analogia, conformidade, imagem, parecença, parentesco, semelhança, similitude
- **NT (hyponym):** —
- **Atributo:** igualdade
- **Família derivada:** coerente, uniforme, uniformidade
- Alvos «(no lemma)» descartados: 72

### Sinalização (revisão humana — NÃO admitidos)
- afetar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- afigurar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- ainda — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- altura — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- amachucado — similar-to fora do eixo (glosa) (via «similar to»)
- amarfanhado — similar-to fora do eixo (glosa) (via «similar to»)
- apresentar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- assumir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- badalar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- brando — relação não-nomeada / #NN (via «see also»)
- brilhar — relação não-nomeada / #NN (via «relation #61»)
- carecer — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- casta — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- chã — similar-to fora do eixo (glosa) (via «similar to»)
- chão — similar-to fora do eixo (glosa) (via «similar to»)
- chato — similar-to fora do eixo (glosa) (via «similar to»)
- classe — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- comparar — relação não-nomeada / #NN (via «relation #61»)
- compensar — relação não-nomeada / #NN (via «relation #61»)
- composição — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- condição — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- constante — relação não-nomeada / #NN (via «see also»)
- constituição — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- descobrir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- desenfardar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- desfraldar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- desigual — relação não-nomeada / #NN (via «relation #61»)
- desinternar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- direito — similar-to fora do eixo (glosa) (via «similar to»)
- diversidade — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- divulgar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- empatar — relação não-nomeada / #NN (via «relation #61»)
- ensinar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- equiparar — relação não-nomeada / #NN (via «relation #61»)
- espécie — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- estampar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- estável — relação não-nomeada / #NN (via «see also»)
- estrutura — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- estruturação — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- etapa — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- exibir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- existência — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- expandir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- exteriorizar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- faltar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- fase — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- fazer ver — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- forma — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- franquear — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- género — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- grau — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- homogéneo — relação não-nomeada / #NN (via «see also»)
- igual — similar-to fora do eixo (glosa) (via «similar to»)
- igualar — relação não-nomeada / #NN (via «relation #61»)
- inércia — relação não-nomeada / #NN (via «relation #61»)
- irregular — relação não-nomeada / #NN (via «relation #61»)
- liso — similar-to fora do eixo (glosa) (via «similar to»)
- macio — relação não-nomeada / #NN (via «see also»)
- manifestar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- manquejar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- mostrar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- nação — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- nível — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- nivelação — relação não-nomeada / #NN (via «relation #61»)
- nivelamento — relação não-nomeada / #NN (via «relation #61»)
- nivelar — relação não-nomeada / #NN (via «relation #61»)
- paciente — relação não-nomeada / #NN (via «relation #61»)
- patentear — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- plano — similar-to fora do eixo (glosa) (via «similar to»)
- ponto — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- qualidade — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- raça — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- raso — similar-to fora do eixo (glosa) (via «similar to»)
- regular — similar-to fora do eixo (glosa) (via «similar to»)
- representar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- reproduzir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- reto — similar-to fora do eixo (glosa) (via «similar to»)
- revelar-se — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- revestir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- simulacro — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- simular — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- soltar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- sorte — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- suar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- suave — relação não-nomeada / #NN (via «see also»)
- tipo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- uniforme — similar-to fora do eixo (glosa) (via «similar to»)
- variação — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- variedade — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- vestir — relação não-nomeada / #NN (via «relation #61 (inverse)»)

## Etapa 4 — Exclusão automática
Nenhum termo descartado.

## Etapa 5 — Adjudicação + §7 proveniência
Admitidos: **6**  ·  Pendentes: **9**  ·  Atributos: **3**

| termo | estatuto | via | offset/ILI | teste decisivo | garantia | definição |
|-------|----------|-----|------------|----------------|----------|-----------|
| regular | atributo | seed (Etapa 1/2) | ili-30-00909545-a | Teste 1 falha | lexical | — |
| igual | atributo | seed (Etapa 1/2) | ili-30-00909545-a | Teste 1 falha | lexical | — |
| desigual | contraste | antonym | — | Teste 3 | lexical | — |
| irregular | contraste | antonym | — | Teste 3 | lexical | — |
| igualdade | atributo | attribute | — | Roteado para attribute_bucket (nome de qualidade) | estrutural | — |
| politípica | contraste | manual (estipulativa) | — | Teste 3 | estipulativa | textura composta por múltiplos tipos simultâneos |

### Pendentes (necessitam de decisão na spec `adjudication`)
afinidade, analogia, conformidade, homogéneo, imagem, parecença, parentesco, semelhança, similitude

## §6 — Mapeamento SKOS-XL / OWL
- `skos:prefLabel` → **uniforme**
- `skosxl:altLabel` (UF) → —
- `skos:related` (RT) → —
- `skos:broader` (BT) → —
- `skos:narrower` (NT) → —
- `:temAtributo` (nomes de qualidade) → igual, igualdade, regular
- `:contrastaCom` + `scopeNote` (contraste) → desigual, irregular, politípica

_Nomes de qualidade NÃO são `skosxl:altLabel`; contrastantes NÃO são `skos:related` (o SKOS não modela antonímia)._
