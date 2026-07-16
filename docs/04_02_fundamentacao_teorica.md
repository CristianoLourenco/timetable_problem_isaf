2. FUNDAMENTAÇÃO TEÓRICA

2.1 O processo de elaboração de horários em
instituições de ensino superior

A elaboração de horários em instituições de ensino superior constitui
uma tarefa administrativa recorrente e de elevada complexidade. @oudevrielink2019 descrevem que as instituições de ensino superior
enfrentam, simultaneamente, a redução progressiva de recursos
partilhados --- como salas de aula e espaços físicos --- e um aumento
crescente das exigências de flexibilidade por parte de estudantes e
docentes. Esta combinação de factores empurra as práticas de elaboração
de horários para os seus limites operacionais.

A natureza da tarefa implica a alocação de recursos finitos ---
professores, turmas, salas e períodos de tempo --- de forma a satisfazer
um conjunto de condições obrigatórias e preferenciais que variam de
instituição para instituição ([@oudevrielink2019]). Wren (1995,
citado em Oude Vrielink et al., 2019) formalizou esta ideia ao definir o
processo de elaboração de horários como a alocação de recursos dados a
objectos específicos posicionados no espaço-tempo, de forma a
satisfazer, tanto quanto possível, um conjunto de objectivos desejáveis,
sujeitos a restrições.

No contexto universitário, este processo repete-se no início de cada
semestre lectivo, exigindo um esforço administrativo considerável
[@abdipoor2023; @bashab2023]. Quando conduzido de forma
manual, o processo é extremamente difícil, demorado e frequentemente
conduz ao desperdício de recursos ([@abdipoor2023]). A ausência de
soluções com aplicabilidade geral na literatura obriga muitas
instituições a manterem a elaboração manual dos horários, perpetuando
ineficiências que afectam estudantes, docentes e pessoal administrativo
([@abdipoor2023]).

@oudevrielink2019 identificam ainda uma lacuna estrutural
entre a investigação académica e a prática institucional: as aplicações
comerciais de elaboração de horários tendem a priorizar a interface
gráfica em detrimento da implementação de algoritmos de resolução
actualizados, utilizando na maioria dos casos métodos desenvolvidos nas
décadas de 1980 e 1990. Os autores concluem que colmatar esta lacuna
entre a investigação recente e os algoritmos implementados nas
aplicações pode produzir sistemas de elaboração de horários mais
robustos, eficientes e generalizáveis.

É neste contexto que surge a motivação para o desenvolvimento de
sistemas inteligentes de geração automática de horários, capazes de
combinar a força algorítmica da investigação em optimização combinatória
com as necessidades práticas das instituições de ensino.

2.2 O Problema de Escalonamento de Horários
(Timetabling Problem)

2.2.1 Definição formal do problema

O problema de elaboração de horários insere-se numa classe mais ampla de
problemas de escalonamento. @bashab2023 estabelecem a
hierarquia conceptual deste domínio, distinguindo scheduling
(escalonamento), timetabling (elaboração de horários), sequencing
(sequenciamento) e rostering (escalonamento de recursos humanos) como
subproblemas distintos dentro da área de planeamento sujeito a
restrições. Especificamente, o timetabling é definido como a alocação,
sujeita a restrições, de recursos dados a objectos posicionados no
espaço-tempo, de forma a satisfazer o maior número possível de um
conjunto de objectivos desejáveis (Wren, 1996, citado em [@bashab2023]). No contexto universitário, o University Course Timetabling
Problem (UCTP) pode ser formalmente enunciado da seguinte forma
([@abdipoor2023]):

**Dado**:

-   Um conjunto de eventos E = {e₁, e₂, e₃, \..., e\|E\|}

-   Um conjunto de períodos de tempo T = {t₁, t₂, t₃, \..., t\|T\|} (com
    \|T\| = 45 nos conjuntos de referência --- 9 períodos por dia × 5
    dias por semana)

-   Um conjunto de salas R = {r₁, r₂, r₃, \..., r\|R\|}

-   Um conjunto de estudantes S = {s₁, s₂, s₃, \..., s\|S\|}

-   Um conjunto de características de salas F = {f₁, f₂, f₃, \...,
    f\|F\|}

-   Um conjunto de dias D = {d₁, d₂, d₃, \..., d\|D\|} (tipicamente os
    dias úteis, com \|D\| = 5)

**Encontrar**: uma atribuição (um horário) de E eventos (com S
estudantes) a R salas (com F características) e T períodos de tempo (ao
longo de D dias) que minimize as violações de restrições.

2.2.2 Classificação: School Timetabling vs.
University Timetabling

O domínio do educational timetabling divide-se em dois ramos principais:
o escalonamento escolar (school timetabling) e o escalonamento
universitário (university timetabling). O escalonamento universitário
subdivide-se, por sua vez, em dois subproblemas distintos: o University
Course Timetabling Problem (UCTP ou UCTTP) e o University Examination
Timetabling Problem (UETP ou UETTP) ([@abdipoor2023]).

@bashab2023 clarificam esta distinção, definindo o course
timetabling como um problema de atribuição multidimensional no qual
estudantes e professores são alocados a disciplinas, e os eventos ---
encontros individuais entre estudantes e professores --- são atribuídos
a salas e períodos de tempo. O examination timetabling, por sua vez,
consiste na atribuição de exames a um número limitado de períodos de
tempo disponíveis, de forma a evitar conflitos ou sobreposições.

No âmbito do UCTP, a literatura identifica ainda duas variantes
principais: o Curriculum-Based Course Timetabling Problem (CB-CTP) e o
Post-Enrollment Course Timetabling Problem (PE-CTP). A principal
diferença entre ambas reside na fonte dos conflitos: no CB-CTP, os
conflitos emergem do currículo publicado pela instituição, enquanto no
PE-CTP decorrem dos dados de inscrição dos estudantes ([@abdipoor2023]).

@oudevrielink2019 observam ainda que a investigação em
escalonamento universitário avançou de forma mais acelerada do que a
investigação em escalonamento escolar, em grande medida porque o
primeiro beneficiou de esforços de padronização através das
International Timetabling Competitions (ITC), que permitiram a
comparação de metodologias num conjunto de referência comum.

2.2.3 Complexidade computacional: problemas
NP-Hard

O UCTP pertence à classe dos problemas de optimização combinatória (COP
--- Combinatorial Optimization Problems), caracterizados por um espaço
de soluções que cresce exponencialmente com a dimensão do problema
([@bashab2023]). Uma vez que existem R\^E formas de alocação
possíveis no UCTP, o tempo computacional necessário aumenta de forma
exponencial com o crescimento do número de eventos, salas e períodos
considerados ([@abdipoor2023]).

Consequentemente, o UCTP é classificado como um problema NP-Hard
(Non-deterministic Polynomial-time hard), o que torna inviável a
aplicação de algoritmos exactos, em particular para instâncias de maior
dimensão ([@abdipoor2023]). [@oudevrielink2019], citando
Even (1975, citado em [@oudevrielink2019]), reforçam que o problema de elaboração de horários é um
problema NP-hard e NP-completo, dependendo das restrições consideradas,
e que soluções viáveis, eficientes ou rápidas --- todos sinónimos de
tempo polinomial --- não se aplicam a este domínio. @bashab2023
acrescentam que as características desta classe de problemas implicam
que: (1) ainda não existe um método capaz de os resolver em tempo
razoável para qualquer instância; (2) o tempo computacional necessário
cresce exponencialmente com a dimensão do problema; e (3) a solução
exacta é apenas alcançável para instâncias modestas, sendo que a maioria
das abordagens adopta algoritmos de aproximação que, não garantindo a
solução óptima, procuram obter soluções suficientemente boas.

2.2.4 Hard Constraints e Soft Constraints

As restrições envolvidas no UCTP classificam-se genericamente em dois
tipos: restrições rígidas (Hard Constraints --- HC) e restrições
flexíveis (Soft Constraints --- SC) [@abdipoor2023; @bashab2023]. As restrições rígidas são condições obrigatórias que
determinam a viabilidade de uma solução --- a sua violação torna o
horário inválido. As restrições flexíveis são condicionantes opcionais
que determinam a qualidade de uma solução --- a sua satisfação é
desejável, mas não imprescindível para a validade do horário ([@abdipoor2023]).

@abdipoor2023 apresentam o catálogo formal das restrições
envolvidas no UCTP padrão. No que respeita às restrições rígidas,
destacam-se: nenhum estudante pode ser atribuído a mais do que uma
disciplina no mesmo período (HC1); a sala deve satisfazer as
características exigidas pela disciplina (HC2); o número de estudantes
inscritos numa disciplina não deve exceder a capacidade da sala (HC3);
não é permitida mais do que uma disciplina por período em cada sala
(HC4); uma disciplina só pode ser atribuída a determinados períodos
pré-definidos (HC5); todas as aulas de uma disciplina devem ser
escalonadas (HC7); as aulas de disciplinas pertencentes ao mesmo
currículo ou leccionadas pelo mesmo docente devem ser escalonadas em
períodos distintos (HC8); e, se o docente de uma disciplina não estiver
disponível num determinado período, nenhuma aula dessa disciplina pode
ser escalonada nesse período (HC9).

Relativamente às restrições flexíveis, os mesmos autores identificam,
entre outras: um estudante não deve ter apenas uma disciplina num
determinado dia (SC1); um estudante não deve ter mais de duas
disciplinas consecutivas (SC2); um estudante não deve ter disciplinas
escalonadas no último período do dia (SC3); as aulas de cada disciplina
devem ser distribuídas pelo número mínimo de dias estabelecido (SC5); as
aulas pertencentes a um mesmo currículo devem ser adjacentes entre si
(SC6); e todas as aulas de uma disciplina devem ser leccionadas na mesma
sala (SC7).

@bashab2023 sublinham que o objectivo da elaboração de um
horário viável consiste em satisfazer todas as restrições rígidas e,
simultaneamente, minimizar as violações das restrições flexíveis. A
função de custo de uma solução candidata S é tipicamente calculada como
a soma ponderada das violações de restrições rígidas e flexíveis: CS =
WSC × \|SC\| + WHC × \|HC\|, sendo que uma solução que viole qualquer
restrição rígida é considerada inviável e, portanto, sem valor prático
([@abdipoor2023]).

2.3 Inteligência Artificial para Optimização
Combinatória

2.3.1 IA simbólica vs. IA subsimbólica

A Inteligência Artificial (IA) divide-se em dois grandes paradigmas com
fundamentos e abordagens distintos. A IA simbólica --- também designada
IA clássica ou IA baseada em conhecimento --- opera sobre representações
explícitas do mundo sob a forma de símbolos, regras e restrições
lógicas. O seu funcionamento é determinístico e interpretável: dado um
conjunto de restrições bem definidas, o sistema procura sistematicamente
uma atribuição de valores às variáveis que satisfaça todas as condições
impostas ([@russellnorvig2021]). A IA subsimbólica, por contraste,
engloba abordagens como as redes neuronais artificiais e a aprendizagem
por reforço, que aprendem padrões a partir de dados históricos sem que
as regras sejam explicitamente programadas.

Para o problema de geração automática de horários, a abordagem simbólica
é a mais adequada. O domínio do problema é completamente especificável
em termos de restrições formais --- não há incerteza sobre as regras,
apenas complexidade combinatória na sua satisfação simultânea.
@harshalatha2026 confirmam esta escolha na sua análise
comparativa, concluindo que as abordagens de IA subsimbólica, como redes
neuronais e aprendizagem por reforço, não garantem intrinsecamente
horários sem conflitos nem oferecem mecanismos para ajustes em tempo
real, reduzindo a sua adequação operacional para ambientes
institucionais dinâmicos.

2.3.2 Satisfação de Restrições (Constraint
Satisfaction Problem --- CSP)

O Problema de Satisfação de Restrições (CSP) é o formalismo matemático
central da IA simbólica aplicada a problemas de escalonamento. Um CSP é
definido como um triplo (X, D, C), onde X = {x₁, \..., xₙ} representa o
conjunto de variáveis, D = {D₁, \..., Dₙ} representa os domínios de
valores possíveis para cada variável, e C = {C₁, \..., Cₖ} representa o
conjunto de restrições que limitam os valores que as variáveis podem
assumir simultaneamente ([@russellnorvig2021]; El-Sakka, 2015).

Uma solução de um CSP consiste numa atribuição completa de valores às
variáveis, de tal forma que todas as restrições sejam satisfeitas.
Quando não existe nenhuma solução que satisfaça todas as restrições
simultaneamente, o problema é considerado inviável (infeasible).
@elsakka2015 esclarece que os CSPs são combinatórios por natureza e
que, para muitas das suas categorias, é improvável que exista um
algoritmo eficiente --- estes problemas são NP-completos, o que
significa que um algoritmo que garanta encontrar uma solução
satisfazendo todas as restrições tem um requisito de tempo exponencial
no pior caso.

Aplicado ao UCTP, cada aula a escalonar constitui uma variável, o
conjunto de períodos e salas disponíveis constitui o seu domínio, e as
restrições rígidas e flexíveis descritas na secção 2.2.4 constituem o
conjunto C. A resolução do problema consiste em encontrar uma atribuição
completa e consistente para todas as variáveis ([@elsakka2015]).

2.3.3 Programação por Restrições (Constraint
Programming --- CP)

A Programação por Restrições (CP) é o paradigma computacional que
operacionaliza a resolução de CSPs. Constitui uma área de investigação
em Inteligência Artificial que combina a expressividade declarativa da
programação lógica com a eficiência dos métodos de investigação
operacional ([@elsakka2015]). A sua principal vantagem reside na
capacidade de fornecer uma descrição declarativa precisa do problema em
termos de restrições, permitindo separar a definição do problema da
estratégia de resolução.

Os mecanismos fundamentais da CP incluem a propagação de restrições ---
que elimina valores dos domínios das variáveis que não podem fazer parte
de nenhuma solução válida --- e a pesquisa sistemática por
*backtracking*, que explora o espaço de soluções de forma organizada,
revertendo atribuições inválidas e tentando alternativas ([@dechter2003]). A combinação de ambos os mecanismos permitem reduzir
drasticamente o espaço de busca antes e durante a pesquisa, tornando
viável a resolução de instâncias de média e grande dimensão que seriam
computacionalmente intratáveis por enumeração exaustiva.

@elsakka2015 demonstra a aplicabilidade directa da CP ao UCTP,
modelando o problema como um CSP formal e resolvendo-o com um solver de
CP, obtendo horários sem conflitos para dados reais de uma instituição
universitária em tempo computacional de poucos segundos --- contra
vários dias de trabalho manual que o mesmo processo exigia
anteriormente.

2.3.4 Revisão da literatura: algoritmos
aplicados ao Timetabling Problem

A literatura sobre o UCTP documenta a aplicação de um amplo espectro de
abordagens algorítmicas ao longo das últimas décadas. @harshalatha2026 sintetizam as principais categorias e as suas limitações
comparativas no contexto do problema de geração de horários.

Os Algoritmos Genéticos (GA) são extensivamente utilizados pela sua
capacidade de exploração de grandes espaços de solução, simulando
processos de selecção natural através de operadores de cruzamento e
mutação. Contudo, são métodos inerentemente probabilísticos e não
garantem a satisfação de restrições rígidas. Quando ocorrem alterações
dinâmicas --- como ausência de um docente ou realocação de sala --- os
sistemas baseados em GA frequentemente requerem a regeneração completa
do horário, o que limita a adaptabilidade em tempo real ([@harshalatha2026]).

O Simulated Annealing (SA) e a Tabu Search (TS) são abordagens de
pesquisa local de solução única que demonstraram resultados competitivos
nos benchmarks do UCTP. @abdipoor2023 documentam que o SA, em
particular em abordagens híbridas colaborativas, figura entre os métodos
de melhor desempenho em vários conjuntos de referência. Contudo, estas
abordagens dependem fortemente da parametrização manual e não oferecem
garantias determinísticas de viabilidade.

As abordagens de Satisfação de Restrições e Programação por Restrições
oferecem soluções determinísticas, garantindo a satisfação de todas as
restrições rígidas por construção. @harshalatha2026 concluem
que, comparativamente às abordagens de GA e meta-heurísticas, a CP
garante a geração de horários sem conflitos, suporta actualizações em
tempo real e oferece escalabilidade e optimalidade, constituindo a
abordagem mais robusta para ambientes institucionais modernos.

2.4 Google OR-Tools e o Solver CP-SAT

2.4.1 Definição

O Google OR-Tools é uma suite de optimização de código aberto
desenvolvida pela equipa de Investigação Operacional da Google, que
disponibiliza ferramentas para a resolução de problemas de optimização
combinatória, incluindo problemas de escalonamento, roteamento e
satisfação de restrições ([@perron2023], citado em [@harshalatha2026]). A suite integra múltiplos solvers especializados, sendo o
CP-SAT o motor principal para problemas de Programação por Restrições
com variáveis inteiras.

2.4.2 Arquitectura interna do CP-SAT Solver

O CP-SAT é descrito pelos seus autores como uma implementação de um
solver de Programação por Restrições puramente integral, construído
sobre um solver SAT (*Satisfiability*) utilizando *Lazy Clause
Generation* ([@perron2023]). O solver inspira-se no *chuffed*
solver e na conferência CP 2013 de Peter Stuckey sobre *Lazy Clause
Generation*, que introduziu a ideia de gerar cláusulas de inferência
apenas quando necessário, evitando a sobrecarga de manter explicitamente
todas as implicações do modelo.

A arquitectura do CP-SAT assenta em dois avanços principais
relativamente ao seu antecessor ([@perron2023]). O primeiro é a
integração de um *simplex* ao lado do motor SAT, trazendo as vantagens
da relaxação linear sobre a componente linear do modelo completo e
iniciando a integração de tecnologia MIP (*Mixed Integer Programming*)
no solver --- incluindo pré-resolução, reduções duais, regras de
*branching* específicas, cortes e fixação por custo reduzido. O segundo
é a implementação de um portfólio de *workers* diversificados para a
fase de pesquisa, permitindo tentar novas ideias e incorporar técnicas
ortogonais com baixa complexidade. Estes *workers* classificam-se
segundo múltiplos critérios: encontrar soluções primais (através de
solvers completos, Pesquisa Local ou *Large Neighborhood Search*),
melhorar limites duais, ou reduzir o problema com ajuda de sondagem
contínua. A diversidade de comportamentos aumenta a robustez do solver,
enquanto a partilha contínua de informação entre *workers* produz
acelerações massivas na execução paralela.

Em termos de desempenho, @perron2023 caracterizam o CP-SAT como
um solver de estado da arte, com desempenho insuperado na comunidade de
Programação por Restrições, resultados de ruptura nos *benchmarks* de
escalonamento --- incluindo o fecho de muitos problemas em aberto --- e
resultados competitivos com os melhores solvers MIP em problemas
puramente inteiros.

2.4.3 Modelagem esparsa vs. densa: impacto na
escalabilidade

Uma decisão de modelagem com impacto directo na viabilidade
computacional do sistema é a escolha entre representação densa e
representação esparsa das variáveis de decisão. Na modelagem densa,
seriam criadas variáveis para todas as combinações possíveis entre
professores, turmas, salas e períodos --- incluindo combinações que são,
à partida, impossíveis ou proibidas pelas restrições do problema. Este
tipo de modelagem conduz a uma explosão no número de variáveis e
restrições, tornando o solver computacionalmente ineficiente para
instâncias de média e grande dimensão. Na modelagem esparsa, as
variáveis de decisão são criadas apenas para as relações válidas e
previamente filtradas. @harshalatha2026 aplicam este princípio
ao seu modelo CP-SAT, definindo variáveis binárias apenas para as
combinações de disciplina, sala, período e turma que satisfazem as
pré-condições do problema. A poda de restrições --- que elimina
combinações inviáveis antes da execução do solver --- reduz o espaço de
busca e melhora os tempos de resolução. Os autores documentam que esta
abordagem permite ao sistema suportar cenários com até 9 turmas e 45
disciplinas sem degradação de desempenho, com tempos de solução que
escalam de forma polinomial com a dimensão do problema.

2.4.4 Aplicação ao University Timetabling
Problem

A aplicação do OR-Tools CP-SAT ao problema de geração de horários
universitários encontra suporte directo na literatura. @harshalatha2026 demonstram que o sistema baseado em CP-SAT alcança zero
conflitos em todos os cenários testados --- pequeno (3 turmas, 15
disciplinas), médio (5 turmas, 25 disciplinas), grande (7 turmas, 35
disciplinas) e complexo (9 turmas, 45 disciplinas) ---, enquanto os
métodos manuais exibem crescimento exponencial do número de conflitos
com o aumento da complexidade.

[@elsakka2015] apresenta uma demonstração análoga com dados reais de
uma instituição universitária com cinco campi distribuídos
geograficamente, dois turnos diários e 42 docentes a leccionar em
simultâneo em múltiplos campi. O modelo CP produziu um horário completo
sem conflitos em poucos segundos, enquanto o processo manual requeria
vários dias de trabalho. O autor conclui que a aplicação de CP com
linguagem de optimização é um meio praticamente viável para o
escalonamento de horários universitários.

Comparativamente às abordagens meta-heurísticas dominantes na literatura
--- Algoritmos Genéticos, Simulated Annealing e Tabu Search ---, a
abordagem CP-SAT distingue-se por três propriedades fundamentais:
determinismo (garante a satisfação de todas as restrições rígidas),
adaptabilidade (suporta actualizações em tempo real sem regeneração
completa) e escalabilidade (os tempos de solução escalam polinomialmente
com a dimensão do problema) ([@harshalatha2026]).

