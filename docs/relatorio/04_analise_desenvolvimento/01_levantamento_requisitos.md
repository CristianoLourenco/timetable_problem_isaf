# 4. ANÁLISE, DESENVOLVIMENTO E DISCUSSÃO DOS RESULTADOS

Este capítulo apresenta o percurso técnico e analítico do
desenvolvimento do sistema, estruturado em seis secções que cobrem desde
o levantamento de requisitos até à discussão crítica dos resultados
obtidos. A sequência adoptada é coerente com a metodologia RUP descrita
na Secção 3.9.2 e com os princípios de engenharia de requisitos
estabelecidos na Secção 3.

## **4.1 Levantamento de requisitos**

O levantamento de requisitos constitui a etapa fundacional do
desenvolvimento de qualquer sistema de software. Seguindo os critérios
de qualidade da norma IEEE 830 --- correcta, completa, clara,
consistente, modificável, priorizada, verificável e rastreável --- os
requisitos do sistema foram elicitados a partir das entrevistas
realizadas com a gestão académica do ISAF, da análise documental dos
horários vigentes e da revisão da literatura científica sobre o UCTP
[@ieee830; @isoiec29148].

De acordo com a norma ISO/IEC/IEEE 29148:2011, os requisitos de sistemas
e software devem expressar necessidades, propriedades esperadas e
especificações verificáveis ao longo do ciclo de vida do produto
[@isoiec29148]. Neste trabalho, a necessidade central identificada
é a seguinte: a gestão pedagógica do ISAF necessita de gerar horários
académicos de forma automática, eliminando os conflitos de alocação de
docentes e salas que ocorrem na distribuição manual de horários no
sistema de gestão escolar actualmente utilizado pelo ISAF. A
propriedade esperada determina que o sistema opere sob
princípios de inteligência artificial simbólica, nomeadamente resolução
de restrições por CSP/CP, rejeitando aproximações probabilísticas que
comprometam a integridade e a verificabilidade dos horários produzidos.
A especificação é documentada nas tabelas de requisitos funcionais e não
funcionais que se seguem.

### **4.1.1 Glossário técnico**

Seguindo a directriz de modificabilidade da norma IEEE 830, que
recomenda a utilização de glossário para evitar ambiguidades e
redundâncias ao longo da especificação, apresenta-se de seguida a
definição formal dos termos técnicos utilizados neste capítulo (IEEE,
1998).

Table: Tabela 1 --- Glossário técnico do sistema

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

### **4.1.2 Requisitos de negócio**

Segundo @vazquezsimoes2016 [p. 125], "Requisitos (ou necessidades) de
negócio são declarações de mais alto nível de objetivos, metas ou
necessidades da organização. Eles descrevem as razões pelas quais um
projeto foi iniciado, as metas que o projeto deve atingir e as métricas
que serão utilizadas para aferir o seu sucesso. Requisitos de negócio
descrevem necessidades da organização como um todo e não de grupos ou
partes interessadas". No contexto deste trabalho,
essas necessidades de negócio foram formalizadas como as regras de
negócio apresentadas na Tabela 2.

Table: Tabela 2 --- Requisitos de negócio

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
                        ideal e o alocado é penalizado na função objectivo.

  RN05    Hard / Soft   A carga horária semanal total definida para cada
          Híbrida       disciplina na matriz curricular da turma deve ser
                        cumprida pelo solver; o défice residual --- tempos
                        lectivos não alocados quando a carga total não é
                        atingível dentro do orçamento de tempo disponível
                        --- é fortemente penalizado na função objectivo em
                        vez de bloquear o solver com um estado INFEASIBLE,
                        garantindo o RNF03 (RF13) e ficando disponível
                        para resolução por alocação manual (UC09).

  RN06    Hard / Soft   Agrupamento de aulas em blocos: proibição absoluta
          Híbrida       de tempos isolados (1 slot livre no meio ou aulas
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

  RN10    HC            Ao registar conta, o email da conta Firebase do
          (Segurança)   Professor deve corresponder ao email do registo
                        criado previamente pelo Gestor --- caso contrário,
                        o backend devolve 403 e a conta não é associada.

  RN11    HC (Acesso)   O Gestor consulta e exporta o horário de qualquer
                        turma ou professor; o Professor só pode consultar
                        o seu próprio horário (UC15 --- Validar Nível de
                        Acesso).

  RN12    Lógica de     Prioridade docente na fixação de horário: 50%
          Priorização   classificação institucional + 30%
                        vínculo/professor de casa + 20% escassez de
                        disponibilidade (menos slots livres = mais
                        prioritário). Turma tem prioridade estrutural
                        sobre Professor --- o solver fixa primeiro os
                        docentes de maior prioridade nos seus tempos
                        disponíveis, depois distribui os restantes o mais
                        próximo possível da disponibilidade registada
                        ("Três Cenários Concorrentes").
  ------------------------------------------------------------------------

### **4.1.3 Requisitos funcionais**

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

Table: Tabela 3 --- Requisitos Funcionais

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

  RF17   Sincronização com Integrações     Sincronizar os horários gerados
         Calendário                        com serviços de calendário
         Externo (Fora do                  externos, nomeadamente a Google
         Âmbito)                           Calendar API. Classificado como
                                           trabalho futuro e fora do âmbito
                                           de implementação e validação deste
                                           MVP (cf. Secção 4.4).
  ---------------------------------------------------------------------------

### **4.1.4 Requisitos não funcionais**

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

Table: Tabela 4 --- Requisitos Não Funcionais

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

  RNF07     Persistência de    Utilização de um SGBD relacional transaccional
            Dados              (PostgreSQL) para garantir integridade
                               referencial e transaccional nas operações de
                               importação em massa, com esquema mapeado
                               directamente pelos modelos SQLModel. Suporte a
                               escrita concorrente é uma propriedade de
                               desenho do SGBD, não validada por teste de
                               carga dedicado neste trabalho.
  --------------------------------------------------------------------------
