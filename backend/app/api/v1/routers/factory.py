# Padrão CRUD partilhado por RF01 (Professores), RF02 (Turmas), RF03 (Disciplinas), RF04 (Salas)
# — ver docs/analise_requisitos_v5.0.md. Cada router de entidade instancia esta fábrica de forma fina;
# a lógica HTTP fica centralizada aqui para evitar duplicar 4x o mesmo CRUD.
from typing import TypeVar

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, SQLModel

from app.api.v1.deps import get_session
from app.core.exceptions import EntidadeNaoEncontradaError, IntegridadeVioladaError
from app.core.security import require_gestor
from app.repositories.base import BaseRepository
from app.services.crud_service import CRUDService

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchema = TypeVar("CreateSchema", bound=SQLModel)
UpdateSchema = TypeVar("UpdateSchema", bound=SQLModel)
ReadSchema = TypeVar("ReadSchema", bound=SQLModel)


def build_crud_router(
    *,
    prefix: str,
    tags: list[str],
    model: type[ModelType],
    create_schema: type[CreateSchema],
    update_schema: type[UpdateSchema],
    read_schema: type[ReadSchema],
    repository_cls: type[BaseRepository],
) -> APIRouter:
    # RN09/RN10 — todo o CRUD de dados mestre é reservado ao Gestor (RF01-RF04).
    router = APIRouter(prefix=prefix, tags=tags, dependencies=[Depends(require_gestor)])

    def get_service(session: Session = Depends(get_session)) -> CRUDService:
        return CRUDService(repository_cls(session))

    @router.post("", response_model=read_schema, status_code=201)
    def criar(payload: create_schema, service: CRUDService = Depends(get_service)):  # type: ignore[valid-type]
        try:
            return service.criar(model(**payload.model_dump()))
        except IntegridadeVioladaError as exc:
            raise HTTPException(409, "Já existe um registo com esta chave única ou referência inválida.") from exc

    @router.get("", response_model=list[read_schema])
    def listar(service: CRUDService = Depends(get_service)):  # type: ignore[valid-type]
        return service.listar()

    @router.get("/{id_}", response_model=read_schema)
    def obter(id_: int, service: CRUDService = Depends(get_service)):  # type: ignore[valid-type]
        try:
            return service.obter(id_)
        except EntidadeNaoEncontradaError as exc:
            raise HTTPException(404, str(exc)) from exc

    @router.put("/{id_}", response_model=read_schema)
    def atualizar(id_: int, payload: update_schema, service: CRUDService = Depends(get_service)):  # type: ignore[valid-type]
        try:
            return service.atualizar(id_, payload.model_dump(exclude_unset=True))
        except EntidadeNaoEncontradaError as exc:
            raise HTTPException(404, str(exc)) from exc
        except IntegridadeVioladaError as exc:
            raise HTTPException(409, "Já existe um registo com esta chave única ou referência inválida.") from exc

    @router.delete("/{id_}", status_code=204)
    def remover(id_: int, service: CRUDService = Depends(get_service)):  # type: ignore[valid-type]
        try:
            service.remover(id_)
        except EntidadeNaoEncontradaError as exc:
            raise HTTPException(404, str(exc)) from exc
        except IntegridadeVioladaError as exc:
            raise HTTPException(409, "Não é possível remover: existem registos dependentes deste.") from exc

    return router
