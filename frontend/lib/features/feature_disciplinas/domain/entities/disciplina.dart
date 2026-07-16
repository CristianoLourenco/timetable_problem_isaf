/// Domain entity representing a subject/discipline (disciplina).
///
/// Pure Dart class — no Flutter, Firebase, or framework imports.
class Disciplina {
  const Disciplina({
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
}
