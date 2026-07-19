import 'package:ghorario/features/feature_horario/domain/entities/alocacao_manual_response.dart';

/// Data Transfer Object for [AlocacaoManualResponse], deserialized from backend AlocacaoRead.
class AlocacaoManualResponseDto {
  const AlocacaoManualResponseDto({
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

  factory AlocacaoManualResponseDto.fromJson(Map<String, dynamic> json) {
    return AlocacaoManualResponseDto(
      id: json['id'] as int? ?? 0,
      jobId: json['job_id']?.toString() ?? '',
      turmaId: json['turma_id'] as int? ?? 0,
      disciplinaId: json['disciplina_id'] as int? ?? 0,
      professorId: json['professor_id'] as int? ?? 0,
      salaId: json['sala_id'] as int? ?? 0,
      diaSemana: json['dia_semana'] as String? ?? '',
      periodo: json['periodo'] as int? ?? 0,
    );
  }

  AlocacaoManualResponse toEntity() {
    return AlocacaoManualResponse(
      id: id,
      jobId: jobId,
      turmaId: turmaId,
      disciplinaId: disciplinaId,
      professorId: professorId,
      salaId: salaId,
      diaSemana: diaSemana,
      periodo: periodo,
    );
  }
}
