import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_turma_repository.dart';

/// Use case to retrieve all turmas.
class GetAllTurmasUseCase implements IUseCase<List<Turma>, void> {
  GetAllTurmasUseCase(this._repository);

  final ITurmaRepository _repository;

  @override
  Future<DataState<List<Turma>>> call(void params) {
    return _repository.getAll();
  }
}
