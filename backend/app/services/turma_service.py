# Implementa: RF02 (UC02) — ver docs/relatorio/04_analise_desenvolvimento/
from sqlmodel import Session

from app.repositories.curso_repository import CursoRepository
from app.repositories.plano_curricular_repository import PlanoCurricularRepository
from app.repositories.turma_repository import TurmaRepository
from app.schemas.turma_schema import TurmaDetalhadaSchema


def listar_turmas_detalhadas(session: Session) -> list[TurmaDetalhadaSchema]:
    """RF02 — todas as Turma já com curso_codigo/curso_nome/ano_curricular
    resolvidos, para o frontend não ter de fazer Turma -> PlanoCurricular -> Curso
    por conta própria (causa provável de "turmas às vezes não trazem os seus
    dados" — a junção falhando silenciosamente do lado do cliente)."""
    turmas = TurmaRepository(session).list()
    planos = {p.id: p for p in PlanoCurricularRepository(session).list()}
    cursos = {c.id: c for c in CursoRepository(session).list()}

    resultado = []
    for turma in turmas:
        plano = planos.get(turma.plano_curricular_id)
        curso = cursos.get(plano.curso_id) if plano else None
        resultado.append(
            TurmaDetalhadaSchema(
                id=turma.id,
                codigo=turma.codigo,
                nome=turma.nome,
                ano_letivo=turma.ano_letivo,
                turno=turma.turno,
                numero_alunos=turma.numero_alunos,
                plano_curricular_id=turma.plano_curricular_id,
                curso_codigo=curso.codigo if curso else "?",
                curso_nome=curso.nome if curso else "Curso não encontrado",
                ano_curricular=plano.ano if plano else 0,
            )
        )
    return resultado
