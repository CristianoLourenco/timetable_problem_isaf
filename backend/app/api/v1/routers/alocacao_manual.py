# Implementa: RF13 (UC09) — endpoints de alocação manual do Gestor
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.exceptions import EntidadeNaoEncontradaError, IntegridadeVioladaError
from app.core.security import require_gestor
from app.repositories.pendencia_repository import PendenciaRepository
from app.schemas.alocacao_manual_schema import (
    AlocacaoRead,
    BlocoVagoRead,
    CriarAlocacaoManualRequest,
    MoverAlocacaoRequest,
    PendenciaRead,
    ProfessorQualificadoRead,
)
from app.services.alocacao_manual_service import AlocacaoManualService

router = APIRouter(tags=["Alocação Manual"], dependencies=[Depends(require_gestor)])


def _get_service(session: Session = Depends(get_session)) -> AlocacaoManualService:
    return AlocacaoManualService(session)


def _csv_para_ids(valor: str) -> list[int]:
    return [int(x) for x in valor.split(",") if x]


@router.get("/jobs/{job_id}/pendencias", response_model=list[PendenciaRead])
def listar_pendencias(job_id: str, session: Session = Depends(get_session)):
    pendencias = PendenciaRepository(session).listar_por_job(job_id)
    return [
        PendenciaRead(
            turma_id=p.turma_id,
            disciplina_id=p.disciplina_id,
            tempos_em_falta=p.tempos_em_falta,
            razao=p.razao,
            professores_conflitantes=_csv_para_ids(p.professores_conflitantes),
            turmas_conflitantes=_csv_para_ids(p.turmas_conflitantes),
        )
        for p in pendencias
    ]


@router.get("/turmas/{turma_id}/professores-qualificados", response_model=list[ProfessorQualificadoRead])
def listar_professores_qualificados(
    turma_id: int, disciplina_id: int, service: AlocacaoManualService = Depends(_get_service)
):
    # turma_id não filtra a qualificação (que é da disciplina, não da turma) — mantido
    # no path por simetria com /turmas/{turma_id}/slots-vagos e para a UI já ter o
    # contexto da turma corrente ao construir o link.
    return service.listar_professores_qualificados(disciplina_id)


@router.get("/turmas/{turma_id}/slots-vagos", response_model=list[BlocoVagoRead])
def listar_slots_vagos(turma_id: int, job_id: str, service: AlocacaoManualService = Depends(_get_service)):
    try:
        return service.listar_slots_vagos(turma_id, job_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post("/alocacoes", response_model=list[AlocacaoRead], status_code=201)
def criar_alocacao(payload: CriarAlocacaoManualRequest, service: AlocacaoManualService = Depends(_get_service)):
    try:
        return service.criar(
            job_id=payload.job_id,
            turma_id=payload.turma_id,
            disciplina_id=payload.disciplina_id,
            professor_id=payload.professor_id,
            sala_id=payload.sala_id,
            dia_semana=payload.dia_semana,
            turno=payload.turno,
            periodos=payload.periodos,
        )
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    except IntegridadeVioladaError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.patch("/alocacoes/{alocacao_id}", response_model=AlocacaoRead)
def mover_alocacao(
    alocacao_id: int, payload: MoverAlocacaoRequest, service: AlocacaoManualService = Depends(_get_service)
):
    try:
        return service.mover(alocacao_id, dia_semana=payload.dia_semana, periodo=payload.periodo)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    except IntegridadeVioladaError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.delete("/alocacoes/{alocacao_id}", status_code=204)
def remover_alocacao(alocacao_id: int, service: AlocacaoManualService = Depends(_get_service)):
    try:
        service.remover(alocacao_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
