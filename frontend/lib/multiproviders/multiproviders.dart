import 'package:dio/dio.dart';
import 'package:hive/hive.dart';
import 'package:provider/provider.dart';
import 'package:provider/single_child_widget.dart';

// Core imports
import 'package:ghorario/core/core.dart';
import 'package:ghorario/core/resources/network/dio/auth_interceptor.dart';

// Feature Docentes
import 'package:ghorario/features/feature_docentes/data/datasource/remote/docente_remote_impl.dart';
import 'package:ghorario/features/feature_docentes/data/datasource/remote/i_docente_remote.dart';
import 'package:ghorario/features/feature_docentes/data/repository_impl/docente_repository_impl.dart';
import 'package:ghorario/features/feature_docentes/domain/repository/i_docente_repository.dart';
import 'package:ghorario/features/feature_docentes/domain/usecase/create_docente_usecase.dart';
import 'package:ghorario/features/feature_docentes/domain/usecase/get_all_docentes_usecase.dart';
import 'package:ghorario/features/feature_docentes/presentation/provider/docentes_provider.dart';

// Feature Turmas (+ Cursos e PlanoCurricular, entidades de suporte de Turma)
import 'package:ghorario/features/feature_turmas/data/datasource/remote/curso_remote_impl.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/i_curso_remote.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/i_plano_curricular_remote.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/i_turma_remote.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/plano_curricular_remote_impl.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/turma_remote_impl.dart';
import 'package:ghorario/features/feature_turmas/data/repository_impl/curso_repository_impl.dart';
import 'package:ghorario/features/feature_turmas/data/repository_impl/plano_curricular_repository_impl.dart';
import 'package:ghorario/features/feature_turmas/data/repository_impl/turma_repository_impl.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_curso_repository.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_plano_curricular_repository.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_turma_repository.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/create_curso_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/create_turma_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/get_all_cursos_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/get_all_planos_curriculares_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/get_all_turmas_usecase.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/cursos_provider.dart';
import 'package:ghorario/features/feature_turmas/presentation/provider/turmas_provider.dart';

// Feature Disciplinas
import 'package:ghorario/features/feature_disciplinas/data/datasource/remote/disciplina_remote_impl.dart';
import 'package:ghorario/features/feature_disciplinas/data/datasource/remote/i_disciplina_remote.dart';
import 'package:ghorario/features/feature_disciplinas/data/repository_impl/disciplina_repository_impl.dart';
import 'package:ghorario/features/feature_disciplinas/domain/repository/i_disciplina_repository.dart';
import 'package:ghorario/features/feature_disciplinas/domain/usecase/create_disciplina_usecase.dart';
import 'package:ghorario/features/feature_disciplinas/domain/usecase/get_all_disciplinas_usecase.dart';
import 'package:ghorario/features/feature_disciplinas/presentation/provider/disciplinas_provider.dart';

// Feature Salas
import 'package:ghorario/features/feature_salas/data/datasource/remote/i_sala_remote.dart';
import 'package:ghorario/features/feature_salas/data/datasource/remote/sala_remote_impl.dart';
import 'package:ghorario/features/feature_salas/data/repository_impl/sala_repository_impl.dart';
import 'package:ghorario/features/feature_salas/domain/repository/i_sala_repository.dart';
import 'package:ghorario/features/feature_salas/domain/usecase/create_sala_usecase.dart';
import 'package:ghorario/features/feature_salas/domain/usecase/get_all_salas_usecase.dart';
import 'package:ghorario/features/feature_salas/presentation/provider/salas_provider.dart';

// Feature Disponibilidade (RF05)
import 'package:ghorario/features/feature_disponibilidade/data/datasource/remote/disponibilidade_remote_impl.dart';
import 'package:ghorario/features/feature_disponibilidade/data/datasource/remote/i_disponibilidade_remote.dart';
import 'package:ghorario/features/feature_disponibilidade/data/datasource/remote/i_tempo_remote.dart';
import 'package:ghorario/features/feature_disponibilidade/data/datasource/remote/tempo_remote_impl.dart';
import 'package:ghorario/features/feature_disponibilidade/data/repository_impl/disponibilidade_repository_impl.dart';
import 'package:ghorario/features/feature_disponibilidade/data/repository_impl/tempo_repository_impl.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/repository/i_disponibilidade_repository.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/repository/i_tempo_repository.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/usecase/get_all_tempos_usecase.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/usecase/get_disponibilidade_usecase.dart';
import 'package:ghorario/features/feature_disponibilidade/domain/usecase/set_disponibilidade_usecase.dart';
import 'package:ghorario/features/feature_disponibilidade/presentation/provider/disponibilidade_provider.dart';

// Feature Grade Curricular (Turma-Disciplina)
import 'package:ghorario/features/feature_turmas/data/datasource/remote/i_turma_disciplina_remote.dart';
import 'package:ghorario/features/feature_turmas/data/datasource/remote/turma_disciplina_remote_impl.dart';
import 'package:ghorario/features/feature_turmas/data/repository_impl/turma_disciplina_repository_impl.dart';
import 'package:ghorario/features/feature_turmas/domain/repository/i_turma_disciplina_repository.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/get_grade_curricular_usecase.dart';
import 'package:ghorario/features/feature_turmas/domain/usecase/set_grade_curricular_usecase.dart';

// Feature Qualificação Docente (Professor-Disciplina)
import 'package:ghorario/features/feature_docentes/data/datasource/remote/i_professor_disciplina_remote.dart';
import 'package:ghorario/features/feature_docentes/data/datasource/remote/professor_disciplina_remote_impl.dart';
import 'package:ghorario/features/feature_docentes/data/repository_impl/professor_disciplina_repository_impl.dart';
import 'package:ghorario/features/feature_docentes/domain/repository/i_professor_disciplina_repository.dart';
import 'package:ghorario/features/feature_docentes/domain/usecase/get_qualificacao_usecase.dart';
import 'package:ghorario/features/feature_docentes/domain/usecase/set_qualificacao_usecase.dart';

// Feature Importação (Excel — RF06/RF07/RF08)
import 'package:ghorario/features/feature_importacao/data/datasource/remote/i_importacao_remote.dart';
import 'package:ghorario/features/feature_importacao/data/datasource/remote/importacao_remote_impl.dart';
import 'package:ghorario/features/feature_importacao/data/repository_impl/importacao_repository_impl.dart';
import 'package:ghorario/features/feature_importacao/domain/repository/i_importacao_repository.dart';
import 'package:ghorario/features/feature_importacao/domain/usecase/importar_excel_usecase.dart';

// Feature Horario
import 'package:ghorario/features/feature_horario/data/datasource/remote/horario_remote_impl.dart';
import 'package:ghorario/features/feature_horario/data/datasource/remote/i_horario_remote.dart';
import 'package:ghorario/features/feature_horario/data/repository_impl/horario_repository_impl.dart';
import 'package:ghorario/features/feature_horario/domain/repository/i_horario_repository.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/check_job_status_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/exportar_horario_turma_pdf_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/exportar_todos_horarios_pdf_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/gerar_horario_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_horario_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_pendencias_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_professores_qualificados_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_slots_vagos_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/criar_alocacao_manual_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/mover_alocacao_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/remover_alocacao_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/get_job_by_scope_usecase.dart';
import 'package:ghorario/features/feature_horario/domain/usecase/delete_job_usecase.dart';
import 'package:ghorario/features/feature_horario/presentation/provider/horario_provider.dart';

// Feature Auth
import 'package:ghorario/features/feature_auth/data/datasource/remote/auth_remote_impl.dart';
import 'package:ghorario/features/feature_auth/data/datasource/remote/i_auth_remote.dart';
import 'package:ghorario/features/feature_auth/data/repository_impl/auth_repository_impl.dart';
import 'package:ghorario/features/feature_auth/domain/repository/i_auth_repository.dart';
import 'package:ghorario/features/feature_auth/domain/usecase/login_usecase.dart';
import 'package:ghorario/features/feature_auth/domain/usecase/logout_usecase.dart';
import 'package:ghorario/features/feature_auth/domain/usecase/get_current_user_usecase.dart';
import 'package:ghorario/features/feature_auth/domain/usecase/recuperar_password_usecase.dart';
import 'package:ghorario/features/feature_auth/domain/usecase/registo_professor_usecase.dart';
import 'package:ghorario/features/feature_auth/presentation/provider/auth_provider.dart';

// Feature Dashboard
import 'package:ghorario/features/feature_dashboard/presentation/provider/dashboard_provider.dart';

/// Central helper for configuring and initializing all global app providers.
class AppMultiProviders {
  static List<SingleChildWidget> getProviders(Box<String> sessionBox) {
    // 0. Local session storage (id_token / refresh_token)
    final IStorageMethods storage = ProviderStateHiveBox(sessionBox);

    // 1. Initialize Network Client
    final dio = Dio(
      BaseOptions(
        baseUrl: 'http://localhost:8000', // FastAPI backend server URL
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 15),
      ),
    );
    dio.interceptors.add(AuthInterceptor(storage, dio));
    final IHttpMethods httpMethods = DioClient(dio);

    // 2. Auth Dependencies
    final IAuthRemote authRemote = AuthRemoteImpl(httpMethods);
    final IAuthRepository authRepository = AuthRepositoryImpl(
      remoteDatasource: authRemote,
      storage: storage,
    );
    final loginUseCase = LoginUseCase(authRepository);
    final logoutUseCase = LogoutUseCase(authRepository);
    final getCurrentUserUseCase = GetCurrentUserUseCase(authRepository);
    final registoProfessorUseCase = RegistoProfessorUseCase(authRepository);
    final recuperarPasswordUseCase = RecuperarPasswordUseCase(authRepository);

    // 3. Docentes Dependencies
    final IDocenteRemote docenteRemote = DocenteRemoteImpl(httpMethods);
    final IDocenteRepository docenteRepository = DocenteRepositoryImpl(remoteDatasource: docenteRemote);
    final getAllDocentesUseCase = GetAllDocentesUseCase(docenteRepository);
    final createDocenteUseCase = CreateDocenteUseCase(docenteRepository);

    // 4. Turmas + Cursos Dependencies
    final ITurmaRemote turmaRemote = TurmaRemoteImpl(httpMethods);
    final ITurmaRepository turmaRepository = TurmaRepositoryImpl(remoteDatasource: turmaRemote);
    final getAllTurmasUseCase = GetAllTurmasUseCase(turmaRepository);
    final createTurmaUseCase = CreateTurmaUseCase(turmaRepository);
    final ICursoRemote cursoRemote = CursoRemoteImpl(httpMethods);
    final ICursoRepository cursoRepository = CursoRepositoryImpl(remoteDatasource: cursoRemote);
    final getAllCursosUseCase = GetAllCursosUseCase(cursoRepository);
    final createCursoUseCase = CreateCursoUseCase(cursoRepository);
    final IPlanoCurricularRemote planoCurricularRemote = PlanoCurricularRemoteImpl(httpMethods);
    final IPlanoCurricularRepository planoCurricularRepository =
        PlanoCurricularRepositoryImpl(remoteDatasource: planoCurricularRemote);
    final getAllPlanosCurricularesUseCase = GetAllPlanosCurricularesUseCase(planoCurricularRepository);

    // 5. Disciplinas Dependencies
    final IDisciplinaRemote disciplinaRemote = DisciplinaRemoteImpl(httpMethods);
    final IDisciplinaRepository disciplinaRepository = DisciplinaRepositoryImpl(remoteDatasource: disciplinaRemote);
    final getAllDisciplinasUseCase = GetAllDisciplinasUseCase(disciplinaRepository);
    final createDisciplinaUseCase = CreateDisciplinaUseCase(disciplinaRepository);

    // 6. Salas Dependencies
    final ISalaRemote salaRemote = SalaRemoteImpl(httpMethods);
    final ISalaRepository salaRepository = SalaRepositoryImpl(remoteDatasource: salaRemote);
    final getAllSalasUseCase = GetAllSalasUseCase(salaRepository);
    final createSalaUseCase = CreateSalaUseCase(salaRepository);

    // 7. Horário Dependencies
    final IHorarioRemote horarioRemote = HorarioRemoteImpl(httpMethods);
    final IHorarioRepository horarioRepository = HorarioRepositoryImpl(remoteDatasource: horarioRemote);
    final gerarHorarioUseCase = GerarHorarioUseCase(horarioRepository);
    final getHorarioUseCase = GetHorarioUseCase(horarioRepository);
    final checkJobStatusUseCase = CheckJobStatusUseCase(horarioRepository);
    final exportarHorarioTurmaPdfUseCase = ExportarHorarioTurmaPdfUseCase(horarioRepository);
    final exportarTodosHorariosPdfUseCase = ExportarTodosHorariosPdfUseCase(horarioRepository);
    final getPendenciasUseCase = GetPendenciasUseCase(horarioRepository);
    final getProfessoresQualificadosUseCase = GetProfessoresQualificadosUseCase(horarioRepository);
    final getSlotsVagosUseCase = GetSlotsVagosUseCase(horarioRepository);
    final criarAlocacaoManualUseCase = CriarAlocacaoManualUseCase(horarioRepository);
    final moverAlocacaoUseCase = MoverAlocacaoUseCase(horarioRepository);
    final removerAlocacaoUseCase = RemoverAlocacaoUseCase(horarioRepository);
    final getJobByScopeUseCase = GetJobByScopeUseCase(horarioRepository);
    final deleteJobUseCase = DeleteJobUseCase(horarioRepository);

    // 8. Importação Excel Dependencies (RF06/RF07/RF08)
    final IImportacaoRemote importacaoRemote = ImportacaoRemoteImpl(httpMethods);
    final IImportacaoRepository importacaoRepository =
        ImportacaoRepositoryImpl(remoteDatasource: importacaoRemote);
    final importarExcelUseCase = ImportarExcelUseCase(importacaoRepository);

    // 9. Disponibilidade Dependencies (RF05)
    final ITempoRemote tempoRemote = TempoRemoteImpl(httpMethods);
    final ITempoRepository tempoRepository = TempoRepositoryImpl(remoteDatasource: tempoRemote);
    final getAllTemposUseCase = GetAllTemposUseCase(tempoRepository);
    final IDisponibilidadeRemote disponibilidadeRemote = DisponibilidadeRemoteImpl(httpMethods);
    final IDisponibilidadeRepository disponibilidadeRepository =
        DisponibilidadeRepositoryImpl(remoteDatasource: disponibilidadeRemote);
    final getDisponibilidadeUseCase = GetDisponibilidadeUseCase(disponibilidadeRepository);
    final setDisponibilidadeUseCase = SetDisponibilidadeUseCase(disponibilidadeRepository);

    // 10. Grade Curricular Dependencies (Turma-Disciplina)
    final ITurmaDisciplinaRemote turmaDisciplinaRemote = TurmaDisciplinaRemoteImpl(httpMethods);
    final ITurmaDisciplinaRepository turmaDisciplinaRepository =
        TurmaDisciplinaRepositoryImpl(remoteDatasource: turmaDisciplinaRemote);
    final getGradeCurricularUseCase = GetGradeCurricularUseCase(turmaDisciplinaRepository);
    final setGradeCurricularUseCase = SetGradeCurricularUseCase(turmaDisciplinaRepository);

    // 11. Qualificação Docente Dependencies (Professor-Disciplina)
    final IProfessorDisciplinaRemote professorDisciplinaRemote = ProfessorDisciplinaRemoteImpl(httpMethods);
    final IProfessorDisciplinaRepository professorDisciplinaRepository =
        ProfessorDisciplinaRepositoryImpl(remoteDatasource: professorDisciplinaRemote);
    final getQualificacaoUseCase = GetQualificacaoUseCase(professorDisciplinaRepository);
    final setQualificacaoUseCase = SetQualificacaoUseCase(professorDisciplinaRepository);

    return [
      ChangeNotifierProvider<AuthProvider>(
        create: (_) => AuthProvider(
          loginUseCase: loginUseCase,
          logoutUseCase: logoutUseCase,
          getCurrentUserUseCase: getCurrentUserUseCase,
          registoProfessorUseCase: registoProfessorUseCase,
          recuperarPasswordUseCase: recuperarPasswordUseCase,
        )..checkCurrentUser(),
      ),
      ChangeNotifierProvider<DocentesProvider>(
        create: (_) => DocentesProvider(
          getAllDocentesUseCase: getAllDocentesUseCase,
          createDocenteUseCase: createDocenteUseCase,
        ),
      ),
      ChangeNotifierProvider<TurmasProvider>(
        create: (_) => TurmasProvider(
          getAllTurmasUseCase: getAllTurmasUseCase,
          createTurmaUseCase: createTurmaUseCase,
        ),
      ),
      ChangeNotifierProvider<CursosProvider>(
        create: (_) => CursosProvider(
          getAllCursosUseCase: getAllCursosUseCase,
          createCursoUseCase: createCursoUseCase,
        ),
      ),
      ChangeNotifierProvider<DisciplinasProvider>(
        create: (_) => DisciplinasProvider(
          getAllDisciplinasUseCase: getAllDisciplinasUseCase,
          createDisciplinaUseCase: createDisciplinaUseCase,
        ),
      ),
      ChangeNotifierProvider<SalasProvider>(
        create: (_) => SalasProvider(
          getAllSalasUseCase: getAllSalasUseCase,
          createSalaUseCase: createSalaUseCase,
        ),
      ),
      ChangeNotifierProvider<HorarioProvider>(
        create: (_) => HorarioProvider(
          gerarHorarioUseCase: gerarHorarioUseCase,
          getHorarioUseCase: getHorarioUseCase,
          checkJobStatusUseCase: checkJobStatusUseCase,
          exportarHorarioTurmaPdfUseCase: exportarHorarioTurmaPdfUseCase,
          exportarTodosHorariosPdfUseCase: exportarTodosHorariosPdfUseCase,
          getPendenciasUseCase: getPendenciasUseCase,
          getProfessoresQualificadosUseCase: getProfessoresQualificadosUseCase,
          getSlotsVagosUseCase: getSlotsVagosUseCase,
          criarAlocacaoManualUseCase: criarAlocacaoManualUseCase,
          moverAlocacaoUseCase: moverAlocacaoUseCase,
          removerAlocacaoUseCase: removerAlocacaoUseCase,
          getJobByScopeUseCase: getJobByScopeUseCase,
          deleteJobUseCase: deleteJobUseCase,
        ),
      ),
      ChangeNotifierProvider<DashboardProvider>(
        create: (_) => DashboardProvider(),
      ),
      ChangeNotifierProvider<DisponibilidadeProvider>(
        create: (_) => DisponibilidadeProvider(
          getAllTemposUseCase: getAllTemposUseCase,
          getDisponibilidadeUseCase: getDisponibilidadeUseCase,
          setDisponibilidadeUseCase: setDisponibilidadeUseCase,
        ),
      ),
      Provider<GetAllCursosUseCase>.value(value: getAllCursosUseCase),
      Provider<GetAllPlanosCurricularesUseCase>.value(value: getAllPlanosCurricularesUseCase),
      Provider<ImportarExcelUseCase>.value(value: importarExcelUseCase),
      Provider<GetGradeCurricularUseCase>.value(value: getGradeCurricularUseCase),
      Provider<SetGradeCurricularUseCase>.value(value: setGradeCurricularUseCase),
      Provider<GetQualificacaoUseCase>.value(value: getQualificacaoUseCase),
      Provider<SetQualificacaoUseCase>.value(value: setQualificacaoUseCase),
      Provider<GetProfessoresQualificadosUseCase>.value(value: getProfessoresQualificadosUseCase),
      Provider<GetSlotsVagosUseCase>.value(value: getSlotsVagosUseCase),
      Provider<CriarAlocacaoManualUseCase>.value(value: criarAlocacaoManualUseCase),
      Provider<RemoverAlocacaoUseCase>.value(value: removerAlocacaoUseCase),
      Provider<MoverAlocacaoUseCase>.value(value: moverAlocacaoUseCase),
      Provider<GetJobByScopeUseCase>.value(value: getJobByScopeUseCase),
      Provider<DeleteJobUseCase>.value(value: deleteJobUseCase),
    ];
  }
}
