import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'package:ghorario/core/widgets/gradient_container.dart';
import 'package:ghorario/features/feature_auth/presentation/provider/auth_provider.dart';
import 'package:ghorario/features/feature_dashboard/ui/components/dashboard_screen_components/sidebar_menu.dart';

/// Dashboard shell screen — provides the persistent sidebar layout.
///
/// The [child] is injected by GoRouter's [ShellRoute] and changes
/// as the user navigates between features.
class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key, required this.child});

  final Widget child;

  Future<void> _handleLogout(BuildContext context) async {
    await context.read<AuthProvider>().logout();
    if (context.mounted) context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: <Widget>[
          Expanded(
            child: GradientContainer(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              child: SidebarMenu(onLogout: () => _handleLogout(context)),
            ),
          ),
          Expanded(
            flex: 4,
            child: child,
          ),
        ],
      ),
    );
  }
}
