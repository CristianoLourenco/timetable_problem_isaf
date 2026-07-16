import 'package:ghorario/core/core.dart';
import 'package:ghorario/features/feature_docentes/data/models/docente_dto.dart';

/// Abstract remote datasource interface for Docentes.
abstract class IDocenteRemote {
  Future<DataState<List<DocenteDto>>> getAll();
  Future<DataState<DocenteDto>> getById(String id);
  Future<DataState<void>> create(DocenteDto dto);
  Future<DataState<void>> update(DocenteDto dto);
  Future<DataState<void>> delete(String id);
}
