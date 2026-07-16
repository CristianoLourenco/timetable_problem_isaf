import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/models/plano_curricular_dto.dart';

/// Abstract remote datasource interface for Planos Curriculares.
abstract class IPlanoCurricularRemote {
  Future<DataState<List<PlanoCurricularDto>>> getAll();
  Future<DataState<void>> create(PlanoCurricularDto dto);
}
