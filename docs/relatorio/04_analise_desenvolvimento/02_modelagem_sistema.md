## **4.2 Modelagem do sistema**

A modelagem do sistema foi realizada com recurso à Unified Modeling
Language (UML), linguagem amplamente utilizada para especificar,
visualizar e documentar artefactos de sistemas orientados a objectos
[@boochrumbaughjacobson2005]. São apresentados os actores do
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
externos à organização [@vazquezsimoes2016].

No caso do sistema proposto, identificam-se duas entidades externas
humanas --- o Gestor Académico/Secretaria e o Professor --- e uma
entidade externa não humana, o serviço Firebase Authentication,
responsável pela emissão e validação da identidade dos utilizadores. O
motor CP-SAT e o backend FastAPI não constituem entidades externas, por
serem componentes internos da fronteira do sistema.

Figura 1

*Diagrama de contexto*

![](media/diagramas/diagrama_contexto.png)

*Nota.* Criado pelo autor (2026).

### **4.2.2 Diagrama de Casos de Uso**

O Diagrama de Casos de Uso é um artefacto UML formal que demonstra o
comportamento externo do sistema na perspectiva do utilizador,
evidenciando as funções e serviços oferecidos e os actores que podem
utilizá-los [@guedes2011]. O sistema envolve dois actores humanos ---
Gestor Académico/Secretaria e Professor --- cujas responsabilidades e
interacções se encontram descritas na tabela seguinte, com
rastreabilidade directa aos requisitos funcionais.

Table: Tabela 5 --- Casos de uso do sistema

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

  UC13   Login             RF15     Gestor                  Pré-condição
                                    Académico/Secretaria,   transversal aos
                                    Professor               restantes casos de uso
                                                            --- não representada
                                                            como \<\<include\>\>
                                                            gráfico, para evitar
                                                            poluição visual do
                                                            diagrama
                                                            [@bittnerspence2002];
                                                            representada em
                                                            alternativa por
                                                            generalização de actor
                                                            (Gestor e Professor
                                                            generalizam Utilizador,
                                                            que é quem liga a UC13
                                                            e UC14).

  UC14   Recuperar         RF16     Gestor                  Delegado inteiramente
         Password                   Académico/Secretaria,   ao mecanismo nativo do
                                    Professor               Firebase
                                                            Authentication.

  UC15   Validar Nível     RN11     Gestor                  Incluído
         de Acesso                  Académico/Secretaria,   (\<\<include\>\>) por
                                    Professor               UC12 --- restringe a
                                                            consulta ao horário do
                                                            próprio Professor
                                                            quando o actor não é
                                                            Gestor.
  ---------------------------------------------------------------------------------

Registam-se duas decisões de modelação relevantes. Em primeiro lugar, a
autenticação (UC13/UC14) não é representada graficamente como relação
\<\<include\>\> a partir de cada caso de uso: tratando-se de uma
pré-condição transversal, a sua representação por setas \<\<include\>\>
universais constitui um uso indevido das relações do diagrama,
explicitamente desaconselhado por [@bittnerspence2002]. Em vez disso,
o diagrama recorre a generalização de actor --- Gestor e Professor
generalizam um actor comum, Utilizador, que é quem se liga a UC13 e
UC14 --- e a validação de token em cada pedido HTTP (RN09) é, essa sim,
documentada apenas textualmente na especificação de cada caso de uso,
por ser uma verificação de infra-estrutura (incluindo a expiração do
token) e não um comportamento observável adicional do actor. Já a
verificação de nível de acesso em UC12 (RN11 --- Professor só vê o seu
próprio horário) tem valor observável específico daquele caso de uso, e
é por isso modelada graficamente como UC15, incluída (\<\<include\>\>)
por UC12. Em segundo lugar, o requisito RF08 (idempotência) não origina
caso de uso próprio, por se tratar de regra de negócio interna ao
comportamento de UC06, sem valor observável autónomo para o actor. A
especificação textual completa dos casos de uso mais complexos
encontra-se no Apêndice B.

Figura 2

*Diagrama de casos de uso*

![](media/diagramas/diagrama_casos_uso.png)

*Nota.* Criado pelo autor (2026).

### **4.2.3 Diagrama de Classes**

O Diagrama de Classes é o diagrama estrutural central da UML,
representando as classes do sistema, os seus atributos, operações e
relacionamentos, e servindo de base lógica para a maioria dos demais
diagramas e para a própria estrutura da base de dados [@guedes2011].
Neste projecto, o Diagrama de Classes cumpre dupla função: artefacto de
modelação e esquema directo de persistência, uma vez que cada classe de
domínio corresponde a um modelo SQLModel no backend FastAPI, persistido
em PostgreSQL (RNF07).

Foram identificadas onze classes de domínio: Curso, Professor, Turma,
Disciplina e Sala (dados mestre, RF01--RF04); PlanoCurricular e
PlanoCurricularDisciplina (a grade curricular oficial — disciplinas e
carga horária semanal por curso, ano e semestre — partilhada por todas
as turmas desse ano, em vez de definida turma a turma); Disponibilidade
(RF05, associada por composição ao Professor); Utilizador (identidade —
liga, por email, uma conta
Firebase Authentication a um Gestor ou, opcionalmente, a um Professor já
registado, RF15/RN09/RN10); Job (a tarefa assíncrona do solver, RF09/RF10,
com estado e motivo de falha); e Alocacao (a saída do solver, associando
cada combinação turma-disciplina-professor a uma sala, dia e período —
o turno não é atributo próprio de Alocacao, por ser sempre igual ao da
Turma alocada, RN de normalização até à 3.ª Forma Normal). Uma Turma
segue sempre um único PlanoCurricular (RF02), do qual herda curso e ano
(também não repetidos em Turma pela mesma razão); o Professor liga-se à
Turma indirectamente — leciona uma Disciplina que integra o
PlanoCurricular dessa Turma, e é entre os professores assim
qualificados e disponíveis que o solver escolhe quem lecciona cada
turma (RNF01). A qualificação docente (Professor--Disciplina) é uma
associação muitos-para-muitos sem atributos próprios além das chaves
estrangeiras, pelo que não constitui classe de domínio própria no
diagrama conceptual — persiste, ainda assim, como tabela de junção
(ProfessorDisciplina) no esquema físico (secção 4.2.4).

Figura 3

*Diagrama de classes*

![](media/diagramas/diagrama_classes.png)

*Nota.* Criado pelo autor (2026).

### **4.2.4 Diagrama Entidade-Relacional**

O Modelo Entidade-Relacionamento, proposto por [@chen1976], representa
os dados de um domínio como entidades, atributos e relacionamentos,
servindo de ponte entre o modelo conceptual e o esquema físico da base
de dados relacional. Enquanto o Diagrama de Classes modela a estrutura
orientada a objectos da aplicação, o DER modela a estrutura de
persistência --- neste projecto, o esquema PostgreSQL (RNF07), com
correspondência directa de uma tabela por classe de domínio persistente.

Destaca-se uma decisão de desenho: as restrições UNIQUE sobre o atributo
codigo (ou email, no caso de Professor e Utilizador) de cada entidade de
dados mestre implementam directamente a chave de idempotência da
importação (RF08). A regra RN03 (sala sem dupla turma no mesmo tempo) é
garantida matematicamente pelo solver (secção 4.3.3) — não existe, para
já, uma restrição UNIQUE composta redundante ao nível da base de dados
sobre a tabela de alocações; fica identificada como melhoria futura de
defesa em profundidade.

Figura 4

*Diagrama entidade-relacional*

![](media/diagramas/diagrama_er.png)

*Nota.* Criado pelo autor (2026).
