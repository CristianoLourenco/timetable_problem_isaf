import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_docentes/domain/entities/docente.dart';

/// Abstract repository interface for the Docentes feature.
abstract class IDocenteRepository {
  Future<DataState<List<Docente>>> getAll();
  Future<DataState<Docente>> getById(String id);
  Future<DataState<void>> create(Docente docente);
  Future<DataState<void>> update(Docente docente);
  Future<DataState<void>> delete(String id);
}
