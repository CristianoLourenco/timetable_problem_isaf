import 'package:ghorario/features/feature_turmas/domain/entities/item_grade_curricular.dart';

class ItemGradeCurricularDto {
  const ItemGradeCurricularDto({required this.disciplinaId, required this.cargaHorariaSemanal});

  final int disciplinaId;
  final int cargaHorariaSemanal;

  factory ItemGradeCurricularDto.fromJson(Map<String, dynamic> json) {
    return ItemGradeCurricularDto(
      disciplinaId: json['disciplina_id'] as int,
      cargaHorariaSemanal: json['carga_horaria_semanal'] as int,
    );
  }

  Map<String, dynamic> toJson() => {
        'disciplina_id': disciplinaId,
        'carga_horaria_semanal': cargaHorariaSemanal,
      };

  ItemGradeCurricular toEntity() =>
      ItemGradeCurricular(disciplinaId: disciplinaId, cargaHorariaSemanal: cargaHorariaSemanal);

  factory ItemGradeCurricularDto.fromEntity(ItemGradeCurricular entity) {
    return ItemGradeCurricularDto(
      disciplinaId: entity.disciplinaId,
      cargaHorariaSemanal: entity.cargaHorariaSemanal,
    );
  }
}
