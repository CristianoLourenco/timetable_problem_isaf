REFERÊNCIAS

::: {#refs}
:::

APÊNDICES

Apêndice A --- Código-fonte do Motor de
Optimização

**\[PLACEHOLDER --- Inserir excertos comentados do módulo CP-SAT após
conclusão da implementação do backend\]**

Apêndice B --- Especificação Textual dos Casos
de Uso

UC06 --- Importar Dados em Massa via Excel

**Ator Principal:** Gestor Académico/Secretaria

**Pré-condições:** Gestor autenticado (UC13); ficheiro Excel no formato
institucional esperado.

**Gatilho:** O Gestor selecciona \"Importar Dados\" e escolhe a
entidade-alvo.

**Fluxo Principal:** 1. O Gestor selecciona a entidade e carrega o
ficheiro Excel. 2. O sistema invoca UC07 --- Validar Dados Importados
(\<\<include\>\>). 3. O sistema apresenta o resultado da validação
(registos válidos, inválidos, duplicados) para confirmação. 4. O Gestor
confirma a gravação. 5. O sistema aplica a regra de idempotência (RF08).
6. O sistema grava os registos novos e apresenta o relatório final.

**Fluxo Alternativo A1:** Cancelamento antes da confirmação --- nenhum
dado é gravado.

**Fluxo de Excepção E1:** Ficheiro em formato inválido --- o sistema
rejeita e informa o formato esperado.

**Garantia de Sucesso:** Registos válidos e não duplicados persistidos
na base de dados.

**Garantia Mínima:** Nenhum registo parcialmente importado --- operação
transaccional.

UC08 --- Disparar Geração de Horário

**Ator Principal:** Gestor Académico/Secretaria

**Pré-condições:** Dados, mestre, completos e disponibilidades
registadas; Gestor autenticado (UC13).

**Gatilho:** O Gestor selecciona \"Gerar Horário\".

**Fluxo Principal:** 1. O Gestor solicita a geração. 2. O sistema cria
um Job assíncrono e devolve um Job ID (RNF02). 3. O sistema executa o
motor CP-SAT em segundo plano, aplicando RN01--RN09 e a função
objectivo. 4. O motor devolve uma solução óptima ou quase-óptima \[Ponto
de Extensão: \"Sem Solução Viável\"\]. 5. O sistema associa o resultado
ao Job ID e marca o estado como concluído.

**Extensão condicional (passo 4):** Se o solver não conseguir satisfazer
as restrições após relaxamento das soft constraints, invoca UC09
(\<\<extend\>\>).

**Garantia de Sucesso:** Horário completo persistido e disponível para
consulta (UC11, UC12).

**Garantia Mínima:** Mesmo em INFEASIBLE, o Job é marcado como Falhado
com o motivo registado --- o sistema nunca falha silenciosamente
(RNF03).

UC13 --- Autenticar-se

**Atores:** Gestor Académico/Secretaria; Professor

**Pré-condição:** O actor possui conta registada no Firebase
Authentication.

**Fluxo Principal:** 1. O actor submete email e password na aplicação
Flutter. 2. A aplicação envia as credenciais ao backend FastAPI
(`POST /auth/login`) --- o cliente nunca comunica directamente com o
Firebase Authentication. 3. O backend troca as credenciais pela REST API
do Firebase Identity Toolkit e devolve à aplicação Flutter um ID Token e
um Refresh Token. 4. A aplicação Flutter anexa o ID Token a cada pedido
subsequente ao backend FastAPI (cabeçalho `Authorization: Bearer`). 5. O
backend valida o ID Token contra os certificados públicos do Google
antes de processar qualquer pedido (RN09).

**Fluxo de Excepção E1:** Credenciais inválidas --- mensagem de erro
genérica, sem indicar qual campo falhou.

**Fluxo de Excepção E2:** Token expirado --- backend devolve HTTP 401; a
aplicação Flutter tenta renovação silenciosa via `POST /auth/refresh`;
novo login só é exigido se essa renovação falhar.

**Garantia Mínima:** Nenhuma sessão é criada sem validação bem-sucedida
da identidade.

Apêndice C --- Capturas de Ecrã do Sistema

**\[PLACEHOLDER --- Inserir capturas de ecrã da interface Flutter
(autenticação, gestão de entidades, grelha de horário) e da documentação
Swagger da API após conclusão do frontend\]**

ANEXOS

**\[PLACEHOLDER --- Inserir, caso aplicável, documentos institucionais
de suporte, como o modelo de horário manual actualmente em uso no
ISAF.**
