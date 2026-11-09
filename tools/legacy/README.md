# Ferramentas antigas (não usar)

`gen.py` e `bundle.py` construíram a primeira versão dos sete ecrãs que não são da Ficha 02, antes de existir `src/`.

**Já não geram o estado atual da app.** Faltam-lhes, entre outras coisas, a paleta âmbar, as caixas `chkL3SimularFalha`/`chkL3SimularVazio`, a faixa `conL3Aviso` e todas as alterações da migração m001. Voltar a corrê-los e colar o resultado apagaria trabalho.

Ficam aqui como registo histórico e como exemplo de geração de YAML a partir de Python (útil numa aula). O fluxo atual está em `docs/alm.md`: `src/` → `python -m tools.dac colar` → Studio.

Defeito conhecido: `pt2inv` trocava `;` e `,` também dentro de textos (`"Olá, mundo"`). A conversão correta está em `tools/dac/pafx.py`.
