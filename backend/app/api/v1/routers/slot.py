# Implementa: RF05 (UC05) — ver docs/04_04_analise_desenvolvimento.md
#
# Não existe tabela Slot nem BD envolvida aqui: a grelha de tempos letivos é calculada
# em runtime a partir de core/config.py (ver app/core/calendario.py). Sem isto o cliente
# não tem como saber a que dia/turno/período/hora corresponde cada tempo, para montar a
# grelha de disponibilidade (RF05) ou legendar o horário gerado (RF11/RF12).
from fastapi import APIRouter, Depends

from app.core.calendario import gerar_grelha_tempos
from app.core.security import UtilizadorAutenticado, get_current_user
from app.schemas.tempo_schema import TempoRead

router = APIRouter(prefix="/slots", tags=["Slots"])


@router.get("", response_model=list[TempoRead])
def listar_tempos(user: UtilizadorAutenticado = Depends(get_current_user)):
    return gerar_grelha_tempos()
