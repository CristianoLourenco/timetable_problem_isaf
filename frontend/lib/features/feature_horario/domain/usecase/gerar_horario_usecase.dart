import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Use case to trigger the timetable generation process.
class GerarHorarioUseCase implements IUseCase<String, void> {
  GerarHorarioUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<String>> call(void params) {
    return _repository.triggerGeneration();
  }
}
