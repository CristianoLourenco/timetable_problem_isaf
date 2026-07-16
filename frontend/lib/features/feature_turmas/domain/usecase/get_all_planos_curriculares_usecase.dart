import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/plano_curricular.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_plano_curricular_repository.dart';

/// Use case to retrieve all planos curriculares (needed to resolve `plano_curricular_id` for a Turma).
class GetAllPlanosCurricularesUseCase implements IUseCase<List<PlanoCurricular>, void> {
  GetAllPlanosCurricularesUseCase(this._repository);

  final IPlanoCurricularRepository _repository;

  @override
  Future<DataState<List<PlanoCurricular>>> call(void params) {
    return _repository.getAll();
  }
}
