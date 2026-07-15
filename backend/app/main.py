from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import curso, disciplina, disponibilidade, importacao, professor, sala, turma

app = FastAPI(title="ISAF — Sistema Inteligente de Geração de Horários", version="0.1.0")

# CORS aberto em desenvolvimento para o cliente Flutter (web/mobile). Restringir origins em produção.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(curso.router)
app.include_router(professor.router)
app.include_router(turma.router)
app.include_router(disciplina.router)
app.include_router(sala.router)
app.include_router(disponibilidade.router)
app.include_router(importacao.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
