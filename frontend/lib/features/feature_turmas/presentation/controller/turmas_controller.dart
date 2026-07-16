import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/turmas_provider.dart';
import 'package:ghorario/features/feature_turmas/presentation/states/turmas_state.dart';

/// Local controller for the Turmas UI.
class TurmasController extends ValueNotifier<TurmasState> {
  TurmasController({
    required TurmasProvider provider,
  })  : _provider = provider,
        super(const TurmasState());

  final TurmasProvider _provider;

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
      turmas: _provider.turmas,
      isLoading: _provider.isLoading,
      errorMessage: _provider.errorMessage,
    );
    if (_provider.turmas.isEmpty) {
      fetchTurmas();
    }
  }

  void _onProviderChanged() {
    value = value.copyWith(
      turmas: _provider.turmas,
      isLoading: _provider.isLoading,
      errorMessage: _provider.errorMessage,
    );
  }

  Future<void> fetchTurmas() async {
    await _provider.loadTurmas();
  }

  Future<bool> createTurma(Turma turma) async {
    return _provider.createTurma(turma);
  }
}
