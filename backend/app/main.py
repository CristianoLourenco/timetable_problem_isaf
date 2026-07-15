from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ISAF — Sistema Inteligente de Geração de Horários", version="0.1.0")

# CORS aberto em desenvolvimento para o cliente Flutter (web/mobile). Restringir origins em produção.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
