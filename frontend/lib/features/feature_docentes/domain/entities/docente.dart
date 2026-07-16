/// Domain entity representing a teacher (docente).
///
/// Pure Dart class — no Flutter, Firebase, or framework imports.
class Docente {
  const Docente({
    required this.id,
    required this.name,
    this.email,
    this.phone,
    this.createdAt,
    this.updatedAt,
  });

  final String id;
  final String name;
  final String? email;
  final String? phone;
  final DateTime? createdAt;
  final DateTime? updatedAt;
}
