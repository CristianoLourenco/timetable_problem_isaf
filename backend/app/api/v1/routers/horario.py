# Implementa: RF09, RF10 (UC08, UC10) — ver docs/analise_requisitos_v5.0.md
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.exceptions import EntidadeNaoEncontradaError
from app.schemas.horario_schema import HorarioResponseSchema
from app.schemas.job_schema import GerarHorarioResponse, JobRead
from app.services.horario_service import HorarioService
from app.workers.job_runner import executar

router = APIRouter(tags=["Horário"])


def _get_service(session: Session = Depends(get_session)) -> HorarioService:
    return HorarioService(session)


@router.post("/gerar-horario", response_model=GerarHorarioResponse, status_code=202)
def gerar_horario(background_tasks: BackgroundTasks, service: HorarioService = Depends(_get_service)):
    """RF09 (UC08) — dispara a geração em background e devolve o job_id de imediato."""
    job = service.disparar_geracao()
    background_tasks.add_task(executar, job.id)
    return GerarHorarioResponse(job_id=job.id, status=job.status)


@router.get("/jobs/{job_id}", response_model=JobRead)
def obter_job(job_id: str, service: HorarioService = Depends(_get_service)):
    """RF10 (UC10) — consulta de estado; RF13/UC09 quando status=INFEASIBLE (ver diagnostico)."""
    try:
        return service.consultar_job(job_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/horarios/turma/{turma_id}", response_model=HorarioResponseSchema)
def horario_por_turma(turma_id: int, service: HorarioService = Depends(_get_service)):
    """RF11 (UC11) — horário estruturado por dia/slot, a partir do Job DONE mais recente."""
    try:
        return service.consultar_horario_turma(turma_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/horarios/professor/{professor_id}", response_model=HorarioResponseSchema)
def horario_por_professor(professor_id: int, service: HorarioService = Depends(_get_service)):
    """RF12 (UC12) — horário estruturado por dia/slot, a partir do Job DONE mais recente."""
    try:
        return service.consultar_horario_professor(professor_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
