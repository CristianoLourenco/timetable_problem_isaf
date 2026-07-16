/// One row of a Turma's curriculum grid — a Disciplina and its weekly
/// teaching load for that specific Turma (`TurmaDisciplinaReadSchema`).
class ItemGradeCurricular {
  const ItemGradeCurricular({required this.disciplinaId, required this.cargaHorariaSemanal});

  final int disciplinaId;
  final int cargaHorariaSemanal;
}
