# Tabela Dataverse: Cloud Service

Nome lógico `mcsft_cloudservice` (conjunto `mcsft_cloudservices`), tipo Standard. Lida a 7 de novembro de 2026 pela Web API (`EntityDefinitions`).

| Coluna (nome a mostrar) | Nome lógico | Tipo | Limite / opções |
|---|---|---|---|
| Service Title (coluna principal) | `mcsft_servicetitle` | Texto (uma linha) | 850 caracteres |
| Provider | `mcsft_provider` | Texto (uma linha) | 100 caracteres |
| Service Description | `mcsft_servicedescription` | Texto (uma linha) | 100 caracteres |
| Service Model | `mcsft_servicemodel` | Escolha local (`mcsft_cloudservice_mcsft_servicemodel`) | 1 IaaS · 2 PaaS · 3 SaaS |
| Status | `mcsft_status` | Escolha local (`mcsft_cloudservice_mcsft_status`) | 0 Descontinuado · 1 Ativo · 291310001 Em avaliação |

Conteúdo a 8/11/2026: 375 registos, 63 IaaS, 219 PaaS e 93 SaaS; 32 com o estado Descontinuado.

## Notas

- A 7/11/2026 foi apagado um registo lixo (a linha de cabeçalho de uma importação CSV: "Titulo", "Fornecedor", "Descricao") com `mcsft_servicemodel = 0`. O 0 não é uma opção válida e qualquer pedido que lesse o Modelo com essa linha falhava com "Foram recebidos dados inválidos a partir da rede".
- O ambiente tem também uma tabela `mcsft_cloudservice1` com o mesmo nome a mostrar. A app usa `mcsft_cloudservice`.

# Tabelas Dataverse da Ficha 04: Cliente e Pedido

Criadas na solução DAC2627 com o prefixo `dac`. Lidas a 16 de novembro de 2026 no `customizations.xml` da exportação 1.0.0.1.

## Cliente (`dac_cliente`, no Studio `Clientes`)

| Coluna (nome a mostrar) | Nome lógico | Tipo | Obrigatória | Limite / formato |
|---|---|---|---|---|
| Nome (coluna principal) | `dac_nome` | Texto (uma linha) | não | 850 caracteres |
| NIF | `dac_nif` | Texto (uma linha) | sim | 9 caracteres |
| Email | `dac_email` | Texto (uma linha) | sim | 100 caracteres, formato email |
| Telefone | `dac_telefone` | Texto (uma linha) | sim | 100 caracteres, formato telefone |

Pesquisa rápida («Localização Rápida de Entidades Clientes Ativas»): procura por Nome, NIF e Email. Configurada à mão no designer da vista, porque a Web API recusa a alteração.

## Pedido (`dac_pedido`, no Studio `Pedidos`)

| Coluna (nome a mostrar) | Nome lógico | Tipo | Obrigatória | Limite / opções |
|---|---|---|---|---|
| NumeroPedido (coluna principal) | `dac_numeropedido` | Número automático | sim | `PED-{SEQNUM:4}`, 20 caracteres |
| Clientes | `dac_cliente` | Pesquisa para Cliente | sim | relação `dac_Cliente_Pedido` |
| DataPedido | `dac_datapedido` | Data | sim | só data |
| EstadoPedido | `dac_estado` | Escolha local (`dac_pedido_dac_estado`) | sim | 774300000 Pendente · 774300001 Em Processamento · 774300002 Concluído · 774300003 Cancelado |
| Valor | `dac_valor` | Moeda | sim | 2 casas decimais |
| Descrição | `dac_descricao` | Texto (várias linhas) | sim | 2000 caracteres |

### Colunas da Ficha 04 · Melhoramento (20/11/2026)

Escritas pelos fluxos, nunca pela app. No formulário principal do Pedido estão nas secções «Processamento (escrito pelo fluxo)» e «Revisão humana (escrito pelo fluxo)», só de leitura. Rótulos em português (2070).

| Coluna (nome a mostrar) | Nome lógico | Tipo | Opções / notas |
|---|---|---|---|
| Tratamento | `dac_tratamento` | Escolha local | 774300000 Por processar (omissão) · 774300001 Automático · 774300002 Revisão · 774300003 Erro |
| Processado | `dac_processado` | Sim/Não | Não por omissão |
| DataProcessamento | `dac_dataprocessamento` | Data e hora | comportamento Local do utilizador |
| ObservacoesProcessamento | `dac_observacoesprocessamento` | Texto (várias linhas) | 2000 caracteres |
| IdExecucao | `dac_idexecucao` | Texto (uma linha) | `workflow()?['run']?['name']`, 100 caracteres |
| ValorProcessado | `dac_valorprocessado` | Moeda | valor que o fluxo classificou (idempotência) |
| Decisao | `dac_decisao` | Escolha local | 774300000 Aguarda decisão · 774300001 Aprovado · 774300002 Rejeitado |
| ComentarioDecisao | `dac_comentariodecisao` | Texto (várias linhas) | 2000 caracteres |
| DataDecisao | `dac_datadecisao` | Data e hora | |

Os pedidos que já existiam antes de 20/11/2026 ficam com Tratamento vazio («Não processado» na app): o fluxo só trata pedidos criados depois ou cujo Valor mude.

Obrigatória quer dizer obrigatória nas aplicações (`ApplicationRequired`). A Web API aceitou a 20/11/2026 um pedido sem Valor (PED-1182), e é para esse caso que o fluxo tem o ramo «Dados inválidos».

Variáveis de ambiente da solução: `dac_LimiteRevisao` (decimal, 500) e `dac_LigacaoApp` (texto, o endereço da app nos emails, v1.6.0). A `dac_LigacaoApp` substitui a `dac_AprovadorEmail`, retirada a 20/11/2026 com o acordo do utilizador, porque deixou de ser usada e levava o email do dono em cada exportação.

### Colunas da Ficha 04 · Revisão (v1.6.0, 20/11/2026)

Criadas por `dataverse/revisao_modelo.js`. Registado por é escrito pela app ao registar um pedido no `scrL4Revisao`. As restantes são escritas só pelo fluxo `DAC2627_Pedido_Decidir`.

| Coluna (nome a mostrar) | Nome lógico | Tipo | Notas |
|---|---|---|---|
| Registado por | `dac_registadopor` | Pesquisa para Utilizador | relação `dac_Utilizador_Pedido_Registado` |
| Proposta por | `dac_propostapor` | Pesquisa para Utilizador | relação `dac_Utilizador_Pedido_Proposta`, o Gestor |
| Decidido por | `dac_decididopor` | Pesquisa para Utilizador | relação `dac_Utilizador_Pedido_Decisao`, o Admin |
| Comentário da proposta | `dac_comentarioproposta` | Texto (várias linhas) | 2000 caracteres |
| Data da proposta | `dac_dataproposta` | Data e hora | |

A Decisão ganhou duas opções: 774300003 «Proposta: aprovar» e 774300004 «Proposta: rejeitar». As três relações removem a ligação quando o utilizador é apagado.

Vistas públicas usadas no `Filter` da app: «Pedidos Pendentes» e «Pedidos Concluídos», com Estado igual a Ativo, o valor da escolha e DataPedido por ordem descendente.

## Relação

`dac_Cliente_Pedido`: 1:N de Cliente para Pedido, com Eliminar em **Restringir**. Um cliente com pedidos não pode ser apagado, nem na app nem fora dela.

# Tabela Dataverse da Ficha 04 · Revisão: Utilizador

Nome lógico `dac_utilizador` (conjunto `dac_utilizadors`, no Studio `Utilizadores`), na solução DAC2627, criada a 20/11/2026 por `dataverse/revisao_modelo.js`. A password nunca é guardada: só o hash PBKDF2 e o salt.

| Coluna (nome a mostrar) | Nome lógico | Tipo | Notas |
|---|---|---|---|
| Nome (coluna principal) | `dac_nome` | Texto (uma linha) | obrigatória, 100 caracteres |
| Email | `dac_email` | Texto (uma linha), formato email | obrigatória, única pela chave alternativa `dac_chave_email` |
| Perfil | `dac_perfil` | Escolha local | 774300000 Admin · 774300001 Gestor · 774300002 Cliente (omissão), obrigatória |
| Hash da password | `dac_passwordhash` | Texto (uma linha) | **segurança de coluna**, Base64 |
| Salt da password | `dac_passwordsalt` | Texto (uma linha) | **segurança de coluna**, 16 bytes em Base64 |
| Iterações | `dac_iteracoes` | Número inteiro | 600 000 |
| Algoritmo | `dac_algoritmo` | Texto (uma linha) | PBKDF2-SHA256 |
| Ativo | `dac_ativo` | Sim/Não | Sim por omissão |
| Tentativas falhadas | `dac_tentativasfalhadas` | Número inteiro | 5 seguidas bloqueiam 15 minutos |
| Bloqueado até | `dac_bloqueadoate` | Data e hora | |
| Último acesso | `dac_ultimoacesso` | Data e hora | |
| Testemunho de sessão | `dac_sessaotoken` | Texto (uma linha) | **segurança de coluna**, 64 carateres hexadecimais |
| Sessão expira | `dac_sessaoexpira` | Data e hora | 8 horas depois da entrada |
| Cliente | `dac_cliente` | Pesquisa para Cliente | relação `dac_Cliente_Utilizador`, só no perfil Cliente |

Segurança de coluna: sem um perfil de segurança de campos, só o administrador do sistema lê o hash, o salt e o testemunho. Os fluxos correm com a ligação do dono da solução e leem-nos, a app nunca os pede.

Utilizadores de demonstração criados a 20/11/2026: Admin Demo, Gestor Demo e Cliente Demo (este associado a «Vinhos do Varosa, Lda»), com emails do dono da solução com o sufixo +admin, +gestor e +cliente. As passwords foram entregues ao utilizador num ficheiro à parte e não estão no repositório.
