import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:ghorario/features/feature_auth/ui/screens/login_screen.dart';
import 'package:ghorario/features/feature_auth/ui/screens/recuperar_password_screen.dart';
import 'package:ghorario/features/feature_auth/ui/screens/registo_professor_screen.dart';
import 'package:ghorario/features/feature_dashboard/ui/screens/dashboard_screen.dart';
import 'package:ghorario/features/feature_dashboard/ui/screens/home_screen.dart';
import 'package:ghorario/features/feature_docentes/ui/screens/docentes_screen.dart';
import 'package:ghorario/features/feature_turmas/ui/screens/turmas_screen.dart';
import 'package:ghorario/features/feature_turmas/ui/screens/cursos_screen.dart';
import 'package:ghorario/features/feature_disciplinas/ui/screens/disciplinas_screen.dart';
import 'package:ghorario/features/feature_disponibilidade/ui/screens/disponibilidade_screen.dart';
import 'package:ghorario/features/feature_salas/ui/screens/salas_screen.dart';
import 'package:ghorario/features/feature_horario/ui/screens/horario_screen.dart';

/// Application route paths.
class AppRoutes {
  AppRoutes._();

  static const String login = '/login';
  static const String registoProfessor = '/registo-professor';
  static const String recuperarPassword = '/recuperar-password';
  static const String dashboard = '/dashboard';
  static const String docentes = 'docentes';
  static const String turmas = 'turmas';
  static const String cursos = 'cursos';
  static const String disciplinas = 'disciplinas';
  static const String salas = 'salas';
  static const String horario = 'horario';
  static const String disponibilidade = 'disponibilidade';
}

/// Global navigator key used by GoRouter.
final GlobalKey<NavigatorState> _rootNavigatorKey = GlobalKey<NavigatorState>();

/// GoRouter configuration for the application.
///
/// Uses a [ShellRoute] for the dashboard so the sidebar persists
/// while the content area navigates between features.
final GoRouter appRouter = GoRouter(
  navigatorKey: _rootNavigatorKey,
  initialLocation: AppRoutes.login,
  routes: [
    GoRoute(
      path: AppRoutes.login,
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: AppRoutes.registoProfessor,
      builder: (context, state) => const RegistoProfessorScreen(),
    ),
    GoRoute(
      path: AppRoutes.recuperarPassword,
      builder: (context, state) => const RecuperarPasswordScreen(),
    ),
    ShellRoute(
      builder: (context, state, child) => DashboardScreen(child: child),
      routes: [
        GoRoute(
          path: AppRoutes.dashboard,
          builder: (context, state) => const HomeScreen(),
          routes: [
            GoRoute(
              path: AppRoutes.docentes,
              builder: (context, state) => const DocentesScreen(),
            ),
            GoRoute(
              path: AppRoutes.turmas,
              builder: (context, state) => const TurmasScreen(),
            ),
            GoRoute(
              path: AppRoutes.cursos,
              builder: (context, state) => const CursosScreen(),
            ),
            GoRoute(
              path: AppRoutes.disciplinas,
              builder: (context, state) => const DisciplinasScreen(),
            ),
            GoRoute(
              path: AppRoutes.salas,
              builder: (context, state) => const SalasScreen(),
            ),
            GoRoute(
              path: AppRoutes.horario,
              builder: (context, state) => const HorarioScreen(),
            ),
            GoRoute(
              path: AppRoutes.disponibilidade,
              builder: (context, state) => const DisponibilidadeScreen(),
            ),
          ],
        ),
      ],
    ),
  ],
);
