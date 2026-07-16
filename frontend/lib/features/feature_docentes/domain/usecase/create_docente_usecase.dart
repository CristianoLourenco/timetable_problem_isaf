import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_docentes/domain/entities/docente.dart';
import 'package:ghorario/features/feature_docentes/domain/repository/i_docente_repository.dart';

/// Use case to create a new Docente (Professor).
class CreateDocenteUseCase implements IUseCase<void, Docente> {
  CreateDocenteUseCase(this._repository);

  final IDocenteRepository _repository;

  @override
  Future<DataState<void>> call(Docente params) {
    return _repository.create(params);
  }
}
