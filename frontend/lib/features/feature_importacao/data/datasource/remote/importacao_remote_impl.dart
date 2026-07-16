import 'package:dio/dio.dart';
import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_importacao/data/datasource/remote/i_importacao_remote.dart';
import 'package:ghorario/features/feature_importacao/data/models/relatorio_importacao_dto.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/entidade_importacao.dart';

/// Concrete implementation of [IImportacaoRemote].
///
/// Uses [IHttpMethods] with a [FormData] payload — the interface's
/// `dynamic data` parameter is forwarded as-is to Dio, so no change to the
/// generic HTTP contract is needed for this multipart upload.
class ImportacaoRemoteImpl implements IImportacaoRemote {
  ImportacaoRemoteImpl(this._http);

  final IHttpMethods _http;

  @override
  Future<DataState<RelatorioImportacaoDto>> importarExcel({
    required EntidadeImportacao entidade,
    required List<int> bytes,
    required String filename,
  }) async {
    final formData = FormData.fromMap({
      'file': MultipartFile.fromBytes(bytes, filename: filename),
    });

    final response = await _http.post<dynamic>(
      '/upload/excel',
      data: formData,
      queryParameters: {'entidade': entidade.apiValue},
    );

    if (!response.success || response.data == null) {
      return DataState<RelatorioImportacaoDto>(
        success: false,
        error: response.error,
        statusCode: response.statusCode,
      );
    }

    try {
      final dto = RelatorioImportacaoDto.fromJson(response.data as Map<String, dynamic>);
      return DataState<RelatorioImportacaoDto>(data: dto, success: true, statusCode: response.statusCode);
    } catch (e) {
      return DataState<RelatorioImportacaoDto>(
        success: false,
        error: ServerFailure(message: 'Erro ao processar relatório de importação: $e'),
      );
    }
  }
}
