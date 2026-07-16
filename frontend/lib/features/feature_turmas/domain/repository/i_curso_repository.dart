import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/curso.dart';

/// Abstract repository interface for the Cursos (support entity for Turma.cursoId).
abstract class ICursoRepository {
  Future<DataState<List<Curso>>> getAll();
  Future<DataState<void>> create(Curso curso);
}
