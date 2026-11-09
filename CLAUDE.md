# Instruções para o Claude Code

Este repositório é o código extraído de uma Canvas app do Power Apps (APP DAC2627). Não há build nem testes automáticos: a app corre no Power Apps Studio. O trabalho aqui é **ler, analisar e propor alterações** aos ficheiros `.pa.yaml`.

## Onde está o quê

- `src/screens/*.pa.yaml` e `src/app/App.pa.yaml`: a fonte a analisar (Power Fx em YAML, esquema oficial em https://go.microsoft.com/fwlink/?linkid=2304907).
- `dataverse/schema.md`: colunas e escolhas da tabela usada na Ficha 02.
- `connector/openapi.json`: o conector personalizado da Ficha 03 (`JSONPlaceholderDAC.ListarUtilizadores`, `ListarPublicacoes`).
- `msapp/` e `solution/`: exportação em bruto. Não editar; servem só de referência.

## Convenções da app

- Nos ficheiros `.pa.yaml` as fórmulas estão no formato invariante: argumentos separados por `,` e encadeamento com `;`. O Studio em português mostra-as com `;` e `;;`, e converte ao colar.
- Nomes: prefixo do tipo (`scr`, `con`, `gal`, `lbl`, `btn`, `txt`, `drp`, `ico`, `frm`, `tmr`, `rec`) + ficha (`In`, `L1`, `L2`, `L3`) + função. Ex.: `galL2Servicos`.
- Variáveis: `gbl*` globais (`Set`), `loc*` de contexto (`UpdateContext`), `col*` coleções.
- Cores só pelas fórmulas nomeadas `nf*` em `App.Formulas` (paleta: `nfAzul #1F4E79`, `nfFundo #F6F4EF`, `nfVermelho`/`nfVermelhoFundo` para erros, `nfAmbar #9A5B00`/`nfAmbarFundo #FFF4DB` para avisos, ...).
- Layout: contentores com AutoLayout (`GroupContainer@1.5.0`). Responsividade por `<ecrã>.Size` (Small < 600, Medium 600–900, Large 900–1200). Regras no manual, secção A10.

## Pontos já decididos (não reverter sem razão)

- `galL2Servicos.Items` usa `If(... = "Todos"; ...)` com dois `Filter` delegáveis e compara a escolha com `LookUp(Choices('Cloud Service'.'Service Model'); ...)`. Nunca `Text('Service Model')` dentro do `Filter`: deixa de ser delegável e passa a ver só os primeiros 500 registos.
- `lblL2Contagem` conta com `CountRows(Filter(...))` no Dataverse, porque `galL2Servicos.AllItems` só tem as linhas já carregadas (100 de cada vez).
- Ficha 03: duas caixas de teste visíveis de propósito, para o professor. `chkL3SimularFalha` faz o `btnL3Carregar` lançar `Error({Kind: ErrorKind.Network, ...})`, apanhado pelo `IfError` (faixa `conL3Erro`); `chkL3SimularVazio` deixa as coleções vazias e mostra a faixa de aviso `conL3Aviso` (âmbar, `nfAmbar`/`nfAmbarFundo`, com `lblL3Vazio` e o botão Atualizar), equivalente ao `lblSemDados` da app da aula. Erro a vermelho, aviso a âmbar. As caixas só preparam o teste: o efeito aparece ao premir Atualizar ou Tentar novamente (sem `OnCheck`).
- Ficha 03 Detalhe: os cartões dentro de `conL3Blocos` (contentor com `LayoutWrap`) usam `AlignInContainer.Start`; com `Stretch` ficavam com a altura da linha e cortavam o texto. Blocos de altura fixa têm `LayoutMinHeight` igual à altura, e o cartão branco desloca (`LayoutOverflow.Scroll`) em vez de encolher o conteúdo.
- Textos da API com quebras de linha (`body`) mostrados numa só linha passam por `Substitute(..., Char(10), " ")`.
- Contentores interiores com `DropShadow.None`; filhos de altura fixa com `FillPortions = 0`; etiquetas e ícones dentro de galerias com `OnSelect = Select(Parent)`.

## Sugestões de análise

1. Fórmulas duplicadas entre `galL2Servicos.Items` e `lblL2Contagem` (candidatas a uma fórmula nomeada em `App.Formulas`).
2. Acessibilidade: o verificador do Studio aponta cerca de 150 avisos (sobretudo `AccessibleLabel` e ordem de tabulação).
3. Tratamento de erros da Ficha 03 (`IfError`, estados de carregamento, botão Atualizar, caixa `chkL3SimularFalha`).
4. Consistência de nomes e de tamanhos de letra entre ecrãs.
5. Delegação e desempenho com tabelas acima de 500 registos.

Ao propor alterações, mostre o excerto YAML antes e depois e indique o ecrã e o controlo. Responda em português de Portugal.
