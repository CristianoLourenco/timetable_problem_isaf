import 'package:ghorario/core/resources/data_state.dart';

/// Abstract contract for HTTP network methods.
abstract class IHttpMethods {
  Future<DataState<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
  });

  Future<DataState<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  });

  Future<DataState<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  });

  Future<DataState<T>> patch<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  });

  Future<DataState<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  });
}
