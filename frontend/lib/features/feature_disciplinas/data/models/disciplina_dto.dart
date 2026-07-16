import 'package:ghorario/features/feature_disciplinas/domain/entities/disciplina.dart';

/// Data Transfer Object for [Disciplina] entity (`DisciplinaRead`: id, codigo, nome).
///
/// Weekly hours are not a Disciplina attribute in the backend — they belong to
/// `TurmaDisciplina` (the curriculum grid), not the subject itself.
class DisciplinaDto {
  const DisciplinaDto({
    required this.id,
    required this.name,
    this.code,
    this.weeklyHours,
    this.createdAt,
    this.updatedAt,
  });

  final String id;
  final String name;
  final String? code;
  final int? weeklyHours;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  factory DisciplinaDto.fromJson(Map<String, dynamic> json) {
    return DisciplinaDto(
      id: json['id'].toString(),
      name: json['nome'] as String? ?? '',
      code: json['codigo'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'nome': name,
      'codigo': code,
    };
  }

  Disciplina toEntity() {
    return Disciplina(
      id: id,
      name: name,
      code: code,
      weeklyHours: weeklyHours,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }

  factory DisciplinaDto.fromEntity(Disciplina entity) {
    return DisciplinaDto(
      id: entity.id,
      name: entity.name,
      code: entity.code,
      weeklyHours: entity.weeklyHours,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
    );
  }
}
