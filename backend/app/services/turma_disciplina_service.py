# Grade curricular — pré-requisito de dados do solver (conjunto E da definição formal UCTP)
from sqlmodel import Session

from app.core.exceptions import EntidadeNaoEncontradaError
from app.models.turma_disciplina import TurmaDisciplina
from app.repositories.disciplina_repository import DisciplinaRepository
from app.repositories.turma_disciplina_repository import TurmaDisciplinaRepository
from app.repositories.turma_repository import TurmaRepository


class TurmaDisciplinaService:
    def __init__(self, session: Session):
        self.grade_repo = TurmaDisciplinaRepository(session)
        self.turma_repo = TurmaRepository(session)
        self.disciplina_repo = DisciplinaRepository(session)

    def _validar_turma(self, turma_id: int) -> None:
        if self.turma_repo.get(turma_id) is None:
            raise EntidadeNaoEncontradaError("Turma não encontrada.")

    def obter(self, turma_id: int) -> list[TurmaDisciplina]:
        self._validar_turma(turma_id)
        return self.grade_repo.listar_por_turma(turma_id)

    def definir(self, turma_id: int, itens: list[tuple[int, int]]) -> list[TurmaDisciplina]:
        self._validar_turma(turma_id)
        for disciplina_id, _ in itens:
            if self.disciplina_repo.get(disciplina_id) is None:
                raise EntidadeNaoEncontradaError(f"Disciplina {disciplina_id} não encontrada.")

        self.grade_repo.substituir(turma_id, itens)
        return self.grade_repo.listar_por_turma(turma_id)
