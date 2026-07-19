import 'package:ghorario/features/feature_horario/domain/entities/pendencia.dart';

/// Data Transfer Object for [Pendencia], deserialized from backend PendenciaRead.
class PendenciaDto {
  const PendenciaDto({
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

  factory PendenciaDto.fromJson(Map<String, dynamic> json) {
    return PendenciaDto(
      turmaId: json['turma_id'] as int? ?? 0,
      disciplinaId: json['disciplina_id'] as int? ?? 0,
      temposEmFalta: json['tempos_em_falta'] as int? ?? 0,
      razao: json['razao'] as String? ?? '',
      professoresConflitantes: List<int>.from(json['professores_conflitantes'] as List? ?? []),
      turmasConflitantes: List<int>.from(json['turmas_conflitantes'] as List? ?? []),
    );
  }

  Pendencia toEntity() {
    return Pendencia(
      turmaId: turmaId,
      disciplinaId: disciplinaId,
      temposEmFalta: temposEmFalta,
      razao: razao,
      professoresConflitantes: professoresConflitantes,
      turmasConflitantes: turmasConflitantes,
    );
  }
}
