# 3. Especificação Textual dos Casos de Uso
> Parte da Modelagem do Sistema — TFC ISAF. Ver índice geral em [`../modelagem_sistema.md`](../modelagem_sistema.md).
> Depende de [`02_diagrama_casos_uso.md`](02_diagrama_casos_uso.md) (atores, UC01–UC14, relações `<<include>>`/`<<extend>>` já fechadas).

**Estado:** ✅ Fundamentação e aplicação concluídas

---

## 3.1 Definição

O Diagrama de Casos de Uso responde a "quem faz o quê" — mas não descreve *como*. Segundo [@cockburn2000], o próprio diagrama gráfico da UML (elipses, setas, bonecos de palito) mostra apenas o empacotamento e a decomposição dos casos de uso, não o seu conteúdo real; o contrato de comportamento entre os stakeholders e o sistema só existe, de facto, na descrição textual. É por isso que este artefacto é indispensável antes de avançar para os diagramas de comportamento mais técnicos (Classes, Sequência, Atividade): sem ele, `<<include>>` e `<<extend>>` seriam apenas setas sem semântica documentada.

Este artefacto combina duas tradições complementares:

1. [@cockburn2000], *Writing Effective Use Cases* — referência internacional que formaliza o conceito de **caso de uso "fully dressed"** (totalmente vestido): estabelece campos como *Primary Actor*, *Goal/Level*, *Stakeholders and Interests*, *Preconditions*, *Trigger*, *Main Success Scenario*, *Extensions*, *Success Guarantee* e *Minimal Guarantee* — este último particularmente valioso para o ISAF, pois obriga a documentar o que o sistema garante **mesmo quando o caso de uso falha** (ex.: cenário INFEASIBLE, RF13).
2. **Convenção académica de língua portuguesa (base RUP)** — amplamente usada em TFCs/TCCs da região, com nomenclatura em português: Ator(es), Gatilho, Pré-condição(ões), Pós-condição(ões), Fluxo Principal, Fluxos Alternativos, Fluxos de Exceção, Regras de Negócio, Referências (Include/Extend).

A fusão destas duas fontes dá ao capítulo o rigor conceptual de Cockburn com a nomenclatura em português já usada por [@guedes2011] e reconhecida pelo modelo institucional do ISAF.

## 3.2 Regras de Construção (Template Adotado)

| Campo | Definição | Fonte |
|---|---|---|
| **Nome** | Idêntico ao já definido no Diagrama de Casos de Uso (verbo + objeto) | [@guedes2011] |
| **Ator(es)** | Principal (dono do objetivo) e secundário(s), se houver | [@cockburn2000] |
| **Nível do Objetivo (Goal Level)** | *User goal* (a maioria dos UCs do ISAF), *Summary* (objetivo composto por vários user goals) ou *Subfunction* (passo demasiado pequeno para ser um UC — não deve aparecer no diagrama, regra já aplicada em 2.2.9) | [@cockburn2000] |
| **Pré-condição(ões)** | O que já tem de ser verdade antes do caso de uso começar; **não é testado dentro do próprio UC** — é assumido | [@cockburn2000] |
| **Gatilho (Trigger)** | Evento ou intenção que dá início ao fluxo | [@cockburn2000] |
| **Fluxo Principal** | Sequência numerada de passos ator↔sistema, sem desvios; idealmente entre 3 e 9 passos (acima disso, o caso de uso provavelmente devia ser decomposto) | [@cockburn2000] |
| **Fluxos Alternativos** | Desvios previstos e válidos do fluxo principal (ex. cancelar a meio); identificados como `Axx` | Convenção RUP/PT |
| **Fluxos de Exceção** | Situações de erro/falha; identificados como `Exx` | Convenção RUP/PT |
| **Pós-condição / Garantia de Sucesso** | Estado obrigatório do sistema quando o caso termina com sucesso | [@cockburn2000] |
| **Garantia Mínima** | O que o sistema garante **mesmo que o caso de uso falhe** — nunca deixar o sistema num estado inconsistente ou falhar silenciosamente | [@cockburn2000] |
| **Regras de Negócio associadas** | Referência cruzada às RNs de `analise_requisitos.md` | Convenção RUP/PT |
| **Relações (`<<include>>`/`<<extend>>`)** | Referência cruzada ao Diagrama de Casos de Uso já fechado | [@omguml] |

**Decisão de granularidade de escrita** (justificada por Cockburn, que dedica uma secção específica a *"CRUD and parameterised use cases"*): casos de uso CRUD estruturalmente idênticos, diferindo apenas na entidade envolvida (UC01–UC04), são escritos **uma única vez, de forma parametrizada**, em vez de repetidos 4 vezes — evita redundância sem perder rigor. Casos de uso simples de consulta (UC10–UC12) são escritos em **formato casual** (mais compacto); os casos de uso centrais ou com lógica condicional relevante (UC05–UC09, UC13, UC14) são escritos em **formato *fully dressed*** completo.

## 3.3 Fontes

- [@cockburn2000] — referência primária desta secção: define o template *fully dressed*, os conceitos de pré-condição/gatilho/garantias, os níveis de objetivo, e o tratamento de casos de uso CRUD/parametrizados.
- [@guedes2011] — mantém a nomenclatura em português já usada nos artefactos anteriores.
- [@bittnerspence2002] — reforça o tratamento de pré-condições como atributo textual do caso de uso, já usado em 2.4.3 para justificar a não-representação gráfica da autenticação.
- [@omguml] — mantém a coerência das relações `<<include>>`/`<<extend>>` já fechadas no artefacto anterior.

---

## 3.4 Aplicação ao Projeto ISAF

### 3.4.1 UC01–UC04 — Gerir Professores / Turmas / Disciplinas / Salas (CRUD parametrizado)

| Campo | Descrição |
|---|---|
| **Ator Principal** | Gestor Académico/Secretaria |
| **Nível** | User goal |
| **Pré-condição** | Gestor autenticado com sucesso (UC13) |
| **Gatilho** | Gestor seleciona "Gerir `<Entidade>`" no menu, onde `<Entidade>` ∈ {Professor, Turma, Disciplina, Sala} |
| **Fluxo Principal (Criar)** | 1. Gestor solicita criação de novo registo de `<Entidade>`. 2. Sistema apresenta formulário com os campos obrigatórios da entidade. 3. Gestor preenche os dados e confirma. 4. Sistema valida formato e obrigatoriedade dos campos. 5. Sistema grava o registo e apresenta confirmação. |
| **Fluxos Principais análogos** | Consultar (listar/filtrar), Atualizar (editar campos de um registo existente) e Eliminar seguem a mesma estrutura de 5 passos, substituindo o verbo no passo 1 |
| **Fluxo de Exceção E1** | Dados inválidos no passo 4 → sistema rejeita e informa os campos problemáticos, sem gravar |
| **Fluxo de Exceção E2** | Tentativa de eliminar um registo com dependências ativas (ex. Professor já alocado num horário gerado) → sistema bloqueia a eliminação e informa o motivo |
| **Pós-condição / Garantia de Sucesso** | Registo de `<Entidade>` refletido no repositório de dados mestre, disponível para Importação (RF06) e Geração de Horário (RF09) |
| **Garantia Mínima** | Nenhum registo parcialmente gravado — operação atómica |
| **Regras de Negócio** | Alimenta indiretamente RN01–RN08 (os dados mestre são a base de todas as restrições do solver) |

### 3.4.2 UC05 — Registar Disponibilidade

- **Ator Principal:** Professor · **Nível:** User goal
- **Pré-condição:** Professor autenticado (UC13); conta de Professor já criada previamente pelo Gestor (UC01)
- **Gatilho:** Professor acede à secção "A Minha Disponibilidade"
- **Fluxo Principal:** 1. Professor solicita registar disponibilidade. 2. Sistema apresenta grelha semanal de slots. 3. Professor seleciona os slots em que está disponível. 4. Professor confirma. 5. Sistema grava a disponibilidade associada ao Professor.
- **Fluxo Alternativo A1 — Disponibilidade já existente:** sistema apresenta o registo atual pré-preenchido para edição, em vez de um formulário vazio.
- **Fluxo de Exceção E1 — Nenhum slot selecionado:** sistema aplica RN07 (professor tratado como totalmente disponível) e informa o Professor desta implicação antes de confirmar.
- **Pós-condição / Garantia de Sucesso:** disponibilidade do Professor disponível para o motor CP-SAT na próxima geração de horário.
- **Regras de Negócio:** RN07.

### 3.4.3 UC06 — Importar Dados em Massa via Excel *(fully dressed — inclui UC07)*

- **Ator Principal:** Gestor · **Nível:** User goal
- **Pré-condição:** Gestor autenticado (UC13); ficheiro Excel no formato institucional esperado para a entidade selecionada
- **Gatilho:** Gestor seleciona "Importar Dados" e escolhe a entidade-alvo
- **Fluxo Principal:**
  1. Gestor seleciona a entidade e carrega o ficheiro Excel.
  2. Sistema invoca **UC07 — Validar Dados Importados** (`<<include>>`).
  3. Sistema apresenta o resultado da validação (registos válidos, inválidos, duplicados) para confirmação do Gestor.
  4. Gestor confirma a gravação dos registos válidos e não duplicados.
  5. Sistema aplica a regra de idempotência (RF08): ignora registos cuja chave institucional já exista.
  6. Sistema grava os registos novos e apresenta relatório final (nº criados / ignorados / rejeitados).
- **Fluxo Alternativo A1 — Cancelamento antes da confirmação (passo 3):** sistema descarta o lote; nenhum dado é gravado.
- **Fluxo de Exceção E1 — Ficheiro em formato inválido (passo 1):** sistema rejeita o ficheiro e informa o formato esperado.
- **Pós-condição / Garantia de Sucesso:** registos válidos e não duplicados persistidos na base de dados mestre da entidade selecionada.
- **Garantia Mínima:** nenhum registo parcialmente importado — falha a meio do lote não deixa dados inconsistentes (operação transacional).
- **Regras de Negócio:** RF08 (idempotência, ver `analise_requisitos.md`).
- **Relação:** inclui UC07.

### 3.4.4 UC07 — Validar Dados Importados *(incluído por UC06)*

- **Ator:** Gestor (indireto — acionado pelo Sistema dentro do fluxo de UC06)
- **Pré-condição:** ficheiro já recebido pelo Sistema (interno ao fluxo de UC06)
- **Fluxo Principal:** 1. Sistema lê cada linha do ficheiro. 2. Sistema verifica obrigatoriedade de campos, tipos e formatos. 3. Sistema verifica a unicidade da chave institucional (deteção prévia de duplicados, RF08). 4. Sistema classifica cada linha como Válida, Inválida ou Duplicada. 5. Sistema devolve o relatório de classificação ao caso de uso incluidor (UC06).
- **Fluxo de Exceção E1 — Ficheiro vazio:** sistema devolve relatório vazio com mensagem informativa.
- **Pós-condição:** cada linha do ficheiro classificada, pronta para decisão de gravação em UC06.

### 3.4.5 UC08 — Disparar Geração de Horário *(fully dressed — estendido por UC09)*

- **Ator Principal:** Gestor · **Nível:** User goal
- **Pré-condição:** dados mestre completos (Professores, Turmas, Disciplinas, Salas) e disponibilidades registadas (RF05); Gestor autenticado
- **Gatilho:** Gestor seleciona "Gerar Horário"
- **Fluxo Principal:**
  1. Gestor solicita a geração do horário.
  2. Sistema cria um Job assíncrono e devolve um Job ID (RNF02).
  3. Sistema executa o motor CP-SAT em segundo plano, aplicando RN01–RN09 e a função objetivo definida em `analise_requisitos.md` (Secção 5).
  4. Motor CP-SAT devolve uma solução ótima ou quase-ótima. **[Ponto de Extensão: "Sem Solução Viável"]**
  5. Sistema associa o resultado ao Job ID e marca o estado como "Concluído".
- **Fluxo Alternativo A1 — Consulta durante o processamento:** delega para UC10 (Consultar Estado de Processamento), sem interromper o processamento em curso.
- **Extensão condicional (passo 4):** se o solver retornar um estado próximo de INFEASIBLE mesmo após esgotar o relaxamento das soft constraints, o Sistema invoca **UC09 — Notificar Cenário Sem Solução Viável** (`<<extend>>`).
- **Pós-condição / Garantia de Sucesso:** horário completo persistido e disponível para consulta (UC11, UC12).
- **Garantia Mínima:** mesmo em caso de INFEASIBLE, o Job é marcado como "Falhado" com o motivo registado — o sistema nunca falha silenciosamente (RNF03).

### 3.4.6 UC09 — Notificar Cenário Sem Solução Viável *(estende UC08)*

- **Ator:** Gestor
- **Condição de extensão:** o solver não consegue satisfazer as hard constraints mesmo após esgotadas as alternativas de relaxamento das soft constraints.
- **Fluxo:** 1. Sistema identifica que não existe solução viável completa. 2. Sistema regista o(s) motivo(s) específico(s) do conflito (ex. professor X sem nenhuma janela compatível com a Turma Y). 3. Sistema notifica o Gestor com o relatório de conflito. 4. Gestor intervém manualmente fora do sistema (negociação direta com o professor — fora do escopo do sistema, conforme Secção 5 de `analise_requisitos.md`).
- **Pós-condição:** Gestor informado com detalhe suficiente para decidir a ação seguinte.

### 3.4.7 UC10 — Consultar Estado de Processamento *(casual)*

- **Ator:** Gestor · **Pré-condição:** Job ID válido de uma geração já disparada (UC08).
- **Fluxo:** Gestor fornece o Job ID → Sistema devolve o estado atual (Em Processamento / Concluído / Falhado) e, se concluído, a referência ao horário gerado.

### 3.4.8 UC11 — Consultar Horário por Turma *(casual)*

- **Ator:** Gestor · **Pré-condição:** existe pelo menos um horário gerado com sucesso.
- **Fluxo:** Gestor seleciona a Turma → Sistema devolve o horário semanal dessa Turma.

### 3.4.9 UC12 — Consultar Horário por Professor *(casual)*

- **Ator:** Gestor, Professor · **Pré-condição:** existe pelo menos um horário gerado com sucesso.
- **Fluxo:** Ator seleciona (ou, no caso do Professor, acede diretamente ao) horário do Professor → Sistema devolve o horário semanal correspondente.
- **Nota de autorização:** quando o Ator é o próprio Professor, o Sistema restringe a consulta ao seu próprio horário — nunca ao de terceiros (regra de autorização decorrente de RN09).

### 3.4.10 UC13 — Autenticar-se *(fully dressed)*

- **Ator Principal:** Gestor, Professor · **Nível:** User goal
- **Pré-condição:** ator possui conta registada no Firebase Authentication (contas de Professor são criadas previamente pelo Gestor, via UC01)
- **Gatilho:** ator submete credenciais no ecrã de login
- **Fluxo Principal:**
  1. Ator submete email e password.
  2. A aplicação Flutter envia as credenciais ao Firebase Authentication (SDK nativo).
  3. Firebase valida as credenciais e devolve um ID Token.
  4. A aplicação Flutter anexa o ID Token a cada pedido subsequente ao backend FastAPI.
  5. O backend valida o ID Token via Firebase Admin SDK antes de processar qualquer pedido (RN09).
- **Fluxo de Exceção E1 — Credenciais inválidas:** Firebase rejeita a autenticação; a aplicação apresenta uma mensagem de erro genérica, sem indicar se foi o email ou a password que falhou (boa prática de segurança — evita enumeração de contas).
- **Fluxo de Exceção E2 — Token expirado num pedido posterior:** backend devolve HTTP 401; o SDK do Firebase tenta um refresh silencioso do token; só é exigido novo login se esse refresh também falhar.
- **Pós-condição / Garantia de Sucesso:** ator possui um ID Token válido, incluído em todos os pedidos subsequentes ao backend.
- **Garantia Mínima:** nenhuma sessão é criada sem validação bem-sucedida da identidade.
- **Regras de Negócio:** RN09.

### 3.4.11 UC14 — Recuperar Password *(casual)*

- **Ator:** Gestor, Professor · **Pré-condição:** ator possui conta registada com email válido.
- **Fluxo:** Ator solicita "Esqueci-me da password" → Firebase envia email com link de reset → Ator define nova password através do fluxo nativo do Firebase.
- **Nota:** por ser delegado inteiramente ao Firebase (RF16), o Sistema (FastAPI/CP-SAT) não participa deste fluxo além de disponibilizar a opção na interface Flutter.

---

> **Nota de rastreabilidade:** todas as pré-condições "ator autenticado (UC13)" acima materializam, caso a caso, a decisão registada em `02_diagrama_casos_uso.md` (2.4.3) de tratar a autenticação como pré-condição textual transversal, em vez de uma relação `<<include>>` desenhada a partir de cada caso de uso.