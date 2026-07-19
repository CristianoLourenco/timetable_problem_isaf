import 'dart:typed_data';

import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Use case to download the PDF (RF11) of a single turma's timetable.
class ExportarHorarioTurmaPdfUseCase implements IUseCase<Uint8List, String> {
  ExportarHorarioTurmaPdfUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<Uint8List>> call(String turmaId) {
    return _repository.downloadHorarioTurmaPdf(turmaId);
  }
}
