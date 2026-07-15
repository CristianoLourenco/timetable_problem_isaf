# Grade curricular — pré-requisito de dados do solver (conjunto E da definição formal UCTP)
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.exceptions import EntidadeNaoEncontradaError
from app.core.security import require_gestor
from app.schemas.turma_disciplina_schema import (
    ItemGradeCurricular,
    TurmaDisciplinaReadSchema,
    TurmaDisciplinaSetSchema,
)
from app.services.turma_disciplina_service import TurmaDisciplinaService

# RN09/RN10 — grade curricular é gerida pelo Gestor (parte de RF02/RF03).
router = APIRouter(prefix="/turmas", tags=["Grade Curricular"], dependencies=[Depends(require_gestor)])


def _get_service(session: Session = Depends(get_session)) -> TurmaDisciplinaService:
    return TurmaDisciplinaService(session)


def _para_schema(itens) -> TurmaDisciplinaReadSchema:
    return TurmaDisciplinaReadSchema(
        itens=[
            ItemGradeCurricular(disciplina_id=i.disciplina_id, carga_horaria_semanal=i.carga_horaria_semanal)
            for i in itens
        ]
    )


@router.get("/{turma_id}/disciplinas", response_model=TurmaDisciplinaReadSchema)
def obter_grade_curricular(turma_id: int, service: TurmaDisciplinaService = Depends(_get_service)):
    try:
        itens = service.obter(turma_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    return _para_schema(itens)


@router.post("/{turma_id}/disciplinas", response_model=TurmaDisciplinaReadSchema)
def definir_grade_curricular(
    turma_id: int,
    payload: TurmaDisciplinaSetSchema,
    service: TurmaDisciplinaService = Depends(_get_service),
):
    try:
        itens = service.definir(turma_id, [(i.disciplina_id, i.carga_horaria_semanal) for i in payload.itens])
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    return _para_schema(itens)
