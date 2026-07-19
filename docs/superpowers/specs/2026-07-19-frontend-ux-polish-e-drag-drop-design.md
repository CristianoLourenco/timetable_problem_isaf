# Frontend — Polimento de UX, Padronização de Tabelas e Alocação Manual em Drag-and-Drop — Design

Só UI — nenhuma mudança de contrato de API está implicada aqui (os endpoints
já existem e já foram testados no backend, ver commits
`e21eced`/`92fb537`/`f596fe3` em `feat/backend-fase8-solver-performance`).
Se algo parecer exigir um endpoint novo ou um campo que a API não devolve,
parar e reportar antes de inventar um contrato — não modelar dados no cliente
que já deviam vir resolvidos do backend.

## Stack (obrigatório, ver CLAUDE.md raiz)
Flutter + GoRouter, Provider (global) + ValueNotifier (local), Clean
Architecture (`data/domain/presentation/ui`). Sem Riverpod/Bloc/GetX. Usar
Material widgets nativos do Flutter (`NavigationRail`/`Drawer` colapsável,
`DataTable`/`Table`, `DropdownButton`) em vez de componentes customizados do
zero sempre que o Material já resolver o requisito.

## Contexto — bugs visuais e de dados observados (screenshots anexados pelo utilizador)

1. Cards de turma com **overflow visível** ("BOTTOM OVERFLOWED BY N PIXELS")
   tanto na visão de grelha como na de lista — acontece quando o nome do curso
   é longo.
2. **Pendências** ("N turmas/disciplinas por distribuir") também têm overflow
   nos botões/cards.
3. Menu lateral atual é uma coluna fixa de texto — não é colapsável, não usa
   componentes Material, e o card de perfil do utilizador fica na parte
   **inferior** (deveria estar no **topo**).
4. Card de professor (ficha do docente) mostra a grade de disciplinas
   lecionadas como uma lista de botões repetidos por turma — quando a mesma
   disciplina é lecionada a várias turmas, o nome da disciplina repete-se em
   vez de aparecer uma vez com as turmas agrupadas.
5. Cards de turma às vezes aparecem **sem dados** (nome do curso em branco,
   ano incorreto) — corrigido no backend nesta sessão com o endpoint
   `GET /turmas-detalhadas` (ver secção "Endpoints a consumir/trocar").

## Endpoints a consumir/trocar

```
GET /turmas-detalhadas
```
Substitui qualquer lógica no cliente que hoje tenta juntar `Turma` +
`PlanoCurricular` + `Curso` para montar o card/linha de uma turma. Devolve já
resolvido, por turma:
```json
{
  "id": 1, "codigo": "IGF1S1-T1", "nome": "...", "ano_letivo": 2026,
  "turno": "tarde", "numero_alunos": 33, "plano_curricular_id": 4,
  "curso_codigo": "IGF", "curso_nome": "Informática de Gestão Financeira",
  "ano_curricular": 1
}
```
- **`ano_curricular`** (1..4) é o que deve aparecer como "1º/2º/3º/4º Ano" no
  card — **nunca** `ano_letivo` (esse é o ano civil, ex: 2026, mostrado
  separadamente se necessário, ex: "Ano letivo: 2026").
- **`curso_codigo`** é a sigla (ex: "IGF") — usar isto na visão de **card**
  (grelha), nunca `curso_nome` completo, para nunca mais dar overflow por
  nome de curso longo.
- Na visão de **lista/linha** (row), pode mostrar as duas colunas lado a
  lado: `Curso: IGF | Descrição: Informática de Gestão Financeira` — aqui
  há espaço horizontal suficiente, não corta.
- Se `curso_codigo == "?"` ou `ano_curricular == 0`: o backend está a
  sinalizar um dado órfão (`plano_curricular_id` inválido) — mostrar um
  placeholder claro tipo "Dados incompletos" em vez de esconder o card ou
  mostrar campos vazios/quebrados.

```
GET /jobs?ano_letivo={ano}&semestre={semestre}
```
Devolve `{"job": JobRead | null}`. Chamar sempre que o Gestor mudar o filtro
de ano/semestre na tela de Horários — **nunca** reutilizar o job mais recente
global entre trocas de filtro. `job: null` = "ainda não gerado" para este
âmbito → mostrar estado vazio (ex: "Nenhum horário gerado para 2027/2º
Semestre. Gerar Horário?"), não um erro.

```
DELETE /jobs/{job_id}
```
Botão **"Limpar Horário"** — chama isto para o `job_id` do âmbito
atualmente selecionado (vindo do `GET /jobs?...` acima). Sucesso = 204 sem
corpo. Depois de limpar, re-consultar `GET /jobs?ano_letivo=&semestre=` (deve
devolver `job: null`) e atualizar a UI para o estado vazio. Pedir confirmação
antes de chamar (ação destrutiva — apaga todas as alocações e pendências
desse job).

```
GET /horarios/turma/{turma_id}
```
Agora pode devolver **200 com corpo `null`** quando a turma existe mas ainda
não há horário gerado para o seu âmbito (antes era 404) — tratar isso como
"sem horário ainda", não como erro de rede/turma inválida. Cada item da
grade já inclui **`sala_nome`** — se a UI hoje não mostra a sala alocada,
adicionar (o dado já vem no payload, não precisa de mudança de API).

```
GET /horarios/turma/{turma_id}/pdf
GET /jobs/{job_id}/exportar-pdf
```
Investigados no backend nesta sessão — `gerar_pdf_turma`/`gerar_zip_por_job`
funcionam corretamente (testado diretamente, produzem PDF/ZIP válidos). O bug
relatado ("exportar não funciona") deve estar no lado Flutter: verificar (a)
se o token de autenticação Firebase está a ser enviado no cabeçalho deste
pedido específico (`dio_client_interceptor.dart`), (b) se a resposta binária
está a ser tratada como `ResponseType.bytes` no Dio (não `json`), (c) se
`file_share_service.dart` está a receber e a gravar os bytes corretamente
antes de partilhar/abrir o ficheiro. Reproduzir com um `job_id` real (há
sempre pelo menos um horário gerado na BD de desenvolvimento) e inspecionar
o response completo (status, headers, content-length) antes de assumir a
causa.

## Funcionalidade 1 — Menu lateral: colapsável, Material, perfil no topo

- Trocar a coluna de texto atual por `NavigationRail` (para desktop/tablet
  largo) ou `Drawer` (mobile/estreito) — ambos widgets Material nativos.
- `NavigationRail` deve suportar o modo colapsado (`extended: false`) —
  mostra só os ícones — com um botão/gesto para expandir e mostrar os
  rótulos. Guardar a preferência (expandido/colapsado) em `SharedPreferences`
  ou equivalente já usado no projeto, não perder ao reiniciar a app.
  Não introduzir bibliotecas novas de menu — os widgets Material padrão do
  Flutter já cobrem este requisito (ver CLAUDE.md — perguntar antes de
  introduzir libs).
- O card do utilizador logado (avatar + email + perfil + "Terminar Sessão")
  passa para o **topo** do menu, antes dos itens de navegação — não no
  rodapé como está hoje.

## Funcionalidade 2 — Overflow: sigla do curso no card, coluna de descrição na linha

Ver secção "Endpoints a consumir" acima (`GET /turmas-detalhadas`) para os
campos exatos. Regra geral para qualquer card com texto potencialmente longo
(nome de curso, nome de disciplina, nome de turma): usar `Expanded`/`Flexible`
+ `TextOverflow.ellipsis` como rede de segurança, mesmo já usando a sigla —
nunca confiar só em "o texto agora é curto" para eliminar overflow
definitivamente, sempre truncar com reticências se ainda assim não couber
(ex: em ecrãs muito estreitos).

## Funcionalidade 3 — Tabelas padronizadas (header, search, filtro)

Aplicar o mesmo padrão visual e estrutural a **todas** as tabelas/listagens
do sistema (Professores, Turmas, Cursos, Disciplinas, Salas, etc. — qualquer
tela com `DataTable`/lista tabular):

- **Header da tabela**: precisa de contraste visível com as linhas de dados —
  hoje "demasiado comum", indistinguível do corpo. Usar um `Container`/
  `DataColumn` com background de cor sólida (ex: `AppColors.blackBlue` ou
  similar já usado no design system do projeto — reaproveitar, não inventar
  cor nova) + texto em negrito/branco.
- **Search**: campo de busca por texto livre, mesmo posicionamento em todas
  as telas (topo da tabela, ao lado do título).
- **Filtro**: dropdowns (nunca campos de texto livre para filtro) — para a
  tela de Turmas especificamente, filtros por **Ano** (curricular, 1-4),
  **Curso** e **Turno**. Cada filtro é um dropdown independente, combináveis
  entre si (AND).
- **Linhas clicáveis**: em Professores (e por extensão, qualquer entidade
  com uma "ficha"/detalhe — Turmas, Disciplinas), a linha inteira deve ser
  clicável para navegar à ficha/detalhe — não só um ícone/botão no final da
  linha. Usar `InkWell`/`GestureDetector` a envolver a `Row`/`DataRow`
  inteira, com `hover`/`splash` visual de que é clicável.

## Funcionalidade 4 — Ficha do Professor: disciplinas agrupadas, sem duplicação

Na ficha do professor, a lista de disciplinas lecionadas deve:
- Mostrar cada disciplina **uma única vez** (nunca repetir o nome da
  disciplina por cada turma que a leciona).
- Sob cada disciplina, listar as turmas associadas (repetição de turmas é
  esperada e correta — é a disciplina que não deve repetir).
- Usar a **sigla/código da turma** (ex: `T1`, `T2`, `N1` — o sufixo já usado
  em `Turma.codigo`, ver `seed_dados_teste.py` para o formato exato:
  `{curso}{ano}S{semestre}-{turma_codigo}`) para identificar cada turma
  dentro do grupo, não o nome completo — mesmo princípio de "usar siglas
  para simplificar" já aplicado ao curso.
- Deve ser possível **associar uma nova disciplina** ao professor a partir
  desta ficha. Endpoints já existentes e confirmados:
  ```
  GET  /professores/{professor_id}/disciplinas   -> {disciplina_ids: [int]}
  POST /professores/{professor_id}/disciplinas   body: {disciplina_ids: [int]}
  ```
  **Atenção**: `POST` **substitui** a lista inteira de qualificações (não é
  "adicionar uma", é "definir o conjunto completo") — ao associar uma nova
  disciplina na UI, buscar primeiro a lista atual (`GET`), acrescentar o novo
  `disciplina_id`, e enviar o array completo resultante no `POST`. Enviar só
  `[novo_id]` apagaria todas as qualificações anteriores do professor.
- Como a ficha agora já mostra as disciplinas lecionadas de forma clara e
  agrupada, **remover** a duplicação anterior de cards de disciplina soltos
  associados ao horário do professor (o padrão antigo mencionado pelo
  utilizador) — uma única fonte de verdade visual para "que disciplinas este
  professor leciona".

## Funcionalidade 5 — Alocação manual em drag-and-drop

Reformular o fluxo de alocação manual (hoje um diálogo com dropdowns) para
manipulação direta na grelha do horário:

- Cada célula da grelha (dia × período) é um slot. Um slot **livre** (sem
  alocação) tem uma cor/estado visual distinto de um slot **ocupado por
  outra turma/turno do mesmo professor** (ex: cinza para "professor ocupado
  noutro compromisso", branco/vazio para "livre"). A distinção visual exata
  fica a critério de design, mas as duas categorias devem ser
  inequivocamente diferentes (cor de fundo, não só texto).
- **Clicar** num slot livre (dia+hora) abre um diálogo pequeno para escolher
  Turma + Disciplina (só se o professor tiver mais de uma combinação
  possível nesse contexto — se só houver uma opção, pré-selecionar e pedir
  só confirmação). Isto substitui o fluxo de dropdowns completo do início ao
  fim — o clique no slot já fixa dia/hora/professor, só falta turma/
  disciplina (e sala, se aplicável).
- **Arrastar** (drag-and-drop) uma alocação já existente de um slot para
  outro slot livre é a forma de **mover** um horário já preenchido — nunca
  deve ser possível arrastar por cima de um slot que já quebraria outra
  restrição do próprio professor (RN01 — sem dupla alocação). Bloquear
  visualmente o drop nesses slots (ex: não realçar como destino válido
  durante o arrasto).
- Diferença chave face ao desenho anterior de alocação manual: aqui a
  associação é **sempre 1 slot de cada vez** (não é preciso escolher um
  bloco de N períodos consecutivos de uma vez) — o Gestor pode ir montando a
  grade período a período, deixando "buracos" temporários até ficar completa.

  **Já implementado no backend nesta sessão** (RN06, bloco contíguo >=2, era
  a regra do solver automático — nunca foi para a alocação manual, agora
  corrigido): `POST /alocacoes` aceita `periodos` de tamanho 1 sem erro, e
  `GET /turmas/{turma_id}/slots-vagos?job_id=X` agora também devolve blocos
  de tamanho 1 (um período isolado entre duas alocações já existentes) como
  opção selecionável — antes só devolvia blocos com 2+ períodos contíguos.
  Nada a fazer do lado do contrato de API — implementar a UI já assumindo
  este comportamento.

### Nota sobre "tempos letivos de disciplina do plano curricular"

O utilizador pediu para não implementar nada aqui ainda, só explicar como o
cálculo é feito hoje, para ele reunir mais informação antes de decidir:
`PlanoCurricularDisciplina.carga_horaria_semanal` é o número de tempos (não
horas) que uma disciplina deve ter por semana para um dado
`PlanoCurricular` (curso+ano+semestre) — é este valor que
`add_carga_horaria_cumprida` (RN05, `app/solver/constraints_hard.py`) tenta
igualar (ou aproximar, já que RN05 hoje é soft-com-défice) durante a geração
automática. Não há lógica adicional de "tempos letivos" derivada de outra
fonte — o valor vem diretamente desse campo, definido manualmente ao
importar/criar a grade curricular (RF06-08). Não implementar nenhuma mudança
aqui até o utilizador confirmar o que quer.

## Fora de âmbito por agora

- Refinamento em background do resultado do solver — spec separado, ver
  `2026-07-19-refinamento-background-design.md`.
- Qualquer mudança ao cálculo de `carga_horaria_semanal` — ver nota acima.
- Anonimização do seed de dados de teste — pendência já registada no
  `backend/README.md` secção 10.
