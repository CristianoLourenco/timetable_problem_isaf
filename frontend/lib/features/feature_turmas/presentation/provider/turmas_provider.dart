import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/turma.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/create_turma_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/get_all_turmas_usecase.dart';

/// Provider for global turmas state.
class TurmasProvider extends ChangeNotifier {
  TurmasProvider({
    required GetAllTurmasUseCase getAllTurmasUseCase,
    required CreateTurmaUseCase createTurmaUseCase,
  })  : _getAllTurmasUseCase = getAllTurmasUseCase,
        _createTurmaUseCase = createTurmaUseCase;

  final GetAllTurmasUseCase _getAllTurmasUseCase;
  final CreateTurmaUseCase _createTurmaUseCase;

  List<Turma> _turmas = const <Turma>[];
  List<Turma> get turmas => _turmas;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  Future<void> loadTurmas() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final result = await _getAllTurmasUseCase(null);
    if (result.success && result.data != null) {
      _turmas = result.data!;
    } else {
      _errorMessage = result.message;
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Persists the new Turma via the API and refreshes the list.
  Future<bool> createTurma(Turma turma) async {
    _errorMessage = null;
    final result = await _createTurmaUseCase(turma);
    if (!result.success) {
      _errorMessage = result.message;
      notifyListeners();
      return false;
    }
    await loadTurmas();
    return true;
  }
}
