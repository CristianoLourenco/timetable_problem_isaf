## **4.6 Discussão dos resultados**

Os resultados obtidos confirmam parcialmente a hipótese H1 (Secção 1.5)
nos limites testados. Em todos os cenários --- sintéticos (CT01, CT02,
CT05) e reais (CT07) --- o motor nunca produziu um único conflito de
professor, turma ou sala (RN01--RN03): esta garantia é absoluta por
construção do modelo CP-SAT, independente da escala testada. A carga
horária semanal (RN05), por sua vez, foi integralmente cumprida nos
cenários sintéticos de menor dimensão (CT01, CT02, CT05), mas apresentou
défice parcial no cenário à escala real do ISAF (CT07: 93,2% de
cobertura), reflectindo o compromisso deliberado entre tempo de
resolução e optimalidade formalizado na função objectivo (Secção 4.4.1)
--- o défice residual não representa uma falha do motor, mas uma
alocação incompleta explicitamente sinalizada ao Gestor para resolução
manual (RF13). O mecanismo de diagnóstico estrutural (CT03, CT04)
cumpriu o RNF03 ao garantir que nenhum cenário sem solução resulta em
falha silenciosa, incluindo o caso de fronteira --- esgotamento do tempo
de resolução --- que poderia ser confundido com uma inviabilidade real.

Dois limites da validação efectuada devem ser assinalados com rigor
científico. Primeiro, embora o cenário CT07 valide o motor directamente
contra dados reais do ISAF a uma escala substancialmente superior aos
cenários sintéticos (45 turmas e 104 docentes, face às 12 turmas e 8
docentes de CT02), esta escala cobre apenas um semestre da instituição e
fica ainda aquém da totalidade do limite superior formalmente definido
pelo RNF01 (100+ professores, 60+ turmas); a modelagem esparsa (Secção
2.4.3) sustenta teoricamente a escalabilidade do motor para essa
totalidade, mas essa extrapolação completa não foi validada
empiricamente neste trabalho. Segundo, apesar de o cenário CT07
demonstrar a correcção do motor contra dados reais de entrada da
instituição, não foi possível realizar a análise comparativa de
desempenho prevista na Secção 3.7 entre os horários gerados pelo motor
CP-SAT e os horários actualmente produzidos manualmente pela instituição
(Anexo A), por ausência de um registo estruturado dos conflitos do
processo manual histórico (limitação identificada na Secção 5.1) --- a
validação obtida circunscreve-se, portanto, à correcção matemática do
motor face às restrições formalizadas e à sua aplicabilidade directa aos
dados reais do ISAF, e não a uma medição directa do ganho de eficiência
face ao processo manual. Ambos os limites motivam as recomendações
apresentadas na Secção 5.2.
