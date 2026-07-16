# Implementa: RF06, RF07, RF08 (UC06, UC07) — ver docs/04_04_analise_desenvolvimento.md
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.security import require_gestor
from app.schemas.importacao_schema import RelatorioImportacaoSchema
from app.services import importacao_service

# RN09/RN10 — importação em massa é reservada ao Gestor (RF06).
router = APIRouter(prefix="/upload", tags=["Importação"], dependencies=[Depends(require_gestor)])

ENTIDADES_SUPORTADAS = frozenset(
    {
        "cursos",
        "planos_curriculares",
        "professores",
        "turmas",
        "disciplinas",
        "salas",
        "qualificacoes",
        "grade_curricular",
    }
)


@router.post(
    "/excel",
    response_model=RelatorioImportacaoSchema,
    description="""
Importação em massa via .xlsx (RF06/RF07/RF08). Primeira linha = cabeçalho, com as colunas
exatamente pela ordem abaixo (nomes não sensíveis a maiúsculas/minúsculas). Idempotência por
chave única — reimportar ignora linhas cuja chave já exista (não atualiza, não duplica).
Nunca aborta na primeira linha inválida — devolve um relatório com todos os erros.

`turmas` referencia um `plano_curricular` por curso_codigo+ano+semestre (importar
`planos_curriculares` primeiro), que por sua vez referencia um `curso_codigo` (importar
`cursos` primeiro). `qualificacoes` e `grade_curricular` são aditivas (nunca substituem
associações já existentes) e exigem que professores/planos curriculares/disciplinas
referenciados já estejam importados.

**Ficheiro com múltiplas folhas**: ao importar `entidade=planos_curriculares`, se o mesmo
.xlsx tiver também uma folha chamada `grade_curricular`, esta é importada na mesma chamada
(idem para `entidade=professores` + folha `qualificacoes`). As folhas são identificadas pelo
nome, não pela posição — a folha principal pode ter qualquer nome (cai na folha ativa), mas
o complemento só é detetado se a folha se chamar exatamente `grade_curricular`/`qualificacoes`.

| entidade | colunas (nesta ordem) | chave de idempotência |
|---|---|---|
| `cursos` | codigo, nome | codigo |
| `planos_curriculares` | curso_codigo, ano, semestre | (curso_codigo, ano, semestre) |
| `professores` | nome, email, classificacao (1-5), vinculo_casa (true/false) | email |
| `disciplinas` | codigo, nome | codigo |
| `salas` | codigo, nome, capacidade (>0) | codigo |
| `turmas` | codigo, nome, ano_letivo, turno, numero_alunos (>0), curso_codigo, ano, semestre | codigo (curso_codigo+ano+semestre tem de já existir como plano_curricular) |
| `qualificacoes` | professor_email, disciplina_codigo | par (professor_email, disciplina_codigo) |
| `grade_curricular` | curso_codigo, ano, semestre, disciplina_codigo, carga_horaria_semanal (>0) | par (plano_curricular, disciplina_codigo) |
""",
)
async def importar_excel(
    entidade: str,
    file: UploadFile,
    session: Session = Depends(get_session),
) -> RelatorioImportacaoSchema:
    if entidade not in ENTIDADES_SUPORTADAS:
        raise HTTPException(400, f"Entidade inválida. Use uma de: {sorted(ENTIDADES_SUPORTADAS)}")
    conteudo = await file.read()
    try:
        return importacao_service.importar(entidade, conteudo, session)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
