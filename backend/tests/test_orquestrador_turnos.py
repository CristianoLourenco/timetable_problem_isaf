# Implementa: RF09/RF13 — testes da decomposição por turno, ver app/solver/orquestrador_turnos.py
from collections import defaultdict
from unittest.mock import patch

from app.solver.dto import (
    DisponibilidadeDTO,
    HorarioInput,
    ProfessorDisciplinaDTO,
    ProfessorDTO,
    SalaDTO,
    SlotDTO,
    SolverResult,
    TurmaDisciplinaDTO,
    TurmaDTO,
)
from app.solver.orquestrador_turnos import resolver_horario_por_turnos
from app.solver.solve import resolver_horario

MAX_TIME_TESTE = 5.0


def _slots(turno: str, dias: list[str], periodos_por_dia: int) -> list[SlotDTO]:
    return [SlotDTO(dia_semana=dia, turno=turno, periodo=p) for dia in dias for p in range(1, periodos_por_dia + 1)]


def _cenario_dois_turnos() -> HorarioInput:
    """2 turmas manhã + 2 turmas tarde, professores partilhados entre turnos —
    valida que a decomposição resolve ambas as fases sem conflitos e sem
    duplicar/perder alocações."""
    slots = _slots("manha", ["segunda", "terca"], 4) + _slots("tarde", ["segunda", "terca"], 4)

    return HorarioInput(
        turmas=[
            TurmaDTO(id=1, numero_alunos=20, turno="manha"),
            TurmaDTO(id=2, numero_alunos=20, turno="manha"),
            TurmaDTO(id=3, numero_alunos=20, turno="tarde"),
            TurmaDTO(id=4, numero_alunos=20, turno="tarde"),
        ],
        professores=[
            ProfessorDTO(id=1, classificacao=5, vinculo_casa=True),
            ProfessorDTO(id=2, classificacao=3, vinculo_casa=False),
        ],
        salas=[SalaDTO(id=1, capacidade=30), SalaDTO(id=2, capacidade=30)],
        slots=slots,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=2, disciplina_id=2, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=3, disciplina_id=3, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=4, disciplina_id=4, carga_horaria_semanal=2),
        ],
        professor_disciplinas=[
            # professor 1 dá manhã e tarde (partilhado entre fases)
            ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1),
            ProfessorDisciplinaDTO(professor_id=1, disciplina_id=3),
            ProfessorDisciplinaDTO(professor_id=2, disciplina_id=2),
            ProfessorDisciplinaDTO(professor_id=2, disciplina_id=4),
        ],
        disponibilidades=[],  # RN07 — todos totalmente disponíveis
    )


def test_decomposicao_resolve_ambas_as_fases_sem_conflitos():
    dados = _cenario_dois_turnos()
    resultado = resolver_horario_por_turnos(dados, max_time_in_seconds_total=MAX_TIME_TESTE)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert resultado.diagnostico is None
    assert len(resultado.alocacoes) == 8  # soma das cargas: 2+2+2+2

    def tempo_de(aloc):
        return (aloc.dia_semana, aloc.turno, aloc.periodo)

    contagem_professor_tempo: dict[tuple, int] = defaultdict(int)
    contagem_turma_tempo: dict[tuple, int] = defaultdict(int)
    contagem_sala_tempo: dict[tuple, int] = defaultdict(int)
    for aloc in resultado.alocacoes:
        contagem_professor_tempo[(aloc.professor_id, *tempo_de(aloc))] += 1
        contagem_turma_tempo[(aloc.turma_id, *tempo_de(aloc))] += 1
        contagem_sala_tempo[(aloc.sala_id, *tempo_de(aloc))] += 1

    assert all(c <= 1 for c in contagem_professor_tempo.values())
    assert all(c <= 1 for c in contagem_turma_tempo.values())
    assert all(c <= 1 for c in contagem_sala_tempo.values())

    turmas_manha = {1, 2}
    turmas_tarde = {3, 4}
    for aloc in resultado.alocacoes:
        if aloc.turma_id in turmas_manha:
            assert aloc.turno == "manha"
        else:
            assert aloc.turma_id in turmas_tarde
            assert aloc.turno == "tarde"


def test_turma_sem_professor_qualificado_vira_pendencia_no_turno_certo():
    """Turma da tarde sem nenhum professor qualificado — a fase da manhã resolve
    normalmente; a turma da tarde fica como pendência (não bloqueia mais nada)."""
    slots = _slots("manha", ["segunda"], 4) + _slots("tarde", ["segunda"], 4)

    dados = HorarioInput(
        turmas=[
            TurmaDTO(id=1, numero_alunos=20, turno="manha"),
            TurmaDTO(id=2, numero_alunos=20, turno="tarde"),
        ],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=2, disciplina_id=99, carga_horaria_semanal=2),  # sem professor qualificado
        ],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    resultado = resolver_horario_por_turnos(dados, max_time_in_seconds_total=MAX_TIME_TESTE)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert len(resultado.alocacoes) == 2  # só a turma 1 (manhã) foi alocada
    assert len(resultado.pendencias) == 1
    assert resultado.pendencias[0].turma_id == 2
    assert resultado.pendencias[0].disciplina_id == 99


def test_fase_sem_turmas_e_ignorada():
    """Âmbito só com turmas da manhã — a fase da tarde/noite deve ser saltada sem
    erro (nenhuma turma para resolver)."""
    slots = _slots("manha", ["segunda"], 4)
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno="manha")],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    resultado = resolver_horario_por_turnos(dados, max_time_in_seconds_total=MAX_TIME_TESTE)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert len(resultado.alocacoes) == 2
    assert all(a.turno == "manha" for a in resultado.alocacoes)


def test_timeout_em_fase_posterior_preserva_alocacoes_e_pendencias_de_fases_anteriores():
    """Finding (revisão final): manhã resolve com sucesso (>=1 alocação); tarde
    simula timeout (UNKNOWN mapeado para INFEASIBLE por resolver_horario). O
    resultado final deve continuar INFEASIBLE (o Gestor sabe que falta a Tarde),
    mas sem descartar o que a manhã já produziu."""
    dados = _cenario_dois_turnos()

    resultado_manha_real = None
    chamadas = {"n": 0}

    def resolver_horario_fake(*args, **kwargs):
        chamadas["n"] += 1
        if chamadas["n"] == 1:
            nonlocal resultado_manha_real
            resultado_manha_real = resolver_horario(*args, **kwargs)
            return resultado_manha_real
        return SolverResult(status="INFEASIBLE", alocacoes=[], diagnostico="timeout simulado", pendencias=[])

    with patch("app.solver.orquestrador_turnos.resolver_horario", side_effect=resolver_horario_fake):
        resultado = resolver_horario_por_turnos(dados, max_time_in_seconds_total=MAX_TIME_TESTE)

    assert resultado.status == "INFEASIBLE"
    assert "[Turno tarde]" in resultado.diagnostico
    assert len(resultado.alocacoes) == len(resultado_manha_real.alocacoes) > 0
    assert resultado.pendencias == resultado_manha_real.pendencias


def test_orcamento_total_e_distribuido_proporcionalmente_ao_tamanho_do_turno():
    """RNF01 — um turno com mais pares (turma, disciplina, professor qualificado)
    candidatos recebe uma fatia maior do orçamento total do que um turno pequeno,
    em vez de cada turno receber o mesmo tempo fixo (ineficiente: desperdiça tempo
    no turno pequeno, falta tempo ao grande — achado real medido à escala do ISAF
    em 2026-07-19: Manhã convergia em 75s/100s, Tarde não convergia nem em 100s)."""
    slots = (
        _slots("manha", ["segunda", "terca"], 4)
        + _slots("tarde", ["segunda", "terca"], 4)
    )

    # Manhã: 1 turma, 1 par (turma,disciplina), 1 professor qualificado -> turno pequeno.
    # Tarde: 4 turmas, 4 pares, 4 professores qualificados cada -> turno bem maior.
    dados = HorarioInput(
        turmas=[
            TurmaDTO(id=1, numero_alunos=20, turno="manha"),
            TurmaDTO(id=2, numero_alunos=20, turno="tarde"),
            TurmaDTO(id=3, numero_alunos=20, turno="tarde"),
            TurmaDTO(id=4, numero_alunos=20, turno="tarde"),
            TurmaDTO(id=5, numero_alunos=20, turno="tarde"),
        ],
        professores=[ProfessorDTO(id=p, classificacao=3, vinculo_casa=False) for p in range(1, 9)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=2, disciplina_id=2, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=3, disciplina_id=3, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=4, disciplina_id=4, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=5, disciplina_id=5, carga_horaria_semanal=2),
        ],
        professor_disciplinas=[
            ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1),
            # disciplinas 2-5 (tarde) têm 2 professores qualificados cada -> mais
            # combinações candidatas do que a disciplina 1 (manhã, só 1 professor).
            ProfessorDisciplinaDTO(professor_id=2, disciplina_id=2),
            ProfessorDisciplinaDTO(professor_id=3, disciplina_id=2),
            ProfessorDisciplinaDTO(professor_id=4, disciplina_id=3),
            ProfessorDisciplinaDTO(professor_id=5, disciplina_id=3),
            ProfessorDisciplinaDTO(professor_id=6, disciplina_id=4),
            ProfessorDisciplinaDTO(professor_id=7, disciplina_id=4),
            ProfessorDisciplinaDTO(professor_id=8, disciplina_id=5),
            ProfessorDisciplinaDTO(professor_id=2, disciplina_id=5),
        ],
        disponibilidades=[],
    )

    tempos_usados: dict[str, float] = {}

    def resolver_horario_fake(sub_dados, max_time_in_seconds, **kwargs):
        turno = sub_dados.turmas[0].turno
        tempos_usados[turno] = max_time_in_seconds
        return resolver_horario(sub_dados, max_time_in_seconds=max_time_in_seconds, **kwargs)

    with patch("app.solver.orquestrador_turnos.resolver_horario", side_effect=resolver_horario_fake):
        resolver_horario_por_turnos(dados, max_time_in_seconds_total=30.0)

    assert tempos_usados["tarde"] > tempos_usados["manha"]
    # soma das fatias não pode exceder o orçamento total pedido
    assert sum(tempos_usados.values()) <= 30.0 + 1e-6
