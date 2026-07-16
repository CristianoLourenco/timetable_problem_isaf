# Grade curricular — pré-requisito de dados do solver (conjunto E da definição formal UCTP)
from sqlmodel import Session

from app.core.exceptions import EntidadeNaoEncontradaError
from app.models.plano_curricular_disciplina import PlanoCurricularDisciplina
from app.repositories.disciplina_repository import DisciplinaRepository
from app.repositories.plano_curricular_disciplina_repository import PlanoCurricularDisciplinaRepository
from app.repositories.plano_curricular_repository import PlanoCurricularRepository


class PlanoCurricularDisciplinaService:
    def __init__(self, session: Session):
        self.itens_repo = PlanoCurricularDisciplinaRepository(session)
        self.plano_repo = PlanoCurricularRepository(session)
        self.disciplina_repo = DisciplinaRepository(session)

    def _validar_plano(self, plano_curricular_id: int) -> None:
        if self.plano_repo.get(plano_curricular_id) is None:
            raise EntidadeNaoEncontradaError("PlanoCurricular não encontrado.")

    def obter(self, plano_curricular_id: int) -> list[PlanoCurricularDisciplina]:
        self._validar_plano(plano_curricular_id)
        return self.itens_repo.listar_por_plano(plano_curricular_id)

    def definir(self, plano_curricular_id: int, itens: list[tuple[int, int]]) -> list[PlanoCurricularDisciplina]:
        self._validar_plano(plano_curricular_id)
        for disciplina_id, _ in itens:
            if self.disciplina_repo.get(disciplina_id) is None:
                raise EntidadeNaoEncontradaError(f"Disciplina {disciplina_id} não encontrada.")

        self.itens_repo.substituir(plano_curricular_id, itens)
        return self.itens_repo.listar_por_plano(plano_curricular_id)
