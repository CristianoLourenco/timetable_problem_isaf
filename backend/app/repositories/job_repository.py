# Implementa: RF09, RF10, RF13 (UC08, UC09, UC10) — ver docs/analise_requisitos_v5.0.md
from datetime import datetime

from sqlmodel import Session, select

from app.models.job import Job, JobStatus


class JobRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar(self, ano_letivo: int, semestre: str) -> Job:
        # tempo_maximo_minutos nunca é escolhido aqui — job_runner.py define-o a
        # cada tentativa do escalonamento automático (RF13, ESCALONAMENTO_TEMPO_MINUTOS).
        job = Job(ano_letivo=ano_letivo, semestre=semestre)
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def obter(self, job_id: str) -> Job | None:
        return self.session.get(Job, job_id)

    def obter_ultimo_concluido(self) -> Job | None:
        """RF12 — horário "atual" de um Professor: o Job DONE mais recente entre
        todos os âmbitos (um professor não está preso a um único ano/semestre)."""
        return self.session.exec(
            select(Job).where(Job.status == JobStatus.DONE).order_by(Job.concluido_em.desc())
        ).first()

    def obter_ultimo_para(self, ano_letivo: int, semestre: str) -> Job | None:
        """Job mais recente (qualquer status) do (ano_letivo, semestre) exato pedido
        — para o frontend distinguir "ainda não gerado" de "a gerar"/"falhou"/"pronto"
        ao consultar um âmbito específico (botão "limpar horário", filtro de
        ano/semestre na tela de Horários). Ao contrário de `obter_ultimo_concluido_para`,
        não filtra por DONE nem aceita "Anual" — é sempre o âmbito exato de um Job
        (RF09), nunca a regra de exibição de uma Turma específica."""
        return self.session.exec(
            select(Job)
            .where(Job.ano_letivo == ano_letivo, Job.semestre == semestre)
            .order_by(Job.criado_em.desc())
        ).first()

    def remover(self, job: Job) -> None:
        """Botão "limpar horário" — apaga o Job; Alocacao/Pendencia associadas são
        removidas pelo repositório chamador antes disto (ver AlocacaoManualService
        para o padrão equivalente), nunca aqui — este repositório só conhece Job."""
        self.session.delete(job)
        self.session.commit()

    def obter_ultimo_concluido_para(self, ano_letivo: int, semestres: list[str]) -> Job | None:
        """RF11 — horário de uma Turma: o Job DONE mais recente do (ano_letivo,
        semestre) exato dessa turma, nunca "o mais recente entre todos" (que
        poderia pertencer a um âmbito diferente e simplesmente não conter a turma
        pedida). `semestres` recebe mais do que um valor apenas para turmas de
        um PlanoCurricular "Anual" — o Job pode ter sido gerado como "1" ou "2"."""
        return self.session.exec(
            select(Job)
            .where(
                Job.status == JobStatus.DONE,
                Job.ano_letivo == ano_letivo,
                Job.semestre.in_(semestres),
            )
            .order_by(Job.concluido_em.desc())
        ).first()

    def atualizar_status(
        self,
        job: Job,
        status: JobStatus,
        *,
        diagnostico: str | None = None,
        concluido_em: datetime | None = None,
    ) -> Job:
        job.status = status
        job.diagnostico = diagnostico
        job.concluido_em = concluido_em
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job
