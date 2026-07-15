"""Cria as tabelas e semeia os registos de Slot a partir da configuração do calendário letivo.

Uso: python init_db.py
"""

from datetime import datetime, time, timedelta

from sqlmodel import Session, select

import app.models  # noqa: F401 - garante que todos os modelos são registados no metadata
from app.core.config import settings
from app.core.database import engine, init_db
from app.models.slot import Slot


def _horario_do_tempo(tempo_ordem: int) -> tuple[time, time]:
    inicio_base = datetime.strptime(settings.slot_inicio_primeiro_tempo, "%H:%M")
    inicio = inicio_base + timedelta(minutes=(tempo_ordem - 1) * settings.slot_duracao_minutos)
    fim = inicio + timedelta(minutes=settings.slot_duracao_minutos)
    return inicio.time(), fim.time()


def seed_slots(session: Session) -> None:
    ja_existem = session.exec(select(Slot)).first()
    if ja_existem:
        print("Slots já existem — a saltar seed.")
        return

    for dia in settings.slot_dias_semana:
        for tempo_ordem in range(1, settings.slot_tempos_por_dia + 1):
            hora_inicio, hora_fim = _horario_do_tempo(tempo_ordem)
            session.add(
                Slot(
                    dia_semana=dia,
                    tempo_ordem=tempo_ordem,
                    hora_inicio=hora_inicio,
                    hora_fim=hora_fim,
                )
            )
    session.commit()
    total = len(settings.slot_dias_semana) * settings.slot_tempos_por_dia
    print(f"{total} slots criados.")


if __name__ == "__main__":
    init_db()
    with Session(engine) as session:
        seed_slots(session)
