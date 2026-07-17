from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+psycopg://isaf:isaf@localhost:5432/isaf_horarios"
    firebase_credentials_path: str = "./firebase-service-account.json"
    solver_max_time_seconds: int = 60
    # Sem isto, o CP-SAT usa por omissão todos os cores da máquina (portfolio de
    # workers, ver docs/04_02_fundamentacao_teorica.md secção 2.4.2) durante todo
    # o solver_max_time_seconds — mesmo correndo em BackgroundTasks (thread à
    # parte), satura a máquina inteira. Valor por omissão deixa alguns cores
    # livres para o resto do sistema; ajustar ao hardware real em produção.
    solver_num_search_workers: int = 4
    environment: str = "development"

    # Autenticação (RN09/RN10) — ver core/security.py. project_id vem do Firebase
    # Console (frontend/lib/core/config/firebase_config.dart); a verificação do ID
    # Token usa google-auth contra os certificados públicos do Google, sem exigir
    # firebase-service-account.json (que não está disponível neste projeto).
    firebase_project_id: str = "g-horario-b00eb"
    # Web API Key do Firebase (pública — não é segredo, identifica o projeto; ver
    # frontend/lib/core/config/firebase_config.dart). Usada para chamar a REST API do
    # Identity Toolkit (login, refresh, recuperação de password, login Google) a
    # partir do backend — o login NÃO é feito no cliente Flutter (ver core/firebase_rest.py).
    firebase_web_api_key: str = "AIzaSyCcmvG_mtxbvyMQnIcFynm2WWv_SwS7wXI"
    # URI arbitrário exigido pelo endpoint accounts:signInWithIdp do Firebase para o
    # login com Google — não é um redirect real (o Google ID Token já vem do cliente),
    # só precisa de ser um URI sintaticamente válido associado ao projeto.
    google_login_request_uri: str = "https://g-horario-b00eb.firebaseapp.com"
    # Bootstrap do primeiro perfil Superadmin — não tem tabela própria (ver
    # backend/CLAUDE.md Fase 6); só Superadmin pode criar Utilizador(perfil=GESTOR).
    superadmin_emails: list[str] = []

    # Pesos da função objetivo do solver (docs/analise_requisitos_v5.0.md secção 6).
    # Valores relativos ainda não fixados pela banca/orientador (secção 9 — pergunta em
    # aberto); ordem de grandeza reflete "penalização muito alta" (RN08) > "alta" (RN04)
    # > equidade, conforme classificação da tabela de RNs.
    solver_peso_rn04_disponibilidade: int = 10
    solver_peso_rn08_capacidade: int = 20
    solver_peso_equidade_diaria: int = 1

    # Calendário letivo — nunca hardcoded fora daqui (ver CLAUDE.md, proibições gerais).
    # Valores por omissão servem apenas de bootstrap para ambiente local/dev.
    # Não existe tabela Slot (ver docs/04_04_analise_desenvolvimento.md secção 4.2.4) —
    # dia_semana + turno + periodo são campos simples; a grelha de horas reais é
    # calculada a partir daqui em app/core/calendario.py, nunca persistida.
    slot_dias_semana: list[str] = ["segunda", "terca", "quarta", "quinta", "sexta"]
    turno_periodos: dict[str, int] = {"manha": 6, "tarde": 5, "noite": 5}
    turno_hora_inicio: dict[str, str] = {"manha": "07:30", "tarde": "13:00", "noite": "18:00"}
    slot_duracao_minutos: int = 45


settings = Settings()
