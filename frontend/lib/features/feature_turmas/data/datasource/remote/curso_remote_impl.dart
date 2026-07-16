import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/i_curso_remote.dart';
import 'package:ghorario/features/feature_turmas/data/models/curso_dto.dart';

/// Concrete implementation of [ICursoRemote] using [IHttpMethods].
class CursoRemoteImpl implements ICursoRemote {
  CursoRemoteImpl(this._http);

  final IHttpMethods _http;

  @override
  Future<DataState<List<CursoDto>>> getAll() async {
    final response = await _http.get<dynamic>('/cursos');
    if (!response.success || response.data == null) {
      return DataState<List<CursoDto>>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final list = (response.data as List)
          .map((dynamic e) => CursoDto.fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<CursoDto>>(data: list, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<CursoDto>>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar dados dos cursos: $e'),
      );
    }
  }

  @override
  Future<DataState<void>> create(CursoDto dto) async {
    final response = await _http.post<dynamic>('/cursos', data: dto.toJson());
    return DataState<void>(success: response.success, error: response.error, statusCode: response.statusCode);
  }
}
