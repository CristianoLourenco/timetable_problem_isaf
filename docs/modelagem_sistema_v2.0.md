# Modelagem do Sistema — Índice (ISAF)
> Documento vivo — Capítulo 4.1.3 do TFC.
> Ferramenta de modelação: **Visual Paradigm** (definitivo) + Mermaid (preview GitHub).
> Fonte de verdade: [`analise_requisitos.md`](analise_requisitos.md)

---

## Metodologia

Para cada diagrama: **1) Fundamentar → 2) Aplicar ao ISAF.**
A ordem entre diagramas foi ajustada por prazo (15/07), mas o método interno mantém-se.

---

## Estado dos Diagramas

| # | Diagrama | Ficheiro | Estado |
|---|---|---|---|
| 1 | Diagrama de Contexto | [`diagramas/01_diagrama_contexto.md`](diagramas/01_diagrama_contexto.md) | ✅ VP exportado (PDF entregue) |
| 2 | Diagrama de Casos de Uso | [`diagramas/02_diagrama_casos_uso.md`](diagramas/02_diagrama_casos_uso.md) | ✅ Versão final 15/07 — VP pendente |
| 3 | Especificação Textual dos UCs | [`diagramas/03_especificacao_casos_uso.md`](diagramas/03_especificacao_casos_uso.md) | 🔵 Desactualizado — rever após UC final |
| 4 | Diagrama de Classes | [`diagramas/04_diagrama_classes.md`](diagramas/04_diagrama_classes.md) | 🔵 Rever — entidades mudaram (RF18, RN10, RN11) |
| 5 | Diagrama Entidade-Relacional | [`diagramas/05_diagrama_er.md`](diagramas/05_diagrama_er.md) | 🔵 Rever — idem |
| 6 | Diagrama de Sequência | [`diagramas/06_diagrama_sequencia.md`](diagramas/06_diagrama_sequencia.md) | ✅ Fluxo assíncrono RF09/RF10 |
| 7 | ~~Diagrama de Atividade~~ | — | ❌ Cortado (decisão de prazo 15/07) |

---

## Coerência entre diagramas

- **Fonte única:** `analise_requisitos.md` — qualquer alteração de UC/RF/RN é feita aqui primeiro, depois propaga.
- **Actores:** Utilizador (pai) → Gestor / Professor. Firebase Auth aparece **só** no Diagrama de Contexto como entidade externa.
- **UCs:** UC01–UC16 (16 casos de uso). UC07, UC09, UC15 são internos ao sistema (sem actor directo).
- **Diagramas 4 e 5** precisam de ser revistos para reflectir: UC15 (nova lógica de permissão), RF18 (exportação), RN10/RN11.

---

## Próximos passos

1. Rever Diagrama de Classes (04) e DER (05) com as novas entidades
2. Actualizar Especificação Textual (03) com UC05 renomeado, UC15 e UC16 novos
3. Passar todos os diagramas para o Visual Paradigm
4. Explorar output do OR-Tools → definir estrutura JSON → actualizar Diagrama de Sequência
