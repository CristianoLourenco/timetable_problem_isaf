import 'dart:io';
import 'dart:typed_data';

import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

/// Saves downloaded bytes (PDF/zip) to a temp file and opens the native
/// share/save sheet — kept out of Screens/Components per the project's
/// "no business logic in UI files" rule.
class FileShareService {
  const FileShareService();

  Future<void> saveAndShareBytes(Uint8List bytes, String filename) async {
    final directory = await getTemporaryDirectory();
    final file = File('${directory.path}/$filename');
    await file.writeAsBytes(bytes, flush: true);
    await Share.shareXFiles([XFile(file.path)], fileNameOverrides: [filename]);
  }
}
