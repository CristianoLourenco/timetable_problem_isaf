import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_disciplinas/domain/entities/disciplina.dart';
import 'package:ghorario/features/feature_disciplinas/presentation/provider/disciplinas_provider.dart';
import 'package:ghorario/features/feature_disciplinas/presentation/states/disciplinas_state.dart';

/// Local controller for the Disciplinas UI.
class DisciplinasController extends ValueNotifier<DisciplinasState> {
  DisciplinasController({
    required DisciplinasProvider provider,
  })  : _provider = provider,
        super(const DisciplinasState());

  final DisciplinasProvider _provider;

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
      disciplinas: _provider.disciplinas,
      isLoading: _provider.isLoading,
      errorMessage: _provider.errorMessage,
    );
    if (_provider.disciplinas.isEmpty) {
      fetchDisciplinas();
    }
  }

  void _onProviderChanged() {
    value = value.copyWith(
      disciplinas: _provider.disciplinas,
      isLoading: _provider.isLoading,
      errorMessage: _provider.errorMessage,
    );
  }

  Future<void> fetchDisciplinas() async {
    await _provider.loadDisciplinas();
  }

  Future<bool> addDisciplina(Disciplina disciplina) async {
    return _provider.createDisciplina(disciplina);
  }
}
