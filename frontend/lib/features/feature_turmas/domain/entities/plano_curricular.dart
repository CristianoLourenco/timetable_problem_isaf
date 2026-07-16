/// Domain entity representing a curriculum plan (plano curricular) — mirrors
/// the backend's `PlanoCurricular` (`PlanoCurricularRead`: id, curso_id, ano,
/// semestre). A Turma always follows exactly one PlanoCurricular, from which
/// it inherits its disciplinas (via PlanoCurricularDisciplina) — replaces the
/// old per-turma grade curricular (TurmaDisciplina).
class PlanoCurricular {
  const PlanoCurricular({required this.id, required this.cursoId, required this.ano, required this.semestre});

  final String id;
  final String cursoId;
  final int ano;
  final String semestre;
}
