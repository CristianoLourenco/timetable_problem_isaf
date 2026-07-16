import 'package:ghorario/features/feature_docentes/domain/entities/docente.dart';

/// Data Transfer Object for [Docente] entity.
///
/// Maps to the backend's `Professor` (`ProfessorRead`: id, nome, email,
/// classificacao, vinculo_casa) — kept under the "Docente" feature name for
/// UI/folder purposes only.
class DocenteDto {
  const DocenteDto({
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

  factory DocenteDto.fromJson(Map<String, dynamic> json) {
    return DocenteDto(
      id: json['id'].toString(),
      name: json['nome'] as String? ?? '',
      email: json['email'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'nome': name,
      'email': email,
    };
  }

  /// Converts this DTO to a domain [Docente] entity.
  Docente toEntity() {
    return Docente(
      id: id,
      name: name,
      email: email,
      phone: phone,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }

  /// Creates a DTO from a domain [Docente] entity.
  factory DocenteDto.fromEntity(Docente entity) {
    return DocenteDto(
      id: entity.id,
      name: entity.name,
      email: entity.email,
      phone: entity.phone,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
    );
  }
}
