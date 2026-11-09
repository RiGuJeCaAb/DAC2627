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
