from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+psycopg://isaf:isaf@localhost:5432/isaf_horarios"
    firebase_credentials_path: str = "./firebase-service-account.json"
    solver_max_time_seconds: int = 60
    environment: str = "development"

    # Calendário letivo — nunca hardcoded fora daqui (ver CLAUDE.md, proibições gerais).
    # Valores por omissão servem apenas de bootstrap para ambiente local/dev.
    slot_dias_semana: list[str] = ["segunda", "terca", "quarta", "quinta", "sexta"]
    slot_tempos_por_dia: int = 9
    slot_inicio_primeiro_tempo: str = "07:30"
    slot_duracao_minutos: int = 45


settings = Settings()
