import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disciplinas/domain/entities/disciplina.dart';
import 'package:ghorario/features/feature_disciplinas/domain/repository/i_disciplina_repository.dart';

/// Use case to retrieve all subjects/disciplinas.
class GetAllDisciplinasUseCase implements IUseCase<List<Disciplina>, void> {
  GetAllDisciplinasUseCase(this._repository);

  final IDisciplinaRepository _repository;

  @override
  Future<DataState<List<Disciplina>>> call(void params) {
    return _repository.getAll();
  }
}
