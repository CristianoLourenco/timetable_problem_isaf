import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/i_plano_curricular_remote.dart';
import 'package:ghorario/features/feature_turmas/data/models/plano_curricular_dto.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/plano_curricular.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_plano_curricular_repository.dart';

/// Concrete implementation of [IPlanoCurricularRepository].
class PlanoCurricularRepositoryImpl implements IPlanoCurricularRepository {
  PlanoCurricularRepositoryImpl({required this.remoteDatasource});

  final IPlanoCurricularRemote remoteDatasource;

  @override
  Future<DataState<List<PlanoCurricular>>> getAll() async {
    final response = await remoteDatasource.getAll();
    if (response.success && response.data != null) {
      final entities = response.data!.map((PlanoCurricularDto dto) => dto.toEntity()).toList();
      return DataState<List<PlanoCurricular>>(data: entities, success: true, statusCode: response.statusCode);
    }
    return DataState<List<PlanoCurricular>>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> create(PlanoCurricular plano) {
    return remoteDatasource.create(PlanoCurricularDto.fromEntity(plano));
  }
}
