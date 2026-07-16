import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disciplinas/data/models/disciplina_dto.dart';

/// Abstract remote datasource interface for Disciplinas.
abstract class IDisciplinaRemote {
  Future<DataState<List<DisciplinaDto>>> getAll();
  Future<DataState<DisciplinaDto>> getById(String id);
  Future<DataState<void>> create(DisciplinaDto dto);
  Future<DataState<void>> update(DisciplinaDto dto);
  Future<DataState<void>> delete(String id);
}
