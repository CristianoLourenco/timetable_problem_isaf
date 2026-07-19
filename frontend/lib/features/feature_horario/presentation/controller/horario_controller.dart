import 'package:flutter/foundation.dart';
import 'package:ghorario/core/services/file_share_service.dart';
import 'package:ghorario/features/feature_horario/presentation/provider/horario_provider.dart';
import 'package:ghorario/features/feature_horario/presentation/states/horario_state.dart';

/// Local controller for the Horario UI.
class HorarioController extends ValueNotifier<HorarioState> {
  HorarioController({
    required HorarioProvider provider,
  })  : _provider = provider,
        super(const HorarioState());

  final HorarioProvider _provider;

  void init() {
    _hydrate();
    _provider.addListener(_onProviderChanged);
  }

  @override
  void dispose() {
    _provider.removeListener(_onProviderChanged);
    super.dispose();
  }

  void _hydrate() {
    value = value.copyWith(
      slots: _provider.slots,
      isLoading: _provider.isLoading,
      isGenerating: _provider.isGenerating,
      errorMessage: _provider.errorMessage,
      currentJobId: _provider.currentJobId,
      jobStatus: _provider.jobStatus,
      elapsedSeconds: _provider.elapsedSeconds,
      isExporting: _provider.isExporting,
      exportError: _provider.exportError,
      pendencias: _provider.pendencias,
      isAlocando: _provider.isAlocando,
      alocacaoError: _provider.alocacaoError,
      tempoMaximoMinutos: _provider.tempoMaximoMinutos,
      hasScopeJob: _provider.hasScopeJob,
      isCheckingScope: _provider.isCheckingScope,
    );
  }

  void _onProviderChanged() {
    value = value.copyWith(
      slots: _provider.slots,
      isLoading: _provider.isLoading,
      isGenerating: _provider.isGenerating,
      errorMessage: _provider.errorMessage,
      currentJobId: _provider.currentJobId,
      jobStatus: _provider.jobStatus,
      elapsedSeconds: _provider.elapsedSeconds,
      isExporting: _provider.isExporting,
      exportError: _provider.exportError,
      pendencias: _provider.pendencias,
      isAlocando: _provider.isAlocando,
      alocacaoError: _provider.alocacaoError,
      tempoMaximoMinutos: _provider.tempoMaximoMinutos,
      hasScopeJob: _provider.hasScopeJob,
      isCheckingScope: _provider.isCheckingScope,
    );
  }

  Future<void> generateTimetable(String turmaId, {required int anoLetivo, required String semestre}) async {
    await _provider.generateTimetable(turmaId, anoLetivo: anoLetivo, semestre: semestre);
  }

  /// RF09/RF10 — verifica se existe Job para o âmbito (ano/semestre) exato
  /// selecionado no filtro, independentemente de qual turma está selecionada.
  Future<void> checkScope(int anoLetivo, String semestre) async {
    await _provider.checkScope(anoLetivo, semestre);
  }

  /// Botão "Limpar Horário" — apaga o Job do âmbito atual.
  Future<bool> limparHorarioDoAmbito(int anoLetivo, String semestre) {
    return _provider.limparHorarioDoAmbito(anoLetivo, semestre);
  }

  /// Limpa o horário mostrado — usado quando checkScope confirma que não há
  /// Job para o âmbito atualmente selecionado.
  void clearSlots() {
    _provider.clearSlots();
  }

  Future<void> fetchTimetableByTurma(String turmaId) async {
    await _provider.fetchTimetableByTurma(turmaId);
  }

  Future<void> fetchTimetableByProfessor(String professorId) async {
    await _provider.fetchTimetableByProfessor(professorId);
  }

  Future<void> exportarHorarioTurmaPdf(String turmaId, FileShareService fileShareService) async {
    await _provider.exportarHorarioTurmaPdf(turmaId, fileShareService);
  }

  Future<void> exportarTodosHorarios(FileShareService fileShareService) async {
    await _provider.exportarTodosHorarios(fileShareService);
  }

  Future<bool> criarAlocacaoManual({
    required String jobId,
    required String turmaId,
    required String disciplinaId,
    required String professorId,
    required String salaId,
    required String diaSemana,
    required String turno,
    required List<int> periodos,
  }) {
    return _provider.criarAlocacaoManual(
      jobId: jobId,
      turmaId: turmaId,
      disciplinaId: disciplinaId,
      professorId: professorId,
      salaId: salaId,
      diaSemana: diaSemana,
      turno: turno,
      periodos: periodos,
    );
  }

  Future<bool> moverAlocacao(int alocacaoId, String diaSemana, int periodo) {
    return _provider.moverAlocacao(alocacaoId, diaSemana, periodo);
  }

  Future<bool> removerAlocacao(int alocacaoId) {
    return _provider.removerAlocacao(alocacaoId);
  }
}
