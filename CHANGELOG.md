# Registo de alterações

Formato: [Keep a Changelog](https://keepachangelog.com/pt-PT/1.1.0/). Versões da app em `nfVersao` (`App.Formulas`).

## [1.4.0] · 19/11/2026 · publicada (exportação 1.0.0.6)

- Ficha 02 (`scrL2Servicos`): o painel de detalhe em modo de leitura passa a ser uma ficha própria (`conL2Ficha`), no lugar do formulário com os rótulos do Dataverse em inglês. Três cartões com contorno para Fornecedor (com o número de serviços desse fornecedor no inventário), Modelo de serviço e Estado, com as cores das etiquetas da lista (IaaS azul, PaaS verde, SaaS laranja; Ativo verde, Em avaliação âmbar, Descontinuado vermelho), a descrição numa caixa delimitada e «Quem gere o quê», o que fica a cargo do fornecedor e do cliente nesse modelo. O `frmL2Servico` fica só para criar e editar, com os rótulos em português. Migração `m005`, teste novo (62 no total). Afinada depois de vista no Studio: cartões empilhados quando a ficha tem menos de 720 px (no monitor vertical o rótulo «MODELO DE SERVIÇO» partia-se), caixas com cantos redondos dentro de contentores, e cartões com folga e sem esticar na vertical, porque esticados o contorno de baixo ficava cortado no ecrã inteiro. Exportação 1.0.0.5 sincronizada, `dac deriva` a zero; o Studio apagou o `FillPortions = 1` do `conL2Ficha`, que passa a `yamlio.OMISSAO`. Verificador: 219 avisos, os 13 novos todos etiquetas decorativas da ficha.
- Depois da revisão do Sourcery no PR #7: o `AccessibleLabel` e a `Tooltip` dos cinco campos do formulário passam a português (o leitor de ecrã dizia o nome do Dataverse em inglês), e um serviço sem modelo ou sem estado mostra o cartão neutro com um travessão, em vez de cair na última cor do `Switch` e parecer SaaS ou descontinuado. A m001 deixa de repor `Parent.DisplayName` nesses campos. Teste novo que reconstrói o ecrã de antes da m005 e confirma que a migração dá o ecrã atual (63 no total). Publicada a 19/11 (versão 43 da app) e exportada na 1.0.0.6, igual ao repositório sem nenhuma diferença. Verificador: 219 avisos, todos de decorativos.

## [Por publicar] · repositório

- Exportação 1.0.0.4 (v1.3.0 publicada a 19/11/2026) sincronizada, `dac deriva` a zero. Verificador: 206 avisos, todos de decorativos (138 etiquetas, 48 etiquetas geradas dos cartões de formulário, 8 retângulos, 5 ícones, as 5 pílulas e 8 `AccessibleLabel` em retângulos). O Studio apagou `TabIndex 0` e `FontWeight.Semibold` nos botões e guardou a `App.Formulas` com a linha em branco final (bloco `|+`): os dois botões passam a `yamlio.OMISSAO`, o `yamlio` escreve `|+` byte a byte, as migrações m001 e m002 não reescrevem a fórmula só por essa linha, e o `colar` deixa de acrescentar a linha em branco aos `App.Formulas.*.txt`.
- Correção de 19/11/2026: o `conConteudoL4b` (ecrã `scrL4Complemento`) tinha `LayoutOverflow`, uma propriedade que não existe, e o Studio recusou a colagem com `PA2108`. O nome certo é `LayoutOverflowY`; a `m004` passa a escrevê-lo e apaga o errado. Nova regra `DAC405` (erro): compara cada propriedade com as que o Studio já exportou para esse tipo de controlo (`projeto.propriedades_exportadas`, a partir de `msapp/Controls`), para o lint apanhar estes nomes antes da colagem. Manual F8 e Aula 4 corrigidos. 2 testes novos (61 no total).
- `dac colar` gera `build/colar/ORDEM.md`, o guia de colagem passo a passo: fontes de dados exigidas, `App.Formulas` na barra de fórmulas, ecrãs pela ordem certa, confirmação e exportação. A ordem é calculada a partir do código (`tools/dac/ordem.py`): um ecrã que recebe variáveis por `Navigate` entra depois de um dos ecrãs que lhas envia. `TODOS_OS_ECRAS.yaml` segue a mesma ordem.
- `dac.yaml › fontes`: as quatro fontes de dados da app, com a armadilha de cada uma (duas tabelas "Cloud Service" no ambiente).
- A mensagem do `colar` deixa de sugerir renomear o ecrã antigo: renomear muda as fórmulas dos outros ecrãs para o nome novo.
- `docs/alm.md`: as seis regras de colagem aprendidas a 10/11/2026.
- `.gitattributes`: `msapp/`, `solution/`, `_export/` e os documentos gerados marcados como gerados, para os PRs mostrarem só o código escrito à mão.
- 9 testes novos (42 no total).
- `yamlio.ler_tolerante`: lê `.pa.yaml` com um tabulador dentro de um valor (`Text: ="Voltar<TAB>"`), que o Studio exporta sem aspas e o PyYAML recusa. Visto na DACLearn a 18/11/2026. O `validar` avisa com a linha, o `lint`, o `pt`, o `deriva` e o `colar` leem na mesma (o `colar` avisa que o bloco leva um espaço no lugar do tabulador), e o `formatar` recusa reescrever o ficheiro, para o tabulador não virar espaço em silêncio. As migrações continuam com a leitura estrita. Depois da revisão do Sourcery no PR #5: as linhas com tabulador são devolvidas mesmo quando o PyYAML lê o ficheiro sozinho (tabulador entre aspas), um tabulador na indentação continua a ser erro, o `formatar` devolve 1 quando salta ficheiros, o `deriva` distingue tabulador de espaço, o `pt` avisa quando mostra um espaço no lugar do tabulador, e o `App.pa.yaml` também é lido assim no `colar` e no `paleta`.
- 8 testes novos (59 no total, com os da v1.3.0).

## [1.3.0] · 2026-11-17 · Ponto 8 com apresentação e tabela num botão

### App (migração `tools/migracoes/m004_v1_3_ponto8.py`, por colar)
- 18/11, à tarde: o ponto 8 é reescrito em parágrafos desenvolvidos, com a estrutura do texto de apoio do Qwen: em cada serviço, o modelo de serviço como subtítulo, a fundamentação arquitetural, um aspeto técnico aprofundado (limiar de vista e delegação, ciclo de vida, segurança e ambientes, computação e lógica no servidor), os fatores com título a negrito e uma síntese. No ecrã entram quatro etiquetas por serviço (`Modelo`, `AprofTit`, `Aprof`, `Sintese`), e os parágrafos separam-se com uma linha em branco. A regra «uma frase por parágrafo» estava errada e saiu do conteúdo, do gerador e das notas de escrita.
- 18/11: o ponto 8 ganha a perspetiva cloud. Cada serviço diz o modelo de serviço (SharePoint SaaS, Dataverse plataforma gerida, Azure SQL PaaS com vCores, DTU e conjuntos elásticos). Fatores novos: segurança por coluna e ALM com soluções no Dataverse, o limite de 500 a 10 000 registos sem delegação, o custo por GB do Dataverse. A tabela passa a nove linhas: os sete critérios do enunciado e «Modelo de serviço cloud» e «Custo e licenciamento». A introdução da tabela (`tab_intro`) passa para o `.yaml`.
- Fonte desta revisão: um texto de apoio gerado por outro modelo (Qwen), verificado afirmação a afirmação. Ficou de fora o que as fontes da Microsoft não confirmam (a «farm partilhada por milhares de organizações») ou desmentem (o limite de 2000 registos, que hoje vai até 10 000, e ambientes separados como obrigatórios, que são recomendados).
- **Complemento da Ficha 04** (`scrL4Complemento`): duas vistas, por `locL4bVista`. O texto apresenta SharePoint, Dataverse e SQL, cada um com o que é, a favor e contra. No fim, «Ver a tabela comparativa» mostra os sete critérios do enunciado (Estrutura, Relações, Desenvolvimento Power Apps, Interface pronta, Lógica, Gestão, Caso de uso sugerido) e a conclusão.
- **Sem alturas fixas**: etiquetas com `AutoHeight` num contentor que desloca, e cada linha da tabela com a altura da etiqueta mais alta. A galeria anterior, com `TemplateSize` fixo, cortava o texto no monitor vertical.
- **Ecrã inicial**: o quinto cartão passa a «Origens de dados». «SharePoint, Dataverse e SQL» não cabia numa linha e aparecia cortado.
- `nfVersao` passa a "1.3.0". A `m002` deixa de repor o cartão e a versão antigos.

### Repositório
- 18/11, à tarde: o gerador do `.docx` deixa de partir os textos em frases. Cada entrada é um parágrafo, os fatores têm o título a negrito, as questões têm título, a pergunta em itálico e a resposta fundamentada. Os capítulos dos serviços passam a ter cinco secções (fundamentação, aspeto técnico, fatores positivos, fatores menos positivos, síntese). 13 páginas.
- 18/11: o `.docx` ganha o capítulo V, «Questões de análise» (`documento › questoes`, com fontes por questão). 18 fontes, e um teste novo garante que cada fonte listada é citada e cada citação existe. 59 testes.
- `conteudo/ponto8.yaml`: fonte única do ecrã e do documento para o docente, com as fontes Microsoft de cada afirmação.
- `python -m tools.ponto8` gera o `.docx` (RETA ESTGL 2022, APA 7.ª) a partir do mesmo ficheiro.
- `yamlio.OMISSAO`: `Visible = true` e, nos botões, `BorderThickness = 2` também são valores por omissão (nenhum sobrevive na exportação 1.0.0.3).
- `cores.PARES`: três pares novos do ponto 8, todos AA.
- 51 testes (`test_migracao_m004_idempotente`, `test_ponto8_conteudo_e_ecra_coerentes`).

### Ambiente
- A tabela `mcsft_cloudservice1` fica: tem 21 registos e pertence à solução DACCCMB2426Final (decisão do utilizador, 17/11).

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
