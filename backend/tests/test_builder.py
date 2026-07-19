# Implementa: RN03, RN08 — geração esparsa de variáveis (ver app/solver/builder.py)
from ortools.sat.python import cp_model

from app.solver.builder import atribuir_salas_por_turma_turno, build_variables
from app.solver.dto import (
    HorarioInput,
    ProfessorDisciplinaDTO,
    ProfessorDTO,
    SalaDTO,
    SlotDTO,
    TurmaDisciplinaDTO,
    TurmaDTO,
)


def _dados_duas_turmas_mesmo_turno() -> HorarioInput:
    """2 turmas no mesmo turno, cada uma com 2 disciplinas diferentes — cenário
    mínimo para provar que cada turma fica presa a UMA única sala ao longo do
    turno inteiro, mesmo trocando de disciplina."""
    slots = [SlotDTO(dia_semana="segunda", turno="manha", periodo=p) for p in range(1, 5)]
    return HorarioInput(
        turmas=[
            TurmaDTO(id=1, numero_alunos=20, turno="manha"),
            TurmaDTO(id=2, numero_alunos=25, turno="manha"),
        ],
        professores=[ProfessorDTO(id=1, classificacao=5, vinculo_casa=True), ProfessorDTO(id=2, classificacao=5, vinculo_casa=True)],
        salas=[SalaDTO(id=1, capacidade=30), SalaDTO(id=2, capacidade=30), SalaDTO(id=3, capacidade=30)],
        slots=slots,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=2, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=2, disciplina_id=1, carga_horaria_semanal=2),
        ],
        professor_disciplinas=[
            ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1),
            ProfessorDisciplinaDTO(professor_id=2, disciplina_id=2),
        ],
        disponibilidades=[],
    )


def test_atribuir_salas_por_turma_turno_e_deterministico_e_sem_colisao():
    """Cada (turma, turno) recebe exatamente 1 sala; duas turmas do mesmo turno
    nunca recebem a mesma sala (evita RN03 ficar impossível de cumprir por
    construção — a atribuição determinística já não pode colidir)."""
    dados = _dados_duas_turmas_mesmo_turno()
    atribuicao = atribuir_salas_por_turma_turno(dados)

    assert set(atribuicao.keys()) == {(1, "manha"), (2, "manha")}
    assert atribuicao[(1, "manha")] != atribuicao[(2, "manha")]

    # Determinístico: chamar de novo com os mesmos dados devolve a mesma atribuição.
    atribuicao_repetida = atribuir_salas_por_turma_turno(dados)
    assert atribuicao == atribuicao_repetida


def test_build_variables_usa_sempre_a_mesma_sala_para_a_turma_no_turno():
    """A turma 1 tem 2 disciplinas diferentes no mesmo turno — todas as
    variáveis geradas para a turma 1 (independente da disciplina) devem usar
    a mesma sala; idem para a turma 2, com uma sala diferente da turma 1."""
    dados = _dados_duas_turmas_mesmo_turno()
    model = cp_model.CpModel()
    variaveis = build_variables(model, dados)

    salas_por_turma: dict[int, set[int]] = {}
    for chave in variaveis.x:
        turma_id, _, _, sala_id, _, _, _ = chave
        salas_por_turma.setdefault(turma_id, set()).add(sala_id)

    assert len(salas_por_turma[1]) == 1, "turma 1 devia usar uma única sala em todo o turno"
    assert len(salas_por_turma[2]) == 1, "turma 2 devia usar uma única sala em todo o turno"
    assert salas_por_turma[1] != salas_por_turma[2], "turmas diferentes no mesmo turno não podem partilhar sala"


def test_build_variables_turmas_de_turnos_diferentes_podem_repetir_sala():
    """Uma sala pode ser reutilizada por turmas de turnos DIFERENTES (manhã,
    tarde, noite) — só dentro do mesmo turno é que a sala fica exclusiva de
    uma única turma (RN03 sem dupla turma no mesmo tempo já garantiria isso
    de qualquer forma, mas aqui confirmamos que turnos diferentes não sofrem
    a mesma restrição de exclusividade artificial)."""
    slots_manha = [SlotDTO(dia_semana="segunda", turno="manha", periodo=p) for p in range(1, 3)]
    slots_tarde = [SlotDTO(dia_semana="segunda", turno="tarde", periodo=p) for p in range(1, 3)]
    dados = HorarioInput(
        turmas=[
            TurmaDTO(id=1, numero_alunos=20, turno="manha"),
            TurmaDTO(id=2, numero_alunos=20, turno="tarde"),
        ],
        professores=[ProfessorDTO(id=1, classificacao=5, vinculo_casa=True)],
        salas=[SalaDTO(id=1, capacidade=30)],  # uma única sala candidata para ambas
        slots=slots_manha + slots_tarde,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=2, disciplina_id=1, carga_horaria_semanal=2),
        ],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )
    model = cp_model.CpModel()
    variaveis = build_variables(model, dados)

    salas_por_turma = {chave[0]: chave[3] for chave in variaveis.x}
    assert salas_por_turma[1] == 1
    assert salas_por_turma[2] == 1
