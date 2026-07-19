import 'package:flutter/foundation.dart';
import 'package:ghorario/core/services/file_share_service.dart';
import 'package:ghorario/features/feature_horario/domain/entities/horario_slot.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_status.dart';
import 'package:ghorario/features/feature_horario/domain/entities/pendencia.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/check_job_status_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/exportar_horario_turma_pdf_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/exportar_todos_horarios_pdf_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/gerar_horario_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_horario_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_pendencias_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_professores_qualificados_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_slots_vagos_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/criar_alocacao_manual_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/mover_alocacao_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/remover_alocacao_usecase.dart';

export 'package:ghorario/features/feature_horario/domain/usecase/get_horario_usecase.dart' show GetHorarioParams;

/// Provider for global horario state.
class HorarioProvider extends ChangeNotifier {
  HorarioProvider({
    required GerarHorarioUseCase gerarHorarioUseCase,
    required GetHorarioUseCase getHorarioUseCase,
    required CheckJobStatusUseCase checkJobStatusUseCase,
    required ExportarHorarioTurmaPdfUseCase exportarHorarioTurmaPdfUseCase,
    required ExportarTodosHorariosPdfUseCase exportarTodosHorariosPdfUseCase,
    required GetPendenciasUseCase getPendenciasUseCase,
    required GetProfessoresQualificadosUseCase getProfessoresQualificadosUseCase,
    required GetSlotsVagosUseCase getSlotsVagosUseCase,
    required CriarAlocacaoManualUseCase criarAlocacaoManualUseCase,
    required MoverAlocacaoUseCase moverAlocacaoUseCase,
    required RemoverAlocacaoUseCase removerAlocacaoUseCase,
  })  : _gerarHorarioUseCase = gerarHorarioUseCase,
        _getHorarioUseCase = getHorarioUseCase,
        _checkJobStatusUseCase = checkJobStatusUseCase,
        _exportarHorarioTurmaPdfUseCase = exportarHorarioTurmaPdfUseCase,
        _exportarTodosHorariosPdfUseCase = exportarTodosHorariosPdfUseCase,
        _getPendenciasUseCase = getPendenciasUseCase,
        _criarAlocacaoManualUseCase = criarAlocacaoManualUseCase,
        _moverAlocacaoUseCase = moverAlocacaoUseCase,
        _removerAlocacaoUseCase = removerAlocacaoUseCase;

  final GerarHorarioUseCase _gerarHorarioUseCase;
  final GetHorarioUseCase _getHorarioUseCase;
  final CheckJobStatusUseCase _checkJobStatusUseCase;
  final ExportarHorarioTurmaPdfUseCase _exportarHorarioTurmaPdfUseCase;
  final ExportarTodosHorariosPdfUseCase _exportarTodosHorariosPdfUseCase;
  final GetPendenciasUseCase _getPendenciasUseCase;
  final CriarAlocacaoManualUseCase _criarAlocacaoManualUseCase;
  final MoverAlocacaoUseCase _moverAlocacaoUseCase;
  final RemoverAlocacaoUseCase _removerAlocacaoUseCase;

  static const _pollInterval = Duration(seconds: 3);
  // ~20min — o backend escalona automaticamente 2→5→10 min por tentativa
  // (job_runner.ESCALONAMENTO_TEMPO_MINUTOS) até deixar de dar timeout; no pior
  // caso (todas as 3 tentativas esgotam) isso já soma 17min sozinho, mais a
  // bisecção de diagnóstico por pendência (app/solver/diagnostico.py). Um
  // timeout de polling mais curto do que isto faz a UI desistir e mostrar erro
  // mesmo quando o backend ainda está genuinamente a trabalhar e vai terminar
  // com sucesso pouco depois — bug real encontrado em 2026-07-19.
  static const _maxPollAttempts = 400;

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

  JobStatus? _jobStatus;
  JobStatus? get jobStatus => _jobStatus;

  int _elapsedSeconds = 0;
  int get elapsedSeconds => _elapsedSeconds;

  bool _isExporting = false;
  bool get isExporting => _isExporting;

  String? _exportError;
  String? get exportError => _exportError;

  List<Pendencia> _pendencias = const <Pendencia>[];
  List<Pendencia> get pendencias => _pendencias;

  bool _isAlocando = false;
  bool get isAlocando => _isAlocando;

  String? _alocacaoError;
  String? get alocacaoError => _alocacaoError;

  int? _tempoMaximoMinutos;
  int? get tempoMaximoMinutos => _tempoMaximoMinutos;

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
    _jobStatus = JobStatus.pending;
    _elapsedSeconds = 0;
    _tempoMaximoMinutos = null;
    _pendencias = const <Pendencia>[];
    notifyListeners();

    final triggerResult = await _gerarHorarioUseCase(
      GerarHorarioParams(anoLetivo: anoLetivo, semestre: semestre),
    );
    if (!triggerResult.success || triggerResult.data == null) {
      _errorMessage = triggerResult.message;
      _isGenerating = false;
      _jobStatus = null;
      notifyListeners();
      return;
    }

    _currentJobId = triggerResult.data;
    notifyListeners();

    JobStatus status = JobStatus.pending;
    String? diagnostico;
    int? tempoMax;
    for (var attempt = 0; attempt < _maxPollAttempts; attempt++) {
      final statusResult = await _checkJobStatusUseCase(_currentJobId!);
      if (!statusResult.success || statusResult.data == null) {
        _errorMessage = statusResult.message;
        _isGenerating = false;
        _jobStatus = null;
        notifyListeners();
        return;
      }
      status = statusResult.data!.status;
      diagnostico = statusResult.data!.diagnostico;
      tempoMax = statusResult.data!.tempoMaximoMinutos;
      
      _jobStatus = status;
      _elapsedSeconds = (attempt + 1) * _pollInterval.inSeconds;
      notifyListeners();
      if (status == JobStatus.done || status == JobStatus.infeasible) break;
      await Future<void>.delayed(_pollInterval);
    }

    _tempoMaximoMinutos = tempoMax;

    if (status == JobStatus.infeasible) {
      _errorMessage = diagnostico ?? 'Não foi possível gerar um horário sem conflitos com os dados atuais.';
      _isGenerating = false;
      _jobStatus = null;
      // Mesmo com status INFEASIBLE, podemos ter pendências e alocações parciais a mostrar
      await loadPendencias(_currentJobId!);
      await fetchTimetableByTurma(turmaId);
      return;
    }
    if (status != JobStatus.done) {
      _errorMessage = 'A geração está a demorar mais do que o esperado. Tente consultar novamente dentro de momentos.';
      _isGenerating = false;
      _jobStatus = null;
      notifyListeners();
      return;
    }

    _isGenerating = false;
    _jobStatus = null;
    await loadPendencias(_currentJobId!);
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
      _slots = result.data!.slots;
      _currentJobId = result.data!.jobId;
      if (_currentJobId != null && _currentJobId!.isNotEmpty) {
        // Carrega pendências do Job correspondente ao horário carregado
        await loadPendencias(_currentJobId!);
        // Busca também os detalhes do Job para recuperar o tempoMaximoMinutos
        final jobResult = await _checkJobStatusUseCase(_currentJobId!);
        if (jobResult.success && jobResult.data != null) {
          _tempoMaximoMinutos = jobResult.data!.tempoMaximoMinutos;
        }
      }
    } else {
      _errorMessage = result.message;
    }

    _isLoading = false;
    notifyListeners();
  }

  Future<void> loadPendencias(String jobId) async {
    final result = await _getPendenciasUseCase(jobId);
    if (result.success && result.data != null) {
      _pendencias = result.data!;
      notifyListeners();
    }
  }

  /// Creates a manual allocation. Returns true on success.
  Future<bool> criarAlocacaoManual({
    required String jobId,
    required String turmaId,
    required String disciplinaId,
    required String professorId,
    required String salaId,
    required String diaSemana,
    required String turno,
    required List<int> periodos,
  }) async {
    _isAlocando = true;
    _alocacaoError = null;
    notifyListeners();

    final result = await _criarAlocacaoManualUseCase(
      CriarAlocacaoManualParams(
        jobId: jobId,
        turmaId: turmaId,
        disciplinaId: disciplinaId,
        professorId: professorId,
        salaId: salaId,
        diaSemana: diaSemana,
        turno: turno,
        periodos: periodos,
      ),
    );

    _isAlocando = false;
    if (result.success) {
      _alocacaoError = null;
      notifyListeners();
      return true;
    } else {
      _alocacaoError = result.message;
      notifyListeners();
      return false;
    }
  }

  /// Moves an existing allocation. Returns true on success.
  Future<bool> moverAlocacao(int alocacaoId, String diaSemana, int periodo) async {
    _isAlocando = true;
    _alocacaoError = null;
    notifyListeners();

    final result = await _moverAlocacaoUseCase(
      MoverAlocacaoParams(
        alocacaoId: alocacaoId,
        diaSemana: diaSemana,
        periodo: periodo,
      ),
    );

    _isAlocando = false;
    if (result.success) {
      _alocacaoError = null;
      notifyListeners();
      return true;
    } else {
      _alocacaoError = result.message;
      notifyListeners();
      return false;
    }
  }

  /// Removes an allocation. Returns true on success.
  Future<bool> removerAlocacao(int alocacaoId) async {
    _isAlocando = true;
    _alocacaoError = null;
    notifyListeners();

    final result = await _removerAlocacaoUseCase(alocacaoId);

    _isAlocando = false;
    if (result.success) {
      _alocacaoError = null;
      notifyListeners();
      return true;
    } else {
      _alocacaoError = result.message;
      notifyListeners();
      return false;
    }
  }

  /// Downloads the PDF (RF11) of [turmaId]'s current timetable and opens the
  /// native share/save sheet.
  Future<void> exportarHorarioTurmaPdf(String turmaId, FileShareService fileShareService) async {
    _isExporting = true;
    _exportError = null;
    notifyListeners();

    final result = await _exportarHorarioTurmaPdfUseCase(turmaId);
    if (result.success && result.data != null) {
      await fileShareService.saveAndShareBytes(result.data!, 'horario_turma_$turmaId.pdf');
    } else {
      _exportError = result.message;
    }

    _isExporting = false;
    notifyListeners();
  }

  /// Downloads a .zip with one PDF per turma covered by the current
  /// [_currentJobId] and opens the native share/save sheet.
  Future<void> exportarTodosHorarios(FileShareService fileShareService) async {
    final jobId = _currentJobId;
    if (jobId == null) {
      _exportError = 'Gere ou consulte um horário primeiro para poder exportar.';
      notifyListeners();
      return;
    }

    _isExporting = true;
    _exportError = null;
    notifyListeners();

    final result = await _exportarTodosHorariosPdfUseCase(jobId);
    if (result.success && result.data != null) {
      await fileShareService.saveAndShareBytes(result.data!, 'horarios_$jobId.zip');
    } else {
      _exportError = result.message;
    }

    _isExporting = false;
    notifyListeners();
  }
}
