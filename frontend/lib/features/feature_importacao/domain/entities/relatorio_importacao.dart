/// Implementa: RF06, RF07, RF08 (UC06, UC07) — ver docs/analise_requisitos_v5.0.md
class ErroImportacao {
  const ErroImportacao({required this.linha, required this.campo, required this.motivo});

  final int linha;
  final String campo;
  final String motivo;
}

/// Report returned by `POST /upload/excel` — the endpoint never aborts on the
/// first invalid row, it always returns every error found (RF07).
class RelatorioImportacao {
  const RelatorioImportacao({
    required this.totalLinhas,
    required this.importados,
    required this.ignoradosIdempotencia,
    required this.erros,
  });

  final int totalLinhas;
  final int importados;
  final int ignoradosIdempotencia;
  final List<ErroImportacao> erros;

  bool get temErros => erros.isNotEmpty;
}
