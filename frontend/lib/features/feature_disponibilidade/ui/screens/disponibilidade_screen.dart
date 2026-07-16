import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:ghorario/core/enums/dia_semana.dart';
import 'package:ghorario/core/enums/turno.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/features/feature_auth/presentation/provider/auth_provider.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo_chave.dart';
import 'package:ghorario/features/feature_disponibilidade/presentation/controller/disponibilidade_controller.dart';
import 'package:ghorario/features/feature_disponibilidade/presentation/provider/disponibilidade_provider.dart';
import 'package:ghorario/features/feature_disponibilidade/presentation/states/disponibilidade_state.dart';
import 'package:ghorario/features/feature_docentes/domain/entities/docente.dart';
import 'package:ghorario/features/feature_docentes/presentation/controller/docentes_controller.dart';
import 'package:ghorario/features/feature_docentes/presentation/provider/docentes_provider.dart';
import 'package:ghorario/features/feature_docentes/presentation/states/docentes_state.dart';

/// Screen for the professor's weekly availability grid (RF05/UC05).
///
/// A Professor manages only their own grid; Gestor/Superadmin pick any
/// professor first (RN11). Rendered as one mini-grid per turno (manhã/tarde/
/// noite) because `periodo` restarts at 1 in each turno — there is no single
/// flat 1..9 axis anymore (no `Slot` table on the backend, see
/// backend/app/core/calendario.py).
class DisponibilidadeScreen extends StatefulWidget {
  const DisponibilidadeScreen({super.key});

  @override
  State<DisponibilidadeScreen> createState() => _DisponibilidadeScreenState();
}

class _DisponibilidadeScreenState extends State<DisponibilidadeScreen> {
  late final DisponibilidadeController _controller;
  DocentesController? _docentesController;
  int? _selectedProfessorId;

  @override
  void initState() {
    super.initState();
    _controller = DisponibilidadeController(provider: context.read<DisponibilidadeProvider>());

    final user = context.read<AuthProvider>().currentUser;
    if (user != null && user.isProfessor && user.professorId != null) {
      _selectedProfessorId = user.professorId;
      WidgetsBinding.instance.addPostFrameCallback((_) => _controller.init(_selectedProfessorId!));
    } else {
      _docentesController = DocentesController(provider: context.read<DocentesProvider>());
      WidgetsBinding.instance.addPostFrameCallback((_) => _docentesController!.init());
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _docentesController?.dispose();
    super.dispose();
  }

  void _onProfessorSelected(Docente docente) {
    final id = int.tryParse(docente.id);
    if (id == null) return;
    setState(() => _selectedProfessorId = id);
    _controller.load(id);
  }

  Widget _buildProfessorPicker() {
    return ValueListenableBuilder<DocentesState>(
      valueListenable: _docentesController!,
      builder: (context, state, child) {
        if (state.isLoading) return const Center(child: CircularProgressIndicator());
        if (state.docentes.isEmpty) {
          return const Text(
            'Nenhum professor registado.',
            style: TextStyle(color: AppColors.textSecondary, fontFamily: 'Poppins'),
          );
        }
        final selected = state.docentes.where((d) => d.id == _selectedProfessorId?.toString());
        return DropdownButtonFormField<Docente>(
          initialValue: selected.isEmpty ? null : selected.first,
          decoration: const InputDecoration(labelText: 'Professor', border: OutlineInputBorder()),
          items: state.docentes.map((d) => DropdownMenuItem(value: d, child: Text(d.name))).toList(),
          onChanged: (docente) {
            if (docente != null) _onProfessorSelected(docente);
          },
        );
      },
    );
  }

  Widget _buildGrid(DisponibilidadeState state) {
    if (state.isLoading) return const Center(child: CircularProgressIndicator());
    if (state.tempos.isEmpty) {
      return const Center(
        child: Text('Nenhum tempo letivo configurado.', style: TextStyle(color: AppColors.textSecondary)),
      );
    }

    final temposPorTurno = <Turno, List<Tempo>>{};
    for (final tempo in state.tempos) {
      (temposPorTurno[tempo.turno] ??= []).add(tempo);
    }

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final turno in Turno.values)
            if (temposPorTurno.containsKey(turno)) ...[
              Padding(
                padding: const EdgeInsets.only(top: 16, bottom: 8),
                child: Text(
                  turno.displayName,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontFamily: 'Poppins', fontSize: 16, color: AppColors.blackBlue),
                ),
              ),
              _buildTurnoTable(state, temposPorTurno[turno]!),
            ],
        ],
      ),
    );
  }

  Widget _buildTurnoTable(DisponibilidadeState state, List<Tempo> temposDoTurno) {
    final temposPorDia = <DiaSemana, List<Tempo>>{};
    for (final tempo in temposDoTurno) {
      (temposPorDia[tempo.diaSemana] ??= []).add(tempo);
    }
    for (final list in temposPorDia.values) {
      list.sort((a, b) => a.periodo.compareTo(b.periodo));
    }
    final periodos = (temposPorDia[DiaSemana.segunda] ?? const <Tempo>[]).map((t) => t.periodo).toList();

    return Table(
      border: TableBorder.all(color: const Color(0xFFF1F5F9)),
      columnWidths: const {0: FixedColumnWidth(120)},
      children: [
        TableRow(
          decoration: const BoxDecoration(color: Color(0xFFF8FAFC)),
          children: [
            const Padding(padding: EdgeInsets.all(8), child: SizedBox.shrink()),
            for (final dia in DiaSemana.values)
              Padding(
                padding: const EdgeInsets.all(8),
                child: Text(
                  dia.displayName,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontFamily: 'Poppins', fontSize: 12),
                ),
              ),
          ],
        ),
        for (final periodo in periodos)
          TableRow(
            children: [
              Padding(
                padding: const EdgeInsets.all(8),
                child: Text(
                  temposPorDia[DiaSemana.segunda]!.firstWhere((t) => t.periodo == periodo).horaInicio,
                  style: const TextStyle(fontFamily: 'Poppins', fontSize: 12),
                ),
              ),
              for (final dia in DiaSemana.values)
                Builder(builder: (context) {
                  final candidatos = (temposPorDia[dia] ?? const <Tempo>[]).where((t) => t.periodo == periodo);
                  if (candidatos.isEmpty) return const SizedBox.shrink();
                  final tempo = candidatos.first;
                  final chave = TempoChave(diaSemana: tempo.diaSemana, turno: tempo.turno, periodo: tempo.periodo);
                  final selected = state.selectedTempos.contains(chave);
                  return InkWell(
                    onTap: () => _controller.toggleTempo(chave),
                    child: Container(
                      margin: const EdgeInsets.all(4),
                      height: 40,
                      decoration: BoxDecoration(
                        color: selected ? AppColors.blackBlue : const Color(0xFFF8FAFC),
                        borderRadius: BorderRadius.circular(6),
                      ),
                    ),
                  );
                }),
            ],
          ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Disponibilidade',
                      style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: AppColors.blackBlue, fontFamily: 'Poppins'),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'Toque numa célula para marcar/desmarcar disponibilidade',
                      style: TextStyle(fontSize: 14, color: AppColors.textSecondary, fontFamily: 'Poppins'),
                    ),
                  ],
                ),
                if (_selectedProfessorId != null)
                  ValueListenableBuilder<DisponibilidadeState>(
                    valueListenable: _controller,
                    builder: (context, state, child) {
                      return ElevatedButton.icon(
                        onPressed: state.isSaving
                            ? null
                            : () async {
                                final messenger = ScaffoldMessenger.of(context);
                                final success = await _controller.save(_selectedProfessorId!);
                                messenger.showSnackBar(
                                  SnackBar(
                                    content: Text(success ? 'Disponibilidade guardada.' : (state.errorMessage ?? 'Erro ao guardar.')),
                                  ),
                                );
                              },
                        icon: state.isSaving
                            ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                            : const Icon(Icons.save, size: 18),
                        label: const Text('Guardar'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.blackBlue,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                        ),
                      );
                    },
                  ),
              ],
            ),
            const SizedBox(height: 24),
            if (_docentesController != null) ...[
              SizedBox(width: 320, child: _buildProfessorPicker()),
              const SizedBox(height: 24),
            ],
            Expanded(
              child: _selectedProfessorId == null
                  ? const Center(
                      child: Text('Selecione um professor.', style: TextStyle(color: AppColors.textSecondary)),
                    )
                  : ValueListenableBuilder<DisponibilidadeState>(
                      valueListenable: _controller,
                      builder: (context, state, child) => _buildGrid(state),
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
