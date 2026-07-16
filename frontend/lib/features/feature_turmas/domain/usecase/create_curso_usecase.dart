import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/curso.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_curso_repository.dart';

class CreateCursoUseCase implements IUseCase<void, Curso> {
  CreateCursoUseCase(this._repository);

  final ICursoRepository _repository;

  @override
  Future<DataState<void>> call(Curso params) {
    return _repository.create(params);
  }
}
