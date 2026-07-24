import 'package:ghorario/core/enums/dia_semana.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_resultado.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_slot.dart';

/// Data Transfer Object for a single [HorarioSlot], parsed from one item of
/// `HorarioResponseSchema.dias[].tempos[]` (`HorarioItemSchema`).
class HorarioSlotDto {
  const HorarioSlotDto({
    required this.id,
    required this.docenteName,
    required this.turmaName,
    required this.disciplinaName,
    required this.disciplinaNomeCurto,
    required this.salaName,
    required this.dayOfWeek,
    required this.timeSlot,
    required this.turno,
    required this.periodo,
    required this.disciplinaId,
    required this.professorId,
    required this.salaId,
    this.alocacaoId,
  });

  final String id;
  final String docenteName;
  final String turmaName;
  final String disciplinaName;
  final String disciplinaNomeCurto;
  final String salaName;
  final int dayOfWeek;
  final String timeSlot;
  final String turno;
  final int periodo;
  final int disciplinaId;
  final int professorId;
  final int salaId;
  final int? alocacaoId;

  factory HorarioSlotDto.fromJson(Map<String, dynamic> json, String diaSemana) {
    final horaInicio = json['hora_inicio']?.toString() ?? '';
    final horaFim = json['hora_fim']?.toString() ?? '';
    final turno = json['turno']?.toString() ?? '';
    final periodo = json['periodo'] as int? ?? 0;
    return HorarioSlotDto(
      id: '$diaSemana-$turno-$periodo',
      docenteName: json['professor_nome'] as String? ?? '',
      turmaName: json['turma_nome'] as String? ?? '',
      disciplinaName: json['disciplina_nome'] as String? ?? '',
      disciplinaNomeCurto: json['disciplina_nome_curto'] as String? ?? '',
      salaName: json['sala_nome'] as String? ?? '',
      dayOfWeek: DiaSemana.fromApi(diaSemana).ordem,
      timeSlot: '$horaInicio - $horaFim',
      turno: turno,
      periodo: periodo,
      disciplinaId: json['disciplina_id'] as int? ?? 0,
      professorId: json['professor_id'] as int? ?? 0,
      salaId: json['sala_id'] as int? ?? 0,
      alocacaoId: json['alocacao_id'] as int?,
    );
  }

  HorarioSlot toEntity() {
    return HorarioSlot(
      id: id,
      docenteName: docenteName,
      turmaName: turmaName,
      disciplinaName: disciplinaName,
      disciplinaNomeCurto: disciplinaNomeCurto,
      salaName: salaName,
      dayOfWeek: dayOfWeek,
      timeSlot: timeSlot,
      turno: turno,
      periodo: periodo,
      disciplinaId: disciplinaId,
      professorId: professorId,
      salaId: salaId,
      alocacaoId: alocacaoId,
    );
  }
}

/// DTO for the full `HorarioResponseSchema` — slots plus the `job_id` that
/// produced them (RF11/RF12 response shape).
class HorarioResponseDto {
  const HorarioResponseDto({required this.jobId, required this.slots});

  final String jobId;
  final List<HorarioSlotDto> slots;

  factory HorarioResponseDto.fromJson(Map<String, dynamic> json) {
    final dias = json['dias'] as List;
    final slots = <HorarioSlotDto>[];
    for (final dia in dias) {
      final diaMap = dia as Map<String, dynamic>;
      final diaSemana = diaMap['dia_semana']?.toString() ?? '';
      final tempos = diaMap['tempos'] as List;
      for (final tempo in tempos) {
        slots.add(HorarioSlotDto.fromJson(tempo as Map<String, dynamic>, diaSemana));
      }
    }
    return HorarioResponseDto(jobId: json['job_id']?.toString() ?? '', slots: slots);
  }

  HorarioResultado toEntity() {
    return HorarioResultado(jobId: jobId, slots: slots.map((s) => s.toEntity()).toList());
  }
}
