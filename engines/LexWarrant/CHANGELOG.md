# CHANGELOG — LexWarrant

## [versão a fixar] — 2026-07-13 — Tarefa 1: reticulado de estatutos no veredicto

- `project_status_for_comparison(status)` + tabela declarada `STATUS_COMPAT`:
  a comparação do veredicto passa a usar conjuntos de compatibilidade
  (atributo↔{UF,RT}; BT/NT neutros; UF/RT/contraste eles próprios; contraste
  isolado). Convergência = intersecção não-vazia dos projectados; divergência
  = intersecção vazia. Elimina divergências-artefacto por granularidade
  (PULO=atributo vs ONTO=RT/UF) sem mascarar oposição genuína
  (atributo/UF/RT vs contraste continua divergência).
- O estatuto RICO original permanece intacto na matriz, no JSON e nas colunas
  por-fonte; a projecção alimenta apenas a comparação.
- Auditoria: novo campo `status_projection` por conceito (ex.:
  `{"PULO": "atributo→RT/UF"}`) + nota humana «projecção p/ comparação: …».
- `proposta_final` (conservative) em convergência com brutos distintos propõe
  o estatuto mais específico realmente presente numa fonte (nunca inventado);
  divergência continua ⇒ null.
- T1–T11 sem regressões (16 testes unitários + fusão TexturaUniforme +
  fixtures de divergência genuína: 11/11 PASS).

### Correcção (opção iii) — proposta_final com dupla natureza
- Em convergência projectada com estatutos brutos mistos envolvendo «atributo»
  (ex.: PULO=atributo ∩ ONTO=RT), a proposta continua a ser o estatuto mais
  específico realmente presente, MAS regista-se nota explícita:
  «proposta “RT” com dupla natureza: PULO via “atributo”
  (destino :temAtributo preservado)». Nada é inventado; T1–T11 PASS.

