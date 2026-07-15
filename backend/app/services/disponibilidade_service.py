# Implementa: RF05 (UC05) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import Session

from app.core.exceptions import EntidadeNaoEncontradaError
from app.repositories.disponibilidade_repository import DisponibilidadeRepository
from app.repositories.professor_repository import ProfessorRepository


class DisponibilidadeService:
    def __init__(self, session: Session):
        self.disponibilidade_repo = DisponibilidadeRepository(session)
        self.professor_repo = ProfessorRepository(session)

    def _validar_professor(self, professor_id: int) -> None:
        if self.professor_repo.get(professor_id) is None:
            raise EntidadeNaoEncontradaError("Professor não encontrado.")

    def obter(self, professor_id: int) -> list[int]:
        self._validar_professor(professor_id)
        return self.disponibilidade_repo.listar_slot_ids(professor_id)

    def definir(self, professor_id: int, slot_ids: list[int]) -> list[int]:
        self._validar_professor(professor_id)
        self.disponibilidade_repo.substituir(professor_id, slot_ids)
        return slot_ids
