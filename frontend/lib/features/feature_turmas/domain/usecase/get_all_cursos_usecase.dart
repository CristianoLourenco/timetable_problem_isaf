import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/curso.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_curso_repository.dart';

/// Use case to retrieve all cursos (needed to resolve `curso_id` for a Turma).
class GetAllCursosUseCase implements IUseCase<List<Curso>, void> {
  GetAllCursosUseCase(this._repository);

  final ICursoRepository _repository;

  @override
  Future<DataState<List<Curso>>> call(void params) {
    return _repository.getAll();
  }
}
