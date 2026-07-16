import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/i_turma_remote.dart';
import 'package:ghorario/features/feature_turmas/data/models/turma_dto.dart';

/// Concrete implementation of [ITurmaRemote] using [IHttpMethods].
class TurmaRemoteImpl implements ITurmaRemote {
  TurmaRemoteImpl(this._http);

  final IHttpMethods _http;

  @override
  Future<DataState<List<TurmaDto>>> getAll() async {
    final response = await _http.get<dynamic>('/turmas');
    if (!response.success || response.data == null) {
      return DataState<List<TurmaDto>>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final list = (response.data as List)
          .map((dynamic e) => TurmaDto.fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<TurmaDto>>(data: list, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<TurmaDto>>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar dados das turmas: $e'),
      );
    }
  }

  @override
  Future<DataState<TurmaDto>> getById(String id) async {
    final response = await _http.get<dynamic>('/turmas/$id');
    if (!response.success || response.data == null) {
      return DataState<TurmaDto>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }
    try {
      final dto = TurmaDto.fromJson(response.data as Map<String, dynamic>);
      return DataState<TurmaDto>(data: dto, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<TurmaDto>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar turma: $e'),
      );
    }
  }

  @override
  Future<DataState<void>> create(TurmaDto dto) async {
    final response = await _http.post<dynamic>('/turmas', data: dto.toJson());
    return DataState<void>(
      success: response.success,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> update(TurmaDto dto) async {
    final response = await _http.put<dynamic>('/turmas/${dto.id}', data: dto.toJson());
    return DataState<void>(
      success: response.success,
      error: response.error,
      statusCode: response.statusCode,
    );
  }

  @override
  Future<DataState<void>> delete(String id) async {
    final response = await _http.delete<dynamic>('/turmas/$id');
    return DataState<void>(
      success: response.success,
      error: response.error,
      statusCode: response.statusCode,
    );
  }
}
