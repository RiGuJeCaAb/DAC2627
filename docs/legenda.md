# Anexo · Legenda dos elementos da APP DAC2627

Gerado por `python -m tools.dac legenda` a partir de `src/`. Não editar à mão: mudar o código e voltar a gerar.

A app tem 12 ecrãs e 587 controlos. Para cada elemento, a legenda diz o que é, onde está e em que secção do Manual ABC é construído. Os nomes seguem a convenção da A2: o prefixo diz o tipo (`lbl`, `btn`, `con`…), o código diz a ficha (`In`, `L1` a `L4`, com `L4b` para o Complemento, `L4c` para o Melhoramento e `L4d` para a Revisão) e o resto diz a função. As descrições saem das próprias fórmulas: o texto de uma etiqueta, o que um botão faz, a origem de uma galeria.

## Ecrãs

| Ecrã | Ficha | Controlos | Secção do Manual |
|---|---|---:|---|
| `scrInicio` | Início | 13 | B |
| `scrL1BoasVindas` | Ficha 01 | 9 | C2 |
| `scrL1Pedido` | Ficha 01 | 13 | C3 |
| `scrL1Saudacao` | Ficha 01 | 12 | C4 |
| `scrL2Servicos` | Ficha 02 | 91 | D |
| `scrL3Lista` | Ficha 03 | 41 | E5, E6 |
| `scrL3Detalhe` | Ficha 03 | 34 | E7 |
| `scrL3Publicacao` | Ficha 03 | 16 | E7 |
| `scrL4Pedidos` | Ficha 04 (três modos) | 183 | F2 a F7 |
| `scrL4Complemento` | Ficha 04 · Complemento | 91 | F8 |
| `scrL4Entrar` | Ficha 04 · Revisão (entrada) | 34 | F11.5 |
| `scrL4Conta` | Ficha 04 · Revisão (conta) | 50 | F11.5 |

## scrInicio

| Controlo | Tipo | Dentro de | O que é | Manual |
|---|---|---|---|---|
| `conEcraIn` | Contentor | ecrã | Contentor vertical, raiz do ecrã | B |
| `conCabIn` | Contentor | `conEcraIn` | Contentor horizontal | B |
| `lblCabIn` | Etiqueta | `conCabIn` | Texto fixo «APP DAC2627» | B |
| `conConteudoIn` | Contentor | `conEcraIn` | Contentor vertical | B |
| `lblInTitulo` | Etiqueta | `conConteudoIn` | Texto fixo «Laboratórios de DAC 2026/27» | B |
| `lblInSubtitulo` | Etiqueta | `conConteudoIn` | Texto fixo «Escolha a ficha que quer abrir.» | B |
| `galInFichas` | Galeria | `conConteudoIn` | Galeria de Pedidos, Clientes, Utilizadores, uma tabela escrita na fórmula | B |
| `conInCartao` | Contentor | `galInFichas` | Contentor vertical, caixa com contorno | B |
| `lblInFicha` | Etiqueta | `galInFichas` | Mostra ThisItem.Ficha | B |
| `lblInFichaTitulo` | Etiqueta | `galInFichas` | Mostra ThisItem.Titulo | B |
| `lblInFichaDescricao` | Etiqueta | `galInFichas` | Mostra ThisItem.Descricao | B |
| `btnInAbrir` | Botão | `galInFichas` | Botão If(ThisItem.Disponivel; "Abrir"; "Em breve"): passa o toque à linha da galeria | B |
| `lblInRodape` | Etiqueta | `conConteudoIn` | Mostra "Desenvolvimento de Aplicações na Cloud · CTeSP Computação Cloud · v" & nfVersao | B |

## scrL1BoasVindas

| Controlo | Tipo | Dentro de | O que é | Manual |
|---|---|---|---|---|
| `conEcraL1a` | Contentor | ecrã | Contentor vertical, raiz do ecrã | C2 |
| `conCabL1a` | Contentor | `conEcraL1a` | Contentor horizontal | C2 |
| `icoInicioL1a` | Ícone | `conCabL1a` | Ícone Home («Voltar ao início»): abre scrInicio | C2 |
| `lblCabL1a` | Etiqueta | `conCabL1a` | Texto fixo «Ficha 01 · Hello Cloud» | C2 |
| `conConteudoL1a` | Contentor | `conEcraL1a` | Contentor vertical | C2 |
| `conL1aCartao` | Contentor | `conConteudoL1a` | Contentor vertical, caixa com contorno | C2 |
| `lblL1Titulo` | Etiqueta | `conL1aCartao` | Texto fixo «Bem-vindo à Cloud» | C2 |
| `lblL1Subtitulo` | Etiqueta | `conL1aCartao` | Texto fixo «A sua primeira aplicação Power Apps, criada, executada e partilhada a…» | C2 |
| `btnL1Comecar` | Botão | `conL1aCartao` | Botão «Começar»: abre scrL1Pedido | C2 |

## scrL1Pedido

| Controlo | Tipo | Dentro de | O que é | Manual |
|---|---|---|---|---|
| `conEcraL1b` | Contentor | ecrã | Contentor vertical, raiz do ecrã | C3 |
| `conCabL1b` | Contentor | `conEcraL1b` | Contentor horizontal | C3 |
| `icoInicioL1b` | Ícone | `conCabL1b` | Ícone Home («Voltar ao início»): abre scrInicio | C3 |
| `icoL1Voltar` | Ícone | `conCabL1b` | Ícone ChevronLeft («Voltar»): Back() | C3 |
| `lblCabL1b` | Etiqueta | `conCabL1b` | Texto fixo «Ficha 01 · Passo 1 de 2» | C3 |
| `conConteudoL1b` | Contentor | `conEcraL1b` | Contentor vertical | C3 |
| `conL1bCartao` | Contentor | `conConteudoL1b` | Contentor vertical, caixa com contorno | C3 |
| `lblL1Pergunta` | Etiqueta | `conL1bCartao` | Texto fixo «Como se chama?» | C3 |
| `txtL1Nome` | Caixa de texto | `conL1bCartao` | Entrada de texto: O seu nome | C3 |
| `conL1Aviso` | Contentor | `conL1bCartao` | Contentor horizontal | C3 |
| `lblL1Aviso` | Etiqueta | `conL1Aviso` | Texto fixo «Introduza o seu nome.» | C3 |
| `btnL1Saudar` | Botão | `conL1bCartao` | Botão «Saudar»: abre scrL1Saudacao; define gblL1Nome; muda locAviso | C3 |
| `lblL1Anuncio` | Etiqueta | ecrã | Mostra If(conL1Aviso.Visible; lblL1Aviso.Text; "") | C3 |

## scrL1Saudacao

| Controlo | Tipo | Dentro de | O que é | Manual |
|---|---|---|---|---|
| `conEcraL1c` | Contentor | ecrã | Contentor vertical, raiz do ecrã | C4 |
| `conCabL1c` | Contentor | `conEcraL1c` | Contentor horizontal | C4 |
| `icoInicioL1c` | Ícone | `conCabL1c` | Ícone Home («Voltar ao início»): abre scrInicio | C4 |
| `lblCabL1c` | Etiqueta | `conCabL1c` | Texto fixo «Ficha 01 · Passo 2 de 2» | C4 |
| `conConteudoL1c` | Contentor | `conEcraL1c` | Contentor vertical | C4 |
| `conL1cCartao` | Contentor | `conConteudoL1c` | Contentor vertical, caixa com contorno | C4 |
| `icoL1Sucesso` | Ícone | `conL1cCartao` | Ícone Check («Sucesso»): decorativo | C4 |
| `lblL1BoasVindas` | Etiqueta | `conL1cCartao` | Texto fixo «Bem-vindo à Cloud» | C4 |
| `lblL1Saudacao` | Etiqueta | `conL1cCartao` | Mostra If(IsBlank(gblL1Nome); "Introduza o seu nome."; "Olá, " & gblL1Nome & "!") | C4 |
| `conL1Botoes` | Contentor | `conL1cCartao` | Contentor horizontal | C4 |
| `btnL1Alterar` | Botão | `conL1Botoes` | Botão «Alterar nome»: Back() | C4 |
| `btnL1Terminar` | Botão | `conL1Botoes` | Botão «Terminar»: abre scrL1BoasVindas; define gblL1Nome | C4 |

## scrL2Servicos

| Controlo | Tipo | Dentro de | O que é | Manual |
|---|---|---|---|---|
| `conEcraL2` | Contentor | ecrã | Contentor vertical, raiz do ecrã | D |
| `conCabL2` | Contentor | `conEcraL2` | Contentor horizontal | D |
| `icoInicioL2` | Ícone | `conCabL2` | Ícone Home («Voltar ao início»): abre scrInicio | D |
| `lblCabL2` | Etiqueta | `conCabL2` | Texto fixo «Ficha 02 · Serviços Cloud» | D |
| `conConteudoL2` | Contentor | `conEcraL2` | Contentor vertical | D |
| `conL2Barra` | Contentor | `conConteudoL2` | Contentor horizontal | D |
| `txtL2Pesquisa` | Caixa de texto | `conL2Barra` | Entrada de texto: Pesquisar serviços pelo início do nome | D |
| `drpL2Modelo` | Lista pendente | `conL2Barra` | Escolha de ["Todos"; "IaaS"; "PaaS"; "SaaS"] | D |
| `lblL2Contagem` | Etiqueta | `conL2Barra` | Mostra With({n: If(drpL2Modelo.Selected.Value = "Todos"; CountRows(Filter('Cloud Servi… | D |
| `btnL2Novo` | Botão | `conL2Barra` | Botão «+ Novo serviço»: abre o formulário a criar; muda locTentou | D |
| `conL2Corpo` | Contentor | `conConteudoL2` | Contentor horizontal | D |
| `conL2Lista` | Contentor | `conL2Corpo` | Contentor vertical, caixa com contorno | D |
| `lblL2Vazio` | Etiqueta | `conL2Lista` | Texto fixo «Nenhum serviço encontrado com estes critérios.» | D |
| `galL2Servicos` | Galeria | `conL2Lista` | Galeria de 'Cloud Service' | D |
| `recL2ItemCartao` | Retângulo | `galL2Servicos` | Fundo de cartão | D |
| `recL2ItemBarra` | Retângulo | `galL2Servicos` | Barra de cor à esquerda da linha | D |
| `lblL2ItemTitulo` | Etiqueta | `galL2Servicos` | Mostra ThisItem.'Service Title' | D |
| `lblL2ItemFornecedor` | Etiqueta | `galL2Servicos` | Mostra ThisItem.Provider | D |
| `btnL2ItemModelo` | Botão | `galL2Servicos` | Botão Text(ThisItem.'Service Model'): passa o toque à linha da galeria | D |
| `conL2Painel` | Contentor | `conL2Corpo` | Contentor vertical, caixa com contorno | D |
| `conL2PainelTopo` | Contentor | `conL2Painel` | Contentor horizontal | D |
| `btnL2VoltarLista` | Botão | `conL2PainelTopo` | Botão «‹ Lista»: muda locSel | D |
| `lblL2PainelTitulo` | Etiqueta | `conL2PainelTopo` | Mostra If(frmL2Servico.Mode = FormMode.New; "Novo serviço"; frmL2Servico.Mode = FormMo… | D |
| `conL2ErroGeral` | Contentor | `conL2Painel` | Contentor horizontal | D |
| `lblL2ErroGeral` | Etiqueta | `conL2ErroGeral` | Texto fixo «Preencha os campos obrigatórios assinalados.» | D |
| `frmL2Servico` | Formulário | `conL2Painel` | Formulário de 'Cloud Service' | D |
| `Service Title_DataCard1` | Cartão de dados | `frmL2Servico` | Cartão do formulário | D |
| `DataCardKey2` | Etiqueta | `Service Title_DataCard1` | Texto fixo «Nome do serviço» | D |
| `txtL2Titulo` | Caixa de texto | `Service Title_DataCard1` | Entrada de texto: Nome do serviço | D |
| `ErrorMessage2` | Etiqueta | `Service Title_DataCard1` | Texto fixo «Indique o nome do serviço.» | D |
| `StarVisible2` | Etiqueta | `Service Title_DataCard1` | Texto fixo «*» | D |
| `Status_DataCard1` | Cartão de dados | `frmL2Servico` | Cartão do formulário | D |
| `DataCardKey5` | Etiqueta | `Status_DataCard1` | Texto fixo «Estado» | D |
| `cmbL2Estado` | Caixa de combinação | `Status_DataCard1` | Escolha de Choices('Status (Cloud Service)') | D |
| `ErrorMessage5` | Etiqueta | `Status_DataCard1` | Mostra Parent.Error | D |
| `StarVisible5` | Etiqueta | `Status_DataCard1` | Texto fixo «*» | D |
| `Provider_DataCard1` | Cartão de dados | `frmL2Servico` | Cartão do formulário | D |
| `DataCardKey1` | Etiqueta | `Provider_DataCard1` | Texto fixo «Fornecedor» | D |
| `txtL2Fornecedor` | Caixa de texto | `Provider_DataCard1` | Entrada de texto: Fornecedor | D |
| `ErrorMessage1` | Etiqueta | `Provider_DataCard1` | Texto fixo «Indique o fornecedor.» | D |
| `StarVisible1` | Etiqueta | `Provider_DataCard1` | Texto fixo «*» | D |
| `Service Model_DataCard1` | Cartão de dados | `frmL2Servico` | Cartão do formulário | D |
| `DataCardKey4` | Etiqueta | `Service Model_DataCard1` | Texto fixo «Modelo de serviço» | D |
| `cmbL2Modelo` | Caixa de combinação | `Service Model_DataCard1` | Escolha de Choices('Service Model (Cloud Service)') | D |
| `ErrorMessage4` | Etiqueta | `Service Model_DataCard1` | Texto fixo «Escolha o modelo de serviço.» | D |
| `StarVisible4` | Etiqueta | `Service Model_DataCard1` | Texto fixo «*» | D |
| `Service Description_DataCard1` | Cartão de dados | `frmL2Servico` | Cartão do formulário | D |
| `DataCardKey3` | Etiqueta | `Service Description_DataCard1` | Texto fixo «Descrição» | D |
| `txtL2Descricao` | Caixa de texto | `Service Description_DataCard1` | Entrada de texto: Descrição | D |
| `ErrorMessage3` | Etiqueta | `Service Description_DataCard1` | Mostra Parent.Error | D |
| `StarVisible3` | Etiqueta | `Service Description_DataCard1` | Texto fixo «*» | D |
| `conL2Ficha` | Contentor | `conL2Painel` | Contentor vertical, desloca | D |
| `conL2FichaFactos` | Contentor | `conL2Ficha` | Contentor horizontal | D |
| `conL2FichaFornecedor` | Contentor | `conL2FichaFactos` | Contentor vertical, caixa com contorno | D |
| `lblL2FichaFornecedorRotulo` | Etiqueta | `conL2FichaFornecedor` | Texto fixo «FORNECEDOR» | D |
| `lblL2FichaFornecedor` | Etiqueta | `conL2FichaFornecedor` | Mostra locSel.Provider | D |
| `lblL2FichaFornecedorNota` | Etiqueta | `conL2FichaFornecedor` | Mostra With({n: CountRows(Filter('Cloud Service'; Provider = locSel.Provider))}; n & I… | D |
| `conL2FichaModelo` | Contentor | `conL2FichaFactos` | Contentor vertical, caixa com contorno | D |
| `lblL2FichaModeloRotulo` | Etiqueta | `conL2FichaModelo` | Texto fixo «MODELO DE SERVIÇO» | D |
| `lblL2FichaModelo` | Etiqueta | `conL2FichaModelo` | Mostra If(IsBlank(locSel.'Service Model'); "—"; Text(locSel.'Service Model')) | D |
| `lblL2FichaModeloNota` | Etiqueta | `conL2FichaModelo` | Mostra Switch(Text(locSel.'Service Model'); "IaaS"; "Infraestrutura como serviço"; "Pa… | D |
| `conL2FichaEstado` | Contentor | `conL2FichaFactos` | Contentor vertical, caixa com contorno | D |
| `lblL2FichaEstadoRotulo` | Etiqueta | `conL2FichaEstado` | Texto fixo «ESTADO» | D |
| `lblL2FichaEstado` | Etiqueta | `conL2FichaEstado` | Mostra If(IsBlank(locSel.Status); "—"; Text(locSel.Status)) | D |
| `lblL2FichaEstadoNota` | Etiqueta | `conL2FichaEstado` | Mostra Switch(Text(locSel.Status); "Ativo"; "Em uso no inventário"; "Em avaliação"; "E… | D |
| `lblL2FichaDescricaoTit` | Etiqueta | `conL2Ficha` | Texto fixo «Descrição» | D |
| `conL2FichaDescricao` | Contentor | `conL2Ficha` | Contentor vertical, caixa com contorno | D |
| `lblL2FichaDescricao` | Etiqueta | `conL2FichaDescricao` | Mostra If(IsBlank(Trim(locSel.'Service Description')); "Sem descrição."; locSel.'Servi… | D |
| `lblL2FichaResponsabilidadeTit` | Etiqueta | `conL2Ficha` | Texto fixo «Quem gere o quê» | D |
| `conL2FichaResponsabilidade` | Contentor | `conL2Ficha` | Contentor vertical | D |
| `lblL2FichaResponsabilidade` | Etiqueta | `conL2FichaResponsabilidade` | Mostra Switch(Text(locSel.'Service Model'); "IaaS"; "O fornecedor gere os centros de d… | D |
| `lblL2PainelVazio` | Etiqueta | `conL2Painel` | Texto fixo «Selecione um serviço na lista ou crie um novo.» | D |
| `conL2Acoes` | Contentor | `conL2Painel` | Contentor horizontal | D |
| `btnL2Remover` | Botão | `conL2Acoes` | Botão «Remover»: muda locAcao | D |
| `lblL2Espaco` | Etiqueta | `conL2Acoes` | Texto fixo «» | D |
| `btnL2Cancelar` | Botão | `conL2Acoes` | Botão «Cancelar»: muda locTentou | D |
| `btnL2Editar` | Botão | `conL2Acoes` | Botão «Editar»: abre o formulário a editar; muda locTentou | D |
| `btnL2Guardar` | Botão | `conL2Acoes` | Botão «Guardar»: muda locAcao, locTentou | D |
| `recL2Veu` | Retângulo | ecrã | Véu por trás do diálogo | D |
| `conL2Dialogo` | Contentor | ecrã | Contentor vertical, raiz do ecrã | D |
| `lblL2ConfTitulo` | Etiqueta | `conL2Dialogo` | Mostra Switch(locAcao; "criar"; "Criar serviço?"; "editar"; "Guardar alterações?"; "Re… | D |
| `lblL2ConfTexto` | Etiqueta | `conL2Dialogo` | Mostra Switch(locAcao; "criar"; "O serviço " & Trim(txtL2Titulo.Text) & " vai ser acre… | D |
| `conL2ConfBotoes` | Contentor | `conL2Dialogo` | Contentor horizontal | D |
| `btnL2ConfCancelar` | Botão | `conL2ConfBotoes` | Botão «Cancelar»: muda locAcao | D |
| `btnL2ConfOk` | Botão | `conL2ConfBotoes` | Botão Switch(locAcao; "criar"; "Criar"; "editar"; "Guar…: grava o formulário; apaga um registo; muda locMsg, locSel, locUltimaAcao | D |
| `conL2Mensagem` | Contentor | ecrã | Contentor horizontal, raiz do ecrã | D |
| `icoL2MsgIcone` | Ícone | `conL2Mensagem` | Ícone If(locMsgTipo = "erro"; Warning; Check): decorativo | D |
| `lblL2Mensagem` | Etiqueta | `conL2Mensagem` | Mostra locMsg | D |
| `icoL2FecharMsg` | Ícone | `conL2Mensagem` | Ícone Cancel («Fechar mensagem»): muda locMsg | D |
| `tmrL2Mensagem` | Temporizador | ecrã | Temporizador de 3500 ms: muda locMsg | D |
| `lblL2Anuncio` | Etiqueta | ecrã | Mostra If(!IsBlank(locMsg); locMsg; conL2ErroGeral.Visible; lblL2ErroGeral.Text; lblL2… | D |

## scrL3Lista

| Controlo | Tipo | Dentro de | O que é | Manual |
|---|---|---|---|---|
| `conEcraL3a` | Contentor | ecrã | Contentor vertical, raiz do ecrã | E5, E6 |
| `conCabL3a` | Contentor | `conEcraL3a` | Contentor horizontal | E5, E6 |
| `icoInicioL3a` | Ícone | `conCabL3a` | Ícone Home («Voltar ao início»): abre scrInicio | E5, E6 |
| `lblCabL3a` | Etiqueta | `conCabL3a` | Texto fixo «Ficha 03 · Consulta de API» | E5, E6 |
| `conConteudoL3a` | Contentor | `conEcraL3a` | Contentor vertical | E5, E6 |
| `conL3Separadores` | Contentor | `conConteudoL3a` | Contentor horizontal, caixa com contorno | E5, E6 |
| `btnL3SepUtil` | Botão | `conL3Separadores` | Botão "Utilizadores (" & CountRows(colL3Utilizadores) &…: muda locL3Vista | E5, E6 |
| `btnL3SepPub` | Botão | `conL3Separadores` | Botão "Publicações (" & CountRows(colL3Publicacoes) & "…: muda locL3Vista | E5, E6 |
| `conL3Barra` | Contentor | `conConteudoL3a` | Contentor horizontal | E5, E6 |
| `txtL3Pesquisa` | Caixa de texto | `conL3Barra` | Entrada de texto | E5, E6 |
| `drpL3Utilizador` | Lista pendente | `conL3Barra` | Escolha de Ungroup( Table( {grp: Table({id: 0; name: "Todos os utilizadores"})};… | E5, E6 |
| `lblL3Contagem` | Etiqueta | `conL3Barra` | Mostra If(locL3Vista = "publicacoes"; CountRows(Filter(colL3Publicacoes; (drpL3Utiliza… | E5, E6 |
| `btnL3Atualizar` | Botão | `conL3Barra` | Botão «Atualizar»: Select(btnL3Carregar) | E5, E6 |
| `btnL3Carregar` | Botão | `conL3Barra` | Botão «Carregar»: carrega uma coleção; muda locL3ACarregar, locL3Erro | E5, E6 |
| `chkL3SimularFalha` | Caixa de verificação | `conConteudoL3a` | Caixa de verificação «Simular falha da API (teste de erro)» | E5, E6 |
| `chkL3SimularVazio` | Caixa de verificação | `conConteudoL3a` | Caixa de verificação «Simular resposta sem dados (teste)» | E5, E6 |
| `conL3Erro` | Contentor | `conConteudoL3a` | Contentor horizontal | E5, E6 |
| `icoL3Aviso` | Ícone | `conL3Erro` | Ícone Warning («Erro»): decorativo | E5, E6 |
| `lblL3Erro` | Etiqueta | `conL3Erro` | Mostra locL3Erro | E5, E6 |
| `btnL3Repetir` | Botão | `conL3Erro` | Botão «Tentar novamente»: Select(btnL3Carregar) | E5, E6 |
| `conL3Aviso` | Contentor | `conConteudoL3a` | Contentor horizontal | E5, E6 |
| `icoL3AvisoVazio` | Ícone | `conL3Aviso` | Ícone Warning («Aviso»): decorativo | E5, E6 |
| `lblL3Vazio` | Etiqueta | `conL3Aviso` | Mostra If(locL3Vista = "publicacoes"; "Sem publicações para apresentar. Prima Atualiza… | E5, E6 |
| `btnL3AvisoAtualizar` | Botão | `conL3Aviso` | Botão «Atualizar»: Select(btnL3Carregar) | E5, E6 |
| `lblL3ACarregar` | Etiqueta | `conConteudoL3a` | Texto fixo «A carregar dados da API…» | E5, E6 |
| `lblL3SemResultados` | Etiqueta | `conConteudoL3a` | Texto fixo «Nada corresponde à pesquisa.» | E5, E6 |
| `galL3Utilizadores` | Galeria | `conConteudoL3a` | Galeria de Utilizadores, colL3Utilizadores | E5, E6 |
| `recL3ItemCartao` | Retângulo | `galL3Utilizadores` | Fundo de cartão | E5, E6 |
| `btnL3Iniciais` | Botão | `galL3Utilizadores` | Botão Upper(Left(ThisItem.name; 1)): passa o toque à linha da galeria | E5, E6 |
| `lblL3ItemNome` | Etiqueta | `galL3Utilizadores` | Mostra ThisItem.name | E5, E6 |
| `lblL3ItemEmail` | Etiqueta | `galL3Utilizadores` | Mostra ThisItem.email | E5, E6 |
| `lblL3ItemEmpresa` | Etiqueta | `galL3Utilizadores` | Mostra ThisItem.company.name | E5, E6 |
| `icoL3Abrir` | Ícone | `galL3Utilizadores` | Ícone ChevronRight: passa o toque à linha da galeria | E5, E6 |
| `galL3Publicacoes` | Galeria | `conConteudoL3a` | Galeria de colL3Publicacoes | E5, E6 |
| `recL3PubCartao` | Retângulo | `galL3Publicacoes` | Fundo de cartão | E5, E6 |
| `lblL3PubItemTitulo` | Etiqueta | `galL3Publicacoes` | Mostra ThisItem.title | E5, E6 |
| `lblL3PubItemAutor` | Etiqueta | `galL3Publicacoes` | Mostra "Publicação " & ThisItem.id & " · " & Coalesce(LookUp(colL3Utilizadores; id = T… | E5, E6 |
| `lblL3PubItemResumo` | Etiqueta | `galL3Publicacoes` | Mostra With({t: Substitute(ThisItem.body; Char(10); " ")}; If(Len(t) > 100; Left(t; 10… | E5, E6 |
| `icoL3PubAbrir` | Ícone | `galL3Publicacoes` | Ícone ChevronRight: passa o toque à linha da galeria | E5, E6 |
| `lblL3AnuncioErro` | Etiqueta | ecrã | Mostra locL3Erro | E5, E6 |
| `lblL3Anuncio` | Etiqueta | ecrã | Mostra If(lblL3ACarregar.Visible; lblL3ACarregar.Text; conL3Aviso.Visible; lblL3Vazio.… | E5, E6 |

## scrL3Detalhe

| Controlo | Tipo | Dentro de | O que é | Manual |
|---|---|---|---|---|
| `conEcraL3b` | Contentor | ecrã | Contentor vertical, raiz do ecrã | E7 |
| `conCabL3b` | Contentor | `conEcraL3b` | Contentor horizontal | E7 |
| `icoInicioL3b` | Ícone | `conCabL3b` | Ícone Home («Voltar ao início»): abre scrInicio | E7 |
| `icoL3Voltar` | Ícone | `conCabL3b` | Ícone ChevronLeft («Voltar»): Back() | E7 |
| `lblCabL3b` | Etiqueta | `conCabL3b` | Texto fixo «Ficha 03 · Detalhe» | E7 |
| `conConteudoL3b` | Contentor | `conEcraL3b` | Contentor vertical | E7 |
| `lblL3SemSel` | Etiqueta | `conConteudoL3b` | Texto fixo «Escolha um utilizador na lista.» | E7 |
| `conL3bCartao` | Contentor | `conConteudoL3b` | Contentor vertical, caixa com contorno, desloca | E7 |
| `conL3bTopo` | Contentor | `conL3bCartao` | Contentor horizontal | E7 |
| `btnL3bIniciais` | Botão | `conL3bTopo` | Botão Upper(Left(locL3Sel.name; 1)) | E7 |
| `conL3bNomes` | Contentor | `conL3bTopo` | Contentor vertical | E7 |
| `lblL3Nome` | Etiqueta | `conL3bNomes` | Mostra locL3Sel.name | E7 |
| `lblL3Utilizador` | Etiqueta | `conL3bNomes` | Mostra "@" & locL3Sel.username | E7 |
| `conL3Blocos` | Contentor | `conL3bCartao` | Contentor horizontal | E7 |
| `conL3Contacto` | Contentor | `conL3Blocos` | Contentor vertical, caixa com contorno | E7 |
| `lblL3TitContacto` | Etiqueta | `conL3Contacto` | Texto fixo «CONTACTO» | E7 |
| `lblL3Email` | Etiqueta | `conL3Contacto` | Mostra locL3Sel.email | E7 |
| `lblL3Telefone` | Etiqueta | `conL3Contacto` | Mostra Coalesce(locL3Sel.phone; "Sem telefone") | E7 |
| `lblL3Site` | Etiqueta | `conL3Contacto` | Mostra Coalesce(locL3Sel.website; "Sem site") | E7 |
| `conL3Morada` | Contentor | `conL3Blocos` | Contentor vertical, caixa com contorno | E7 |
| `lblL3TitMorada` | Etiqueta | `conL3Morada` | Texto fixo «MORADA» | E7 |
| `lblL3Rua` | Etiqueta | `conL3Morada` | Mostra locL3Sel.address.street & ", " & locL3Sel.address.suite | E7 |
| `lblL3Cidade` | Etiqueta | `conL3Morada` | Mostra locL3Sel.address.zipcode & " " & locL3Sel.address.city | E7 |
| `conL3Empresa` | Contentor | `conL3Blocos` | Contentor vertical, caixa com contorno | E7 |
| `lblL3TitEmpresa` | Etiqueta | `conL3Empresa` | Texto fixo «EMPRESA» | E7 |
| `lblL3Empresa` | Etiqueta | `conL3Empresa` | Mostra locL3Sel.company.name | E7 |
| `lblL3Lema` | Etiqueta | `conL3Empresa` | Mostra locL3Sel.company.catchPhrase | E7 |
| `conL3PubsUtil` | Contentor | `conL3bCartao` | Contentor vertical | E7 |
| `lblL3TituloPubs` | Etiqueta | `conL3PubsUtil` | Mostra "PUBLICAÇÕES (" & CountRows(Filter(colL3Publicacoes; userId = locL3Sel.id)) & "… | E7 |
| `galL3PubsUtil` | Galeria | `conL3PubsUtil` | Galeria de colL3Publicacoes | E7 |
| `lblL3PubsUtilNum` | Etiqueta | `galL3PubsUtil` | Mostra ThisItem.id | E7 |
| `lblL3PubsUtilItem` | Etiqueta | `galL3PubsUtil` | Mostra ThisItem.title | E7 |
| `icoL3PubsUtilAbrir` | Ícone | `galL3PubsUtil` | Ícone ChevronRight: passa o toque à linha da galeria | E7 |
| `recL3PubsUtilSep` | Retângulo | `galL3PubsUtil` | Linha de separação | E7 |

## scrL3Publicacao

| Controlo | Tipo | Dentro de | O que é | Manual |
|---|---|---|---|---|
| `conEcraL3c` | Contentor | ecrã | Contentor vertical, raiz do ecrã | E7 |
| `conCabL3c` | Contentor | `conEcraL3c` | Contentor horizontal | E7 |
| `icoInicioL3c` | Ícone | `conCabL3c` | Ícone Home («Voltar ao início»): abre scrInicio | E7 |
| `icoL3cVoltar` | Ícone | `conCabL3c` | Ícone ChevronLeft («Voltar»): Back() | E7 |
| `lblCabL3c` | Etiqueta | `conCabL3c` | Texto fixo «Ficha 03 · Publicação» | E7 |
| `conConteudoL3c` | Contentor | `conEcraL3c` | Contentor vertical | E7 |
| `lblL3SemPub` | Etiqueta | `conConteudoL3c` | Texto fixo «Escolha uma publicação na lista.» | E7 |
| `conL3cCartao` | Contentor | `conConteudoL3c` | Contentor vertical, caixa com contorno | E7 |
| `lblL3PubNumero` | Etiqueta | `conL3cCartao` | Mostra "PUBLICAÇÃO N.º " & locL3Pub.id | E7 |
| `lblL3PubTitulo` | Etiqueta | `conL3cCartao` | Mostra locL3Pub.title | E7 |
| `conL3PubAutor` | Contentor | `conL3cCartao` | Contentor horizontal, caixa com contorno | E7 |
| `btnL3PubIniciais` | Botão | `conL3PubAutor` | Botão Upper(Left(LookUp(colL3Utilizadores; id = locL3Pu… | E7 |
| `lblL3PubAutor` | Etiqueta | `conL3PubAutor` | Mostra With({autor: LookUp(colL3Utilizadores; id = locL3Pub.userId)}; If(IsBlank(autor… | E7 |
| `btnL3VerAutor` | Botão | `conL3PubAutor` | Botão «Ver autor»: abre scrL3Detalhe | E7 |
| `lblL3PubTexto` | Etiqueta | `conL3cCartao` | Mostra locL3Pub.body | E7 |
| `lblL3PubNota` | Etiqueta | `conL3cCartao` | Texto fixo «Dados fictícios devolvidos pela API de demonstração JSONPlaceholder.» | E7 |

## scrL4Pedidos

| Controlo | Tipo | Dentro de | O que é | Manual |
|---|---|---|---|---|
| `conEcraL4` | Contentor | ecrã | Contentor vertical, raiz do ecrã | F2 a F7 |
| `conCabL4` | Contentor | `conEcraL4` | Contentor horizontal | F2 a F7 |
| `icoInicioL4` | Ícone | `conCabL4` | Ícone Home («Voltar ao início»): abre scrInicio | F2 a F7 |
| `lblCabL4` | Etiqueta | `conCabL4` | Mostra If(scrL4Pedidos.Size = ScreenSize.Small && gblL4Nivel = "revisao"; "Ficha 04";… | F2 a F7 |
| `btnL4dIniciais` | Botão | `conCabL4` | Pílula decorativa With({p: Split(Trim(gblL4dSessao.nome); " ")}; Up… | F11.5 |
| `lblL4dQuem` | Etiqueta | `conCabL4` | Mostra gblL4dSessao.nome | F11.5 |
| `btnL4dPerfil` | Botão | `conCabL4` | Pílula decorativa gblL4dSessao.perfil | F11.5 |
| `icoL4dUtilizadores` | Ícone | `conCabL4` | Ícone People («Gerir os utilizadores»): abre scrL4Conta; define gblL4dArea | F11.5 |
| `icoL4dPassword` | Ícone | `conCabL4` | Ícone Lock («Mudar a minha password»): abre scrL4Conta; define gblL4dArea | F11.5 |
| `btnL4dSair` | Botão | `conCabL4` | Botão «Sair»: abre scrL4Entrar; define gblL4dSessao | F11.5 |
| `conConteudoL4` | Contentor | `conEcraL4` | Contentor vertical | F2 a F7 |
| `conL4Barra` | Contentor | `conConteudoL4` | Contentor horizontal | F2 a F7 |
| `txtL4Pesquisa` | Caixa de texto | `conL4Barra` | Entrada de texto: Pesquisar clientes pelo início do nome | F2 a F7 |
| `lblL4Contagem` | Etiqueta | `conL4Barra` | Mostra With({n: CountRows(Filter(Clientes; StartsWith(Nome; txtL4Pesquisa.Text)))}; If… | F2 a F7 |
| `btnL4TodosPedidos` | Botão | `conL4Barra` | Botão «Todos os pedidos»: muda locL4Cliente | F2 a F7 |
| `conL4Corpo` | Contentor | `conConteudoL4` | Contentor horizontal | F2 a F7 |
| `conL4Lista` | Contentor | `conL4Corpo` | Contentor vertical, caixa com contorno | F2 a F7 |
| `lblL4ListaTitulo` | Etiqueta | `conL4Lista` | Texto fixo «CLIENTES» | F2 a F7 |
| `lblL4ListaVazia` | Etiqueta | `conL4Lista` | Texto fixo «Nenhum cliente começa por este texto.» | F2 a F7 |
| `galL4Clientes` | Galeria | `conL4Lista` | Galeria de Clientes | F2 a F7 |
| `recL4CliMarca` | Retângulo | `galL4Clientes` | Barra de cor à esquerda da linha | F2 a F7 |
| `btnL4CliIniciais` | Botão | `galL4Clientes` | Pílula decorativa With({p: Filter(Split(Trim(ThisItem.Nome); " ");… | F2 a F7 |
| `lblL4CliNome` | Etiqueta | `galL4Clientes` | Mostra ThisItem.Nome | F2 a F7 |
| `lblL4CliInfo` | Etiqueta | `galL4Clientes` | Mostra "NIF " & ThisItem.NIF & " · " & ThisItem.Telefone | F2 a F7 |
| `icoL4CliSeta` | Ícone | `galL4Clientes` | Ícone ChevronRight: passa o toque à linha da galeria | F2 a F7 |
| `recL4CliSeparador` | Retângulo | `galL4Clientes` | Linha de separação | F2 a F7 |
| `conL4Painel` | Contentor | `conL4Corpo` | Contentor vertical, caixa com contorno | F2 a F7 |
| `conL4PainelTopo` | Contentor | `conL4Painel` | Contentor horizontal | F2 a F7 |
| `btnL4VoltarLista` | Botão | `conL4PainelTopo` | Botão «‹ Clientes»: muda locL4Painel | F2 a F7 |
| `conL4PainelTit` | Contentor | `conL4PainelTopo` | Contentor vertical | F2 a F7 |
| `lblL4PainelTitulo` | Etiqueta | `conL4PainelTit` | Mostra Switch(locL4Modo; "cliente"; If(locL4Acao = "criar"; "Novo cliente"; "Editar cl… | F2 a F7 |
| `lblL4ClienteDados` | Etiqueta | `conL4PainelTit` | Mostra Switch(locL4Modo; "detalhe"; locL4Pedido.Clientes.Nome; "pedido"; locL4Pedido.C… | F2 a F7 |
| `btnL4cTratamento` | Botão | `conL4PainelTopo` | Pílula decorativa If(IsBlank(locL4Pedido.Tratamento); "Não processa… | F10 |
| `conL4Separadores` | Contentor | `conL4Painel` | Contentor horizontal, caixa com contorno | F2 a F7 |
| `btnL4SepTodos` | Botão | `conL4Separadores` | Botão "Todos (" & If(IsBlank(locL4Cliente); CountRows(F…: muda locL4Vista | F2 a F7 |
| `btnL4SepPendentes` | Botão | `conL4Separadores` | Botão If(scrL4Pedidos.Size >= ScreenSize.ExtraLarge; "P…: muda locL4Vista | F2 a F7 |
| `btnL4SepConcluidos` | Botão | `conL4Separadores` | Botão If(scrL4Pedidos.Size >= ScreenSize.ExtraLarge; "P…: muda locL4Vista | F2 a F7 |
| `conL4cSeparadores` | Contentor | `conL4Painel` | Contentor horizontal, caixa com contorno | F10 |
| `btnL4cSepAuto` | Botão | `conL4cSeparadores` | Botão "Automático (" & If(IsBlank(locL4Cliente); CountR…: muda locL4Vista | F10 |
| `btnL4cSepRevisao` | Botão | `conL4cSeparadores` | Botão If(gblL4Nivel = "revisao"; "Por decidir (" & If(I…: muda locL4Vista | F10 |
| `btnL4cSepErro` | Botão | `conL4cSeparadores` | Botão "Erro (" & If(IsBlank(locL4Cliente); CountRows(Fi…: muda locL4Vista | F10 |
| `lblL4Resumo` | Etiqueta | `conL4Painel` | Mostra Switch(locL4Vista; "pendentes"; "Vista do Dataverse «Pedidos Pendentes» · mais… | F2 a F7 |
| `lblL4SemPedidos` | Etiqueta | `conL4Painel` | Mostra If(IsBlank(locL4Cliente); "Não há pedidos nesta vista."; "Este cliente não tem… | F2 a F7 |
| `galL4Pedidos` | Galeria | `conL4Painel` | Galeria de Pedidos, Clientes | F2 a F7 |
| `recL4PedCartao` | Retângulo | `galL4Pedidos` | Fundo de cartão | F2 a F7 |
| `recL4PedBarra` | Retângulo | `galL4Pedidos` | Barra de cor à esquerda da linha | F2 a F7 |
| `lblL4PedNumero` | Etiqueta | `galL4Pedidos` | Mostra ThisItem.NumeroPedido & If(IsBlank(locL4Cliente); " · " & ThisItem.Clientes.Nom… | F2 a F7 |
| `lblL4PedDescricao` | Etiqueta | `galL4Pedidos` | Mostra Text(ThisItem.DataPedido; "dd/mm/yyyy") & " · " & ThisItem.Descrição | F2 a F7 |
| `lblL4PedValor` | Etiqueta | `galL4Pedidos` | Mostra If(IsBlank(ThisItem.Valor); "sem valor"; Text(ThisItem.Valor; "[$-pt-PT]0,00")… | F2 a F7 |
| `btnL4PedEstado` | Botão | `galL4Pedidos` | Pílula decorativa Text(ThisItem.EstadoPedido) | F2 a F7 |
| `btnL4cGTratamento` | Botão | `galL4Pedidos` | Pílula decorativa If(gblL4Nivel = "revisao" && ThisItem.Tratamento… | F10 |
| `frmL4Cliente` | Formulário | `conL4Painel` | Formulário de Clientes | F2 a F7 |
| `Nome_DataCard1` | Cartão de dados | `frmL4Cliente` | Cartão do formulário | F2 a F7 |
| `DataCardKey6` | Etiqueta | `Nome_DataCard1` | Mostra Parent.DisplayName | F2 a F7 |
| `txtL4CliNome` | Caixa de texto | `Nome_DataCard1` | Entrada de texto | F2 a F7 |
| `ErrorMessage6` | Etiqueta | `Nome_DataCard1` | Mostra Parent.Error | F2 a F7 |
| `StarVisible6` | Etiqueta | `Nome_DataCard1` | Texto fixo «*» | F2 a F7 |
| `NIF_DataCard1` | Cartão de dados | `frmL4Cliente` | Cartão do formulário | F2 a F7 |
| `DataCardKey9` | Etiqueta | `NIF_DataCard1` | Mostra Parent.DisplayName | F2 a F7 |
| `txtL4CliNIF` | Caixa de texto | `NIF_DataCard1` | Entrada de texto | F2 a F7 |
| `ErrorMessage9` | Etiqueta | `NIF_DataCard1` | Mostra Parent.Error | F2 a F7 |
| `StarVisible9` | Etiqueta | `NIF_DataCard1` | Texto fixo «*» | F2 a F7 |
| `Email_DataCard1` | Cartão de dados | `frmL4Cliente` | Cartão do formulário | F2 a F7 |
| `DataCardKey7` | Etiqueta | `Email_DataCard1` | Mostra Parent.DisplayName | F2 a F7 |
| `txtL4CliEmail` | Caixa de texto | `Email_DataCard1` | Entrada de texto | F2 a F7 |
| `ErrorMessage7` | Etiqueta | `Email_DataCard1` | Mostra Parent.Error | F2 a F7 |
| `StarVisible7` | Etiqueta | `Email_DataCard1` | Texto fixo «*» | F2 a F7 |
| `Telefone_DataCard1` | Cartão de dados | `frmL4Cliente` | Cartão do formulário | F2 a F7 |
| `DataCardKey8` | Etiqueta | `Telefone_DataCard1` | Mostra Parent.DisplayName | F2 a F7 |
| `txtL4CliTelefone` | Caixa de texto | `Telefone_DataCard1` | Entrada de texto | F2 a F7 |
| `ErrorMessage8` | Etiqueta | `Telefone_DataCard1` | Mostra Parent.Error | F2 a F7 |
| `StarVisible8` | Etiqueta | `Telefone_DataCard1` | Texto fixo «*» | F2 a F7 |
| `conL4cTestes` | Contentor | `conL4Painel` | Contentor horizontal, caixa com contorno | F10 |
| `lblL4cTestesRot` | Etiqueta | `conL4cTestes` | Texto fixo «Valor de teste:» | F10 |
| `btnL4cTeste100` | Botão | `conL4cTestes` | Botão «100»: muda locL4cValorTeste | F10 |
| `btnL4cTeste500` | Botão | `conL4cTestes` | Botão «500»: muda locL4cValorTeste | F10 |
| `btnL4cTeste750` | Botão | `conL4cTestes` | Botão «750»: muda locL4cValorTeste | F10 |
| `btnL4cTesteSemvalor` | Botão | `conL4cTestes` | Botão «Sem valor»: muda locL4cValorTeste | F10 |
| `frmL4Pedido` | Formulário | `conL4Painel` | Formulário de Pedidos | F2 a F7 |
| `Cliente_DataCard1` | Cartão de dados | `frmL4Pedido` | Cartão do formulário: Cliente | F2 a F7 |
| `DataCardKey22` | Etiqueta | `Cliente_DataCard1` | Mostra Parent.DisplayName | F2 a F7 |
| `cmbL4PedCliente` | Caixa de combinação | `Cliente_DataCard1` | Escolha de Choices([@Pedidos].dac_Cliente) | F2 a F7 |
| `ErrorMessage21` | Etiqueta | `Cliente_DataCard1` | Mostra Parent.Error | F2 a F7 |
| `StarVisible21` | Etiqueta | `Cliente_DataCard1` | Texto fixo «*» | F2 a F7 |
| `lblL4PedCliente` | Etiqueta | `Cliente_DataCard1` | Mostra If(frmL4Pedido.Mode = FormMode.New; locL4Cliente.Nome; LookUp(Clientes; Cliente… | F2 a F7 |
| `DataPedido_DataCard1` | Cartão de dados | `frmL4Pedido` | Cartão do formulário: Data do pedido | F2 a F7 |
| `DataCardKey15` | Etiqueta | `DataPedido_DataCard1` | Mostra Parent.DisplayName | F2 a F7 |
| `dteL4PedData` | Seletor de data | `DataPedido_DataCard1` | Seletor de data | F2 a F7 |
| `ErrorMessage15` | Etiqueta | `DataPedido_DataCard1` | Mostra Parent.Error | F2 a F7 |
| `StarVisible15` | Etiqueta | `DataPedido_DataCard1` | Texto fixo «*» | F2 a F7 |
| `Estado (dac_estado)_DataCard1` | Cartão de dados | `frmL4Pedido` | Cartão do formulário: Estado | F2 a F7 |
| `DataCardKey17` | Etiqueta | `Estado (dac_estado)_DataCard1` | Mostra Parent.DisplayName | F2 a F7 |
| `cmbL4PedEstado` | Caixa de combinação | `Estado (dac_estado)_DataCard1` | Escolha de Choices('EstadoPedido (Pedidos)') | F2 a F7 |
| `ErrorMessage17` | Etiqueta | `Estado (dac_estado)_DataCard1` | Mostra Parent.Error | F2 a F7 |
| `StarVisible17` | Etiqueta | `Estado (dac_estado)_DataCard1` | Texto fixo «*» | F2 a F7 |
| `Valor_DataCard1` | Cartão de dados | `frmL4Pedido` | Cartão do formulário: Valor (€) | F2 a F7 |
| `DataCardKey19` | Etiqueta | `Valor_DataCard1` | Mostra Parent.DisplayName | F2 a F7 |
| `txtL4PedValor` | Caixa de texto | `Valor_DataCard1` | Entrada de texto | F2 a F7 |
| `ErrorMessage18` | Etiqueta | `Valor_DataCard1` | Mostra Parent.Error | F2 a F7 |
| `StarVisible18` | Etiqueta | `Valor_DataCard1` | Texto fixo «*» | F2 a F7 |
| `Descricao_DataCard1` | Cartão de dados | `frmL4Pedido` | Cartão do formulário: Descrição | F2 a F7 |
| `DataCardKey16` | Etiqueta | `Descricao_DataCard1` | Mostra Parent.DisplayName | F2 a F7 |
| `txtL4PedDescricao` | Caixa de texto | `Descricao_DataCard1` | Entrada de texto | F2 a F7 |
| `ErrorMessage16` | Etiqueta | `Descricao_DataCard1` | Mostra Parent.Error | F2 a F7 |
| `StarVisible16` | Etiqueta | `Descricao_DataCard1` | Texto fixo «*» | F2 a F7 |
| `conL4cDetalhe` | Contentor | `conL4Painel` | Contentor vertical, desloca | F10 |
| `conL4cDetConteudo` | Contentor | `conL4cDetalhe` | Contentor vertical | F10 |
| `conL4cSecDados` | Contentor | `conL4cDetConteudo` | Contentor vertical, caixa com contorno | F10 |
| `lblL4cSecDadosTit` | Etiqueta | `conL4cSecDados` | Texto fixo «Dados do pedido» | F10 |
| `conL4cDetData` | Contentor | `conL4cSecDados` | Contentor horizontal | F10 |
| `lblL4cDetDataRot` | Etiqueta | `conL4cDetData` | Texto fixo «Data» | F10 |
| `lblL4cDetData` | Etiqueta | `conL4cDetData` | Mostra Text(locL4Pedido.DataPedido; "dd/mm/yyyy") & If(IsBlank(locL4Pedido.'Registado… | F10 |
| `conL4cDetEstado` | Contentor | `conL4cSecDados` | Contentor horizontal | F10 |
| `lblL4cDetEstadoRot` | Etiqueta | `conL4cDetEstado` | Texto fixo «Estado» | F10 |
| `lblL4cDetEstado` | Etiqueta | `conL4cDetEstado` | Mostra Text(locL4Pedido.EstadoPedido) | F10 |
| `conL4cDetValor` | Contentor | `conL4cSecDados` | Contentor horizontal | F10 |
| `lblL4cDetValorRot` | Etiqueta | `conL4cDetValor` | Texto fixo «Valor» | F10 |
| `lblL4cDetValor` | Etiqueta | `conL4cDetValor` | Mostra If(IsBlank(locL4Pedido.Valor); "sem valor"; Text(locL4Pedido.Valor; "[$-pt-PT]0… | F10 |
| `conL4cDetDescricao` | Contentor | `conL4cSecDados` | Contentor horizontal | F10 |
| `lblL4cDetDescricaoRot` | Etiqueta | `conL4cDetDescricao` | Texto fixo «Descrição» | F10 |
| `lblL4cDetDescricao` | Etiqueta | `conL4cDetDescricao` | Mostra Coalesce(locL4Pedido.'Descrição'; "—") | F10 |
| `conL4cSecProc` | Contentor | `conL4cDetConteudo` | Contentor vertical, caixa com contorno | F10 |
| `lblL4cProcTitulo` | Etiqueta | `conL4cSecProc` | Texto fixo «Processamento automático» | F10 |
| `conL4cPassos` | Contentor | `conL4cSecProc` | Contentor horizontal | F10 |
| `btnL4cPasso1` | Botão | `conL4cPassos` | Pílula decorativa «Registado» | F10 |
| `conL4cPassoTraco1` | Contentor | `conL4cPassos` | Linha de separação (contentor vazio) | F10 |
| `btnL4cPasso2` | Botão | `conL4cPassos` | Pílula decorativa If(locL4cAguardar; "A classificar"; locL4Pedido.P… | F10 |
| `conL4cPassoTraco2` | Contentor | `conL4cPassos` | Linha de separação (contentor vazio) | F10 |
| `btnL4cPasso3` | Botão | `conL4cPassos` | Pílula decorativa If(!locL4Pedido.Processado; "Decisão"; locL4Pedid… | F10 |
| `lblL4cAguarda` | Etiqueta | `conL4cSecProc` | Mostra "A aguardar o fluxo DAC2627_Pedido_Classificar · consulta " & (locL4cTentativas… | F10 |
| `conL4cDetProcessado` | Contentor | `conL4cSecProc` | Contentor horizontal | F10 |
| `lblL4cDetProcessadoRot` | Etiqueta | `conL4cDetProcessado` | Texto fixo «Processado» | F10 |
| `lblL4cDetProcessado` | Etiqueta | `conL4cDetProcessado` | Mostra If(locL4Pedido.Processado; "Sim, em " & Text(locL4Pedido.DataProcessamento; "dd… | F10 |
| `conL4cDetObs` | Contentor | `conL4cSecProc` | Contentor horizontal | F10 |
| `lblL4cDetObsRot` | Etiqueta | `conL4cDetObs` | Texto fixo «Justificação» | F10 |
| `lblL4cDetObs` | Etiqueta | `conL4cDetObs` | Mostra Coalesce(locL4Pedido.ObservacoesProcessamento; "—") | F10 |
| `conL4cDetExecucao` | Contentor | `conL4cSecProc` | Contentor horizontal | F10 |
| `lblL4cDetExecucaoRot` | Etiqueta | `conL4cDetExecucao` | Texto fixo «Execução» | F10 |
| `lblL4cDetExecucao` | Etiqueta | `conL4cDetExecucao` | Mostra Coalesce(locL4Pedido.IdExecucao; "—") | F10 |
| `conL4cAcoes` | Contentor | `conL4cSecProc` | Contentor horizontal | F10 |
| `btnL4cAtualizar` | Botão | `conL4cAcoes` | Botão «Atualizar estado»: volta a ler os dados; muda locL4Pedido | F10 |
| `btnL4cReprocessar` | Botão | `conL4cAcoes` | Botão «Reprocessar»: chama o fluxo DAC2627_Pedido_Reprocessar; muda locL4MsgTipo, locL4cAguardar | F10 |
| `lblL4cProcNota` | Etiqueta | `conL4cSecProc` | Texto fixo «O fluxo DAC2627_Pedido_Classificar trata o pedido em segundo plano, s…» | F10 |
| `conL4cSecRev` | Contentor | `conL4cDetConteudo` | Contentor vertical, caixa com contorno | F10 |
| `lblL4cRevTitulo` | Etiqueta | `conL4cSecRev` | Texto fixo «Revisão humana» | F10 |
| `lblL4cDecisao` | Etiqueta | `conL4cSecRev` | Mostra "Decisão: " & If(IsBlank(locL4Pedido.Decisao); "—"; Text(locL4Pedido.Decisao))… | F10 |
| `lblL4dDetProposta` | Etiqueta | `conL4cSecRev` | Mostra "Proposta de " & locL4Pedido.'Proposta por'.Nome & " em " & Text(locL4Pedido.'D… | F11.5 |
| `lblL4dDetDecisao` | Etiqueta | `conL4cSecRev` | Mostra "Decisão final: " & Lower(Text(locL4Pedido.Decisao)) & If(IsBlank(locL4Pedido.'… | F11.5 |
| `lblL4dDetEspera` | Etiqueta | `conL4cSecRev` | Mostra If(locL4Pedido.Decisao = 'Decisao (Pedidos)'.'Aguarda decisão'; "Aguarda a prop… | F11.5 |
| `lblL4dSoLeitura` | Etiqueta | `conL4cSecRev` | Texto fixo «O perfil Cliente acompanha os pedidos mas não decide.» | F11.5 |
| `lblL4dComentarioRot` | Etiqueta | `conL4cSecRev` | Texto fixo «Comentário (obrigatório para rejeitar)» | F11.5 |
| `txtL4dComentario` | Caixa de texto | `conL4cSecRev` | Entrada de texto: Comentário da proposta ou da decisão | F11.5 |
| `conL4dAcoesGestor` | Contentor | `conL4cSecRev` | Contentor horizontal | F11.5 |
| `btnL4dProporRejeitar` | Botão | `conL4dAcoesGestor` | Botão «Propor rejeitar»: chama o fluxo DAC2627_Pedido_Decidir; volta a ler os dados; muda locL4MsgTipo, locL4Pedido | F11.5 |
| `btnL4dProporAprovar` | Botão | `conL4dAcoesGestor` | Botão «Propor aprovar»: chama o fluxo DAC2627_Pedido_Decidir; volta a ler os dados; muda locL4MsgTipo, locL4Pedido | F11.5 |
| `conL4dAcoesAdmin` | Contentor | `conL4cSecRev` | Contentor horizontal | F11.5 |
| `btnL4dRejeitar` | Botão | `conL4dAcoesAdmin` | Botão «Rejeitar»: chama o fluxo DAC2627_Pedido_Decidir; volta a ler os dados; muda locL4MsgTipo, locL4Pedido | F11.5 |
| `btnL4dAprovar` | Botão | `conL4dAcoesAdmin` | Botão «Aprovar»: chama o fluxo DAC2627_Pedido_Decidir; volta a ler os dados; muda locL4MsgTipo, locL4Pedido | F11.5 |
| `conL4RodapeLinha` | Contentor | `conL4Painel` | Linha de separação (contentor vazio) | F2 a F7 |
| `conL4Rodape` | Contentor | `conL4Painel` | Contentor horizontal | F2 a F7 |
| `btnL4cVoltar` | Botão | `conL4Rodape` | Botão «‹ Pedidos»: muda locL4Modo | F10 |
| `btnL4cEditar` | Botão | `conL4Rodape` | Botão «Editar pedido»: abre o formulário a editar; muda locL4Modo | F10 |
| `btnL4RemoverCliente` | Botão | `conL4Rodape` | Botão If(scrL4Pedidos.Size = ScreenSize.Small; "Remover…: muda locL4Confirmar | F2 a F7 |
| `btnL4EditarCliente` | Botão | `conL4Rodape` | Botão If(scrL4Pedidos.Size = ScreenSize.Small; "Editar"…: abre o formulário a editar; muda locL4Modo | F2 a F7 |
| `btnL4NovoCliente` | Botão | `conL4Rodape` | Botão If(scrL4Pedidos.Size = ScreenSize.Small; "+ Clien…: abre o formulário a criar; muda locL4Modo | F2 a F7 |
| `btnL4NovoPedido` | Botão | `conL4Rodape` | Botão If(scrL4Pedidos.Size = ScreenSize.Small; "+ Pedid…: abre o formulário a criar; muda locL4Pedido | F2 a F7 |
| `btnL4RemoverPedido` | Botão | `conL4Rodape` | Botão If(scrL4Pedidos.Size = ScreenSize.Small; "Remover…: muda locL4Confirmar | F2 a F7 |
| `btnL4Cancelar` | Botão | `conL4Rodape` | Botão «Cancelar»: muda locL4Modo | F2 a F7 |
| `btnL4Guardar` | Botão | `conL4Rodape` | Botão «Guardar»: muda locL4Confirmar, locL4MsgTipo | F2 a F7 |
| `recL4Veu` | Retângulo | ecrã | Véu por trás do diálogo | F2 a F7 |
| `conL4Dialogo` | Contentor | ecrã | Contentor vertical, raiz do ecrã | F2 a F7 |
| `lblL4ConfTitulo` | Etiqueta | `conL4Dialogo` | Mostra Switch(locL4Confirmar; "guardar"; If(locL4Modo = "cliente"; If(locL4Acao = "cri… | F2 a F7 |
| `lblL4ConfTexto` | Etiqueta | `conL4Dialogo` | Mostra Switch(locL4Confirmar; "guardar"; If(locL4Modo = "cliente"; If(locL4Acao = "cri… | F2 a F7 |
| `conL4ConfBotoes` | Contentor | `conL4Dialogo` | Contentor horizontal | F2 a F7 |
| `btnL4ConfCancelar` | Botão | `conL4ConfBotoes` | Botão «Cancelar»: muda locL4Confirmar | F2 a F7 |
| `btnL4ConfOk` | Botão | `conL4ConfBotoes` | Botão If(locL4Confirmar = "guardar"; If(locL4Acao = "cr…: grava o formulário; apaga um registo; muda locL4Cliente, locL4MsgTipo, locL4Pedido, locL4UltimaConf | F2 a F7 |
| `conL4Mensagem` | Contentor | ecrã | Contentor horizontal, raiz do ecrã | F2 a F7 |
| `icoL4MsgIcone` | Ícone | `conL4Mensagem` | Ícone If(locL4MsgTipo = "erro"; Warning; Check): decorativo | F2 a F7 |
| `lblL4Mensagem` | Etiqueta | `conL4Mensagem` | Mostra locL4Msg | F2 a F7 |
| `icoL4FecharMsg` | Ícone | `conL4Mensagem` | Ícone Cancel («Fechar mensagem»): muda locL4Msg | F2 a F7 |
| `tmrL4Mensagem` | Temporizador | ecrã | Temporizador de 3500 ms: muda locL4Msg | F2 a F7 |
| `tmrL4cEstado` | Temporizador | ecrã | Temporizador de 3000 ms: volta a ler os dados; muda locL4Pedido, locL4cAguardar | F10 |
| `lblL4Anuncio` | Etiqueta | ecrã | Mostra locL4Msg | F2 a F7 |

## scrL4Complemento

| Controlo | Tipo | Dentro de | O que é | Manual |
|---|---|---|---|---|
| `conEcraL4b` | Contentor | ecrã | Contentor vertical, raiz do ecrã | F8 |
| `conCabL4b` | Contentor | `conEcraL4b` | Contentor horizontal | F8 |
| `icoInicioL4b` | Ícone | `conCabL4b` | Ícone Home («Voltar ao início»): abre scrInicio | F8 |
| `lblCabL4b` | Etiqueta | `conCabL4b` | Texto fixo «Ficha 04 · Complemento» | F8 |
| `conConteudoL4b` | Contentor | `conEcraL4b` | Contentor vertical, desloca | F8 |
| `lblL4bTitulo` | Etiqueta | `conConteudoL4b` | Mostra If(locL4bVista = "tabela"; "Comparação por critério"; "SharePoint, Dataverse e… | F8 |
| `lblL4bIntro` | Etiqueta | `conConteudoL4b` | Texto fixo «Ponto 8 do Lab 4. A Ficha 04 guarda clientes e pedidos no Dataverse,…» | F8 |
| `lblL4bSpNome` | Etiqueta | `conConteudoL4b` | Texto fixo «SharePoint (listas)» | F8 |
| `lblL4bSpModelo` | Etiqueta | `conConteudoL4b` | Texto fixo «O modelo SaaS colaborativo» | F8 |
| `lblL4bSpOQue` | Etiqueta | `conConteudoL4b` | Mostra "As listas do SharePoint são as mesmas da aplicação Microsoft Lists e vivem num… | F8 |
| `lblL4bSpAprofTit` | Etiqueta | `conConteudoL4b` | Texto fixo «O limiar de vista e a delegação» | F8 |
| `lblL4bSpAprof` | Etiqueta | `conConteudoL4b` | Mostra "Uma lista pode guardar até 30 milhões de itens, mas uma consulta que percorra… | F8 |
| `lblL4bSpFavorTit` | Etiqueta | `conConteudoL4b` | Texto fixo «A favor» | F8 |
| `lblL4bSpFavor` | Etiqueta | `conConteudoL4b` | Mostra "• Incluído no Microsoft 365. O conector do SharePoint é standard, por isso uma… | F8 |
| `lblL4bSpContraTit` | Etiqueta | `conConteudoL4b` | Texto fixo «Contra» | F8 |
| `lblL4bSpContra` | Etiqueta | `conConteudoL4b` | Mostra "• Limiar de vista. Uma consulta não processa mais de 5000 itens de cada vez, e… | F8 |
| `lblL4bSpSintese` | Etiqueta | `conConteudoL4b` | Texto fixo «Em síntese. O SharePoint é uma boa escolha para prototipar depressa e…» | F8 |
| `lblL4bDvNome` | Etiqueta | `conConteudoL4b` | Texto fixo «Dataverse» | F8 |
| `lblL4bDvModelo` | Etiqueta | `conConteudoL4b` | Texto fixo «A plataforma de dados da Power Platform» | F8 |
| `lblL4bDvOQue` | Etiqueta | `conConteudoL4b` | Mostra "O Microsoft Dataverse é uma base de dados relacional gerida pela Microsoft, qu… | F8 |
| `lblL4bDvAprofTit` | Etiqueta | `conConteudoL4b` | Texto fixo «Ciclo de vida, segurança e ambientes» | F8 |
| `lblL4bDvAprof` | Etiqueta | `conConteudoL4b` | Mostra "O Dataverse traz para o desenvolvimento low-code a gestão do ciclo de vida das… | F8 |
| `lblL4bDvFavorTit` | Etiqueta | `conConteudoL4b` | Texto fixo «A favor» | F8 |
| `lblL4bDvFavor` | Etiqueta | `conConteudoL4b` | Mostra "• Relações nativas. As relações de um para muitos e de muitos para muitos pert… | F8 |
| `lblL4bDvContraTit` | Etiqueta | `conConteudoL4b` | Texto fixo «Contra» | F8 |
| `lblL4bDvContra` | Etiqueta | `conConteudoL4b` | Mostra "• Licenciamento premium. O conector do Dataverse é premium, e cada utilizador… | F8 |
| `lblL4bDvSintese` | Etiqueta | `conConteudoL4b` | Texto fixo «Em síntese. O Dataverse é a escolha natural para aplicações de negóci…» | F8 |
| `lblL4bSqlNome` | Etiqueta | `conConteudoL4b` | Texto fixo «SQL (Azure SQL Database)» | F8 |
| `lblL4bSqlModelo` | Etiqueta | `conConteudoL4b` | Texto fixo «O PaaS relacional» | F8 |
| `lblL4bSqlOQue` | Etiqueta | `conConteudoL4b` | Mostra "O Azure SQL Database é o motor do SQL Server oferecido como serviço na cloud d… | F8 |
| `lblL4bSqlAprofTit` | Etiqueta | `conConteudoL4b` | Texto fixo «Computação, armazenamento e lógica no servidor» | F8 |
| `lblL4bSqlAprof` | Etiqueta | `conConteudoL4b` | Mostra "No Dataverse, a parte variável do custo é a capacidade de armazenamento. No Az… | F8 |
| `lblL4bSqlFavorTit` | Etiqueta | `conConteudoL4b` | Texto fixo «A favor» | F8 |
| `lblL4bSqlFavor` | Etiqueta | `conConteudoL4b` | Mostra "• Modelo relacional completo. Chaves estrangeiras, índices, vistas e procedime… | F8 |
| `lblL4bSqlContraTit` | Etiqueta | `conConteudoL4b` | Texto fixo «Contra» | F8 |
| `lblL4bSqlContra` | Etiqueta | `conConteudoL4b` | Mostra "• Custos somados. O conector SQL Server é premium, e a base de dados no Azure… | F8 |
| `lblL4bSqlSintese` | Etiqueta | `conConteudoL4b` | Texto fixo «Em síntese. O Azure SQL Database é a escolha para grandes volumes de…» | F8 |
| `btnL4bVerTabela` | Botão | `conConteudoL4b` | Botão «Ver a tabela comparativa»: muda locL4bVista | F8 |
| `lblL4bTabIntro` | Etiqueta | `conConteudoL4b` | Texto fixo «Os sete critérios do enunciado do Lab 4 e dois da perspetiva cloud, l…» | F8 |
| `conL4bCabecalho` | Contentor | `conConteudoL4b` | Contentor horizontal | F8 |
| `lblL4bCabCriterio` | Etiqueta | `conL4bCabecalho` | Texto fixo «Critério» | F8 |
| `lblL4bCabSharePoint` | Etiqueta | `conL4bCabecalho` | Texto fixo «SharePoint (listas)» | F8 |
| `lblL4bCabDataverse` | Etiqueta | `conL4bCabecalho` | Mostra If(scrL4Complemento.Size = ScreenSize.Medium; "Dataverse"; "Dataverse · usado n… | F8 |
| `lblL4bCabSQL` | Etiqueta | `conL4bCabecalho` | Texto fixo «SQL (Azure SQL)» | F8 |
| `conL4bLinha1` | Contentor | `conConteudoL4b` | Contentor horizontal | F8 |
| `lblL4bCrit1` | Etiqueta | `conL4bLinha1` | Texto fixo «Estrutura» | F8 |
| `lblL4bSp1` | Etiqueta | `conL4bLinha1` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SharePoint · "; "") & "Listas com… | F8 |
| `lblL4bDv1` | Etiqueta | `conL4bLinha1` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "Dataverse · "; "") & "Tabelas com… | F8 |
| `lblL4bSql1` | Etiqueta | `conL4bLinha1` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SQL · "; "") & "Tabelas, tipos e… | F8 |
| `conL4bLinha2` | Contentor | `conConteudoL4b` | Contentor horizontal | F8 |
| `lblL4bCrit2` | Etiqueta | `conL4bLinha2` | Texto fixo «Relações» | F8 |
| `lblL4bSp2` | Etiqueta | `conL4bLinha2` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SharePoint · "; "") & "Coluna de… | F8 |
| `lblL4bDv2` | Etiqueta | `conL4bLinha2` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "Dataverse · "; "") & "1:N e N:N n… | F8 |
| `lblL4bSql2` | Etiqueta | `conL4bLinha2` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SQL · "; "") & "Chaves estrangeir… | F8 |
| `conL4bLinha3` | Contentor | `conConteudoL4b` | Contentor horizontal | F8 |
| `lblL4bCrit3` | Etiqueta | `conL4bLinha3` | Texto fixo «Desenvolvimento Power Apps» | F8 |
| `lblL4bSp3` | Etiqueta | `conL4bLinha3` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SharePoint · "; "") & "Conector s… | F8 |
| `lblL4bDv3` | Etiqueta | `conL4bLinha3` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "Dataverse · "; "") & "Conector pr… | F8 |
| `lblL4bSql3` | Etiqueta | `conL4bLinha3` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SQL · "; "") & "Conector premium.… | F8 |
| `conL4bLinha4` | Contentor | `conConteudoL4b` | Contentor horizontal | F8 |
| `lblL4bCrit4` | Etiqueta | `conL4bLinha4` | Texto fixo «Interface pronta» | F8 |
| `lblL4bSp4` | Etiqueta | `conL4bLinha4` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SharePoint · "; "") & "Sim. Micro… | F8 |
| `lblL4bDv4` | Etiqueta | `conL4bLinha4` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "Dataverse · "; "") & "Sim. App ba… | F8 |
| `lblL4bSql4` | Etiqueta | `conL4bLinha4` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SQL · "; "") & "Não. A interface… | F8 |
| `conL4bLinha5` | Contentor | `conConteudoL4b` | Contentor horizontal | F8 |
| `lblL4bCrit5` | Etiqueta | `conL4bLinha5` | Texto fixo «Lógica» | F8 |
| `lblL4bSp5` | Etiqueta | `conL4bLinha5` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SharePoint · "; "") & "Validação… | F8 |
| `lblL4bDv5` | Etiqueta | `conL4bLinha5` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "Dataverse · "; "") & "Regras de n… | F8 |
| `lblL4bSql5` | Etiqueta | `conL4bLinha5` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SQL · "; "") & "Restrições, gatil… | F8 |
| `conL4bLinha6` | Contentor | `conConteudoL4b` | Contentor horizontal | F8 |
| `lblL4bCrit6` | Etiqueta | `conL4bLinha6` | Texto fixo «Gestão» | F8 |
| `lblL4bSp6` | Etiqueta | `conL4bLinha6` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SharePoint · "; "") & "Dono do si… | F8 |
| `lblL4bDv6` | Etiqueta | `conL4bLinha6` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "Dataverse · "; "") & "Centro de a… | F8 |
| `lblL4bSql6` | Etiqueta | `conL4bLinha6` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SQL · "; "") & "Portal do Azure (… | F8 |
| `conL4bLinha7` | Contentor | `conConteudoL4b` | Contentor horizontal | F8 |
| `lblL4bCrit7` | Etiqueta | `conL4bLinha7` | Texto fixo «Caso de uso sugerido» | F8 |
| `lblL4bSp7` | Etiqueta | `conL4bLinha7` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SharePoint · "; "") & "Listas sim… | F8 |
| `lblL4bDv7` | Etiqueta | `conL4bLinha7` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "Dataverse · "; "") & "Apps de neg… | F8 |
| `lblL4bSql7` | Etiqueta | `conL4bLinha7` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SQL · "; "") & "Dados que já vive… | F8 |
| `conL4bLinha8` | Contentor | `conConteudoL4b` | Contentor horizontal | F8 |
| `lblL4bCrit8` | Etiqueta | `conL4bLinha8` | Texto fixo «Modelo de serviço cloud» | F8 |
| `lblL4bSp8` | Etiqueta | `conL4bLinha8` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SharePoint · "; "") & "SaaS. Faz… | F8 |
| `lblL4bDv8` | Etiqueta | `conL4bLinha8` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "Dataverse · "; "") & "Plataforma… | F8 |
| `lblL4bSql8` | Etiqueta | `conL4bLinha8` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SQL · "; "") & "PaaS do Azure. Co… | F8 |
| `conL4bLinha9` | Contentor | `conConteudoL4b` | Contentor horizontal | F8 |
| `lblL4bCrit9` | Etiqueta | `conL4bLinha9` | Texto fixo «Custo e licenciamento» | F8 |
| `lblL4bSp9` | Etiqueta | `conL4bLinha9` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SharePoint · "; "") & "Incluído n… | F8 |
| `lblL4bDv9` | Etiqueta | `conL4bLinha9` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "Dataverse · "; "") & "Licença Pow… | F8 |
| `lblL4bSql9` | Etiqueta | `conL4bLinha9` | Mostra If(scrL4Complemento.Size = ScreenSize.Small; "SQL · "; "") & "Licença Power App… | F8 |
| `lblL4bConclusao` | Etiqueta | `conConteudoL4b` | Mostra "A Ficha 04 usa o Dataverse porque o problema o pedia: uma relação de um para m… | F8 |
| `btnL4bVoltarTexto` | Botão | `conConteudoL4b` | Botão «Voltar ao texto»: muda locL4bVista | F8 |

## scrL4Entrar

| Controlo | Tipo | Dentro de | O que é | Manual |
|---|---|---|---|---|
| `conEcraL4dE` | Contentor | ecrã | Contentor vertical, raiz do ecrã | F11.5 |
| `conCabL4dE` | Contentor | `conEcraL4dE` | Contentor horizontal | F11.5 |
| `icoInicioL4dE` | Ícone | `conCabL4dE` | Ícone Home («Voltar ao início»): abre scrInicio | F11.5 |
| `lblCabL4dE` | Etiqueta | `conCabL4dE` | Texto fixo «Ficha 04 · Revisão» | F11.5 |
| `conConteudoL4dE` | Contentor | `conEcraL4dE` | Contentor vertical, desloca | F11.5 |
| `conL4dEntrarCorpo` | Contentor | `conConteudoL4dE` | Contentor horizontal | F11.5 |
| `conL4dEntrar` | Contentor | `conL4dEntrarCorpo` | Contentor vertical, caixa com contorno | F11.5 |
| `lblL4dEntrarTitulo` | Etiqueta | `conL4dEntrar` | Texto fixo «Entrar» | F11.5 |
| `lblL4dEntrarSub` | Etiqueta | `conL4dEntrar` | Texto fixo «Use o email e a password da sua conta.» | F11.5 |
| `lblL4dEmailRot` | Etiqueta | `conL4dEntrar` | Texto fixo «Email» | F11.5 |
| `txtL4dEmail` | Caixa de texto | `conL4dEntrar` | Entrada de texto: Email | F11.5 |
| `lblL4dPasswordRot` | Etiqueta | `conL4dEntrar` | Texto fixo «Password» | F11.5 |
| `txtL4dPassword` | Caixa de texto | `conL4dEntrar` | Entrada de texto (password): Password | F11.5 |
| `btnL4dEntrar` | Botão | `conL4dEntrar` | Botão If(locL4dAEntrar; "A verificar…"; "Entrar"): abre scrL4Pedidos; chama o fluxo DAC2627_Utilizador_Entrar; define gblL4dSessao; define gblL4Nivel; muda locL4dAEntrar, locL4dMsgTipo | F11.5 |
| `conL4dPerfis` | Contentor | `conL4dEntrarCorpo` | Contentor vertical | F11.5 |
| `lblL4dPerfisTitulo` | Etiqueta | `conL4dPerfis` | Texto fixo «Revisão de pedidos com três perfis» | F11.5 |
| `conL4dPerfilCliente` | Contentor | `conL4dPerfis` | Contentor horizontal | F11.5 |
| `lblL4dPerfilClienteRot` | Etiqueta | `conL4dPerfilCliente` | Texto fixo «Cliente» | F11.5 |
| `lblL4dPerfilCliente` | Etiqueta | `conL4dPerfilCliente` | Texto fixo «Regista pedidos para a sua empresa e acompanha a decisão.» | F11.5 |
| `conL4dPerfilGestor` | Contentor | `conL4dPerfis` | Contentor horizontal | F11.5 |
| `lblL4dPerfilGestorRot` | Etiqueta | `conL4dPerfilGestor` | Texto fixo «Gestor» | F11.5 |
| `lblL4dPerfilGestor` | Etiqueta | `conL4dPerfilGestor` | Texto fixo «Gere clientes e pedidos e propõe aprovar ou rejeitar os que estão em…» | F11.5 |
| `conL4dPerfilAdmin` | Contentor | `conL4dPerfis` | Contentor horizontal | F11.5 |
| `lblL4dPerfilAdminRot` | Etiqueta | `conL4dPerfilAdmin` | Texto fixo «Admin» | F11.5 |
| `lblL4dPerfilAdmin` | Etiqueta | `conL4dPerfilAdmin` | Texto fixo «Decide os pedidos, valida as propostas dos Gestores e gere os utiliza…» | F11.5 |
| `conL4dPerfisLinha` | Contentor | `conL4dPerfis` | Linha de separação (contentor vazio) | F11.5 |
| `lblL4dComoTitulo` | Etiqueta | `conL4dPerfis` | Texto fixo «Como é verificada a password» | F11.5 |
| `lblL4dComo` | Etiqueta | `conL4dPerfis` | Texto fixo «A password não fica guardada em lado nenhum. O fluxo DAC2627_Utilizad…» | F11.5 |
| `conL4dEMensagem` | Contentor | ecrã | Contentor horizontal, raiz do ecrã | F11.5 |
| `icoL4dEMsgIcone` | Ícone | `conL4dEMensagem` | Ícone If(locL4dMsgTipo = "erro"; Warning; Check): decorativo | F11.5 |
| `lblL4dEMensagem` | Etiqueta | `conL4dEMensagem` | Mostra locL4dMsg | F11.5 |
| `icoL4dEFecharMsg` | Ícone | `conL4dEMensagem` | Ícone Cancel («Fechar mensagem»): muda locL4dMsg | F11.5 |
| `tmrL4dEMensagem` | Temporizador | ecrã | Temporizador de 5000 ms: muda locL4dMsg | F11.5 |
| `lblL4dEAnuncio` | Etiqueta | ecrã | Mostra locL4dMsg | F11.5 |

## scrL4Conta

| Controlo | Tipo | Dentro de | O que é | Manual |
|---|---|---|---|---|
| `conEcraL4dC` | Contentor | ecrã | Contentor vertical, raiz do ecrã | F11.5 |
| `conCabL4dC` | Contentor | `conEcraL4dC` | Contentor horizontal | F11.5 |
| `icoInicioL4dC` | Ícone | `conCabL4dC` | Ícone Home («Voltar ao início»): abre scrInicio | F11.5 |
| `lblCabL4dC` | Etiqueta | `conCabL4dC` | Texto fixo «Ficha 04 · Revisão» | F11.5 |
| `icoL4dCUtilizadores` | Ícone | `conCabL4dC` | Ícone People («Gerir os utilizadores»): define gblL4dArea; muda locL4dUtil | F11.5 |
| `icoL4dCPassword` | Ícone | `conCabL4dC` | Ícone Lock («Mudar a minha password»): define gblL4dArea; muda locL4dUtil | F11.5 |
| `conConteudoL4dC` | Contentor | `conEcraL4dC` | Contentor vertical, desloca | F11.5 |
| `conL4dAreaTopo` | Contentor | `conConteudoL4dC` | Contentor horizontal | F11.5 |
| `lblL4dAreaTitulo` | Etiqueta | `conL4dAreaTopo` | Mostra If(gblL4dArea = "utilizadores"; "Utilizadores"; "A minha password") | F11.5 |
| `btnL4dAreaVoltar` | Botão | `conL4dAreaTopo` | Botão «‹ Pedidos»: abre scrL4Pedidos | F11.5 |
| `conL4dVistaUtilizadores` | Contentor | `conConteudoL4dC` | Contentor horizontal | F11.5 |
| `conL4dUtilLista` | Contentor | `conL4dVistaUtilizadores` | Contentor vertical | F11.5 |
| `btnL4dUtilNovo` | Botão | `conL4dUtilLista` | Botão «Novo utilizador»: muda locL4dUtil | F11.5 |
| `conL4dUtilCartao` | Contentor | `conL4dUtilLista` | Contentor vertical, caixa com contorno | F11.5 |
| `galL4dUtilizadores` | Galeria | `conL4dUtilCartao` | Galeria de Utilizadores | F11.5 |
| `lblL4dGUtilNome` | Etiqueta | `galL4dUtilizadores` | Mostra ThisItem.Nome & " · " & Text(ThisItem.Perfil) | F11.5 |
| `lblL4dGUtilEmail` | Etiqueta | `galL4dUtilizadores` | Mostra ThisItem.Email | F11.5 |
| `btnL4dGUtilEstado` | Botão | `galL4dUtilizadores` | Pílula decorativa If(!ThisItem.Ativo; "Inativo"; !IsBlank(ThisItem.… | F11.5 |
| `recL4dGUtilSeparador` | Retângulo | `galL4dUtilizadores` | Linha de separação | F11.5 |
| `conL4dUtilForm` | Contentor | `conL4dVistaUtilizadores` | Contentor vertical, caixa com contorno | F11.5 |
| `lblL4dUtilTitulo` | Etiqueta | `conL4dUtilForm` | Mostra If(IsBlank(locL4dUtil); "Novo utilizador"; locL4dUtil.Nome) | F11.5 |
| `lblL4dUtilNomeRot` | Etiqueta | `conL4dUtilForm` | Texto fixo «Nome» | F11.5 |
| `txtL4dUtilNome` | Caixa de texto | `conL4dUtilForm` | Entrada de texto: Nome do utilizador | F11.5 |
| `lblL4dUtilEmailRot` | Etiqueta | `conL4dUtilForm` | Texto fixo «Email» | F11.5 |
| `txtL4dUtilEmail` | Caixa de texto | `conL4dUtilForm` | Entrada de texto: Email do utilizador | F11.5 |
| `lblL4dUtilPerfilRot` | Etiqueta | `conL4dUtilForm` | Texto fixo «Perfil» | F11.5 |
| `drpL4dUtilPerfil` | Lista pendente | `conL4dUtilForm` | Escolha de Choices('Perfil (Utilizadores)') | F11.5 |
| `lblL4dUtilClienteRot` | Etiqueta | `conL4dUtilForm` | Texto fixo «Cliente associado» | F11.5 |
| `drpL4dUtilCliente` | Lista pendente | `conL4dUtilForm` | Escolha de Sort(Clientes; Nome) | F11.5 |
| `chkL4dUtilAtivo` | Caixa de verificação | `conL4dUtilForm` | Caixa de verificação «Ativo (pode entrar)» | F11.5 |
| `conL4dUtilAcoes` | Contentor | `conL4dUtilForm` | Contentor horizontal | F11.5 |
| `btnL4dUtilGuardar` | Botão | `conL4dUtilAcoes` | Botão «Guardar»: grava no Dataverse; muda locL4dMsgTipo, locL4dUtil | F11.5 |
| `btnL4dUtilDesbloquear` | Botão | `conL4dUtilAcoes` | Botão «Desbloquear»: grava no Dataverse; muda locL4dMsgTipo, locL4dUtil | F11.5 |
| `lblL4dUtilPassRot` | Etiqueta | `conL4dUtilForm` | Texto fixo «Definir a password (mínimo 8 caracteres)» | F11.5 |
| `txtL4dUtilPassword` | Caixa de texto | `conL4dUtilForm` | Entrada de texto (password): Nova password do utilizador | F11.5 |
| `btnL4dUtilDefinir` | Botão | `conL4dUtilForm` | Botão «Definir password»: chama o fluxo DAC2627_Utilizador_DefinirPassword; volta a ler os dados; muda locL4dMsgTipo, locL4dUtil | F11.5 |
| `conL4dVistaPassword` | Contentor | `conConteudoL4dC` | Contentor vertical, caixa com contorno | F11.5 |
| `lblL4dPassAtualRot` | Etiqueta | `conL4dVistaPassword` | Texto fixo «Password atual» | F11.5 |
| `txtL4dPassAtual` | Caixa de texto | `conL4dVistaPassword` | Entrada de texto (password): Password atual | F11.5 |
| `lblL4dPassNovaRot` | Etiqueta | `conL4dVistaPassword` | Texto fixo «Nova password (8 a 128 caracteres)» | F11.5 |
| `txtL4dPassNova` | Caixa de texto | `conL4dVistaPassword` | Entrada de texto (password): Nova password | F11.5 |
| `lblL4dPassConfirmaRot` | Etiqueta | `conL4dVistaPassword` | Texto fixo «Confirmar a nova password» | F11.5 |
| `txtL4dPassConfirma` | Caixa de texto | `conL4dVistaPassword` | Entrada de texto (password): Confirmar a nova password | F11.5 |
| `btnL4dPassMudar` | Botão | `conL4dVistaPassword` | Botão «Mudar password»: chama o fluxo DAC2627_Utilizador_DefinirPassword; muda locL4dMsgTipo | F11.5 |
| `conL4dCMensagem` | Contentor | ecrã | Contentor horizontal, raiz do ecrã | F11.5 |
| `icoL4dCMsgIcone` | Ícone | `conL4dCMensagem` | Ícone If(locL4dMsgTipo = "erro"; Warning; Check): decorativo | F11.5 |
| `lblL4dCMensagem` | Etiqueta | `conL4dCMensagem` | Mostra locL4dMsg | F11.5 |
| `icoL4dCFecharMsg` | Ícone | `conL4dCMensagem` | Ícone Cancel («Fechar mensagem»): muda locL4dMsg | F11.5 |
| `tmrL4dCMensagem` | Temporizador | ecrã | Temporizador de 5000 ms: muda locL4dMsg | F11.5 |
| `lblL4dCAnuncio` | Etiqueta | ecrã | Mostra locL4dMsg | F11.5 |

## Variáveis

As globais (`gbl`) definem-se com `Set` e valem em toda a app. As de contexto (`loc`) definem-se com `UpdateContext` ou com o terceiro argumento do `Navigate` e valem num só ecrã. As coleções (`col`) enchem-se com `ClearCollect`.

| Variável | Tipo | Definida em | Aparece nos ecrãs |
|---|---|---|---|
| `colL3Publicacoes` | coleção | `btnL3Carregar.OnSelect` | scrL3Detalhe, scrL3Lista |
| `colL3Utilizadores` | coleção | `btnL3Carregar.OnSelect` | scrL3Lista, scrL3Publicacao |
| `gblL1Nome` | global | `btnL1Saudar.OnSelect`, `btnL1Terminar.OnSelect` | scrL1Pedido, scrL1Saudacao |
| `gblL4Nivel` | global | `btnL4dEntrar.OnSelect`, `galInFichas.OnSelect` | scrInicio, scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `gblL4dArea` | global | `icoL4dCPassword.OnSelect`, `icoL4dCUtilizadores.OnSelect`, `icoL4dPassword.OnSelect`, `icoL4dUtilizadores.OnSelect` | scrL4Conta, scrL4Pedidos |
| `gblL4dSessao` | global | `btnL4dEntrar.OnSelect`, `btnL4dSair.OnSelect` | scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `locAcao` | de contexto | `btnL2ConfCancelar.OnSelect`, `btnL2ConfOk.OnSelect`, `btnL2Guardar.OnSelect`, `btnL2Remover.OnSelect` e mais 1 | scrL2Servicos |
| `locAviso` | de contexto | `btnL1Saudar.OnSelect`, `scrL1Pedido.OnVisible` | scrL1Pedido |
| `locL3ACarregar` | de contexto | `btnL3Carregar.OnSelect` | scrL3Lista |
| `locL3Erro` | de contexto | `btnL3Carregar.OnSelect` | scrL3Lista |
| `locL3Pub` | de contexto | `galL3Publicacoes.OnSelect (Navigate)`, `galL3PubsUtil.OnSelect (Navigate)` | scrL3Publicacao |
| `locL3Sel` | de contexto | `btnL3VerAutor.OnSelect (Navigate)`, `galL3Utilizadores.OnSelect (Navigate)` | scrL3Detalhe |
| `locL3Vista` | de contexto | `btnL3SepPub.OnSelect`, `btnL3SepUtil.OnSelect` | scrL3Lista |
| `locL4Acao` | de contexto | `btnL4EditarCliente.OnSelect`, `btnL4NovoCliente.OnSelect`, `btnL4NovoPedido.OnSelect`, `btnL4cEditar.OnSelect` e mais 2 | scrL4Pedidos |
| `locL4Cliente` | de contexto | `btnL4ConfOk.OnSelect`, `btnL4TodosPedidos.OnSelect`, `frmL4Cliente.OnSuccess`, `galL4Clientes.OnSelect` e mais 1 | scrL4Pedidos |
| `locL4Confirmar` | de contexto | `btnL4Cancelar.OnSelect`, `btnL4ConfCancelar.OnSelect`, `btnL4ConfOk.OnSelect`, `btnL4Guardar.OnSelect` e mais 3 | scrL4Pedidos |
| `locL4Modo` | de contexto | `btnL4Cancelar.OnSelect`, `btnL4ConfOk.OnSelect`, `btnL4EditarCliente.OnSelect`, `btnL4NovoCliente.OnSelect` e mais 7 | scrL4Pedidos |
| `locL4Msg` | de contexto | `btnL4ConfOk.OnSelect`, `btnL4EditarCliente.OnSelect`, `btnL4Guardar.OnSelect`, `btnL4NovoCliente.OnSelect` e mais 17 | scrL4Pedidos |
| `locL4MsgTipo` | de contexto | `btnL4ConfOk.OnSelect`, `btnL4Guardar.OnSelect`, `btnL4cReprocessar.OnSelect`, `btnL4dAprovar.OnSelect` e mais 9 | scrL4Pedidos |
| `locL4Painel` | de contexto | `btnL4ConfOk.OnSelect`, `btnL4NovoCliente.OnSelect`, `btnL4TodosPedidos.OnSelect`, `btnL4VoltarLista.OnSelect` e mais 3 | scrL4Pedidos |
| `locL4Pedido` | de contexto | `btnL4ConfOk.OnSelect`, `btnL4NovoPedido.OnSelect`, `btnL4cAtualizar.OnSelect`, `btnL4dAprovar.OnSelect` e mais 7 | scrL4Pedidos |
| `locL4Timer` | de contexto | `btnL4ConfOk.OnSelect`, `btnL4EditarCliente.OnSelect`, `btnL4Guardar.OnSelect`, `btnL4NovoCliente.OnSelect` e mais 17 | scrL4Pedidos |
| `locL4UltimaConf` | de contexto | `btnL4ConfOk.OnSelect`, `scrL4Pedidos.OnVisible` | scrL4Pedidos |
| `locL4Vista` | de contexto | `btnL4SepConcluidos.OnSelect`, `btnL4SepPendentes.OnSelect`, `btnL4SepTodos.OnSelect`, `btnL4cSepAuto.OnSelect` e mais 3 | scrL4Pedidos |
| `locL4bVista` | de contexto | `btnL4bVerTabela.OnSelect`, `btnL4bVoltarTexto.OnSelect`, `scrL4Complemento.OnVisible` | scrL4Complemento |
| `locL4cAguardar` | de contexto | `btnL4NovoPedido.OnSelect`, `btnL4cEditar.OnSelect`, `btnL4cReprocessar.OnSelect`, `btnL4cVoltar.OnSelect` e mais 4 | scrL4Pedidos |
| `locL4cTentativas` | de contexto | `btnL4cReprocessar.OnSelect`, `frmL4Pedido.OnSuccess`, `scrL4Pedidos.OnVisible`, `tmrL4cEstado.OnTimerEnd` | scrL4Pedidos |
| `locL4cValorTeste` | de contexto | `btnL4Cancelar.OnSelect`, `btnL4NovoPedido.OnSelect`, `btnL4cEditar.OnSelect`, `btnL4cTeste100.OnSelect` e mais 5 | scrL4Pedidos |
| `locL4dAEntrar` | de contexto | `btnL4dEntrar.OnSelect`, `scrL4Entrar.OnVisible` | scrL4Entrar |
| `locL4dMsg` | de contexto | `btnL4dEntrar.OnSelect`, `btnL4dPassMudar.OnSelect`, `btnL4dUtilDefinir.OnSelect`, `btnL4dUtilDesbloquear.OnSelect` e mais 9 | scrL4Conta, scrL4Entrar |
| `locL4dMsgTipo` | de contexto | `btnL4dEntrar.OnSelect`, `btnL4dPassMudar.OnSelect`, `btnL4dUtilDefinir.OnSelect`, `btnL4dUtilDesbloquear.OnSelect` e mais 3 | scrL4Conta, scrL4Entrar |
| `locL4dTimer` | de contexto | `btnL4dEntrar.OnSelect`, `btnL4dPassMudar.OnSelect`, `btnL4dUtilDefinir.OnSelect`, `btnL4dUtilDesbloquear.OnSelect` e mais 9 | scrL4Conta, scrL4Entrar |
| `locL4dUtil` | de contexto | `btnL4dUtilDefinir.OnSelect`, `btnL4dUtilDesbloquear.OnSelect`, `btnL4dUtilGuardar.OnSelect`, `btnL4dUtilNovo.OnSelect` e mais 4 | scrL4Conta |
| `locMsg` | de contexto | `btnL2ConfOk.OnSelect`, `btnL2Editar.OnSelect`, `btnL2Novo.OnSelect`, `btnL2Remover.OnSelect` e mais 5 | scrL2Servicos |
| `locMsgTipo` | de contexto | `btnL2ConfOk.OnSelect`, `frmL2Servico.OnFailure`, `frmL2Servico.OnSuccess`, `scrL2Servicos.OnVisible` | scrL2Servicos |
| `locSel` | de contexto | `btnL2ConfOk.OnSelect`, `btnL2VoltarLista.OnSelect`, `frmL2Servico.OnSuccess`, `galL2Servicos.OnSelect` e mais 1 | scrL2Servicos |
| `locTentou` | de contexto | `btnL2Cancelar.OnSelect`, `btnL2Editar.OnSelect`, `btnL2Guardar.OnSelect`, `btnL2Novo.OnSelect` e mais 3 | scrL2Servicos |
| `locTimer` | de contexto | `btnL2ConfOk.OnSelect`, `btnL2Editar.OnSelect`, `btnL2Novo.OnSelect`, `btnL2Remover.OnSelect` e mais 4 | scrL2Servicos |
| `locUltimaAcao` | de contexto | `btnL2ConfOk.OnSelect`, `scrL2Servicos.OnVisible` | scrL2Servicos |

## Fórmulas com nome (App.Formulas)

Cores, versão e textos comuns. As cores só se usam por estes nomes (lint DAC201); os contrastes estão em `docs/paleta.md`.

| Nome | Valor | Usos |
|---|---|---:|
| `nfAzul` | `ColorValue("#1F4E79"); // Paleta da APP DAC2627: todas as c…` | 225 |
| `nfAzulFundo` | `ColorValue("#DCE7F2"); // Verde (madeira): sucesso e PaaS.…` | 23 |
| `nfVerdeTexto` | `ColorValue("#1F5E43")` | 28 |
| `nfVerdeFundo` | `ColorValue("#DDEFE6"); // Vermelho (fogo): erros e ações de…` | 17 |
| `nfVermelhoTexto` | `ColorValue("#8E1F25")` | 33 |
| `nfVermelhoFundo` | `ColorValue("#FBE9EA"); // Âmbar e laranja (terra quente): a…` | 17 |
| `nfAmbarFundo` | `ColorValue("#FFF4DB")` | 16 |
| `nfLaranja` | `ColorValue("#8A3B0F")` | 6 |
| `nfLaranjaFundo` | `ColorValue("#FBEBD9"); // Neutros (terra e metal): fundos,…` | 2 |
| `nfSuperficie` | `ColorValue("#F7F8F9")` | 21 |
| `nfTexto` | `ColorValue("#1E2A33")` | 139 |
| `nfTextoSuave` | `ColorValue("#46525C")` | 92 |
| `nfLinha` | `ColorValue("#E4E7EA")` | 36 |
| `nfLinhaForte` | `ColorValue("#C5CBD1")` | 12 |
| `nfBorda` | `ColorValue("#7D8993")` | 80 |
| `nfDesativado` | `ColorValue("#A6A6A6")` | 1 |
| `nfVeu` | `RGBA(30, 42, 51, 0.55); // Versão mostrada no rodapé do ecr…` | 2 |

## Funções Power Fx usadas

| Função | O que faz | Ecrãs onde aparece |
|---|---|---|
| `And` | e lógico | scrL2Servicos, scrL4Pedidos |
| `Back` | volta ao ecrã anterior | scrL1Pedido, scrL1Saudacao, scrL3Detalhe, scrL3Publicacao |
| `Blank` | valor vazio | scrL1Saudacao, scrL2Servicos, scrL4Conta, scrL4Pedidos |
| `Char` | carácter pelo código (Char(10) é a mudança de linha) | scrL3Lista, scrL4Complemento, scrL4Pedidos |
| `Choices` | opções de uma coluna de escolha | scrL2Servicos, scrL4Conta, scrL4Pedidos |
| `ClearCollect` | esvazia e enche uma coleção | scrL3Lista |
| `Coalesce` | primeiro valor não vazio | scrL3Detalhe, scrL3Lista, scrL4Pedidos |
| `CountRows` | conta as linhas de uma tabela | scrL2Servicos, scrL3Detalhe, scrL3Lista, scrL4Pedidos |
| `DataSourceInfo` | informação sobre a fonte de dados | scrL2Servicos, scrL4Pedidos |
| `Defaults` | registo novo com os valores por omissão | scrL4Conta |
| `EditForm` | põe um formulário a editar | scrL2Servicos, scrL4Pedidos |
| `Error` | provoca um erro | scrL3Lista |
| `Filter` | linhas que cumprem condições | scrL2Servicos, scrL3Detalhe, scrL3Lista, scrL4Pedidos |
| `First` | primeira linha | scrL4Pedidos |
| `GUID` | identificador único a partir de texto | scrL4Pedidos |
| `If` | escolhe pelo primeiro teste verdadeiro | scrInicio, scrL1BoasVindas, scrL1Pedido, scrL1Saudacao, scrL2Servicos, scrL3Detalhe, scrL3Lista, scrL3Publicacao, scrL4Complemento, scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `IfError` | apanha erros e dá alternativa | scrL2Servicos, scrL3Lista, scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `Index` | linha pela posição | scrL4Pedidos |
| `IsBlank` | testa se está vazio | scrL1Pedido, scrL1Saudacao, scrL2Servicos, scrL3Detalhe, scrL3Lista, scrL3Publicacao, scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `IsEmpty` | testa se a tabela não tem linhas | scrL2Servicos, scrL3Lista, scrL4Pedidos |
| `IsMatch` | testa um texto contra um padrão | scrL4Conta |
| `Last` | última linha | scrL4Pedidos |
| `Left` | primeiros caracteres | scrL3Detalhe, scrL3Lista, scrL3Publicacao, scrL4Pedidos |
| `Len` | número de caracteres | scrL3Lista, scrL4Conta, scrL4Pedidos |
| `LookUp` | primeira linha que cumpre a condição | scrL2Servicos, scrL3Lista, scrL3Publicacao, scrL4Conta, scrL4Pedidos |
| `Lower` | texto em minúsculas | scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `Max` | o maior valor | scrL4Complemento, scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `Min` | o menor valor | scrL1BoasVindas, scrL1Pedido, scrL1Saudacao, scrL2Servicos, scrL3Detalhe, scrL3Lista, scrL3Publicacao, scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `Navigate` | muda de ecrã | scrInicio, scrL1BoasVindas, scrL1Pedido, scrL1Saudacao, scrL2Servicos, scrL3Detalhe, scrL3Lista, scrL3Publicacao, scrL4Complemento, scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `NewForm` | põe um formulário a criar | scrL2Servicos, scrL4Pedidos |
| `Now` | data e hora atuais | scrL4Conta |
| `Patch` | cria ou altera um registo | scrL4Conta, scrL4Pedidos |
| `Refresh` | volta a ler a fonte de dados | scrL4Conta, scrL4Pedidos |
| `Remove` | apaga um registo | scrL2Servicos, scrL4Pedidos |
| `Reset` | repõe o valor inicial de um controlo | scrL1Pedido, scrL3Lista, scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `ResetForm` | repõe um formulário | scrL2Servicos, scrL4Pedidos |
| `RoundDown` | arredonda para baixo | scrL2Servicos, scrL4Pedidos |
| `Select` | faz como se o controlo fosse tocado | scrInicio, scrL2Servicos, scrL3Detalhe, scrL3Lista, scrL4Conta, scrL4Pedidos |
| `Set` | define uma variável global | scrInicio, scrL1Pedido, scrL1Saudacao, scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `ShowColumns` | fica só com algumas colunas | scrL3Lista |
| `Sort` | ordena uma tabela | scrL2Servicos, scrL3Detalhe, scrL3Lista, scrL4Conta, scrL4Pedidos |
| `Split` | parte um texto numa tabela | scrL4Pedidos |
| `StartsWith` | testa o início de um texto | scrL2Servicos, scrL4Pedidos |
| `SubmitForm` | grava um formulário | scrL2Servicos, scrL4Pedidos |
| `Substitute` | troca partes de um texto | scrL3Lista |
| `Switch` | escolhe pelo valor | scrInicio, scrL2Servicos, scrL3Detalhe, scrL4Pedidos |
| `Table` | tabela escrita na fórmula | scrInicio, scrL3Lista |
| `Text` | valor como texto, com formato | scrL2Servicos, scrL4Conta, scrL4Pedidos |
| `Today` | data de hoje | scrL4Pedidos |
| `Trim` | tira espaços a mais | scrL1Pedido, scrL2Servicos, scrL3Lista, scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `Ungroup` | desfaz agrupamentos | scrL3Lista |
| `UpdateContext` | define variáveis de contexto do ecrã | scrL1Pedido, scrL2Servicos, scrL3Lista, scrL4Complemento, scrL4Conta, scrL4Entrar, scrL4Pedidos |
| `Upper` | texto em maiúsculas | scrL3Detalhe, scrL3Lista, scrL3Publicacao, scrL4Pedidos |
| `Value` | texto como número | scrL4Pedidos |
| `With` | dá nome a valores dentro de uma fórmula | scrL2Servicos, scrL3Lista, scrL3Publicacao, scrL4Conta, scrL4Entrar, scrL4Pedidos |

## Fontes de dados e fluxos

| Nome | Tipo | Nota |
|---|---|---|
| Cloud Service | Tabela Dataverse | Escolher a de nome lógico mcsft_cloudservice. O ambiente tem outra com o mesmo nome a mostrar (mcsft_cloudservice1). |
| Clientes | Tabela Dataverse | Tabela Cliente, nome lógico dac_cliente. |
| Pedidos | Tabela Dataverse | Tabela Pedido, nome lógico dac_pedido. |
| JSONPlaceholderDAC | Conector personalizado | Usar a ligação existente do conector da solução DAC2627 (não o Defaulttitle do Lab 3). |
| DAC2627_Pedido_Reprocessar | Fluxo Power Automate | Fluxo instantâneo da Ficha 04 · Melhoramento (gatilho Power Apps V2, entrada PedidoId). |
| Utilizadores | Tabela Dataverse | Tabela Utilizador (dac_utilizador) da Ficha 04 · Revisão. Na pesquisa aparece como Utilizadores. |
| DAC2627_Utilizador_Entrar | Fluxo Power Automate | Ficha 04 · Revisão, entradas Email e Password. |
| DAC2627_Utilizador_DefinirPassword | Fluxo Power Automate | Ficha 04 · Revisão, entradas Token, UtilizadorId, NovaPassword e PasswordAtual. |
| DAC2627_Pedido_Decidir | Fluxo Power Automate | Ficha 04 · Revisão, entradas Token, PedidoId, Acao e Comentario. |
