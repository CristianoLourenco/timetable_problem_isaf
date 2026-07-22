# Grelha de tempos letivos — substitui a tabela Slot (ver docs/relatorio/04_analise_desenvolvimento/
# secção 4.2.4: dia_semana + turno + periodo são campos simples, sem entidade própria no DER).
#
# A numeração do período reinicia a 1 em cada turno (manhã 1..6, tarde/noite 1..5) porque
# uma Turma pertence sempre a um único turno (Turma.turno) — periodo sozinho é ambíguo sem
# turno. Esta grelha nunca é persistida: é gerada em runtime a partir de core/config.py e
# usada tanto pelo solver (dia_semana/turno/periodo, sem horas) como pela camada de
# apresentação (horas reais, para a grelha semanal do Flutter).
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from enum import StrEnum

from app.core.config import settings


class TurnoEnum(StrEnum):
    MANHA = "manha"
    TARDE = "tarde"
    NOITE = "noite"


@dataclass(frozen=True)
class DefinicaoTempo:
    dia_semana: str
    turno: str
    periodo: int
    hora_inicio: time
    hora_fim: time


def gerar_grelha_tempos() -> list[DefinicaoTempo]:
    """Gera a grelha completa dia x turno x período, com a hora real de cada tempo.

    Duração fixa (slot_duracao_minutos) e sem intervalos — cada período começa onde o
    anterior termina, a partir da hora de início do respetivo turno.
    """
    grelha: list[DefinicaoTempo] = []
    for dia in settings.slot_dias_semana:
        for turno, total_periodos in settings.turno_periodos.items():
            inicio_turno = datetime.strptime(settings.turno_hora_inicio[turno], "%H:%M")
            for periodo in range(1, total_periodos + 1):
                inicio = inicio_turno + timedelta(minutes=(periodo - 1) * settings.slot_duracao_minutos)
                fim = inicio + timedelta(minutes=settings.slot_duracao_minutos)
                grelha.append(
                    DefinicaoTempo(
                        dia_semana=dia,
                        turno=turno,
                        periodo=periodo,
                        hora_inicio=inicio.time(),
                        hora_fim=fim.time(),
                    )
                )
    return grelha
