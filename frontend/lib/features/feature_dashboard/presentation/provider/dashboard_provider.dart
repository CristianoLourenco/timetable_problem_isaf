import 'package:flutter/foundation.dart';

/// Provider maintaining the global dashboard layout status.
class DashboardProvider extends ChangeNotifier {
  String _currentRoute = '/dashboard';
  String get currentRoute => _currentRoute;

  void changeRoute(String route) {
    if (_currentRoute != route) {
      _currentRoute = route;
      notifyListeners();
    }
  }
}
