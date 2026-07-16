import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:ghorario/core/themes/app_colors.dart';

// Providers
import 'package:ghorario/features/feature_docentes/presentation/provider/docentes_provider.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/cursos_provider.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/turmas_provider.dart';
import 'package:ghorario/features/feature_disciplinas/presentation/provider/disciplinas_provider.dart';
import 'package:ghorario/features/feature_salas/presentation/provider/salas_provider.dart';

// Controller & State
import 'package:ghorario/features/feature_dashboard/presentation/controller/dashboard_controller.dart';
import 'package:ghorario/features/feature_dashboard/presentation/states/dashboard_state.dart';

// Entities
import 'package:ghorario/features/feature_turmas/domain/entities/curso.dart';
import 'package:ghorario/features/feature_docentes/domain/entities/docente.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';
import 'package:ghorario/features/feature_salas/domain/entities/sala.dart';

// Components
import 'package:ghorario/features/feature_dashboard/ui/components/home_screen_components/kpi_card.dart';
import 'package:ghorario/features/feature_dashboard/ui/components/home_screen_components/tab_pill.dart';
import 'package:ghorario/features/feature_dashboard/ui/components/home_screen_components/list_row.dart';
import 'package:ghorario/features/feature_dashboard/ui/components/home_screen_components/empty_state.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final DashboardController _controller;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _controller = DashboardController(
      docentesProvider: context.read<DocentesProvider>(),
      turmasProvider: context.read<TurmasProvider>(),
      disciplinasProvider: context.read<DisciplinasProvider>(),
      salasProvider: context.read<SalasProvider>(),
      cursosProvider: context.read<CursosProvider>(),
    );
    // Providers' first loadX() calls notifyListeners() before their first
    // `await` — calling that synchronously from initState hits Flutter's
    // "setState during build" assertion, since initState runs mid-build.
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
    _controller.setSearchQuery(_searchController.text);
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<DashboardState>(
      valueListenable: _controller,
      builder: (context, state, child) {
        return Scaffold(
          backgroundColor: Colors.transparent,
          body: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Home Screen',
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: AppColors.blackBlue,
                        fontFamily: 'Poppins',
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'Resumo operacional do campus',
                      style: TextStyle(
                        fontSize: 14,
                        color: AppColors.textSecondary,
                        fontFamily: 'Poppins',
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 32),

                // KPI Grid / Row
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      KpiCard(
                        icon: Icons.people_outline_rounded,
                        value: '${state.teachersCount}',
                        title: 'Professores',
                        subtitle: '${state.totalWeeklyHours}h semanais',
                        iconColor: AppColors.lightBlue,
                      ),
                      const SizedBox(width: 16),
                      KpiCard(
                        icon: Icons.school_outlined,
                        value: '${state.classesCount}',
                        title: 'Turmas',
                        subtitle: '0 alunos',
                        iconColor: AppColors.blackBlue,
                      ),
                      const SizedBox(width: 16),
                      KpiCard(
                        icon: Icons.book_outlined,
                        value: '${state.coursesCount}',
                        title: 'Cursos',
                        subtitle: 'Cursos ativos',
                        iconColor: const Color(0xFF6366F1),
                      ),
                      const SizedBox(width: 16),
                      KpiCard(
                        icon: Icons.assignment_outlined,
                        value: '${state.disciplinasCount}',
                        title: 'Disciplinas',
                        subtitle: 'cadastradas',
                        iconColor: const Color(0xFF10B981),
                      ),
                      const SizedBox(width: 16),
                      KpiCard(
                        icon: Icons.meeting_room_outlined,
                        value: '${state.roomsCount}',
                        title: 'Salas',
                        subtitle: 'Espaços ativos',
                        iconColor: const Color(0xFFF59E0B),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),
                // Main "Horários" Table Card
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: const Color(0xFFE8EEF5),
                        width: 1.2,
                      ),
                    ),
                    clipBehavior: Clip.antiAlias,
                    child: Column(
                      children: [
                        // Card Header Row
                        Padding(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 24,
                            vertical: 20,
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                children: [
                                  const Icon(
                                    Icons.calendar_today_outlined,
                                    color: AppColors.blackBlue,
                                    size: 20,
                                  ),
                                  const SizedBox(width: 12),
                                  const Text(
                                    'Horários',
                                    style: TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: AppColors.blackBlue,
                                      fontFamily: 'Poppins',
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFF1F5F9),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: const Text(
                                      '0 aulas geradas',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: Color(0xFF64748B),
                                        fontWeight: FontWeight.w500,
                                        fontFamily: 'Poppins',
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              OutlinedButton.icon(
                                onPressed: () {
                                  // Export action placeholder
                                },
                                icon: const Icon(
                                  Icons.download_rounded,
                                  size: 18,
                                  color: AppColors.blackBlue,
                                ),
                                label: const Text(
                                  'Exportar todos',
                                  style: TextStyle(
                                    color: AppColors.blackBlue,
                                    fontWeight: FontWeight.w600,
                                    fontFamily: 'Poppins',
                                  ),
                                ),
                                style: OutlinedButton.styleFrom(
                                  side: const BorderSide(
                                    color: Color(0xFFE2E8F0),
                                  ),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 16,
                                    vertical: 12,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Divider(
                          color: Color(0xFFF1F5F9),
                          height: 1,
                          thickness: 1,
                        ),

                        // Filter Actions & Search Input Row
                        Padding(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 24,
                            vertical: 16,
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              // Custom Pills Segmented Control
                              Container(
                                decoration: BoxDecoration(
                                  color: const Color(0xFFF1F5F9),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                padding: const EdgeInsets.all(4),
                                child: Row(
                                  children: [
                                    _buildTabPill(
                                      'Professores',
                                      HomeTab.professores,
                                      state.activeTab,
                                    ),
                                    _buildTabPill(
                                      'Turmas',
                                      HomeTab.turmas,
                                      state.activeTab,
                                    ),
                                    _buildTabPill(
                                      'Cursos',
                                      HomeTab.cursos,
                                      state.activeTab,
                                    ),
                                    _buildTabPill(
                                      'Salas',
                                      HomeTab.salas,
                                      state.activeTab,
                                    ),
                                  ],
                                ),
                              ),

                              // Search Bar
                              SizedBox(
                                width: 240,
                                height: 40,
                                child: TextField(
                                  controller: _searchController,
                                  style: const TextStyle(fontSize: 14),
                                  decoration: InputDecoration(
                                    prefixIcon: const Icon(
                                      Icons.search,
                                      size: 18,
                                      color: Color(0xFF94A3B8),
                                    ),
                                    hintText: 'Filtrar...',
                                    hintStyle: const TextStyle(
                                      color: Color(0xFF94A3B8),
                                    ),
                                    contentPadding: EdgeInsets.zero,
                                    filled: true,
                                    fillColor: Colors.white,
                                    border: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(8),
                                      borderSide: const BorderSide(
                                        color: Color(0xFFE2E8F0),
                                      ),
                                    ),
                                    enabledBorder: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(8),
                                      borderSide: const BorderSide(
                                        color: Color(0xFFE2E8F0),
                                      ),
                                    ),
                                    focusedBorder: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(8),
                                      borderSide: const BorderSide(
                                        color: AppColors.blackBlue,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Divider(
                          color: Color(0xFFF1F5F9),
                          height: 1,
                          thickness: 1,
                        ),

                        // List View Area
                        Expanded(
                          child: state.filteredItems.isEmpty
                              ? const HomeEmptyState()
                              : ListView.separated(
                                  padding: EdgeInsets.zero,
                                  itemCount: state.filteredItems.length,
                                  separatorBuilder: (context, index) =>
                                      const Divider(
                                        color: Color(0xFFF1F5F9),
                                        height: 1,
                                        thickness: 1,
                                      ),
                                  itemBuilder: (context, index) {
                                    final item = state.filteredItems[index];
                                    return _buildListRow(item);
                                  },
                                ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTabPill(String label, HomeTab tab, HomeTab activeTab) {
    return TabPill(
      label: label,
      isActive: activeTab == tab,
      onTap: () {
        _controller.setActiveTab(tab);
      },
    );
  }

  Widget _buildListRow(dynamic item) {
    String title = '';
    String subtitle = '';
    VoidCallback onView = () {};

    if (item is Curso) {
      title = item.name;
      subtitle = 'Código: ${item.codigo}';
      onView = () => context.go('/dashboard/cursos');
    } else if (item is Docente) {
      title = item.name;
      subtitle = item.email ?? 'Sem e-mail cadastrado';
      onView = () => context.go('/dashboard/docentes');
    } else if (item is Turma) {
      title = item.name;
      subtitle = 'Período: ${item.period?.displayName ?? 'Não informado'}';
      onView = () => context.go('/dashboard/turmas');
    } else if (item is Sala) {
      title = 'Sala ${item.name}';
      subtitle = 'Código: ${item.code ?? 'N/A'} • Capacidade: ${item.capacity ?? 0}';
      onView = () => context.go('/dashboard/salas');
    }

    return HomeListRow(title: title, subtitle: subtitle, onViewPressed: onView);
  }
}
