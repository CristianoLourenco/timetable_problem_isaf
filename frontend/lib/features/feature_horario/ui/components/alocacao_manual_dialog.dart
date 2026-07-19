import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/features/feature_disciplinas/domain/entities/disciplina.dart';
import 'package:ghorario/features/feature_horario/domain/entities/bloco_vago.dart';
import 'package:ghorario/features/feature_horario/domain/entities/professor_qualificado.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/criar_alocacao_manual_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_professores_qualificados_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_slots_vagos_usecase.dart';
import 'package:ghorario/features/feature_horario/presentation/provider/horario_provider.dart';
import 'package:ghorario/features/feature_salas/domain/entities/sala.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';
import 'package:provider/provider.dart';

const Map<String, String> _diaSemanaLabels = {
  'monday': 'Segunda-feira',
  'tuesday': 'Terça-feira',
  'wednesday': 'Quarta-feira',
  'thursday': 'Quinta-feira',
  'friday': 'Sexta-feira',
};

const Map<String, String> _turnoLabels = {
  'manha': 'Manhã',
  'tarde': 'Tarde',
  'noite': 'Noite',
};

/// Full-featured manual allocation dialog.
///
/// Cascade: Turma → Disciplina → Professor (async) → Sala → Bloco Vago (async) → Confirmar
/// Errors from POST /alocacoes (409, etc.) are shown verbatim as the spec requires.
class AlocacaoManualDialog extends StatefulWidget {
  const AlocacaoManualDialog({
    super.key,
    required this.turmas,
    required this.disciplinas,
    required this.salas,
    required this.getProfessoresQualificadosUseCase,
    required this.getSlotsVagosUseCase,
    required this.criarAlocacaoManualUseCase,
    this.preencherTurmaId,
    this.preencherDisciplinaId,
    this.jobId,
  });

  final List<Turma> turmas;
  final List<Disciplina> disciplinas;
  final List<Sala> salas;
  final GetProfessoresQualificadosUseCase getProfessoresQualificadosUseCase;
  final GetSlotsVagosUseCase getSlotsVagosUseCase;
  final CriarAlocacaoManualUseCase criarAlocacaoManualUseCase;
  final String? preencherTurmaId;
  final int? preencherDisciplinaId;
  final String? jobId;

  @override
  State<AlocacaoManualDialog> createState() => _AlocacaoManualDialogState();
}

class _AlocacaoManualDialogState extends State<AlocacaoManualDialog> {
  Turma? _selectedTurma;
  Disciplina? _selectedDisciplina;
  ProfessorQualificado? _selectedProfessor;
  Sala? _selectedSala;
  BlocoVago? _selectedBloco;

  List<ProfessorQualificado> _professores = [];
  List<BlocoVago> _blocos = [];

  bool _loadingProfessores = false;
  bool _loadingBlocos = false;
  bool _submitting = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    // Pre-fill from pendência if provided
    if (widget.preencherTurmaId != null) {
      _selectedTurma = widget.turmas.where((t) => t.id == widget.preencherTurmaId).firstOrNull;
    }
    if (widget.preencherDisciplinaId != null) {
      _selectedDisciplina = widget.disciplinas
          .where((d) => int.tryParse(d.id) == widget.preencherDisciplinaId)
          .firstOrNull;
    }
    if (_selectedTurma != null && _selectedDisciplina != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _loadProfessores());
    }
  }

  Future<void> _loadProfessores() async {
    if (_selectedTurma == null || _selectedDisciplina == null) return;
    setState(() {
      _loadingProfessores = true;
      _professores = [];
      _selectedProfessor = null;
      _blocos = [];
      _selectedBloco = null;
    });
    final result = await widget.getProfessoresQualificadosUseCase(
      GetProfessoresQualificadosParams(
        turmaId: _selectedTurma!.id,
        disciplinaId: _selectedDisciplina!.id,
      ),
    );
    if (!mounted) return;
    setState(() {
      _loadingProfessores = false;
      if (result.success && result.data != null) {
        _professores = result.data!;
      }
    });
  }

  Future<void> _loadBlocos() async {
    final jobId = widget.jobId ?? context.read<HorarioProvider>().currentJobId;
    if (_selectedTurma == null || jobId == null) return;
    setState(() {
      _loadingBlocos = true;
      _blocos = [];
      _selectedBloco = null;
    });
    final result = await widget.getSlotsVagosUseCase(
      GetSlotsVagosParams(
        turmaId: _selectedTurma!.id,
        jobId: jobId,
      ),
    );
    if (!mounted) return;
    setState(() {
      _loadingBlocos = false;
      if (result.success && result.data != null) {
        _blocos = result.data!;
      }
    });
  }

  bool get _canSubmit =>
      _selectedTurma != null &&
      _selectedDisciplina != null &&
      _selectedProfessor != null &&
      _selectedSala != null &&
      _selectedBloco != null &&
      !_submitting;

  Future<void> _submit() async {
    final jobId = widget.jobId ?? context.read<HorarioProvider>().currentJobId;
    if (jobId == null) {
      setState(() => _error = 'Nenhum job ativo encontrado. Gere um horário primeiro.');
      return;
    }
    setState(() {
      _submitting = true;
      _error = null;
    });

    final result = await widget.criarAlocacaoManualUseCase(
      CriarAlocacaoManualParams(
        jobId: jobId,
        turmaId: _selectedTurma!.id,
        disciplinaId: _selectedDisciplina!.id,
        professorId: _selectedProfessor!.id.toString(),
        salaId: _selectedSala!.id,
        diaSemana: _selectedBloco!.diaSemana,
        turno: _selectedBloco!.turno,
        periodos: _selectedBloco!.periodos,
      ),
    );

    if (!mounted) return;
    setState(() => _submitting = false);

    if (result.success) {
      Navigator.of(context).pop(true);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Alocação criada com sucesso!'),
          backgroundColor: AppColors.success,
          behavior: SnackBarBehavior.floating,
        ),
      );
    } else {
      final msg = result.message;
      setState(() => _error = msg.isNotEmpty ? msg : 'Erro ao criar alocação.');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.symmetric(horizontal: 40, vertical: 40),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 4, sigmaY: 4),
          child: Container(
            constraints: const BoxConstraints(maxWidth: 560),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFFE2E8F0), width: 1.2),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 40,
                  offset: const Offset(0, 16),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Header
                _buildHeader(),
                const Divider(height: 1, color: Color(0xFFF1F5F9)),
                // Content
                Flexible(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(28),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildDropdown<Turma>(
                          label: 'Turma',
                          icon: Icons.group_outlined,
                          value: _selectedTurma,
                          items: widget.turmas,
                          itemLabel: (t) => t.code ?? t.name,
                          onChanged: (t) {
                            setState(() {
                              _selectedTurma = t;
                              _selectedDisciplina = null;
                              _selectedProfessor = null;
                              _selectedSala = null;
                              _selectedBloco = null;
                              _professores = [];
                              _blocos = [];
                            });
                          },
                        ),
                        const SizedBox(height: 16),
                        _buildDropdown<Disciplina>(
                          label: 'Disciplina',
                          icon: Icons.book_outlined,
                          value: _selectedDisciplina,
                          items: _selectedTurma != null ? widget.disciplinas : [],
                          itemLabel: (d) => d.name,
                          onChanged: _selectedTurma == null
                              ? null
                              : (d) {
                                  setState(() {
                                    _selectedDisciplina = d;
                                    _selectedProfessor = null;
                                    _professores = [];
                                  });
                                  if (d != null) _loadProfessores();
                                },
                        ),
                        const SizedBox(height: 16),
                        // Professor — async loaded
                        _buildAsyncDropdown<ProfessorQualificado>(
                          label: 'Professor',
                          icon: Icons.person_outlined,
                          loading: _loadingProfessores,
                          value: _selectedProfessor,
                          items: _professores,
                          itemLabel: (p) => p.nome,
                          onChanged: (p) {
                            setState(() {
                              _selectedProfessor = p;
                            });
                            if (p != null && _selectedSala != null) _loadBlocos();
                          },
                          emptyHint: _selectedDisciplina == null
                              ? 'Selecione uma disciplina primeiro'
                              : 'Nenhum professor qualificado',
                        ),
                        const SizedBox(height: 16),
                        _buildDropdown<Sala>(
                          label: 'Sala',
                          icon: Icons.meeting_room_outlined,
                          value: _selectedSala,
                          items: widget.salas,
                          itemLabel: (s) => '${s.name} (cap. ${s.capacity ?? '—'})',
                          onChanged: (s) {
                            setState(() => _selectedSala = s);
                            if (s != null && _selectedProfessor != null) _loadBlocos();
                          },
                        ),
                        const SizedBox(height: 16),
                        // Blocos Vagos — async loaded
                        _buildAsyncDropdown<BlocoVago>(
                          label: 'Bloco de Tempo Livre',
                          icon: Icons.schedule_outlined,
                          loading: _loadingBlocos,
                          value: _selectedBloco,
                          items: _blocos,
                          itemLabel: (b) {
                            final dia = _diaSemanaLabels[b.diaSemana] ?? b.diaSemana;
                            final turno = _turnoLabels[b.turno] ?? b.turno;
                            final periodos = b.periodos.join(', ');
                            return '$dia — $turno (períodos: $periodos)';
                          },
                          onChanged: (b) => setState(() => _selectedBloco = b),
                          emptyHint: _selectedTurma == null
                              ? 'Selecione uma turma primeiro'
                              : 'Nenhum bloco livre disponível',
                        ),
                        if (_error != null) ...[
                          const SizedBox(height: 16),
                          _buildErrorBanner(_error!),
                        ],
                      ],
                    ),
                  ),
                ),
                const Divider(height: 1, color: Color(0xFFF1F5F9)),
                // Footer actions
                _buildFooter(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(28, 24, 20, 20),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.blackBlue.withOpacity(0.06),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(Icons.edit_calendar_outlined, color: AppColors.blackBlue, size: 20),
          ),
          const SizedBox(width: 14),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Alocação Manual',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppColors.blackBlue,
                    fontFamily: 'Poppins',
                  ),
                ),
                Text(
                  'Atribua manualmente uma disciplina a um professor e sala',
                  style: TextStyle(fontSize: 12, color: AppColors.textSecondary, fontFamily: 'Poppins'),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: () => Navigator.of(context).pop(false),
            icon: const Icon(Icons.close, color: AppColors.textSecondary, size: 20),
          ),
        ],
      ),
    );
  }

  Widget _buildFooter() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(28, 16, 28, 24),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          TextButton(
            onPressed: _submitting ? null : () => Navigator.of(context).pop(false),
            style: TextButton.styleFrom(
              foregroundColor: AppColors.textSecondary,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            ),
            child: const Text('Cancelar', style: TextStyle(fontFamily: 'Poppins')),
          ),
          const SizedBox(width: 12),
          ElevatedButton.icon(
            onPressed: _canSubmit ? _submit : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.blackBlue,
              foregroundColor: Colors.white,
              disabledBackgroundColor: const Color(0xFFE2E8F0),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
              elevation: 0,
            ),
            icon: _submitting
                ? const SizedBox(
                    width: 14,
                    height: 14,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.check_circle_outline, size: 16),
            label: Text(
              _submitting ? 'A alocar...' : 'Confirmar Alocação',
              style: const TextStyle(fontWeight: FontWeight.w600, fontFamily: 'Poppins'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDropdown<T>({
    required String label,
    required IconData icon,
    required T? value,
    required List<T> items,
    required String Function(T) itemLabel,
    required ValueChanged<T?>? onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: AppColors.blackBlue,
            fontFamily: 'Poppins',
            letterSpacing: 0.4,
          ),
        ),
        const SizedBox(height: 6),
        Container(
          decoration: BoxDecoration(
            color: onChanged == null ? const Color(0xFFF8FAFC) : Colors.white,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: const Color(0xFFE2E8F0), width: 1.2),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<T>(
              value: items.contains(value) ? value : null,
              isExpanded: true,
              icon: Icon(Icons.keyboard_arrow_down, color: onChanged == null ? const Color(0xFFCBD5E1) : const Color(0xFF64748B)),
              style: const TextStyle(fontSize: 14, color: AppColors.blackBlue, fontFamily: 'Poppins'),
              hint: Row(
                children: [
                  Icon(icon, size: 16, color: const Color(0xFF94A3B8)),
                  const SizedBox(width: 8),
                  Text(
                    'Selecione $label',
                    style: const TextStyle(fontSize: 13, color: Color(0xFF94A3B8), fontFamily: 'Poppins'),
                  ),
                ],
              ),
              items: items
                  .map((item) => DropdownMenuItem<T>(
                        value: item,
                        child: Text(itemLabel(item), overflow: TextOverflow.ellipsis),
                      ))
                  .toList(),
              onChanged: onChanged,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildAsyncDropdown<T>({
    required String label,
    required IconData icon,
    required bool loading,
    required T? value,
    required List<T> items,
    required String Function(T) itemLabel,
    required ValueChanged<T?>? onChanged,
    required String emptyHint,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: AppColors.blackBlue,
            fontFamily: 'Poppins',
            letterSpacing: 0.4,
          ),
        ),
        const SizedBox(height: 6),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: const Color(0xFFE2E8F0), width: 1.2),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
          child: loading
              ? const Padding(
                  padding: EdgeInsets.symmetric(vertical: 10),
                  child: Row(
                    children: [
                      SizedBox(
                        width: 14,
                        height: 14,
                        child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.blackBlue),
                      ),
                      SizedBox(width: 12),
                      Text('A carregar...', style: TextStyle(fontSize: 13, color: AppColors.textSecondary, fontFamily: 'Poppins')),
                    ],
                  ),
                )
              : items.isEmpty
                  ? Padding(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      child: Text(
                        emptyHint,
                        style: const TextStyle(fontSize: 13, color: Color(0xFF94A3B8), fontFamily: 'Poppins'),
                      ),
                    )
                  : DropdownButtonHideUnderline(
                      child: DropdownButton<T>(
                        value: items.contains(value) ? value : null,
                        isExpanded: true,
                        icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF64748B)),
                        style: const TextStyle(fontSize: 14, color: AppColors.blackBlue, fontFamily: 'Poppins'),
                        hint: Row(
                          children: [
                            Icon(icon, size: 16, color: const Color(0xFF94A3B8)),
                            const SizedBox(width: 8),
                            Text(
                              'Selecione $label',
                              style: const TextStyle(fontSize: 13, color: Color(0xFF94A3B8), fontFamily: 'Poppins'),
                            ),
                          ],
                        ),
                        items: items
                            .map((item) => DropdownMenuItem<T>(
                                  value: item,
                                  child: Text(itemLabel(item), overflow: TextOverflow.ellipsis),
                                ))
                            .toList(),
                        onChanged: onChanged,
                      ),
                    ),
        ),
      ],
    );
  }

  Widget _buildErrorBanner(String message) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.error.withOpacity(0.06),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.error.withOpacity(0.25), width: 1),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.error_outline, color: AppColors.error, size: 18),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(fontSize: 13, color: AppColors.error, fontFamily: 'Poppins'),
            ),
          ),
        ],
      ),
    );
  }
}
