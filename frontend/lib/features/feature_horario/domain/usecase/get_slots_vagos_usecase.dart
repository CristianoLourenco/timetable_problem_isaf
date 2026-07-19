import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/entities/bloco_vago.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

class GetSlotsVagosParams {
  const GetSlotsVagosParams({
    required this.turmaId,
    required this.jobId,
  });

  final String turmaId;
  final String jobId;
}

/// Use case to fetch vacant slots for a specific class (turma) under a job session.
class GetSlotsVagosUseCase implements IUseCase<List<BlocoVago>, GetSlotsVagosParams> {
  GetSlotsVagosUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<List<BlocoVago>>> call(GetSlotsVagosParams params) {
    return _repository.getSlotsVagos(params.turmaId, params.jobId);
  }
}
