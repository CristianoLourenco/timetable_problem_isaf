## 2.4 Google OR-Tools e o Solver CP-SAT

### 2.4.1 Definição

O Google OR-Tools é uma suite de optimização de código aberto
desenvolvida pela equipa de Investigação Operacional da Google, que
disponibiliza ferramentas para a resolução de problemas de optimização
combinatória, incluindo problemas de escalonamento, roteamento e
satisfação de restrições [@perron2023]. A suite integra múltiplos
solvers especializados, sendo o CP-SAT o motor principal para problemas
de Programação por Restrições com variáveis inteiras.

### 2.4.2 Arquitectura interna do CP-SAT Solver

O CP-SAT é descrito pelos seus autores como uma implementação de um
solver de Programação por Restrições puramente integral, construído
sobre um solver SAT (*Satisfiability*) utilizando *Lazy Clause
Generation* [@perron2023]. O solver inspira-se no *chuffed*
solver e na conferência CP 2013 de Peter Stuckey sobre *Lazy Clause
Generation*, que introduziu a ideia de gerar cláusulas de inferência
apenas quando necessário, evitando a sobrecarga de manter explicitamente
todas as implicações do modelo.

A arquitectura do CP-SAT assenta em dois avanços principais
relativamente ao seu antecessor [@perron2023]. O primeiro é a
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

### 2.4.3 Modelagem esparsa vs. densa: impacto na escalabilidade

Uma decisão de modelagem com impacto directo na viabilidade
computacional do sistema é a escolha entre representação densa e
representação esparsa das variáveis de decisão. Na modelagem densa,
seriam criadas variáveis para todas as combinações possíveis entre
professores, turmas, salas e períodos --- incluindo combinações que são,
à partida, impossíveis ou proibidas pelas restrições do problema. Este
tipo de modelagem conduz a uma explosão no número de variáveis e
restrições, tornando o solver computacionalmente ineficiente para
instâncias de média e grande dimensão [@dechter2003]. Na modelagem
esparsa, as variáveis de decisão são criadas apenas para as relações
válidas e previamente filtradas --- a poda de combinações inviáveis
antes da execução do solver reduz o espaço de busca e melhora os
tempos de resolução, um princípio aplicado directamente na construção do
motor deste trabalho (Secção 4.4.1) e validado empiricamente à escala
real do ISAF (Secção 4.5, CT07).

### 2.4.4 Aplicação ao University Timetabling Problem

A aplicação do OR-Tools CP-SAT ao problema de geração de horários
universitários encontra suporte directo na literatura. @elsakka2015
apresenta uma demonstração com dados reais de uma instituição
universitária com cinco campi distribuídos geograficamente, dois turnos
diários e 42 docentes a leccionar em simultâneo em múltiplos campi. O
modelo CP produziu um horário completo sem conflitos em poucos segundos,
enquanto o processo manual requeria vários dias de trabalho. O autor
conclui que a aplicação de CP com linguagem de optimização é um meio
praticamente viável para o escalonamento de horários universitários.

Comparativamente às abordagens meta-heurísticas dominantes na literatura
--- Algoritmos Genéticos, Simulated Annealing e Tabu Search ---, a
abordagem CP-SAT distingue-se por três propriedades fundamentais:
determinismo (garante a satisfação de todas as restrições rígidas por
construção, ao contrário dos métodos probabilísticos [@bashab2023]),
desempenho competitivo face aos melhores solvers da sua classe, incluindo
em problemas MIP puramente inteiros [@perron2023], e escalabilidade por
via da modelagem esparsa (Secção 2.4.3), validada empiricamente à escala
real do ISAF neste trabalho (Secção 4.5, CT07).
