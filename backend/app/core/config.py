from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+psycopg://isaf:isaf@localhost:5432/isaf_horarios"
    firebase_credentials_path: str = "./firebase-service-account.json"
    # 60s era demasiado curto à escala real do ISAF — medido: mesmo um único curso
    # completo (todos os 4 anos curriculares, 9-22 turmas) frequentemente não encontra
    # NENHUMA solução em 60s (UNKNOWN, não INFEASIBLE — o espaço de procura é genuinamente
    # grande, não impossível). RF09 já é assíncrono (BackgroundTasks) — esperar mais tempo
    # não bloqueia o pedido HTTP, só atrasa quando o Gestor vê o resultado. 300s (5min) dá
    # ao CP-SAT margem real para encontrar uma primeira solução viável nos cenários mais
    # densos; ajustar novamente se a escala real do ISAF continuar a precisar de mais.
    solver_max_time_seconds: int = 300
    # Sem isto, o CP-SAT usa por omissão todos os cores da máquina (portfolio de
    # workers, ver docs/04_02_fundamentacao_teorica.md secção 2.4.2) durante todo
    # o solver_max_time_seconds — mesmo correndo em BackgroundTasks (thread à
    # parte), satura a máquina inteira. O portfolio interno de sub-solvers do
    # CP-SAT só ativa estratégias focadas em encontrar a PRIMEIRA solução viável
    # a partir de 5 workers (documentação do CP-SAT) — com o valor antigo (4)
    # ficávamos mesmo abaixo desse limiar, exatamente quando "encontrar alguma
    # solução" (não otimizar) é o problema real medido à escala do ISAF. 8 é um
    # ponto de partida para desenvolvimento; ajustar ao nº de núcleos reais do
    # hardware de produção (mais núcleos = pode subir mais, até aos 12/16/32
    # onde o CP-SAT ativa progressivamente mais sub-solvers).
    solver_num_search_workers: int = 8
    # Aceita uma solução dentro deste gap do bound provado em vez de exigir
    # otimalidade — a função objetivo é uma soma de penalizações soft (RN04,
    # RN08, equidade, défice de RN05), nunca uma correção binária, logo uma
    # solução "boa o suficiente" encontrada depressa vale mais em produção do
    # que uma marginalmente melhor encontrada muito mais tarde (ou nunca).
    # 0.10 media, à escala real do turno Manhã do ISAF, um gap real de ~85%
    # nunca fechado — o CP-SAT gastava todo o orçamento tentando prová-lo em
    # vez de aceitar uma solução já boa. Medido em 2026-07-19: com 0.30, o
    # mesmo turno prova OPTIMAL em 75s (défice=14, melhor resultado obtido em
    # qualquer combinação testada) — 0.10 nunca convergiu no mesmo tempo.
    solver_relative_gap_limit: float = 0.30
    # Bisecção de diagnóstico (app/solver/diagnostico.py) — só corre quando o CP-SAT já
    # provou INFEASIBLE no solve principal (nunca para decidir UNKNOWN vs INFEASIBLE) e
    # as verificações baratas não encontraram nenhuma causa óbvia. Tempo limitado por
    # tentativa e no total para nunca virar nova fonte de lentidão — se o orçamento
    # esgotar sem confirmar nada, mantém-se a mensagem genérica em vez de arriscar um
    # falso positivo (ver isolar_nucleo_infeasible).
    solver_diagnostico_timeout_por_tentativa: float = 5.0
    solver_diagnostico_orcamento_total: float = 60.0
    # Cada tentativa da bisecção reconstrói o modelo do zero — a escala real do ISAF
    # isso sozinho pode demorar mais do que o orçamento total, fazendo a bisecção
    # esgotar o tempo a meio de uma ronda e devolver um núcleo grande (quase o
    # conjunto original) em vez de pequeno e acionável. Um núcleo maior do que isto
    # não vale a pena mostrar ao Gestor — mantém-se a mensagem genérica nesse caso.
    solver_diagnostico_tamanho_maximo_util: int = 12
    # Limite de salas candidatas por turma na geração esparsa de variáveis (RN08 é soft
    # — "capacidade mínima viável" — mas incluir TODAS as salas com capacidade suficiente
    # como candidatas cria simetria severa entre salas de capacidade semelhante e infla o
    # nº de BoolVar sem benefício real: uma sala com muito mais excesso de capacidade do
    # que outra nunca é preferida pelo objetivo, logo nunca seria escolhida numa solução
    # ótima a não ser forçada por conflito de outras turmas — o que as top-K mais próximas
    # já cobrem com folga. Medido no benchmark: reduz variáveis ~5-10x sem alterar a
    # qualidade prática da solução (ver docs/04_04_analise_desenvolvimento.md secção 4.4.1).
    solver_max_salas_candidatas: int = 5
    # Decomposição por turno (Manhã→Tarde→Noite, ver app/solver/orquestrador_turnos.py)
    # — reduz o tamanho de cada modelo CP-SAT individual em vez de resolver o
    # semestre inteiro num único modelo monolítico, tornando viável encontrar uma
    # solução completa dentro do orçamento de tempo à escala real do ISAF (RNF01).
    # Mantém-se o caminho monolítico vivo por trás da flag (não removido) — rollback
    # imediato e ponto de comparação para a discussão de RNF01 na tese.
    solver_usar_decomposicao_turno: bool = True
    # 3 fases × 100s = 300s, o mesmo teto já justificado de solver_max_time_seconds.
    solver_max_time_seconds_por_turno: int = 100
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
    # Sem default: sempre lida de FIREBASE_WEB_API_KEY em .env (ver .env.example) — nunca
    # hardcoded no repositório (scanner de secrets do GitHub sinaliza o valor literal).
    firebase_web_api_key: str
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
    # RF13 — défice de RN05 (carga horária não cumprida). Peso muito acima de
    # qualquer combinação plausível de RN04×prioridade (peso 10, multiplicador
    # até 2.0) + RN08 (peso 20) + equidade (peso 1) — o solver só aceita
    # défice quando preencher tudo é genuinamente impossível, nunca como troca
    # vantajosa face a uma otimização menor.
    solver_peso_deficit_rn05: int = 1000

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
