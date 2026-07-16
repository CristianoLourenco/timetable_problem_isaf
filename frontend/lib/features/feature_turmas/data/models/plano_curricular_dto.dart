import 'package:ghorario/features/feature_turmas/domain/entities/plano_curricular.dart';

/// Data Transfer Object for [PlanoCurricular] (`PlanoCurricularRead`: id, curso_id, ano, semestre).
class PlanoCurricularDto {
  const PlanoCurricularDto({required this.id, required this.cursoId, required this.ano, required this.semestre});

  final String id;
  final String cursoId;
  final int ano;
  final String semestre;

  factory PlanoCurricularDto.fromJson(Map<String, dynamic> json) {
    return PlanoCurricularDto(
      id: json['id'].toString(),
      cursoId: json['curso_id'].toString(),
      ano: json['ano'] as int? ?? 0,
      semestre: json['semestre'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() => {'curso_id': int.tryParse(cursoId), 'ano': ano, 'semestre': semestre};

  PlanoCurricular toEntity() => PlanoCurricular(id: id, cursoId: cursoId, ano: ano, semestre: semestre);

  factory PlanoCurricularDto.fromEntity(PlanoCurricular entity) {
    return PlanoCurricularDto(id: entity.id, cursoId: entity.cursoId, ano: entity.ano, semestre: entity.semestre);
  }
}
