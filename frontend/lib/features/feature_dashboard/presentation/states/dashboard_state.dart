enum HomeTab { professores, turmas, cursos, salas }

/// State class for the Dashboard feature.
class DashboardState {
  const DashboardState({
    this.currentRoute = '/dashboard',
    this.activeTab = HomeTab.cursos,
    this.searchQuery = '',
    this.filteredItems = const [],
    this.teachersCount = 0,
    this.classesCount = 0,
    this.disciplinasCount = 0,
    this.roomsCount = 0,
    this.coursesCount = 0,
    this.totalWeeklyHours = 0,
  });

  final String currentRoute;
  final HomeTab activeTab;
  final String searchQuery;
  final List<dynamic> filteredItems;
  final int teachersCount;
  final int classesCount;
  final int disciplinasCount;
  final int roomsCount;
  final int coursesCount;
  final int totalWeeklyHours;

  DashboardState copyWith({
    String? currentRoute,
    HomeTab? activeTab,
    String? searchQuery,
    List<dynamic>? filteredItems,
    int? teachersCount,
    int? classesCount,
    int? disciplinasCount,
    int? roomsCount,
    int? coursesCount,
    int? totalWeeklyHours,
  }) {
    return DashboardState(
      currentRoute: currentRoute ?? this.currentRoute,
      activeTab: activeTab ?? this.activeTab,
      searchQuery: searchQuery ?? this.searchQuery,
      filteredItems: filteredItems ?? this.filteredItems,
      teachersCount: teachersCount ?? this.teachersCount,
      classesCount: classesCount ?? this.classesCount,
      disciplinasCount: disciplinasCount ?? this.disciplinasCount,
      roomsCount: roomsCount ?? this.roomsCount,
      coursesCount: coursesCount ?? this.coursesCount,
      totalWeeklyHours: totalWeeklyHours ?? this.totalWeeklyHours,
    );
  }
}
