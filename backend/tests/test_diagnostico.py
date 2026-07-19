# Implementa: RF13 (UC09) — geração de razão por pendência (app/solver/diagnostico.py)
from unittest.mock import patch

from app.solver.diagnostico import formatar_diagnostico_nucleo, gerar_razao_pendencia, isolar_nucleo_infeasible
from app.solver.dto import (
    HorarioInput,
    ProfessorDisciplinaDTO,
    ProfessorDTO,
    SalaDTO,
    SlotDTO,
    TurmaDisciplinaDTO,
    TurmaDTO,
)
from app.solver.solve import resolver_horario

TURNO_TESTE = "manha"


def _cenario_com_professor_sobrecarregado() -> HorarioInput:
    """2 turmas partilham o ÚNICO professor qualificado para a sua disciplina, mas
    o turno só tem 3 tempos no total — o professor precisaria de 4 (2+2) usos
    distintos, impossível por pigeonhole independentemente de blocos/salas.
    Réplica minimalista do caso real encontrado à escala do ISAF (GBS 4º ano)."""
    slots = [SlotDTO(dia_semana="segunda", turno=TURNO_TESTE, periodo=p) for p in range(1, 4)]
    return HorarioInput(
        turmas=[
            TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE),
            TurmaDTO(id=2, numero_alunos=20, turno=TURNO_TESTE),
        ],
        professores=[ProfessorDTO(id=1, classificacao=5, vinculo_casa=True)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=2, disciplina_id=1, carga_horaria_semanal=2),
        ],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )


def test_isolar_nucleo_encontra_as_duas_turmas_em_conflito():
    dados = _cenario_com_professor_sobrecarregado()
    nucleo = isolar_nucleo_infeasible(dados, timeout_por_tentativa=5.0, orcamento_total=20.0)

    assert nucleo == [1, 2]


def test_formatar_diagnostico_menciona_o_professor_partilhado():
    dados = _cenario_com_professor_sobrecarregado()
    mensagem = formatar_diagnostico_nucleo([1, 2], dados)

    assert "turmas 1 e 2" in mensagem
    assert "professor(es) 1" in mensagem


def test_isolar_nucleo_devolve_none_para_cenario_viavel():
    """Não deve nunca reportar um núcleo para um cenário que é, na verdade, viável."""
    slots = [SlotDTO(dia_semana="segunda", turno=TURNO_TESTE, periodo=p) for p in range(1, 5)]
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=5, vinculo_casa=True)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )
    nucleo = isolar_nucleo_infeasible(dados, timeout_por_tentativa=5.0, orcamento_total=10.0)

    assert nucleo is None


def test_resolver_horario_reporta_pendencia_com_professor_partilhado_de_ponta_a_ponta():
    """Antes: INFEASIBLE com o núcleo isolado no campo `diagnostico`. Agora (RF13):
    OPTIMAL/FEASIBLE com uma pendência por turma, cada uma explicando o professor
    partilhado na razão."""
    dados = _cenario_com_professor_sobrecarregado()
    resultado = resolver_horario(dados, max_time_in_seconds=20.0, num_search_workers=4)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert len(resultado.pendencias) >= 1
    turmas_pendentes = {p.turma_id for p in resultado.pendencias}
    assert turmas_pendentes & {1, 2}
    assert any("professor" in p.razao.lower() for p in resultado.pendencias)


def _cenario_tres_turmas_professor_escasso() -> HorarioInput:
    """3 turmas partilham o ÚNICO professor qualificado para a sua disciplina,
    turno com apenas 3 tempos no total — nenhuma das 3 turmas passa pelas causas
    baratas #1/#2 (carga de 2 <= 3 tempos do turno), então as 3 caem na causa #3
    (bisecção). Usado para provar que isolar_nucleo_infeasible é chamado NO
    MÁXIMO 1 vez por chamada a _extrair_pendencias_deficit, não uma vez por
    pendência (finding da revisão final)."""
    slots = [SlotDTO(dia_semana="segunda", turno=TURNO_TESTE, periodo=p) for p in range(1, 4)]
    return HorarioInput(
        turmas=[
            TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE),
            TurmaDTO(id=2, numero_alunos=20, turno=TURNO_TESTE),
            TurmaDTO(id=3, numero_alunos=20, turno=TURNO_TESTE),
        ],
        professores=[ProfessorDTO(id=1, classificacao=5, vinculo_casa=True)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=2, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=3, disciplina_id=1, carga_horaria_semanal=2),
        ],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )


def test_isolar_nucleo_infeasible_e_chamado_no_maximo_uma_vez_por_chamada_ao_solver():
    """Finding (revisão final): antes, gerar_razao_pendencia chamava
    isolar_nucleo_infeasible(dados) internamente para CADA pendência sem causa
    barata — com N pendências no mesmo cenário isso custava até N x orçamento de
    bisecção. Agora _extrair_pendencias_deficit (solve.py) calcula o núcleo uma
    única vez e reutiliza para todas as pendências do mesmo cenário."""
    dados = _cenario_tres_turmas_professor_escasso()

    with patch(
        "app.solver.solve.isolar_nucleo_infeasible", wraps=isolar_nucleo_infeasible
    ) as nucleo_mock:
        resultado = resolver_horario(dados, max_time_in_seconds=20.0, num_search_workers=4)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert len(resultado.pendencias) >= 2  # múltiplas pendências sem causa barata no mesmo cenário
    assert nucleo_mock.call_count <= 1


def _cenario_multiplas_pendencias_sem_nucleo_infeasible() -> HorarioInput:
    """4 turmas, cada uma com défice de RN05 (soft) mas SEM nenhum conflito
    estrutural provável — RN01-RN06 são satisfazíveis para cada uma sozinha,
    o défice só existe porque relative_gap_limit aceitou uma solução "boa o
    suficiente" antes de preencher tudo (ver core/config.py). Reproduz o caso
    real medido à escala do ISAF (2026-07-19, 86 turmas): isolar_nucleo_infeasible
    devolve None (não confirma INFEASIBLE de nenhum subconjunto), e o bug
    corrigido aqui era tratar esse None partilhado como "não fornecido",
    recalculando a bisecção cara (5-9s) para CADA uma das pendências."""
    slots = [SlotDTO(dia_semana="segunda", turno=TURNO_TESTE, periodo=p) for p in range(1, 6)]
    turmas = [TurmaDTO(id=i, numero_alunos=20, turno=TURNO_TESTE) for i in range(1, 5)]
    professores = [ProfessorDTO(id=i, classificacao=5, vinculo_casa=True) for i in range(1, 5)]
    return HorarioInput(
        turmas=turmas,
        professores=professores,
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=i, disciplina_id=i, carga_horaria_semanal=2) for i in range(1, 5)
        ],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=i, disciplina_id=i) for i in range(1, 5)],
        disponibilidades=[],
    )


def test_isolar_nucleo_infeasible_e_chamado_no_maximo_uma_vez_mesmo_quando_devolve_none():
    """Bug real (2026-07-19, 86 turmas): `nucleo_compartilhado if nucleo_compartilhado
    is not None else isolar_nucleo_infeasible(dados)` tratava o retorno legítimo
    `None` (bisecção não confirma nenhum núcleo INFEASIBLE — comum agora que RN05 é
    soft-com-défice) como "não fornecido", recalculando isolar_nucleo_infeasible
    (5-9s cada) para cada pendência sem causa barata. Com 56 pendências isto mediu
    419s de 572s totais (73%) num teste ponta-a-ponta real. Corrigido com o
    sentinela `_NAO_FORNECIDO` — `None` explícito nunca mais dispara o recálculo."""
    dados = _cenario_multiplas_pendencias_sem_nucleo_infeasible()

    with patch(
        "app.solver.solve.isolar_nucleo_infeasible", wraps=isolar_nucleo_infeasible
    ) as nucleo_mock:
        resultado = resolver_horario(dados, max_time_in_seconds=10.0, num_search_workers=4)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert nucleo_mock.call_count <= 1


def test_gerar_razao_pendencia_disciplina_excede_tempos_do_turno():
    """Causa barata #3: a própria carga da disciplina excede o total de tempos do
    turno da turma — deve ser identificada sem precisar da bisecção cara."""
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=5, vinculo_casa=True)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=[SlotDTO(dia_semana="segunda", turno=TURNO_TESTE, periodo=p) for p in range(1, 3)],  # só 2 tempos
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=6)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    pendencia = gerar_razao_pendencia(1, 1, tempos_em_falta=4, dados=dados)

    assert pendencia.turma_id == 1
    assert pendencia.disciplina_id == 1
    assert pendencia.tempos_em_falta == 4
    assert "excede o total de tempos semanais do turno" in pendencia.razao
