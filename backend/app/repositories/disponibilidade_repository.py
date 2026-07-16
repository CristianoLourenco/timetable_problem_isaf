# Implementa: RF05 (UC05) — ver docs/04_04_analise_desenvolvimento.md
from sqlmodel import Session, delete, select

from app.models.disponibilidade import Disponibilidade
from app.schemas.tempo_schema import TempoChave


class DisponibilidadeRepository:
    def __init__(self, session: Session):
        self.session = session

    def listar_tempos(self, professor_id: int) -> list[TempoChave]:
        rows = self.session.exec(
            select(Disponibilidade.dia_semana, Disponibilidade.turno, Disponibilidade.periodo).where(
                Disponibilidade.professor_id == professor_id
            )
        )
        return [TempoChave(dia_semana=d, turno=t, periodo=p) for d, t, p in rows]

    def substituir(self, professor_id: int, tempos: list[TempoChave]) -> None:
        self.session.exec(delete(Disponibilidade).where(Disponibilidade.professor_id == professor_id))
        for tempo in tempos:
            self.session.add(
                Disponibilidade(
                    professor_id=professor_id,
                    dia_semana=tempo.dia_semana,
                    turno=tempo.turno,
                    periodo=tempo.periodo,
                )
            )
        self.session.commit()
