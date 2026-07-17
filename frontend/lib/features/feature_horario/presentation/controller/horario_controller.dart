import 'package:flutter/foundation.dart';
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
    );
  }

  void _onProviderChanged() {
    value = value.copyWith(
      slots: _provider.slots,
      isLoading: _provider.isLoading,
      isGenerating: _provider.isGenerating,
      errorMessage: _provider.errorMessage,
      currentJobId: _provider.currentJobId,
    );
  }

  Future<void> generateTimetable(
    String turmaId, {
    required String cursoId,
    required int anoLetivo,
    required String semestre,
  }) async {
    await _provider.generateTimetable(turmaId, cursoId: cursoId, anoLetivo: anoLetivo, semestre: semestre);
  }

  Future<void> fetchTimetableByTurma(String turmaId) async {
    await _provider.fetchTimetableByTurma(turmaId);
  }

  Future<void> fetchTimetableByProfessor(String professorId) async {
    await _provider.fetchTimetableByProfessor(professorId);
  }
}
