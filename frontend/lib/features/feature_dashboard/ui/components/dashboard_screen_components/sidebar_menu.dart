import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'package:ghorario/core/constants/app_strings.dart';
import 'package:ghorario/core/themes/app_colors.dart';
import 'package:ghorario/features/feature_auth/domain/entities/user.dart';

// ---------------------------------------------------------------------------
// Menu item model
// ---------------------------------------------------------------------------

class _MenuItem {
  const _MenuItem({
    required this.label,
    required this.icon,
    required this.activeIcon,
    required this.route,
    this.gestorOnly = false,
  });

  final String label;
  final IconData icon;
  final IconData activeIcon;
  final String route;
  final bool gestorOnly;
}

// ---------------------------------------------------------------------------
// SidebarMenu — wide-screen NavigationRail variant
// ---------------------------------------------------------------------------

/// Collapsible sidebar using [NavigationRail].
///
/// - Expanded: shows icon + label
/// - Collapsed: shows only icon
/// - Collapse state is persisted in the Hive 'session' box
/// - User profile card is at the *top*, logout at the *bottom*
class SidebarMenu extends StatefulWidget {
  const SidebarMenu({super.key, required this.onLogout, required this.user});

  final VoidCallback onLogout;
  final User? user;

  static const List<_MenuItem> _items = [
    _MenuItem(
      label: AppStrings.menuHomeScreen,
      icon: Icons.dashboard_outlined,
      activeIcon: Icons.dashboard,
      route: '/dashboard',
    ),
    _MenuItem(
      label: AppStrings.menuDocentes,
      icon: Icons.people_outline,
      activeIcon: Icons.people,
      route: '/dashboard/docentes',
      gestorOnly: true,
    ),
    _MenuItem(
      label: AppStrings.menuCursos,
      icon: Icons.school_outlined,
      activeIcon: Icons.school,
      route: '/dashboard/cursos',
      gestorOnly: true,
    ),
    _MenuItem(
      label: AppStrings.menuTurmas,
      icon: Icons.groups_outlined,
      activeIcon: Icons.groups,
      route: '/dashboard/turmas',
      gestorOnly: true,
    ),
    _MenuItem(
      label: AppStrings.menuDisciplinas,
      icon: Icons.book_outlined,
      activeIcon: Icons.book,
      route: '/dashboard/disciplinas',
      gestorOnly: true,
    ),
    _MenuItem(
      label: AppStrings.menuSalas,
      icon: Icons.meeting_room_outlined,
      activeIcon: Icons.meeting_room,
      route: '/dashboard/salas',
      gestorOnly: true,
    ),
    _MenuItem(
      label: AppStrings.menuHorario,
      icon: Icons.schedule_outlined,
      activeIcon: Icons.schedule_rounded,
      route: '/dashboard/horario',
    ),
    _MenuItem(
      label: AppStrings.menuDisponibilidade,
      icon: Icons.event_available_outlined,
      activeIcon: Icons.event_available,
      route: '/dashboard/disponibilidade',
    ),
  ];

  static const String _hiveKey = 'sidebar_extended';

  @override
  State<SidebarMenu> createState() => _SidebarMenuState();
}

class _SidebarMenuState extends State<SidebarMenu> {
  bool _extended = true;

  @override
  void initState() {
    super.initState();
    final box = Hive.box<String>('session');
    final stored = box.get(SidebarMenu._hiveKey);
    _extended = stored != 'false';
  }

  void _toggleExtended() {
    setState(() => _extended = !_extended);
    Hive.box<String>('session').put(SidebarMenu._hiveKey, _extended.toString());
  }

  @override
  Widget build(BuildContext context) {
    final currentLocation = GoRouterState.of(context).uri.path;
    final isProfessor = widget.user?.isProfessor ?? false;
    final visibleItems = isProfessor
        ? SidebarMenu._items.where((i) => !i.gestorOnly).toList()
        : SidebarMenu._items;

    // Map visible items → NavigationRailDestination
    final destinations = visibleItems
        .map(
          (item) => NavigationRailDestination(
            icon: Icon(item.icon),
            selectedIcon: Icon(item.activeIcon),
            label: Text(item.label, style: const TextStyle(fontFamily: 'Poppins', fontSize: 13)),
            padding: const EdgeInsets.symmetric(vertical: 2),
          ),
        )
        .toList();

    // Determine selected index
    int selectedIndex = visibleItems.indexWhere((i) => currentLocation.startsWith(i.route));
    if (selectedIndex < 0) selectedIndex = 0;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      width: _extended ? 256 : 72,
      color: AppColors.blackBlue,
      child: Column(
        children: [
          // ── User profile header ──────────────────────────────────────────
          _buildProfileSection(),
          const Divider(color: Colors.white12, height: 1, thickness: 1),

          // ── NavigationRail ───────────────────────────────────────────────
          Expanded(
            child: NavigationRail(
              extended: _extended,
              backgroundColor: AppColors.blackBlue,
              selectedIndex: selectedIndex,
              onDestinationSelected: (index) {
                context.go(visibleItems[index].route);
              },
              selectedIconTheme: const IconThemeData(color: Colors.white),
              unselectedIconTheme: const IconThemeData(color: Colors.white54),
              selectedLabelTextStyle: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w600,
                fontFamily: 'Poppins',
              ),
              unselectedLabelTextStyle: const TextStyle(
                color: Colors.white54,
                fontFamily: 'Poppins',
              ),
              indicatorColor: Colors.white24,
              destinations: destinations,
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: _buildLogoutTile(),
          ),

          // ── Toggle collapse button ───────────────────────────────────────
          _buildToggleButton(),
        ],
      ),
    );
  }

  Widget _buildProfileSection() {
    final user = widget.user;
    if (!_extended) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: CircleAvatar(
          radius: 18,
          backgroundColor: Colors.white24,
          child: Text(
            user?.nomeVisivel.isNotEmpty == true
                ? user!.nomeVisivel[0].toUpperCase()
                : 'U',
            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
        ),
      );
    }
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 20, 16, 12),
      child: Row(
        children: [
          CircleAvatar(
            radius: 20,
            backgroundColor: Colors.white24,
            child: Text(
              user?.nomeVisivel.isNotEmpty == true
                  ? user!.nomeVisivel[0].toUpperCase()
                  : 'U',
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  user?.nomeVisivel ?? 'Utilizador',
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                    fontFamily: 'Poppins',
                  ),
                ),
                Text(
                  user?.papel.rotulo ?? '',
                  style: const TextStyle(color: Colors.white54, fontSize: 11, fontFamily: 'Poppins'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLogoutTile() {
    if (!_extended) {
      return IconButton(
        icon: const Icon(Icons.logout, color: Colors.white54),
        tooltip: 'Terminar Sessão',
        onPressed: widget.onLogout,
      );
    }
    return TextButton.icon(
      onPressed: widget.onLogout,
      icon: const Icon(Icons.logout, color: Colors.white54, size: 18),
      label: const Text(
        'Terminar Sessão',
        style: TextStyle(color: Colors.white54, fontFamily: 'Poppins', fontSize: 13),
      ),
    );
  }

  Widget _buildToggleButton() {
    return InkWell(
      onTap: _toggleExtended,
      child: Container(
        color: Colors.white10,
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 10),
        child: Icon(
          _extended ? Icons.chevron_left : Icons.chevron_right,
          color: Colors.white54,
          size: 20,
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// DrawerSidebarMenu — narrow-screen Drawer variant
// ---------------------------------------------------------------------------

/// Sidebar content rendered inside a [Drawer] for narrow screens.
class DrawerSidebarMenu extends StatelessWidget {
  const DrawerSidebarMenu({super.key, required this.onLogout, required this.user});

  final VoidCallback onLogout;
  final User? user;

  @override
  Widget build(BuildContext context) {
    final currentLocation = GoRouterState.of(context).uri.path;
    final isProfessor = user?.isProfessor ?? false;
    final visibleItems = isProfessor
        ? SidebarMenu._items.where((i) => !i.gestorOnly).toList()
        : SidebarMenu._items;

    return Drawer(
      backgroundColor: AppColors.blackBlue,
      child: Column(
        children: [
          // User profile header
          Container(
            color: AppColors.blackBlue,
            padding: const EdgeInsets.fromLTRB(20, 48, 20, 16),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 22,
                  backgroundColor: Colors.white24,
                  child: Text(
                    user?.nomeVisivel.isNotEmpty == true
                        ? user!.nomeVisivel[0].toUpperCase()
                        : 'U',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        user?.nomeVisivel ?? 'Utilizador',
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                          fontFamily: 'Poppins',
                        ),
                      ),
                      Text(
                        user?.papel.rotulo ?? '',
                        style: const TextStyle(color: Colors.white54, fontSize: 12, fontFamily: 'Poppins'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const Divider(color: Colors.white12, height: 1, thickness: 1),
          // Nav items
          Expanded(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                for (final item in visibleItems)
                  _DrawerItem(
                    item: item,
                    isActive: currentLocation.startsWith(item.route),
                    onTap: () {
                      Navigator.of(context).pop();
                      context.go(item.route);
                    },
                  ),
              ],
            ),
          ),
          const Divider(color: Colors.white12, height: 1),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.white54),
            title: const Text(
              'Terminar Sessão',
              style: TextStyle(color: Colors.white54, fontFamily: 'Poppins'),
            ),
            onTap: onLogout,
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }
}

class _DrawerItem extends StatelessWidget {
  const _DrawerItem({required this.item, required this.isActive, required this.onTap});

  final _MenuItem item;
  final bool isActive;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(
        isActive ? item.activeIcon : item.icon,
        color: isActive ? Colors.white : Colors.white54,
      ),
      title: Text(
        item.label,
        style: TextStyle(
          color: isActive ? Colors.white : Colors.white54,
          fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
          fontFamily: 'Poppins',
        ),
      ),
      tileColor: isActive ? Colors.white12 : Colors.transparent,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 2),
      onTap: onTap,
    );
  }
}
