# 5. CONCLUSÃO E RECOMENDAÇÕES

O presente trabalho propôs-se desenvolver um sistema inteligente para a
geração automática de horários académicos no ISAF, recorrendo a
técnicas de IA simbólica --- Programação por Restrições com o solver
Google OR-Tools CP-SAT --- integradas numa arquitectura de três camadas
composta por Flutter na apresentação, FastAPI na integração e
PostgreSQL na persistência; a implementação técnica e a validação do
sistema, detalhadas nos objectivos específicos (Secção 1.6.2), são
discutidas de seguida.

Dos cinco objectivos específicos definidos no Capítulo 1, quatro foram
integralmente cumpridos: os requisitos funcionais e não funcionais foram
levantados e formalizados segundo as normas IEEE 830 e ISO/IEC/IEEE
29148, com dezassete requisitos funcionais, sete não funcionais e doze
regras de negócio rastreáveis; o problema foi modelado formalmente como
CSP com componente de optimização e implementado num sistema CP-SAT
funcional; a API REST e a persistência dos dados académicos foram
desenvolvidas com FastAPI e PostgreSQL; e a interface de utilizador foi
construída em Flutter, cobrindo a gestão de entidades académicas, a
visualização de horários e a exportação de resultados. O quinto
objectivo --- validar o sistema comparando os resultados com a
distribuição manual de horários no sistema de gestão escolar do ISAF ---
foi parcialmente cumprido: o sistema foi submetido a cenários de teste
progressivos (cf. Secção 4.5), incluindo cenários sintéticos de escala
crescente, dois cenários de inviabilidade intencional para validação do
mecanismo de diagnóstico, e um cenário adicional (CT07) validado
directamente contra dados reais extraídos da grade curricular do ISAF
(45 turmas, 104 docentes, 2025/2026); mas a comparação quantitativa
directa com essa distribuição manual, prevista na Secção 3.7, não foi
realizada, por ausência de um registo estruturado dos conflitos desse
processo histórico (cf. Secção 5.1). O cenário
de maior escala testado com dados reais (CT07, 45 turmas) fica ainda
aquém do limite superior formalmente definido pelo RNF01 (100+
professores, 60+ turmas); a validação empírica nesse limite fica
identificada como trabalho futuro (cf. Secção 5.2).

Os resultados confirmam a hipótese H1: nos cenários matematicamente
viáveis, o sistema garantiu horários sem conflitos com tempos de resolução
dentro dos limites estabelecidos. O mecanismo de diagnóstico estrutural
--- que verifica, antes da resolução, causas comuns de inviabilidade
como ausência de professor qualificado, capacidade de sala insuficiente
ou carga horária incompatível com o agrupamento em blocos (RN06) ---
assegurou que os cenários sem solução produzem um relatório de
diagnóstico em vez de uma falha silenciosa, cumprindo o RNF03.

## 5.1 Limitações do estudo

Reconhecem-se três limitações centrais deste trabalho. Primeira, e mais
significativa, a ausência de comparação quantitativa directa com a
distribuição manual de horários no sistema de gestão escolar do ISAF:
embora os 86 horários manuais vigentes em 2025/2026 tenham sido
recolhidos (Anexo A) e um cenário adicional (CT07) tenha validado o
sistema directamente contra dados reais de entrada da instituição (45
turmas, 104 docentes), não existe um registo estruturado dos conflitos
de alocação desse processo histórico que permita medir a redução
efectiva proporcionada pelo sistema. A única evidência disponível quanto
ao tempo do processo manual é uma estimativa verbal pontual do Director
da Área Académica (Secção 3.6: menos de 10 minutos por turma, sem
disponibilidades docentes por resolver), que, projectada de forma
puramente indicativa para a escala de CT07, sugere uma diferença de
desempenho de ordens de grandeza face aos 95,3 segundos do sistema
(Secção 4.6) --- mas que não substitui uma medição documentada e
comparável, por não ser cronometrada, não cobrir o esforço de resolução
de conflitos entre turmas, e reflectir a distribuição de uma única
turma, não do conjunto. A validação obtida circunscreve-se, portanto, à
correcção matemática do sistema face às restrições formalizadas e a este
indício qualitativo de eficiência, não a uma medição rigorosa. Segunda,
a validação empírica não cobre a
totalidade do RNF01 (100+ professores, 60+ turmas): o maior cenário
testado com dados reais (CT07) cobre 45 turmas e 104 docentes de um
único semestre, ficando a validação ao limite superior do requisito
identificada como trabalho futuro. Terceira, o código-fonte do motor de
optimização, embora referenciado no Apêndice A com rastreabilidade
directa aos requisitos funcionais e regras de negócio implementados, não
é reproduzido integralmente no corpo do documento, remetendo para o
repositório do projecto.
