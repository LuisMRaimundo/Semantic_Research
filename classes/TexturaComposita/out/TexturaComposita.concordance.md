# LexWarrant — concordância cruzada (**TexturaComposita**)

- **Política de divergência:** conservative
- **Fontes:** PULO, OWN-PT, WordNet  (colunas: ONTO, PULO, OWN-PT, WordNet)
- **Tabela legada OEWN↔PULO** (`legacy_equivalence`): não carregada (junção runtime usa CILI oficial quando ambas as fontes partilham ``i…``; isto não significa que os identificadores CILI estejam indisponíveis).
- **Junções interfontes:** nenhuma — 0 item(ns) da matriz provenientes exclusivamente de uma única fonte (identificadores CILI normalizados na coluna ILI não implicam junção OEWN↔PULO).
- **WordNet/OEWN:** disponível/consultada, sem formas portuguesas admitidas na matriz (`source_contributed_results=false`)
- **Onto.PT:** discovery-only — queried=False; discovery_evidence=False; concordance_results=false (não admite na matriz LexWarrant)
- **Gerado:** 2026-07-31T03:57:06
- **Descartados (só pendentes):** 0 (termos ainda por adjudicar; contados, não listados)
- **Asserções:** 13/13 PASS ✅

> Esta etapa **relata**; não admite nem reclassifica. `proposta_final` é uma sugestão para adjudicação humana, nunca uma auto-admissão.

## Matriz de concordância

| termo | ili | ONTO | PULO | OWN-PT | WordNet | join | veredicto | proposta | notas |
|---|---|---|---|---|---|---|---|---|---|

## Resumo por veredicto


## Cobertura da recolha automática de contraste (R6)

_Verificação apenas — a lógica de recolha não é alterada nesta etapa._

- **OWN-PT:** 0 antónimo(s) auto — antonímia consultável (OEWN)
- **PULO:** 0 antónimo(s) auto — fonte sem antonímia consultável (esperado)
- **WordNet:** 0 antónimo(s) auto — antonímia consultável (OEWN)
- **ILIs ancorados (admitidos) sem material de contraste auto:** —(nenhum ou sem âncoras)
- **Fontes sem antonímia consultável (esperado):** PULO

## Conjunto mais defensável — «convergência plena» (requer junção por ILI)
_(nenhum — nenhuma convergência ancorada em ILI)_

## Convergência (sentido) — PULO admitido + OWN-PT atestado (ILI partilhado)
_Sem estatuto simulado no OWN-PT. Pares PULO↔OWN-PT: `recursos_derivados: PWN`._
_(nenhum)_

## Convergência por termo (acordo de ≥2 fontes, mas sem ILI comum)
_(nenhum)_

## Lista de trabalho humano — divergências
_(nenhuma divergência)_

## Fonte única (aguarda segunda fonte)
_(nenhum)_

## Asserções

| # | Asserção | Resultado | Evidência |
|---|----------|-----------|-----------|
| T1 | Nenhuma junção por termo quando ambos têm ILI (ILI tem precedência). | PASS ✅ | OK |
| T2 | Junção weak(term) só ocorre sem ILI partilhado entre fontes (caso contrário aplicar-se-ia a junção por ILI). | PASS ✅ | 0 conceito(s) weak(term) |
| T3 | Nenhum ILI é fabricado; junção OEWN↔PULO só via CILI; pares sem âncora CILI ficam sem junção ILI (não fabricados). | PASS ✅ | bogus→(None, False); unmapped_flag=False |
| T4 | Cada divergência de estatuto é registada por-fonte (sem colapso em contagem). | PASS ✅ | 0 divergência(s) |
| T5 | Nenhum termo admitido pelos motores é descartado da matriz (PULO; OWN-PT/WordNet corroboram; Onto = descoberta) | PASS ✅ | 0 admitidos / 0 em matriz |
| T6 | WordNet/OEWN: source_available / source_queried / source_contributed_results distintos. | PASS ✅ | source_available=true; source_queried=true; source_contributed_results=false (sem formas PT admitidas na matriz) |
| T7 | proposta_final nunca é um estatuto não suportado; conservador ⇒ null em divergência. | PASS ✅ | OK |
| T8 | Entradas de classes diferentes são recusadas com erro claro. | PASS ✅ | ClassMismatch levantada para classes mistas |
| T10 | «Convergência plena» / «convergência (sentido)» exigem junção por ILI (nunca só weak(term)). | PASS ✅ | OK |
| T10b | Convergência ILI PULO↔OWN-PT marca sempre recursos_derivados:«PWN». | PASS ✅ | OK |
| T11 | Nenhum conceito só-pendente figura como linha da matriz (são contados em «descartados_pendentes»). | PASS ✅ | OK |
| T9 | concordance.json faz round-trip (contagens de term/ili estáveis). | PASS ✅ | 0 conceitos |
| T13 | Nenhuma célula nem proposta_final com valor «contraste» na matriz (migração completa: ver teste unitário de decisions). | PASS ✅ | OK |
| T12 | Nenhum item do bloco de evidência figura no bloco de vocabulário, e vice-versa. | PASS ✅ | blocos A/B disjuntos |
