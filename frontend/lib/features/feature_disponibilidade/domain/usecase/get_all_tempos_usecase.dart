import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/repository/i_tempo_repository.dart';

class GetAllTemposUseCase implements IUseCase<List<Tempo>, void> {
  GetAllTemposUseCase(this._repository);

  final ITempoRepository _repository;

  @override
  Future<DataState<List<Tempo>>> call(void params) {
    return _repository.getAll();
  }
}
