import 'package:ghorario/features/feature_turmas/domain/entities/curso.dart';

/// Data Transfer Object for [Curso] (`CursoRead`: id, codigo, nome).
class CursoDto {
  const CursoDto({required this.id, required this.codigo, required this.nome});

  final String id;
  final String codigo;
  final String nome;

  factory CursoDto.fromJson(Map<String, dynamic> json) {
    return CursoDto(
      id: json['id'].toString(),
      codigo: json['codigo'] as String? ?? '',
      nome: json['nome'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() => {'codigo': codigo, 'nome': nome};

  Curso toEntity() => Curso(id: id, codigo: codigo, name: nome);

  factory CursoDto.fromEntity(Curso entity) {
    return CursoDto(id: entity.id, codigo: entity.codigo, nome: entity.name);
  }
}
