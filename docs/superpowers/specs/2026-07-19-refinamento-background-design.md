# Refinamento em Background do Resultado do Solver — Ideia (não implementado)

Registado em 2026-07-19, durante a investigação de performance do solver (redução de tempo de
geração + nº de pendências). Não faz parte do trabalho de performance em curso — fica como ideia
a retomar depois, com o mesmo processo (spec detalhado → plano → TDD) dos sub-projetos anteriores.

## Problema que motivou a ideia

Com `relative_gap_limit` mais largo (0.30, ver commit da mudança de performance), o CP-SAT aceita
mais depressa uma solução "suficientemente boa" — incluindo défice residual (pendências) mesmo em
cenários genuinamente resolúveis sem nenhuma pendência, se o défice pequeno já satisfizer o gap
antes do teto de tempo. Gap mais apertado (ex: 0.10) evitava isso mas era a causa principal da
lentidão original (~17min no pior caso).

## Ideia: entregar rápido, refinar depois, nunca substituir sem confirmação

1. Devolver ao Gestor o resultado `FEASIBLE` (com pendências) assim que disponível — RF09 continua
   rápido, sem esperar pelo refinamento.
2. Continuar a refinar em background (gap mais apertado e/ou mais tempo), tentando reduzir/eliminar
   as pendências desse mesmo Job.
3. Se o Gestor tentar alocar manualmente enquanto o refinamento decorre, avisar que o horário está
   a ser refinado; se ele prosseguir com a alocação manual mesmo assim, o refinamento em background
   para definitivamente para esse Job (nunca sobrescreve trabalho manual) e o resultado manual passa
   a ser considerado o final.
4. Quando o refinamento terminar (e não tiver sido cancelado pelo passo 3), comparar o nº de
   pendências novo vs. antigo e perguntar ao Gestor se quer substituir o resultado atual pelo
   refinado — nunca substituir silenciosamente.

## Implicações a desenhar quando isto for retomado

- Novo estado/campo em `Job` (algo como "a refinar" + guardar as pendências anteriores para
  comparar depois).
- Um processo de background separado do `job_runner.executar` original (ou uma extensão dele).
- Endpoints novos: notificar o Gestor que há refinamento em curso, comparar resultado antigo vs.
  novo, confirmar/recusar a substituição.
- Detetar alocação manual em curso (RF13, sub-projeto "alocação manual") para cancelar o
  refinamento no momento certo.
- UI no frontend para a notificação/comparação/confirmação.

## Fora de âmbito por agora

O foco imediato é reduzir o tempo total de geração e o nº de pendências na geração síncrona
(tempo dinâmico por turno, ajuste de `relative_gap_limit`/`solver_peso_deficit_rn05`) — este
documento só regista a ideia para não se perder, não é um compromisso de implementação.
