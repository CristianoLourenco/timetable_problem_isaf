# Implementa: RF13 (UC09) — alocação manual do Gestor, reaproveita RN01-RN06 como
# validação imperativa (nunca CP-SAT) sobre Alocacao já persistidas.
from collections import defaultdict

from sqlmodel import Session, select

from app.core.calendario import gerar_grelha_tempos
from app.core.exceptions import EntidadeNaoEncontradaError, IntegridadeVioladaError
from app.models.alocacao import Alocacao
from app.models.professor import Professor
from app.repositories.alocacao_repository import AlocacaoRepository
from app.repositories.pendencia_repository import PendenciaRepository
from app.repositories.professor_disciplina_repository import ProfessorDisciplinaRepository
from app.repositories.professor_repository import ProfessorRepository
from app.repositories.sala_repository import SalaRepository
from app.repositories.turma_repository import TurmaRepository


class AlocacaoManualService:
    """RF13/UC09 — o Gestor escolhe professor+turma+disciplina+slot livremente para
    preencher uma pendência (ou reorganizar o horário já gerado). Reaplica RN01
    (professor sem dupla alocação), RN02 (turma sem dupla disciplina), RN03 (sala sem
    dupla turma) e RN06 (bloco contíguo >=2 tempos) diretamente contra as Alocacao já
    persistidas desse job — nunca contra variáveis do CP-SAT, que não existem fora do
    solve. Qualificação (ProfessorDisciplina) é hard de facto: o Gestor só consegue
    escolher um professor já habilitado para a disciplina."""

    def __init__(self, session: Session):
        self.session = session
        self.alocacao_repo = AlocacaoRepository(session)
        self.pendencia_repo = PendenciaRepository(session)
        self.turma_repo = TurmaRepository(session)
        self.sala_repo = SalaRepository(session)
        self.professor_repo = ProfessorRepository(session)
        self.professor_disciplina_repo = ProfessorDisciplinaRepository(session)

    def criar(
        self,
        *,
        job_id: str,
        turma_id: int,
        disciplina_id: int,
        professor_id: int,
        sala_id: int,
        dia_semana: str,
        turno: str,
        periodos: list[int],
    ) -> list[Alocacao]:
        if self.turma_repo.get(turma_id) is None:
            raise EntidadeNaoEncontradaError(f"Turma {turma_id} não encontrada.")
        if self.sala_repo.get(sala_id) is None:
            raise EntidadeNaoEncontradaError(f"Sala {sala_id} não encontrada.")

        self._validar_bloco(periodos)
        self._validar_qualificacao(professor_id, disciplina_id)

        for periodo in periodos:
            self._validar_sem_conflito(
                job_id=job_id,
                turma_id=turma_id,
                professor_id=professor_id,
                sala_id=sala_id,
                dia_semana=dia_semana,
                turno=turno,
                periodo=periodo,
            )

        alocacoes = [
            Alocacao(
                job_id=job_id,
                turma_id=turma_id,
                disciplina_id=disciplina_id,
                professor_id=professor_id,
                sala_id=sala_id,
                dia_semana=dia_semana,
                periodo=periodo,
            )
            for periodo in periodos
        ]
        self.alocacao_repo.criar_em_lote(alocacoes)
        # Remove a pendência inteira desta (turma, disciplina) — se o bloco alocado
        # não cobrir todo o défice, o Gestor volta a chamar POST /alocacoes para o
        # resto (não há défice residual persistido; um novo GET pendencias já não
        # a mostra até a próxima geração automática confirmar que ainda falta algo).
        self.pendencia_repo.remover_por_turma_disciplina(job_id, turma_id, disciplina_id)
        return alocacoes

    def _validar_bloco(self, periodos: list[int]) -> None:
        """RN06 — bloco contíguo >=2 tempos, sem tempo isolado."""
        if len(periodos) < 2:
            raise IntegridadeVioladaError(
                "RN06: um bloco de alocação manual precisa de pelo menos 2 tempos contíguos "
                "(nunca um tempo isolado)."
            )
        ordenados = sorted(periodos)
        if any(ordenados[i + 1] - ordenados[i] != 1 for i in range(len(ordenados) - 1)):
            raise IntegridadeVioladaError(
                "RN06: os períodos do bloco têm de ser contíguos (ex: [1,2], nunca [1,3])."
            )

    def _validar_qualificacao(self, professor_id: int, disciplina_id: int) -> None:
        if not self.professor_disciplina_repo.existe(professor_id, disciplina_id):
            raise IntegridadeVioladaError(
                f"Professor {professor_id} não está qualificado (ProfessorDisciplina) para a "
                f"disciplina {disciplina_id}."
            )

    def _validar_sem_conflito(
        self,
        *,
        job_id: str,
        turma_id: int,
        professor_id: int,
        sala_id: int,
        dia_semana: str,
        turno: str,
        periodo: int,
        ignorar_id: int | None = None,
    ) -> None:
        existentes = self.session.exec(
            select(Alocacao).where(
                Alocacao.job_id == job_id,
                Alocacao.dia_semana == dia_semana,
                Alocacao.periodo == periodo,
            )
        ).all()
        for aloc in existentes:
            if aloc.id == ignorar_id:
                continue
            if aloc.professor_id == professor_id:
                raise IntegridadeVioladaError(
                    f"RN01: professor {professor_id} já tem alocação em {dia_semana}/{turno}/{periodo}."
                )
            if aloc.turma_id == turma_id:
                raise IntegridadeVioladaError(
                    f"RN02: turma {turma_id} já tem disciplina alocada em {dia_semana}/{turno}/{periodo}."
                )
            if aloc.sala_id == sala_id:
                raise IntegridadeVioladaError(
                    f"RN03: sala {sala_id} já está ocupada em {dia_semana}/{turno}/{periodo}."
                )

    def listar_professores_qualificados(self, disciplina_id: int) -> list[Professor]:
        """RF13 — dropdown 1: só professores com ProfessorDisciplina para a disciplina."""
        ids = self.professor_disciplina_repo.listar_por_disciplina(disciplina_id)
        return [p for p in (self.professor_repo.get(i) for i in ids) if p is not None]

    def listar_slots_vagos(self, turma_id: int, job_id: str) -> list[dict]:
        """RF13 — dropdown 2: slots do turno da turma sem Alocacao(job_id, turma_id),
        agrupados em blocos contíguos >=2 por dia (RN06) — nunca um período isolado."""
        turma = self.turma_repo.get(turma_id)
        if turma is None:
            raise EntidadeNaoEncontradaError(f"Turma {turma_id} não encontrada.")

        ocupados = {
            (a.dia_semana, a.periodo)
            for a in self.alocacao_repo.listar_por_job_e_turma(job_id, turma_id)
        }

        periodos_por_dia: dict[str, list[int]] = defaultdict(list)
        for slot in gerar_grelha_tempos():
            if slot.turno == turma.turno:
                periodos_por_dia[slot.dia_semana].append(slot.periodo)

        blocos = []
        for dia_semana, periodos in periodos_por_dia.items():
            for periodo_inicio, tamanho in self._blocos_contiguos_livres(sorted(periodos), dia_semana, ocupados):
                if tamanho >= 2:
                    blocos.append(
                        {
                            "dia_semana": dia_semana,
                            "turno": turma.turno,
                            "periodos": list(range(periodo_inicio, periodo_inicio + tamanho)),
                        }
                    )
        return blocos

    @staticmethod
    def _blocos_contiguos_livres(
        periodos_do_turno: list[int], dia_semana: str, ocupados: set[tuple[str, int]]
    ) -> list[tuple[int, int]]:
        """Devolve (periodo_inicio, tamanho) de cada sequência maximal de períodos
        livres e contíguos dentro dos períodos do turno, nesse dia."""
        blocos: list[tuple[int, int]] = []
        inicio_atual: int | None = None
        anterior: int | None = None
        for periodo in periodos_do_turno:
            livre = (dia_semana, periodo) not in ocupados
            contiguo = anterior is not None and periodo == anterior + 1
            if livre and inicio_atual is not None and contiguo:
                pass  # continua o bloco atual
            elif livre:
                if inicio_atual is not None:
                    blocos.append((inicio_atual, anterior - inicio_atual + 1))
                inicio_atual = periodo
            else:
                if inicio_atual is not None:
                    blocos.append((inicio_atual, anterior - inicio_atual + 1))
                inicio_atual = None
            anterior = periodo
        if inicio_atual is not None:
            blocos.append((inicio_atual, anterior - inicio_atual + 1))
        return blocos

    def remover(self, alocacao_id: int) -> None:
        """RF13 — remove uma alocação; se isso reabre défice nessa (turma,
        disciplina), recria a Pendencia com razão genérica (não isola causa —
        foi o próprio Gestor que removeu, não um conflito automático)."""
        alocacao = self.alocacao_repo.get(alocacao_id)
        if alocacao is None:
            raise EntidadeNaoEncontradaError(f"Alocação {alocacao_id} não encontrada.")

        job_id, turma_id, disciplina_id = alocacao.job_id, alocacao.turma_id, alocacao.disciplina_id
        self.alocacao_repo.remover(alocacao)

        ja_pendente = any(
            p.disciplina_id == disciplina_id
            for p in self.pendencia_repo.listar_por_job_e_turma(job_id, turma_id)
        )
        if not ja_pendente:
            # tempos_em_falta=1: só se sabe que ESTE período reabriu; o défice
            # exato (carga_horaria_semanal - alocações restantes) fica para uma
            # versão futura que reconsulte PlanoCurricularDisciplina aqui.
            self.pendencia_repo.criar_em_lote(
                job_id,
                [
                    {
                        "turma_id": turma_id,
                        "disciplina_id": disciplina_id,
                        "tempos_em_falta": 1,
                        "razao": "Removido manualmente pelo Gestor.",
                        "professores_conflitantes": (),
                        "turmas_conflitantes": (),
                    }
                ],
            )

    def mover(self, alocacao_id: int, *, dia_semana: str, periodo: int) -> Alocacao:
        """RF13 — move um único período de uma alocação existente para outro slot,
        reaplicando RN01-RN03 contra o novo valor (nunca edita o bloco inteiro de
        uma vez — o Gestor move período a período)."""
        alocacao = self.alocacao_repo.get(alocacao_id)
        if alocacao is None:
            raise EntidadeNaoEncontradaError(f"Alocação {alocacao_id} não encontrada.")

        turma = self.turma_repo.get(alocacao.turma_id)
        turno = turma.turno if turma is not None else ""

        self._validar_sem_conflito(
            job_id=alocacao.job_id,
            turma_id=alocacao.turma_id,
            professor_id=alocacao.professor_id,
            sala_id=alocacao.sala_id,
            dia_semana=dia_semana,
            turno=turno,
            periodo=periodo,
            ignorar_id=alocacao.id,
        )
        return self.alocacao_repo.atualizar(alocacao, {"dia_semana": dia_semana, "periodo": periodo})
