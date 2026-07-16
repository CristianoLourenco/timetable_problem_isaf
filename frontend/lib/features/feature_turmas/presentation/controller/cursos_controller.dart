import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/curso.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/cursos_provider.dart';
import 'package:ghorario/features/feature_turmas/presentation/states/cursos_state.dart';

/// Local controller for the Cursos UI.
class CursosController extends ValueNotifier<CursosState> {
  CursosController({
    required CursosProvider provider,
  })  : _provider = provider,
        super(const CursosState());

  final CursosProvider _provider;

  void init() {
    _hydrate();
    _provider.addListener(_onProviderChanged);
    if (_provider.cursos.isEmpty) {
      fetchCursos();
    }
  }

  @override
  void dispose() {
    _provider.removeListener(_onProviderChanged);
    super.dispose();
  }

  void _hydrate() {
    value = value.copyWith(
      cursos: _provider.cursos,
      isLoading: _provider.isLoading,
      errorMessage: _provider.errorMessage,
    );
  }

  void _onProviderChanged() {
    value = value.copyWith(
      cursos: _provider.cursos,
      isLoading: _provider.isLoading,
      errorMessage: _provider.errorMessage,
    );
  }

  Future<void> fetchCursos() async {
    await _provider.loadCursos();
  }

  Future<bool> createCurso(Curso curso) async {
    return _provider.createCurso(curso);
  }
}
