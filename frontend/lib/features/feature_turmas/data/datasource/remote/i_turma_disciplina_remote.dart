import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/models/item_grade_curricular_dto.dart';

/// Abstract remote datasource for `/planos-curriculares/{id}/disciplinas` (curriculum grid).
abstract class ITurmaDisciplinaRemote {
  Future<DataState<List<ItemGradeCurricularDto>>> obter(int planoCurricularId);
  Future<DataState<List<ItemGradeCurricularDto>>> definir(int planoCurricularId, List<ItemGradeCurricularDto> itens);
}
