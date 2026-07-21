# Implementa: RN12 — testes da fórmula de prioridade docente, ver app/solver/prioridade_docente.py
from app.core.calendario import gerar_grelha_tempos
from app.solver.dto import DisponibilidadeDTO, ProfessorDTO
from app.solver.prioridade_docente import calcular_prioridades


def test_professor_classificacao_maxima_vinculo_casa_sem_registo():
    """classificacao=5, vinculo_casa=True, zero disponibilidade -> escassez=0 (RN07:
    quem não regista nada é o menos escasso) -> 0.5*1 + 0.3*1 + 0.2*0 = 0.8."""
    professores = [ProfessorDTO(id=1, classificacao=5, vinculo_casa=True)]
    prioridades = calcular_prioridades(professores, disponibilidades=[])
    assert prioridades[1] == 0.8


def test_professor_classificacao_minima_sem_vinculo_disponibilidade_ampla():
    """classificacao=1, vinculo_casa=False, disponibilidade cobrindo 90% da grelha
    -> norm_classificacao=0, norm_vinculo=0, escassez=0.1 -> 0.2*0.1 = 0.02."""
    grelha = gerar_grelha_tempos()
    total = len(grelha)
    n_disponiveis = round(total * 0.9)
    disponibilidades = [
        DisponibilidadeDTO(professor_id=1, dia_semana=g.dia_semana, turno=g.turno, periodo=g.periodo)
        for g in grelha[:n_disponiveis]
    ]
    professores = [ProfessorDTO(id=1, classificacao=1, vinculo_casa=False)]

    prioridades = calcular_prioridades(professores, disponibilidades)

    esperado = 0.2 * (1 - n_disponiveis / total)
    assert abs(prioridades[1] - esperado) < 1e-9


def test_professor_classificacao_intermedia():
    """classificacao=3 (meio da escala 1-5) -> norm_classificacao=0.5."""
    professores = [ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)]
    prioridades = calcular_prioridades(professores, disponibilidades=[])
    assert prioridades[1] == 0.5 * 0.5


def test_prioridades_ficam_no_intervalo_0_1():
    professores = [
        ProfessorDTO(id=1, classificacao=5, vinculo_casa=True),
        ProfessorDTO(id=2, classificacao=1, vinculo_casa=False),
    ]
    disponibilidades = [DisponibilidadeDTO(professor_id=2, dia_semana="segunda", turno="manha", periodo=1)]

    prioridades = calcular_prioridades(professores, disponibilidades)

    for valor in prioridades.values():
        assert 0.0 <= valor <= 1.0
    assert prioridades[1] > prioridades[2]  # maior classificação/vínculo domina
