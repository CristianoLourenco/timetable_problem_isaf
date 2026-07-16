import 'package:ghorario/core/enums/dia_semana.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_slot.dart';

/// Data Transfer Object for a single [HorarioSlot], parsed from one item of
/// `HorarioResponseSchema.dias[].tempos[]` (`HorarioItemSchema`).
class HorarioSlotDto {
  const HorarioSlotDto({
    required this.id,
    required this.docenteName,
    required this.turmaName,
    required this.disciplinaName,
    required this.salaName,
    required this.dayOfWeek,
    required this.timeSlot,
  });

  final String id;
  final String docenteName;
  final String turmaName;
  final String disciplinaName;
  final String salaName;
  final int dayOfWeek;
  final String timeSlot;

  factory HorarioSlotDto.fromJson(Map<String, dynamic> json, String diaSemana) {
    final horaInicio = json['hora_inicio']?.toString() ?? '';
    final horaFim = json['hora_fim']?.toString() ?? '';
    // Não existe slot_id (sem tabela Slot no backend — ver
    // backend/app/core/calendario.py); id sintético a partir da própria chave.
    final turno = json['turno']?.toString() ?? '';
    final periodo = json['periodo']?.toString() ?? '';
    return HorarioSlotDto(
      id: '$diaSemana-$turno-$periodo',
      docenteName: json['professor_nome'] as String? ?? '',
      turmaName: json['turma_nome'] as String? ?? '',
      disciplinaName: json['disciplina_nome'] as String? ?? '',
      salaName: json['sala_nome'] as String? ?? '',
      dayOfWeek: DiaSemana.fromApi(diaSemana).ordem,
      timeSlot: '$horaInicio - $horaFim',
    );
  }

  HorarioSlot toEntity() {
    return HorarioSlot(
      id: id,
      docenteName: docenteName,
      turmaName: turmaName,
      disciplinaName: disciplinaName,
      salaName: salaName,
      dayOfWeek: dayOfWeek,
      timeSlot: timeSlot,
    );
  }
}
