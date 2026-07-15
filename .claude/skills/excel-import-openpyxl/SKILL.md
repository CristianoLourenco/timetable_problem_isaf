---
name: excel-import-openpyxl
description: Use ao implementar ou alterar importacao_service.py, o endpoint POST /upload/excel, ou qualquer fluxo de importação em massa de Docentes/Turmas/Disciplinas/Salas a partir de ficheiros .xlsx institucionais. Cobre RF06 (importar), RF07 (validar) e RF08 (idempotência).
---

# Importação de dados via Excel (ISAF)

## Fluxo obrigatório: validar → confirmar → idempotência

RF06 inclui obrigatoriamente RF07 (UC06 `<<include>>` UC07). O fluxo nunca grava direto:

1. **Parse** — ler o `.xlsx` com `openpyxl`, uma função de parser por entidade (Docente, Turma, Disciplina, Sala).
2. **Validar (RF07)** — checar estrutura (colunas esperadas presentes), tipos, obrigatoriedade de campos, e integridade referencial (ex: `Turma.curso_id` existe). Devolver uma lista estruturada de erros por linha — nunca abortar no primeiro erro sem reportar os restantes.
3. **Confirmar** — a gravação só acontece depois da validação passar (ou após confirmação explícita do Gestor, se o fluxo UI pedir revisão antes de gravar).
4. **Idempotência (RF08)** — reimportação ignora registos já existentes com base na chave institucional única (`codigo`). Nunca duplicar por reimportação do mesmo ficheiro. Usar `INSERT ... ON CONFLICT DO NOTHING`-equivalente via SQLModel/upsert, ou verificação explícita antes do insert.

## Onde vive isto

`importacao_service.py` na camada `services/` (ver skill `fastapi-clean-architecture`) — nunca lógica de parsing dentro do router. O router apenas recebe o `UploadFile`, chama o service, devolve o relatório de importação (linhas aceites / linhas rejeitadas com motivo).

## Relatório de importação (contrato de resposta)

Estruturar sempre como resumo + detalhe, nunca só "sucesso"/"erro" genérico:

```json
{
  "total_linhas": 42,
  "importados": 39,
  "ignorados_idempotencia": 2,
  "erros": [
    {"linha": 17, "campo": "email", "motivo": "email institucional em falta"}
  ]
}
```

Mensagens de `motivo` em português (Angola) — vão diretamente para a UI do Gestor.

## Testes

Cobrir pelo menos: ficheiro válido completo, ficheiro com uma linha inválida (deve reportar sem abortar as restantes), reimportação do mesmo ficheiro (deve ser idempotente e não duplicar).
