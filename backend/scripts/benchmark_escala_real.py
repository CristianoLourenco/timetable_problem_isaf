#!/usr/bin/env python3
# Implementa: RNF01 — benchmark manual à escala real do ISAF (100+ professores,
# 60+ turmas), comparando o solve monolítico com a decomposição por turno.
#
# NUNCA correr via pytest/CI — só manualmente (`python backend/scripts/benchmark_escala_real.py`),
# exatamente o mecanismo para validar RNF01 sem impor um teste de vários minutos à
# suite automática (ver docs/04_04_analise_desenvolvimento.md, decisão do utilizador
# de evitar testes de 10 minutos). Gera um HorarioInput sintético inteiramente em
# memória (sem BD) e reporta tempo de construção do modelo, nº de variáveis, tempo
# de resolução e status para ambas as abordagens.
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ortools.sat.python import cp_model  # noqa: E402

from app.core.calendario import gerar_grelha_tempos  # noqa: E402
from app.solver.builder import build_variables  # noqa: E402
from app.solver.dto import (  # noqa: E402
    HorarioInput,
    ProfessorDisciplinaDTO,
    ProfessorDTO,
    SalaDTO,
    SlotDTO,
    TurmaDisciplinaDTO,
    TurmaDTO,
)
from app.solver.orquestrador_turnos import resolver_horario_por_turnos  # noqa: E402
from app.solver.preprocessamento import podar_dominio  # noqa: E402
from app.solver.solve import resolver_horario  # noqa: E402

N_TURMAS_POR_TURNO = 20  # 60 turmas no total — escala RNF01 (60+)
N_PROFESSORES = 100  # escala RNF01 (100+)
N_DISCIPLINAS = 20
N_SALAS = 10
TURNOS = ("manha", "tarde", "noite")

MAX_TIME_MONOLITICO = 300.0  # settings.solver_max_time_seconds
MAX_TIME_TOTAL_DECOMPOSTO = 300.0  # orçamento agregado, distribuído por turno (ver _distribuir_orcamento)


def _construir_cenario() -> HorarioInput:
    turmas = []
    turma_disciplinas = []
    turma_id = 1
    for turno in TURNOS:
        for i in range(N_TURMAS_POR_TURNO):
            turmas.append(TurmaDTO(id=turma_id, numero_alunos=30, turno=turno))
            disciplina_a = (turma_id % N_DISCIPLINAS) + 1
            disciplina_b = ((turma_id + 1) % N_DISCIPLINAS) + 1
            turma_disciplinas.append(TurmaDisciplinaDTO(turma_id=turma_id, disciplina_id=disciplina_a, carga_horaria_semanal=2))
            turma_disciplinas.append(TurmaDisciplinaDTO(turma_id=turma_id, disciplina_id=disciplina_b, carga_horaria_semanal=3))
            turma_id += 1

    professores = [ProfessorDTO(id=p, classificacao=(p % 5) + 1, vinculo_casa=(p % 2 == 0)) for p in range(1, N_PROFESSORES + 1)]

    # Cada disciplina tem vários professores qualificados (round-robin) — evita a
    # colisão "único professor qualificado" que já causou INFEASIBLE real à escala
    # do ISAF (ver commit 6328dac).
    professor_disciplinas = []
    for p in range(1, N_PROFESSORES + 1):
        disciplina = ((p - 1) % N_DISCIPLINAS) + 1
        professor_disciplinas.append(ProfessorDisciplinaDTO(professor_id=p, disciplina_id=disciplina))
        disciplina_extra = (p % N_DISCIPLINAS) + 1
        professor_disciplinas.append(ProfessorDisciplinaDTO(professor_id=p, disciplina_id=disciplina_extra))

    salas = [SalaDTO(id=s, capacidade=40) for s in range(1, N_SALAS + 1)]
    slots = [SlotDTO(dia_semana=g.dia_semana, turno=g.turno, periodo=g.periodo) for g in gerar_grelha_tempos()]

    return HorarioInput(
        turmas=turmas,
        professores=professores,
        salas=salas,
        slots=slots,
        turma_disciplinas=turma_disciplinas,
        professor_disciplinas=professor_disciplinas,
        disponibilidades=[],  # RN07 — fallback totalmente disponível, foco no scaling
    )


def _contar_variaveis(dados: HorarioInput) -> int:
    dados_podados, _ = podar_dominio(dados)
    model = cp_model.CpModel()
    variaveis = build_variables(model, dados_podados)
    return len(variaveis.x)


def main() -> None:
    dados = _construir_cenario()
    print(f"Cenário: {len(dados.turmas)} turmas, {len(dados.professores)} professores, "
          f"{len(dados.turma_disciplinas)} pares turma-disciplina, {len(dados.salas)} salas")

    print("\n--- Contagem de variáveis (após poda de domínio) ---")
    t0 = time.perf_counter()
    n_vars_monolitico = _contar_variaveis(dados)
    print(f"Monolítico: {n_vars_monolitico} variáveis (construção: {time.perf_counter() - t0:.2f}s)")

    print("\n--- Solve monolítico (um único modelo CP-SAT) ---")
    t0 = time.perf_counter()
    resultado_mono = resolver_horario(dados, max_time_in_seconds=MAX_TIME_MONOLITICO)
    tempo_mono = time.perf_counter() - t0
    print(f"status={resultado_mono.status} alocacoes={len(resultado_mono.alocacoes)} tempo={tempo_mono:.2f}s")
    if resultado_mono.status == "INFEASIBLE":
        print(f"diagnostico: {resultado_mono.diagnostico}")

    print("\n--- Solve decomposto por turno (Manhã → Tarde → Noite) ---")
    t0 = time.perf_counter()
    resultado_turnos = resolver_horario_por_turnos(dados, max_time_in_seconds_total=MAX_TIME_TOTAL_DECOMPOSTO)
    tempo_turnos = time.perf_counter() - t0
    print(f"status={resultado_turnos.status} alocacoes={len(resultado_turnos.alocacoes)} tempo={tempo_turnos:.2f}s")
    if resultado_turnos.status == "INFEASIBLE":
        print(f"diagnostico: {resultado_turnos.diagnostico}")

    print("\n--- Resumo ---")
    print(f"Monolítico:  status={resultado_mono.status:12s} tempo={tempo_mono:7.2f}s")
    print(f"Decomposto:  status={resultado_turnos.status:12s} tempo={tempo_turnos:7.2f}s")


if __name__ == "__main__":
    main()
