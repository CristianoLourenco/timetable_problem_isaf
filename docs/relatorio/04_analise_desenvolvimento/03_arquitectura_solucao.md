## **4.3 Arquitectura da solução**

O sistema adoptou uma arquitectura de três camadas com separação
rigorosa de responsabilidades, em alinhamento com os princípios de
Clean Architecture [@martin2017]. Esta separação garante que a lógica
matemática do solver é
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
polling no endpoint GET /jobs/{job\_id} até à conclusão do cálculo,
evitando o bloqueio da conexão HTTP.

A camada de integração é ainda responsável pela persistência dos dados
académicos em PostgreSQL, através de modelos SQLModel que espelham as
classes de domínio definidas na Secção 4.2.3, garantindo integridade
transaccional nas operações de importação em massa (RF06--RF08) e
suporte a escrita concorrente em ambiente de hospedagem (RNF07).

#### Autenticação e autorização (RN09--RN11, RF15/RF16, RNF06)

A segurança de acesso é delegada ao Firebase Authentication (RNF06),
mas nunca de forma directa entre o cliente Flutter e o Firebase: por
decisão de arquitectura, todas as operações de autenticação --- login
por email/senha, login com o Google, renovação de sessão e recuperação
de password --- são intermediadas pelo backend, que fala com a REST API
pública do Identity Toolkit e do Secure Token API do Firebase
(`accounts:signInWithPassword`, `accounts:signInWithIdp`,
`token`, `accounts:sendOobCode`) autenticado apenas pela Web API Key do
projecto, que é pública e não constitui segredo. Esta escolha evita duas
dependências que a alternativa --- Firebase Admin SDK no backend, ou
chamadas directas do cliente ao Firebase --- exigiria: um ficheiro de
credenciais de serviço (`firebase-service-account.json`) para operações
administrativas, e a exposição de lógica de sessão fora do backend, onde
seria mais difícil de auditar centralmente.

O fluxo de autorização segue três passos em cada pedido HTTP protegido.
Primeiro, o cliente envia o ID Token Firebase obtido no login no
cabeçalho `Authorization: Bearer <token>`; o backend verifica a sua
validade e assinatura directamente contra os certificados públicos do
Google (biblioteca `google-auth`), sem qualquer chamada de rede
adicional ao Firebase por pedido --- a verificação é criptográfica e
local, apenas os certificados são obtidos e postos em cache (RN09). Um
token ausente, inválido, expirado ou com assinatura incorrecta resulta
em `401 Unauthorized` antes de qualquer lógica de negócio ser executada.
Segundo, o email extraído do token verificado é resolvido para um papel
aplicacional --- Superadmin (lista de bootstrap em configuração, sem
tabela própria), Gestor ou Professor --- por consulta à tabela
`Utilizador`; um email autenticado no Firebase mas sem registo
correspondente nesta tabela é rejeitado com `403 Forbidden`, distinto de
um token inválido (`401`), porque a causa é de autorização e não de
autenticação. Terceiro, dependências FastAPI (`require_gestor`,
`require_superadmin`, `verificar_acesso_professor_proprio`) aplicam o
controlo de acesso por papel a cada rota: o CRUD de dados mestre e a
geração de horários exigem Gestor ou Superadmin (RN09); a consulta do
próprio horário está reservada a cada Professor sobre os seus próprios
dados, nunca sobre os de outro (RN11); e a gestão de contas de Gestor é
exclusiva do Superadmin.

A ligação entre uma conta Firebase de Professor e o registo institucional
correspondente é validada de forma imperativa no momento do
auto-registo (RN10, RF15): o Professor só consegue criar a sua conta se
o email indicado já corresponder a um registo de `Professor` criado
previamente pelo Gestor (RF01) --- nunca ao contrário --- e a conta
Firebase só é criada depois dessa validação passar, evitando contas
órfãs sem correspondência institucional. A recuperação de password
(RF16) devolve sempre `204 No Content`, mesmo quando o email não
corresponde a nenhuma conta, para não permitir a um terceiro enumerar
quais emails têm conta registada por observação da resposta HTTP.

### **4.3.3 Camada de optimização (CP-SAT Solver)**

O núcleo do sistema é o motor de optimização implementado em Python com
Google OR-Tools CP-SAT. Esta camada recebe o problema formalizado como
CSP, instância as variáveis de decisão de acordo com a modelagem esparsa
(RNF01), adiciona as restrições rígidas e flexíveis ao modelo, e invoca
o solver. O resultado é devolvido como um objecto estruturado que a
camada FastAPI serializa em JSON para consumo pela interface Flutter.
Caso o solver devolva o status INFEASIBLE --- indicando que o conjunto
de restrições é matematicamente irresolvível --- o sistema activa o
mecanismo de diagnóstico (RF13): uma verificação estrutural leve,
executada antes de qualquer nova resolução, que testa as causas mais
comuns de inviabilidade (ausência de professor qualificado para uma
disciplina, número de alunos da turma a exceder a capacidade de todas
as salas disponíveis, ou carga horária semanal incompatível com o
tamanho mínimo de bloco exigido pelo RN06) e devolve a causa
identificada em vez de falhar criticamente. Não recorre a variáveis de
folga (*slack variables*) nem a extracção do conjunto mínimo de
restrições em conflito via `SufficientAssumptionsForInfeasibility` do
CP-SAT --- ficando como melhoria futura (cf. Secção 5.2) para os casos
em que nenhuma das causas estruturais verificadas é identificada.

A sincronização dos horários gerados com serviços de calendário externos
(Google Calendar API) foi identificada como extensão de valor
acrescentado, mas encontra-se formalmente classificada como trabalho
futuro (RF17), não fazendo parte do âmbito de implementação e validação
deste MVP.
