import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_docentes/domain/entities/docente.dart';
import 'package:ghorario/features/feature_docentes/presentation/provider/docentes_provider.dart';
import 'package:ghorario/features/feature_docentes/presentation/states/docentes_state.dart';

/// Local controller managing the state lifecycle of the Docentes UI.
class DocentesController extends ValueNotifier<DocentesState> {
  DocentesController({
    required DocentesProvider provider,
  })  : _provider = provider,
        super(const DocentesState());

  final DocentesProvider _provider;

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
      docentes: _provider.docentes,
      isLoading: _provider.isLoading,
      errorMessage: _provider.errorMessage,
    );
    if (_provider.docentes.isEmpty) {
      fetchDocentes();
    }
  }

  void _onProviderChanged() {
    value = value.copyWith(
      docentes: _provider.docentes,
      isLoading: _provider.isLoading,
      errorMessage: _provider.errorMessage,
    );
  }

  Future<void> fetchDocentes() async {
    await _provider.loadDocentes();
  }

  Future<bool> createDocente(Docente docente) async {
    return _provider.createDocente(docente);
  }
}
