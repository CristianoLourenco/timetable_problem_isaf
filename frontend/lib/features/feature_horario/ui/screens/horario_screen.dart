import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:ghorario/core/services/file_share_service.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/core/enums/turno.dart';
import 'package:ghorario/features/feature_disciplinas/presentation/provider/disciplinas_provider.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/usecase/get_all_tempos_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_slot.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_status.dart';
import 'package:ghorario/features/feature_horario/domain/entities/pendencia.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/criar_alocacao_manual_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_professores_qualificados_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_slots_vagos_usecase.dart';
import 'package:ghorario/features/feature_horario/presentation/controller/horario_controller.dart';
import 'package:ghorario/features/feature_horario/presentation/provider/horario_provider.dart';
import 'package:ghorario/features/feature_horario/presentation/states/horario_state.dart';
import 'package:ghorario/features/feature_horario/ui/components/alocacao_manual_dialog.dart';
import 'package:ghorario/features/feature_salas/presentation/provider/salas_provider.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma_detalhada.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/get_turmas_detalhadas_usecase.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/turmas_provider.dart';
import 'package:ghorario/features/feature_docentes/presentation/provider/docentes_provider.dart';
import 'package:ghorario/core/enums/dia_semana.dart';

const _fileShareService = FileShareService();

// ── Utility helpers ────────────────────────────────────────────────────────

String _jobStatusLabel(JobStatus? status) {
  switch (status) {
    case JobStatus.pending:
      return 'Na fila de espera';
    case JobStatus.running:
      return 'A resolver o horário';
    case JobStatus.done:
    case JobStatus.infeasible:
    case null:
      return 'A gerar';
  }
}

String _formatElapsed(int seconds) {
  final minutes = seconds ~/ 60;
  final secs = seconds % 60;
  return '${minutes.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
}

const List<String> _weekdayLabels = [
  'Segunda-feira',
  'Terça-feira',
  'Quarta-feira',
  'Quinta-feira',
  'Sexta-feira',
];

const List<String> _turnos = ['manha', 'tarde', 'noite'];
const Map<String, String> _turnoLabels = {'manha': 'Manhã', 'tarde': 'Tarde', 'noite': 'Noite'};

/// Derives a stable HSL color from a discipline ID integer.
Color _disciplinaColor(int disciplinaId) {
  const hues = [210.0, 280.0, 150.0, 30.0, 340.0, 60.0, 190.0, 320.0, 90.0, 0.0];
  return HSLColor.fromAHSL(1, hues[disciplinaId % hues.length], 0.65, 0.52).toColor();
}

// ── Screen widget ──────────────────────────────────────────────────────────

enum _FiltroTipo { turma, professor }

/// Timetable screen with:
/// - Funcionalidade 1: Solver progress indicator with elapsed time
/// - Funcionalidade 2: Pendências section with "Alocar manualmente" CTA
/// - Funcionalidade 3: Manual allocation dialog
/// - Funcionalidade 5: Professor/Turma toggle, shift tabs, legend
class HorarioScreen extends StatefulWidget {
  const HorarioScreen({super.key});

  @override
  State<HorarioScreen> createState() => _HorarioScreenState();
}

class _HorarioScreenState extends State<HorarioScreen> with SingleTickerProviderStateMixin {
  late final HorarioController _controller;
  late final TabController _tabController;

  _FiltroTipo _filtroTipo = _FiltroTipo.turma;
  String? _selectedTurmaId;
  String? _selectedProfessorId;
  late int _anoLetivo = DateTime.now().year;
  String _semestre = '1';

  // RF02 — turmas do dropdown, filtradas por _anoLetivo/_semestre (GET
  // /turmas-detalhadas), ao contrário de TurmasProvider.turmas (todas as
  // turmas, todos os anos/semestres — usado por outros ecrãs). Sem este
  // filtro, o dropdown mostrava turmas de âmbitos sem nenhum Job gerado,
  // parecendo "sem horário" um bug do solver (bug real, 2026-07-24).
  List<TurmaDetalhada> _turmasDoAmbito = const <TurmaDetalhada>[];

  // Grelha oficial de tempos (GET /slots) — independente das alocações já
  // feitas. Sem isto, a grade era derivada dos próprios `HorarioSlot`
  // preenchidos: uma turma/professor sem NENHUMA alocação ficava sem grade
  // nenhuma, impedindo o Gestor de clicar em qualquer célula para fazer a
  // alocação manual (bug real, 2026-07-19).
  List<Tempo> _todosTempos = const <Tempo>[];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _controller = HorarioController(provider: context.read<HorarioProvider>())..init();

    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (!mounted) return;
      final turmasProvider = context.read<TurmasProvider>();
      final docentesProvider = context.read<DocentesProvider>();
      final disciplinasProvider = context.read<DisciplinasProvider>();
      final salasProvider = context.read<SalasProvider>();
      final getAllTemposUseCase = context.read<GetAllTemposUseCase>();

      if (turmasProvider.turmas.isEmpty) await turmasProvider.loadTurmas();
      if (docentesProvider.docentes.isEmpty) await docentesProvider.loadDocentes();
      if (disciplinasProvider.disciplinas.isEmpty) await disciplinasProvider.loadDisciplinas();
      if (salasProvider.salas.isEmpty) await salasProvider.loadSalas();

      await _carregarTodosTempos(getAllTemposUseCase);

      if (!mounted) return;
      await _onAmbitoChanged();
    });
  }

  /// Recarrega o dropdown de turmas para o âmbito atual (_anoLetivo/_semestre)
  /// e resincroniza _selectedTurmaId: se a turma selecionada deixou de
  /// pertencer ao novo âmbito, repõe para a primeira da nova lista (ou null
  /// se vier vazia) — nunca deixar um id selecionado "fantasma" que já não
  /// existe no dropdown.
  Future<void> _carregarTurmasDoAmbito() async {
    final getTurmasDetalhadasUseCase = context.read<GetTurmasDetalhadasUseCase>();
    final result = await getTurmasDetalhadasUseCase(
      GetTurmasDetalhadasParams(anoLetivo: _anoLetivo, semestre: _semestre),
    );
    if (!mounted) return;

    final turmas = result.success ? (result.data ?? const <TurmaDetalhada>[]) : const <TurmaDetalhada>[];
    final aindaValida = _selectedTurmaId != null && turmas.any((t) => t.id == _selectedTurmaId);

    setState(() {
      _turmasDoAmbito = turmas;
      if (!aindaValida) {
        _selectedTurmaId = turmas.isNotEmpty ? turmas.first.id : null;
      }
    });
  }

  /// GET /slots alimenta a estrutura fixa da grade (linhas/colunas), independente
  /// de haver ou não alocações — sem isto a grade mostra sempre "Nenhum tempo
  /// letivo definido" mesmo com um horário real já gerado (ver _HorarioGrid).
  /// Bug real (2026-07-24): uma falha de rede/servidor transitória nesta única
  /// chamada, sem retry nem aviso nenhum, deixava _todosTempos vazio até a tela
  /// ser reaberta — indistinguível, para o Gestor, de "não há horário gerado".
  /// Tenta 3 vezes (backoff curto) antes de admitir falha e avisar visivelmente.
  Future<void> _carregarTodosTempos(GetAllTemposUseCase getAllTemposUseCase) async {
    for (var tentativa = 1; tentativa <= 3; tentativa++) {
      final temposResult = await getAllTemposUseCase(null);
      if (!mounted) return;
      if (temposResult.success && temposResult.data != null) {
        setState(() => _todosTempos = temposResult.data!);
        return;
      }
      if (tentativa < 3) {
        await Future<void>.delayed(Duration(milliseconds: 300 * tentativa));
      }
    }
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Não foi possível carregar a grelha de tempos letivos. Tente recarregar a página.'),
        backgroundColor: AppColors.error,
      ),
    );
  }

  /// RF09/RF10 — troca de filtro ano/semestre nunca deve reutilizar o
  /// horário/pendências do âmbito anterior: verifica primeiro se existe Job
  /// para o novo âmbito e só então decide buscar (existe) ou limpar (não
  /// existe) o horário da turma/professor atualmente selecionado. Bug real
  /// (2026-07-19): antes, fetchTimetableByTurma corria ANTES de checkScope
  /// terminar — checkScope então limpava (ou não repunha) `_slots` por cima
  /// do resultado que tinha acabado de chegar, fazendo a grelha nunca
  /// aparecer mesmo com um horário real já gerado.
  ///
  /// Bug real #2 (2026-07-24): `hasScopeJob` é `null` quando checkScope FALHOU
  /// (erro de rede/servidor, ex: 500 transitório) — distinto de `false`
  /// ("confirmado que não há Job para este âmbito"). `!= true` tratava os
  /// dois casos da mesma forma e limpava a grelha mesmo quando a falha foi
  /// só em verificar o âmbito, escondendo um horário real já carregado ou
  /// prestes a ser carregado. Só limpar quando `hasScopeJob == false`
  /// (confirmado ausente); em caso de falha (`null`), manter o que já
  /// estava visível e tentar buscar na mesma — fetchTimetableByTurma/Professor
  /// já tratam "sem Job" devolvendo vazio, sem precisar do resultado de
  /// checkScope para isso.
  Future<void> _onAmbitoChanged() async {
    // Resincroniza o dropdown de turmas ANTES de decidir o que buscar —
    // _selectedTurmaId pode mudar aqui (turma antiga fora do novo âmbito).
    await _carregarTurmasDoAmbito();
    if (!mounted) return;

    await _controller.checkScope(_anoLetivo, _semestre);
    if (!mounted) return;

    if (_controller.value.hasScopeJob == false) {
      _controller.clearSlots();
      return;
    }
    if (_filtroTipo == _FiltroTipo.turma && _selectedTurmaId != null) {
      await _controller.fetchTimetableByTurma(_selectedTurmaId!, anoLetivo: _anoLetivo, semestre: _semestre);
    } else if (_filtroTipo == _FiltroTipo.professor && _selectedProfessorId != null) {
      await _controller.fetchTimetableByProfessor(_selectedProfessorId!, anoLetivo: _anoLetivo, semestre: _semestre);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _tabController.dispose();
    super.dispose();
  }

  void _onTurmaSelected(String turmaId) {
    setState(() => _selectedTurmaId = turmaId);
    _controller.fetchTimetableByTurma(turmaId, anoLetivo: _anoLetivo, semestre: _semestre);
  }

  void _onProfessorSelected(String professorId) {
    setState(() => _selectedProfessorId = professorId);
    _controller.fetchTimetableByProfessor(professorId, anoLetivo: _anoLetivo, semestre: _semestre);
  }

  Future<void> _openAlocacaoDialog({
    int? preencherTurmaId,
    int? preencherDisciplinaId,
    String? preencherDiaSemana,
    int? preencherPeriodo,
    String? preencherTurno,
  }) async {
    final horarioProvider = context.read<HorarioProvider>();
    final turmas = context.read<TurmasProvider>().turmas;
    final disciplinas = context.read<DisciplinasProvider>().disciplinas;
    final salas = context.read<SalasProvider>().salas;

    // Alocação manual exige um Job já existente (Alocacao.job_id é FK — ver
    // app/services/alocacao_manual_service.py) — sem nenhum horário gerado
    // ainda para este âmbito, não há a quem associar a alocação.
    final jobId = horarioProvider.currentJobId ?? horarioProvider.scopeJobId;
    if (jobId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Gere o horário deste âmbito primeiro (mesmo que incompleto) para poder alocar manualmente.'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    final turmaIdStr = preencherTurmaId != null ? preencherTurmaId.toString() : _selectedTurmaId;

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
        preencherTurmaId: turmaIdStr,
        preencherDisciplinaId: preencherDisciplinaId,
        preencherDiaSemana: preencherDiaSemana,
        preencherPeriodo: preencherPeriodo,
        preencherTurno: preencherTurno,
        jobId: jobId,
      ),
    );

    if (result == true && mounted) {
      if (_filtroTipo == _FiltroTipo.turma && _selectedTurmaId != null) {
        _controller.fetchTimetableByTurma(_selectedTurmaId!, anoLetivo: _anoLetivo, semestre: _semestre);
      } else if (_filtroTipo == _FiltroTipo.professor && _selectedProfessorId != null) {
        _controller.fetchTimetableByProfessor(_selectedProfessorId!, anoLetivo: _anoLetivo, semestre: _semestre);
      }
      await horarioProvider.loadPendencias(jobId);
    }
  }

  Future<void> _moverAlocacao(HorarioSlot slot, int day, int periodo) async {
    if (slot.alocacaoId == null) return;
    final diaSemana = DiaSemana.values[day - 1].apiValue;

    final success = await _controller.moverAlocacao(slot.alocacaoId!, diaSemana, periodo);
    if (!mounted) return;

    if (success) {
      // O provider não reescreve `slots` sozinho após mover (o HorarioSlot
      // movido continuaria com o dia/período antigos em memória) — sem isto
      // o drag-and-drop parecia "não fazer nada" mesmo com o PATCH a ter
      // sucesso no backend (bug real, 2026-07-19).
      if (_filtroTipo == _FiltroTipo.turma && _selectedTurmaId != null) {
        await _controller.fetchTimetableByTurma(_selectedTurmaId!, anoLetivo: _anoLetivo, semestre: _semestre);
      } else if (_filtroTipo == _FiltroTipo.professor && _selectedProfessorId != null) {
        await _controller.fetchTimetableByProfessor(_selectedProfessorId!, anoLetivo: _anoLetivo, semestre: _semestre);
      }
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Alocação movida com sucesso!'), backgroundColor: AppColors.success),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(_controller.value.alocacaoError ?? 'Erro ao mover alocação.'), backgroundColor: AppColors.error),
      );
    }
  }

  void _onEmptyCellTap(int day, int periodo, String timeLabel, String turno) {
    final diaSemana = DiaSemana.values[day - 1].apiValue;
    _openAlocacaoDialog(
      preencherDiaSemana: diaSemana,
      preencherPeriodo: periodo,
      preencherTurno: turno,
    );
  }

  /// Botão "Limpar Horário" (RF09) — ação destrutiva (apaga o Job do âmbito
  /// selecionado e todas as suas Alocacao/Pendencia), por isso pede
  /// confirmação antes de chamar o provider.
  ///
  /// Bug real (2026-07-24): o botão só ficava ativo com hasScopeJob == true —
  /// uma falha transitória em checkScope (hasScopeJob == null) desativava o
  /// botão sem nenhum aviso, parecendo simplesmente avariado. Agora o botão
  /// fica ativo também quando a verificação falhou (null), e tenta
  /// re-verificar o âmbito aqui antes de desistir.
  Future<void> _confirmarLimparHorario() async {
    if (_controller.value.hasScopeJob != true) {
      await _controller.checkScope(_anoLetivo, _semestre);
      if (!mounted) return;
      if (_controller.value.hasScopeJob != true) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Não foi possível confirmar o horário deste âmbito. Tente novamente.'),
            backgroundColor: AppColors.error,
          ),
        );
        return;
      }
    }

    final confirmar = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Limpar horário?'),
        content: Text(
          'Isto apaga permanentemente o horário gerado para o Ano Letivo $_anoLetivo, '
          '$_semestreº Semestre, incluindo todas as alocações e pendências. Esta ação não '
          'pode ser desfeita.',
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Cancelar')),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Limpar', style: TextStyle(color: AppColors.error)),
          ),
        ],
      ),
    );
    if (confirmar != true || !mounted) return;

    final sucesso = await _controller.limparHorarioDoAmbito(_anoLetivo, _semestre);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(sucesso ? 'Horário limpo com sucesso.' : 'Erro ao limpar o horário.'),
        backgroundColor: sucesso ? AppColors.success : AppColors.error,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final docentes = context.watch<DocentesProvider>().docentes;

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
                // ── Header Row ──────────────────────────────────────────
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
                          style: TextStyle(fontSize: 14, color: AppColors.textSecondary, fontFamily: 'Poppins'),
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
                          onAnoLetivoChanged: (v) {
                            setState(() => _anoLetivo = v);
                            _onAmbitoChanged();
                          },
                          onSemestreChanged: (v) {
                            setState(() => _semestre = v);
                            _onAmbitoChanged();
                          },
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
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                            elevation: 0,
                          ),
                          icon: state.isGenerating
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                )
                              : const Icon(Icons.flash_on, size: 16),
                          label: Text(
                            state.isGenerating
                                ? '${_jobStatusLabel(state.jobStatus)}... ${_formatElapsed(state.elapsedSeconds)}'
                                : 'Gerar Horário',
                            style: const TextStyle(fontWeight: FontWeight.w600, fontFamily: 'Poppins'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        OutlinedButton.icon(
                          onPressed: (state.isGenerating || state.hasScopeJob == false)
                              ? null
                              : _confirmarLimparHorario,
                          style: OutlinedButton.styleFrom(
                            backgroundColor: Colors.white,
                            side: const BorderSide(color: Color(0xFFE2E8F0), width: 1.2),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                          ),
                          icon: const Icon(Icons.delete_outline, size: 16, color: AppColors.error),
                          label: const Text(
                            'Limpar Horário',
                            style: TextStyle(color: AppColors.error, fontWeight: FontWeight.w600, fontFamily: 'Poppins'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        OutlinedButton.icon(
                          onPressed: (state.isExporting || state.currentJobId == null)
                              ? null
                              : () => _controller.exportarTodosHorarios(_fileShareService),
                          style: OutlinedButton.styleFrom(
                            backgroundColor: Colors.white,
                            side: const BorderSide(color: Color(0xFFE2E8F0), width: 1.2),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                          ),
                          icon: state.isExporting
                              ? const SizedBox(
                                  width: 14,
                                  height: 14,
                                  child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.blackBlue),
                                )
                              : const Icon(Icons.folder_zip_outlined, size: 16, color: AppColors.blackBlue),
                          label: const Text(
                            'Exportar Todos',
                            style: TextStyle(color: AppColors.blackBlue, fontWeight: FontWeight.w600, fontFamily: 'Poppins'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton.icon(
                          onPressed: () => _openAlocacaoDialog(),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF10B981),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                            elevation: 0,
                          ),
                          icon: const Icon(Icons.edit_calendar_outlined, size: 16),
                          label: const Text(
                            'Alocar Manualmente',
                            style: TextStyle(fontWeight: FontWeight.w600, fontFamily: 'Poppins'),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                if (state.exportError != null) ...[
                  const SizedBox(height: 8),
                  Text(state.exportError!, style: const TextStyle(color: AppColors.error, fontSize: 12, fontFamily: 'Poppins')),
                ],
                // ── Pendências ──────────────────────────────────────────
                if (state.pendencias.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  _PendenciasSection(
                    pendencias: state.pendencias,
                    onAlocarManualmente: (p) => _openAlocacaoDialog(
                      preencherTurmaId: p.turmaId,
                      preencherDisciplinaId: p.disciplinaId,
                    ),
                  ),
                ],
                const SizedBox(height: 24),
                // ── Main timetable card ─────────────────────────────────
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
                        // ── Filter toolbar ──────────────────────────────
                        Padding(
                          padding: const EdgeInsets.all(20),
                          child: Row(
                            children: [
                              // Toggle Professor / Turma
                              _FiltroToggle(
                                value: _filtroTipo,
                                onChanged: (v) {
                                  setState(() {
                                    _filtroTipo = v;
                                    if (v == _FiltroTipo.turma && _selectedTurmaId != null) {
                                      _controller.fetchTimetableByTurma(_selectedTurmaId!, anoLetivo: _anoLetivo, semestre: _semestre);
                                    } else if (v == _FiltroTipo.professor && _selectedProfessorId != null) {
                                      _controller.fetchTimetableByProfessor(_selectedProfessorId!, anoLetivo: _anoLetivo, semestre: _semestre);
                                    }
                                  });
                                },
                              ),
                              const SizedBox(width: 16),
                              // Entity selector
                              _filtroTipo == _FiltroTipo.turma
                                  ? _EntityDropdown<TurmaDetalhada>(
                                      items: _turmasDoAmbito,
                                      value: _turmasDoAmbito.where((t) => t.id == _selectedTurmaId).firstOrNull,
                                      itemLabel: (t) => t.code ?? t.name,
                                      hint: 'Selecione Turma',
                                      onChanged: (t) {
                                        if (t != null) _onTurmaSelected(t.id);
                                      },
                                    )
                                  : _EntityDropdown(
                                      items: docentes,
                                      value: docentes.where((d) => d.id == _selectedProfessorId).firstOrNull,
                                      itemLabel: (d) => d.name,
                                      hint: 'Selecione Professor',
                                      onChanged: (d) {
                                        if (d != null) _onProfessorSelected(d.id);
                                      },
                                    ),
                              const Spacer(),
                              // Export this entity
                              if (_filtroTipo == _FiltroTipo.turma && _selectedTurmaId != null)
                                IconButton(
                                  tooltip: 'Exportar PDF desta turma',
                                  onPressed: (state.isExporting || state.slots.isEmpty)
                                      ? null
                                      : () => _controller.exportarHorarioTurmaPdf(_selectedTurmaId!, _fileShareService),
                                  icon: state.isExporting
                                      ? const SizedBox(
                                          width: 16,
                                          height: 16,
                                          child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.blackBlue),
                                        )
                                      : const Icon(Icons.picture_as_pdf_outlined, size: 18, color: AppColors.blackBlue),
                                ),
                            ],
                          ),
                        ),
                        const Divider(height: 1, color: Color(0xFFF1F5F9)),
                        // ── Content area ────────────────────────────────
                        Expanded(
                          child: state.isGenerating
                              ? _GeracaoEmProgresso(
                                  status: state.jobStatus,
                                  elapsedSeconds: state.elapsedSeconds,
                                  tempoMaximoMinutos: state.tempoMaximoMinutos,
                                )
                              : state.isLoading || state.isCheckingScope
                                  ? const Center(child: CircularProgressIndicator(color: AppColors.blackBlue))
                                  : state.errorMessage != null
                                      ? _ErrorView(message: state.errorMessage!)
                                      // A grelha aparece SEMPRE (mesmo sem nenhuma alocação
                                      // ainda) — desenhada a partir de _todosTempos (grelha
                                      // oficial, GET /slots), não a partir de state.slots
                                      // (que ficaria vazio para uma turma/professor sem
                                      // nenhum horário gerado, impedindo a alocação manual).
                                      : _filtroTipo == _FiltroTipo.turma
                                          ? _TurmaView(
                                              slots: state.slots,
                                              todosTempos: _todosTempos,
                                              turno: _turmasDoAmbito.where((t) => t.id == _selectedTurmaId).firstOrNull?.turma.period,
                                              onMoveAlocacao: _moverAlocacao,
                                              onEmptyCellTap: _onEmptyCellTap,
                                            )
                                          : _ProfessorView(
                                              slots: state.slots,
                                              todosTempos: _todosTempos,
                                              tabController: _tabController,
                                              onMoveAlocacao: _moverAlocacao,
                                              onEmptyCellTap: _onEmptyCellTap,
                                            ),
                        ),
                        // ── Legend ──────────────────────────────────────
                        if (!state.isLoading && !state.isGenerating && !state.isCheckingScope && state.slots.isNotEmpty)
                          _Legenda(slots: state.slots),
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

// ── Pendências section (Funcionalidade 2) ──────────────────────────────────

class _PendenciasSection extends StatefulWidget {
  const _PendenciasSection({required this.pendencias, required this.onAlocarManualmente});

  final List<Pendencia> pendencias;
  final void Function(Pendencia) onAlocarManualmente;

  @override
  State<_PendenciasSection> createState() => _PendenciasSectionState();
}

class _PendenciasSectionState extends State<_PendenciasSection> {
  bool _expanded = true;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFFFFBEB),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFFDE68A), width: 1.2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          InkWell(
            onTap: () => setState(() => _expanded = !_expanded),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber_rounded, color: Color(0xFFD97706), size: 18),
                  const SizedBox(width: 10),
                  Text(
                    '${widget.pendencias.length} turma${widget.pendencias.length == 1 ? '' : 's'}/disciplina${widget.pendencias.length == 1 ? '' : 's'} por distribuir',
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF92400E),
                      fontFamily: 'Poppins',
                    ),
                  ),
                  const Spacer(),
                  Icon(
                    _expanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                    color: const Color(0xFFD97706),
                    size: 18,
                  ),
                ],
              ),
            ),
          ),
          if (_expanded) ...[
            const Divider(height: 1, color: Color(0xFFFDE68A)),
            SizedBox(
              height: 144,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
                itemCount: widget.pendencias.length,
                itemBuilder: (context, index) {
                  final p = widget.pendencias[index];
                  return _PendenciaCard(
                    pendencia: p,
                    onAlocarManualmente: () => widget.onAlocarManualmente(p),
                  );
                },
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _PendenciaCard extends StatelessWidget {
  const _PendenciaCard({required this.pendencia, required this.onAlocarManualmente});

  final Pendencia pendencia;
  final VoidCallback onAlocarManualmente;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 220,
      margin: const EdgeInsets.only(right: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFFDE68A), width: 1),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8, offset: const Offset(0, 2)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            pendencia.razao,
            style: const TextStyle(fontSize: 11, color: Color(0xFF92400E), fontFamily: 'Poppins'),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const Spacer(),
          Text(
            '${pendencia.temposEmFalta} período${pendencia.temposEmFalta == 1 ? '' : 's'} em falta',
            style: const TextStyle(fontSize: 10, color: Color(0xFFD97706), fontFamily: 'Poppins', fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 6),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: onAlocarManualmente,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFD97706),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                padding: const EdgeInsets.symmetric(vertical: 7),
                elevation: 0,
              ),
              child: const Text('Alocar manualmente', style: TextStyle(fontSize: 11, fontFamily: 'Poppins', fontWeight: FontWeight.w600)),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Grid views ─────────────────────────────────────────────────────────────

/// Turma view — no tabs, shows grid for the turma's single shift (Funcionalidade 5)
class _TurmaView extends StatelessWidget {
  const _TurmaView({
    required this.slots,
    required this.todosTempos,
    required this.turno,
    required this.onMoveAlocacao,
    required this.onEmptyCellTap,
  });

  final List<HorarioSlot> slots;
  final List<Tempo> todosTempos;
  final Turno? turno;
  final void Function(HorarioSlot slot, int dayOfWeek, int periodo) onMoveAlocacao;
  final void Function(int dayOfWeek, int periodo, String timeLabel, String turno) onEmptyCellTap;

  @override
  Widget build(BuildContext context) {
    if (turno == null) {
      return const Center(
        child: Text('Selecione uma turma.', style: TextStyle(color: AppColors.textSecondary, fontFamily: 'Poppins')),
      );
    }
    return _HorarioGrid(
      slots: slots,
      tempos: todosTempos.where((t) => t.turno == turno).toList(),
      onMoveAlocacao: onMoveAlocacao,
      onEmptyCellTap: onEmptyCellTap,
    );
  }
}

/// Professor view — tabs by shift (Funcionalidade 5)
class _ProfessorView extends StatelessWidget {
  const _ProfessorView({
    required this.slots,
    required this.todosTempos,
    required this.tabController,
    required this.onMoveAlocacao,
    required this.onEmptyCellTap,
  });

  final List<HorarioSlot> slots;
  final List<Tempo> todosTempos;
  final TabController tabController;
  final void Function(HorarioSlot slot, int dayOfWeek, int periodo) onMoveAlocacao;
  final void Function(int dayOfWeek, int periodo, String timeLabel, String turno) onEmptyCellTap;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          color: const Color(0xFFF8FAFC),
          child: TabBar(
            controller: tabController,
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
          child: TabBarView(
            controller: tabController,
            children: _turnos
                .map((turno) => _HorarioGrid(
                      slots: slots.where((s) => s.turno == turno).toList(),
                      tempos: todosTempos.where((t) => t.turno.apiValue == turno).toList(),
                      onMoveAlocacao: onMoveAlocacao,
                      onEmptyCellTap: onEmptyCellTap,
                    ))
                .toList(),
          ),
        ),
      ],
    );
  }
}

class _HorarioGrid extends StatelessWidget {
  const _HorarioGrid({
    required this.slots,
    required this.tempos,
    required this.onMoveAlocacao,
    required this.onEmptyCellTap,
  });

  final List<HorarioSlot> slots;
  // Grelha oficial de tempos deste turno (GET /slots) — fonte da estrutura
  // da grade (linhas/colunas), independente de haver ou não alocações.
  final List<Tempo> tempos;
  final void Function(HorarioSlot slot, int dayOfWeek, int periodo) onMoveAlocacao;
  final void Function(int dayOfWeek, int periodo, String timeLabel, String turno) onEmptyCellTap;

  @override
  Widget build(BuildContext context) {
    if (tempos.isEmpty) {
      return const Center(
        child: Text('Nenhum tempo letivo definido para este turno.', style: TextStyle(color: AppColors.textSecondary, fontFamily: 'Poppins')),
      );
    }

    // (periodo, timeLabel) únicos, ordenados por periodo — cada linha da
    // grade é um período do turno (não depende de haver alocação nele).
    final periodosOrdenados = tempos.map((t) => t.periodo).toSet().toList()..sort();
    final timeLabelPorPeriodo = <int, String>{
      for (final t in tempos) t.periodo: '${t.horaInicio}-${t.horaFim}',
    };
    final turnoApiValue = tempos.first.turno.apiValue;

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Column(
        children: [
          // Day header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Row(
              children: [
                const SizedBox(width: 100),
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
          ),
          const SizedBox(height: 8),
          for (final periodo in periodosOrdenados) ...[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: SizedBox(
                height: 90,
                child: Row(
                  children: [
                    SizedBox(
                      width: 100,
                      child: Text(
                        timeLabelPorPeriodo[periodo] ?? '',
                        style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8), fontFamily: 'Poppins'),
                      ),
                    ),
                    for (int day = 1; day <= 5; day++)
                      Expanded(
                        child: _GridCell(
                          dayOfWeek: day,
                          periodo: periodo,
                          timeLabel: timeLabelPorPeriodo[periodo] ?? '',
                          turno: turnoApiValue,
                          slots: slots,
                          onMoveAlocacao: onMoveAlocacao,
                          onEmptyCellTap: onEmptyCellTap,
                        ),
                      ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),
          ],
        ],
      ),
    );
  }
}

class _GridCell extends StatelessWidget {
  const _GridCell({
    required this.dayOfWeek,
    required this.periodo,
    required this.timeLabel,
    required this.turno,
    required this.slots,
    required this.onMoveAlocacao,
    required this.onEmptyCellTap,
  });

  final int dayOfWeek;
  // Vem sempre da grelha oficial de tempos (Tempo.periodo, ver _HorarioGrid),
  // nunca derivado de `slots` — antes, uma célula vazia calculava o período
  // com `slots.firstWhere((s) => s.timeSlot == timeLabel).periodo`, que
  // lançava exceção sempre que não havia NENHUMA alocação nesse horário em
  // nenhum dia (turma/professor sem horário gerado — bug real, 2026-07-19).
  final int periodo;
  final String timeLabel;
  final String turno;
  final List<HorarioSlot> slots;
  final void Function(HorarioSlot slot, int dayOfWeek, int periodo) onMoveAlocacao;
  final void Function(int dayOfWeek, int periodo, String timeLabel, String turno) onEmptyCellTap;

  @override
  Widget build(BuildContext context) {
    final match = slots.where((s) => s.dayOfWeek == dayOfWeek && s.periodo == periodo).firstOrNull;

    if (match == null) {
      return DragTarget<HorarioSlot>(
        onWillAcceptWithDetails: (details) => true, // Valid because cell is empty
        onAcceptWithDetails: (details) {
          onMoveAlocacao(details.data, dayOfWeek, periodo);
        },
        builder: (context, candidateData, rejectedData) {
          final isHovering = candidateData.isNotEmpty;
          return InkWell(
            onTap: () => onEmptyCellTap(dayOfWeek, periodo, timeLabel, turno),
            child: Container(
              margin: const EdgeInsets.all(3),
              decoration: BoxDecoration(
                color: isHovering ? const Color(0xFFE2E8F0) : const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: isHovering ? AppColors.blackBlue : const Color(0xFFF1F5F9),
                  width: 1,
                ),
              ),
            ),
          );
        },
      );
    }

    final color = _disciplinaColor(match.disciplinaId);

    final cellContent = Container(
      margin: const EdgeInsets.all(3),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
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
            match.disciplinaNomeCurto.isNotEmpty ? match.disciplinaNomeCurto : match.disciplinaName,
            style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.bold, fontFamily: 'Poppins'),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 2),
          Text(
            match.docenteName,
            style: const TextStyle(color: Color(0xFF64748B), fontSize: 9, fontFamily: 'Poppins'),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          Text(
            '${match.turmaName} · ${match.salaName}',
            style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 9, fontFamily: 'Poppins'),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );

    final draggableCell = Draggable<HorarioSlot>(
      data: match,
      feedback: Material(
        color: Colors.transparent,
        child: Opacity(
          opacity: 0.9,
          child: SizedBox(
            width: 140, // approximate width
            height: 90,
            child: cellContent,
          ),
        ),
      ),
      childWhenDragging: Opacity(
        opacity: 0.4,
        child: cellContent,
      ),
      child: cellContent,
    );

    // Sem isto, arrastar uma alocação por cima de uma célula já ocupada não
    // dava nenhum feedback (nem cor, nem "Ocupado") — só a célula vazia tinha
    // DragTarget, então o Gestor largava aqui sem perceber porque nada
    // acontecia. Nunca aceita o drop (RN01-RN03 já bloqueariam no backend de
    // qualquer forma); só sinaliza visualmente que este slot não está livre.
    return DragTarget<HorarioSlot>(
      onWillAcceptWithDetails: (details) => details.data.alocacaoId != match.alocacaoId,
      builder: (context, candidateData, rejectedData) {
        if (candidateData.isNotEmpty) {
          return Container(
            margin: const EdgeInsets.all(3),
            decoration: BoxDecoration(
              color: const Color(0xFF64748B).withOpacity(0.35),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFF64748B), width: 1.2),
            ),
            alignment: Alignment.center,
            child: const Text(
              'Ocupado',
              style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold, fontFamily: 'Poppins'),
            ),
          );
        }
        return draggableCell;
      },
    );
  }
}

// ── Legend (Funcionalidade 5) ──────────────────────────────────────────────

class _Legenda extends StatelessWidget {
  const _Legenda({required this.slots});

  final List<HorarioSlot> slots;

  @override
  Widget build(BuildContext context) {
    // Grade mostra a sigla curta (mais espaço para nomes disciplina + docente
    // + turma na mesma célula) — legenda liga a sigla ao nome completo.
    final Map<int, String> disciplinaNames = {};
    for (final slot in slots) {
      final sigla = slot.disciplinaNomeCurto.isNotEmpty ? slot.disciplinaNomeCurto : slot.disciplinaName;
      disciplinaNames[slot.disciplinaId] =
          sigla == slot.disciplinaName ? slot.disciplinaName : '$sigla — ${slot.disciplinaName}';
    }

    return Container(
      decoration: const BoxDecoration(
        color: Color(0xFFF8FAFC),
        border: Border(top: BorderSide(color: Color(0xFFF1F5F9), width: 1)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      child: Row(
        children: [
          const Text(
            'LEGENDA:',
            style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8), letterSpacing: 1, fontFamily: 'Poppins'),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Wrap(
              spacing: 12,
              runSpacing: 6,
              children: disciplinaNames.entries.map((entry) {
                final color = _disciplinaColor(entry.key);
                return Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(width: 10, height: 10, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
                    const SizedBox(width: 6),
                    Text(
                      entry.value,
                      style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w600, fontFamily: 'Poppins'),
                    ),
                  ],
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Supporting widgets ─────────────────────────────────────────────────────

class _FiltroToggle extends StatelessWidget {
  const _FiltroToggle({required this.value, required this.onChanged});

  final _FiltroTipo value;
  final ValueChanged<_FiltroTipo> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFF1F5F9),
        borderRadius: BorderRadius.circular(8),
      ),
      padding: const EdgeInsets.all(3),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _ToggleOption(
            label: 'Turma',
            selected: value == _FiltroTipo.turma,
            onTap: () => onChanged(_FiltroTipo.turma),
          ),
          _ToggleOption(
            label: 'Professor',
            selected: value == _FiltroTipo.professor,
            onTap: () => onChanged(_FiltroTipo.professor),
          ),
        ],
      ),
    );
  }
}

class _ToggleOption extends StatelessWidget {
  const _ToggleOption({required this.label, required this.selected, required this.onTap});

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(6),
          boxShadow: selected
              ? [BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 4, offset: const Offset(0, 1))]
              : null,
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 13,
            fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
            color: selected ? AppColors.blackBlue : AppColors.textSecondary,
            fontFamily: 'Poppins',
          ),
        ),
      ),
    );
  }
}

class _EntityDropdown<T> extends StatelessWidget {
  const _EntityDropdown({
    required this.items,
    required this.value,
    required this.itemLabel,
    required this.hint,
    required this.onChanged,
  });

  final List<T> items;
  final T? value;
  final String Function(T) itemLabel;
  final String hint;
  final ValueChanged<T?> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE2E8F0), width: 1.2),
      ),
      child: items.isEmpty
          ? Text(
              'Nenhum item encontrado',
              style: const TextStyle(fontSize: 13, color: AppColors.textSecondary, fontFamily: 'Poppins'),
            )
          : DropdownButtonHideUnderline(
              child: DropdownButton<T>(
                value: items.contains(value) ? value : null,
                hint: Text(hint, style: const TextStyle(fontSize: 13, color: AppColors.textSecondary, fontFamily: 'Poppins')),
                icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF64748B)),
                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.blackBlue, fontFamily: 'Poppins'),
                items: items
                    .map((item) => DropdownMenuItem<T>(value: item, child: Text(itemLabel(item), overflow: TextOverflow.ellipsis)))
                    .toList(),
                onChanged: onChanged,
              ),
            ),
    );
  }
}

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
        _SeletorBox(
          child: DropdownButtonHideUnderline(
            child: DropdownButton<int>(
              value: anoLetivo,
              icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF64748B)),
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.blackBlue, fontFamily: 'Poppins'),
              items: anos.map((a) => DropdownMenuItem(value: a, child: Text('Ano lectivo: $a'))).toList(),
              onChanged: enabled ? (v) => v != null ? onAnoLetivoChanged(v) : null : null,
            ),
          ),
        ),
        const SizedBox(width: 8),
        _SeletorBox(
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: semestre,
              icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF64748B)),
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.blackBlue, fontFamily: 'Poppins'),
              items: const [
                DropdownMenuItem(value: '1', child: Text('1º Semestre')),
                DropdownMenuItem(value: '2', child: Text('2º Semestre')),
              ],
              onChanged: enabled ? (v) => v != null ? onSemestreChanged(v) : null : null,
            ),
          ),
        ),
      ],
    );
  }
}

class _SeletorBox extends StatelessWidget {
  const _SeletorBox({required this.child});

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

class _GeracaoEmProgresso extends StatelessWidget {
  const _GeracaoEmProgresso({
    required this.status,
    required this.elapsedSeconds,
    this.tempoMaximoMinutos,
  });

  final JobStatus? status;
  final int elapsedSeconds;
  final int? tempoMaximoMinutos;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const SizedBox(
            width: 48,
            height: 48,
            child: CircularProgressIndicator(color: AppColors.blackBlue, strokeWidth: 3),
          ),
          const SizedBox(height: 20),
          Text(
            _jobStatusLabel(status),
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.blackBlue, fontFamily: 'Poppins'),
          ),
          const SizedBox(height: 6),
          Text(
            'Tempo decorrido: ${_formatElapsed(elapsedSeconds)}',
            style: const TextStyle(fontSize: 12, color: AppColors.textSecondary, fontFamily: 'Poppins'),
          ),
          if (tempoMaximoMinutos != null) ...[
            const SizedBox(height: 4),
            Text(
              'Resolvido em $tempoMaximoMinutos min',
              style: const TextStyle(fontSize: 11, color: AppColors.textSecondary, fontFamily: 'Poppins'),
            ),
          ],
        ],
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 48, color: AppColors.error),
            const SizedBox(height: 16),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(color: AppColors.error, fontFamily: 'Poppins'),
            ),
          ],
        ),
      ),
    );
  }
}

