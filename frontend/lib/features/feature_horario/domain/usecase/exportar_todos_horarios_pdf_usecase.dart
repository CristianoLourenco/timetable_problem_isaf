import 'dart:typed_data';

import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Use case to download a .zip with one PDF per turma covered by a Job
/// (RF11 — replicates the ISAF exemplar structure of one file per turma).
class ExportarTodosHorariosPdfUseCase implements IUseCase<Uint8List, String> {
  ExportarTodosHorariosPdfUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<Uint8List>> call(String jobId) {
    return _repository.downloadExportarTodosPdf(jobId);
  }
}
