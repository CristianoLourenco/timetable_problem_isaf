# Implementa: RF02 (UC02) — ver docs/relatorio/04_analise_desenvolvimento/
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.api.v1.routers.factory import build_crud_router
from app.core.exceptions import EntidadeNaoEncontradaError
from app.core.security import require_gestor
from app.models.plano_curricular import PlanoCurricular
from app.repositories.plano_curricular_repository import PlanoCurricularRepository
from app.schemas.plano_curricular_schema import (
    ItemPlanoCurricular,
    PlanoCurricularCreate,
    PlanoCurricularDisciplinaReadSchema,
    PlanoCurricularDisciplinaSetSchema,
    PlanoCurricularRead,
    PlanoCurricularUpdate,
)
from app.services.plano_curricular_disciplina_service import PlanoCurricularDisciplinaService

router = build_crud_router(
    prefix="/planos-curriculares",
    tags=["Planos Curriculares"],
    model=PlanoCurricular,
    create_schema=PlanoCurricularCreate,
    update_schema=PlanoCurricularUpdate,
    read_schema=PlanoCurricularRead,
    repository_cls=PlanoCurricularRepository,
)

# RN09/RN10 — grade curricular é gerida pelo Gestor (parte de RF02/RF03).
itens_router = APIRouter(
    prefix="/planos-curriculares", tags=["Planos Curriculares"], dependencies=[Depends(require_gestor)]
)


def _get_service(session: Session = Depends(get_session)) -> PlanoCurricularDisciplinaService:
    return PlanoCurricularDisciplinaService(session)


def _para_schema(itens) -> PlanoCurricularDisciplinaReadSchema:
    return PlanoCurricularDisciplinaReadSchema(
        itens=[
            ItemPlanoCurricular(disciplina_id=i.disciplina_id, carga_horaria_semanal=i.carga_horaria_semanal)
            for i in itens
        ]
    )


@itens_router.get("/{plano_curricular_id}/disciplinas", response_model=PlanoCurricularDisciplinaReadSchema)
def obter_disciplinas(plano_curricular_id: int, service: PlanoCurricularDisciplinaService = Depends(_get_service)):
    try:
        itens = service.obter(plano_curricular_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    return _para_schema(itens)


@itens_router.post("/{plano_curricular_id}/disciplinas", response_model=PlanoCurricularDisciplinaReadSchema)
def definir_disciplinas(
    plano_curricular_id: int,
    payload: PlanoCurricularDisciplinaSetSchema,
    service: PlanoCurricularDisciplinaService = Depends(_get_service),
):
    try:
        itens = service.definir(
            plano_curricular_id, [(i.disciplina_id, i.carga_horaria_semanal) for i in payload.itens]
        )
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    return _para_schema(itens)
