import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/core/themes/app_text_styles.dart';
import 'package:ghorario/core/widgets/import_excel_button.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/entidade_importacao.dart';
import 'package:ghorario/features/feature_importacao/domain/usecase/importar_excel_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/curso.dart';
import 'package:ghorario/features/feature_turmas/presentation/controller/cursos_controller.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/cursos_provider.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/turmas_provider.dart';
import 'package:ghorario/features/feature_turmas/presentation/states/cursos_state.dart';

/// Screen for displaying and managing Courses (Cursos) — a support entity
/// with no RF of its own, required only as `Turma.cursoId`'s prerequisite.
class CursosScreen extends StatefulWidget {
  const CursosScreen({super.key});

  @override
  State<CursosScreen> createState() => _CursosScreenState();
}

class _CursosScreenState extends State<CursosScreen> {
  late final CursosController _controller;

  @override
  void initState() {
    super.initState();
    _controller = CursosController(provider: context.read<CursosProvider>());
    final turmasProvider = context.read<TurmasProvider>();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _controller.init();
      if (turmasProvider.turmas.isEmpty) {
        turmasProvider.loadTurmas();
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  int _turmasCount(String cursoId) {
    final turmas = context.watch<TurmasProvider>().turmas;
    return turmas.where((t) => t.cursoId?.toString() == cursoId).length;
  }

  void _showNewCourseBottomSheet() {
    final codeController = TextEditingController();
    final nameController = TextEditingController();

    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (BuildContext context) {
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
                Text(
                  'Novo Curso',
                  style: AppTextStyles.heading2.copyWith(color: AppColors.blackBlue),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: 'Nome do Curso',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: codeController,
                  decoration: const InputDecoration(
                    labelText: 'Código (Ex: CC)',
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
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      onPressed: () async {
                        if (nameController.text.isEmpty || codeController.text.isEmpty) return;
                        final novoCurso = Curso(
                          id: '',
                          codigo: codeController.text.toUpperCase(),
                          name: nameController.text,
                        );
                        final navigator = Navigator.of(context);
                        final messenger = ScaffoldMessenger.of(context);
                        final success = await _controller.createCurso(novoCurso);
                        if (success) {
                          navigator.pop();
                        } else {
                          messenger.showSnackBar(
                            SnackBar(content: Text(_controller.value.errorMessage ?? 'Erro ao criar curso.')),
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
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: ValueListenableBuilder<CursosState>(
        valueListenable: _controller,
        builder: (BuildContext context, CursosState state, Widget? child) {
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
                          'Cursos',
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            color: AppColors.blackBlue,
                            fontFamily: 'Poppins',
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${state.cursos.length} cursos registados',
                          style: const TextStyle(
                            fontSize: 14,
                            color: AppColors.textSecondary,
                            fontFamily: 'Poppins',
                          ),
                        ),
                      ],
                    ),
                    Row(
                      children: [
                        ImportExcelButton(
                          entidade: EntidadeImportacao.cursos,
                          importarExcelUseCase: context.read<ImportarExcelUseCase>(),
                          onImported: _controller.fetchCursos,
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton(
                          onPressed: _showNewCourseBottomSheet,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.blackBlue,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                            elevation: 0,
                          ),
                          child: const Text(
                            'Novo Curso',
                            style: TextStyle(
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
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFFE8EEF5), width: 1.2),
                    ),
                    clipBehavior: Clip.antiAlias,
                    child: state.isLoading
                        ? const Center(child: CircularProgressIndicator())
                        : state.errorMessage != null
                            ? Center(child: Text(state.errorMessage!, style: const TextStyle(color: Colors.red)))
                            : state.cursos.isEmpty
                                ? const Center(
                                    child: Text(
                                      'Nenhum curso encontrado.',
                                      style: TextStyle(color: AppColors.textSecondary, fontFamily: 'Poppins'),
                                    ),
                                  )
                                : ListView.separated(
                                    padding: EdgeInsets.zero,
                                    itemCount: state.cursos.length,
                                    separatorBuilder: (context, index) => const Divider(
                                      color: Color(0xFFF1F5F9),
                                      height: 1,
                                      thickness: 1,
                                    ),
                                    itemBuilder: (context, index) {
                                      final curso = state.cursos[index];
                                      return Padding(
                                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                                        child: Row(
                                          children: [
                                            Container(
                                              width: 44,
                                              height: 44,
                                              decoration: BoxDecoration(
                                                color: AppColors.blackBlue,
                                                borderRadius: BorderRadius.circular(10),
                                              ),
                                              alignment: Alignment.center,
                                              child: Text(
                                                curso.codigo,
                                                style: const TextStyle(
                                                  color: Colors.white,
                                                  fontSize: 12,
                                                  fontWeight: FontWeight.bold,
                                                  fontFamily: 'Lato',
                                                ),
                                              ),
                                            ),
                                            const SizedBox(width: 20),
                                            Expanded(
                                              child: Text(
                                                curso.name,
                                                style: const TextStyle(
                                                  fontSize: 16,
                                                  fontWeight: FontWeight.bold,
                                                  color: AppColors.blackBlue,
                                                  fontFamily: 'Poppins',
                                                  height: 1.2,
                                                ),
                                              ),
                                            ),
                                            Column(
                                              crossAxisAlignment: CrossAxisAlignment.end,
                                              children: [
                                                const Text(
                                                  'TURMAS',
                                                  style: TextStyle(
                                                    fontSize: 10,
                                                    fontWeight: FontWeight.bold,
                                                    color: Color(0xFF94A3B8),
                                                    letterSpacing: 0.8,
                                                    fontFamily: 'Poppins',
                                                  ),
                                                ),
                                                const SizedBox(height: 4),
                                                Text(
                                                  '${_turmasCount(curso.id)}',
                                                  style: const TextStyle(
                                                    fontSize: 20,
                                                    fontWeight: FontWeight.bold,
                                                    color: AppColors.lightBlue,
                                                    fontFamily: 'Poppins',
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ],
                                        ),
                                      );
                                    },
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
