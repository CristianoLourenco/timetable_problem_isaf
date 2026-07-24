import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma_detalhada.dart';

/// Abstract repository interface for the Turmas feature.
abstract class ITurmaRepository {
  Future<DataState<List<Turma>>> getAll();
  Future<DataState<Turma>> getById(String id);
  Future<DataState<void>> create(Turma turma);
  Future<DataState<void>> update(Turma turma);
  Future<DataState<void>> delete(String id);

  /// RF02 — turmas filtradas por âmbito (ano letivo/semestre), com dados de
  /// curso já resolvidos. `anoLetivo`/`semestre` opcionais.
  Future<DataState<List<TurmaDetalhada>>> getDetalhadas({int? anoLetivo, String? semestre});
}
