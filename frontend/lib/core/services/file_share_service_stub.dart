import 'dart:typed_data';

class FileShareService {
  const FileShareService();

  Future<void> saveAndShareBytes(Uint8List bytes, String filename) async {
    throw UnsupportedError('Plataforma não suportada');
  }
}
