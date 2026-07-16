import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo_chave.dart';
import 'package:ghorario/features/feature_disponibilidade/presentation/provider/disponibilidade_provider.dart';
import 'package:ghorario/features/feature_disponibilidade/presentation/states/disponibilidade_state.dart';

/// Local controller for the Disponibilidade UI.
class DisponibilidadeController extends ValueNotifier<DisponibilidadeState> {
  DisponibilidadeController({
    required DisponibilidadeProvider provider,
  })  : _provider = provider,
        super(const DisponibilidadeState());

  final DisponibilidadeProvider _provider;

  void init(int professorId) {
    _hydrate();
    _provider.addListener(_onProviderChanged);
    load(professorId);
  }

  @override
  void dispose() {
    _provider.removeListener(_onProviderChanged);
    super.dispose();
  }

  void _hydrate() {
    value = value.copyWith(
      tempos: _provider.tempos,
      selectedTempos: _provider.selectedTempos,
      isLoading: _provider.isLoading,
      isSaving: _provider.isSaving,
      errorMessage: _provider.errorMessage,
    );
  }

  void _onProviderChanged() {
    value = value.copyWith(
      tempos: _provider.tempos,
      selectedTempos: _provider.selectedTempos,
      isLoading: _provider.isLoading,
      isSaving: _provider.isSaving,
      errorMessage: _provider.errorMessage,
    );
  }

  Future<void> load(int professorId) async {
    await _provider.load(professorId);
  }

  void toggleTempo(TempoChave tempo) {
    _provider.toggleTempo(tempo);
  }

  Future<bool> save(int professorId) async {
    return _provider.save(professorId);
  }
}
