import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_resultado.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Parameters for [GetJobByScopeUseCase].
class GetJobByScopeParams {
  const GetJobByScopeParams({required this.anoLetivo, required this.semestre});

  final int anoLetivo;
  final String semestre;
}

/// Use case to fetch the active job for a given academic year/semester scope.
/// Returns null data if no job exists yet for that scope.
class GetJobByScopeUseCase implements IUseCase<JobResultado?, GetJobByScopeParams> {
  GetJobByScopeUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<JobResultado?>> call(GetJobByScopeParams params) {
    return _repository.getJobByScope(params.anoLetivo, params.semestre);
  }
}
