import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_dashboard/presentation/states/dashboard_state.dart';
import 'package:ghorario/features/feature_docentes/presentation/provider/docentes_provider.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/cursos_provider.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/turmas_provider.dart';
import 'package:ghorario/features/feature_disciplinas/presentation/provider/disciplinas_provider.dart';
import 'package:ghorario/features/feature_salas/presentation/provider/salas_provider.dart';

/// Local controller for managing the Dashboard UI and Home Screen data.
class DashboardController extends ValueNotifier<DashboardState> {
  DashboardController({
    required this.docentesProvider,
    required this.turmasProvider,
    required this.disciplinasProvider,
    required this.salasProvider,
    required this.cursosProvider,
  }) : super(const DashboardState());

  final DocentesProvider docentesProvider;
  final TurmasProvider turmasProvider;
  final DisciplinasProvider disciplinasProvider;
  final SalasProvider salasProvider;
  final CursosProvider cursosProvider;

  void init() {
    docentesProvider.loadDocentes();
    turmasProvider.loadTurmas();
    disciplinasProvider.loadDisciplinas();
    salasProvider.loadSalas();
    cursosProvider.loadCursos();

    docentesProvider.addListener(_onDataChanged);
    turmasProvider.addListener(_onDataChanged);
    disciplinasProvider.addListener(_onDataChanged);
    salasProvider.addListener(_onDataChanged);
    cursosProvider.addListener(_onDataChanged);

    _onDataChanged();
  }

  @override
  void dispose() {
    docentesProvider.removeListener(_onDataChanged);
    turmasProvider.removeListener(_onDataChanged);
    disciplinasProvider.removeListener(_onDataChanged);
    salasProvider.removeListener(_onDataChanged);
    cursosProvider.removeListener(_onDataChanged);
    super.dispose();
  }

  void _onDataChanged() {
    final teachersCount = docentesProvider.docentes.length;
    final classesCount = turmasProvider.turmas.length;
    final disciplinasCount = disciplinasProvider.disciplinas.length;
    final roomsCount = salasProvider.salas.length;
    final coursesCount = cursosProvider.cursos.length;

    final totalWeeklyHours = disciplinasProvider.disciplinas.fold<int>(
      0, (sum, item) => sum + (item.weeklyHours ?? 0)
    );

    value = value.copyWith(
      teachersCount: teachersCount,
      classesCount: classesCount,
      disciplinasCount: disciplinasCount,
      roomsCount: roomsCount,
      coursesCount: coursesCount,
      totalWeeklyHours: totalWeeklyHours,
      filteredItems: _getFilteredItems(value.activeTab, value.searchQuery),
    );
  }

  void setActiveTab(HomeTab tab) {
    value = value.copyWith(
      activeTab: tab,
      filteredItems: _getFilteredItems(tab, value.searchQuery),
    );
  }

  void setSearchQuery(String query) {
    value = value.copyWith(
      searchQuery: query,
      filteredItems: _getFilteredItems(value.activeTab, query),
    );
  }

  List<dynamic> _getFilteredItems(HomeTab tab, String query) {
    final lowerQuery = query.toLowerCase();
    switch (tab) {
      case HomeTab.cursos:
        final list = cursosProvider.cursos;
        if (lowerQuery.isEmpty) return list;
        return list.where((item) => item.name.toLowerCase().contains(lowerQuery)).toList();
      case HomeTab.professores:
        final list = docentesProvider.docentes;
        if (lowerQuery.isEmpty) return list;
        return list.where((item) => item.name.toLowerCase().contains(lowerQuery)).toList();
      case HomeTab.turmas:
        final list = turmasProvider.turmas;
        if (lowerQuery.isEmpty) return list;
        return list.where((item) => item.name.toLowerCase().contains(lowerQuery)).toList();
      case HomeTab.salas:
        final list = salasProvider.salas;
        if (lowerQuery.isEmpty) return list;
        return list.where((item) => item.name.toLowerCase().contains(lowerQuery)).toList();
    }
  }
}
