import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/core/themes/app_text_styles.dart';
import 'package:ghorario/core/widgets/import_excel_button.dart';
import 'package:ghorario/features/feature_disciplinas/domain/entities/disciplina.dart';
import 'package:ghorario/features/feature_disciplinas/presentation/controller/disciplinas_controller.dart';
import 'package:ghorario/features/feature_disciplinas/presentation/provider/disciplinas_provider.dart';
import 'package:ghorario/features/feature_disciplinas/presentation/states/disciplinas_state.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/entidade_importacao.dart';
import 'package:ghorario/features/feature_importacao/domain/usecase/importar_excel_usecase.dart';

/// Screen for displaying and managing academic disciplines.
///
/// A Disciplina is global — it has no direct link to a Curso in the backend
/// data model (only Turma does; a discipline reaches a curso indirectly by
/// being part of one of that curso's turmas via the curriculum grid). Do not
/// reintroduce a "curso" column/field here without a matching backend field.
class DisciplinasScreen extends StatefulWidget {
  const DisciplinasScreen({super.key});

  @override
  State<DisciplinasScreen> createState() => _DisciplinasScreenState();
}

class _DisciplinasScreenState extends State<DisciplinasScreen> {
  late final DisciplinasController _controller;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _controller = DisciplinasController(provider: context.read<DisciplinasProvider>());
    WidgetsBinding.instance.addPostFrameCallback((_) => _controller.init());
    _searchController.addListener(_onSearchChanged);
  }

  @override
  void dispose() {
    _searchController.removeListener(_onSearchChanged);
    _searchController.dispose();
    _controller.dispose();
    super.dispose();
  }

  void _onSearchChanged() {
    setState(() {});
  }

  void _showNewDisciplinaBottomSheet() {
    final nameController = TextEditingController();
    final codeController = TextEditingController();

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
                  'Nova Disciplina',
                  style: AppTextStyles.heading2.copyWith(color: AppColors.blackBlue),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: 'Nome da Disciplina',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: codeController,
                  decoration: const InputDecoration(
                    labelText: 'Código (Ex: ENG301)',
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
                        final newDisc = Disciplina(
                          id: '',
                          name: nameController.text,
                          code: codeController.text.toUpperCase(),
                        );
                        final navigator = Navigator.of(context);
                        final messenger = ScaffoldMessenger.of(context);
                        final success = await _controller.addDisciplina(newDisc);
                        if (success) {
                          navigator.pop();
                        } else {
                          messenger.showSnackBar(
                            SnackBar(content: Text(_controller.value.errorMessage ?? 'Erro ao criar disciplina.')),
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
      body: ValueListenableBuilder<DisciplinasState>(
        valueListenable: _controller,
        builder: (BuildContext context, DisciplinasState state, Widget? child) {
          if (state.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state.errorMessage != null) {
            return Center(
              child: Text(
                state.errorMessage!,
                style: const TextStyle(color: Colors.red),
              ),
            );
          }

          final List<Disciplina> currentList = state.disciplinas;

          // Filter by search query
          final query = _searchController.text.toLowerCase();
          final filteredList = currentList.where((d) {
            final nameMatch = d.name.toLowerCase().contains(query);
            final codeMatch = (d.code ?? '').toLowerCase().contains(query);
            return nameMatch || codeMatch;
          }).toList();

          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Row
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Disciplinas',
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            color: AppColors.blackBlue,
                            fontFamily: 'Poppins',
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${filteredList.length} disciplinas cadastradas',
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
                          entidade: EntidadeImportacao.disciplinas,
                          importarExcelUseCase: context.read<ImportarExcelUseCase>(),
                          onImported: _controller.fetchDisciplinas,
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton(
                          onPressed: _showNewDisciplinaBottomSheet,
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
                            'Nova Disciplina',
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
                // Main White Card containing Search and Table
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFFE8EEF5), width: 1.2),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF0F172A).withOpacity(0.02),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    clipBehavior: Clip.antiAlias,
                    child: Column(
                      children: [
                        // Search Bar
                        Padding(
                          padding: const EdgeInsets.all(24),
                          child: Container(
                            decoration: BoxDecoration(
                              color: const Color(0xFFF8FAFC),
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: const Color(0xFFE2E8F0)),
                            ),
                            child: TextField(
                              controller: _searchController,
                              decoration: const InputDecoration(
                                hintText: 'Pesquisar por disciplina ou código...',
                                hintStyle: TextStyle(
                                  color: Color(0xFF94A3B8),
                                  fontSize: 14,
                                  fontFamily: 'Poppins',
                                ),
                                prefixIcon: Icon(
                                  Icons.search,
                                  color: Color(0xFF94A3B8),
                                  size: 20,
                                ),
                                border: InputBorder.none,
                                contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                              ),
                              style: const TextStyle(
                                fontSize: 14,
                                color: AppColors.blackBlue,
                                fontFamily: 'Poppins',
                              ),
                            ),
                          ),
                        ),
                        // Table Header Row
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                          child: Row(
                            children: const [
                              Expanded(
                                flex: 2,
                                child: Text(
                                  'CÓDIGO',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF94A3B8),
                                    letterSpacing: 0.8,
                                    fontFamily: 'Poppins',
                                  ),
                                ),
                              ),
                              Expanded(
                                flex: 6,
                                child: Text(
                                  'DISCIPLINA',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF94A3B8),
                                    letterSpacing: 0.8,
                                    fontFamily: 'Poppins',
                                  ),
                                ),
                              ),
                              SizedBox(width: 48), // Space for action button
                            ],
                          ),
                        ),
                        const Divider(
                          color: Color(0xFFF1F5F9),
                          height: 1,
                          thickness: 1,
                        ),
                        // List Body
                        Expanded(
                          child: filteredList.isEmpty
                              ? const Center(
                                  child: Text(
                                    'Nenhuma disciplina correspondente encontrada.',
                                    style: TextStyle(
                                      color: AppColors.textSecondary,
                                      fontFamily: 'Poppins',
                                    ),
                                  ),
                                )
                              : ListView.separated(
                                  padding: EdgeInsets.zero,
                                  itemCount: filteredList.length,
                                  separatorBuilder: (context, index) => const Divider(
                                    color: Color(0xFFF1F5F9),
                                    height: 1,
                                    thickness: 1,
                                  ),
                                  itemBuilder: (context, index) {
                                    final disc = filteredList[index];
                                    return Padding(
                                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                                      child: Row(
                                        children: [
                                          // Code
                                          Expanded(
                                            flex: 2,
                                            child: Text(
                                              disc.code ?? 'N/A',
                                              style: const TextStyle(
                                                fontSize: 14,
                                                fontWeight: FontWeight.w600,
                                                color: AppColors.blackBlue,
                                                fontFamily: 'Poppins',
                                              ),
                                            ),
                                          ),
                                          // Subject Name
                                          Expanded(
                                            flex: 6,
                                            child: Text(
                                              disc.name,
                                              style: const TextStyle(
                                                fontSize: 14,
                                                fontWeight: FontWeight.bold,
                                                color: AppColors.blackBlue,
                                                fontFamily: 'Poppins',
                                              ),
                                            ),
                                          ),
                                          // Actions dot button
                                          SizedBox(
                                            width: 48,
                                            child: IconButton(
                                              icon: const Icon(
                                                Icons.more_horiz,
                                                color: Color(0xFF94A3B8),
                                              ),
                                              onPressed: () {},
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
