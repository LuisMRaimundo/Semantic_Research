# Fase 0 (PULO / WordNet.PT) — **uniforme** (`TexturaUniforme`)

- **Eixo definidor:** invariância face a um parâmetro
- **Fonte:** PULO / WordNet.PT export (âncora ILI; sem porta estatística)
- **Gerado:** 2026-08-07T14:10:58
- **Estado global:** ❌ EXISTEM ASSERÇÕES FALHADAS

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido tem ili_offset e glosa mapeada ao eixo. | PASS ✅ | OK |
| Etapa 1 | Nenhum synset off-axis (exclude) figura na lista branca admitida. | PASS ✅ | OK |
| Etapa 1 | A lista branca é persistida por offset ILI e os offsets são únicos. | PASS ✅ | OK |
| ILI | Nenhum id oewn-/por- é usado como chave de junção; a chave é o ILI. | FAIL ❌ | offsets não-ILI na lista branca: ['pwn30-01200095-a', 'pwn30-01966488-a'] |
| ILI | Synsets sem ili_offset são sinalizados (não descartados em silêncio). | PASS ✅ | nenhum synset sem ILI no export |
| Etapa 2 | Os sinónimos colhidos provêm exclusivamente de synsets admitidos. | PASS ✅ | OK |
| Etapa 3 | Alvos de relação são tipados pelo mapeamento; «(no lemma)» nunca admitido. | PASS ✅ | OK (35 alvos «(no lemma)» descartados) |
| Etapa 4 | «(no lemma)», colocações e termos só de relação não-nomeada (sem corroboração) são excluídos. | PASS ✅ | OK |
| Etapa 5 | Cada admitido tem estatuto∈{UF,RT,BT,NT} (garantia calculada a jusante; atributo = evidência). | PASS ✅ | OK |
| Garantia | Termos com garantia «estipulativa» têm definição E relação estrutural. | PASS ✅ | OK |
| Consistência | Nenhum termo é UF de duas classes com owl:disjointWith entre si. | PASS ✅ | OK |
| Consistência | Nenhum estatuto de evidência (contraste/atributo) em admitidos. | PASS ✅ | OK |
| Serialização | X.skos.ttl analisa com rdflib e tem a contagem de triplos esperada. | PASS ✅ | triplos esperados=12, analisados=12 |

## Etapa 1 — Selecção de acepções (lista branca ILI)
- **UF** `pwn30-01200095-a` — que se mantém o mesmo; constante e invariável ao longo do parâmetro
- **UF** `pwn30-01966488-a` — sempre o mesmo parâmetro; imutável e uniforme
- **RT** `ili-30-04745370-n` — ausência de variação; invariância e uniformidade de um parâmetro
- Excluídos (off-axis): `['pwn30-00909545-a', 'pwn30-02302187-a', 'pwn30-00910101-a', 'pwn30-04509592-n', 'pwn30-00744506-a', 'por-30-99999999-x']`

## Etapa 2 — Sementes (sinónimos de synsets admitidos)
Total: **8** — coerente, constante, imutável, invariável, invariância, periódico, uniforme, uniformidade

## Etapa 3 — Colheita de relações tipadas
- **Contraste (antonym):** —
- **RT/UF (similar-to):** homogéneo
- **BT (hypernym):** afinidade, analogia, conformidade, imagem, parecença, parentesco, semelhança, similitude
- **NT (hyponym):** —
- **Atributo:** —
- **Família derivada:** coerente, uniforme, uniformidade
- Alvos «(no lemma)» descartados: 35

### Sinalização (revisão humana — NÃO admitidos)
- afetar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- afigurar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- ainda — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- apresentar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- assumir — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- badalar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- carecer — relação não-nomeada / #NN (via «relation #61 (inverse)»)
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
- diversidade — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- divulgar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- empatar — relação não-nomeada / #NN (via «relation #61»)
- ensinar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- equiparar — relação não-nomeada / #NN (via «relation #61»)
- espécie — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- estampar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
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
- igualar — relação não-nomeada / #NN (via «relation #61»)
- inércia — relação não-nomeada / #NN (via «relation #61»)
- manifestar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- manquejar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- mostrar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- nação — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- nível — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- nivelação — relação não-nomeada / #NN (via «relation #61»)
- nivelamento — relação não-nomeada / #NN (via «relation #61»)
- nivelar — relação não-nomeada / #NN (via «relation #61»)
- patentear — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- ponto — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- qualidade — relação não-nomeada / #NN (via «relation #61 (inverse)»)
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
- variação — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- variedade — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- vestir — relação não-nomeada / #NN (via «relation #61 (inverse)»)

## Etapa 4 — Exclusão automática
Nenhum termo descartado.

## Etapa 5 — Adjudicação + §7 proveniência
Admitidos: **7**  ·  Pendentes: **10**  ·  (atributo/oposicao/vizinha = evidência, fora de provenance)

| termo | estatuto | via | offset/ILI | teste decisivo | garantia | definição |
|-------|----------|-----|------------|----------------|----------|-----------|
| uniforme | UF | derivationally related form | pwn30-01200095-a, pwn30-01966488-a | derivado do sentido (PASSO 3) | sense_decision | — |
| constante | UF | seed (Etapa 1/2) | pwn30-01200095-a | derivado do sentido (PASSO 3) | sense_decision | — |
| invariável | UF | seed (Etapa 1/2) | pwn30-01200095-a | derivado do sentido (PASSO 3) | sense_decision | — |
| imutável | UF | seed (Etapa 1/2) | pwn30-01966488-a | derivado do sentido (PASSO 3) | sense_decision | — |
| uniformidade | RT | derivationally related form | ili-30-04745370-n | derivado do sentido (PASSO 3) | sense_decision | — |
| invariância | RT | seed (Etapa 1/2) | ili-30-04745370-n | derivado do sentido (PASSO 3) | sense_decision | — |
| periódico | RT | seed (Etapa 1/2) | ili-30-04745370-n | derivado do sentido (PASSO 3) | sense_decision | — |

### Pendentes (necessitam de decisão na spec `adjudication`)
afinidade, analogia, coerente, conformidade, homogéneo, imagem, parecença, parentesco, semelhança, similitude

## §6 — Mapeamento SKOS / OWL (só Bloco A)
- `skos:prefLabel` → **uniforme**
- `skos:altLabel` (UF) → constante, imutável, invariável, uniforme
- `:termoRelacionado` (RT) → invariância, periódico, uniformidade
- `skos:broader` (BT) → —
- `skos:narrower` (NT) → —

_Evidência (`atributo`, oposição, vizinha, sinalização) NÃO é serializada como relação SKOS._
