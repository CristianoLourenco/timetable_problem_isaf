import 'package:ghorario/features/feature_salas/domain/entities/sala.dart';

/// Data Transfer Object for [Sala] entity (`SalaRead`: id, codigo, nome, capacidade).
class SalaDto {
  const SalaDto({
    required this.id,
    required this.name,
    this.code,
    this.capacity,
  });

  final String id;
  final String name;
  final String? code;
  final int? capacity;

  factory SalaDto.fromJson(Map<String, dynamic> json) {
    return SalaDto(
      id: json['id'].toString(),
      name: json['nome'] as String? ?? '',
      code: json['codigo'] as String?,
      capacity: json['capacidade'] as int?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'nome': name,
      'codigo': code,
      'capacidade': capacity,
    };
  }

  Sala toEntity() {
    return Sala(id: id, name: name, code: code, capacity: capacity);
  }

  factory SalaDto.fromEntity(Sala entity) {
    return SalaDto(id: entity.id, name: entity.name, code: entity.code, capacity: entity.capacity);
  }
}
