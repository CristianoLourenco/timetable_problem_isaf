# Implementa: RF11, RF12 (UC11, UC12) — exportação do horário em PDF.
#
# Estrutura visual alinhada aos exemplares reais do ISAF (docs/exemplar_isaf/, não
# versionado — confidencial): cabeçalho institucional, grelha dias x tempos com
# disciplina+sala por célula, legenda de professores em baixo. Acrescenta uma faixa
# âmbar distintiva ("Gerado automaticamente") para nunca poder ser confundido com um
# horário manual real do ISAF — decisão confirmada com o utilizador.
#
# Reaproveita HorarioService.consultar_horario_turma/montar_resposta (mesma fonte de
# verdade da consulta JSON RF11/RF12) em vez de duplicar a resolução de
# disciplina/professor/sala — só a renderização é nova aqui.
import io
import zipfile
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlmodel import Session

from app.core.exceptions import EntidadeNaoEncontradaError
from app.models.curso import Curso
from app.models.job import JobStatus
from app.models.plano_curricular import PlanoCurricular
from app.models.turma import Turma
from app.repositories.alocacao_repository import AlocacaoRepository
from app.repositories.curso_repository import CursoRepository
from app.repositories.job_repository import JobRepository
from app.repositories.plano_curricular_repository import PlanoCurricularRepository
from app.repositories.turma_repository import TurmaRepository
from app.schemas.horario_schema import HorarioResponseSchema
from app.services.horario_service import HorarioService

_COR_FAIXA = colors.HexColor("#F59E0B")  # âmbar — mesmo tom de AppColors.warning no Flutter
_COR_LINHA_PAR = colors.HexColor("#EAF6FF")
_COR_CABECALHO_GRELHA = colors.HexColor("#00395E")  # AppColors.blackBlue
_ORDEM_DIAS = ["segunda", "terca", "quarta", "quinta", "sexta"]
_NOME_DIA = {
    "segunda": "Segunda-Feira",
    "terca": "Terça-Feira",
    "quarta": "Quarta-Feira",
    "quinta": "Quinta-Feira",
    "sexta": "Sexta-Feira",
}


def gerar_pdf_turma(session: Session, turma_id: int) -> bytes:
    """Um PDF para a turma indicada, a partir do Job DONE mais recente do seu
    (ano_letivo, semestre) — mesma regra de RF11 (ver HorarioService).

    Ao contrário da consulta JSON (RF11), aqui "ainda não há horário gerado" É um
    erro — não faz sentido exportar um PDF vazio; consultar_horario_turma devolve
    None nesse caso (200/null na consulta interativa), convertido aqui em
    EntidadeNaoEncontradaError (404) por ser uma ação explícita do Gestor."""
    resposta = HorarioService(session).consultar_horario_turma(turma_id)
    if resposta is None:
        raise EntidadeNaoEncontradaError("Ainda não existe horário gerado para esta turma.")
    turma, plano, curso = _obter_cabecalho(session, turma_id)
    return _renderizar_pdf(turma, plano, curso, resposta)


def gerar_zip_por_job(session: Session, job_id: str) -> bytes:
    """Um .zip com um PDF por turma (nome do ficheiro = código da turma), replicando
    a estrutura de um ficheiro por turma dos exemplares reais do ISAF — todas as
    turmas cobertas por este Job (RF09 — um Job cobre sempre um único
    (ano_letivo, semestre))."""
    job_repo = JobRepository(session)
    job = job_repo.obter(job_id)
    if job is None:
        raise EntidadeNaoEncontradaError("Job não encontrado.")
    if job.status != JobStatus.DONE:
        raise ValueError("Só é possível exportar um Job com status DONE.")

    alocacao_repo = AlocacaoRepository(session)
    alocacoes_todas = alocacao_repo.listar_por_job(job_id)
    turma_ids = sorted({a.turma_id for a in alocacoes_todas})

    horario_service = HorarioService(session)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for turma_id in turma_ids:
            alocacoes_turma = [a for a in alocacoes_todas if a.turma_id == turma_id]
            resposta = horario_service.montar_resposta(job_id, alocacoes_turma)
            turma, plano, curso = _obter_cabecalho(session, turma_id)
            pdf_bytes = _renderizar_pdf(turma, plano, curso, resposta)
            nome_ficheiro = f"{turma.codigo}.pdf" if turma else f"turma_{turma_id}.pdf"
            zf.writestr(nome_ficheiro, pdf_bytes)
    return buffer.getvalue()


def _obter_cabecalho(
    session: Session, turma_id: int
) -> tuple[Turma | None, PlanoCurricular | None, Curso | None]:
    turma = TurmaRepository(session).get(turma_id)
    plano = PlanoCurricularRepository(session).get(turma.plano_curricular_id) if turma else None
    curso = CursoRepository(session).get(plano.curso_id) if plano else None
    return turma, plano, curso


def _renderizar_pdf(
    turma: Turma | None, plano: PlanoCurricular | None, curso: Curso | None, resposta: HorarioResponseSchema
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm,
    )
    estilos = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "Titulo", parent=estilos["Heading1"], alignment=TA_CENTER, fontSize=14, spaceAfter=2
    )
    subtitulo_style = ParagraphStyle(
        "Subtitulo", parent=estilos["Normal"], alignment=TA_CENTER, fontSize=10, spaceAfter=2
    )
    faixa_style = ParagraphStyle(
        "Faixa",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.white,
        spaceBefore=0,
        spaceAfter=0,
    )
    celula_disciplina_style = ParagraphStyle("CelDisc", parent=estilos["Normal"], fontSize=8, leading=10)
    celula_sala_style = ParagraphStyle(
        "CelSala", parent=estilos["Normal"], fontSize=7, textColor=colors.HexColor("#6B7280"), leading=9
    )
    legenda_style = ParagraphStyle("Legenda", parent=estilos["Normal"], fontSize=8, leading=11)

    elementos = []
    elementos.append(Paragraph("Instituto Superior de Administração e Finanças", titulo_style))
    if curso:
        elementos.append(Paragraph(f"Licenciatura: {curso.nome}", subtitulo_style))
    ano_academico = f"{turma.ano_letivo - 1}/{turma.ano_letivo}" if turma else ""
    semestre_label = f"{plano.semestre}º Semestre" if plano and plano.semestre != "Anual" else "Anual"
    ano_curricular_label = f"{plano.ano}º Ano" if plano else ""
    turma_label = f"Turma: {turma.codigo}" if turma else ""
    elementos.append(
        Paragraph(
            f"Ano Académico: {ano_academico} &nbsp;&nbsp;|&nbsp;&nbsp; {semestre_label} "
            f"&nbsp;&nbsp;|&nbsp;&nbsp; {ano_curricular_label} &nbsp;&nbsp;|&nbsp;&nbsp; {turma_label}",
            subtitulo_style,
        )
    )
    elementos.append(Spacer(1, 0.3 * cm))

    faixa = Table(
        [[Paragraph(f"Gerado automaticamente — Sistema ISAF-Horários ({datetime.now():%d/%m/%Y %H:%M})", faixa_style)]],
        colWidths=[doc.width],
    )
    faixa.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), _COR_FAIXA), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    elementos.append(faixa)
    elementos.append(Spacer(1, 0.4 * cm))

    elementos.append(_montar_grelha(resposta, celula_disciplina_style, celula_sala_style))
    elementos.append(Spacer(1, 0.4 * cm))
    elementos.append(_montar_legenda(resposta, legenda_style))

    doc.build(elementos)
    return buffer.getvalue()


def _montar_grelha(resposta: HorarioResponseSchema, estilo_disciplina: ParagraphStyle, estilo_sala: ParagraphStyle) -> Table:
    tempos_por_dia = {dia.dia_semana: dia.tempos for dia in resposta.dias}

    blocos_horario: dict[tuple, None] = {}
    for tempos in tempos_por_dia.values():
        for item in tempos:
            blocos_horario[(item.hora_inicio, item.hora_fim)] = None
    blocos_ordenados = sorted(blocos_horario.keys())

    cabecalho = ["Tempo"] + [_NOME_DIA[dia] for dia in _ORDEM_DIAS]
    linhas = [cabecalho]
    for hora_inicio, hora_fim in blocos_ordenados:
        linha = [f"{hora_inicio.strftime('%H:%M')}\n{hora_fim.strftime('%H:%M')}"]
        for dia in _ORDEM_DIAS:
            item = next(
                (i for i in tempos_por_dia.get(dia, []) if i.hora_inicio == hora_inicio and i.hora_fim == hora_fim),
                None,
            )
            if item is None:
                linha.append("")
            else:
                linha.append(
                    [
                        Paragraph(item.disciplina_nome, estilo_disciplina),
                        Paragraph(item.sala_nome, estilo_sala),
                    ]
                )
        linhas.append(linha)

    tabela = Table(linhas, colWidths=[2.2 * cm] + [4.6 * cm] * len(_ORDEM_DIAS), repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), _COR_CABECALHO_GRELHA),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("FONTSIZE", (0, 1), (0, -1), 8),
    ]
    for i in range(1, len(linhas)):
        if i % 2 == 0:
            estilo.append(("BACKGROUND", (0, i), (-1, i), _COR_LINHA_PAR))
    tabela.setStyle(TableStyle(estilo))
    return tabela


def _montar_legenda(resposta: HorarioResponseSchema, estilo: ParagraphStyle) -> Table:
    pares: dict[str, str] = {}
    for dia in resposta.dias:
        for item in dia.tempos:
            pares[item.disciplina_nome] = item.professor_nome

    linhas = [[Paragraph(f"<b>{disciplina}</b> — {professor}", estilo)] for disciplina, professor in sorted(pares.items())]
    if not linhas:
        linhas = [[Paragraph("Sem alocações.", estilo)]]
    tabela = Table(linhas, colWidths=[24 * cm])
    tabela.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    return tabela
