import 'package:ghorario/features/feature_importacao/domain/entities/relatorio_importacao.dart';

class RelatorioImportacaoDto {
  const RelatorioImportacaoDto({
    required this.totalLinhas,
    required this.importados,
    required this.ignoradosIdempotencia,
    required this.erros,
  });

  final int totalLinhas;
  final int importados;
  final int ignoradosIdempotencia;
  final List<ErroImportacao> erros;

  factory RelatorioImportacaoDto.fromJson(Map<String, dynamic> json) {
    final errosJson = (json['erros'] as List?) ?? const [];
    return RelatorioImportacaoDto(
      totalLinhas: json['total_linhas'] as int? ?? 0,
      importados: json['importados'] as int? ?? 0,
      ignoradosIdempotencia: json['ignorados_idempotencia'] as int? ?? 0,
      erros: errosJson
          .map((dynamic e) => ErroImportacao(
                linha: (e as Map<String, dynamic>)['linha'] as int? ?? 0,
                campo: e['campo'] as String? ?? '',
                motivo: e['motivo'] as String? ?? '',
              ))
          .toList(),
    );
  }

  RelatorioImportacao toEntity() {
    return RelatorioImportacao(
      totalLinhas: totalLinhas,
      importados: importados,
      ignoradosIdempotencia: ignoradosIdempotencia,
      erros: erros,
    );
  }
}
