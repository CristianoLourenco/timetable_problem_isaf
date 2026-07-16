import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_salas/domain/entities/sala.dart';
import 'package:ghorario/features/feature_salas/domain/usecase/create_sala_usecase.dart';
import 'package:ghorario/features/feature_salas/domain/usecase/get_all_salas_usecase.dart';

/// Provider for global salas state.
class SalasProvider extends ChangeNotifier {
  SalasProvider({
    required GetAllSalasUseCase getAllSalasUseCase,
    required CreateSalaUseCase createSalaUseCase,
  })  : _getAllSalasUseCase = getAllSalasUseCase,
        _createSalaUseCase = createSalaUseCase;

  final GetAllSalasUseCase _getAllSalasUseCase;
  final CreateSalaUseCase _createSalaUseCase;

  List<Sala> _salas = const <Sala>[];
  List<Sala> get salas => _salas;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  Future<void> loadSalas() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final result = await _getAllSalasUseCase(null);
    if (result.success && result.data != null) {
      _salas = result.data!;
    } else {
      _errorMessage = result.message;
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Persists the new Sala via the API and refreshes the list.
  Future<bool> createSala(Sala sala) async {
    _errorMessage = null;
    final result = await _createSalaUseCase(sala);
    if (!result.success) {
      _errorMessage = result.message;
      notifyListeners();
      return false;
    }
    await loadSalas();
    return true;
  }
}
