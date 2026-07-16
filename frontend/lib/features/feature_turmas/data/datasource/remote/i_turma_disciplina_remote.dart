import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/models/item_grade_curricular_dto.dart';

/// Abstract remote datasource for `/turmas/{id}/disciplinas` (curriculum grid).
abstract class ITurmaDisciplinaRemote {
  Future<DataState<List<ItemGradeCurricularDto>>> obter(int turmaId);
  Future<DataState<List<ItemGradeCurricularDto>>> definir(int turmaId, List<ItemGradeCurricularDto> itens);
}
