# Implementa: RF02 (UC02) — ver docs/analise_requisitos_v5.0.md
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.api.v1.routers.factory import build_crud_router
from app.core.security import require_gestor
from app.models.turma import Turma
from app.repositories.turma_repository import TurmaRepository
from app.schemas.turma_schema import TurmaCreate, TurmaDetalhadaSchema, TurmaRead, TurmaUpdate
from app.services.turma_service import listar_turmas_detalhadas

router = build_crud_router(
    prefix="/turmas",
    tags=["Turmas"],
    model=Turma,
    create_schema=TurmaCreate,
    update_schema=TurmaUpdate,
    read_schema=TurmaRead,
    repository_cls=TurmaRepository,
)

# Path distinto de /turmas/{id_} (registado pela fábrica acima) para não colidir.
router_detalhado = APIRouter(tags=["Turmas"], dependencies=[Depends(require_gestor)])


@router_detalhado.get("/turmas-detalhadas", response_model=list[TurmaDetalhadaSchema])
def turmas_detalhadas(session: Session = Depends(get_session)):
    """RF02 — Turma já com curso_codigo/curso_nome/ano_curricular resolvidos, para
    o frontend não montar essa junção por conta própria (ver turma_service.py)."""
    return listar_turmas_detalhadas(session)
