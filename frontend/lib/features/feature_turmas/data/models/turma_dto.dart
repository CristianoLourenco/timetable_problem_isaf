import 'package:ghorario/core/enums/turno.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';

/// Data Transfer Object for [Turma] entity (`TurmaRead`: id, codigo, nome,
/// ano_letivo, turno, numero_alunos, curso_id).
class TurmaDto {
  const TurmaDto({
    required this.id,
    required this.name,
    this.code,
    this.year,
    this.period,
    this.studentsCount,
    this.cursoId,
    this.createdAt,
    this.updatedAt,
  });

  final String id;
  final String name;
  final String? code;
  final int? year;
  final Turno? period;
  final int? studentsCount;
  final int? cursoId;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  factory TurmaDto.fromJson(Map<String, dynamic> json) {
    return TurmaDto(
      id: json['id'].toString(),
      name: json['nome'] as String? ?? '',
      code: json['codigo'] as String?,
      year: json['ano_letivo'] as int?,
      period: Turno.fromApi(json['turno'] as String?),
      studentsCount: json['numero_alunos'] as int?,
      cursoId: json['curso_id'] as int?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'codigo': code,
      'nome': name,
      'ano_letivo': year,
      'turno': period?.apiValue,
      'numero_alunos': studentsCount,
      'curso_id': cursoId,
    };
  }

  Turma toEntity() {
    return Turma(
      id: id,
      name: name,
      code: code,
      year: year,
      period: period,
      studentsCount: studentsCount,
      cursoId: cursoId,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }

  factory TurmaDto.fromEntity(Turma entity) {
    return TurmaDto(
      id: entity.id,
      name: entity.name,
      code: entity.code,
      year: entity.year,
      period: entity.period,
      studentsCount: entity.studentsCount,
      cursoId: entity.cursoId,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
    );
  }
}
