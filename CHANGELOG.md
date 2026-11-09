# Registo de alterações

Formato: [Keep a Changelog](https://keepachangelog.com/pt-PT/1.1.0/). Versões da app em `nfVersao` (`App.Formulas`).

## [1.1.0] · 2026-11-09 · em `src/`, por colar no Studio

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

### Por confirmar no Studio
- Colagem dos 8 ecrãs e de `App.Formulas` (com comentários `//`), seguida do Verificador de aplicações.
- Aspeto do formulário da Ficha 02 com os tokens no lugar das cores por omissão.

## [1.0.0] · 2026-11-08
- Exportação inicial da solução DAC2627 (app, tabela Cloud Service e conector JSONPlaceholderDAC), com as correções de responsividade.
