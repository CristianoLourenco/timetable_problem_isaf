import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'package:ghorario/features/feature_auth/presentation/provider/auth_provider.dart';
import 'package:ghorario/features/feature_dashboard/ui/components/dashboard_screen_components/sidebar_menu.dart';

/// Dashboard shell screen — provides the persistent sidebar layout.
///
/// - Wide screens (≥ 720 px): [NavigationRail] sidebar + main content in a [Row].
/// - Narrow screens (< 720 px): [Scaffold] with [AppBar] + [Drawer].
///
/// The [child] is injected by GoRouter's [ShellRoute] and changes as the user
/// navigates between features.
class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key, required this.child});

  final Widget child;

  Future<void> _handleLogout(BuildContext context) async {
    await context.read<AuthProvider>().logout();
    if (context.mounted) context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().currentUser;

    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        final bool isWide = constraints.maxWidth >= 720;

        if (isWide) {
          // ── Wide layout: rail + content ────────────────────────────────
          return Scaffold(
            backgroundColor: Colors.transparent,
            body: Row(
              children: [
                SidebarMenu(
                  onLogout: () => _handleLogout(context),
                  user: user,
                ),
                Expanded(child: child),
              ],
            ),
          );
        } else {
          // ── Narrow layout: AppBar + Drawer ─────────────────────────────
          return Scaffold(
            appBar: AppBar(
              backgroundColor: const Color(0xFF00395E),
              foregroundColor: Colors.white,
              title: const Text(
                'G-Horário',
                style: TextStyle(
                  fontFamily: 'Poppins',
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              iconTheme: const IconThemeData(color: Colors.white),
            ),
            drawer: DrawerSidebarMenu(
              onLogout: () => _handleLogout(context),
              user: user,
            ),
            body: child,
          );
        }
      },
    );
  }
}
