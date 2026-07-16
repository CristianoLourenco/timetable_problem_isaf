import 'package:ghorario/core/enums/dia_semana.dart';
import 'package:ghorario/core/enums/turno.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo_chave.dart';

/// DTO for `TempoRead` (`GET /slots`) — no `Slot` table on the backend, the
/// grid is calculated at runtime (see backend/app/core/calendario.py).
class TempoDto {
  const TempoDto({
    required this.diaSemana,
    required this.turno,
    required this.periodo,
    required this.horaInicio,
    required this.horaFim,
  });

  final DiaSemana diaSemana;
  final Turno turno;
  final int periodo;
  final String horaInicio;
  final String horaFim;

  factory TempoDto.fromJson(Map<String, dynamic> json) {
    return TempoDto(
      diaSemana: DiaSemana.fromApi(json['dia_semana'] as String? ?? ''),
      turno: Turno.fromApi(json['turno'] as String?) ?? Turno.manha,
      periodo: json['periodo'] as int? ?? 0,
      horaInicio: (json['hora_inicio'] as String? ?? '').substring(0, 5),
      horaFim: (json['hora_fim'] as String? ?? '').substring(0, 5),
    );
  }

  Tempo toEntity() {
    return Tempo(diaSemana: diaSemana, turno: turno, periodo: periodo, horaInicio: horaInicio, horaFim: horaFim);
  }

  TempoChave toChave() => TempoChave(diaSemana: diaSemana, turno: turno, periodo: periodo);
}
