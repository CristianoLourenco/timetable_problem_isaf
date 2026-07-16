import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/i_plano_curricular_remote.dart';
import 'package:ghorario/features/feature_turmas/data/models/plano_curricular_dto.dart';

/// Concrete implementation of [IPlanoCurricularRemote] using [IHttpMethods].
class PlanoCurricularRemoteImpl implements IPlanoCurricularRemote {
  PlanoCurricularRemoteImpl(this._http);

  final IHttpMethods _http;

  @override
  Future<DataState<List<PlanoCurricularDto>>> getAll() async {
    final response = await _http.get<dynamic>('/planos-curriculares');
    if (!response.success || response.data == null) {
      return DataState<List<PlanoCurricularDto>>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final list = (response.data as List)
          .map((dynamic e) => PlanoCurricularDto.fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<PlanoCurricularDto>>(data: list, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<PlanoCurricularDto>>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar dados dos planos curriculares: $e'),
      );
    }
  }

  @override
  Future<DataState<void>> create(PlanoCurricularDto dto) async {
    final response = await _http.post<dynamic>('/planos-curriculares', data: dto.toJson());
    return DataState<void>(success: response.success, error: response.error, statusCode: response.statusCode);
  }
}
