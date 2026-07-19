import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/entities/pendencia.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Use case to check for any pending/undistributed allocations for a specific job.
class GetPendenciasUseCase implements IUseCase<List<Pendencia>, String> {
  GetPendenciasUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<List<Pendencia>>> call(String jobId) {
    return _repository.getPendencias(jobId);
  }
}
