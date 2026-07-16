import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_salas/domain/entities/sala.dart';
import 'package:ghorario/features/feature_salas/domain/repository/i_sala_repository.dart';

/// Use case to create a new Sala.
class CreateSalaUseCase implements IUseCase<void, Sala> {
  CreateSalaUseCase(this._repository);

  final ISalaRepository _repository;

  @override
  Future<DataState<void>> call(Sala params) {
    return _repository.create(params);
  }
}
