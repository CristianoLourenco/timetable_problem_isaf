# Implementa: RF05 (UC05) — ver docs/relatorio/04_analise_desenvolvimento/
from sqlmodel import Session

from app.core.exceptions import EntidadeNaoEncontradaError
from app.repositories.disponibilidade_repository import DisponibilidadeRepository
from app.repositories.professor_repository import ProfessorRepository
from app.schemas.tempo_schema import TempoChave


class DisponibilidadeService:
    def __init__(self, session: Session):
        self.disponibilidade_repo = DisponibilidadeRepository(session)
        self.professor_repo = ProfessorRepository(session)

    def _validar_professor(self, professor_id: int) -> None:
        if self.professor_repo.get(professor_id) is None:
            raise EntidadeNaoEncontradaError("Professor não encontrado.")

    def obter(self, professor_id: int) -> list[TempoChave]:
        self._validar_professor(professor_id)
        return self.disponibilidade_repo.listar_tempos(professor_id)

    def definir(self, professor_id: int, tempos: list[TempoChave]) -> list[TempoChave]:
        self._validar_professor(professor_id)
        self.disponibilidade_repo.substituir(professor_id, tempos)
        return tempos
