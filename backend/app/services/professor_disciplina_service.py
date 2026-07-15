# Qualificação docente — filtro obrigatório da modelagem esparsa do solver
from sqlmodel import Session

from app.core.exceptions import EntidadeNaoEncontradaError
from app.repositories.disciplina_repository import DisciplinaRepository
from app.repositories.professor_disciplina_repository import ProfessorDisciplinaRepository
from app.repositories.professor_repository import ProfessorRepository


class ProfessorDisciplinaService:
    def __init__(self, session: Session):
        self.qualificacao_repo = ProfessorDisciplinaRepository(session)
        self.professor_repo = ProfessorRepository(session)
        self.disciplina_repo = DisciplinaRepository(session)

    def _validar_professor(self, professor_id: int) -> None:
        if self.professor_repo.get(professor_id) is None:
            raise EntidadeNaoEncontradaError("Professor não encontrado.")

    def obter(self, professor_id: int) -> list[int]:
        self._validar_professor(professor_id)
        return self.qualificacao_repo.listar_por_professor(professor_id)

    def definir(self, professor_id: int, disciplina_ids: list[int]) -> list[int]:
        self._validar_professor(professor_id)
        for disciplina_id in disciplina_ids:
            if self.disciplina_repo.get(disciplina_id) is None:
                raise EntidadeNaoEncontradaError(f"Disciplina {disciplina_id} não encontrada.")

        self.qualificacao_repo.substituir(professor_id, disciplina_ids)
        return disciplina_ids
