/// Mirrors the backend's `JobStatus` (RF09/RF10) returned by `GET /jobs/{job_id}`.
enum JobStatus {
  pending,
  running,
  done,
  infeasible;

  static JobStatus fromApi(String? value) {
    return JobStatus.values.firstWhere(
      (s) => s.apiValue == value,
      orElse: () => JobStatus.pending,
    );
  }

  String get apiValue => name.toUpperCase();
}
