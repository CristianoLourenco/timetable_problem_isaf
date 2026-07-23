import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_resultado.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Query target for [GetHorarioUseCase] — the timetable is always looked up
/// by turma or professor, never by job_id (RN — see backend/README.md).
class GetHorarioParams {
  const GetHorarioParams.turma(this.id, {this.anoLetivo, this.semestre}) : isProfessor = false;
  const GetHorarioParams.professor(this.id, {this.anoLetivo, this.semestre}) : isProfessor = true;

  final String id;
  final bool isProfessor;

  /// Quando fornecidos, restringe a consulta ao Job DONE desse (ano_letivo,
  /// semestre) exato, em vez do Job DONE mais recente entre todos os âmbitos.
  final int? anoLetivo;
  final String? semestre;
}

/// Use case to fetch the current timetable of a turma or professor.
class GetHorarioUseCase implements IUseCase<HorarioResultado, GetHorarioParams> {
  GetHorarioUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<HorarioResultado>> call(GetHorarioParams params) {
    return params.isProfessor
        ? _repository.getTimetableByProfessor(params.id, anoLetivo: params.anoLetivo, semestre: params.semestre)
        : _repository.getTimetableByTurma(params.id, anoLetivo: params.anoLetivo, semestre: params.semestre);
  }
}
