import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';

/// RF02 — [Turma] enriched with its course and curricular year, resolved by
/// the backend (`GET /turmas-detalhadas`) so the frontend never has to chain
/// Turma -> PlanoCurricular -> Curso requests to render a single card/row.
///
/// Composes [Turma] rather than extending it: this is a distinct read model
/// (scoped by ano_letivo/semestre, extra fields) used only where that scope
/// filtering matters (ver HorarioScreen) — other screens keep using the
/// unfiltered [Turma] via TurmasProvider/GetAllTurmasUseCase.
class TurmaDetalhada {
  const TurmaDetalhada({
    required this.turma,
    required this.cursoCodigo,
    required this.cursoNome,
    required this.anoCurricular,
    required this.semestre,
  });

  final Turma turma;
  final String cursoCodigo;
  final String cursoNome;

  /// 1..4 — ano curricular do PlanoCurricular, não confundir com
  /// `turma.year` (ano_letivo, ano civil, ex: 2026).
  final int anoCurricular;
  final String semestre;

  String get id => turma.id;
  String get name => turma.name;
  String? get code => turma.code;
}
