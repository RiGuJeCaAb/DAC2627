# Instruções para o Claude Code

Este repositório é o código extraído de uma Canvas app do Power Apps (APP DAC2627). A app corre no Power Apps Studio; aqui há ferramentas de verificação (`tools/dac`), testes (`tests/`) e CI. O trabalho é **ler, analisar e alterar** os ficheiros `.pa.yaml` e levá-los ao Studio com `python -m tools.dac colar`.

## Antes de dar uma alteração por terminada

```bash
make verificar        # validar + formatar --verificar + lint --estrito + paleta + inventario + pytest
python -m tools.dac colar --estrito   # blocos para o Studio, ORDEM.md e verificação das fontes contra a exportação
```

- Alterações em muitos controlos: escrever uma migração idempotente em `tools/migracoes/mNNN_*.py` (modelo: `m001`). Não editar à mão dezenas de ocorrências.
- Escrever `.pa.yaml` sempre através de `tools/dac/yamlio.py` (preserva o formato do Studio byte a byte). Para ler, as ferramentas usam `yamlio.ler_tolerante` (aceita tabuladores dentro de valores, como o Studio, e devolve as linhas para aviso). Uma migração usa `yamlio.ler`, estrito, porque reescreve o ficheiro. Converter fórmulas para PT com `tools/dac/pafx.py`, nunca com substituições de texto: estas trocam `,` também dentro de `"..."`.
- `docs/inventario.md` e `docs/paleta.md` são gerados: `make docs`.
- Para levar alterações ao Studio: `python -m tools.dac colar` e seguir `build/colar/ORDEM.md`. Não indicar outra ordem de colagem à mão: a ordem é calculada em `tools/dac/ordem.py` (quem envia variáveis por `Navigate` entra antes de quem as recebe). Uma fonte de dados nova entra em `dac.yaml › fontes` (há um teste que o exige).
- Uma regra nova do lint precisa de um teste em `tests/test_lint.py` e de uma linha em `docs/regras-lint.md` (há um teste que o exige).
- Uma exceção ao lint vai para `dac.yaml` com `motivo`.

## Onde está o quê

- `src/screens/*.pa.yaml` e `src/app/App.pa.yaml`: a fonte a analisar (Power Fx em YAML, esquema oficial em https://go.microsoft.com/fwlink/?linkid=2304907).
- `dataverse/schema.md`: colunas e escolhas das tabelas usadas nas Fichas 02 e 04 (Cloud Service, Cliente, Pedido).
- `connector/openapi.json`: o conector personalizado da Ficha 03 (`JSONPlaceholderDAC.ListarUtilizadores`, `ListarPublicacoes`).
- `msapp/` e `solution/`: exportação em bruto. Não editar; atualizar só com `python -m tools.dac sincronizar <zip>`.
- `tools/legacy/gen.py`: obsoleto, já não gera o estado de `src/`. Não correr.
- `docs/alm.md`: o ciclo Studio ⇄ git; `docs/regras-lint.md`: códigos DACnnn.

## Convenções da app

- Nos ficheiros `.pa.yaml` as fórmulas estão no formato invariante: argumentos separados por `,` e encadeamento com `;`. O Studio em português mostra-as com `;` e `;;`, e converte ao colar.
- Nomes: prefixo do tipo (`scr`, `con`, `gal`, `lbl`, `btn`, `txt`, `drp`, `cmb`, `dte`, `chk`, `ico`, `frm`, `tmr`, `rec`) + ficha (`In`, `L1`, `L2`, `L3`, `L4`; o complemento da Ficha 04 usa `L4b`) + função. Ex.: `galL2Servicos`, `txtL4CliNome`.
- Variáveis: `gbl*` globais (`Set`), `loc*` de contexto (`UpdateContext`), `col*` coleções.
- Cores só pelas fórmulas nomeadas `nf*` em `App.Formulas` (22 tokens; o lint DAC201 falha com qualquer `ColorValue`/`RGBA` fora dali). Erro: `nfVermelho`/`nfVermelhoTexto`/`nfVermelhoFundo`; aviso: `nfAmbar`/`nfAmbarFundo`; sucesso: `nfVerde`/`nfVerdeTexto`/`nfVerdeFundo`; contornos de entradas: `nfBorda`. Lista completa e contrastes em `docs/paleta.md`. Um par texto/fundo novo entra em `tools/dac/cores.py:PARES`.
- Acessibilidade: `TabIndex = 0` em tudo o que é interativo. Nos decorativos não se escreve `TabIndex` nem `AccessibleLabel`: ausentes valem `-1` e `""`. `AccessibleLabel` com texto em entradas, galerias e ícones com ação. `FocusedBorderThickness = 2` nas etiquetas fora de galerias, incluindo as dos formulários.
- Layout: contentores com AutoLayout (`GroupContainer@1.5.0`). Responsividade por `<ecrã>.Size` (Small < 600, Medium 600–900, Large 900–1200). Regras no manual, secção A10.

## Pontos já decididos (não reverter sem razão)

- `galL2Servicos.Items` usa `If(... = "Todos"; ...)` com dois `Filter` delegáveis e compara a escolha com `LookUp(Choices('Cloud Service'.'Service Model'); ...)`. Nunca `Text('Service Model')` dentro do `Filter`: deixa de ser delegável e passa a ver só os primeiros 500 registos.
- `lblL2Contagem` conta com `CountRows(Filter(...))` no Dataverse, porque `galL2Servicos.AllItems` só tem as linhas já carregadas (100 de cada vez). Na Ficha 03, `lblL3Contagem` e `lblL3TituloPubs` também contam sobre as coleções (v1.1.0), à custa de repetir o filtro da galeria.
- Ficha 03: duas caixas de teste visíveis de propósito, para o professor. `chkL3SimularFalha` faz o `btnL3Carregar` lançar `Error({Kind: ErrorKind.Network, ...})`, apanhado pelo `IfError` (faixa `conL3Erro`); `chkL3SimularVazio` deixa as coleções vazias e mostra a faixa de aviso `conL3Aviso` (âmbar, `nfAmbar`/`nfAmbarFundo`, com `lblL3Vazio` e o botão Atualizar), equivalente ao `lblSemDados` da app da aula. Erro a vermelho, aviso a âmbar. As caixas só preparam o teste: o efeito aparece ao premir Atualizar ou Tentar novamente (sem `OnCheck`).
- Ficha 03 Detalhe: os cartões dentro de `conL3Blocos` (contentor com `LayoutWrap`) usam `AlignInContainer.Start`; com `Stretch` ficavam com a altura da linha e cortavam o texto. Blocos de altura fixa têm `LayoutMinHeight` igual à altura, e o cartão branco desloca (`LayoutOverflow.Scroll`) em vez de encolher o conteúdo.
- Textos da API com quebras de linha (`body`) mostrados numa só linha passam por `Substitute(..., Char(10), " ")`.
- Ficha 04: o separador Todos de `galL4Pedidos` mostra só pedidos ativos (`Estado = 'Estado (Pedidos)'.Ativo`), como a contagem do `btnL4SepTodos`. Pendentes e Concluídos usam as vistas do Dataverse no `Filter`.
- Formulários clássicos: a largura dos cartões é por fórmula, para ficarem um por linha no telemóvel. Ficha 04 por `scrL4Pedidos.Size` (cliente 1/2/3 por linha, pedido 1/2); Ficha 02 pela largura do formulário, `If(Parent.Width < 560, Parent.Width - 1, RoundDown(Parent.Width / 2, 0) - 1)`, porque no tablet o painel ocupa só metade do ecrã. Descrição sempre `Parent.Width - 1`.
- Complemento da Ficha 04 (ponto 8 do Lab 4): ecrã próprio `scrL4Complemento`, aberto pelo quinto cartão do ecrã inicial («Origens de dados»). Não é um botão dentro da Ficha 04. Duas vistas por `locL4bVista`: texto (o que é, modelo de serviço cloud, a favor, contra) e tabela com os sete critérios do enunciado e dois da perspetiva cloud (modelo de serviço, custo), aberta por um botão no fim do texto. Cada afirmação tem fonte Microsoft em `fontes`, e um teste exige que todas as fontes listadas sejam citadas. Textos com «: » no YAML vão entre aspas simples.
- O texto do ponto 8 vive só em `conteudo/ponto8.yaml`. A `m004` gera o ecrã e `python -m tools.ponto8` gera o `.docx` para o docente. Mudar o texto lá e gerar os dois, nunca editar um só.
- Ficha 02: em modo de leitura o painel mostra a ficha `conL2Ficha` (cartões Fornecedor, Modelo de serviço e Estado com as cores das etiquetas da lista, descrição e «Quem gere o quê»), e o `frmL2Servico` só aparece a criar e a editar, com os rótulos em português (m005). Os cartões ficam lado a lado só com `conL2Ficha.Width >= 720` e não esticam na vertical: esticados, o contorno de baixo ficava cortado.
- Ecrãs com muito texto: etiquetas com `AutoHeight` num contentor com `LayoutOverflow.Scroll`, e linhas de tabela com `Height = Max(<alturas das etiquetas>)`. Nada de galerias com `TemplateSize` fixo para texto de comprimento variável.
- Nas partes A a G do Manual o aluno escreve as fórmulas à mão. O `dac colar` é só do repositório (parte H).
- A tabela `mcsft_cloudservice1` fica no ambiente: pertence à solução DACCCMB2426Final e tem dados (decisão do utilizador).
- Doze pílulas decorativas com `TabIndex = -1` e exceção DAC302 em `dac.yaml`: `btnL2ItemModelo`, `btnL3Iniciais`, `btnL3bIniciais`, `btnL3PubIniciais`, `btnL4PedEstado`, `btnL4cTratamento`, `btnL4cGTratamento`, `btnL4dGDecisao`, `btnL4dGUtilEstado`, `btnL4dDetEstado`, `btnL4dIniciais`, `btnL4dPerfil`.
- O Verificador marca qualquer controlo com `TabIndex = -1` fora de galerias com `Select(Parent)`: na v1.4.0, 211 avisos de tabulação e 8 de `AccessibleLabel` em decorativos ficam de propósito (`docs/alm.md`). Não dar `TabIndex = 0` a etiquetas decorativas para os limpar.
- O Studio apaga ao guardar os valores por omissão (`TabIndex -1` e `Size 13` em etiquetas, `AccessibleLabel ""` e `TabIndex -1` em ícones e retângulos, `DropShadow.Light` em contentores). Não os escrever: `yamlio.OMISSAO` e o lint DAC504 tratam disso. Uma propriedade ausente vale o valor por omissão.
- A exportação da solução leva a versão **publicada**. Depois de colar: guardar, publicar, exportar, `dac sincronizar`, `dac deriva`. A ordem de colagem está em `build/colar/ORDEM.md` (gerado por `dac colar`, calculado em `tools/dac/ordem.py`).
- Ficha 04 · Melhoramento (aula 7): ecrã `scrL4Melhoramento`, prefixo `L4c`, aberto pelo sexto cartão. A app só grava o pedido e consulta o estado (`tmrL4cEstado`, 3 s, 20 vezes): quem classifica é o fluxo `DAC2627_Pedido_Classificar`. O único fluxo chamado pela app é `DAC2627_Pedido_Reprocessar` (Power Apps V2), que responde logo. As colunas de processamento são escritas só pelos fluxos. Fluxos e colunas em `dataverse/fluxos.md` e `dataverse/schema.md`. O conector Aprovações está bloqueado pela política do tenant. Desde a v1.6.0 o email só avisa (`DAC2627_Pedido_Notificar`) e a decisão é tomada na Ficha 04 · Revisão.
- Ficha 04 · Revisão (v1.6.0): ecrãs `scrL4Entrar` e `scrL4Revisao`, prefixo `L4d`, abertos pelo sétimo cartão. A password nunca fica na app nem no Dataverse: vai do `txtL4dPassword` para o fluxo `DAC2627_Utilizador_Entrar`, que a verifica no serviço de hash (`azure/servico-hash/`, App Service F1, PBKDF2-SHA256 com 600 000 iterações), e a caixa é limpa logo a seguir. A sessão é um testemunho de 64 carateres válido 8 horas, em `gblL4dSessao`. Os fluxos que alteram dados (`DefinirPassword`, `Decidir`) leem o perfil da sessão no Dataverse, nunca da app. O Gestor propõe, o Admin decide, o Cliente regista e acompanha. Não é uma Azure Function porque a subscrição de estudante não autoriza `Microsoft.Storage`. O login dentro da app organiza o ecrã: a segurança dos dados é das funções de segurança do Dataverse. A chave do serviço está só na definição `DAC_CHAVE_API` da aplicação web e na ligação do conector, nunca no repositório.
- Ficha 04 · Revisão, layout (23/11/2026, a pedido do utilizador): nada de cumprimentos («Olá») nem frases sobre o perfil. Quem entrou aparece no cabeçalho (`btnL4dIniciais`, `lblL4dQuem`, `btnL4dPerfil`, Sair). As vistas abrem-se num menu lateral (`galL4dMenu`), que no telemóvel é `galL4dMenuCompacto`, e o atalho para a Ficha 04 fica no fundo do menu. Na revisão, segmentado com contagens, lista em linhas com barra de estado e detalhe em pares rótulo/valor (`_linha_info`) com estado vazio. Separadores de 1 px são contentores vazios (`_linha`), porque retângulos dentro de contentores ainda não estão na exportação (DAC405).
- Contentores interiores com `DropShadow.None`; filhos de altura fixa com `FillPortions = 0`; etiquetas e ícones dentro de galerias com `OnSelect = Select(Parent)`.

## Sugestões de análise (em aberto)

1. Filtros duplicados entre galerias e contagens (`galL2Servicos.Items`/`lblL2Contagem`, `galL3Publicacoes.Items`/`lblL3Contagem`): candidatos a funções definidas pelo utilizador em `App.Formulas`, confirmando primeiro no Studio que a delegação se mantém.
2. Tamanhos de letra e espaçamentos como tokens (`nfTam*`), como já se faz com as cores.
3. Delegação e desempenho com tabelas acima de 500 registos.
4. Verificador na v1.4.0: 219 avisos (211 de tabulação, 8 de `AccessibleLabel`), todos de controlos decorativos com `TabIndex = -1` ou `AccessibleLabel ""` (ver `docs/alm.md`). Sobre a v1.2.0, mais 64 das etiquetas de texto do `scrL4Complemento` e 13 da ficha do serviço da Ficha 02 (`conL2Ficha`). Cores literais: zero.

Ao propor alterações, mostre o excerto YAML antes e depois e indique o ecrã e o controlo. Responda em português de Portugal.
