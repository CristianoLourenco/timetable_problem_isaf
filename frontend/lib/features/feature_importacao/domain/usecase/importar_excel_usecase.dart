import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/entidade_importacao.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/relatorio_importacao.dart';
import 'package:ghorario/features/feature_importacao/domain/repository/i_importacao_repository.dart';

class ImportarExcelParams {
  const ImportarExcelParams({
    required this.entidade,
    required this.bytes,
    required this.filename,
  });

  final EntidadeImportacao entidade;
  final List<int> bytes;
  final String filename;
}

/// Use case to bulk-import an entity from a .xlsx file (RF06/RF07/RF08).
class ImportarExcelUseCase implements IUseCase<RelatorioImportacao, ImportarExcelParams> {
  ImportarExcelUseCase(this._repository);

  final IImportacaoRepository _repository;

  @override
  Future<DataState<RelatorioImportacao>> call(ImportarExcelParams params) {
    return _repository.importarExcel(
      entidade: params.entidade,
      bytes: params.bytes,
      filename: params.filename,
    );
  }
}
