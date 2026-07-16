/// Domain entity representing a room (sala) — mirrors the backend's `Sala`
/// exactly (`SalaRead`: id, codigo, nome, capacidade). There is no
/// "building/bloco" field backend-side — do not reintroduce one without a
/// matching backend field.
class Sala {
  const Sala({
    required this.id,
    required this.name,
    this.code,
    this.capacity,
  });

  final String id;
  final String name;
  final String? code;
  final int? capacity;
}
