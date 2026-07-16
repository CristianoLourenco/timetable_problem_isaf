import 'package:flutter/foundation.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/entities/tempo_chave.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/usecase/get_all_tempos_usecase.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/usecase/get_disponibilidade_usecase.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/usecase/set_disponibilidade_usecase.dart';

/// Provider for the professor's weekly availability grid (RF05).
class DisponibilidadeProvider extends ChangeNotifier {
  DisponibilidadeProvider({
    required GetAllTemposUseCase getAllTemposUseCase,
    required GetDisponibilidadeUseCase getDisponibilidadeUseCase,
    required SetDisponibilidadeUseCase setDisponibilidadeUseCase,
  })  : _getAllTemposUseCase = getAllTemposUseCase,
        _getDisponibilidadeUseCase = getDisponibilidadeUseCase,
        _setDisponibilidadeUseCase = setDisponibilidadeUseCase;

  final GetAllTemposUseCase _getAllTemposUseCase;
  final GetDisponibilidadeUseCase _getDisponibilidadeUseCase;
  final SetDisponibilidadeUseCase _setDisponibilidadeUseCase;

  List<Tempo> _tempos = const <Tempo>[];
  List<Tempo> get tempos => _tempos;

  Set<TempoChave> _selectedTempos = const <TempoChave>{};
  Set<TempoChave> get selectedTempos => _selectedTempos;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  bool _isSaving = false;
  bool get isSaving => _isSaving;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  Future<void> load(int professorId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final temposResult = await _getAllTemposUseCase(null);
    final disponibilidadeResult = await _getDisponibilidadeUseCase(professorId);

    if (temposResult.success && temposResult.data != null) {
      _tempos = temposResult.data!;
    } else {
      _errorMessage = temposResult.message;
    }

    if (disponibilidadeResult.success && disponibilidadeResult.data != null) {
      _selectedTempos = disponibilidadeResult.data!.toSet();
    } else {
      _errorMessage ??= disponibilidadeResult.message;
    }

    _isLoading = false;
    notifyListeners();
  }

  void toggleTempo(TempoChave tempo) {
    final updated = {..._selectedTempos};
    if (!updated.remove(tempo)) {
      updated.add(tempo);
    }
    _selectedTempos = updated;
    notifyListeners();
  }

  Future<bool> save(int professorId) async {
    _isSaving = true;
    _errorMessage = null;
    notifyListeners();

    final result = await _setDisponibilidadeUseCase(
      SetDisponibilidadeParams(professorId: professorId, tempos: _selectedTempos.toList()),
    );

    if (result.success && result.data != null) {
      _selectedTempos = result.data!.toSet();
    } else {
      _errorMessage = result.message;
    }

    _isSaving = false;
    notifyListeners();
    return result.success;
  }
}
