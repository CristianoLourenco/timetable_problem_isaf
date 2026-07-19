import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/entities/alocacao_manual_response.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

class MoverAlocacaoParams {
  const MoverAlocacaoParams({
    required this.alocacaoId,
    required this.diaSemana,
    required this.periodo,
  });

  final int alocacaoId;
  final String diaSemana;
  final int periodo;
}

/// Use case to move/reschedule a specific single-period allocation slot.
class MoverAlocacaoUseCase implements IUseCase<AlocacaoManualResponse, MoverAlocacaoParams> {
  MoverAlocacaoUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<AlocacaoManualResponse>> call(MoverAlocacaoParams params) {
    return _repository.moverAlocacao(
      params.alocacaoId,
      params.diaSemana,
      params.periodo,
    );
  }
}
