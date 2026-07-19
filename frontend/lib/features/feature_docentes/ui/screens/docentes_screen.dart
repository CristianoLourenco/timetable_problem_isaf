import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/core/themes/app_text_styles.dart';
import 'package:ghorario/core/widgets/import_excel_button.dart';
import 'package:ghorario/features/feature_disciplinas/presentation/provider/disciplinas_provider.dart';
import 'package:ghorario/features/feature_docentes/domain/entities/docente.dart';
import 'package:ghorario/features/feature_docentes/domain/usecase/get_qualificacao_usecase.dart';
import 'package:ghorario/features/feature_docentes/domain/usecase/set_qualificacao_usecase.dart';
import 'package:ghorario/features/feature_docentes/presentation/controller/docentes_controller.dart';
import 'package:ghorario/features/feature_docentes/presentation/provider/docentes_provider.dart';
import 'package:ghorario/features/feature_docentes/presentation/states/docentes_state.dart';
import 'package:ghorario/features/feature_docentes/ui/components/docentes_screen_components/qualificacao_dialog.dart';
import 'package:ghorario/features/feature_importacao/domain/entities/entidade_importacao.dart';
import 'package:ghorario/features/feature_importacao/domain/usecase/importar_excel_usecase.dart';

/// Screen for displaying and managing teachers (docentes/professores).
class DocentesScreen extends StatefulWidget {
  const DocentesScreen({super.key});

  @override
  State<DocentesScreen> createState() => _DocentesScreenState();
}

class _DocentesScreenState extends State<DocentesScreen> {
  late final DocentesController _controller;
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _controller = DocentesController(provider: context.read<DocentesProvider>());
    WidgetsBinding.instance.addPostFrameCallback((_) => _controller.init());
  }

  @override
  void dispose() {
    _controller.dispose();
    _searchController.dispose();
    super.dispose();
  }

  String _getInitials(String name) {
    final parts = name.trim().split(' ').where((e) => e.isNotEmpty).toList();
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    } else if (parts.isNotEmpty && parts[0].isNotEmpty) {
      return parts[0][0].toUpperCase();
    }
    return '';
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

  void _showNewDocenteBottomSheet() {
    final nameController = TextEditingController();
    final emailController = TextEditingController();

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
                  'Novo Professor',
                  style: AppTextStyles.heading2.copyWith(color: AppColors.blackBlue),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: 'Nome Completo',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(
                    labelText: 'E-mail',
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
                        if (nameController.text.isEmpty || emailController.text.isEmpty) return;
                        final novoDocente = Docente(
                          id: '',
                          name: nameController.text,
                          email: emailController.text,
                        );
                        final navigator = Navigator.of(context);
                        final messenger = ScaffoldMessenger.of(context);
                        final success = await _controller.createDocente(novoDocente);
                        if (success) {
                          navigator.pop();
                        } else {
                          messenger.showSnackBar(
                            SnackBar(content: Text(_controller.value.errorMessage ?? 'Erro ao criar professor.')),
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
      body: ValueListenableBuilder<DocentesState>(
        valueListenable: _controller,
        builder: (BuildContext context, DocentesState state, Widget? child) {
          final query = _searchQuery.toLowerCase();
          final filteredDocentes = state.docentes.where((docente) {
            return docente.name.toLowerCase().contains(query) ||
                (docente.email ?? '').toLowerCase().contains(query);
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
                          'Professores',
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            color: AppColors.blackBlue,
                            fontFamily: 'Poppins',
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${state.docentes.length} professores registados',
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
                          entidade: EntidadeImportacao.professores,
                          importarExcelUseCase: context.read<ImportarExcelUseCase>(),
                          onImported: _controller.fetchDocentes,
                          label: 'Importar Professores',
                        ),
                        const SizedBox(width: 12),
                        ImportExcelButton(
                          entidade: EntidadeImportacao.qualificacoes,
                          importarExcelUseCase: context.read<ImportarExcelUseCase>(),
                          onImported: () {},
                          label: 'Importar Qualificações',
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton(
                          onPressed: _showNewDocenteBottomSheet,
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
                            'Novo Professor',
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
                // Main Container holding search and table list
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
                        Padding(
                          padding: const EdgeInsets.all(24),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Container(
                                width: 320,
                                height: 44,
                                decoration: BoxDecoration(
                                  color: const Color(0xFFF8FAFC),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: const Color(0xFFE2E8F0), width: 1.2),
                                ),
                                child: TextField(
                                  controller: _searchController,
                                  onChanged: (value) {
                                    setState(() {
                                      _searchQuery = value;
                                    });
                                  },
                                  decoration: const InputDecoration(
                                    hintText: 'Pesquisar por nome ou email...',
                                    hintStyle: TextStyle(
                                      fontSize: 13,
                                      color: Color(0xFF94A3B8),
                                      fontFamily: 'Poppins',
                                    ),
                                    border: InputBorder.none,
                                    contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                                  ),
                                ),
                              ),
                              Text(
                                '${filteredDocentes.length} resultados',
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: Color(0xFF94A3B8),
                                  fontFamily: 'Poppins',
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Padding(
                          padding: EdgeInsets.symmetric(horizontal: 24, vertical: 8),
                          child: Row(
                            children: [
                              Expanded(
                                flex: 8,
                                child: Text(
                                  'NOME',
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
                                  'EMAIL',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF94A3B8),
                                    letterSpacing: 0.8,
                                    fontFamily: 'Poppins',
                                  ),
                                ),
                              ),
                              SizedBox(width: 96),
                            ],
                          ),
                        ),
                        const Divider(color: Color(0xFFF1F5F9), height: 1, thickness: 1),
                        Expanded(
                          child: state.isLoading
                              ? const Center(child: CircularProgressIndicator())
                              : state.errorMessage != null
                                  ? Center(
                                      child: Text(
                                        state.errorMessage!,
                                        style: const TextStyle(color: Colors.red),
                                      ),
                                    )
                                  : ListView.separated(
                                      padding: EdgeInsets.zero,
                                      itemCount: filteredDocentes.length,
                                      separatorBuilder: (context, index) => const Divider(
                                        color: Color(0xFFF1F5F9),
                                        height: 1,
                                        thickness: 1,
                                      ),
                                      itemBuilder: (context, index) {
                                        final docente = filteredDocentes[index];
                                        return Padding(
                                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                                          child: Row(
                                            children: [
                                              Expanded(
                                                flex: 8,
                                                child: Row(
                                                  children: [
                                                    CircleAvatar(
                                                      radius: 18,
                                                      backgroundColor: const Color(0xFFE2E8F0),
                                                      child: Text(
                                                        _getInitials(docente.name),
                                                        style: const TextStyle(
                                                          color: Color(0xFF475569),
                                                          fontSize: 11,
                                                          fontWeight: FontWeight.bold,
                                                          fontFamily: 'Lato',
                                                        ),
                                                      ),
                                                    ),
                                                    const SizedBox(width: 12),
                                                    Expanded(
                                                      child: Text(
                                                        docente.name,
                                                        style: const TextStyle(
                                                          fontSize: 14,
                                                          fontWeight: FontWeight.bold,
                                                          color: AppColors.blackBlue,
                                                          fontFamily: 'Poppins',
                                                        ),
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                              ),
                                              Expanded(
                                                flex: 6,
                                                child: Text(
                                                  docente.email ?? '—',
                                                  style: const TextStyle(
                                                    fontSize: 13,
                                                    color: Color(0xFF64748B),
                                                    fontFamily: 'Poppins',
                                                  ),
                                                ),
                                              ),
                                              SizedBox(
                                                width: 48,
                                                child: IconButton(
                                                  icon: const Icon(Icons.school_outlined, color: Color(0xFF94A3B8)),
                                                  tooltip: 'Qualificação',
                                                  onPressed: () => _showQualificacaoDialog(docente),
                                                ),
                                              ),
                                              SizedBox(
                                                width: 48,
                                                child: IconButton(
                                                  icon: const Icon(Icons.calendar_today_outlined, color: Color(0xFF94A3B8)),
                                                  tooltip: 'Ver Ficha do Docente',
                                                  onPressed: () => context.go('/dashboard/docentes/${docente.id}'),
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
