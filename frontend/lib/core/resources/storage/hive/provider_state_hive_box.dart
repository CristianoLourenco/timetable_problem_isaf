import 'package:hive/hive.dart';
import 'package:ghorario/core/resources/data_state.dart';
import 'package:ghorario/core/resources/storage/i_storage_methods.dart';
import 'package:ghorario/core/utils/errors/failure.dart';

/// Concrete implementation of [IStorageMethods] using Hive box.
class ProviderStateHiveBox implements IStorageMethods {
  final Box<String> _box;

  ProviderStateHiveBox(this._box);

  @override
  Future<DataState<void>> save(String key, String value) async {
    try {
      await _box.put(key, value);
      return DataState(data: null, success: true);
    } catch (e) {
      return DataState(
        success: false,
        error: CacheFailure(message: 'Erro ao salvar dados localmente: $e'),
      );
    }
  }

  @override
  Future<DataState<String?>> read(String key) async {
    try {
      final value = _box.get(key);
      return DataState(data: value, success: true);
    } catch (e) {
      return DataState(
        success: false,
        error: CacheFailure(message: 'Erro ao ler dados locais: $e'),
      );
    }
  }

  @override
  Future<DataState<void>> delete(String key) async {
    try {
      await _box.delete(key);
      return DataState(data: null, success: true);
    } catch (e) {
      return DataState(
        success: false,
        error: CacheFailure(message: 'Erro ao remover dados locais: $e'),
      );
    }
  }

  @override
  Future<DataState<void>> clear() async {
    try {
      await _box.clear();
      return DataState(data: null, success: true);
    } catch (e) {
      return DataState(
        success: false,
        error: CacheFailure(message: 'Erro ao limpar dados locais: $e'),
      );
    }
  }
}
