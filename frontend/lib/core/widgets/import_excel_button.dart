import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/entidade_importacao.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/relatorio_importacao.dart';
import 'package:ghorario/features/feature_importacao/domain/usecase/importar_excel_usecase.dart';

/// Reusable "Importar Excel" button (RF06/RF07/RF08).
///
/// Receives the use case and callbacks as parameters — no direct Provider
/// access inside this Component, per the project's architecture rule.
class ImportExcelButton extends StatefulWidget {
  const ImportExcelButton({
    super.key,
    required this.entidade,
    required this.importarExcelUseCase,
    required this.onImported,
    this.label = 'Importar Excel',
  });

  final EntidadeImportacao entidade;
  final ImportarExcelUseCase importarExcelUseCase;
  final VoidCallback onImported;
  final String label;

  @override
  State<ImportExcelButton> createState() => _ImportExcelButtonState();
}

class _ImportExcelButtonState extends State<ImportExcelButton> {
  bool _isImporting = false;

  Future<void> _pickAndImport() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['xlsx'],
      withData: true,
    );
    final file = result?.files.single;
    if (file == null || file.bytes == null) return;

    setState(() => _isImporting = true);
    final response = await widget.importarExcelUseCase(
      ImportarExcelParams(entidade: widget.entidade, bytes: file.bytes!, filename: file.name),
    );
    if (!mounted) return;
    setState(() => _isImporting = false);

    if (response.success && response.data != null) {
      _showRelatorio(response.data!);
      widget.onImported();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(response.message), backgroundColor: Colors.red),
      );
    }
  }

  void _showRelatorio(RelatorioImportacao relatorio) {
    showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Relatório de Importação'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Linhas processadas: ${relatorio.totalLinhas}'),
            Text('Importados: ${relatorio.importados}'),
            Text('Ignorados (já existentes): ${relatorio.ignoradosIdempotencia}'),
            if (relatorio.temErros) ...[
              const SizedBox(height: 12),
              Text('Erros (${relatorio.erros.length}):', style: const TextStyle(fontWeight: FontWeight.bold)),
              ConstrainedBox(
                constraints: const BoxConstraints(maxHeight: 200),
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: relatorio.erros
                        .map((e) => Text('Linha ${e.linha} (${e.campo}): ${e.motivo}'))
                        .toList(),
                  ),
                ),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Fechar')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return OutlinedButton.icon(
      onPressed: _isImporting ? null : _pickAndImport,
      style: OutlinedButton.styleFrom(
        backgroundColor: Colors.white,
        side: const BorderSide(color: Color(0xFFE2E8F0), width: 1.2),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
      ),
      icon: _isImporting
          ? const SizedBox(
              width: 14,
              height: 14,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : const Icon(Icons.upload_file, size: 18, color: AppColors.blackBlue),
      label: Text(
        widget.label,
        style: const TextStyle(color: AppColors.blackBlue, fontWeight: FontWeight.w600, fontFamily: 'Poppins'),
      ),
    );
  }
}
