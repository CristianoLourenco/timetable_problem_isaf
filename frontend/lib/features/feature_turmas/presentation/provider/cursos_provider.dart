import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_turmas/domain/entities/curso.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/create_curso_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/get_all_cursos_usecase.dart';

/// Provider for global cursos state.
class CursosProvider extends ChangeNotifier {
  CursosProvider({
    required GetAllCursosUseCase getAllCursosUseCase,
    required CreateCursoUseCase createCursoUseCase,
  })  : _getAllCursosUseCase = getAllCursosUseCase,
        _createCursoUseCase = createCursoUseCase;

  final GetAllCursosUseCase _getAllCursosUseCase;
  final CreateCursoUseCase _createCursoUseCase;

  List<Curso> _cursos = const <Curso>[];
  List<Curso> get cursos => _cursos;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  Future<void> loadCursos() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final result = await _getAllCursosUseCase(null);
    if (result.success && result.data != null) {
      _cursos = result.data!;
    } else {
      _errorMessage = result.message;
    }

    _isLoading = false;
    notifyListeners();
  }

  Future<bool> createCurso(Curso curso) async {
    _errorMessage = null;
    final result = await _createCursoUseCase(curso);
    if (!result.success) {
      _errorMessage = result.message;
      notifyListeners();
      return false;
    }
    await loadCursos();
    return true;
  }
}
