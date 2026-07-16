import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo_chave.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/repository/i_disponibilidade_repository.dart';

class SetDisponibilidadeParams {
  const SetDisponibilidadeParams({required this.professorId, required this.tempos});

  final int professorId;
  final List<TempoChave> tempos;
}

class SetDisponibilidadeUseCase implements IUseCase<List<TempoChave>, SetDisponibilidadeParams> {
  SetDisponibilidadeUseCase(this._repository);

  final IDisponibilidadeRepository _repository;

  @override
  Future<DataState<List<TempoChave>>> call(SetDisponibilidadeParams params) {
    return _repository.definir(params.professorId, params.tempos);
  }
}
