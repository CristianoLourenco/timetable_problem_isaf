## **4.6 Discussão dos resultados**

Os resultados obtidos confirmam parcialmente a hipótese H1 (Secção 1.5)
nos limites testados. Em todos os cenários --- sintéticos (CT01, CT02,
CT05) e reais (CT07) --- o sistema nunca produziu um único conflito de
professor, turma ou sala (RN01--RN03): esta garantia é absoluta por
construção do modelo CP-SAT, independente da escala testada. A carga
horária semanal (RN05), por sua vez, foi integralmente cumprida nos
cenários sintéticos de menor dimensão (CT01, CT02, CT05), mas apresentou
défice parcial no cenário à escala real do ISAF (CT07: 93,2% de
cobertura), reflectindo o compromisso deliberado entre tempo de
resolução e optimalidade formalizado na função objectivo (Secção 4.4.1)
--- o défice residual não representa uma falha do sistema, mas uma
alocação incompleta explicitamente sinalizada ao Gestor para resolução
manual (RF13). O mecanismo de diagnóstico estrutural (CT03, CT04)
cumpriu o RNF03 ao garantir que nenhum cenário sem solução resulta em
falha silenciosa, incluindo o caso de fronteira --- esgotamento do tempo
de resolução --- que poderia ser confundido com uma inviabilidade real.

Quanto ao tempo de distribuição, o Director da Área Académica estimou
verbalmente, em entrevista (Secção 3.6), que a distribuição manual do
horário de uma turma demora, em média, menos de 10 minutos quando as
disponibilidades dos docentes já estão disponibilizadas. Projectando
esta estimativa, de forma puramente indicativa, para a escala do
cenário CT07 (45 turmas) --- e assumindo distribuição sequencial, sem
sobreposição de esforço entre turmas nem retrabalho por conflitos
descobertos tardiamente ---, obtém-se um limite superior aproximado de
7,5 horas de trabalho manual, contra os 95,3 segundos (~1 minuto e 35
segundos) que o sistema levou a produzir 973 das 1044 alocações da
mesma escala. Esta comparação **não constitui uma medição documentada
nem validada** do ganho de eficiência: baseia-se numa única estimativa
verbal, não cronometrada, referente à distribuição de uma turma
isolada, e não contempla o tempo de resolução de conflitos entre
turmas nem o desgaste cognitivo acumulado ao longo de um processo de
várias horas --- factores que a experiência relatada pelos entrevistados
(Secção 3.6) sugere tornarem o processo manual real mais moroso do que
uma simples multiplicação linear. A projecção é apresentada como
indício da ordem de grandeza da diferença de desempenho, não como
resultado quantitativo rigoroso; a medição directa e comparável
permanece identificada como limitação (ver abaixo) e como direcção de
trabalho futuro (Secção 5.2).

A hipótese H2 (Secção 1.5) confirma-se: a integração entre Flutter,
FastAPI e o algoritmo de optimização CP-SAT em Python resultou numa
solução tecnicamente viável e funcional, como demonstram a arquitectura
implementada (Secção 4.3) e a sua validação directa contra os cenários
de teste, incluindo os dados reais do ISAF (CT07).

Dois limites da validação efectuada devem ser assinalados com rigor
científico. Primeiro, embora o cenário CT07 valide o sistema directamente
contra dados reais do ISAF a uma escala substancialmente superior aos
cenários sintéticos (45 turmas e 104 docentes, face às 12 turmas e 8
docentes de CT02), esta escala cobre apenas um semestre da instituição e
fica ainda aquém da totalidade do limite superior formalmente definido
pelo RNF01 (100+ professores, 60+ turmas); a modelagem esparsa (Secção
2.4.3) sustenta teoricamente a escalabilidade do sistema para essa
totalidade, mas essa extrapolação completa não foi validada
empiricamente neste trabalho. Segundo, apesar de o cenário CT07
demonstrar a correcção do sistema contra dados reais de entrada da
instituição, não foi possível realizar a análise comparativa de
desempenho prevista na Secção 3.7 entre os horários gerados pelo sistema
e os horários actualmente distribuídos manualmente pela instituição no
seu sistema de gestão escolar (Anexo A), por ausência de um registo
estruturado dos conflitos desse processo histórico (limitação
identificada na Secção 5.1) --- a validação obtida circunscreve-se,
portanto, à correcção matemática do sistema face às restrições
formalizadas e à sua aplicabilidade directa aos dados reais do ISAF, e
não a uma medição directa e documentada do ganho de eficiência face à
distribuição manual; a única evidência disponível quanto ao tempo é a
estimativa verbal pontual referida acima, que aponta para uma diferença
de desempenho de ordens de grandeza, mas não a quantifica com rigor.
Ambos os limites motivam as recomendações apresentadas na Secção 5.2.
