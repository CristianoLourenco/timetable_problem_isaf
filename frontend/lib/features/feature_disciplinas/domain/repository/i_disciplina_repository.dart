import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disciplinas/domain/entities/disciplina.dart';

/// Abstract repository interface for the Disciplinas feature.
abstract class IDisciplinaRepository {
  Future<DataState<List<Disciplina>>> getAll();
  Future<DataState<Disciplina>> getById(String id);
  Future<DataState<void>> create(Disciplina disciplina);
  Future<DataState<void>> update(Disciplina disciplina);
  Future<DataState<void>> delete(String id);
}
