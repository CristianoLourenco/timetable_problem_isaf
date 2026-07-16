import 'package:dio/dio.dart';
import 'package:ghorario/core/resources/data_state.dart';
import 'package:ghorario/core/resources/network/i_http_methods.dart';
import 'package:ghorario/core/utils/errors/i_exception_error.dart';

/// Concrete implementation of [IHttpMethods] using the [Dio] client.
class DioClient implements IHttpMethods {
  final Dio _dio;

  DioClient(this._dio);

  Future<DataState<T>> _handleRequest<T>(Future<Response<T>> request) async {
    try {
      final response = await request;
      return DataState<T>(
        data: response.data,
        success: true,
        statusCode: response.statusCode,
      );
    } on DioException catch (e) {
      final error = _mapDioException(e);
      return DataState<T>(
        error: error,
        success: false,
        statusCode: e.response?.statusCode,
        message: error.message,
      );
    } catch (e) {
      return DataState<T>(
        error: UnknownError(message: e.toString()),
        success: false,
      );
    }
  }

  IExceptionError _mapDioException(DioException e) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.sendTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return const TimeoutError();
    }
    if (e.type == DioExceptionType.connectionError) {
      return const NetworkError();
    }
    final response = e.response;
    if (response != null) {
      final code = response.statusCode;
      if (code == 401 || code == 403) {
        return const UnauthorizedError();
      }
      if (code == 404) {
        return const NotFoundError();
      }
      if (code == 429) {
        return const ManyTriesError();
      }
      if (code != null && code >= 500) {
        return ServerError(
          message: 'Erro do servidor externo. Por favor, tente mais tarde.',
          statusCode: code,
        );
      }
      final responseData = response.data;
      String? apiMessage;
      if (responseData is Map) {
        apiMessage = responseData['detail']?.toString() ?? responseData['message']?.toString();
      } else if (responseData is String) {
        apiMessage = responseData;
      }
      return ServerError(
        message: apiMessage ?? 'Ocorreu um erro no processamento do seu pedido.',
        statusCode: code,
      );
    }
    return UnknownError(message: e.message ?? 'Ocorreu um erro desconhecido.');
  }

  @override
  Future<DataState<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) {
    return _handleRequest<T>(
      _dio.delete<T>(
        path,
        data: data,
        queryParameters: queryParameters,
      ),
    );
  }

  @override
  Future<DataState<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) {
    return _handleRequest<T>(
      _dio.get<T>(
        path,
        queryParameters: queryParameters,
      ),
    );
  }

  @override
  Future<DataState<T>> patch<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) {
    return _handleRequest<T>(
      _dio.patch<T>(
        path,
        data: data,
        queryParameters: queryParameters,
      ),
    );
  }

  @override
  Future<DataState<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) {
    return _handleRequest<T>(
      _dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
      ),
    );
  }

  @override
  Future<DataState<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) {
    return _handleRequest<T>(
      _dio.put<T>(
        path,
        data: data,
        queryParameters: queryParameters,
      ),
    );
  }
}
