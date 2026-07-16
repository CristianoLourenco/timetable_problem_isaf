import 'package:ghorario/core/enums/dia_semana.dart';
import 'package:ghorario/core/enums/turno.dart';

/// Domain entity mirroring the backend's `TempoRead` (RF05) — a single
/// teaching period, identified by (diaSemana, turno, periodo). There is no
/// `Slot` table on the backend: this grid is calculated at runtime from
/// `core/config.py`, never persisted (see backend/app/core/calendario.py).
/// `periodo` restarts at 1 in each turno — it is only meaningful together
/// with `turno`.
class Tempo {
  const Tempo({
    required this.diaSemana,
    required this.turno,
    required this.periodo,
    required this.horaInicio,
    required this.horaFim,
  });

  final DiaSemana diaSemana;
  final Turno turno;
  final int periodo;
  final String horaInicio;
  final String horaFim;
}
