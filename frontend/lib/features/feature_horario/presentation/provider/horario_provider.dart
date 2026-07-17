import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_slot.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_status.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/check_job_status_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/gerar_horario_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_horario_usecase.dart';

export 'package:ghorario/features/feature_horario/domain/usecase/get_horario_usecase.dart' show GetHorarioParams;

/// Provider for global horario state.
class HorarioProvider extends ChangeNotifier {
  HorarioProvider({
    required GerarHorarioUseCase gerarHorarioUseCase,
    required GetHorarioUseCase getHorarioUseCase,
    required CheckJobStatusUseCase checkJobStatusUseCase,
  })  : _gerarHorarioUseCase = gerarHorarioUseCase,
        _getHorarioUseCase = getHorarioUseCase,
        _checkJobStatusUseCase = checkJobStatusUseCase;

  final GerarHorarioUseCase _gerarHorarioUseCase;
  final GetHorarioUseCase _getHorarioUseCase;
  final CheckJobStatusUseCase _checkJobStatusUseCase;

  static const _pollInterval = Duration(seconds: 2);
  static const _maxPollAttempts = 60; // ~2min — backend caps the solver at 60s (config.py)

  List<HorarioSlot> _slots = const <HorarioSlot>[];
  List<HorarioSlot> get slots => _slots;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  bool _isGenerating = false;
  bool get isGenerating => _isGenerating;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  String? _currentJobId;
  String? get currentJobId => _currentJobId;

  /// Triggers the solver run for every turma of [anoLetivo]/[semestre] (RF09
  /// — sempre o horário completo desse âmbito, de uma vez), polls
  /// `GET /jobs/{job_id}` until it leaves PENDING/RUNNING, then — if DONE —
  /// fetches [turmaId]'s resulting grid. INFEASIBLE surfaces the backend's
  /// diagnostic (RF13/RNF03), never a bare failure.
  Future<void> generateTimetable(
    String turmaId, {
    required int anoLetivo,
    required String semestre,
  }) async {
    _isGenerating = true;
    _errorMessage = null;
    _slots = const <HorarioSlot>[];
    notifyListeners();

    final triggerResult = await _gerarHorarioUseCase(
      GerarHorarioParams(anoLetivo: anoLetivo, semestre: semestre),
    );
    if (!triggerResult.success || triggerResult.data == null) {
      _errorMessage = triggerResult.message;
      _isGenerating = false;
      notifyListeners();
      return;
    }

    _currentJobId = triggerResult.data;
    notifyListeners();

    JobStatus status = JobStatus.pending;
    String? diagnostico;
    for (var attempt = 0; attempt < _maxPollAttempts; attempt++) {
      final statusResult = await _checkJobStatusUseCase(_currentJobId!);
      if (!statusResult.success || statusResult.data == null) {
        _errorMessage = statusResult.message;
        _isGenerating = false;
        notifyListeners();
        return;
      }
      status = statusResult.data!.status;
      diagnostico = statusResult.data!.diagnostico;
      if (status == JobStatus.done || status == JobStatus.infeasible) break;
      await Future<void>.delayed(_pollInterval);
    }

    if (status == JobStatus.infeasible) {
      _errorMessage = diagnostico ?? 'Não foi possível gerar um horário sem conflitos com os dados atuais.';
      _isGenerating = false;
      notifyListeners();
      return;
    }
    if (status != JobStatus.done) {
      _errorMessage = 'A geração está a demorar mais do que o esperado. Tente consultar novamente dentro de momentos.';
      _isGenerating = false;
      notifyListeners();
      return;
    }

    _isGenerating = false;
    await fetchTimetableByTurma(turmaId);
  }

  Future<void> fetchTimetableByTurma(String turmaId) async {
    await _fetchTimetable(GetHorarioParams.turma(turmaId));
  }

  Future<void> fetchTimetableByProfessor(String professorId) async {
    await _fetchTimetable(GetHorarioParams.professor(professorId));
  }

  Future<void> _fetchTimetable(GetHorarioParams params) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final result = await _getHorarioUseCase(params);
    if (result.success && result.data != null) {
      _slots = result.data!;
    } else {
      _errorMessage = result.message;
    }

    _isLoading = false;
    notifyListeners();
  }
}
