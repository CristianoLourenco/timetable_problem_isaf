import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';

/// Abstract repository interface for the Turmas feature.
abstract class ITurmaRepository {
  Future<DataState<List<Turma>>> getAll();
  Future<DataState<Turma>> getById(String id);
  Future<DataState<void>> create(Turma turma);
  Future<DataState<void>> update(Turma turma);
  Future<DataState<void>> delete(String id);
}
