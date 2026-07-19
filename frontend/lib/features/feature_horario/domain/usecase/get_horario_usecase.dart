import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_resultado.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Query target for [GetHorarioUseCase] — the timetable is always looked up
/// by turma or professor, never by job_id (RN — see backend/README.md).
class GetHorarioParams {
  const GetHorarioParams.turma(this.id) : isProfessor = false;
  const GetHorarioParams.professor(this.id) : isProfessor = true;

  final String id;
  final bool isProfessor;
}

/// Use case to fetch the current timetable of a turma or professor.
class GetHorarioUseCase implements IUseCase<HorarioResultado, GetHorarioParams> {
  GetHorarioUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<HorarioResultado>> call(GetHorarioParams params) {
    return params.isProfessor
        ? _repository.getTimetableByProfessor(params.id)
        : _repository.getTimetableByTurma(params.id);
  }
}
