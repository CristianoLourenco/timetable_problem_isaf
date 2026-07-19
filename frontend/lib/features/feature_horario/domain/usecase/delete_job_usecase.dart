import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Use case to delete (clear) a generated timetable job by its ID.
/// Returns 204 No Content on success.
class DeleteJobUseCase implements IUseCase<void, String> {
  DeleteJobUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<void>> call(String jobId) {
    return _repository.deleteJob(jobId);
  }
}
