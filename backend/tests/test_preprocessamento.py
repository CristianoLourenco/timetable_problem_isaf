# Implementa: RN01-RN08 — testes de poda de domínio, ver app/solver/preprocessamento.py
from app.solver.dto import (
    HorarioInput,
    ProfessorDisciplinaDTO,
    ProfessorDTO,
    SalaDTO,
    SlotDTO,
    TurmaDisciplinaDTO,
    TurmaDTO,
)
from app.solver.preprocessamento import podar_dominio
from app.solver.solve import resolver_horario

TURNO_TESTE = "manha"


def _slots() -> list[SlotDTO]:
    return [SlotDTO(dia_semana=dia, turno=TURNO_TESTE, periodo=p) for dia in ["segunda", "terca"] for p in range(1, 5)]


def test_podar_dominio_remove_professores_irrelevantes():
    """5 professores, só 2 qualificados para as disciplinas em uso — os outros 3
    nunca vão gerar nenhum BoolVar em builder.py, logo devem sair de dados.professores
    e de dados.disponibilidades."""
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=p, classificacao=3, vinculo_casa=False) for p in range(1, 6)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=_slots(),
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[
            ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1),
            ProfessorDisciplinaDTO(professor_id=2, disciplina_id=1),
            # professores 3, 4, 5 qualificados só para disciplinas fora deste âmbito
            ProfessorDisciplinaDTO(professor_id=3, disciplina_id=99),
        ],
        disponibilidades=[],
    )

    dados_podados, pendencias = podar_dominio(dados)

    assert pendencias == []
    assert {p.id for p in dados_podados.professores} == {1, 2}
    assert {pd.professor_id for pd in dados_podados.professor_disciplinas} == {1, 2}


def test_podar_dominio_detecta_disciplina_sem_professor_qualificado():
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=_slots(),
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=99)],  # não é a disciplina 1
        disponibilidades=[],
    )

    _, pendencias = podar_dominio(dados)

    assert len(pendencias) == 1
    assert pendencias[0].turma_id == 1
    assert pendencias[0].disciplina_id == 1
    assert pendencias[0].tempos_em_falta == 2
    assert "nenhum professor qualificado" in pendencias[0].razao


def test_podar_dominio_detecta_turma_sem_sala_com_capacidade():
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=50, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=_slots(),
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    _, pendencias = podar_dominio(dados)

    assert len(pendencias) == 1
    assert "50 alunos excede a capacidade" in pendencias[0].razao


def test_podar_dominio_cenario_valido_nao_bloqueia_resolucao():
    """Regressão: um cenário totalmente válido não deve ser sinalizado como
    pendência, e resolver_horario deve continuar a chegar ao CP-SAT."""
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=_slots(),
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    _, pendencias = podar_dominio(dados)
    assert pendencias == []

    resultado = resolver_horario(dados, max_time_in_seconds=5.0)
    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert resultado.pendencias == []


def test_resolver_horario_nunca_bloqueia_sem_professor_qualificado():
    """Antes: INFEASIBLE instantâneo. Agora: OPTIMAL/FEASIBLE com uma pendência de
    défice total, sem sequer acionar o CP-SAT para essa turma_disciplina."""
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=_slots(),
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=99)],
        disponibilidades=[],
    )

    resultado = resolver_horario(dados, max_time_in_seconds=10.0)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert resultado.alocacoes == []
    assert len(resultado.pendencias) == 1
    assert resultado.pendencias[0].tempos_em_falta == 2
    assert "nenhum professor qualificado" in resultado.pendencias[0].razao
