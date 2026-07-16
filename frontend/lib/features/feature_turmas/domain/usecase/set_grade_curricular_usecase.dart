import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/item_grade_curricular.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_turma_disciplina_repository.dart';

class SetGradeCurricularParams {
  const SetGradeCurricularParams({required this.turmaId, required this.itens});

  final int turmaId;
  final List<ItemGradeCurricular> itens;
}

class SetGradeCurricularUseCase implements IUseCase<List<ItemGradeCurricular>, SetGradeCurricularParams> {
  SetGradeCurricularUseCase(this._repository);

  final ITurmaDisciplinaRepository _repository;

  @override
  Future<DataState<List<ItemGradeCurricular>>> call(SetGradeCurricularParams params) {
    return _repository.definir(params.turmaId, params.itens);
  }
}
