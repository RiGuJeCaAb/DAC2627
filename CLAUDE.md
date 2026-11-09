# Instruções para o Claude Code

Este repositório é o código extraído de uma Canvas app do Power Apps (APP DAC2627). A app corre no Power Apps Studio; aqui há ferramentas de verificação (`tools/dac`), testes (`tests/`) e CI. O trabalho é **ler, analisar e alterar** os ficheiros `.pa.yaml` e levá-los ao Studio com `python -m tools.dac colar`.

## Antes de dar uma alteração por terminada

```bash
make verificar        # validar + formatar --verificar + lint --estrito + paleta + inventario + pytest
```

- Alterações em muitos controlos: escrever uma migração idempotente em `tools/migracoes/mNNN_*.py` (modelo: `m001`). Não editar à mão dezenas de ocorrências.
- Escrever `.pa.yaml` sempre através de `tools/dac/yamlio.py` (preserva o formato do Studio byte a byte). Converter fórmulas para PT com `tools/dac/pafx.py`, nunca com substituições de texto: estas trocam `,` também dentro de `"..."`.
- `docs/inventario.md` e `docs/paleta.md` são gerados: `make docs`.
- Uma regra nova do lint precisa de um teste em `tests/test_lint.py` e de uma linha em `docs/regras-lint.md` (há um teste que o exige).
- Uma exceção ao lint vai para `dac.yaml` com `motivo`.

## Onde está o quê

- `src/screens/*.pa.yaml` e `src/app/App.pa.yaml`: a fonte a analisar (Power Fx em YAML, esquema oficial em https://go.microsoft.com/fwlink/?linkid=2304907).
- `dataverse/schema.md`: colunas e escolhas da tabela usada na Ficha 02.
- `connector/openapi.json`: o conector personalizado da Ficha 03 (`JSONPlaceholderDAC.ListarUtilizadores`, `ListarPublicacoes`).
- `msapp/` e `solution/`: exportação em bruto. Não editar; atualizar só com `python -m tools.dac sincronizar <zip>`.
- `tools/legacy/gen.py`: obsoleto, já não gera o estado de `src/`. Não correr.
- `docs/alm.md`: o ciclo Studio ⇄ git; `docs/regras-lint.md`: códigos DACnnn.

## Convenções da app

- Nos ficheiros `.pa.yaml` as fórmulas estão no formato invariante: argumentos separados por `,` e encadeamento com `;`. O Studio em português mostra-as com `;` e `;;`, e converte ao colar.
- Nomes: prefixo do tipo (`scr`, `con`, `gal`, `lbl`, `btn`, `txt`, `drp`, `ico`, `frm`, `tmr`, `rec`) + ficha (`In`, `L1`, `L2`, `L3`) + função. Ex.: `galL2Servicos`.
- Variáveis: `gbl*` globais (`Set`), `loc*` de contexto (`UpdateContext`), `col*` coleções.
- Cores só pelas fórmulas nomeadas `nf*` em `App.Formulas` (22 tokens; o lint DAC201 falha com qualquer `ColorValue`/`RGBA` fora dali). Erro: `nfVermelho`/`nfVermelhoTexto`/`nfVermelhoFundo`; aviso: `nfAmbar`/`nfAmbarFundo`; sucesso: `nfVerde`/`nfVerdeTexto`/`nfVerdeFundo`; contornos de entradas: `nfBorda`. Lista completa e contrastes em `docs/paleta.md`. Um par texto/fundo novo entra em `tools/dac/cores.py:PARES`.
- Acessibilidade: `TabIndex` explícito (0 interativo, -1 decorativo), `AccessibleLabel` em entradas, galerias e ícones (`""` só em decorativos), `FocusedBorderThickness = 2` nas etiquetas.
- Layout: contentores com AutoLayout (`GroupContainer@1.5.0`). Responsividade por `<ecrã>.Size` (Small < 600, Medium 600–900, Large 900–1200). Regras no manual, secção A10.

## Pontos já decididos (não reverter sem razão)

- `galL2Servicos.Items` usa `If(... = "Todos"; ...)` com dois `Filter` delegáveis e compara a escolha com `LookUp(Choices('Cloud Service'.'Service Model'); ...)`. Nunca `Text('Service Model')` dentro do `Filter`: deixa de ser delegável e passa a ver só os primeiros 500 registos.
- `lblL2Contagem` conta com `CountRows(Filter(...))` no Dataverse, porque `galL2Servicos.AllItems` só tem as linhas já carregadas (100 de cada vez). Na Ficha 03, `lblL3Contagem` e `lblL3TituloPubs` também contam sobre as coleções (v1.1.0), à custa de repetir o filtro da galeria.
- Ficha 03: duas caixas de teste visíveis de propósito, para o professor. `chkL3SimularFalha` faz o `btnL3Carregar` lançar `Error({Kind: ErrorKind.Network, ...})`, apanhado pelo `IfError` (faixa `conL3Erro`); `chkL3SimularVazio` deixa as coleções vazias e mostra a faixa de aviso `conL3Aviso` (âmbar, `nfAmbar`/`nfAmbarFundo`, com `lblL3Vazio` e o botão Atualizar), equivalente ao `lblSemDados` da app da aula. Erro a vermelho, aviso a âmbar. As caixas só preparam o teste: o efeito aparece ao premir Atualizar ou Tentar novamente (sem `OnCheck`).
- Ficha 03 Detalhe: os cartões dentro de `conL3Blocos` (contentor com `LayoutWrap`) usam `AlignInContainer.Start`; com `Stretch` ficavam com a altura da linha e cortavam o texto. Blocos de altura fixa têm `LayoutMinHeight` igual à altura, e o cartão branco desloca (`LayoutOverflow.Scroll`) em vez de encolher o conteúdo.
- Textos da API com quebras de linha (`body`) mostrados numa só linha passam por `Substitute(..., Char(10), " ")`.
- Contentores interiores com `DropShadow.None`; filhos de altura fixa com `FillPortions = 0`; etiquetas e ícones dentro de galerias com `OnSelect = Select(Parent)`.

## Sugestões de análise (em aberto)

1. Filtros duplicados entre galerias e contagens (`galL2Servicos.Items`/`lblL2Contagem`, `galL3Publicacoes.Items`/`lblL3Contagem`): candidatos a funções definidas pelo utilizador em `App.Formulas`, confirmando primeiro no Studio que a delegação se mantém.
2. Tamanhos de letra e espaçamentos como tokens (`nfTam*`), como já se faz com as cores.
3. Delegação e desempenho com tabelas acima de 500 registos.
4. Resolvido na v1.1.0: os 154 avisos do Verificador e as cores literais.

Ao propor alterações, mostre o excerto YAML antes e depois e indique o ecrã e o controlo. Responda em português de Portugal.
