import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_importacao/data/models/relatorio_importacao_dto.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/entidade_importacao.dart';

/// Abstract remote datasource interface for bulk Excel import.
abstract class IImportacaoRemote {
  Future<DataState<RelatorioImportacaoDto>> importarExcel({
    required EntidadeImportacao entidade,
    required List<int> bytes,
    required String filename,
  });
}
