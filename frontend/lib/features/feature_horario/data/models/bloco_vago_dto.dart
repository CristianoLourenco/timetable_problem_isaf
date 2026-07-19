import 'package:ghorario/features/feature_horario/domain/entities/bloco_vago.dart';

/// Data Transfer Object for [BlocoVago], deserialized from backend BlocoVagoRead.
class BlocoVagoDto {
  const BlocoVagoDto({
    required this.diaSemana,
    required this.turno,
    required this.periodos,
  });

  final String diaSemana;
  final String turno;
  final List<int> periodos;

  factory BlocoVagoDto.fromJson(Map<String, dynamic> json) {
    return BlocoVagoDto(
      diaSemana: json['dia_semana'] as String? ?? '',
      turno: json['turno'] as String? ?? '',
      periodos: List<int>.from(json['periodos'] as List? ?? []),
    );
  }

  BlocoVago toEntity() {
    return BlocoVago(
      diaSemana: diaSemana,
      turno: turno,
      periodos: periodos,
    );
  }
}
