import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_turma_repository.dart';

/// Use case to create a new Turma.
class CreateTurmaUseCase implements IUseCase<void, Turma> {
  CreateTurmaUseCase(this._repository);

  final ITurmaRepository _repository;

  @override
  Future<DataState<void>> call(Turma params) {
    return _repository.create(params);
  }
}
