import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/item_grade_curricular.dart';

abstract class ITurmaDisciplinaRepository {
  Future<DataState<List<ItemGradeCurricular>>> obter(int planoCurricularId);
  Future<DataState<List<ItemGradeCurricular>>> definir(int planoCurricularId, List<ItemGradeCurricular> itens);
}
