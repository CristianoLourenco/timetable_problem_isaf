# Implementa: RF09, RF10, RF11, RF12 (UC08, UC10, UC11, UC12) — ver docs/relatorio/04_analise_desenvolvimento/
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.exceptions import EntidadeNaoEncontradaError
from app.core.security import UtilizadorAutenticado, get_current_user, require_gestor, verificar_acesso_professor_proprio
from app.schemas.horario_schema import HorarioResponseSchema
from app.schemas.job_schema import GerarHorarioRequest, GerarHorarioResponse, JobDeAmbitoResponse, JobRead
from app.services.exportacao_pdf_service import gerar_pdf_turma, gerar_zip_por_job
from app.services.horario_service import HorarioService
from app.workers.job_runner import executar

router = APIRouter(tags=["Horário"])


def _get_service(session: Session = Depends(get_session)) -> HorarioService:
    return HorarioService(session)


@router.post("/gerar-horario", response_model=GerarHorarioResponse, status_code=202, dependencies=[Depends(require_gestor)])
def gerar_horario(
    payload: GerarHorarioRequest,
    background_tasks: BackgroundTasks,
    service: HorarioService = Depends(_get_service),
):
    """RF09 (UC08) — gera de uma vez o horário completo de todas as turmas do
    (ano_letivo, semestre) pedido; dispara em background e devolve o job_id de imediato."""
    job = service.disparar_geracao(payload.ano_letivo, payload.semestre)
    background_tasks.add_task(executar, job.id)
    return GerarHorarioResponse(job_id=job.id, status=job.status)


@router.get("/jobs/{job_id}", response_model=JobRead, dependencies=[Depends(require_gestor)])
def obter_job(job_id: str, service: HorarioService = Depends(_get_service)):
    """RF10 (UC10) — consulta de estado; RF13/UC09 quando status=INFEASIBLE (ver diagnostico)."""
    try:
        return service.consultar_job(job_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/jobs", response_model=JobDeAmbitoResponse, dependencies=[Depends(require_gestor)])
def obter_job_de_ambito(ano_letivo: int, semestre: str, service: HorarioService = Depends(_get_service)):
    """RF09/RF10 — Job mais recente (qualquer status) de um (ano_letivo, semestre)
    exato, para a tela de Horários trocar de filtro sem esconder/misturar âmbitos
    diferentes. `job=null` (200) é o estado "ainda não gerado" — nunca 404, é um
    estado normal da UI, não um erro."""
    job = service.consultar_job_de_ambito(ano_letivo, semestre)
    return JobDeAmbitoResponse(job=job)


@router.delete("/jobs/{job_id}", status_code=204, dependencies=[Depends(require_gestor)])
def limpar_horario(job_id: str, service: HorarioService = Depends(_get_service)):
    """RF09 — botão "limpar horário": apaga o Job e as Alocacao/Pendencia associadas,
    para o Gestor poder gerar de novo o mesmo âmbito do zero."""
    try:
        service.limpar_horario(job_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get(
    "/horarios/turma/{turma_id}", response_model=HorarioResponseSchema | None, dependencies=[Depends(require_gestor)]
)
def horario_por_turma(turma_id: int, service: HorarioService = Depends(_get_service)):
    """RF11 (UC11) — actor exclusivo Gestor; horário estruturado por dia/slot.
    200 com corpo `null` quando a turma existe mas ainda não há horário gerado
    para o seu âmbito — "ainda não gerado" não é um erro (ver horario_service.py)."""
    try:
        return service.consultar_horario_turma(turma_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/horarios/professor/{professor_id}", response_model=HorarioResponseSchema)
def horario_por_professor(
    professor_id: int,
    ano_letivo: int | None = None,
    semestre: str | None = None,
    service: HorarioService = Depends(_get_service),
    user: UtilizadorAutenticado = Depends(get_current_user),
):
    """RF12 (UC12) — Gestor vê qualquer professor; Professor só o seu próprio (RN11/UC15).

    (ano_letivo, semestre) opcionais: quando enviados (filtro de âmbito ativo na UI),
    escopam a busca ao Job DONE desse âmbito exato — evita que um professor sem
    aulas no âmbito mais recentemente gerado apareça com horário vazio (ver
    consultar_horario_professor). Omitidos, mantém o comportamento antigo (Job DONE
    mais recente entre todos os âmbitos)."""
    verificar_acesso_professor_proprio(user, professor_id)
    try:
        return service.consultar_horario_professor(professor_id, ano_letivo, semestre)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/horarios/turma/{turma_id}/pdf", dependencies=[Depends(require_gestor)])
def horario_por_turma_pdf(turma_id: int, session: Session = Depends(get_session)):
    """RF11 — PDF do horário desta turma, mesma estrutura visual dos exemplares reais
    do ISAF, com uma faixa distintiva a identificar geração automática."""
    try:
        pdf_bytes = gerar_pdf_turma(session, turma_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="horario_turma_{turma_id}.pdf"'},
    )


@router.get("/jobs/{job_id}/exportar-pdf", dependencies=[Depends(require_gestor)])
def exportar_horarios_do_job(job_id: str, session: Session = Depends(get_session)):
    """RF11 — .zip com um PDF por turma cobertas por este Job (RF09: um Job cobre
    sempre um único ano_letivo/semestre)."""
    try:
        zip_bytes = gerar_zip_por_job(session, job_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="horarios_{job_id}.zip"'},
    )
