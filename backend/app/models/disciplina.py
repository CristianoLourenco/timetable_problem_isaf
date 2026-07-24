# Implementa: RF03 (UC03) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import Field, SQLModel

from app.core.abreviacoes import gerar_nome_curto


class Disciplina(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)  # chave de idempotência (RF08)
    nome: str
    # Nome reduzido para a grelha de horário (espaço limitado nas células) —
    # gerado automaticamente (ver core/abreviacoes.py) mas editável pelo
    # Gestor quando o resultado automático ficar confuso.
    nome_curto: str = Field(default="")

    def model_post_init(self, __context) -> None:
        if not self.nome_curto and self.nome:
            self.nome_curto = gerar_nome_curto(self.nome)
