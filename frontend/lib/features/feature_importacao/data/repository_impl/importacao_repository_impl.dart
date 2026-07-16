import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_importacao/data/datasource/remote/i_importacao_remote.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/entidade_importacao.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/relatorio_importacao.dart';
import 'package:ghorario/features/feature_importacao/domain/repository/i_importacao_repository.dart';

class ImportacaoRepositoryImpl implements IImportacaoRepository {
  ImportacaoRepositoryImpl({required this.remoteDatasource});

  final IImportacaoRemote remoteDatasource;

  @override
  Future<DataState<RelatorioImportacao>> importarExcel({
    required EntidadeImportacao entidade,
    required List<int> bytes,
    required String filename,
  }) async {
    final response = await remoteDatasource.importarExcel(
      entidade: entidade,
      bytes: bytes,
      filename: filename,
    );
    if (response.success && response.data != null) {
      return DataState<RelatorioImportacao>(
        data: response.data!.toEntity(),
        success: true,
        statusCode: response.statusCode,
      );
    }
    return DataState<RelatorioImportacao>(
      success: false,
      error: response.error,
      statusCode: response.statusCode,
    );
  }
}
