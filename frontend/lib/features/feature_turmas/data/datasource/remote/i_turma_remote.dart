import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/models/turma_dto.dart';

/// Abstract remote datasource interface for Turmas.
abstract class ITurmaRemote {
  Future<DataState<List<TurmaDto>>> getAll();
  Future<DataState<TurmaDto>> getById(String id);
  Future<DataState<void>> create(TurmaDto dto);
  Future<DataState<void>> update(TurmaDto dto);
  Future<DataState<void>> delete(String id);
}
