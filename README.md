# APP DAC2627 — código-fonte

Canvas app do Power Apps que reúne os laboratórios da UC **Desenvolvimento de Aplicações na Cloud** (CTeSP Computação Cloud, ESTGL/IPV, 2026/27) atrás de um ecrã inicial. Este repositório tem o código extraído da solução **DAC2627** (não gerida, versão 1.0.0.0), exportada a 8 de novembro de 2026 depois da publicação com as correções de responsividade.

| Item | Valor |
|---|---|
| App | `DAC2627_RGJCA` (Canvas, tablet/responsiva) |
| Ambiente | Ambiente de RICARDO GUILHERME DE JESUS CAEIRO DE ABREU 26103 (`94d3a652-b3a8-e2dd-9b54-025090fe6659`) |
| Solução | `DAC2627` — 3 objetos: a app, a tabela Cloud Service e o conector JSONPlaceholder |
| Ecrã inicial | `scrInicio` |
| Dados | Dataverse `mcsft_cloudservice` (375 registos) e a API REST `jsonplaceholder.typicode.com` |

## Estrutura

```
src/
  app/App.pa.yaml            Formulas (paleta nf*), StartScreen, Theme
  screens/*.pa.yaml          Um ficheiro por ecrã, em Power Fx YAML (formato oficial do Studio)
dataverse/schema.md          Tabela Cloud Service: colunas, escolhas e limites
connector/openapi.json       Definição OpenAPI do conector personalizado (GET /users, GET /posts)
data/
  cloud_service_375.csv      Conteúdo atual da tabela (20 originais + 355 importados a 7/11/2026)
  CloudService_levantamento_servicos.xlsx   Levantamento com categorias, notas de estado e fontes
tools/
  gen.py, bundle.py          Gerador usado para construir os ecrãs em YAML (colagem no Studio)
solution/                    Solução exportada, descompactada (customizations.xml, solution.xml, ...)
msapp/                       Pacote .msapp descompactado (Src/, Controls/, References/)
_export/DAC2627_1_0_0_0.zip  O ficheiro original da exportação
```

`src/` é a vista para ler e analisar. `solution/` e `msapp/` são a exportação em bruto, para referência.

## Ecrãs

| Ficha | Ecrã | Função |
|---|---|---|
| — | `scrInicio` | Galeria de fichas (Hello Cloud, Serviços Cloud, Consulta de API, Próximo laboratório) |
| 01 | `scrL1BoasVindas` → `scrL1Pedido` → `scrL1Saudacao` | Três ecrãs, navegação e variável global com o nome |
| 02 | `scrL2Servicos` | CRUD sobre a tabela Cloud Service num só ecrã: lista filtrável, formulário, validação, diálogo de remoção e faixa de mensagens |
| 03 | `scrL3Lista` → `scrL3Detalhe` → `scrL3Publicacao` | Utilizadores e publicações da API JSONPlaceholder, com filtro por utilizador e tratamento de erros |

## Como reconstruir

1. Importar `_export/DAC2627_1_0_0_0.zip` noutro ambiente (Soluções › Importar) e voltar a ligar o conector.
2. Para editar um ecrã fora do Studio, alterar o `.pa.yaml`, copiar o bloco `Screens:` e colar com Ctrl+V na Vista de árvore do Studio. O Studio só aceita a colagem com um Ctrl+V real do utilizador.
3. O `tools/gen.py` gera os 7 ecrãs que não são da Ficha 02 com as regras de responsividade do manual (secção A10).

## Documentação

O manual completo de construção (Manual ABC · APP DAC2627) está em Claude Docs: https://claude.ai/artifact/KBTUodvciyxM4pzJ9kdhxL
