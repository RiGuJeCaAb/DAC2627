# Regras do lint (`python -m tools.dac lint`)

Cada achado tem um código estável. Um **erro** faz falhar o CI; um **aviso** também, porque o CI corre com `--estrito`; um **info** nunca faz falhar. Para aceitar um caso de propósito, acrescente-o a `lint.excecoes` em `dac.yaml`, com `motivo`. Uma exceção sem motivo é o erro DAC900.

| Código | Gravidade | O que verifica | Como corrigir |
|---|---|---|---|
| DAC101 | aviso | Prefixo do tipo (`lbl`, `btn`, `con`...) e código da ficha (`In`, `L1`, `L2`, `L3`) no nome | Renomear no Studio: `Label3` → `lblL2Contagem` |
| DAC102 | erro | Nome repetido na app (o Power Apps exige nomes únicos em todos os ecrãs) | Renomear um deles |
| DAC103 | aviso | `UpdateContext` e o registo do `Navigate` com `loc*`, `Set` com `gbl*`, `Collect`/`ClearCollect` com `col*` | Renomear a variável em todas as fórmulas |
| DAC104 | info | Controlo de cartão de dados com o nome gerado (`DataCardValue5`) | Desbloquear o cartão e renomear (`cmbL2Estado`) |
| DAC201 | aviso | Cor literal (`ColorValue("#...")`, `RGBA(...)`, `Color.Red`) fora de `App.Formulas`. `Color.White` e `Color.Transparent` são aceites | Usar ou criar um token `nf*` |
| DAC202 | erro | Token `nf*` usado mas não definido em `App.Formulas` | Definir o token ou corrigir o nome |
| DAC301 | aviso | `AccessibleLabel` vazio ou ausente num controlo interativo: galerias, caixas de texto, listas, caixas de combinação, e ícones, imagens ou retângulos com ação no `OnSelect` | Texto que descreve a função. Nos decorativos não se escreve nada: ausente vale `""` |
| DAC302 | aviso | Controlo interativo fora da ordem de tabulação: botão com `TabIndex = -1`, galeria sem `TabIndex`, etiqueta, ícone, imagem ou retângulo com ação e `TabIndex` ausente ou negativo | `TabIndex = 0`. Nos decorativos não se escreve nada: ausente vale `-1` |
| DAC303 | aviso | `FocusedBorderThickness` maior do que 0 nas etiquetas fora de galerias, incluindo as dos cartões dos formulários | `FocusedBorderThickness = 2` |
| DAC304 | aviso | Ícone ou botão com ação mais pequeno do que 44 × 44 | Aumentar `Width` e `Height` para 44 ou mais |
| DAC401 | aviso | `CountRows(Galeria.AllItems)`: `AllItems` só tem as linhas já carregadas | Contar sobre a fonte: `CountRows(Filter(...))` |
| DAC402 | erro | `Text()`, `Len()`, `Left()`, `in`, ... dentro de `Filter`/`LookUp` sobre uma tabela Dataverse: deixa de ser delegável e só vê 500 registos | Comparar a escolha com `LookUp(Choices(...))`, usar `StartsWith` |
| DAC403 | erro | Referência a um controlo ou ecrã com nome da convenção que não existe | Corrigir o nome (gralha ou controlo renomeado) |
| DAC404 | aviso | Variável `loc*`, `gbl*` ou `col*` lida mas nunca definida (as `loc*` por ecrã, contando com o `Navigate`) | Definir a variável ou corrigir o nome |
| DAC405 | erro | Propriedade que o Studio não conhece para o tipo de controlo, comparada com as que aparecem na exportação (`msapp/Controls`). Ex.: `LayoutOverflow` num contentor, quando o nome certo é `LayoutOverflowY`. O Studio recusa a colagem com `PA2108` | Corrigir o nome. Se for uma propriedade legítima que a exportação ainda não usa, colar no Studio para confirmar e registar a exceção em `dac.yaml` |
| DAC501 | info | `Size` fora da escala tipográfica de `dac.yaml` | Usar um tamanho da escala |
| DAC502 | aviso | Etiqueta ou ícone dentro de galeria sem `OnSelect = Select(Parent)` | Acrescentar `OnSelect = Select(Parent)` |
| DAC503 | aviso | Sombra dentro de sombra: contentor com sombra (ausente vale `Light`) dentro de outro com sombra | `DropShadow.None` no contentor de fora ou no de dentro |
| DAC504 | aviso | Valor por omissão escrito no código (`TabIndex -1` e `Size 13` em etiquetas, `AccessibleLabel ""` em ícones e retângulos, `DropShadow.Light` em contentores...). O Studio apaga-o ao guardar e o código deixa de bater certo com a exportação | Retirar a linha. `yamlio` e as migrações já não o escrevem |
| DAC900 | erro | Exceção em `dac.yaml` sem motivo | Escrever o motivo |

## Limites conhecidos

- A análise é léxica, não semântica. DAC402 pode dar falsos positivos quando `Text()` se aplica a um controlo e não a uma coluna. Nesse caso, registe uma exceção com o motivo.
- Uma propriedade ausente vale o valor por omissão do Studio (tabela `OMISSAO` em `tools/dac/yamlio.py`). O Studio apaga esses valores ao guardar: na exportação 1.0.0.3 foram 116 linhas. As regras leem a ausência assim, para que o código exportado passe.
- O Verificador de aplicações marca **todos** os controlos com `TabIndex = -1` que não estejam numa galeria com `OnSelect = Select(Parent)`: etiquetas, ícones de estado, retângulos e as cinco pílulas. A Microsoft manda pôr `-1` nos elementos não interativos, por isso estes avisos (134 na exportação 1.0.0.3) ficam de propósito. Dar `TabIndex = 0` a uma etiqueta decorativa limparia o aviso e pioraria a navegação por teclado.
- O mesmo Verificador pede `AccessibleLabel` nos retângulos decorativos e no ícone `icoL4bConclusao`, que estão certos com `""`.
- O lint não sabe que fontes de dados estão na app nem por que ordem se cola. Isso é com `dac colar` (secção «Colar» de `docs/alm.md`), que compara o código com a última exportação.
- O lint não substitui o teste da app (manual, secção G2).
