import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/item_grade_curricular.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_turma_disciplina_repository.dart';

class GetGradeCurricularUseCase implements IUseCase<List<ItemGradeCurricular>, int> {
  GetGradeCurricularUseCase(this._repository);

  final ITurmaDisciplinaRepository _repository;

  @override
  Future<DataState<List<ItemGradeCurricular>>> call(int turmaId) {
    return _repository.obter(turmaId);
  }
}
