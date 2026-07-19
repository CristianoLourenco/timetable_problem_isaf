import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/features/feature_disciplinas/presentation/provider/disciplinas_provider.dart';
import 'package:ghorario/features/feature_docentes/domain/entities/docente.dart';
import 'package:ghorario/features/feature_docentes/presentation/provider/docentes_provider.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_slot.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/criar_alocacao_manual_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_professores_qualificados_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_slots_vagos_usecase.dart';
import 'package:ghorario/features/feature_horario/presentation/controller/horario_controller.dart';
import 'package:ghorario/features/feature_horario/presentation/provider/horario_provider.dart';
import 'package:ghorario/features/feature_horario/presentation/states/horario_state.dart';
import 'package:ghorario/features/feature_horario/ui/components/alocacao_manual_dialog.dart';
import 'package:ghorario/features/feature_salas/presentation/provider/salas_provider.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/turmas_provider.dart';
import 'package:ghorario/features/feature_docentes/ui/components/docentes_screen_components/qualificacao_dialog.dart';
import 'package:ghorario/features/feature_docentes/domain/usecase/get_qualificacao_usecase.dart';
import 'package:ghorario/features/feature_docentes/domain/usecase/set_qualificacao_usecase.dart';


const List<String> _weekdayLabels = [
  'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta',
];

const List<String> _turnos = ['manha', 'tarde', 'noite'];

const Map<String, String> _turnoLabels = {
  'manha': 'Manhã',
  'tarde': 'Tarde',
  'noite': 'Noite',
};

/// Derives a stable, visually distinct HSL color from a discipline ID integer.
Color _disciplinaColor(int disciplinaId, {double alpha = 1.0}) {
  const hues = [210.0, 280.0, 150.0, 30.0, 340.0, 60.0, 190.0, 320.0, 90.0, 0.0];
  final hue = hues[disciplinaId % hues.length];
  return HSLColor.fromAHSL(alpha, hue, 0.65, 0.52).toColor();
}

/// Detail screen for a specific teacher — Funcionalidade 4.
///
/// Loaded via `/dashboard/docentes/:id`. Shows:
/// - Teacher info card
/// - Timetable tabs by shift (Manhã/Tarde/Noite) using GET /horarios/professor/{id}
/// - Subject+class summary legend at the bottom
/// - "Trocar Disciplina" action → DELETE + POST (Opção A — aprovada)
class DocenteDetalheScreen extends StatefulWidget {
  const DocenteDetalheScreen({super.key, required this.docenteId});

  final String docenteId;

  @override
  State<DocenteDetalheScreen> createState() => _DocenteDetalheScreenState();
}

class _DocenteDetalheScreenState extends State<DocenteDetalheScreen>
    with SingleTickerProviderStateMixin {
  late final HorarioController _controller;
  late final TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _controller = HorarioController(provider: context.read<HorarioProvider>())..init();

    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (!mounted) return;
      _controller.fetchTimetableByProfessor(widget.docenteId);

      final salas = context.read<SalasProvider>();
      final disciplinas = context.read<DisciplinasProvider>();
      final turmas = context.read<TurmasProvider>();

      if (salas.salas.isEmpty) await salas.loadSalas();
      if (disciplinas.disciplinas.isEmpty) await disciplinas.loadDisciplinas();
      if (turmas.turmas.isEmpty) await turmas.loadTurmas();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _tabController.dispose();
    super.dispose();
  }

  Docente? _findDocente() {
    final docentesProvider = context.read<DocentesProvider>();
    return docentesProvider.docentes
        .where((d) => d.id == widget.docenteId)
        .firstOrNull;
  }

  String _getInitials(String name) {
    final parts = name.trim().split(' ').where((e) => e.isNotEmpty).toList();
    if (parts.length >= 2) return '${parts[0][0]}${parts[parts.length - 1][0]}'.toUpperCase();
    if (parts.isNotEmpty && parts[0].isNotEmpty) return parts[0][0].toUpperCase();
    return '?';
  }

  Future<void> _showQualificacaoDialog(Docente docente) async {
    final professorId = int.tryParse(docente.id);
    if (professorId == null) return;

    final disciplinasProvider = context.read<DisciplinasProvider>();
    if (disciplinasProvider.disciplinas.isEmpty) {
      await disciplinasProvider.loadDisciplinas();
    }
    if (!mounted) return;

    await showDialog<void>(
      context: context,
      builder: (context) => QualificacaoDialog(
        professorId: professorId,
        professorNome: docente.name,
        disciplinas: disciplinasProvider.disciplinas,
        getQualificacaoUseCase: context.read<GetQualificacaoUseCase>(),
        setQualificacaoUseCase: context.read<SetQualificacaoUseCase>(),
      ),
    );
  }

  Future<void> _openAlocacaoDialog({int? preencherDisciplinaId}) async {
    final horarioProvider = context.read<HorarioProvider>();
    final disciplinas = context.read<DisciplinasProvider>().disciplinas;
    final salas = context.read<SalasProvider>().salas;
    final turmas = context.read<TurmasProvider>().turmas;

    final result = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlocacaoManualDialog(
        turmas: turmas,
        disciplinas: disciplinas,
        salas: salas,
        pendencias: horarioProvider.pendencias,
        getProfessoresQualificadosUseCase: context.read<GetProfessoresQualificadosUseCase>(),
        getSlotsVagosUseCase: context.read<GetSlotsVagosUseCase>(),
        criarAlocacaoManualUseCase: context.read<CriarAlocacaoManualUseCase>(),
        preencherDisciplinaId: preencherDisciplinaId,
        jobId: horarioProvider.currentJobId,
      ),
    );

    if (result == true && mounted) {
      _controller.fetchTimetableByProfessor(widget.docenteId);
    }
  }

  Future<void> _trocarDisciplina(HorarioSlot slot) async {
    // Opção A: DELETE the current allocation, then open POST dialog pre-filled with turma/disciplina
    if (slot.alocacaoId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Esta alocação não tem ID — não pode ser removida.'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text(
          'Trocar Disciplina/Professor',
          style: TextStyle(fontFamily: 'Poppins', fontWeight: FontWeight.bold, fontSize: 16),
        ),
        content: Text(
          'Isto vai remover a alocação de "${slot.disciplinaName}" (${slot.turmaName}) '
          'neste bloco e abrir o diálogo de nova alocação pré-preenchido com a mesma turma e disciplina. '
          'Confirmar?',
          style: const TextStyle(fontFamily: 'Poppins', fontSize: 13),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancelar', style: TextStyle(color: AppColors.textSecondary)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.blackBlue,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Confirmar', style: TextStyle(fontFamily: 'Poppins')),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    final removed = await _controller.removerAlocacao(slot.alocacaoId!);
    if (!mounted) return;

    if (!removed) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_controller.value.alocacaoError ?? 'Erro ao remover alocação.'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    // Open new allocation dialog pre-filled with same disciplina
    await _openAlocacaoDialog(preencherDisciplinaId: slot.disciplinaId);
  }

  @override
  Widget build(BuildContext context) {
    final docente = _findDocente();

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: ValueListenableBuilder<HorarioState>(
        valueListenable: _controller,
        builder: (context, state, _) {
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Back button + header
                Row(
                  children: [
                    InkWell(
                      onTap: () => context.pop(),
                      borderRadius: BorderRadius.circular(8),
                      child: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFFE2E8F0), width: 1.2),
                        ),
                        child: const Icon(Icons.arrow_back, size: 18, color: AppColors.blackBlue),
                      ),
                    ),
                    const SizedBox(width: 16),
                    if (docente != null) ...[
                      CircleAvatar(
                        radius: 24,
                        backgroundColor: AppColors.blackBlue,
                        child: Text(
                          _getInitials(docente.name),
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontFamily: 'Poppins'),
                        ),
                      ),
                      const SizedBox(width: 14),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            docente.name,
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: AppColors.blackBlue,
                              fontFamily: 'Poppins',
                            ),
                          ),
                          if (docente.email != null)
                            Text(
                              docente.email!,
                              style: const TextStyle(fontSize: 13, color: AppColors.textSecondary, fontFamily: 'Poppins'),
                            ),
                        ],
                      ),
                      const Spacer(),
                      ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.white,
                          foregroundColor: AppColors.blackBlue,
                          elevation: 0,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                            side: const BorderSide(color: Color(0xFFE2E8F0), width: 1.2),
                          ),
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        ),
                        onPressed: () => _showQualificacaoDialog(docente),
                        icon: const Icon(Icons.school_outlined, size: 18),
                        label: const Text('Qualificações', style: TextStyle(fontFamily: 'Poppins', fontWeight: FontWeight.w600)),
                      ),
                    ] else
                      const Text(
                        'Ficha do Docente',
                        style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.blackBlue, fontFamily: 'Poppins'),
                      ),
                    const Spacer(),
                    ElevatedButton.icon(
                      onPressed: () => _openAlocacaoDialog(),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.blackBlue,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                        elevation: 0,
                      ),
                      icon: const Icon(Icons.add_circle_outline, size: 16),
                      label: const Text(
                        'Nova Alocação',
                        style: TextStyle(fontWeight: FontWeight.w600, fontFamily: 'Poppins'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                // Main card with tabs
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFFE8EEF5), width: 1.2),
                    ),
                    clipBehavior: Clip.antiAlias,
                    child: Column(
                      children: [
                        // Tabs
                        Container(
                          color: const Color(0xFFF8FAFC),
                          child: TabBar(
                            controller: _tabController,
                            labelStyle: const TextStyle(fontWeight: FontWeight.w600, fontFamily: 'Poppins', fontSize: 13),
                            unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.normal, fontFamily: 'Poppins', fontSize: 13),
                            labelColor: AppColors.blackBlue,
                            unselectedLabelColor: AppColors.textSecondary,
                            indicatorColor: AppColors.blackBlue,
                            indicatorWeight: 2.5,
                            tabs: _turnos.map((t) => Tab(text: _turnoLabels[t])).toList(),
                          ),
                        ),
                        Expanded(
                          child: state.isLoading
                              ? const Center(child: CircularProgressIndicator(color: AppColors.blackBlue))
                              : state.errorMessage != null
                                  ? Center(
                                      child: Text(
                                        state.errorMessage!,
                                        style: const TextStyle(color: AppColors.error, fontFamily: 'Poppins'),
                                      ),
                                    )
                                  : TabBarView(
                                      controller: _tabController,
                                      children: _turnos
                                          .map((turno) => _DocenteTurnoGrade(
                                                turno: turno,
                                                slots: state.slots.where((s) => s.turno == turno).toList(),
                                                onTrocarDisciplina: _trocarDisciplina,
                                              ))
                                          .toList(),
                                    ),
                        ),
                        // Legend
                        if (!state.isLoading && state.slots.isNotEmpty)
                          _DocenteLegenda(slots: state.slots),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _DocenteTurnoGrade extends StatelessWidget {
  const _DocenteTurnoGrade({
    required this.turno,
    required this.slots,
    required this.onTrocarDisciplina,
  });

  final String turno;
  final List<HorarioSlot> slots;
  final Future<void> Function(HorarioSlot) onTrocarDisciplina;

  @override
  Widget build(BuildContext context) {
    if (slots.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.event_busy_outlined, size: 48, color: Colors.grey[300]),
            const SizedBox(height: 12),
            Text(
              'Nenhuma aula no turno ${_turnoLabels[turno] ?? turno}',
              style: const TextStyle(color: AppColors.textSecondary, fontFamily: 'Poppins', fontSize: 13),
            ),
          ],
        ),
      );
    }

    final timeSlots = slots.map((s) => s.timeSlot).toSet().toList()..sort();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Day header
          Row(
            children: [
              const SizedBox(width: 120),
              for (final day in _weekdayLabels)
                Expanded(
                  child: Center(
                    child: Text(
                      day,
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF94A3B8),
                        letterSpacing: 0.8,
                        fontFamily: 'Poppins',
                      ),
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          for (final timeLabel in timeSlots) ...[
            _buildRow(context, timeLabel),
            const SizedBox(height: 8),
          ],
        ],
      ),
    );
  }

  Widget _buildRow(BuildContext context, String timeLabel) {
    return SizedBox(
      height: 80,
      child: Row(
        children: [
          SizedBox(
            width: 120,
            child: Text(
              timeLabel,
              style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8), fontFamily: 'Poppins'),
            ),
          ),
          for (int day = 1; day <= 5; day++)
            Expanded(child: _buildCell(context, day, timeLabel)),
        ],
      ),
    );
  }

  Widget _buildCell(BuildContext context, int dayOfWeek, String timeLabel) {
    final match = slots.where((s) => s.dayOfWeek == dayOfWeek && s.timeSlot == timeLabel).firstOrNull;

    if (match == null) {
      return Container(
        margin: const EdgeInsets.all(3),
        decoration: BoxDecoration(
          color: const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: const Color(0xFFF1F5F9), width: 1),
        ),
      );
    }

    final color = _disciplinaColor(match.disciplinaId);

    return GestureDetector(
      onTap: () => _showCellMenu(context, match),
      child: Container(
        margin: const EdgeInsets.all(3),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
        decoration: BoxDecoration(
          color: color.withOpacity(0.12),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.4), width: 1.2),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              match.disciplinaName,
              style: TextStyle(
                color: color,
                fontSize: 10,
                fontWeight: FontWeight.bold,
                fontFamily: 'Poppins',
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 2),
            Text(
              match.turmaName,
              style: TextStyle(
                color: color.withOpacity(0.75),
                fontSize: 9,
                fontFamily: 'Poppins',
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            Text(
              match.salaName,
              style: const TextStyle(
                color: Color(0xFF94A3B8),
                fontSize: 9,
                fontFamily: 'Poppins',
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _showCellMenu(BuildContext context, HorarioSlot slot) async {
    final renderBox = context.findRenderObject() as RenderBox?;
    final position = renderBox != null
        ? RelativeRect.fromRect(
            renderBox.localToGlobal(Offset.zero) & renderBox.size,
            Offset.zero & MediaQuery.of(context).size,
          )
        : RelativeRect.fromLTRB(100, 200, 100, 100);

    final action = await showMenu<String>(
      context: context,
      position: position,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      items: [
        const PopupMenuItem(
          value: 'trocar',
          child: Row(
            children: [
              Icon(Icons.swap_horiz_outlined, size: 16, color: AppColors.blackBlue),
              SizedBox(width: 10),
              Text('Trocar Disciplina', style: TextStyle(fontFamily: 'Poppins', fontSize: 13)),
            ],
          ),
        ),
      ],
    );

    if (action == 'trocar') {
      await onTrocarDisciplina(slot);
    }
  }
}

class _DocenteLegenda extends StatelessWidget {
  const _DocenteLegenda({required this.slots});

  final List<HorarioSlot> slots;

  Widget build(BuildContext context) {
    // Group by disciplinaId, accumulating set of turmas
    final Map<int, ({String disciplinaName, Set<String> turmas})> grouped = {};
    for (final slot in slots) {
      if (!grouped.containsKey(slot.disciplinaId)) {
        grouped[slot.disciplinaId] = (disciplinaName: slot.disciplinaName, turmas: <String>{});
      }
      grouped[slot.disciplinaId]!.turmas.add(slot.turmaName);
    }

    return Container(
      decoration: const BoxDecoration(
        color: Color(0xFFF8FAFC),
        border: Border(top: BorderSide(color: Color(0xFFF1F5F9), width: 1)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'DISCIPLINAS LECCIONADAS',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: Color(0xFF94A3B8),
              letterSpacing: 1,
              fontFamily: 'Poppins',
            ),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: grouped.entries.map((entry) {
              final color = _disciplinaColor(entry.key);
              final disciplinaName = entry.value.disciplinaName;
              final turmas = entry.value.turmas.toList()..sort();

              return Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: color.withOpacity(0.3), width: 1),
                  boxShadow: const [
                    BoxShadow(color: Color(0x08000000), blurRadius: 4, offset: Offset(0, 2)),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 10,
                          height: 10,
                          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          disciplinaName,
                          style: TextStyle(fontSize: 12, color: AppColors.blackBlue, fontWeight: FontWeight.w600, fontFamily: 'Poppins'),
                        ),
                      ],
                    ),
                    if (turmas.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        children: turmas.map((t) => Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: color.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            t,
                            style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.w500, fontFamily: 'Poppins'),
                          ),
                        )).toList(),
                      ),
                    ],
                  ],
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}
