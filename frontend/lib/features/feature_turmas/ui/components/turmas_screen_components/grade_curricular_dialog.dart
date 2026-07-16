import 'package:flutter/material.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/features/feature_disciplinas/domain/entities/disciplina.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/item_grade_curricular.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/get_grade_curricular_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/set_grade_curricular_usecase.dart';

/// Dialog to view/edit a Turma's curriculum grid (`GET|POST /turmas/{id}/disciplinas`).
///
/// Receives use cases and data as parameters — no direct Provider access,
/// per the project's architecture rule for Components.
class GradeCurricularDialog extends StatefulWidget {
  const GradeCurricularDialog({
    super.key,
    required this.turmaId,
    required this.turmaNome,
    required this.disciplinas,
    required this.getGradeCurricularUseCase,
    required this.setGradeCurricularUseCase,
  });

  final int turmaId;
  final String turmaNome;
  final List<Disciplina> disciplinas;
  final GetGradeCurricularUseCase getGradeCurricularUseCase;
  final SetGradeCurricularUseCase setGradeCurricularUseCase;

  @override
  State<GradeCurricularDialog> createState() => _GradeCurricularDialogState();
}

class _GradeCurricularDialogState extends State<GradeCurricularDialog> {
  bool _isLoading = true;
  bool _isSaving = false;
  String? _error;
  final Map<int, TextEditingController> _cargaControllers = {};
  final Set<int> _selectedDisciplinaIds = {};

  @override
  void initState() {
    super.initState();
    for (final disciplina in widget.disciplinas) {
      final id = int.tryParse(disciplina.id);
      if (id != null) _cargaControllers[id] = TextEditingController(text: '2');
    }
    _load();
  }

  @override
  void dispose() {
    for (final controller in _cargaControllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> _load() async {
    final result = await widget.getGradeCurricularUseCase(widget.turmaId);
    if (!mounted) return;
    if (result.success && result.data != null) {
      setState(() {
        for (final item in result.data!) {
          _selectedDisciplinaIds.add(item.disciplinaId);
          _cargaControllers[item.disciplinaId]?.text = item.cargaHorariaSemanal.toString();
        }
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
    final itens = _selectedDisciplinaIds
        .map((id) => ItemGradeCurricular(
              disciplinaId: id,
              cargaHorariaSemanal: int.tryParse(_cargaControllers[id]?.text ?? '') ?? 1,
            ))
        .toList();
    final result = await widget.setGradeCurricularUseCase(
      SetGradeCurricularParams(turmaId: widget.turmaId, itens: itens),
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
      title: Text('Grade Curricular — ${widget.turmaNome}'),
      content: SizedBox(
        width: 420,
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
                          final selected = _selectedDisciplinaIds.contains(id);
                          return Row(
                            children: [
                              Checkbox(
                                value: selected,
                                onChanged: (val) {
                                  setState(() {
                                    if (val == true) {
                                      _selectedDisciplinaIds.add(id);
                                    } else {
                                      _selectedDisciplinaIds.remove(id);
                                    }
                                  });
                                },
                              ),
                              Expanded(child: Text(disciplina.name)),
                              SizedBox(
                                width: 80,
                                child: TextField(
                                  controller: _cargaControllers[id],
                                  enabled: selected,
                                  keyboardType: TextInputType.number,
                                  decoration: const InputDecoration(labelText: 'h/semana', isDense: true),
                                ),
                              ),
                            ],
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
