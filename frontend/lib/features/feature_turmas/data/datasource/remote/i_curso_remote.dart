import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/models/curso_dto.dart';

/// Abstract remote datasource interface for Cursos.
abstract class ICursoRemote {
  Future<DataState<List<CursoDto>>> getAll();
  Future<DataState<void>> create(CursoDto dto);
}
