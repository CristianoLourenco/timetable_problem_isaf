import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_docentes/domain/entities/docente.dart';
import 'package:ghorario/features/feature_docentes/domain/usecase/create_docente_usecase.dart';
import 'package:ghorario/features/feature_docentes/domain/usecase/get_all_docentes_usecase.dart';

/// Provider (global state/cache) for the Docentes feature.
class DocentesProvider extends ChangeNotifier {
  DocentesProvider({
    required GetAllDocentesUseCase getAllDocentesUseCase,
    required CreateDocenteUseCase createDocenteUseCase,
  })  : _getAllDocentesUseCase = getAllDocentesUseCase,
        _createDocenteUseCase = createDocenteUseCase;

  final GetAllDocentesUseCase _getAllDocentesUseCase;
  final CreateDocenteUseCase _createDocenteUseCase;

  List<Docente> _docentes = const <Docente>[];
  List<Docente> get docentes => _docentes;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  Future<void> loadDocentes() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final result = await _getAllDocentesUseCase(null);
    if (result.success && result.data != null) {
      _docentes = result.data!;
    } else {
      _errorMessage = result.message;
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Persists the new Professor via the API and refreshes the list.
  /// Returns `false` (with [errorMessage] set) if the API call fails.
  Future<bool> createDocente(Docente docente) async {
    _errorMessage = null;
    final result = await _createDocenteUseCase(docente);
    if (!result.success) {
      _errorMessage = result.message;
      notifyListeners();
      return false;
    }
    await loadDocentes();
    return true;
  }
}
