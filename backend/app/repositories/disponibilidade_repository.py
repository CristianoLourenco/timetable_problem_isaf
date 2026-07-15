# Implementa: RF05 (UC05) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import Session, delete, select

from app.models.disponibilidade import Disponibilidade


class DisponibilidadeRepository:
    def __init__(self, session: Session):
        self.session = session

    def listar_slot_ids(self, professor_id: int) -> list[int]:
        rows = self.session.exec(
            select(Disponibilidade.slot_id).where(Disponibilidade.professor_id == professor_id)
        )
        return list(rows)

    def substituir(self, professor_id: int, slot_ids: list[int]) -> None:
        self.session.exec(delete(Disponibilidade).where(Disponibilidade.professor_id == professor_id))
        for slot_id in slot_ids:
            self.session.add(Disponibilidade(professor_id=professor_id, slot_id=slot_id))
        self.session.commit()
