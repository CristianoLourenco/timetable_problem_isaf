import 'package:ghorario/features/feature_horario/domain/entities/horario_slot.dart';
import 'package:ghorario/features/feature_horario/domain/entities/job_status.dart';
import 'package:ghorario/features/feature_horario/domain/entities/pendencia.dart';

const Object _sentinel = Object();

/// State class for the Horario feature.
class HorarioState {
  const HorarioState({
    this.slots = const <HorarioSlot>[],
    this.isLoading = false,
    this.isGenerating = false,
    this.errorMessage,
    this.currentJobId,
    this.jobStatus,
    this.elapsedSeconds = 0,
    this.isExporting = false,
    this.exportError,
    this.pendencias = const <Pendencia>[],
    this.isAlocando = false,
    this.alocacaoError,
    this.tempoMaximoMinutos,
    this.hasScopeJob,
    this.isCheckingScope = false,
  });

  final List<HorarioSlot> slots;
  final bool isLoading;
  final bool isGenerating;
  final String? errorMessage;
  final String? currentJobId;
  final JobStatus? jobStatus;
  final int elapsedSeconds;
  final bool isExporting;
  final String? exportError;
  final List<Pendencia> pendencias;
  final bool isAlocando;
  final String? alocacaoError;
  final int? tempoMaximoMinutos;
  // null = âmbito (ano/semestre selecionado) ainda não verificado; false =
  // verificado e não existe Job; true = existe Job para este âmbito.
  final bool? hasScopeJob;
  final bool isCheckingScope;

  HorarioState copyWith({
    List<HorarioSlot>? slots,
    bool? isLoading,
    bool? isGenerating,
    Object? errorMessage = _sentinel,
    Object? currentJobId = _sentinel,
    Object? jobStatus = _sentinel,
    int? elapsedSeconds,
    bool? isExporting,
    Object? exportError = _sentinel,
    List<Pendencia>? pendencias,
    bool? isAlocando,
    Object? alocacaoError = _sentinel,
    Object? tempoMaximoMinutos = _sentinel,
    Object? hasScopeJob = _sentinel,
    bool? isCheckingScope,
  }) {
    return HorarioState(
      slots: slots ?? this.slots,
      isLoading: isLoading ?? this.isLoading,
      isGenerating: isGenerating ?? this.isGenerating,
      errorMessage: errorMessage == _sentinel
          ? this.errorMessage
          : (errorMessage as String?),
      currentJobId: currentJobId == _sentinel
          ? this.currentJobId
          : (currentJobId as String?),
      jobStatus: jobStatus == _sentinel ? this.jobStatus : (jobStatus as JobStatus?),
      elapsedSeconds: elapsedSeconds ?? this.elapsedSeconds,
      isExporting: isExporting ?? this.isExporting,
      exportError: exportError == _sentinel ? this.exportError : (exportError as String?),
      pendencias: pendencias ?? this.pendencias,
      isAlocando: isAlocando ?? this.isAlocando,
      alocacaoError: alocacaoError == _sentinel
          ? this.alocacaoError
          : (alocacaoError as String?),
      tempoMaximoMinutos: tempoMaximoMinutos == _sentinel
          ? this.tempoMaximoMinutos
          : (tempoMaximoMinutos as int?),
      hasScopeJob: hasScopeJob == _sentinel ? this.hasScopeJob : (hasScopeJob as bool?),
      isCheckingScope: isCheckingScope ?? this.isCheckingScope,
    );
  }
}

