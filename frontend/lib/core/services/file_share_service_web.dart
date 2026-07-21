import 'dart:html' as html;
import 'dart:typed_data';

class FileShareService {
  const FileShareService();

  Future<void> saveAndShareBytes(Uint8List bytes, String filename) async {
    final blob = html.Blob([bytes]);
    final url = html.Url.createObjectUrlFromBlob(blob);
    final anchor = html.AnchorElement(href: url)
      ..setAttribute("download", filename)
      ..click();
    html.Url.revokeObjectUrl(url);
  }
}
