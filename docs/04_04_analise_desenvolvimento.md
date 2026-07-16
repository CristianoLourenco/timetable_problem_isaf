4. ANÁLISE, DESENVOLVIMENTO E DISCUSSÃO DOS
RESULTADOS

Este capítulo apresenta o percurso técnico e analítico do
desenvolvimento do sistema, estruturado em seis secções que cobrem desde
o levantamento de requisitos até à discussão crítica dos resultados
obtidos. A sequência adoptada é coerente com a metodologia RUP descrita
na Secção 3.9.2 e com os princípios de engenharia de requisitos
estabelecidos na Secção 3.

4.1 Levantamento de requisitos

O levantamento de requisitos constitui a etapa fundacional do
desenvolvimento de qualquer sistema de software. Seguindo os critérios
de qualidade da norma IEEE 830 --- correcta, completa, clara,
consistente, modificável, priorizada, verificável e rastreável --- os
requisitos do sistema foram elicitados a partir das entrevistas
realizadas com a gestão académica do ISAF, da análise documental dos
horários vigentes e da revisão da literatura científica sobre o UCTP
(IEEE, 1998; ISO/IEC/IEEE, 2011).

De acordo com a norma ISO/IEC/IEEE 29148:2011, os requisitos de sistemas
e software devem expressar necessidades, propriedades esperadas e
especificações verificáveis ao longo do ciclo de vida do produto
(ISO/IEC/IEEE, 2011). Neste trabalho, a necessidade central identificada
é a seguinte: a gestão pedagógica do ISAF necessita de gerar horários
académicos de forma automática, eliminando os conflitos de alocação de
docentes e salas que ocorrem no processo manual actualmente utilizado. A
propriedade esperada determina que o motor algorítmico opere sob
princípios de inteligência artificial simbólica, nomeadamente resolução
de restrições por CSP/CP, rejeitando aproximações probabilísticas que
comprometam a integridade e a verificabilidade dos horários produzidos.
A especificação é documentada nas tabelas de requisitos funcionais e não
funcionais que se seguem.

4.1.1 Glossário técnico

Seguindo a directriz de modificabilidade da norma IEEE 830, que
recomenda a utilização de glossário para evitar ambiguidades e
redundâncias ao longo da especificação, apresenta-se de seguida a
definição formal dos termos técnicos utilizados neste capítulo (IEEE,
1998).

  -----------------------------------------------------------------------
  Termo                Definição
  -------------------- --------------------------------------------------
  CB-CTT               Curriculum-Based Course Timetabling --- paradigma
                       de alocação onde os alunos estão agrupados em
                       turmas fixas e imutáveis, sendo os conflitos
                       determinados pelo currículo publicado pela
                       instituição.

  CP-SAT Solver        Motor de Programação por Restrições puramente
                       integral desenvolvido pela Google, construído
                       sobre um solver SAT com Lazy Clause Generation,
                       utilizado como núcleo do motor de optimização do
                       sistema.

  Hard Constraint (HC) Restrição rígida cuja violação torna o horário
                       inválido. A sua satisfação total é condição
                       obrigatória para a viabilidade da solução.

  Soft Constraint (SC) Restrição flexível cuja satisfação é desejável,
                       mas não imprescindível. A sua violação penaliza a
                       qualidade da solução, mas não a invalida.

  Modelagem Esparsa    Técnica em que as variáveis de decisão são
                       instanciadas apenas para as combinações
                       previamente validadas como possíveis, excluindo
                       explicitamente relações irreais para poupar
                       capacidade de processamento.

  Variável de Folga    Recurso matemático que permite ao algoritmo
  (Slack Variable)     colocar uma aula \'de lado\' quando é impossível
                       alocá-la, pagando uma penalidade na função
                       objectivo em vez de travar o sistema.

  Tempo Lectivo        Unidade mínima e indivisível de alocação escolar,
                       equivalente à 45 minutos. Dois tempos lectivos
                       consecutivos formam um bloco de 90 minutos.

  Job ID               Identificador único atribuído a uma tarefa de
                       geração de horário quando o tempo de processamento
                       estimado ultrapassa 5 segundos. Permite ao cliente
                       fazer polling assíncrono sem bloquear a conexão
                       HTTP.
  -----------------------------------------------------------------------

*Tabela 1 --- Glossário técnico do sistema*

4.1.2 Requisitos de negócio

Segundo [@vazquezsimoes2016], Requisitos (ou necessidades) de negócio
são declarações de mais alto nível de objetivos, metas ou necessidades
da organização. Eles descrevem as razões pelas quais um projeto foi
iniciado, as metas que o projeto deve atingir e as métricas que serão
utilizadas para aferir o seu sucesso. Requisitos de negócio descrevem
necessidades da organização como um todo e não de grupos ou partes
interessadas. As necessidades de negócio representam os objetivos que
uma área busca alcançar.

  ------------------------------------------------------------------------
  ID      Tipo          Descrição Técnica e Impacto no Modelo
  ------- ------------- --------------------------------------------------
  RN01    HC            Um professor não pode ter duas ou mais alocações
                        no mesmo slot temporal. (Sem sobreposição de
                        docente).

  RN02    HC            Uma turma não pode ter mais do que uma disciplina
                        alocada no mesmo slot temporal. (Sem sobreposição
                        de turma).

  RN03    HC            Uma sala de aula física não pode comportar mais do
                        que uma turma em simultâneo no mesmo slot
                        temporal. (Sem sobreposição de espaço).

  RN04    SC            O professor deve ser alocado de acordo com a sua
                        disponibilidade registada. O desvio entre o slot
                        ideal e o alocado é penalizado na função objetivo.

  RN05    HC            A carga horária semanal total definida para cada
                        disciplina na matriz curricular da turma deve ser
                        cumprida integralmente pelo solver.

  RN06    Hard / Soft   Agrupamento de aulas em blocos: proibição absoluta
          Hybrid        de tempos isolados (1 slot livre no meio ou aulas
                        singulares). Cargas ímpares são divididas em
                        blocos de tamanho de decisão do solver (ex: 2+3).

  RN07    Lógica de     Docentes sem disponibilidade explicitamente
          Fallback      registada no sistema são tratados como totalmente
                        disponíveis, sem restrições base de slot.

  RN08    SC            Capacidade da Sala: Alocação preferencial na sala
                        adequada com capacidade mínima viável. Violação
                        permitida apenas com pesada penalização em
                        cenários limite.

  RN09    HC            Controlo de Acesso: Qualquer operação de escrita,
          (Segurança)   consulta restrita ou geração exige um ID Token
                        válido do Firebase no cabeçalho HTTP
                        (Authorization Bearer).
  ------------------------------------------------------------------------

*Tabela 2 --- Requisitos de negócio*

4.1.3 Requisitos funcionais

Os requisitos funcionais (RF) definem os serviços, comportamentos e
respostas que o sistema deve fornecer para satisfazer as necessidades
dos utilizadores e os objectivos do negócio. Em termos práticos,
descrevem aquilo que o sistema deve fazer, especificando operações,
entradas, saídas, regras de processamento e reacções a determinadas
situações. No contexto deste estudo, os requisitos funcionais incluem
tanto funções directamente visíveis ao utilizador --- como gerar
horários, validar disponibilidades e devolver relatórios --- como
comportamentos internos indispensáveis para assegurar a produção de uma
solução válida. Conforme assinala [@sommerville2011], estes requisitos
podem também explicitar comportamentos que o sistema não deve permitir,
nomeadamente situações que comprometam a coerência ou a viabilidade da
solução produzida.

  ---------------------------------------------------------------------------
  ID     Nome do Requisito Módulo          Descrição Detalhada / Critérios de
                                           Aceitação
  ------ ----------------- --------------- ----------------------------------
  RF01   CRUD de           Dados Mestre    Permitir a criação, leitura,
         Professores                       atualização e eliminação de
                                           registos de docentes no sistema.

  RF02   CRUD de Turmas    Dados Mestre    Permitir a gestão completa das
                                           turmas da instituição de ensino.

  RF03   CRUD de           Dados Mestre    Gerir o catálogo de disciplinas,
         Disciplinas                       associando cargas horárias
                                           semanais e requisitos base.

  RF04   CRUD de Salas     Dados Mestre    Gerir as salas de aula físicas,
                                           incluindo dados de capacidade e
                                           recursos específicos.

  RF05   Registo de        Dados Mestre    Interface para que o Professor
         Disponibilidade                   registe os seus slots de
                                           preferência e indisponibilidade
                                           para lecionar.

  RF06   Importação em     Importação      Importar dados mestre a partir de
         Massa (Excel)                     ficheiros Excel institucionais por
                                           entidade.

  RF07   Validação de      Importação      Validar a estrutura e integridade
         Importação                        dos dados importados antes da
                                           persistência (fluxo de
                                           pré-visualização e confirmação).

  RF08   Idempotência na   Importação      Ignorar registos já existentes
         Importação                        baseando-se em chaves de
                                           identificação únicas
                                           institucionais (prevenindo
                                           duplicados).

  RF09   Disparar Geração  Motor de        Disparar o processamento
         de Horário        Otimização      assíncrono do motor de otimização
                                           CP-SAT a partir dos dados
                                           consolidados.

  RF10   Consultar Estado  Motor de        Verificar o estado da execução da
         (Polling)         Otimização      geração (Em processamento,
                                           Concluído, Inviável) via Job ID.

  RF11   Consultar Horário Visualização    Apresentar a grelha de horários
         por Turma                         gerada filtrada por uma turma
                                           específica.

  RF12   Consultar Horário Visualização    Apresentar a agenda semanal de
         por Professor                     alocações de um determinado
                                           docente.

  RF13   Tratamento de     Motor de        O sistema deve informar
         Inviabilidade     Otimização      explicitamente as restrições que
                                           causaram o estado \'INFEASIBLE\'
                                           caso o modelo falhe.

  RF14   Alteração Manual  Edição Manual   Permitir alterar manualmente um
         (Reoptimização)                   slot sem invalidar ou recalcular o
                                           resto do horário gerado.

  RF15   Autenticação de   Segurança       Autenticação via Firebase
         Utilizadores                      Authentication para Gestores
                                           Académicos e Professores.
                                           Validação de ID Token no backend
                                           FastAPI.

  RF16   Recuperação de    Segurança       Recuperação self-service integrada
         Password                          com fluxo nativo do Firebase (link
                                           de reset por email).
  ---------------------------------------------------------------------------

*Tabela 3 --- Requisitos Funcionais*

4.1.4 Requisitos não funcionais

Os requisitos não funcionais (RNF) estabelecem as restrições e os
atributos de qualidade que condicionam a forma como o sistema executa os
seus serviços. Diferentemente dos requisitos funcionais, que se
concentram nas funções e comportamentos esperados, os requisitos não
funcionais incidem sobre aspectos como desempenho, eficiência,
interoperabilidade, escalabilidade, segurança e fiabilidade. Em muitos
casos, estes requisitos aplicam-se ao sistema como um todo e não a uma
funcionalidade isolada. Tal como destaca [@sommerville2011], a distinção
entre requisitos funcionais e não funcionais nem sempre é absoluta, pois
um requisito não funcional pode originar novos requisitos funcionais ou
impor restrições à sua implementação. No presente trabalho, os
requisitos não funcionais foram definidos de forma mensurável e
verificável, com o objectivo de assegurar que o sistema, além de gerar
horários válidos, o faça com qualidade técnica, robustez e adequação ao
contexto institucional do ISAF.

  --------------------------------------------------------------------------
  ID        Categoria          Descrição e Métrica de Sucesso
  --------- ------------------ ---------------------------------------------
  RNF01     Desempenho /       Capacidade de escalar eficientemente para
            Escalabilidade     100+ professores e 60+ turmas, utilizando
                               modelagem matemática esparsa para mitigar a
                               explosão combinatória no CP-SAT.

  RNF02     Usabilidade        Operação assíncrona para geração de horários
                               através de arquitetura baseada em Jobs e
                               Polling, garantindo que a interface permanece
                               responsiva.

  RNF03     Confiabilidade     Minimizar cenários sem solução (infeasible)
                               através da modelagem de restrições flexíveis
                               (soft) e garantir que falhas no solver nunca
                               ocorram de forma silenciosa.

  RNF04     Manutenibilidade   Isolamento arquitetural rigoroso do motor do
                               solver OR-Tools / CP-SAT em relação à camada
                               de API REST do FastAPI (Clean Core).

  RNF05     Portabilidade de   Aceitação de ficheiros de entrada no formato
            Dados              institucional Excel (.xlsx) padrão do ISAF
                               para mitigar fricção de migração.

  RNF06     Segurança          Garantia de segurança delegada ao Firebase
                               Authentication com 2 perfis base (Gestor e
                               Professor). O backend FastAPI atua sem
                               persistência de credenciais diretas, apenas
                               validando tokens criptográficos.
  --------------------------------------------------------------------------

*Tabela 4 --- Requisitos Não Funcionais*

**4.2 Modelagem do sistema**

A modelagem do sistema foi realizada com recurso à Unified Modeling
Language (UML), linguagem amplamente utilizada para especificar,
visualizar e documentar artefactos de sistemas orientados a objectos
([@boochrumbaughjacobson2005]). São apresentados os actores do
sistema, os casos de uso principais e a especificação formal do modelo
matemático que fundamenta o motor de optimização.

### **4.2.1 Diagrama de Contexto**

O Diagrama de Contexto é uma ferramenta gráfica utilizada para
representar as interacções entre um sistema e o seu ambiente externo,
definindo os limites do sistema e identificando as entidades externas
(actores) que com ele interagem, bem como os fluxos de dados que entram
e saem. Trata-se de uma visão de alto nível, pensada para simplificar a
compreensão do sistema e facilitar a comunicação entre as partes
interessadas.

O Diagrama de Contexto corresponde ao nível mais alto (nível 0) de um
Diagrama de Fluxo de Dados (DFD), representando todo o sistema como um
único processo, envolto pelas entidades externas com as quais troca
informação, através de fluxos de dados que mostram as interfaces entre o
sistema e essas entidades, permitindo identificar os limites dos
processos, as áreas envolvidas e os relacionamentos com elementos
externos à organização ([@vazquezsimoes2016]).

No caso do sistema proposto, identificam-se duas entidades externas
humanas --- o Gestor Académico/Secretaria e o Professor --- e uma
entidade externa não humana, o serviço Firebase Authentication,
responsável pela emissão e validação da identidade dos utilizadores. O
motor CP-SAT e o backend FastAPI não constituem entidades externas, por
serem componentes internos da fronteira do sistema.

> **[Figura 1 em falta]** — a imagem original não foi extraída corretamente do .docx (pandoc não conseguiu localizar o ficheiro de origem, possivelmente por ter sido inserida como objeto vinculado em vez de imagem embutida). Substituir por: exportar o Diagrama de Contexto do Visual Paradigm (já modelado em `01_diagrama_contexto.md`) e inserir aqui como `.png`.

Figura 1 --- Diagrama de contexto

### **4.2.2 Diagrama de Casos de Uso**

O Diagrama de Casos de Uso é um artefacto UML formal que demonstra o
comportamento externo do sistema na perspectiva do utilizador,
evidenciando as funções e serviços oferecidos e os actores que podem
utilizá-los ([@guedes2011]). O sistema envolve dois actores humanos ---
Gestor Académico/Secretaria e Professor --- cujas responsabilidades e
interacções se encontram descritas na tabela seguinte, com
rastreabilidade directa aos requisitos funcionais.

  ---------------------------------------------------------------------------------
  ID     Caso de Uso       RF de    Ator/Interveniente      Relações / Notas de
                           Origem                           Modelação
  ------ ----------------- -------- ----------------------- -----------------------
  UC01   Gerir Professores RF01     Gestor                  Compreende o CRUD de
                                    Académico/Secretaria    docentes.

  UC02   Gerir Turmas      RF02     Gestor                  Compreende o CRUD de
                                    Académico/Secretaria    turmas.

  UC03   Gerir Disciplinas RF03     Gestor                  Compreende o CRUD de
                                    Académico/Secretaria    disciplinas.

  UC04   Gerir Salas       RF04     Gestor                  Compreende o CRUD de
                                    Académico/Secretaria    salas físicas e
                                                            capacidades.

  UC05   Registar          RF05     Professor               Permite ao docente
         Disponibilidade                                    submeter as suas
                                                            janelas e preferências
                                                            de horário.

  UC06   Importar Dados em RF06     Gestor                  Inclui UC07
         Massa via Excel            Académico/Secretaria    (\<\<include\>\>).
                                                            Importação unificada
                                                            por entidade.

  UC07   Validar Dados     RF07     Gestor                  Incluído por UC06
         Importados                 Académico/Secretaria    (\<\<include\>\>).
                                                            Execução obrigatória
                                                            para garantir
                                                            integridade.

  UC08   Disparar Geração  RF09     Gestor                  Estendido por UC09
         de Horário                 Académico/Secretaria    (\<\<extend\>\>).
                                                            Despoleta execução
                                                            assíncrona do CP-SAT.

  UC09   Notificar Cenário RF13     Gestor                  Estende UC08
         Sem Solução                Académico/Secretaria    (\<\<extend\>\>).
         Viável                                             Ocorre apenas se o
                                                            estado do solver for
                                                            INFEASIBLE.

  UC10   Consultar Estado  RF10     Gestor                  Polling assíncrono do
         de Processamento           Académico/Secretaria    processamento do solver
                                                            via Job ID.

  UC11   Consultar Horário RF11     Gestor                  Visualização
         por Turma                  Académico/Secretaria    estruturada do horário
                                                            escolar correspondente
                                                            a uma turma.

  UC12   Consultar Horário RF12     Gestor                  Acesso à agenda
         por Professor              Académico/Secretaria,   individual de aulas
                                    Professor               (multi-perfil).

  UC13   Autenticar-se     RF15     Gestor                  Pré-condição
                                    Académico/Secretaria,   transversal aos
                                    Professor               restantes casos de uso
                                                            --- não representada
                                                            como \<\<include\>\>
                                                            gráfico, para evitar
                                                            poluição visual do
                                                            diagrama ([@bittnerspence2002]).

  UC14   Recuperar         RF16     Gestor                  Delegado inteiramente
         Password                   Académico/Secretaria,   ao mecanismo nativo do
                                    Professor               Firebase
                                                            Authentication.
  ---------------------------------------------------------------------------------

Tabela 5 --- Casos de uso do sistema

Registam-se duas decisões de modelação relevantes. Em primeiro lugar, a
autenticação (UC13) não é representada graficamente como relação
\<\<include\>\> a partir de cada caso de uso: tratando-se de uma
pré-condição transversal, a sua representação por setas \<\<include\>\>
universais constitui um uso indevido das relações do diagrama,
explicitamente desaconselhado por [@bittnerspence2002]; a
pré-condição é, em alternativa, documentada textualmente na
especificação de cada caso de uso. Em segundo lugar, o requisito RF08
(idempotência) não origina caso de uso próprio, por se tratar de regra
de negócio interna ao comportamento de UC06, sem valor observável
autónomo para o actor. A especificação textual completa dos casos de uso
mais complexos encontra-se no Apêndice B.

*\[Inserir aqui: Diagrama de Casos de Uso (UC01--UC14, com relações
\<\<include\>\> e \<\<extend\>\>) --- exportar do Visual Paradigm\]*

Figura 2 --- Diagrama de casos de uso

### **4.2.3 Diagrama de Classes**

O Diagrama de Classes é o diagrama estrutural central da UML,
representando as classes do sistema, os seus atributos, operações e
relacionamentos, e servindo de base lógica para a maioria dos demais
diagramas e para a própria estrutura da base de dados ([@guedes2011]).
Neste projecto, o Diagrama de Classes cumpre dupla função: artefacto de
modelação e esquema directo de persistência, uma vez que cada classe de
domínio corresponde a um modelo SQLModel no backend FastAPI, persistido
em PostgreSQL (RNF07).

Foram identificadas oito classes de domínio: Professor, Turma,
Disciplina e Sala (dados mestre, RF01--RF04); Disponibilidade (RF05,
associada por composição ao Professor); AtribuicaoCurricular (entrada do
solver, ligando Turma, Disciplina e Professor); GeracaoHorario (o Job
assíncrono, RF09/RF10, com estado e motivo de falha); e Alocacao (a
saída do solver, associando cada atribuição curricular a uma sala, dia e
tempo lectivo). A identidade dos utilizadores não constitui classe de
domínio própria, por ser gerida pelo Firebase Authentication (RF15): a
classe Professor guarda apenas o identificador firebase_uid como
atributo de ligação.

*\[Inserir aqui: Diagrama de Classes (8 classes de domínio, atributos e
multiplicidades) --- exportar do Visual Paradigm\]*

Figura 3 --- Diagrama de classes

### **4.2.4 Diagrama Entidade-Relacional**

O Modelo Entidade-Relacionamento, proposto por [@chen1976], representa
os dados de um domínio como entidades, atributos e relacionamentos,
servindo de ponte entre o modelo conceptual e o esquema físico da base
de dados relacional. Enquanto o Diagrama de Classes modela a estrutura
orientada a objectos da aplicação, o DER modela a estrutura de
persistência --- neste projecto, o esquema PostgreSQL (RNF07), com
correspondência directa de uma tabela por classe de domínio persistente.

Destacam-se duas decisões de desenho: as restrições UNIQUE sobre o
atributo codigo_institucional de cada entidade de dados mestre
implementam directamente a chave de idempotência da importação (RF08); e
a restrição UNIQUE composta sobre (geracao, sala, dia, tempo lectivo) na
tabela de alocações acrescenta uma defesa em profundidade da regra RN03
ao nível da base de dados, complementar à garantia matemática do solver.

*\[Inserir aqui: Diagrama Entidade-Relacional (8 tabelas, chaves
primárias e estrangeiras) --- exportar do Visual Paradigm\]*

Figura 4 --- Diagrama entidade-relacional

## 

## **4.3 Arquitectura da solução**

O sistema adoptou uma arquitectura de três camadas com separação
rigorosa de responsabilidades, em alinhamento com princípios de
arquitectura limpa e separação de responsabilidades em sistemas de
software. Esta separação garante que a lógica matemática do solver é
independente da camada de comunicação HTTP e da camada de apresentação,
facilitando a manutenção, a substituição de componentes e a
escalabilidade futura.

### **4.3.1 Camada de apresentação (Flutter)**

A interface de utilizador foi desenvolvida em Flutter, adoptando Clean
Architecture com separação em três sub-camadas internas: Presentation
(widgets e páginas), Domain (entidades e casos de uso) e Data
(repositórios e modelos de deserialização JSON). Esta estrutura permite
que a interface seja independente da implementação do backend,
comunicando exclusivamente através de contratos JSON definidos pelo
endpoint /gerar-horario da API.

### **4.3.2 Camada de integração (FastAPI)**

O backend foi implementado em Python com FastAPI, responsável pela
validação dos payloads de entrada, pela orquestração das chamadas ao
motor de optimização e pela devolução de respostas estruturadas em JSON.
Para satisfazer o RNF02 (escalabilidade assíncrona), foi implementado um
padrão de Job Queue: quando o tempo de processamento estimado ultrapassa
5 segundos, a API devolve imediatamente um Job ID e o cliente realiza
polling no endpoint /status/{job_id} até à conclusão do cálculo,
evitando o bloqueio da conexão HTTP.

A camada de integração é ainda responsável pela persistência dos dados
académicos em PostgreSQL, através de modelos SQLModel que espelham as
classes de domínio definidas na Secção 4.2.3, garantindo integridade
transaccional nas operações de importação em massa (RF06--RF08) e
suporte a escrita concorrente em ambiente de hospedagem (RNF07).

### **4.3.3 Camada de optimização (CP-SAT Solver)**

O núcleo do sistema é o motor de optimização implementado em Python com
Google OR-Tools CP-SAT. Esta camada recebe o problema formalizado como
CSP, instância as variáveis de decisão de acordo com a modelagem esparsa
(RNF01), adiciona as restrições rígidas e flexíveis ao modelo, e invoca
o solver. O resultado é devolvido como um objecto estruturado que a
camada FastAPI serializa em JSON para consumo pela interface Flutter.
Caso o solver, devolva o status INFEASIBLE --- indicando que o conjunto
de restrições é matematicamente irresolvível --- o motor activa o
mecanismo de diagnóstico (RF13), introduzindo variáveis de folga que
permitem identificar e reportar o conjunto mínimo de restrições
conflituantes, em vez de falhar criticamente.

A sincronização dos horários gerados com serviços de calendário externos
(Google Calendar API) foi identificada como extensão de valor
acrescentado, mas encontra-se formalmente classificada como trabalho
futuro (RF17), não fazendo parte do âmbito de implementação e validação
deste MVP.

## **4.4 Implementação do sistema**

A implementação seguiu uma abordagem incremental e iterativa inspirada
no Rational Unified Process (RUP), com o desenvolvimento organizado em
módulos independentes e testáveis, por ordem de prioridade técnica e de
dependência entre componentes ([@kruchten2003]).

### **4.4.1 Módulo 1 --- Motor de Optimização (Core)**

O módulo central foi desenvolvido em primeiro lugar, de forma isolada,
para validar a lógica matemática sem dependências de framework.
Implementa a modelagem esparsa do CSP com Google OR-Tools CP-SAT, a
gestão das Hard Constraints (RN01, RN02, RN03 e RN05), a penalização das
Soft Constraints (RN04, RN06 e RN08) na função objectivo, e o mecanismo
de variáveis de folga para diagnóstico de inviabilidade (RF13). A
arquitectura do modelo foi preparada para suportar, em iterações
futuras, o congelamento de alocações necessário à reoptimização
incremental (RF14, classificado como trabalho futuro). O código deste
módulo encontra-se reproduzido no Apêndice A.

### **4.4.2 Módulo 2 --- API REST (FastAPI)**

O segundo módulo implementa a camada de integração HTTP, expondo os
endpoints definidos no contrato de API: POST /gerar-horario (recebe o
payload de entidades académicas e acciona o solver), GET
/status/{job_id} (consulta o estado de uma tarefa assíncrona) e GET
/horario/{job_id} (obtém o resultado final em JSON estruturado). A
validação dos payloads de entrada utiliza modelos Pydantic, garantindo a
integridade dos dados antes da sua passagem ao motor de optimização.

### **4.4.3 Módulo 3 --- Interface Flutter**

A interface de utilizador foi implementada em Flutter com Clean
Architecture, disponibilizando os seguintes ecrãs principais:
autenticação de utilizadores (Firebase Authentication, RF15/RF16),
gestão de entidades académicas (docentes, turmas, disciplinas, salas),
registo de disponibilidade docente, visualização do horário gerado em
formato de grelha semanal, consulta do relatório de inviabilidade quando
aplicável, e exportação do horário em PDF. As capturas de ecrã do
sistema encontram-se no Apêndice C.