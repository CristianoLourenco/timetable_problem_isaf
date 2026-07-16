import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disciplinas/domain/entities/disciplina.dart';
import 'package:ghorario/features/feature_disciplinas/domain/repository/i_disciplina_repository.dart';

/// Use case to create a new Disciplina.
class CreateDisciplinaUseCase implements IUseCase<void, Disciplina> {
  CreateDisciplinaUseCase(this._repository);

  final IDisciplinaRepository _repository;

  @override
  Future<DataState<void>> call(Disciplina params) {
    return _repository.create(params);
  }
}
