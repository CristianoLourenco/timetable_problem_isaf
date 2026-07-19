import 'package:ghorario/features/feature_horario/domain/entities/professor_qualificado.dart';

/// Data Transfer Object for [ProfessorQualificado], deserialized from backend ProfessorQualificadoRead.
class ProfessorQualificadoDto {
  const ProfessorQualificadoDto({
    required this.id,
    required this.nome,
    required this.classificacao,
    required this.vinculoCasa,
  });

  final int id;
  final String nome;
  final int classificacao;
  final bool vinculoCasa;

  factory ProfessorQualificadoDto.fromJson(Map<String, dynamic> json) {
    return ProfessorQualificadoDto(
      id: json['id'] as int? ?? 0,
      nome: json['nome'] as String? ?? '',
      classificacao: json['classificacao'] as int? ?? 1,
      vinculoCasa: json['vinculo_casa'] as bool? ?? false,
    );
  }

  ProfessorQualificado toEntity() {
    return ProfessorQualificado(
      id: id,
      nome: nome,
      classificacao: classificacao,
      vinculoCasa: vinculoCasa,
    );
  }
}
