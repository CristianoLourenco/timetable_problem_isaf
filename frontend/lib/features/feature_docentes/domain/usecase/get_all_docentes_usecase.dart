import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_docentes/domain/entities/docente.dart';
import 'package:ghorario/features/feature_docentes/domain/repository/i_docente_repository.dart';

/// Use case to retrieve all docentes.
class GetAllDocentesUseCase implements IUseCase<List<Docente>, void> {
  GetAllDocentesUseCase(this._repository);

  final IDocenteRepository _repository;

  @override
  Future<DataState<List<Docente>>> call(void params) {
    return _repository.getAll();
  }
}
