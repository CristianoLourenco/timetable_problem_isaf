# Implementa: RF09, RF10, RF11, RF12 (UC08, UC10, UC11, UC12) — ver docs/04_04_analise_desenvolvimento.md
#
# Passo 1 (Extração) do fluxo descrito em docs/04_04_analise_desenvolvimento.md secção 4.1:
# lê as entidades da BD e traduz para as dataclasses simples que o solver aceita.
# O solver nunca vê a Session nem os models SQLModel diretamente.
from collections import defaultdict

from sqlmodel import Session, select

from app.core.calendario import gerar_grelha_tempos
from app.core.config import settings
from app.core.exceptions import EntidadeNaoEncontradaError
from app.models.alocacao import Alocacao
from app.models.disponibilidade import Disponibilidade
from app.models.job import Job
from app.models.plano_curricular import PlanoCurricular
from app.models.plano_curricular_disciplina import PlanoCurricularDisciplina
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.turma import Turma
from app.repositories.alocacao_repository import AlocacaoRepository
from app.repositories.disciplina_repository import DisciplinaRepository
from app.repositories.job_repository import JobRepository
from app.repositories.plano_curricular_repository import PlanoCurricularRepository
from app.repositories.professor_repository import ProfessorRepository
from app.repositories.sala_repository import SalaRepository
from app.repositories.turma_repository import TurmaRepository
from app.schemas.horario_schema import HorarioDiaSchema, HorarioItemSchema, HorarioResponseSchema
from app.solver.dto import (
    DisponibilidadeDTO,
    HorarioInput,
    ProfessorDisciplinaDTO,
    ProfessorDTO,
    SalaDTO,
    SlotDTO,
    TurmaDisciplinaDTO,
    TurmaDTO,
)

# Ordem de exibição dos turnos num dia — não existe ordenação natural em string.
_ORDEM_TURNOS = ["manha", "tarde", "noite"]


def extrair_dados(session: Session, curso_id: int, ano_letivo: int, semestre: str) -> HorarioInput:
    """Lê as entidades relevantes da BD e monta o HorarioInput do solver, restrito às
    turmas de um único (curso, ano_letivo, semestre) — um Job gera sempre o horário
    completo desse âmbito de uma só vez (RF09), nunca turmas de cursos diferentes
    misturadas. Restringir por curso, além de ano_letivo/semestre, não é só uma questão
    de tamanho do problema: à escala real do ISAF confirmou-se que gerar vários cursos
    em simultâneo pode ser genuinamente INFEASIBLE (coortes pequenas com corpo docente
    muito reduzido/partilhado entre turmas paralelas do mesmo curso) mesmo sem nenhum
    erro de modelagem — e cursos diferentes não partilham turmas/salas/grade curricular
    entre si, logo não há benefício em otimizá-los juntos.

    Um PlanoCurricular com semestre="Anual" entra em ambos os âmbitos ("1" e "2"),
    já que as suas disciplinas decorrem ao longo do ano inteiro.

    turma_disciplinas é derivado de Turma.plano_curricular_id -> PlanoCurricularDisciplina
    (não existe TurmaDisciplina — grade curricular é partilhada por curso+ano+semestre,
    ver docs/04_04_analise_desenvolvimento.md secção 4.2.3). O solver continua a receber
    a mesma forma (turma_id, disciplina_id, carga_horaria_semanal) de sempre.
    """
    turmas = session.exec(
        select(Turma)
        .join(PlanoCurricular, Turma.plano_curricular_id == PlanoCurricular.id)
        .where(
            PlanoCurricular.curso_id == curso_id,
            Turma.ano_letivo == ano_letivo,
            PlanoCurricular.semestre.in_([semestre, "Anual"]),
        )
    ).all()
    professores = session.exec(select(Professor)).all()
    salas = session.exec(select(Sala)).all()
    itens_plano = session.exec(select(PlanoCurricularDisciplina)).all()
    professor_disciplinas = session.exec(select(ProfessorDisciplina)).all()
    disponibilidades = session.exec(select(Disponibilidade)).all()

    itens_por_plano: dict[int, list[PlanoCurricularDisciplina]] = defaultdict(list)
    for item in itens_plano:
        itens_por_plano[item.plano_curricular_id].append(item)

    turma_disciplinas = [
        TurmaDisciplinaDTO(
            turma_id=turma.id,
            disciplina_id=item.disciplina_id,
            carga_horaria_semanal=item.carga_horaria_semanal,
        )
        for turma in turmas
        for item in itens_por_plano.get(turma.plano_curricular_id, [])
    ]

    return HorarioInput(
        turmas=[TurmaDTO(id=t.id, numero_alunos=t.numero_alunos, turno=t.turno) for t in turmas],
        professores=[
            ProfessorDTO(id=p.id, classificacao=p.classificacao, vinculo_casa=p.vinculo_casa) for p in professores
        ],
        salas=[SalaDTO(id=s.id, capacidade=s.capacidade) for s in salas],
        slots=[SlotDTO(dia_semana=g.dia_semana, turno=g.turno, periodo=g.periodo) for g in gerar_grelha_tempos()],
        turma_disciplinas=turma_disciplinas,
        professor_disciplinas=[
            ProfessorDisciplinaDTO(professor_id=pd.professor_id, disciplina_id=pd.disciplina_id)
            for pd in professor_disciplinas
        ],
        disponibilidades=[
            DisponibilidadeDTO(professor_id=d.professor_id, dia_semana=d.dia_semana, turno=d.turno, periodo=d.periodo)
            for d in disponibilidades
        ],
    )


class HorarioService:
    """Orquestra o ciclo de vida do Job — quem executa o solver é workers/job_runner.py."""

    def __init__(self, session: Session):
        self.job_repo = JobRepository(session)
        self.alocacao_repo = AlocacaoRepository(session)
        self.turma_repo = TurmaRepository(session)
        self.professor_repo = ProfessorRepository(session)
        self.disciplina_repo = DisciplinaRepository(session)
        self.sala_repo = SalaRepository(session)
        self.plano_curricular_repo = PlanoCurricularRepository(session)

    def disparar_geracao(self, curso_id: int, ano_letivo: int, semestre: str) -> Job:
        """RF09 — cria o Job em PENDING para o âmbito (curso, ano_letivo, semestre); o
        router dispara job_runner.executar em BackgroundTasks."""
        return self.job_repo.criar(curso_id=curso_id, ano_letivo=ano_letivo, semestre=semestre)

    def consultar_job(self, job_id: str) -> Job:
        """RF10 — consulta de estado de processamento."""
        job = self.job_repo.obter(job_id)
        if job is None:
            raise EntidadeNaoEncontradaError("Job não encontrado.")
        return job

    def consultar_horario_turma(self, turma_id: int) -> HorarioResponseSchema:
        """RF11 (UC11) — horário da turma, a partir do Job DONE mais recente do
        (curso, ano_letivo, semestre) exato desta turma — nunca "o Job mais recente
        entre todos", que poderia ser de outro curso/ano/semestre e simplesmente não
        conter nenhuma alocação desta turma."""
        turma = self.turma_repo.get(turma_id)
        if turma is None:
            raise EntidadeNaoEncontradaError("Turma não encontrada.")

        plano = self.plano_curricular_repo.get(turma.plano_curricular_id)
        if plano is None:
            raise EntidadeNaoEncontradaError("Plano curricular da turma não encontrado.")
        semestres = ["1", "2"] if plano.semestre == "Anual" else [plano.semestre]

        job = self.job_repo.obter_ultimo_concluido_para(plano.curso_id, turma.ano_letivo, semestres)
        if job is None:
            raise EntidadeNaoEncontradaError(
                f"Ainda não existe horário gerado para o ano letivo {turma.ano_letivo}, "
                f"semestre {'/'.join(semestres)}, desta turma."
            )
        alocacoes = self.alocacao_repo.listar_por_job_e_turma(job.id, turma_id)
        return self._montar_resposta(job.id, alocacoes)

    def consultar_horario_professor(self, professor_id: int) -> HorarioResponseSchema:
        """RF12 (UC12) — horário do professor, a partir do Job DONE mais recente."""
        if self.professor_repo.get(professor_id) is None:
            raise EntidadeNaoEncontradaError("Professor não encontrado.")

        job = self._obter_ultimo_job_concluido()
        alocacoes = self.alocacao_repo.listar_por_job_e_professor(job.id, professor_id)
        return self._montar_resposta(job.id, alocacoes)

    def _obter_ultimo_job_concluido(self) -> Job:
        job = self.job_repo.obter_ultimo_concluido()
        if job is None:
            raise EntidadeNaoEncontradaError("Ainda não existe nenhum horário gerado com sucesso.")
        return job

    def _montar_resposta(self, job_id: str, alocacoes: list[Alocacao]) -> HorarioResponseSchema:
        """Traduz linhas de Alocacao em JSON estruturado por dia/tempo (nunca linhas soltas).

        Alocacao não guarda turno (é sempre o da Turma alocada, RN de normalização até
        à 3.ª Forma Normal — ver docs/media/src/diagrama_er.puml) — obtém-se aqui via
        turmas[aloc.turma_id].turno.
        """
        turmas = {t.id: t for t in self.turma_repo.list()}
        professores = {p.id: p for p in self.professor_repo.list()}
        disciplinas = {d.id: d for d in self.disciplina_repo.list()}
        salas = {s.id: s for s in self.sala_repo.list()}
        horas = {(g.dia_semana, g.turno, g.periodo): (g.hora_inicio, g.hora_fim) for g in gerar_grelha_tempos()}

        itens_por_dia: dict[str, list[HorarioItemSchema]] = defaultdict(list)
        for aloc in alocacoes:
            turno = turmas[aloc.turma_id].turno
            hora_inicio, hora_fim = horas[(aloc.dia_semana, turno, aloc.periodo)]
            itens_por_dia[aloc.dia_semana].append(
                HorarioItemSchema(
                    dia_semana=aloc.dia_semana,
                    turno=turno,
                    periodo=aloc.periodo,
                    hora_inicio=hora_inicio,
                    hora_fim=hora_fim,
                    turma_id=aloc.turma_id,
                    turma_nome=turmas[aloc.turma_id].nome,
                    disciplina_id=aloc.disciplina_id,
                    disciplina_nome=disciplinas[aloc.disciplina_id].nome,
                    professor_id=aloc.professor_id,
                    professor_nome=professores[aloc.professor_id].nome,
                    sala_id=aloc.sala_id,
                    sala_nome=salas[aloc.sala_id].nome,
                )
            )

        dias = [
            HorarioDiaSchema(
                dia_semana=dia,
                tempos=sorted(
                    itens_por_dia.get(dia, []),
                    key=lambda item: (_ORDEM_TURNOS.index(item.turno), item.periodo),
                ),
            )
            for dia in settings.slot_dias_semana
        ]
        return HorarioResponseSchema(job_id=job_id, dias=dias)
