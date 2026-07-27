# LexWarrant — concordância cruzada (**TexturaUniforme**)

- **Política de divergência:** conservative
- **Fontes:** PULO, OWN-PT, WordNet  (colunas: ONTO, PULO, OWN-PT, WordNet)
- **Junção ILI (CILI automático):** C:\Users\lmr20\Desktop\Semantic_Research\classes\TexturaUniforme\out\ili_equivalence.cili.json  (8 pares CILI; 69 sem âncora partilhada)
- **Gerado:** 2026-07-27T12:39:44
- **Descartados (só pendentes):** 11 (termos ainda por adjudicar; contados, não listados)
- **Asserções:** 13/13 PASS ✅

> Esta etapa **relata**; não admite nem reclassifica. `proposta_final` é uma sugestão para adjudicação humana, nunca uma auto-admissão.

## Matriz de concordância

| termo | ili | ONTO | PULO | OWN-PT | WordNet | join | veredicto | proposta | notas |
|---|---|---|---|---|---|---|---|---|---|
| uniforme | ili-30-01200095-a, ili-30-01966488-a, oewn-ili:i10771 | — | UF | atestado | — | ili | convergência (sentido) 〔recursos_derivados:PWN〕 | UF | recursos_derivados: PWN — concordância entre recursos derivados da mesma estrutura conceptual; não constitui atestação independente do português; junção por ILI via tabela de equivalência: ili-30-01966488-a ↔ oewn-ili:i10771; OWN-PT: atestado OWN-PT [own-pt:1.0.0] via ILI i10771 · oewn-01973553-a |
| constante | ili-30-01200095-a | — | UF | — | — | single | fonte única | UF |  |
| imutável | ili-30-01966488-a | — | UF | — | — | single | fonte única | UF |  |
| invariável | ili-30-01200095-a | — | UF | — | — | single | fonte única | UF |  |
| invariância | ili-30-04745370-n | — | RT | — | — | single | fonte única | RT |  |
| periódico | ili-30-04745370-n | — | RT | — | — | single | fonte única | RT |  |
| uniformidade | ili-30-04745370-n | — | RT | — | — | single | fonte única | RT |  |
| consistent | oewn-ili:i6560 | — | — | — | sinalização | single | sinalização | — | WordNet: atestado na WordNet [en_lemma (sem correspondência own-pt)] · oewn-01203638-s · ILI i6560 |
| dedifferentiated | oewn-ili:i4127 | — | — | — | sinalização | single | sinalização | — | WordNet: vizinho similar_to de i4126 (oewn-00748118-a) — sem estatuto; adjudicação humana |
| differentiated | oewn-ili:i4125 | — | — | — | sinalização | single | sinalização | — | WordNet: material de contraste (antonym) de i4126 (oewn-00748118-a) — sem estatuto; adjudicação humana |
| homogeneous | oewn-ili:i6559 | — | — | — | sinalização | single | sinalização | — | WordNet: vizinho similar_to de i6560 (oewn-01203638-s) — sem estatuto; adjudicação humana |
| homogenous | oewn-ili:i6559 | — | — | — | sinalização | single | sinalização | — | WordNet: vizinho similar_to de i6560 (oewn-01203638-s) — sem estatuto; adjudicação humana |
| invariável | oewn-ili:i10771 | — | — | atestado | — | single | sinalização | — | OWN-PT: atestado OWN-PT [own-pt:1.0.0] via ILI i10771 · oewn-01973553-a |
| multiform | oewn-ili:i10773 | — | — | — | sinalização | single | sinalização | — | WordNet: material de contraste (antonym) de i10771 (oewn-01973553-a) — sem estatuto; adjudicação humana |
| single | oewn-ili:i10772 | — | — | — | sinalização | single | sinalização | — | WordNet: vizinho similar_to de i10771 (oewn-01973553-a) — sem estatuto; adjudicação humana |
| undifferentiated | oewn-ili:i4126 | — | — | — | sinalização | single | sinalização | — | WordNet: atestado na WordNet [en_lemma (sem correspondência own-pt)] · oewn-00748118-a · ILI i4126 |
| uniform | oewn-ili:i4126 | — | — | — | sinalização | single | sinalização | — | WordNet: atestado na WordNet [en_lemma (sem correspondência own-pt)] · oewn-00748118-a · ILI i4126 |

## Resumo por veredicto

- **convergência (sentido):** 1
- **fonte única:** 6
- **sinalização:** 10

## Cobertura da recolha automática de contraste (R6)

_Verificação apenas — a lógica de recolha não é alterada nesta etapa._

- **OWN-PT:** 0 antónimo(s) auto — antonímia consultável (OEWN)
- **PULO:** 0 antónimo(s) auto — fonte sem antonímia consultável (esperado)
- **WordNet:** 2 antónimo(s) auto — antonímia consultável (OEWN)
  - termos: differentiated, multiform
- **ILIs ancorados (admitidos) sem material de contraste auto:** ili-30-01200095-a, ili-30-01966488-a, ili-30-04745370-n
- **Fontes sem antonímia consultável (esperado):** PULO

## Conjunto mais defensável — «convergência plena» (requer junção por ILI)
_(nenhum — nenhuma convergência ancorada em ILI)_

## Convergência (sentido) — PULO admitido + OWN-PT atestado (ILI partilhado)
_Sem estatuto simulado no OWN-PT. Pares PULO↔OWN-PT: `recursos_derivados: PWN`._
uniforme

## Convergência por termo (acordo de ≥2 fontes, mas sem ILI comum)
_(nenhum)_

## Lista de trabalho humano — divergências
_(nenhuma divergência)_

## Fonte única (aguarda segunda fonte)
constante, imutável, invariável, invariância, periódico, uniformidade

## Asserções

| # | Asserção | Resultado | Evidência |
|---|----------|-----------|-----------|
| T1 | Nenhuma junção por termo quando ambos têm ILI (ILI tem precedência). | PASS ✅ | OK |
| T2 | Junção weak(term) só ocorre sem ILI partilhado entre fontes (caso contrário aplicar-se-ia a junção por ILI). | PASS ✅ | 0 conceito(s) weak(term) |
| T3 | Nenhum ILI é fabricado; junção OEWN↔PULO só via CILI; pares sem âncora CILI ficam sem junção ILI (não fabricados). | PASS ✅ | bogus→(None, False); unmapped_flag=False |
| T4 | Cada divergência de estatuto é registada por-fonte (sem colapso em contagem). | PASS ✅ | 0 divergência(s) |
| T5 | Nenhum termo admitido pelos motores é descartado da matriz (PULO; OWN-PT/WordNet corroboram; Onto = descoberta) | PASS ✅ | 7 admitidos / 7 em matriz |
| T6 | Fonte WordNet ausente ⇒ coluna toda «—». | PASS ✅ | WordNet presente — N/A |
| T7 | proposta_final nunca é um estatuto não suportado; conservador ⇒ null em divergência. | PASS ✅ | OK |
| T8 | Entradas de classes diferentes são recusadas com erro claro. | PASS ✅ | ClassMismatch levantada para classes mistas |
| T10 | «Convergência plena» / «convergência (sentido)» exigem junção por ILI (nunca só weak(term)). | PASS ✅ | OK |
| T10b | Convergência ILI PULO↔OWN-PT marca sempre recursos_derivados:«PWN». | PASS ✅ | OK |
| T11 | Nenhum conceito só-pendente figura como linha da matriz (são contados em «descartados_pendentes»). | PASS ✅ | OK |
| T9 | concordance.json faz round-trip (contagens de term/ili estáveis). | PASS ✅ | 17 conceitos |
| T13 | Nenhuma célula nem proposta_final com valor «contraste» na matriz (migração completa: ver teste unitário de decisions). | PASS ✅ | OK |
| T12 | Nenhum item do bloco de evidência figura no bloco de vocabulário, e vice-versa. | PASS ✅ | blocos A/B disjuntos |

# Relatório residual — `TexturaUniforme`

Taxonomia de reconciliação (b1/b2/c1/c2/estipulações) **removida** (Corte 2).

## Acepções adjudicadas sem correspondência em motor

_(nenhuma)_
