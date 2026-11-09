# Paleta e contraste

Gerado por `python -m tools.dac paleta` a partir de `App.Formulas`. Não editar à mão.

## Tokens

| Token | Cor | Contraste com branco |
|---|---|---:|
| `nfAzul` | `#1F4E79` | 8.66:1 |
| `nfAzulClaro` | `#E8EFF6` | 1.16:1 |
| `nfAzulFundo` | `#DCE7F2` | 1.25:1 |
| `nfVerde` | `#2E7D5B` | 5.00:1 |
| `nfVerdeTexto` | `#1F5E43` | 7.66:1 |
| `nfVerdeFundo` | `#DDEFE6` | 1.20:1 |
| `nfVermelho` | `#A4262C` | 7.26:1 |
| `nfVermelhoTexto` | `#8E1F25` | 8.85:1 |
| `nfVermelhoFundo` | `#FBE9EA` | 1.17:1 |
| `nfAmbar` | `#9A5B00` | 5.43:1 |
| `nfAmbarFundo` | `#FFF4DB` | 1.09:1 |
| `nfLaranja` | `#8A3B0F` | 7.74:1 |
| `nfLaranjaFundo` | `#FBEBD9` | 1.17:1 |
| `nfFundo` | `#F6F4EF` | 1.10:1 |
| `nfSuperficie` | `#F7F8F9` | 1.06:1 |
| `nfTexto` | `#1E2A33` | 14.64:1 |
| `nfTextoSuave` | `#46525C` | 8.01:1 |
| `nfLinha` | `#E4E7EA` | 1.24:1 |
| `nfLinhaForte` | `#C5CBD1` | 1.64:1 |
| `nfBorda` | `#7D8993` | 3.58:1 |
| `nfDesativado` | `#A6A6A6` | 2.43:1 |
| `nfVeu` | `#1E2A33 · alfa 0.55` | 14.64:1 |

## Pares usados na app

AA exige 4,5:1 para texto normal e 3:1 para texto grande e contornos (WCAG 2.2, 1.4.3 e 1.4.11).

| Texto / primeiro plano | Fundo | Contraste | Nível | Uso |
|---|---|---:|---|---|
| `nfTexto` | `nfFundo` | 13.32:1 | AAA | Texto principal sobre o fundo dos ecrãs |
| `nfTexto` | `Color.White` | 14.64:1 | AAA | Texto principal nos cartões |
| `nfTextoSuave` | `nfFundo` | 7.29:1 | AAA | Texto secundário sobre o fundo |
| `nfTextoSuave` | `Color.White` | 8.01:1 | AAA | Texto secundário nos cartões |
| `Color.White` | `nfAzul` | 8.66:1 | AAA | Cabeçalho e botões primários |
| `nfAzul` | `Color.White` | 8.66:1 | AAA | Botões secundários e títulos de ficha |
| `nfAzul` | `nfAzulClaro` | 7.47:1 | AAA | Iniciais e linha selecionada |
| `nfAzul` | `nfAzulFundo` | 6.91:1 | AA | Etiqueta IaaS |
| `nfVerdeTexto` | `nfVerdeFundo` | 6.41:1 | AA | Mensagem de sucesso e etiqueta PaaS |
| `nfLaranja` | `nfLaranjaFundo` | 6.63:1 | AA | Etiqueta SaaS |
| `nfVermelhoTexto` | `nfVermelhoFundo` | 7.56:1 | AAA | Faixas de erro |
| `nfVermelho` | `Color.White` | 7.26:1 | AAA | Botão Remover |
| `Color.White` | `nfVermelho` | 7.26:1 | AAA | Botão de confirmar remoção |
| `nfAmbar` | `nfAmbarFundo` | 4.96:1 | AA | Faixas de aviso |
| `nfVerde` | `Color.White` | 5.00:1 | AA | Ícone de sucesso |
| `nfBorda` | `Color.White` | 3.58:1 | AA | Contorno das caixas de texto (mínimo 3:1) |
