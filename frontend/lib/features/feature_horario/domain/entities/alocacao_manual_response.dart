/// Domain entity representing the result of a manual allocation creation or movement.
class AlocacaoManualResponse {
  const AlocacaoManualResponse({
    required this.id,
    required this.jobId,
    required this.turmaId,
    required this.disciplinaId,
    required this.professorId,
    required this.salaId,
    required this.diaSemana,
    required this.periodo,
  });

  final int id;
  final String jobId;
  final int turmaId;
  final int disciplinaId;
  final int professorId;
  final int salaId;
  final String diaSemana;
  final int periodo;
}
