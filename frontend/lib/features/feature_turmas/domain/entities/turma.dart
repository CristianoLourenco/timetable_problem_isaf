import 'package:ghorario/core/enums/turno.dart';

/// Domain entity representing a class group (turma).
///
/// Pure Dart class — no Flutter, Firebase, or framework imports.
class Turma {
  const Turma({
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
}
