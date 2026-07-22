# Implementa: RF05/RN07 — geração de disponibilidade sintética para professores
# reais sem nenhum registo, ver docs/relatorio/04_analise_desenvolvimento/.
#
# RF06/RF07 importam classificacao/vinculo_casa de Professor mas não têm caminho
# de importação para Disponibilidade — um professor real importado do Excel
# institucional cai sempre no fallback RN07 ("sem registo = totalmente
# disponível") até que ele próprio preencha via RF05. Esta função gera um
# palpite plausível e fundamentado nas qualificações reais do professor,
# nunca em turnos para os quais ele não teria qualificação nenhuma — mas
# nunca sobrescreve um registo já existente (seja de RF05 ou de uma geração
# anterior), gate estrito em "professor com zero linhas registadas".
import random

from sqlmodel import Session

from app.core.calendario import TurnoEnum
from app.core.config import settings
from app.repositories.disponibilidade_repository import DisponibilidadeRepository
from app.repositories.plano_curricular_disciplina_repository import PlanoCurricularDisciplinaRepository
from app.repositories.professor_disciplina_repository import ProfessorDisciplinaRepository
from app.repositories.professor_repository import ProfessorRepository
from app.schemas.tempo_schema import TempoChave

_DIAS_PROFESSOR_DE_CASA = 4
_DIAS_PROFESSOR_VISITANTE = 2


def gerar_disponibilidade_sintetica(session: Session) -> int:
    """Gera disponibilidade sintética para professores sem nenhum registo, com base
    nos turnos em que as disciplinas que lecionam realmente decorrem. Devolve o
    número de professores semeados. A proporção de dias (4/5 para professor de
    casa, 2/5 para visitante) é uma escolha simples e assumida como tal — não
    calibrada a partir de dados reais, apenas uma distinção defensável entre os
    dois perfis (ver vinculo_casa em Professor).
    """
    professor_repo = ProfessorRepository(session)
    disponibilidade_repo = DisponibilidadeRepository(session)
    professor_disciplina_repo = ProfessorDisciplinaRepository(session)
    plano_curricular_disciplina_repo = PlanoCurricularDisciplinaRepository(session)

    professores_semeados = 0
    for professor in professor_repo.list():
        if disponibilidade_repo.listar_tempos(professor.id):
            continue  # já tem registo (RF05 real ou geração anterior) — nunca sobrescrever

        disciplina_ids = professor_disciplina_repo.listar_por_professor(professor.id)
        if not disciplina_ids:
            continue  # sem qualificações, sem sinal real — fica no fallback RN07

        turnos_por_disciplina = plano_curricular_disciplina_repo.listar_turnos_por_disciplina(disciplina_ids)
        turnos_identificados = {turno for turnos in turnos_por_disciplina.values() for turno in turnos}
        if not turnos_identificados:
            continue  # qualificado para disciplinas sem nenhuma turma ainda — sem sinal real

        tempos = _gerar_tempos(professor.id, professor.vinculo_casa, turnos_identificados)
        disponibilidade_repo.substituir(professor.id, tempos, gerada_automaticamente=True)
        professores_semeados += 1

    return professores_semeados


def _gerar_tempos(professor_id: int, vinculo_casa: bool, turnos_identificados: set[str]) -> list[TempoChave]:
    dias_semana = settings.slot_dias_semana
    turno_periodos = settings.turno_periodos

    if vinculo_casa:
        # Professor de casa: disponível em todos os turnos identificados, na
        # maioria dos dias — perfil mais flexível.
        turnos = turnos_identificados
        rng = random.Random(1000 + professor_id)
        dias = rng.sample(dias_semana, k=min(_DIAS_PROFESSOR_DE_CASA, len(dias_semana)))
    else:
        # Visitante: só no turno mais frequente entre os identificados (desempate
        # pela ordem de TurnoEnum), em menos dias — perfil mais restrito.
        turno_mais_frequente = min(turnos_identificados, key=lambda t: list(TurnoEnum).index(TurnoEnum(t)))
        turnos = {turno_mais_frequente}
        rng = random.Random(2000 + professor_id)
        dias = rng.sample(dias_semana, k=min(_DIAS_PROFESSOR_VISITANTE, len(dias_semana)))

    return [
        TempoChave(dia_semana=dia, turno=turno, periodo=periodo)
        for dia in dias
        for turno in turnos
        for periodo in range(1, turno_periodos[turno] + 1)
    ]
