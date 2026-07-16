import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_disciplinas/domain/entities/disciplina.dart';
import 'package:ghorario/features/feature_disciplinas/domain/usecase/create_disciplina_usecase.dart';
import 'package:ghorario/features/feature_disciplinas/domain/usecase/get_all_disciplinas_usecase.dart';

/// Provider for global disciplinas state.
class DisciplinasProvider extends ChangeNotifier {
  DisciplinasProvider({
    required GetAllDisciplinasUseCase getAllDisciplinasUseCase,
    required CreateDisciplinaUseCase createDisciplinaUseCase,
  })  : _getAllDisciplinasUseCase = getAllDisciplinasUseCase,
        _createDisciplinaUseCase = createDisciplinaUseCase;

  final GetAllDisciplinasUseCase _getAllDisciplinasUseCase;
  final CreateDisciplinaUseCase _createDisciplinaUseCase;

  List<Disciplina> _disciplinas = const <Disciplina>[];
  List<Disciplina> get disciplinas => _disciplinas;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  Future<void> loadDisciplinas() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final result = await _getAllDisciplinasUseCase(null);
    if (result.success && result.data != null) {
      _disciplinas = result.data!;
    } else {
      _errorMessage = result.message;
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Persists the new Disciplina via the API and refreshes the list.
  Future<bool> createDisciplina(Disciplina disciplina) async {
    _errorMessage = null;
    final result = await _createDisciplinaUseCase(disciplina);
    if (!result.success) {
      _errorMessage = result.message;
      notifyListeners();
      return false;
    }
    await loadDisciplinas();
    return true;
  }
}
