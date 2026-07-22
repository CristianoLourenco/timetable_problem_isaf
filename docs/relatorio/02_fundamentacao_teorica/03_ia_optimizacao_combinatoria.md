## 2.3 Inteligência Artificial para Optimização Combinatória

### 2.3.1 IA simbólica vs. IA subsimbólica

A Inteligência Artificial (IA) divide-se em dois grandes paradigmas com
fundamentos e abordagens distintos. A IA simbólica --- também designada
IA clássica ou IA baseada em conhecimento --- opera sobre representações
explícitas do mundo sob a forma de símbolos, regras e restrições
lógicas. O seu funcionamento é determinístico e interpretável: dado um
conjunto de restrições bem definidas, o sistema procura sistematicamente
uma atribuição de valores às variáveis que satisfaça todas as condições
impostas [@russellnorvig2021]. A IA subsimbólica, por contraste,
engloba abordagens como as redes neuronais artificiais e a aprendizagem
por reforço, que aprendem padrões a partir de dados históricos sem que
as regras sejam explicitamente programadas.

Para o problema de geração automática de horários, a abordagem simbólica
é a mais adequada. O domínio do problema é completamente especificável
em termos de restrições formais --- não há incerteza sobre as regras,
apenas complexidade combinatória na sua satisfação simultânea. Esta
escolha é consistente com a revisão sistemática de @oudevrielink2019,
que identifica a garantia de satisfação de restrições rígidas como
requisito recorrente na literatura de timetabling institucional ---
propriedade que as abordagens de IA subsimbólica, como redes neuronais e
aprendizagem por reforço, não oferecem de forma intrínseca, ao
contrário dos métodos baseados em restrições formais [@dechter2003].

### 2.3.2 Satisfação de Restrições (Constraint Satisfaction Problem --- CSP)

O Problema de Satisfação de Restrições (CSP) é o formalismo matemático
central da IA simbólica aplicada a problemas de escalonamento. Um CSP é
definido como um triplo (X, D, C), onde X = {x₁, \..., xₙ} representa o
conjunto de variáveis, D = {D₁, \..., Dₙ} representa os domínios de
valores possíveis para cada variável, e C = {C₁, \..., Cₖ} representa o
conjunto de restrições que limitam os valores que as variáveis podem
assumir simultaneamente [@russellnorvig2021; @elsakka2015].

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
completa e consistente para todas as variáveis [@elsakka2015].

### 2.3.3 Programação por Restrições (Constraint Programming --- CP)

A Programação por Restrições (CP) é o paradigma computacional que
operacionaliza a resolução de CSPs. Constitui uma área de investigação
em Inteligência Artificial que combina a expressividade declarativa da
programação lógica com a eficiência dos métodos de investigação
operacional [@elsakka2015]. A sua principal vantagem reside na
capacidade de fornecer uma descrição declarativa precisa do problema em
termos de restrições, permitindo separar a definição do problema da
estratégia de resolução.

Os mecanismos fundamentais da CP incluem a propagação de restrições ---
que elimina valores dos domínios das variáveis que não podem fazer parte
de nenhuma solução válida --- e a pesquisa sistemática por
*backtracking*, que explora o espaço de soluções de forma organizada,
revertendo atribuições inválidas e tentando alternativas [@dechter2003]. A combinação de ambos os mecanismos permitem reduzir
drasticamente o espaço de busca antes e durante a pesquisa, tornando
viável a resolução de instâncias de média e grande dimensão que seriam
computacionalmente intratáveis por enumeração exaustiva.

@elsakka2015 demonstra a aplicabilidade directa da CP ao UCTP,
modelando o problema como um CSP formal e resolvendo-o com um solver de
CP, obtendo horários sem conflitos para dados reais de uma instituição
universitária em tempo computacional de poucos segundos --- contra
vários dias de trabalho manual que o mesmo processo exigia
anteriormente.

### 2.3.4 Revisão da literatura: algoritmos aplicados ao Timetabling Problem

A literatura sobre o UCTP documenta a aplicação de um amplo espectro de
abordagens algorítmicas ao longo das últimas décadas. @bashab2023
sintetizam as principais categorias e as suas limitações comparativas no
contexto do problema de geração de horários, num levantamento que
abrange metodologias, benchmarks e questões em aberto na área.

Os Algoritmos Genéticos (GA) são extensivamente utilizados pela sua
capacidade de exploração de grandes espaços de solução, simulando
processos de selecção natural através de operadores de cruzamento e
mutação. Contudo, são métodos inerentemente probabilísticos e não
garantem a satisfação de restrições rígidas [@bashab2023]. Quando
ocorrem alterações dinâmicas --- como ausência de um docente ou
realocação de sala --- os sistemas baseados em GA frequentemente
requerem a regeneração completa do horário, o que limita a
adaptabilidade em tempo real.

O Simulated Annealing (SA) e a Tabu Search (TS) são abordagens de
pesquisa local de solução única que demonstraram resultados competitivos
nos benchmarks do UCTP. @abdipoor2023 documentam que o SA, em
particular em abordagens híbridas colaborativas, figura entre os métodos
de melhor desempenho em vários conjuntos de referência. Contudo, estas
abordagens dependem fortemente da parametrização manual e não oferecem
garantias determinísticas de viabilidade.

As abordagens de Satisfação de Restrições e Programação por Restrições
oferecem soluções determinísticas, garantindo a satisfação de todas as
restrições rígidas por construção [@dechter2003]. Comparativamente às
abordagens de GA e meta-heurísticas, a CP garante a geração de horários
sem conflitos por construção e oferece garantias formais de optimalidade
quando o espaço de busca é explorado até à exaustão [@elsakka2015],
constituindo por isso a abordagem adoptada neste trabalho.
