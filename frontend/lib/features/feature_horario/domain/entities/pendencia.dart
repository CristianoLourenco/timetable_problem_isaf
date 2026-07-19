/// Domain entity representing a pending allocation (turma/disciplina not yet distributed).
class Pendencia {
  const Pendencia({
    required this.turmaId,
    required this.disciplinaId,
    required this.temposEmFalta,
    required this.razao,
    required this.professoresConflitantes,
    required this.turmasConflitantes,
  });

  final int turmaId;
  final int disciplinaId;
  final int temposEmFalta;
  final String razao;
  final List<int> professoresConflitantes;
  final List<int> turmasConflitantes;
}
