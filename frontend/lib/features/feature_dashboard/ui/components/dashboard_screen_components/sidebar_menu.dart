import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:ghorario/core/constants/app_strings.dart';

/// Sidebar menu items definition.
class _MenuItem {
  const _MenuItem({
    required this.label,
    required this.icon,
    required this.route,
  });

  final String label;
  final IconData icon;
  final String route;
}

/// The sidebar navigation for the dashboard.
///
/// Uses GoRouter location to determine the active item.
/// Does NOT access any Provider directly — purely declarative; logout is
/// passed in as a callback from the Screen.
class SidebarMenu extends StatelessWidget {
  const SidebarMenu({super.key, required this.onLogout});

  final VoidCallback onLogout;

  static const List<_MenuItem> _items = [
    _MenuItem(
      label: AppStrings.menuHomeScreen,
      icon: Icons.dashboard_outlined,
      route: '/dashboard',
    ),
    _MenuItem(
      label: AppStrings.menuDocentes,
      icon: Icons.people,
      route: '/dashboard/docentes',
    ),
    _MenuItem(
      label: AppStrings.menuCursos,
      icon: Icons.school,
      route: '/dashboard/cursos',
    ),
    _MenuItem(
      label: AppStrings.menuTurmas,
      icon: Icons.groups,
      route: '/dashboard/turmas',
    ),
    _MenuItem(
      label: AppStrings.menuDisciplinas,
      icon: Icons.spellcheck_sharp,
      route: '/dashboard/disciplinas',
    ),
    _MenuItem(
      label: AppStrings.menuSalas,
      icon: Icons.meeting_room,
      route: '/dashboard/salas',
    ),
    _MenuItem(
      label: AppStrings.menuHorario,
      icon: Icons.schedule_rounded,
      route: '/dashboard/horario',
    ),
    _MenuItem(
      label: AppStrings.menuDisponibilidade,
      icon: Icons.event_available,
      route: '/dashboard/disponibilidade',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final currentLocation = GoRouterState.of(context).uri.path;

    return Column(
      children: <Widget>[
        const Spacer(),
        Expanded(
          flex: 3,
          child: ListView.builder(
            itemCount: _items.length,
            itemBuilder: (context, index) {
              final item = _items[index];
              final isActive = currentLocation == item.route;

              return Padding(
                padding: const EdgeInsets.only(top: 5),
                child: ListTile(
                  contentPadding: const EdgeInsets.only(left: 30),
                  title: Text(
                    item.label,
                    textScaler: const TextScaler.linear(1.35),
                    style: TextStyle(
                      fontWeight: isActive ? FontWeight.w500 : FontWeight.w100,
                      color: isActive ? Colors.white : Colors.white54,
                    ),
                  ),
                  leading: Icon(
                    item.icon,
                    color: isActive ? Colors.white : Colors.white54,
                  ),
                  onTap: () => context.go(item.route),
                ),
              );
            },
          ),
        ),
        Padding(
          padding: const EdgeInsets.only(left: 30, bottom: 16),
          child: ListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text(
              'Terminar Sessão',
              textScaler: TextScaler.linear(1.35),
              style: TextStyle(fontWeight: FontWeight.w100, color: Colors.white54),
            ),
            leading: const Icon(Icons.logout, color: Colors.white54),
            onTap: onLogout,
          ),
        ),
      ],
    );
  }
}
