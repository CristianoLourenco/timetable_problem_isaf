import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';

/// Use case to delete/remove a manual allocation slot.
class RemoverAlocacaoUseCase implements IUseCase<void, int> {
  RemoverAlocacaoUseCase(this._repository);

  final IHorarioRepository _repository;

  @override
  Future<DataState<void>> call(int alocacaoId) {
    return _repository.removerAlocacao(alocacaoId);
  }
}
