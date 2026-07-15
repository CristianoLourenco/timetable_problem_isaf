from typing import Any, Generic, TypeVar

from sqlmodel import SQLModel

from app.core.exceptions import EntidadeNaoEncontradaError
from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=SQLModel)


class CRUDService(Generic[ModelType]):
    """Orquestra o repositório; ponto único onde regras de negócio de CRUD (ex: 404) vivem."""

    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    def criar(self, obj_in: ModelType) -> ModelType:
        return self.repository.create(obj_in)

    def listar(self) -> list[ModelType]:
        return self.repository.list()

    def obter(self, id_: Any) -> ModelType:
        obj = self.repository.get(id_)
        if obj is None:
            raise EntidadeNaoEncontradaError("Registo não encontrado.")
        return obj

    def atualizar(self, id_: Any, data: dict[str, Any]) -> ModelType:
        obj = self.obter(id_)
        return self.repository.update(obj, data)

    def remover(self, id_: Any) -> None:
        obj = self.obter(id_)
        self.repository.delete(obj)
