# Implementa: RF09, RF10 (UC08, UC10) — ver docs/analise_requisitos_v5.0.md
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.exceptions import EntidadeNaoEncontradaError
from app.core.security import UtilizadorAutenticado, get_current_user, require_gestor, verificar_acesso_professor_proprio
from app.schemas.horario_schema import HorarioResponseSchema
from app.schemas.job_schema import GerarHorarioResponse, JobRead
from app.services.horario_service import HorarioService
from app.workers.job_runner import executar

router = APIRouter(tags=["Horário"])


def _get_service(session: Session = Depends(get_session)) -> HorarioService:
    return HorarioService(session)


@router.post("/gerar-horario", response_model=GerarHorarioResponse, status_code=202, dependencies=[Depends(require_gestor)])
def gerar_horario(background_tasks: BackgroundTasks, service: HorarioService = Depends(_get_service)):
    """RF09 (UC08) — dispara a geração em background e devolve o job_id de imediato."""
    job = service.disparar_geracao()
    background_tasks.add_task(executar, job.id)
    return GerarHorarioResponse(job_id=job.id, status=job.status)


@router.get("/jobs/{job_id}", response_model=JobRead, dependencies=[Depends(require_gestor)])
def obter_job(job_id: str, service: HorarioService = Depends(_get_service)):
    """RF10 (UC10) — consulta de estado; RF13/UC09 quando status=INFEASIBLE (ver diagnostico)."""
    try:
        return service.consultar_job(job_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/horarios/turma/{turma_id}", response_model=HorarioResponseSchema, dependencies=[Depends(require_gestor)])
def horario_por_turma(turma_id: int, service: HorarioService = Depends(_get_service)):
    """RF11 (UC11) — actor exclusivo Gestor; horário estruturado por dia/slot."""
    try:
        return service.consultar_horario_turma(turma_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/horarios/professor/{professor_id}", response_model=HorarioResponseSchema)
def horario_por_professor(
    professor_id: int,
    service: HorarioService = Depends(_get_service),
    user: UtilizadorAutenticado = Depends(get_current_user),
):
    """RF12 (UC12) — Gestor vê qualquer professor; Professor só o seu próprio (RN11/UC15)."""
    verificar_acesso_professor_proprio(user, professor_id)
    try:
        return service.consultar_horario_professor(professor_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
