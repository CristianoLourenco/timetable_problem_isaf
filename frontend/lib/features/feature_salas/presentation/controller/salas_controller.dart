import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_salas/domain/entities/sala.dart';
import 'package:ghorario/features/feature_salas/presentation/provider/salas_provider.dart';
import 'package:ghorario/features/feature_salas/presentation/states/salas_state.dart';

/// Local controller for the Salas UI.
class SalasController extends ValueNotifier<SalasState> {
  SalasController({
    required SalasProvider provider,
  })  : _provider = provider,
        super(const SalasState());

  final SalasProvider _provider;

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
      salas: _provider.salas,
      isLoading: _provider.isLoading,
      errorMessage: _provider.errorMessage,
    );
    if (_provider.salas.isEmpty) {
      fetchSalas();
    }
  }

  void _onProviderChanged() {
    value = value.copyWith(
      salas: _provider.salas,
      isLoading: _provider.isLoading,
      errorMessage: _provider.errorMessage,
    );
  }

  Future<void> fetchSalas() async {
    await _provider.loadSalas();
  }

  Future<bool> addSala(Sala sala) async {
    return _provider.createSala(sala);
  }
}
