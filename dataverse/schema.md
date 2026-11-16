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

Vistas públicas usadas no `Filter` da app: «Pedidos Pendentes» e «Pedidos Concluídos», com Estado igual a Ativo, o valor da escolha e DataPedido por ordem descendente.

## Relação

`dac_Cliente_Pedido`: 1:N de Cliente para Pedido, com Eliminar em **Restringir**. Um cliente com pedidos não pode ser apagado, nem na app nem fora dela.
