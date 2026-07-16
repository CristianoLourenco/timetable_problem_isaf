import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_resultado.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Use case to poll `GET /jobs/{job_id}` while the solver is running.
class CheckJobStatusUseCase implements IUseCase<JobResultado, String> {
  CheckJobStatusUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<JobResultado>> call(String jobId) {
    return _repository.checkStatus(jobId);
  }
}
