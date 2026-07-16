import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_salas/domain/entities/sala.dart';
import 'package:ghorario/features/feature_salas/domain/repository/i_sala_repository.dart';

/// Use case to retrieve all rooms/salas.
class GetAllSalasUseCase implements IUseCase<List<Sala>, void> {
  GetAllSalasUseCase(this._repository);

  final ISalaRepository _repository;

  @override
  Future<DataState<List<Sala>>> call(void params) {
    return _repository.getAll();
  }
}
