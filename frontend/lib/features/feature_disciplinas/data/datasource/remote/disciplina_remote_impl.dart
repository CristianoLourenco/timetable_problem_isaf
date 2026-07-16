import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disciplinas/data/datasource/remote/i_disciplina_remote.dart';
import 'package:ghorario/features/feature_disciplinas/data/models/disciplina_dto.dart';

/// Concrete implementation of [IDisciplinaRemote] using [IHttpMethods].
class DisciplinaRemoteImpl implements IDisciplinaRemote {
  DisciplinaRemoteImpl(this._http);

  final IHttpMethods _http;

  @override
  Future<DataState<List<DisciplinaDto>>> getAll() async {
    final response = await _http.get<dynamic>('/disciplinas');
    if (!response.success || response.data == null) {
      return DataState<List<DisciplinaDto>>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final list = (response.data as List)
          .map((dynamic e) => DisciplinaDto.fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<DisciplinaDto>>(
        data: list,
        success: true,
        statusCode: response.statusCode,
      );
    } catch (e) {
      return DataState<List<DisciplinaDto>>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar dados das disciplinas: $e'),
      );
    }
  }

  @override
  Future<DataState<DisciplinaDto>> getById(String id) async {
    final response = await _http.get<dynamic>('/disciplinas/$id');
    if (!response.success || response.data == null) {
      return DataState<DisciplinaDto>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final dto = DisciplinaDto.fromJson(response.data as Map<String, dynamic>);
      return DataState<DisciplinaDto>(data: dto, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<DisciplinaDto>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar disciplina: $e'),
      );
    }
  }

  @override
  Future<DataState<void>> create(DisciplinaDto dto) async {
    final response = await _http.post<dynamic>('/disciplinas', data: dto.toJson());
    return DataState<void>(
      success: response.success,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> update(DisciplinaDto dto) async {
    final response = await _http.put<dynamic>('/disciplinas/${dto.id}', data: dto.toJson());
    return DataState<void>(
      success: response.success,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> delete(String id) async {
    final response = await _http.delete<dynamic>('/disciplinas/$id');
    return DataState<void>(
      success: response.success,
      error: response.error,
      statusCode: response.statusCode,
    );
  }
}
