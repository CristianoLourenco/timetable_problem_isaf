import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Params for [GerarHorarioUseCase] — âmbito da geração (RF09): o horário
/// completo de todas as turmas de um único ano lectivo/semestre, de uma vez.
class GerarHorarioParams {
  const GerarHorarioParams({required this.anoLetivo, required this.semestre});

  final int anoLetivo;
  final String semestre;
}

/// Use case to trigger the timetable generation process.
class GerarHorarioUseCase implements IUseCase<String, GerarHorarioParams> {
  GerarHorarioUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<String>> call(GerarHorarioParams params) {
    return _repository.triggerGeneration(anoLetivo: params.anoLetivo, semestre: params.semestre);
  }
}
