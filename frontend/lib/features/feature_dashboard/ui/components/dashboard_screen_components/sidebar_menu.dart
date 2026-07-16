import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:ghorario/core/constants/app_strings.dart';
import 'package:ghorario/features/feature_auth/domain/entities/user.dart';

/// Sidebar menu items definition.
class _MenuItem {
  const _MenuItem({
    required this.label,
    required this.icon,
    required this.route,
    this.gestorOnly = false,
  });

  final String label;
  final IconData icon;
  final String route;

  /// Ecrãs de gestão de dados mestre — o Professor não tem acesso a estes
  /// dados no backend (CRUD/importação Excel), por isso nem aparecem aqui.
  final bool gestorOnly;
}

/// The sidebar navigation for the dashboard.
///
/// Uses GoRouter location to determine the active item.
/// Filters items by [user]'s papel (RN11) — items marked `gestorOnly` are
/// hidden for a Professor. Also shows who is logged in above "Terminar
/// Sessão". Does NOT read Provider directly — [user] and [onLogout] are
/// passed in by the Screen.
class SidebarMenu extends StatelessWidget {
  const SidebarMenu({super.key, required this.onLogout, required this.user});

  final VoidCallback onLogout;
  final User? user;

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
      gestorOnly: true,
    ),
    _MenuItem(
      label: AppStrings.menuCursos,
      icon: Icons.school,
      route: '/dashboard/cursos',
      gestorOnly: true,
    ),
    _MenuItem(
      label: AppStrings.menuTurmas,
      icon: Icons.groups,
      route: '/dashboard/turmas',
      gestorOnly: true,
    ),
    _MenuItem(
      label: AppStrings.menuDisciplinas,
      icon: Icons.spellcheck_sharp,
      route: '/dashboard/disciplinas',
      gestorOnly: true,
    ),
    _MenuItem(
      label: AppStrings.menuSalas,
      icon: Icons.meeting_room,
      route: '/dashboard/salas',
      gestorOnly: true,
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
    final isProfessor = user?.isProfessor ?? false;
    final items = isProfessor
        ? _items.where((item) => !item.gestorOnly).toList()
        : _items;

    return Column(
      children: <Widget>[
        const Spacer(),
        Expanded(
          flex: 3,
          child: ListView.builder(
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = items[index];
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
        if (user != null)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 8),
            child: Row(
              children: <Widget>[
                const CircleAvatar(
                  radius: 16,
                  backgroundColor: Colors.white24,
                  child: Icon(Icons.person, size: 18, color: Colors.white),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      Text(
                        user!.nomeVisivel,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                          fontSize: 13,
                        ),
                      ),
                      Text(
                        user!.papel.rotulo,
                        style: const TextStyle(color: Colors.white54, fontSize: 11),
                      ),
                    ],
                  ),
                ),
              ],
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
