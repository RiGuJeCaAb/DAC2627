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
| DAC301 | aviso | `AccessibleLabel` em galerias, caixas de texto, listas, caixas de combinação, ícones e retângulos | Texto que descreve a função; `""` só em elementos decorativos sem ação |
| DAC302 | aviso | `TabIndex` explícito em etiquetas, ícones, retângulos e galerias; botão com `TabIndex = -1` | `0` se interativo, `-1` se não |
| DAC303 | aviso | `FocusedBorderThickness` maior do que 0 nas etiquetas fora de galerias | `FocusedBorderThickness = 2` |
| DAC304 | aviso | Ícone ou botão com ação mais pequeno do que 44 × 44 | Aumentar `Width` e `Height` para 44 ou mais |
| DAC401 | aviso | `CountRows(Galeria.AllItems)`: `AllItems` só tem as linhas já carregadas | Contar sobre a fonte: `CountRows(Filter(...))` |
| DAC402 | erro | `Text()`, `Len()`, `Left()`, `in`, ... dentro de `Filter`/`LookUp` sobre uma tabela Dataverse: deixa de ser delegável e só vê 500 registos | Comparar a escolha com `LookUp(Choices(...))`, usar `StartsWith` |
| DAC403 | erro | Referência a um controlo ou ecrã com nome da convenção que não existe | Corrigir o nome (gralha ou controlo renomeado) |
| DAC404 | aviso | Variável `loc*`, `gbl*` ou `col*` lida mas nunca definida (as `loc*` por ecrã, contando com o `Navigate`) | Definir a variável ou corrigir o nome |
| DAC501 | info | `Size` fora da escala tipográfica de `dac.yaml` | Usar um tamanho da escala |
| DAC502 | aviso | Etiqueta ou ícone dentro de galeria sem `OnSelect = Select(Parent)` | Acrescentar `OnSelect = Select(Parent)` |
| DAC503 | aviso | Contentor interior sem `DropShadow` explícito (por omissão herda `Light`) | `DropShadow.None`, ou `DropShadow.Light` nos cartões |
| DAC900 | erro | Exceção em `dac.yaml` sem motivo | Escrever o motivo |

## Limites conhecidos

- A análise é léxica, não semântica. DAC402 pode dar falsos positivos quando `Text()` se aplica a um controlo e não a uma coluna. Nesse caso, registe uma exceção com o motivo.
- DAC301 a DAC303 seguem o que o Verificador de aplicações do Studio apontou na exportação de 8/11/2026. O verificador do Studio continua a ser a referência final: corra-o depois de colar.
- O lint não substitui o teste da app (manual, secção G2).
