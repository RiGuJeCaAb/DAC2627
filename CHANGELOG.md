# Registo de alterações

Formato: [Keep a Changelog](https://keepachangelog.com/pt-PT/1.1.0/). Versões da app em `nfVersao` (`App.Formulas`).

## [Por publicar] · repositório

- `dac colar` gera `build/colar/ORDEM.md`, o guia de colagem passo a passo: fontes de dados exigidas, `App.Formulas` na barra de fórmulas, ecrãs pela ordem certa, confirmação e exportação. A ordem é calculada a partir do código (`tools/dac/ordem.py`): um ecrã que recebe variáveis por `Navigate` entra depois de um dos ecrãs que lhas envia. `TODOS_OS_ECRAS.yaml` segue a mesma ordem.
- `dac.yaml › fontes`: as quatro fontes de dados da app, com a armadilha de cada uma (duas tabelas "Cloud Service" no ambiente).
- A mensagem do `colar` deixa de sugerir renomear o ecrã antigo: renomear muda as fórmulas dos outros ecrãs para o nome novo.
- `docs/alm.md`: as seis regras de colagem aprendidas a 10/11/2026.
- `.gitattributes`: `msapp/`, `solution/`, `_export/` e os documentos gerados marcados como gerados, para os PRs mostrarem só o código escrito à mão.
- 9 testes novos (42 no total).

## [1.2.0] · 2026-11-16, publicada a 2026-11-17 · Ficha 04 e complemento

### Publicação e prova (17/11/2026)
- A v1.2.0 foi guardada no Studio a 16/11 mas não publicada. A exportação 1.0.0.2 saiu igual à 1.0.0.1 porque a exportação da solução leva a versão **publicada**. Publicada a 17/11 às 09:32. A exportação 1.0.0.3 é a primeira com os 10 ecrãs e `nfVersao = "1.2.0"`. `dac deriva`: `src/` igual à exportação.
- `docs/alm.md`: publicar é obrigatório antes de exportar, o que o Studio muda ao guardar e os avisos esperados do Verificador.

### Repositório (17/11/2026)
- **O Studio apaga os valores por omissão ao guardar** (116 linhas na 1.0.0.3: `TabIndex -1`, `AccessibleLabel ""`, `DropShadow.Light`...). Depois de sincronizar, o lint passou de 0 para 109 avisos e as migrações deixaram de ser idempotentes. Agora:
  - `yamlio.OMISSAO`: `definir()` não escreve esses valores, como o Studio.
  - DAC301, DAC302 e DAC503 leem uma propriedade ausente como o valor por omissão. DAC503 passa a «sombra dentro de sombra». Regra nova DAC504: valor por omissão escrito no código.
  - `m001` aceita a `App` sem `StartScreen` e conhece o cartão `conL4bTabela`.
- **`dac colar` compara as fontes com a última exportação** (`ordem.verificar_fontes`): uma fonte usada no código que falta na app, ou que aponta para outra tabela (`conjunto` em `dac.yaml › fontes`, por causa da duplicada `mcsft_cloudservice1`). `--estrito` falha. O `ORDEM.md` passa a dizer porque é obrigatório publicar e que avisos do Verificador são esperados.
- 49 testes (3 de fontes, 4 de lint, `test_migracao_m003_idempotente`).

### App (migração `tools/migracoes/m003_v1_2_studio.py`, por colar)
- `FocusedBorderThickness = 2` nas 42 etiquetas dos cartões dos formulários e no `lblL4PedCliente`: os 43 avisos «foco invisível» do Verificador.
- `conEcraL2` com `DropShadow.None`: era o único contentor de ecrã com a sombra por omissão.
- `lblInFicha` com a largura do cartão: «Ficha 04 · Complemento» partia em duas linhas e ficava cortada.
- O Verificador fica com 145 avisos, todos esperados: 134 «Tabulação em falta» em controlos decorativos com `TabIndex = -1` e 11 `AccessibleLabel` em retângulos e num ícone decorativos (ver `docs/alm.md`).

### App (migração `tools/migracoes/m002_v1_2_ficha04.py`)
- **Ficha 04** (`scrL4Pedidos`): clientes e pedidos em duas tabelas Dataverse (`dac_cliente`, `dac_pedido`), relação 1:N com Restringir, vistas «Pedidos Pendentes» e «Pedidos Concluídos» no `Filter`, confirmação e faixa de mensagem como na Ficha 02.
- **Complemento da Ficha 04** (`scrL4Complemento`, novo): ponto 8 do Lab 4, comparação entre SharePoint, Dataverse e SQL em sete critérios. Abre pelo quinto cartão do ecrã inicial, «Ficha 04 · Complemento».
- **Ecrã inicial**: quinto cartão e ramos 4 e 5 do `Switch` em `galInFichas.OnSelect`.
- **Nomes** (DAC104): os nove campos `DataCardValueN` da Ficha 04 passam a `txtL4CliNome`, `txtL4CliNIF`, `txtL4CliEmail`, `txtL4CliTelefone`, `cmbL4PedCliente`, `dteL4PedData`, `cmbL4PedEstado`, `txtL4PedValor` e `txtL4PedDescricao`.
- **Acessibilidade** (DAC301): `AccessibleLabel = Parent.DisplayName` nos campos da Ficha 04 e rótulo no ícone da faixa.
- **Cores** (DAC201): o selo do estado do pedido passa a `nfAmbar`/`nfAmbarFundo`.
- **Letra** (DAC501): tamanhos 10 e 17 passam a 11 e 18.
- **Separador Todos**: mostra só os pedidos ativos, como a contagem do separador.
- **Formulários no telemóvel**: os cartões da Ficha 04 e do `frmL2Servico` têm a largura por fórmula. No telemóvel ficam um por linha. A Ficha 02 decide pela largura do formulário (560 px), porque no tablet o painel ocupa só metade do ecrã.
- `nfVersao` passa a "1.2.0". A `m001` deixa de repor uma versão mais antiga.

### Repositório
- `dac.yaml`: 10 ecrãs, fontes Dataverse `Clientes` e `Pedidos`, exceção DAC302 para `btnL4PedEstado` (5 pílulas no total).
- Teste `test_migracao_m002_idempotente` (33 testes).
- `dataverse/schema.md` com as tabelas Cliente e Pedido.

### Dataverse
- Pesquisa rápida da tabela Cliente («Localizar por») com Nome, NIF e Email, configurada no designer da vista, porque a Web API recusa a alteração.

### Nota
- A v1.1.0 nunca chegou a ser colada no Studio. A exportação 1.0.0.1, de 16/11/2026, ainda tinha o estado anterior em quatro ecrãs. A v1.2.0 é colada inteira, com os 10 ecrãs e a `App.Formulas`, e leva consigo as alterações da v1.1.0.

## [1.1.0] · 2026-11-09 · colada no Studio com a 1.2.0

### Repositório
- Ferramenta `tools/dac`: `validar`, `lint`, `pt`, `colar`, `inventario`, `paleta`, `deriva`, `sincronizar`, `formatar`.
- Leitura e escrita de `.pa.yaml` byte a byte iguais às do Studio, testadas nos 19 ficheiros exportados.
- Schema oficial `pa.schema` v3.0 em `schemas/`; todo o `src/` é validado contra ele.
- 32 testes pytest; CI no GitHub (`verificar.yml`) com anotações do lint e SARIF; modelos de ALM com as Power Platform Actions.
- `gen.py`/`bundle.py` passam para `tools/legacy/`: já não geravam o estado atual de `src/`, e o `pt2inv` trocava separadores dentro de textos.

### App (migração `tools/migracoes/m001_v1_1_qualidade.py`)
- **Cores**: 97 cores literais trocadas por tokens `nf*`, incluindo as cores por omissão do formulário (`RGBA(0, 18, 107, 1)`, `Color.Red`...). A paleta passa de 12 para 22 tokens, um por linha e agrupados. Todos os 16 pares texto/fundo usados passam AA (WCAG 2.2).
- **Acessibilidade**: resolvidos 148 dos 152 avisos de acessibilidade do Verificador (79 TabIndex, 51 FocusedBorder, 22 AccessibleLabel). Os 4 restantes são os botões "pílula", que ficam com `TabIndex = -1` de propósito e estão registados como exceção com motivo em `dac.yaml`. O Studio vai continuar a mostrá-los.
- **Contagens**: `lblL3Contagem` e `lblL3TituloPubs` contam sobre as coleções em vez de `Galeria.AllItems` (os 2 avisos `app-CountRowsGalleryAllItems`).
- **Sombras**: os contentores interiores da Ficha 02 (`conCabL2`, `conConteudoL2`, `conL2Corpo`, `conL2ErroGeral`) herdavam `DropShadow.Light`; passam a `None`, como o resto da app. Os cartões ficam com `Light` explícito.
- **Nomes**: `DataCardValue5` passa a `cmbL2Estado`.
- **Pormenores**: o resumo das publicações só leva "…" quando o texto é cortado; versão no rodapé do ecrã inicial; o aviso da Ficha 01 passa a âmbar (`nfAmbar`/`nfAmbarFundo`), a cor de aviso da app; `StartScreen` sem espaços a mais.

### Corrigido depois (17/11/2026)
- A conta dos avisos estava errada. A v1.1.0 só chegou ao Studio com a v1.2.0, e a exportação 1.0.0.3 mostrou que o Verificador marca qualquer controlo com `TabIndex = -1` fora das galerias. Ficaram 134 avisos de tabulação, não 4, e ficam de propósito.
- O `DropShadow.Light` explícito dos cartões não sobrevive: é o valor por omissão e o Studio apaga-o.

## [1.0.0] · 2026-11-08
- Exportação inicial da solução DAC2627 (app, tabela Cloud Service e conector JSONPlaceholderDAC), com as correções de responsividade.
