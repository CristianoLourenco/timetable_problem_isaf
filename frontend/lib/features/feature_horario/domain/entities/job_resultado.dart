import 'package:ghorario/features/feature_horario/domain/entities/job_status.dart';

/// Result of `GET /jobs/{job_id}` — status plus the human-readable diagnostic
/// the backend always fills in for INFEASIBLE (RF13/RNF03: never a bare 500,
/// always a structured explanation of why no schedule could be generated).
class JobResultado {
  const JobResultado({required this.status, this.diagnostico});

  final JobStatus status;
  final String? diagnostico;
}
