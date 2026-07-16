import 'package:ghorario/core/enums/dia_semana.dart';
import 'package:ghorario/core/enums/turno.dart';

/// Identifies a teaching period without its hours — mirrors the backend's
/// `TempoChave` schema. Used as the unit of selection for the professor's
/// weekly availability grid (RF05) and as a lookup key against [Tempo].
/// Value-equal so it works as a `Set`/`Map` key.
class TempoChave {
  const TempoChave({required this.diaSemana, required this.turno, required this.periodo});

  final DiaSemana diaSemana;
  final Turno turno;
  final int periodo;

  @override
  bool operator ==(Object other) =>
      other is TempoChave && other.diaSemana == diaSemana && other.turno == turno && other.periodo == periodo;

  @override
  int get hashCode => Object.hash(diaSemana, turno, periodo);
}
