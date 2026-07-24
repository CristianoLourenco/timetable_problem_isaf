/// Saves downloaded bytes (PDF/zip) and opens the native share/save sheet —
/// kept out of Screens/Components per the project's "no business logic in
/// UI files" rule.
///
/// Bug real (2026-07-24): este ficheiro continha a implementação mobile
/// (`dart:io` + `share_plus`) diretamente, sem nenhum export condicional —
/// `file_share_service_web.dart` existia mas nunca era escolhido por ninguém.
/// Em `flutter run -d chrome`, `dart:io` é stubado pelo compilador web e
/// `saveAndShareBytes` nunca resolvia nem lançava de forma visível: a
/// exportação ficava presa no loading indefinidamente. Conditional export
/// corrige isto — a versão certa é escolhida em tempo de compilação conforme
/// a plataforma.
export 'file_share_service_stub.dart' if (dart.library.io) 'file_share_service_mobile.dart' if (dart.library.html) 'file_share_service_web.dart';
