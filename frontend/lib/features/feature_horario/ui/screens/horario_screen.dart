import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_slot.dart';
import 'package:ghorario/features/feature_horario/presentation/controller/horario_controller.dart';
import 'package:ghorario/features/feature_horario/presentation/provider/horario_provider.dart';
import 'package:ghorario/features/feature_horario/presentation/states/horario_state.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/turmas_provider.dart';

const List<String> _weekdayLabels = [
  'Segunda-feira',
  'Terça-feira',
  'Quarta-feira',
  'Quinta-feira',
  'Sexta-feira',
];

/// Screen for displaying and generating academic timetables (horários),
/// backed by the real solver output — RF09-RF12.
class HorarioScreen extends StatefulWidget {
  const HorarioScreen({super.key});

  @override
  State<HorarioScreen> createState() => _HorarioScreenState();
}

class _HorarioScreenState extends State<HorarioScreen> {
  late final HorarioController _controller;
  String? _selectedTurmaId;
  late int _anoLetivo = DateTime.now().year;
  String _semestre = '1';

  @override
  void initState() {
    super.initState();
    _controller = HorarioController(provider: context.read<HorarioProvider>());
    final turmasProvider = context.read<TurmasProvider>();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (turmasProvider.turmas.isEmpty) {
        await turmasProvider.loadTurmas();
      }
      if (!mounted) return;
      if (turmasProvider.turmas.isNotEmpty) {
        setState(() => _selectedTurmaId = turmasProvider.turmas.first.id);
        _controller.fetchTimetableByTurma(_selectedTurmaId!);
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onTurmaSelected(String turmaId) {
    setState(() => _selectedTurmaId = turmaId);
    _controller.fetchTimetableByTurma(turmaId);
  }

  @override
  Widget build(BuildContext context) {
    final turmas = context.watch<TurmasProvider>().turmas;

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: ValueListenableBuilder<HorarioState>(
        valueListenable: _controller,
        builder: (BuildContext context, HorarioState state, Widget? child) {
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Row
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Horários',
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            color: AppColors.blackBlue,
                            fontFamily: 'Poppins',
                          ),
                        ),
                        SizedBox(height: 4),
                        Text(
                          'Grade de horários gerada pelo motor de otimização',
                          style: TextStyle(
                            fontSize: 14,
                            color: AppColors.textSecondary,
                            fontFamily: 'Poppins',
                          ),
                        ),
                      ],
                    ),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        _AnoLetivoESemestreSeletor(
                          anoLetivo: _anoLetivo,
                          semestre: _semestre,
                          enabled: !state.isGenerating,
                          onAnoLetivoChanged: (value) => setState(() => _anoLetivo = value),
                          onSemestreChanged: (value) => setState(() => _semestre = value),
                        ),
                        const SizedBox(width: 16),
                        ElevatedButton.icon(
                          onPressed: (state.isGenerating || _selectedTurmaId == null)
                              ? null
                              : () => _controller.generateTimetable(
                                    _selectedTurmaId!,
                                    anoLetivo: _anoLetivo,
                                    semestre: _semestre,
                                  ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.blackBlue,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                            elevation: 0,
                          ),
                          icon: state.isGenerating
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: Colors.white,
                                  ),
                                )
                              : const Icon(Icons.flash_on, size: 16),
                          label: Text(
                            state.isGenerating ? 'A gerar...' : 'Gerar Horário',
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              fontFamily: 'Poppins',
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                // Main timetabling card container
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
                        // Filter and Header toolbar
                        Padding(
                          padding: const EdgeInsets.all(24),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: const Color(0xFFE2E8F0), width: 1.2),
                                ),
                                child: turmas.isEmpty
                                    ? const Text(
                                        'Nenhuma turma encontrada',
                                        style: TextStyle(fontSize: 13, color: AppColors.textSecondary, fontFamily: 'Poppins'),
                                      )
                                    : DropdownButtonHideUnderline(
                                        child: DropdownButton<String>(
                                          value: _selectedTurmaId,
                                          icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF64748B)),
                                          style: const TextStyle(
                                            fontSize: 14,
                                            fontWeight: FontWeight.bold,
                                            color: AppColors.blackBlue,
                                            fontFamily: 'Poppins',
                                          ),
                                          items: turmas
                                              .map((Turma t) => DropdownMenuItem(
                                                    value: t.id,
                                                    child: Text('Turma: ${t.code ?? t.name}'),
                                                  ))
                                              .toList(),
                                          onChanged: (value) {
                                            if (value != null) _onTurmaSelected(value);
                                          },
                                        ),
                                      ),
                              ),
                              Row(
                                children: [
                                  Container(
                                    width: 12,
                                    height: 12,
                                    decoration: BoxDecoration(
                                      color: AppColors.blackBlue,
                                      borderRadius: BorderRadius.circular(3),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  const Text(
                                    'Aula Reservada',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Color(0xFF64748B),
                                      fontFamily: 'Poppins',
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.only(left: 24, right: 24, bottom: 8),
                          child: Row(
                            children: [
                              const SizedBox(width: 100),
                              for (final day in _weekdayLabels)
                                Expanded(
                                  child: Container(
                                    alignment: Alignment.center,
                                    padding: const EdgeInsets.symmetric(vertical: 8),
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
                        ),
                        const Divider(color: Color(0xFFF1F5F9), height: 1, thickness: 1),
                        Expanded(
                          child: (state.isGenerating || state.isLoading)
                              ? const Center(child: CircularProgressIndicator(color: AppColors.blackBlue))
                              : state.errorMessage != null
                                  ? Center(
                                      child: Padding(
                                        padding: const EdgeInsets.all(24),
                                        child: Text(
                                          state.errorMessage!,
                                          textAlign: TextAlign.center,
                                          style: const TextStyle(color: Colors.red, fontFamily: 'Poppins'),
                                        ),
                                      ),
                                    )
                                  : state.slots.isEmpty
                                      ? const Center(
                                          child: Text(
                                            'Sem horário gerado para esta turma ainda.',
                                            style: TextStyle(color: AppColors.textSecondary, fontFamily: 'Poppins'),
                                          ),
                                        )
                                      : _HorarioGrid(slots: state.slots),
                        ),
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

/// Lets the Gestor pick the (ano_letivo, semestre) scope for RF09 — a
/// geração é sempre o horário completo de todas as turmas desse par, de
/// uma vez (nunca todos os anos/semestres misturados).
class _AnoLetivoESemestreSeletor extends StatelessWidget {
  const _AnoLetivoESemestreSeletor({
    required this.anoLetivo,
    required this.semestre,
    required this.enabled,
    required this.onAnoLetivoChanged,
    required this.onSemestreChanged,
  });

  final int anoLetivo;
  final String semestre;
  final bool enabled;
  final ValueChanged<int> onAnoLetivoChanged;
  final ValueChanged<String> onSemestreChanged;

  @override
  Widget build(BuildContext context) {
    final anoAtual = DateTime.now().year;
    final anos = [for (var a = anoAtual - 1; a <= anoAtual + 1; a++) a];

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _SeletorContainer(
          child: DropdownButtonHideUnderline(
            child: DropdownButton<int>(
              value: anoLetivo,
              icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF64748B)),
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppColors.blackBlue,
                fontFamily: 'Poppins',
              ),
              items: anos
                  .map((ano) => DropdownMenuItem(value: ano, child: Text('Ano lectivo: $ano')))
                  .toList(),
              onChanged: enabled ? (value) => value != null ? onAnoLetivoChanged(value) : null : null,
            ),
          ),
        ),
        const SizedBox(width: 8),
        _SeletorContainer(
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: semestre,
              icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF64748B)),
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppColors.blackBlue,
                fontFamily: 'Poppins',
              ),
              items: const [
                DropdownMenuItem(value: '1', child: Text('1º Semestre')),
                DropdownMenuItem(value: '2', child: Text('2º Semestre')),
              ],
              onChanged: enabled ? (value) => value != null ? onSemestreChanged(value) : null : null,
            ),
          ),
        ),
      ],
    );
  }
}

class _SeletorContainer extends StatelessWidget {
  const _SeletorContainer({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE2E8F0), width: 1.2),
      ),
      child: child,
    );
  }
}

/// Renders the real solver output grouped by weekday x time slot — replaces
/// the previous hardcoded mock grid entirely.
class _HorarioGrid extends StatelessWidget {
  const _HorarioGrid({required this.slots});

  final List<HorarioSlot> slots;

  @override
  Widget build(BuildContext context) {
    final timeSlots = slots.map((s) => s.timeSlot).toSet().toList()..sort();

    return ListView.separated(
      padding: const EdgeInsets.symmetric(vertical: 16),
      itemCount: timeSlots.length,
      separatorBuilder: (context, index) => const SizedBox(height: 12),
      itemBuilder: (context, rowIndex) {
        final timeLabel = timeSlots[rowIndex];
        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: SizedBox(
            height: 100,
            child: Row(
              children: [
                SizedBox(
                  width: 100,
                  child: Text(
                    timeLabel,
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: Color(0xFF64748B), fontFamily: 'Poppins'),
                  ),
                ),
                for (int dayOfWeek = 1; dayOfWeek <= 5; dayOfWeek++)
                  Expanded(child: _buildCell(dayOfWeek, timeLabel)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildCell(int dayOfWeek, String timeLabel) {
    final matches = slots.where((s) => s.dayOfWeek == dayOfWeek && s.timeSlot == timeLabel);
    if (matches.isEmpty) {
      return Container(
        margin: const EdgeInsets.all(4),
        decoration: BoxDecoration(
          color: const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: const Color(0xFFF1F5F9), width: 1),
        ),
      );
    }
    final slot = matches.first;
    return Container(
      margin: const EdgeInsets.all(4),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.blackBlue,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            slot.disciplinaName,
            style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold, fontFamily: 'Poppins'),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          Text(
            slot.docenteName,
            style: const TextStyle(color: Color(0xFFCBD5E1), fontSize: 10, fontFamily: 'Poppins'),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 2),
          Text(
            slot.salaName,
            style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 10, fontWeight: FontWeight.w600, fontFamily: 'Poppins'),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
