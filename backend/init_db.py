"""Cria as tabelas da base de dados.

Não existe seed de grelha de tempos: dia_semana + turno + periodo são calculados em
runtime a partir de core/config.py (ver app/core/calendario.py) — não há tabela Slot
para semear (ver docs/04_04_analise_desenvolvimento.md secção 4.2.4).

Uso: python init_db.py
"""

import app.models  # noqa: F401 - garante que todos os modelos são registados no metadata
from app.core.database import init_db

if __name__ == "__main__":
    init_db()
    print("Tabelas criadas.")
