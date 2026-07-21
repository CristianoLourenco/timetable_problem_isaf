#!/usr/bin/env python3
# Implementa: RNF01/CT07 — benchmark contra os dados REAIS do ISAF (currículo
# extraído dos PDFs institucionais, ver seed_dados_teste.py e docs/exemplar_isaf/),
# não um cenário sintético — evidência empírica à escala mais próxima do RNF01
# (100+ professores, 60+ turmas) disponível neste trabalho.
#
# NUNCA correr via pytest/CI — exige a BD real semeada (docker compose up -d +
# seed_dados_teste.py) e pode demorar vários minutos (job_runner.executar
# escalona 2→5→10 min se a 1ª tentativa não convergir). Só leitura da BD — não
# persiste nenhum Job/Alocacao, seguro para correr repetidamente.
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import engine  # noqa: E402
from app.services.horario_service import extrair_dados  # noqa: E402
from app.solver.orquestrador_turnos import resolver_horario_por_turnos  # noqa: E402

ANO_LETIVO = 2026
SEMESTRE = "1"
ORCAMENTO_SEGUNDOS = 120.0  # 1ª tentativa do escalonamento automático (job_runner.ESCALONAMENTO_TEMPO_MINUTOS[0])


def main() -> None:
    with Session(engine) as session:
        dados = extrair_dados(session, ano_letivo=ANO_LETIVO, semestre=SEMESTRE)

    total_esperado = sum(td.carga_horaria_semanal for td in dados.turma_disciplinas)
    print(
        f"Cenário real ISAF ({ANO_LETIVO}/{SEMESTRE}): {len(dados.turmas)} turmas, "
        f"{len(dados.professores)} professores, {len(dados.salas)} salas, "
        f"{total_esperado} tempos lectivos esperados"
    )

    t0 = time.perf_counter()
    resultado = resolver_horario_por_turnos(
        dados,
        max_time_in_seconds_total=ORCAMENTO_SEGUNDOS,
        num_search_workers=settings.solver_num_search_workers,
    )
    tempo = time.perf_counter() - t0

    n_alocado = len(resultado.alocacoes)
    deficit = total_esperado - n_alocado
    turmas_com_deficit = len({p.turma_id for p in resultado.pendencias})
    salas_por_turma: dict[int, set[int]] = {}
    for a in resultado.alocacoes:
        salas_por_turma.setdefault(a.turma_id, set()).add(a.sala_id)
    turmas_multi_sala = [t for t, s in salas_por_turma.items() if len(s) > 1]

    print(f"\ntempo={tempo:.1f}s status={resultado.status}")
    print(f"alocações={n_alocado}/{total_esperado} (défice={deficit}, {100 * n_alocado / total_esperado:.1f}% cobertura)")
    print(f"turmas com défice: {turmas_com_deficit}/{len(dados.turmas)}")
    print(f"turmas com mais de 1 sala no mesmo turno: {len(turmas_multi_sala)} (esperado: 0)")


if __name__ == "__main__":
    main()
