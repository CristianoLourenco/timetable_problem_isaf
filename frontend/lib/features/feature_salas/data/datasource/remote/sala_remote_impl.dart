import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_salas/data/datasource/remote/i_sala_remote.dart';
import 'package:ghorario/features/feature_salas/data/models/sala_dto.dart';

/// Concrete implementation of [ISalaRemote] using [IHttpMethods].
class SalaRemoteImpl implements ISalaRemote {
  SalaRemoteImpl(this._http);

  final IHttpMethods _http;

  @override
  Future<DataState<List<SalaDto>>> getAll() async {
    final response = await _http.get<dynamic>('/salas');
    if (!response.success || response.data == null) {
      return DataState<List<SalaDto>>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final list = (response.data as List)
          .map((dynamic e) => SalaDto.fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<SalaDto>>(data: list, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<SalaDto>>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar dados das salas: $e'),
      );
    }
  }

  @override
  Future<DataState<SalaDto>> getById(String id) async {
    final response = await _http.get<dynamic>('/salas/$id');
    if (!response.success || response.data == null) {
      return DataState<SalaDto>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final dto = SalaDto.fromJson(response.data as Map<String, dynamic>);
      return DataState<SalaDto>(data: dto, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<SalaDto>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar sala: $e'),
      );
    }
  }

  @override
  Future<DataState<void>> create(SalaDto dto) async {
    final response = await _http.post<dynamic>('/salas', data: dto.toJson());
    return DataState<void>(
      success: response.success,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> update(SalaDto dto) async {
    final response = await _http.put<dynamic>('/salas/${dto.id}', data: dto.toJson());
    return DataState<void>(
      success: response.success,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> delete(String id) async {
    final response = await _http.delete<dynamic>('/salas/$id');
    return DataState<void>(
      success: response.success,
      error: response.error,
      statusCode: response.statusCode,
    );
  }
}
