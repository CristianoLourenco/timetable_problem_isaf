# Implementa: RN12 — prioridade docente (classificação 50% + vínculo_casa 30% +
# escassez de disponibilidade 20%) — ver docs/04_04_analise_desenvolvimento.md secção 4.1.2.
from collections import Counter

from app.core.calendario import gerar_grelha_tempos
from app.solver.dto import DisponibilidadeDTO, ProfessorDTO

_PESO_CLASSIFICACAO = 0.5
_PESO_VINCULO_CASA = 0.3
_PESO_ESCASSEZ = 0.2


def calcular_prioridades(
    professores: list[ProfessorDTO], disponibilidades: list[DisponibilidadeDTO]
) -> dict[int, float]:
    """Prioridade docente em [0, 1] — usada para decidir ordem de fixação nos "Três
    Cenários Concorrentes": turma tem prioridade estrutural sobre professor, mas entre
    professores, o de maior prioridade fica mais perto da sua disponibilidade registada.

    Escassez é calculada contra a grelha semanal completa (45 slots), nunca contra
    `dados.slots` — assim a pontuação fica consistente entre o modo monolítico e cada
    fase de uma decomposição por turno, cujo `dados.slots` seria só uma fatia da semana.
    Um professor sem nenhum registo (RN07 — totalmente disponível) é o menos escasso
    por definição: escassez=0.0 não é um caso especial, é o resultado natural da fórmula.
    """
    total_slots_grade = len(gerar_grelha_tempos())
    slots_por_professor = Counter(disp.professor_id for disp in disponibilidades)

    prioridades: dict[int, float] = {}
    for professor in professores:
        norm_classificacao = (professor.classificacao - 1) / 4
        norm_vinculo = 1.0 if professor.vinculo_casa else 0.0
        n_slots = slots_por_professor.get(professor.id, 0)
        escassez = 0.0 if n_slots == 0 else max(0.0, 1 - n_slots / total_slots_grade)

        prioridades[professor.id] = (
            _PESO_CLASSIFICACAO * norm_classificacao
            + _PESO_VINCULO_CASA * norm_vinculo
            + _PESO_ESCASSEZ * escassez
        )

    return prioridades
