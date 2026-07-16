/// Domain entity representing a Dashboard navigation item.
class DashboardItem {
  const DashboardItem({
    required this.label,
    required this.route,
  });

  final String label;
  final String route;
}
