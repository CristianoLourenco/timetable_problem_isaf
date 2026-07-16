import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/plano_curricular.dart';

/// Abstract repository interface for Planos Curriculares (prerequisite for Turma.planoCurricularId).
abstract class IPlanoCurricularRepository {
  Future<DataState<List<PlanoCurricular>>> getAll();
  Future<DataState<void>> create(PlanoCurricular plano);
}
