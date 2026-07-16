import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo_chave.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/repository/i_disponibilidade_repository.dart';

class GetDisponibilidadeUseCase implements IUseCase<List<TempoChave>, int> {
  GetDisponibilidadeUseCase(this._repository);

  final IDisponibilidadeRepository _repository;

  @override
  Future<DataState<List<TempoChave>>> call(int professorId) {
    return _repository.obter(professorId);
  }
}
