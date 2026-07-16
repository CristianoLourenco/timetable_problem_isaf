import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_docentes/data/datasource/remote/i_docente_remote.dart';
import 'package:ghorario/features/feature_docentes/data/models/docente_dto.dart';

/// Concrete implementation of [IDocenteRemote] using [IHttpMethods].
///
/// Talks to the backend's `/professores` routes (entity is `Professor`
/// there — see [DocenteDto]).
class DocenteRemoteImpl implements IDocenteRemote {
  DocenteRemoteImpl(this._http);

  final IHttpMethods _http;

  @override
  Future<DataState<List<DocenteDto>>> getAll() async {
    final response = await _http.get<dynamic>('/professores');
    if (!response.success || response.data == null) {
      return DataState<List<DocenteDto>>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final list = (response.data as List)
          .map((dynamic e) => DocenteDto.fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<DocenteDto>>(data: list, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<DocenteDto>>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar dados dos professores: $e'),
      );
    }
  }

  @override
  Future<DataState<DocenteDto>> getById(String id) async {
    final response = await _http.get<dynamic>('/professores/$id');
    if (!response.success || response.data == null) {
      return DataState<DocenteDto>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final dto = DocenteDto.fromJson(response.data as Map<String, dynamic>);
      return DataState<DocenteDto>(data: dto, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<DocenteDto>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar professor: $e'),
      );
    }
  }

  @override
  Future<DataState<void>> create(DocenteDto dto) async {
    final response = await _http.post<dynamic>('/professores', data: dto.toJson());
    return DataState<void>(
      success: response.success,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> update(DocenteDto dto) async {
    final response = await _http.put<dynamic>('/professores/${dto.id}', data: dto.toJson());
    return DataState<void>(
      success: response.success,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> delete(String id) async {
    final response = await _http.delete<dynamic>('/professores/$id');
    return DataState<void>(
      success: response.success,
      error: response.error,
      statusCode: response.statusCode,
    );
  }
}
