import 'package:ghorario/core/resources/data_state.dart';

/// Abstract contract for local persistent storage methods.
abstract class IStorageMethods {
  Future<DataState<void>> save(String key, String value);
  Future<DataState<String?>> read(String key);
  Future<DataState<void>> delete(String key);
  Future<DataState<void>> clear();
}
