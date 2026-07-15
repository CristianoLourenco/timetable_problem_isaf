# Qualificação docente — filtro obrigatório da modelagem esparsa do solver
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.exceptions import EntidadeNaoEncontradaError
from app.schemas.professor_disciplina_schema import ProfessorDisciplinaReadSchema, ProfessorDisciplinaSetSchema
from app.services.professor_disciplina_service import ProfessorDisciplinaService

router = APIRouter(prefix="/professores", tags=["Qualificação Docente"])


def _get_service(session: Session = Depends(get_session)) -> ProfessorDisciplinaService:
    return ProfessorDisciplinaService(session)


@router.get("/{professor_id}/disciplinas", response_model=ProfessorDisciplinaReadSchema)
def obter_qualificacao(professor_id: int, service: ProfessorDisciplinaService = Depends(_get_service)):
    try:
        disciplina_ids = service.obter(professor_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    return ProfessorDisciplinaReadSchema(disciplina_ids=disciplina_ids)


@router.post("/{professor_id}/disciplinas", response_model=ProfessorDisciplinaReadSchema)
def definir_qualificacao(
    professor_id: int,
    payload: ProfessorDisciplinaSetSchema,
    service: ProfessorDisciplinaService = Depends(_get_service),
):
    try:
        disciplina_ids = service.definir(professor_id, payload.disciplina_ids)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    return ProfessorDisciplinaReadSchema(disciplina_ids=disciplina_ids)
