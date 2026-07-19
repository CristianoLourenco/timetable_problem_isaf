# Implementa: RN01-RN08, RF13 — poda de domínio antes da geração de variáveis
# ver docs/04_04_analise_desenvolvimento.md secção 4.3.3 e skill ortools-timetabling-solver.
#
# builder.py já garante que nenhum BoolVar é criado para uma combinação inválida
# (professor não qualificado, turno errado) — mas só filtra NO MOMENTO de criar as
# variáveis. Os dados brutos que chegam a resolver_horario() (professores,
# disponibilidades) não vêm pré-filtrados pelo âmbito, o que obriga RN01
# (constraints_hard.py), a fórmula de prioridade e o termo de equidade
# (constraints_soft.py) a iterar sobre professores estruturalmente irrelevantes
# a este (ano_letivo, semestre) — cada um deles nunca vai gerar nenhuma variável.
#
# Esta função poda esses dados ANTES de chegarem a build_variables, e aproveita a
# mesma passagem para detetar problemas estruturais óbvios (RN05 impossível de
# cumprir por falta de professor/sala). Desde RF13 (nunca bloquear com
# INFEASIBLE), estes problemas NUNCA impedem o solve — viram PendenciaDTO com
# défice total desde logo, para o Gestor resolver por alocação manual, sem
# sequer gastar tempo do CP-SAT numa turma_disciplina que já sabemos impossível
# de preencher automaticamente.
from collections import defaultdict

from app.solver.builder import atribuir_salas_por_turma_turno
from app.solver.dto import HorarioInput, PendenciaDTO


def podar_dominio(dados: HorarioInput) -> tuple[HorarioInput, list[PendenciaDTO]]:
    """Remove professores/qualificações/disponibilidades irrelevantes ao âmbito de
    `dados` e devolve, no mesmo varrimento, as pendências estruturais óbvias
    (disciplina sem professor qualificado, turma sem sala com capacidade
    suficiente, ou turno com menos salas do que turmas — ver
    atribuir_salas_por_turma_turno) — cada uma já com défice = carga_horaria_semanal
    inteira, pronta para entrar na lista final de SolverResult.pendencias sem
    acionar o CP-SAT."""
    disciplinas_em_uso = {td.disciplina_id for td in dados.turma_disciplinas}

    professores_por_disciplina: dict[int, list[int]] = defaultdict(list)
    for pd in dados.professor_disciplinas:
        if pd.disciplina_id in disciplinas_em_uso:
            professores_por_disciplina[pd.disciplina_id].append(pd.professor_id)

    professores_relevantes = {
        professor_id for professores in professores_por_disciplina.values() for professor_id in professores
    }

    turmas_por_id = {turma.id: turma for turma in dados.turmas}
    capacidade_maxima = max((sala.capacidade for sala in dados.salas), default=0)
    # Turma+turno decidida (ou impossível) por 1-sala-fixa-por-turno — ver
    # app/solver/builder.py::atribuir_salas_por_turma_turno para a decisão de
    # modelagem (2026-07-19). Uma turma ausente daqui não tem NENHUMA sala
    # disponível no seu turno (escassez real, nunca uma turma "grande demais"
    # — esse caso já é pego pela checagem de capacidade_maxima abaixo).
    sala_por_turma_turno = atribuir_salas_por_turma_turno(dados)

    pendencias: list[PendenciaDTO] = []
    for td in dados.turma_disciplinas:
        if not professores_por_disciplina.get(td.disciplina_id):
            pendencias.append(
                PendenciaDTO(
                    turma_id=td.turma_id,
                    disciplina_id=td.disciplina_id,
                    tempos_em_falta=td.carga_horaria_semanal,
                    razao=(
                        f"Turma {td.turma_id} / disciplina {td.disciplina_id}: nenhum professor "
                        "qualificado registado em ProfessorDisciplina. Associe um professor a esta "
                        "disciplina, ou aloque manualmente escolhendo entre os professores já "
                        "qualificados para ela."
                    ),
                )
            )
            continue  # sem professor: turma sem sala não se aplica (já não há como alocar de todo)

        turma = turmas_por_id.get(td.turma_id)
        if turma is not None and turma.numero_alunos > capacidade_maxima:
            pendencias.append(
                PendenciaDTO(
                    turma_id=td.turma_id,
                    disciplina_id=td.disciplina_id,
                    tempos_em_falta=td.carga_horaria_semanal,
                    razao=(
                        f"Turma {td.turma_id}: {turma.numero_alunos} alunos excede a capacidade "
                        f"máxima disponível entre as salas ({capacidade_maxima}). Cadastre uma sala "
                        "com capacidade suficiente, ou aloque manualmente aceitando a lotação atual."
                    ),
                )
            )
            continue

        if turma is not None and (turma.id, turma.turno) not in sala_por_turma_turno:
            pendencias.append(
                PendenciaDTO(
                    turma_id=td.turma_id,
                    disciplina_id=td.disciplina_id,
                    tempos_em_falta=td.carga_horaria_semanal,
                    razao=(
                        f"Turma {td.turma_id}: nenhuma sala disponível no turno '{turma.turno}' — "
                        "cada turma ocupa uma única sala durante todo o turno (ver decisão de "
                        "modelagem), e as salas com capacidade suficiente já estão todas atribuídas "
                        "a outras turmas deste turno. Cadastre mais uma sala, ou aloque manualmente "
                        "partilhando uma sala já em uso."
                    ),
                )
            )

    turma_disciplinas_bloqueadas = {(p.turma_id, p.disciplina_id) for p in pendencias}
    dados_podados = HorarioInput(
        turmas=dados.turmas,
        professores=[p for p in dados.professores if p.id in professores_relevantes],
        salas=dados.salas,
        slots=dados.slots,
        turma_disciplinas=[
            td for td in dados.turma_disciplinas if (td.turma_id, td.disciplina_id) not in turma_disciplinas_bloqueadas
        ],
        professor_disciplinas=[
            pd
            for pd in dados.professor_disciplinas
            if pd.disciplina_id in disciplinas_em_uso and pd.professor_id in professores_relevantes
        ],
        disponibilidades=[d for d in dados.disponibilidades if d.professor_id in professores_relevantes],
    )
    return dados_podados, pendencias
