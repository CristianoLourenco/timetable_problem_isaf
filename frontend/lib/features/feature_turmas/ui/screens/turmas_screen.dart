import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:ghorario/core/enums/turno.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/core/themes/app_text_styles.dart';
import 'package:ghorario/core/widgets/import_excel_button.dart';
import 'package:ghorario/features/feature_disciplinas/presentation/provider/disciplinas_provider.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/entidade_importacao.dart';
import 'package:ghorario/features/feature_importacao/domain/usecase/importar_excel_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/curso.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/plano_curricular.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/get_all_cursos_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/get_all_planos_curriculares_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/get_grade_curricular_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/set_grade_curricular_usecase.dart';
import 'package:ghorario/features/feature_turmas/presentation/controller/turmas_controller.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/turmas_provider.dart';
import 'package:ghorario/features/feature_turmas/presentation/states/turmas_state.dart';
import 'package:ghorario/features/feature_turmas/ui/components/turmas_screen_components/grade_curricular_dialog.dart';

/// Screen for displaying and managing Student Groups (Turmas).
class TurmasScreen extends StatefulWidget {
  const TurmasScreen({super.key});

  @override
  State<TurmasScreen> createState() => _TurmasScreenState();
}

class _TurmasScreenState extends State<TurmasScreen> {
  late final TurmasController _controller;
  List<Curso> _cursos = const <Curso>[];
  List<PlanoCurricular> _planos = const <PlanoCurricular>[];
  bool _isListView = false;

  Turno? _selectedPeriodFilter;

  @override
  void initState() {
    super.initState();
    _controller = TurmasController(provider: context.read<TurmasProvider>());
    WidgetsBinding.instance.addPostFrameCallback((_) => _controller.init());
    _loadCursos();
    _loadPlanos();
  }

  Future<void> _loadCursos() async {
    final result = await context.read<GetAllCursosUseCase>()(null);
    if (mounted && result.success && result.data != null) {
      setState(() => _cursos = result.data!);
    }
  }

  Future<void> _loadPlanos() async {
    final result = await context.read<GetAllPlanosCurricularesUseCase>()(null);
    if (mounted && result.success && result.data != null) {
      setState(() => _planos = result.data!);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _showGradeCurricularDialog(Turma turma) async {
    final planoCurricularId = turma.planoCurricularId;
    if (planoCurricularId == null) return;

    final disciplinasProvider = context.read<DisciplinasProvider>();
    if (disciplinasProvider.disciplinas.isEmpty) {
      await disciplinasProvider.loadDisciplinas();
    }
    if (!mounted) return;

    await showDialog<void>(
      context: context,
      builder: (context) => GradeCurricularDialog(
        planoCurricularId: planoCurricularId,
        turmaNome: turma.code ?? turma.name,
        disciplinas: disciplinasProvider.disciplinas,
        getGradeCurricularUseCase: context.read<GetGradeCurricularUseCase>(),
        setGradeCurricularUseCase: context.read<SetGradeCurricularUseCase>(),
      ),
    );
  }

  String _cursoNomePorId(String? cursoId) {
    if (cursoId == null) return '—';
    final match = _cursos.where((c) => c.id == cursoId);
    return match.isEmpty ? '—' : match.first.name;
  }

  /// "Curso - ano/semestre" label for a Turma's PlanoCurricular (ex: "Informática — 1º Ano, Sem. 1").
  String _planoLabel(int? planoCurricularId) {
    if (planoCurricularId == null) return '—';
    final match = _planos.where((p) => p.id == planoCurricularId.toString());
    if (match.isEmpty) return '—';
    final plano = match.first;
    return '${_cursoNomePorId(plano.cursoId)} — ${plano.ano}º Ano, Sem. ${plano.semestre}';
  }

  Widget _buildPeriodBadge(Turno? period) {
    if (period == null) return const SizedBox.shrink();
    Color bgColor;
    Color textColor;
    switch (period) {
      case Turno.manha:
        bgColor = const Color(0xFFFEF3C7);
        textColor = const Color(0xFFD97706);
        break;
      case Turno.tarde:
        bgColor = const Color(0xFFE0F2FE);
        textColor = const Color(0xFF0284C7);
        break;
      case Turno.noite:
        bgColor = const Color(0xFFE2E8F0);
        textColor = const Color(0xFF334155);
        break;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: bgColor, borderRadius: BorderRadius.circular(4)),
      child: Text(
        period.displayName.toUpperCase(),
        style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: textColor, fontFamily: 'Poppins'),
      ),
    );
  }

  void _showFilterMenu(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Filtrar por Período'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                title: const Text('Todos'),
                leading: Radio<Turno?>(
                  value: null,
                  groupValue: _selectedPeriodFilter,
                  onChanged: (val) {
                    setState(() => _selectedPeriodFilter = val);
                    Navigator.pop(context);
                  },
                ),
              ),
              for (final turno in Turno.values)
                ListTile(
                  title: Text(turno.displayName),
                  leading: Radio<Turno?>(
                    value: turno,
                    groupValue: _selectedPeriodFilter,
                    onChanged: (val) {
                      setState(() => _selectedPeriodFilter = val);
                      Navigator.pop(context);
                    },
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  void _showNewTurmaBottomSheet() {
    final codeController = TextEditingController();
    final nameController = TextEditingController();
    final studentCountController = TextEditingController(text: '30');
    final yearController = TextEditingController(text: '1');

    PlanoCurricular? selectedPlano = _planos.isNotEmpty ? _planos.first : null;
    Turno selectedPeriod = Turno.manha;

    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter setModalState) {
            return Padding(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).viewInsets.bottom,
                left: 24,
                right: 24,
                top: 24,
              ),
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text('Nova Turma', style: AppTextStyles.heading2.copyWith(color: AppColors.blackBlue)),
                    const SizedBox(height: 16),
                    if (_planos.isEmpty)
                      const Text(
                        'Nenhum plano curricular encontrado — crie um Plano Curricular primeiro.',
                        style: TextStyle(color: AppColors.textSecondary, fontFamily: 'Poppins'),
                      )
                    else
                      DropdownButtonFormField<PlanoCurricular>(
                        initialValue: selectedPlano,
                        decoration: const InputDecoration(labelText: 'Plano Curricular', border: OutlineInputBorder()),
                        items: _planos
                            .map((p) => DropdownMenuItem(value: p, child: Text(_planoLabel(int.tryParse(p.id)))))
                            .toList(),
                        onChanged: (val) => setModalState(() => selectedPlano = val),
                      ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: nameController,
                      decoration: const InputDecoration(labelText: 'Nome da Turma', border: OutlineInputBorder()),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: codeController,
                      decoration: const InputDecoration(
                        labelText: 'Código da Turma (Ex: CC-3A)',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: DropdownButtonFormField<Turno>(
                            initialValue: selectedPeriod,
                            decoration: const InputDecoration(labelText: 'Turno', border: OutlineInputBorder()),
                            items: Turno.values
                                .map((t) => DropdownMenuItem(value: t, child: Text(t.displayName)))
                                .toList(),
                            onChanged: (val) {
                              if (val != null) setModalState(() => selectedPeriod = val);
                            },
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: TextField(
                            controller: yearController,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(labelText: 'Ano Letivo', border: OutlineInputBorder()),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: studentCountController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Quantidade de Alunos',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        TextButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text('Cancelar', style: TextStyle(color: AppColors.textSecondary)),
                        ),
                        const SizedBox(width: 8),
                        ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.blackBlue,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          ),
                          onPressed: selectedPlano == null
                              ? null
                              : () async {
                                  if (codeController.text.isEmpty || nameController.text.isEmpty) return;
                                  final novaTurma = Turma(
                                    id: '',
                                    name: nameController.text,
                                    code: codeController.text.toUpperCase(),
                                    year: int.tryParse(yearController.text) ?? 1,
                                    period: selectedPeriod,
                                    studentsCount: int.tryParse(studentCountController.text) ?? 30,
                                    planoCurricularId: int.tryParse(selectedPlano!.id),
                                  );
                                  final navigator = Navigator.of(context);
                                  final messenger = ScaffoldMessenger.of(context);
                                  final success = await _controller.createTurma(novaTurma);
                                  if (success) {
                                    navigator.pop();
                                  } else {
                                    messenger.showSnackBar(
                                      SnackBar(
                                        content:
                                            Text(_controller.value.errorMessage ?? 'Erro ao criar turma.'),
                                      ),
                                    );
                                  }
                                },
                          child: const Text('Adicionar'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildViewToggle() {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: const Color(0xFFE2E8F0), width: 1.2),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            icon: const Icon(Icons.grid_view_rounded, size: 20),
            color: _isListView ? const Color(0xFF94A3B8) : AppColors.blackBlue,
            tooltip: 'Grelha',
            onPressed: () => setState(() => _isListView = false),
          ),
          IconButton(
            icon: const Icon(Icons.view_list_rounded, size: 20),
            color: _isListView ? AppColors.blackBlue : const Color(0xFF94A3B8),
            tooltip: 'Lista',
            onPressed: () => setState(() => _isListView = true),
          ),
        ],
      ),
    );
  }

  Widget _buildListView(List<Turma> turmas) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE8EEF5), width: 1.2),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        children: [
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            child: Row(
              children: [
                Expanded(flex: 2, child: Text('CÓDIGO', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8), letterSpacing: 0.8, fontFamily: 'Poppins'))),
                Expanded(flex: 3, child: Text('CURSO', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8), letterSpacing: 0.8, fontFamily: 'Poppins'))),
                Expanded(flex: 2, child: Text('TURNO', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8), letterSpacing: 0.8, fontFamily: 'Poppins'))),
                Expanded(flex: 2, child: Text('ALUNOS', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8), letterSpacing: 0.8, fontFamily: 'Poppins'))),
                Expanded(flex: 2, child: Text('ANO', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8), letterSpacing: 0.8, fontFamily: 'Poppins'))),
                SizedBox(width: 48),
              ],
            ),
          ),
          const Divider(color: Color(0xFFF1F5F9), height: 1, thickness: 1),
          Expanded(
            child: ListView.separated(
              padding: EdgeInsets.zero,
              itemCount: turmas.length,
              separatorBuilder: (context, index) => const Divider(color: Color(0xFFF1F5F9), height: 1, thickness: 1),
              itemBuilder: (context, index) {
                final turma = turmas[index];
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                  child: Row(
                    children: [
                      Expanded(flex: 2, child: Text(turma.code ?? turma.name, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.blackBlue, fontFamily: 'Poppins'))),
                      Expanded(flex: 3, child: Text(_planoLabel(turma.planoCurricularId), style: const TextStyle(fontSize: 14, color: AppColors.textSecondary, fontFamily: 'Poppins'))),
                      Expanded(flex: 2, child: Text(turma.period?.displayName ?? '—', style: const TextStyle(fontSize: 14, color: AppColors.blackBlue, fontFamily: 'Poppins'))),
                      Expanded(flex: 2, child: Text('${turma.studentsCount ?? '—'}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.blackBlue, fontFamily: 'Poppins'))),
                      Expanded(flex: 2, child: Text('${turma.year ?? '—'}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.lightBlue, fontFamily: 'Poppins'))),
                      SizedBox(
                        width: 48,
                        child: IconButton(
                          icon: const Icon(Icons.menu_book, size: 18, color: Color(0xFF94A3B8)),
                          tooltip: 'Grade Curricular',
                          onPressed: () => _showGradeCurricularDialog(turma),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: ValueListenableBuilder<TurmasState>(
        valueListenable: _controller,
        builder: (BuildContext context, TurmasState state, Widget? child) {
          final filteredTurmas = _selectedPeriodFilter == null
              ? state.turmas
              : state.turmas.where((t) => t.period == _selectedPeriodFilter).toList();

          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Turmas',
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            color: AppColors.blackBlue,
                            fontFamily: 'Poppins',
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${filteredTurmas.length} turmas registadas',
                          style: const TextStyle(fontSize: 14, color: AppColors.textSecondary, fontFamily: 'Poppins'),
                        ),
                      ],
                    ),
                    Row(
                      children: [
                        _buildViewToggle(),
                        const SizedBox(width: 12),
                        ImportExcelButton(
                          entidade: EntidadeImportacao.turmas,
                          importarExcelUseCase: context.read<ImportarExcelUseCase>(),
                          onImported: _controller.fetchTurmas,
                          label: 'Importar Turmas',
                        ),
                        const SizedBox(width: 12),
                        ImportExcelButton(
                          entidade: EntidadeImportacao.gradeCurricular,
                          importarExcelUseCase: context.read<ImportarExcelUseCase>(),
                          onImported: () {},
                          label: 'Importar Grade Curricular',
                        ),
                        const SizedBox(width: 12),
                        OutlinedButton(
                          onPressed: () => _showFilterMenu(context),
                          style: OutlinedButton.styleFrom(
                            backgroundColor: Colors.white,
                            side: const BorderSide(color: Color(0xFFE2E8F0), width: 1.2),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                          ),
                          child: const Text(
                            'Filtrar',
                            style: TextStyle(color: AppColors.blackBlue, fontWeight: FontWeight.w600, fontFamily: 'Poppins'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton(
                          onPressed: _showNewTurmaBottomSheet,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.blackBlue,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                            elevation: 0,
                          ),
                          child: const Text(
                            'Nova Turma',
                            style: TextStyle(fontWeight: FontWeight.w600, fontFamily: 'Poppins'),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                Expanded(
                  child: state.isLoading
                      ? const Center(child: CircularProgressIndicator())
                      : state.errorMessage != null
                          ? Center(
                              child: Text(state.errorMessage!, style: const TextStyle(color: Colors.red)),
                            )
                          : filteredTurmas.isEmpty
                              ? const Center(
                                  child: Text(
                                    'Nenhuma turma encontrada.',
                                    style: TextStyle(fontSize: 16, color: AppColors.textSecondary, fontFamily: 'Poppins'),
                                  ),
                                )
                              : _isListView
                              ? _buildListView(filteredTurmas)
                              : GridView.builder(
                                  padding: EdgeInsets.zero,
                                  gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                                    maxCrossAxisExtent: 320,
                                    mainAxisExtent: 200,
                                    crossAxisSpacing: 24,
                                    mainAxisSpacing: 24,
                                  ),
                                  itemCount: filteredTurmas.length,
                                  itemBuilder: (context, index) {
                                    final turma = filteredTurmas[index];
                                    return Container(
                                      decoration: BoxDecoration(
                                        color: Colors.white,
                                        borderRadius: BorderRadius.circular(16),
                                        border: Border.all(color: const Color(0xFFE8EEF5), width: 1.2),
                                      ),
                                      child: Padding(
                                        padding: const EdgeInsets.all(24),
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Row(
                                              crossAxisAlignment: CrossAxisAlignment.start,
                                              children: [
                                                Expanded(
                                                  child: Wrap(
                                                    crossAxisAlignment: WrapCrossAlignment.center,
                                                    spacing: 6,
                                                    runSpacing: 4,
                                                    children: [
                                                      Text(
                                                        _planoLabel(turma.planoCurricularId),
                                                        style: const TextStyle(
                                                          fontSize: 12,
                                                          fontWeight: FontWeight.w500,
                                                          color: Color(0xFF64748B),
                                                          fontFamily: 'Poppins',
                                                        ),
                                                      ),
                                                      _buildPeriodBadge(turma.period),
                                                    ],
                                                  ),
                                                ),
                                                IconButton(
                                                  icon: const Icon(Icons.menu_book, size: 18, color: Color(0xFF94A3B8)),
                                                  tooltip: 'Grade Curricular',
                                                  onPressed: () => _showGradeCurricularDialog(turma),
                                                  visualDensity: VisualDensity.compact,
                                                  padding: EdgeInsets.zero,
                                                  constraints: const BoxConstraints(maxWidth: 28, maxHeight: 28),
                                                ),
                                              ],
                                            ),
                                            const Spacer(),
                                            Text(
                                              turma.code ?? turma.name,
                                              style: const TextStyle(
                                                fontSize: 24,
                                                fontWeight: FontWeight.bold,
                                                color: AppColors.blackBlue,
                                                fontFamily: 'Poppins',
                                              ),
                                            ),
                                            const Spacer(),
                                            const Divider(color: Color(0xFFF1F5F9), height: 1, thickness: 1),
                                            const SizedBox(height: 16),
                                            Row(
                                              children: [
                                                Column(
                                                  crossAxisAlignment: CrossAxisAlignment.start,
                                                  children: [
                                                    const Text(
                                                      'ALUNOS',
                                                      style: TextStyle(
                                                        fontSize: 9,
                                                        fontWeight: FontWeight.bold,
                                                        color: Color(0xFF94A3B8),
                                                        letterSpacing: 0.8,
                                                        fontFamily: 'Poppins',
                                                      ),
                                                    ),
                                                    const SizedBox(height: 4),
                                                    Text(
                                                      '${turma.studentsCount ?? '—'}',
                                                      style: const TextStyle(
                                                        fontSize: 18,
                                                        fontWeight: FontWeight.bold,
                                                        color: AppColors.blackBlue,
                                                        fontFamily: 'Poppins',
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                                const Spacer(),
                                                Column(
                                                  crossAxisAlignment: CrossAxisAlignment.end,
                                                  children: [
                                                    const Text(
                                                      'ANO LETIVO',
                                                      style: TextStyle(
                                                        fontSize: 9,
                                                        fontWeight: FontWeight.bold,
                                                        color: Color(0xFF94A3B8),
                                                        letterSpacing: 0.8,
                                                        fontFamily: 'Poppins',
                                                      ),
                                                    ),
                                                    const SizedBox(height: 4),
                                                    Text(
                                                      '${turma.year ?? '—'}',
                                                      style: const TextStyle(
                                                        fontSize: 18,
                                                        fontWeight: FontWeight.bold,
                                                        color: AppColors.lightBlue,
                                                        fontFamily: 'Poppins',
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                              ],
                                            ),
                                          ],
                                        ),
                                      ),
                                    );
                                  },
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
