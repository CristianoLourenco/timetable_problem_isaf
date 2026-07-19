# Frontend — Alocação Manual + Ficha do Docente + Grade Renovada — Design

Sub-projeto 3 de 3. Objetivo principal: **integrar na totalidade os recursos
já existentes no backend** (sub-projetos 1 e 2, já implementados e commitados
em `feat/backend-fase8-solver-performance`) e melhorar a UX da consulta/edição
de horário. Não é um redesign — é fechar o gap entre o que a API já oferece e
o que a UI hoje mostra.

## Stack (obrigatório, ver CLAUDE.md raiz)
Flutter + GoRouter, Provider (global) + ValueNotifier (local), Clean
Architecture (`data/domain/presentation`). Sem Riverpod/Bloc/GetX.

## Endpoints já existentes a consumir (todos já implementados, testados, em produção)

```
GET  /jobs/{job_id}/pendencias
GET  /turmas/{turma_id}/professores-qualificados?disciplina_id=X
GET  /turmas/{turma_id}/slots-vagos?job_id=X
POST /alocacoes                body: {job_id, turma_id, disciplina_id, professor_id, sala_id, dia_semana, turno, periodos:[int]}
PATCH /alocacoes/{id}          body: {dia_semana, periodo}
DELETE /alocacoes/{id}
GET  /horarios/turma/{id}      já existe — RF11
GET  /horarios/professor/{id}  já existe — RF12
POST /gerar-horario            já existe — agora aceita tempo_maximo_minutos: 1|5|10 (default 5)
```

`Job` agora tem `tempo_maximo_minutos`. `JobRead` devolve esse campo. `Alocacao`
via `status="INFEASIBLE"` pode conter alocações/pendências parciais — nunca
assumir que INFEASIBLE = nada a mostrar.

## Funcionalidade 1 — Seletor de tempo máximo no ecrã de gerar horário

No formulário/diálogo de "Gerar Horário" (`feature_horario`), adicionar um
seletor (chips ou dropdown — 3 opções fixas, nunca campo livre): **1 min / 5
min / 10 min**, default 5. Enviar como `tempo_maximo_minutos` no `POST
/gerar-horario`. Texto de apoio curto: "tempos maiores encontram mais
alocações, mas demoram mais".

## Funcionalidade 2 — Secção de pendências pós-geração

Depois de um job terminar (DONE ou INFEASIBLE), buscar `GET
/jobs/{id}/pendencias`. Se não vazio, mostrar uma secção "Turmas/disciplinas
por distribuir" — lista de cards, um por pendência: nome da turma, nome da
disciplina, `tempos_em_falta`, `razao` (texto pronto, já explicado pelo
backend). Cada card tem uma ação "Alocar manualmente" → abre o fluxo da
Funcionalidade 3 pré-preenchido com essa turma/disciplina.

## Funcionalidade 3 — Fluxo de alocação manual

Ecrã/diálogo novo: dropdown Turma → dropdown Disciplina (da grade da turma) →
`GET professores-qualificados` popula dropdown Professor → dropdown Sala →
`GET slots-vagos` mostra os blocos livres (dia + período inicial/final) como
opções selecionáveis → confirmar chama `POST /alocacoes`. Erros 409 do backend
(mensagem já vem pronta, ex: "RN01: professor X já tem alocação...") mostrados
como snackbar/erro inline — nunca traduzir/reescrever, mostrar a mensagem tal
como vem.

## Funcionalidade 4 — Ficha do Docente

Nova rota (`feature_docentes`, ou estender a existente): ao selecionar um
docente, ecrã com:
- **Tabs**: Manhã / Tarde / Noite.
- Dentro de cada tab: grade semanal (dia × período) — células com a turma
  alocada naquele tempo, cor distinta por disciplina (paleta consistente,
  gerada por hash do `disciplina_id`, nunca cores fixas por nome).
- **Card** com lista das disciplinas que leciona + turmas, com ação "trocar
  disciplina" → abre um diálogo simples que chama `PATCH /alocacoes/{id}`
  (trocar `professor_id` da alocação, se o backend expuser esse campo no
  PATCH — confirmar; se não, é um gap a reportar antes de implementar).
- Usa `GET /horarios/professor/{id}` (já existe).

## Funcionalidade 5 — Grade renovada por tabs + filtro

No ecrã de consulta de horário (`horario_screen.dart`):
- **Filtro** no topo: Professor | Turma (escolha única).
  - Se Professor: carrega lista de professores → grade em tabs Manhã/Tarde/Noite
    (uma turma pode ter aulas em vários turnos ao longo da semana — um
    professor pode lecionar em mais de um turno).
  - Se Turma: carrega lista de turmas → como a turma pertence a um único
    turno (`Turma.turno`), **sem tabs** — mostra direto a grade desse turno.
- Abaixo da grade: lista "Professores e disciplinas desta turma/deste
  horário" — mesmo padrão visual do PDF já exportado (`exportacao_pdf_service.py`,
  já existe no backend) — blocos com cor leve por disciplina/professor.

## Fora de âmbito
- Exportação PDF (já existe, não mexer).
- Qualquer mudança de modelo no backend — este spec só consome o que já existe.

## Entregáveis mínimos (ordem sugerida)
1. Seletor de tempo (Funcionalidade 1) — mais simples, isolado.
2. Secção de pendências + fluxo de alocação manual (Funcionalidades 2+3) — core do gap a fechar.
3. Grade renovada por tabs + filtro (Funcionalidade 5).
4. Ficha do Docente (Funcionalidade 4) — pode reaproveitar componentes de cor/grade da 5.
