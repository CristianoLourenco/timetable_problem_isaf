import 'package:flutter/material.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/features/feature_disciplinas/domain/entities/disciplina.dart';
import 'package:ghorario/features/feature_docentes/domain/usecase/get_qualificacao_usecase.dart';
import 'package:ghorario/features/feature_docentes/domain/usecase/set_qualificacao_usecase.dart';

/// Dialog to view/edit a Professor's qualification (`GET|POST /professores/{id}/disciplinas`)
/// — which disciplinas they are allowed to teach (mandatory solver filter).
///
/// Receives use cases and data as parameters — no direct Provider access,
/// per the project's architecture rule for Components.
class QualificacaoDialog extends StatefulWidget {
  const QualificacaoDialog({
    super.key,
    required this.professorId,
    required this.professorNome,
    required this.disciplinas,
    required this.getQualificacaoUseCase,
    required this.setQualificacaoUseCase,
  });

  final int professorId;
  final String professorNome;
  final List<Disciplina> disciplinas;
  final GetQualificacaoUseCase getQualificacaoUseCase;
  final SetQualificacaoUseCase setQualificacaoUseCase;

  @override
  State<QualificacaoDialog> createState() => _QualificacaoDialogState();
}

class _QualificacaoDialogState extends State<QualificacaoDialog> {
  bool _isLoading = true;
  bool _isSaving = false;
  String? _error;
  final Set<int> _selectedDisciplinaIds = {};

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final result = await widget.getQualificacaoUseCase(widget.professorId);
    if (!mounted) return;
    if (result.success && result.data != null) {
      setState(() {
        _selectedDisciplinaIds.addAll(result.data!);
        _isLoading = false;
      });
    } else {
      setState(() {
        _error = result.message;
        _isLoading = false;
      });
    }
  }

  Future<void> _save() async {
    setState(() => _isSaving = true);
    final result = await widget.setQualificacaoUseCase(
      SetQualificacaoParams(professorId: widget.professorId, disciplinaIds: _selectedDisciplinaIds.toList()),
    );
    if (!mounted) return;
    if (result.success) {
      Navigator.pop(context);
    } else {
      setState(() {
        _isSaving = false;
        _error = result.message;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Qualificação — ${widget.professorNome}'),
      content: SizedBox(
        width: 380,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (_error != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text(_error!, style: const TextStyle(color: Colors.red)),
                    ),
                  ConstrainedBox(
                    constraints: const BoxConstraints(maxHeight: 360),
                    child: SingleChildScrollView(
                      child: Column(
                        children: widget.disciplinas.map((disciplina) {
                          final id = int.tryParse(disciplina.id);
                          if (id == null) return const SizedBox.shrink();
                          return CheckboxListTile(
                            value: _selectedDisciplinaIds.contains(id),
                            title: Text(disciplina.name),
                            onChanged: (val) {
                              setState(() {
                                if (val == true) {
                                  _selectedDisciplinaIds.add(id);
                                } else {
                                  _selectedDisciplinaIds.remove(id);
                                }
                              });
                            },
                          );
                        }).toList(),
                      ),
                    ),
                  ),
                ],
              ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
        ElevatedButton(
          onPressed: _isSaving || _isLoading ? null : _save,
          style: ElevatedButton.styleFrom(backgroundColor: AppColors.blackBlue, foregroundColor: Colors.white),
          child: _isSaving
              ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
              : const Text('Guardar'),
        ),
      ],
    );
  }
}
