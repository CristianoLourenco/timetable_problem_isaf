import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_disponibilidade/data/datasource/remote/i_tempo_remote.dart';
import 'package:ghorario/features/feature_disponibilidade/data/models/tempo_dto.dart';

class TempoRemoteImpl implements ITempoRemote {
  TempoRemoteImpl(this._http);

  final IHttpMethods _http;

  @override
  Future<DataState<List<TempoDto>>> getAll() async {
    final response = await _http.get<dynamic>('/slots');
    if (!response.success || response.data == null) {
      return DataState<List<TempoDto>>(success: false, error: response.error, statusCode: response.statusCode);
    }
    try {
      final list = (response.data as List)
          .map((dynamic e) => TempoDto.fromJson(e as Map<String, dynamic>))
          .toList();
      return DataState<List<TempoDto>>(data: list, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<List<TempoDto>>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar dados dos tempos letivos: $e'),
      );
    }
  }
}
