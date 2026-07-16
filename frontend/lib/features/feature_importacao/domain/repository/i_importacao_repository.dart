import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/entidade_importacao.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/relatorio_importacao.dart';

abstract class IImportacaoRepository {
  Future<DataState<RelatorioImportacao>> importarExcel({
    required EntidadeImportacao entidade,
    required List<int> bytes,
    required String filename,
  });
}
