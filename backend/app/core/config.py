from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+psycopg://isaf:isaf@localhost:5432/isaf_horarios"
    firebase_credentials_path: str = "./firebase-service-account.json"
    solver_max_time_seconds: int = 60
    environment: str = "development"

    # Autenticação (RN09/RN10) — ver core/security.py. project_id vem do Firebase
    # Console (frontend/lib/core/config/firebase_config.dart); a verificação do ID
    # Token usa google-auth contra os certificados públicos do Google, sem exigir
    # firebase-service-account.json (que não está disponível neste projeto).
    firebase_project_id: str = "g-horario-b00eb"
    # Bootstrap do primeiro perfil Superadmin — não tem tabela própria (ver
    # backend/docs/CONVENCOES.md Fase 6); só Superadmin pode criar Utilizador(perfil=GESTOR).
    superadmin_emails: list[str] = []

    # Pesos da função objetivo do solver (docs/analise_requisitos_v5.0.md secção 6).
    # Valores relativos ainda não fixados pela banca/orientador (secção 9 — pergunta em
    # aberto); ordem de grandeza reflete "penalização muito alta" (RN08) > "alta" (RN04)
    # > equidade, conforme classificação da tabela de RNs.
    solver_peso_rn04_disponibilidade: int = 10
    solver_peso_rn08_capacidade: int = 20
    solver_peso_equidade_diaria: int = 1

    # Calendário letivo — nunca hardcoded fora daqui (ver docs/CONVENCOES.md, proibições gerais).
    # Valores por omissão servem apenas de bootstrap para ambiente local/dev.
    slot_dias_semana: list[str] = ["segunda", "terca", "quarta", "quinta", "sexta"]
    slot_tempos_por_dia: int = 9
    slot_inicio_primeiro_tempo: str = "07:30"
    slot_duracao_minutos: int = 45


settings = Settings()
