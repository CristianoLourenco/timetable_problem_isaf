from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routers import (
    alocacao_manual,
    auth,
    curso,
    disciplina,
    disponibilidade,
    horario,
    importacao,
    plano_curricular,
    professor,
    professor_disciplina,
    sala,
    slot,
    turma,
    utilizador,
)
from app.core.exceptions import AcessoNegadoError, TokenInvalidoError

app = FastAPI(title="API - Sistema Inteligente para a Geração de Horários", version="0.1.0")

# CORS aberto em desenvolvimento para o cliente Flutter (web/mobile). Restringir origins em produção.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(TokenInvalidoError)
async def token_invalido_handler(request: Request, exc: TokenInvalidoError) -> JSONResponse:
    """RN09 — 401 se o ID Token Firebase estiver ausente, inválido ou expirado."""
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(AcessoNegadoError)
async def acesso_negado_handler(request: Request, exc: AcessoNegadoError) -> JSONResponse:
    """RN10/RN11 — 403 se o papel não tiver permissão ou o email não corresponder a nenhum perfil."""
    return JSONResponse(status_code=403, content={"detail": str(exc)})


app.include_router(auth.router)
app.include_router(utilizador.router)
app.include_router(curso.router)
app.include_router(professor.router)
app.include_router(turma.router)
app.include_router(turma.router_detalhado)
app.include_router(disciplina.router)
app.include_router(sala.router)
app.include_router(slot.router)
app.include_router(disponibilidade.router)
app.include_router(plano_curricular.router)
app.include_router(plano_curricular.itens_router)
app.include_router(professor_disciplina.router)
app.include_router(importacao.router)
app.include_router(horario.router)
app.include_router(alocacao_manual.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
