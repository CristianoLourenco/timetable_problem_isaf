# 5. CONCLUSÃO E RECOMENDAÇÕES

O presente trabalho propôs-se desenvolver, implementar e validar um
sistema inteligente para a geração automática de horários académicos no
ISAF, recorrendo a técnicas de IA simbólica --- Programação por
Restrições com o solver Google OR-Tools CP-SAT --- integradas numa
arquitectura de três camadas composta por Flutter na apresentação,
FastAPI na integração e PostgreSQL na persistência.

Os objectivos específicos definidos no Capítulo 1 foram cumpridos: os
requisitos funcionais e não funcionais foram levantados e formalizados
segundo as normas IEEE 830 e ISO/IEC/IEEE 29148, com dezassete
requisitos funcionais, sete não funcionais e nove regras de negócio
rastreáveis; o problema foi modelado formalmente como CSP com componente
de optimização; a modelação do sistema foi documentada através de
diagrama de contexto, diagrama de casos de uso, diagrama de classes,
diagrama entidade-relacional e diagrama de sequência; e o sistema foi
submetido a cenários de teste progressivos, incluindo cenário de stress
no limite superior do RNF01 e cenário de inviabilidade intencional para
validação do mecanismo de diagnóstico.

Os resultados confirmam a hipótese H1: nos cenários matematicamente
viáveis, o motor garantiu horários sem conflitos com tempos de resolução
dentro dos limites estabelecidos. O mecanismo de variáveis de folga
assegurou que os cenários sem solução produzem um relatório de
diagnóstico em vez de uma falha silenciosa, cumprindo o RNF03.

## 5.1 Limitações do estudo

Reconhece-se como limitação central a ausência de validação com dados
reais e completos do ISAF, decorrente da não disponibilização formal dos
registos institucionais durante a fase de desenvolvimento. Os testes
foram conduzidos com instâncias de referência internacional, que, embora
representativas da classe de problemas, podem não capturar todas as
especificidades do contexto angolano.

## 5.2 Recomendações

Recomenda-se: (i) a actualização do sistema com os dados institucionais
reais do ISAF e a realização de uma validação de campo com os
utilizadores finais; (ii) a implementação da reoptimização incremental
(RF14), permitindo ajustes manuais sem recálculo integral do horário;
(iii) a integração com serviços de calendário externos, nomeadamente a
Google Calendar API (RF17), permitindo a exportação e sincronização
automática dos horários gerados para as agendas pessoais de docentes e
estudantes; e (iv) a extensão do estudo a outras instituições angolanas
de ensino superior, contribuindo para a generalização da solução e para
a modernização da gestão académica no país.