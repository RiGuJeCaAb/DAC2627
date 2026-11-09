"""Migração 001 · v1.1.0 · tokens de cor, acessibilidade e correções pequenas.

Corre uma vez sobre src/ e é idempotente: correr de novo não muda nada.

    python -m tools.migracoes.m001_v1_1_qualidade

O que faz (cada ponto corresponde a uma regra do lint ou a uma decisão do manual):
  1. App.Formulas: paleta completa em tokens nf*, uma por linha, agrupada, e nfVersao.
  2. DAC201: troca as cores literais (incluindo as cores por omissão do formulário) por tokens.
  3. DAC301: AccessibleLabel em entradas, galerias e ícones; "" nos elementos decorativos.
  4. DAC302: TabIndex explícito (0 se interativo, -1 se não).
  5. DAC303: FocusedBorderThickness = 2 nas etiquetas fora de galerias.
  6. DAC503: DropShadow explícito (Light nos cartões, None nos contentores interiores).
  7. DAC401: contagens sobre as coleções em vez de Galeria.AllItems.
  8. DAC104: DataCardValue5 passa a cmbL2Estado.
  9. Pormenores: reticências só quando o texto é cortado, versão no rodapé, aviso da Ficha 01 a âmbar.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.dac import pafx, projeto, yamlio
from tools.dac.yamlio import Controlo

VERSAO = "1.1.0"

FORMULAS = f'''nfAzul = ColorValue("#1F4E79"); // Paleta da APP DAC2627: todas as cores da app passam por aqui.
// Azul (água): marca, cabeçalhos, ações principais.
nfAzulClaro = ColorValue("#E8EFF6");
nfAzulFundo = ColorValue("#DCE7F2");
// Verde (madeira): sucesso e PaaS.
nfVerde = ColorValue("#2E7D5B");
nfVerdeTexto = ColorValue("#1F5E43");
nfVerdeFundo = ColorValue("#DDEFE6");
// Vermelho (fogo): erros e ações destrutivas.
nfVermelho = ColorValue("#A4262C");
nfVermelhoTexto = ColorValue("#8E1F25");
nfVermelhoFundo = ColorValue("#FBE9EA");
// Âmbar e laranja (terra quente): avisos e SaaS.
nfAmbar = ColorValue("#9A5B00");
nfAmbarFundo = ColorValue("#FFF4DB");
nfLaranja = ColorValue("#8A3B0F");
nfLaranjaFundo = ColorValue("#FBEBD9");
// Neutros (terra e metal): fundos, texto, linhas e contornos.
nfFundo = ColorValue("#F6F4EF");
nfSuperficie = ColorValue("#F7F8F9");
nfTexto = ColorValue("#1E2A33");
nfTextoSuave = ColorValue("#46525C");
nfLinha = ColorValue("#E4E7EA");
nfLinhaForte = ColorValue("#C5CBD1");
nfBorda = ColorValue("#7D8993");
nfDesativado = ColorValue("#A6A6A6");
nfVeu = RGBA(30, 42, 51, 0.55);
// Versão mostrada no rodapé do ecrã inicial.
nfVersao = "{VERSAO}";'''

# Cores literais -> token. A chave (propriedade, cor) ganha à chave só com a cor.
CORES = {
    'ColorValue("#8E1F25")': "nfVermelhoTexto",
    'ColorValue("#1F5E43")': "nfVerdeTexto",
    'ColorValue("#8A3B0F")': "nfLaranja",
    'ColorValue("#FBEBD9")': "nfLaranjaFundo",
    'ColorValue("#DCE7F2")': "nfAzulFundo",
    'ColorValue("#7D8993")': "nfBorda",
    'ColorValue("#C5CBD1")': "nfLinhaForte",
    'ColorValue("#F7F8F9")': "nfSuperficie",
    'ColorValue("#2F3B45")': "nfTexto",
    'ColorValue("#FDF1E7")': "nfAmbarFundo",
    "RGBA(30, 42, 51, 0.55)": "nfVeu",
    "RGBA(255, 255, 255, 1)": "Color.White",
    "RGBA(56, 96, 178, 1)": "nfAzul",
    "RGBA(186, 202, 226, 1)": "nfAzulFundo",
    "RGBA(168, 0, 0, 1)": "nfVermelhoTexto",
    "RGBA(166, 166, 166, 1)": "nfDesativado",
    "Color.Red": "nfVermelho",
}
CORES_POR_PROP = {
    ("Color", "RGBA(0, 18, 107, 1)"): "nfTexto",
    ("BorderColor", "RGBA(0, 18, 107, 1)"): "nfBorda",
    ("HoverBorderColor", "RGBA(0, 18, 107, 1)"): "nfAzul",
    ("HoverColor", "RGBA(0, 18, 107, 1)"): "nfAzul",
    ("PressedFill", "RGBA(0, 18, 107, 1)"): "nfAzul",
    ("BorderColor", "RGBA(0, 0, 0, 1)"): "nfBorda",
    ("CheckmarkFill", "RGBA(0, 0, 0, 1)"): "nfTexto",
}
# Exceções pontuais: o aviso da Ficha 01 passa a usar a cor de aviso da app (âmbar).
CORES_POR_CONTROLO = {
    ("lblL1Aviso", "Color"): "nfAmbar",
}

ROTULOS = {
    "txtL1Nome": '"O seu nome"',
    "galInFichas": '"Fichas de laboratório"',
    "icoL1Sucesso": '"Sucesso"',
    "txtL2Pesquisa": '"Pesquisar serviços pelo início do nome"',
    "drpL2Modelo": '"Filtrar por modelo de serviço"',
    "galL2Servicos": '"Lista de serviços cloud"',
    "icoL2MsgIcone": 'If(locMsgTipo = "erro", "Erro", "Sucesso")',
    "txtL2Titulo": "Parent.DisplayName",
    "txtL2Fornecedor": "Parent.DisplayName",
    "txtL2Descricao": "Parent.DisplayName",
    "cmbL2Modelo": "Parent.DisplayName",
    "cmbL2Estado": "Parent.DisplayName",
    "txtL3Pesquisa": "Self.HintText",
    "galL3Utilizadores": '"Lista de utilizadores"',
    "galL3Publicacoes": '"Lista de publicações"',
    "galL3PubsUtil": '"Publicações deste utilizador"',
    "icoL3Aviso": '"Erro"',
    "icoL3AvisoVazio": '"Aviso"',
}
DECORATIVOS = ("Rectangle",)  # e os chevrons dentro de galerias

CARTOES = {"conL1aCartao", "conL1bCartao", "conL1cCartao", "conL2Lista", "conL2Painel", "conL3bCartao", "conL3cCartao"}

FORMULAS_NOVAS = {
    ("lblL3TituloPubs", "Text"):
        '="PUBLICAÇÕES (" & CountRows(Filter(colL3Publicacoes, userId = locL3Sel.id)) & ")"',
    ("lblL3Contagem", "Text"): '''=If(locL3Vista = "publicacoes",
    CountRows(Filter(colL3Publicacoes,
        (drpL3Utilizador.Selected.id = 0 || userId = drpL3Utilizador.Selected.id) &&
        (txtL3Pesquisa.Text in title || txtL3Pesquisa.Text in body))) & " de " &
        CountRows(colL3Publicacoes) & " publicações",
    CountRows(Filter(colL3Utilizadores,
        txtL3Pesquisa.Text in name || txtL3Pesquisa.Text in email)) & " de " &
        CountRows(colL3Utilizadores) & " utilizadores")''',
    ("lblL3PubItemResumo", "Text"): '''=With({t: Substitute(ThisItem.body, Char(10), " ")},
    If(Len(t) > 100, Left(t, 100) & "…", t))''',
    ("lblInRodape", "Text"):
        '="Desenvolvimento de Aplicações na Cloud · CTeSP Computação Cloud · v" & nfVersao',
}


def _troca_cores(c: Controlo, prop: str, valor: str) -> str:
    if (c.nome, prop) in CORES_POR_CONTROLO:
        return "=" + CORES_POR_CONTROLO[(c.nome, prop)]
    fx = valor.lstrip("=")
    # ColorValue("#...") atravessa código e texto: troca-se no texto inteiro antes de partir
    for lit, tok in CORES.items():
        if lit.startswith("ColorValue("):
            fx = fx.replace(lit, tok)
    partes = pafx.partir(fx)
    for p in partes:
        if p.tipo != pafx.CODIGO:
            continue
        for (pr, lit), tok in CORES_POR_PROP.items():
            if pr == prop:
                p.texto = p.texto.replace(lit, tok)
        for lit, tok in CORES.items():
            p.texto = p.texto.replace(lit, tok)
    return "=" + "".join(p.texto for p in partes)


def _interativo(c: Controlo) -> bool:
    v = (c.prop("OnSelect") or "").lstrip("=").strip()
    return bool(v) and v not in ("false", "Select(Parent)")


def migrar_controlo(c: Controlo) -> None:
    props = c.corpo.get("Properties") or {}

    # 8. renomear o controlo gerado pelo Studio
    # (o nome é a chave do dicionário pai; trata-se em migrar_documento)

    # 2. cores
    for k in list(props):
        novo = _troca_cores(c, k, str(props[k]))
        if novo != str(props[k]):
            c.definir(k, novo)

    # 7 e 9. fórmulas reescritas
    for (nome, prop), fx in FORMULAS_NOVAS.items():
        if c.nome == nome:
            c.definir(prop, fx)

    if c.dentro_de_formulario and c.tipo in ("Label", "TypedDataCard"):
        return

    # 3. rótulos acessíveis
    if c.nome in ROTULOS:
        c.definir("AccessibleLabel", "=" + ROTULOS[c.nome])
    elif c.prop("AccessibleLabel") is None and (
            c.tipo in DECORATIVOS or (c.tipo == "Icon" and c.dentro_de_galeria and not _interativo(c))):
        c.definir("AccessibleLabel", '=""')

    if c.dentro_de_formulario:
        return

    # 4. ordem de tabulação
    if c.prop("TabIndex") is None:
        if c.tipo == "Gallery" or (c.tipo == "Icon" and _interativo(c) and not c.dentro_de_galeria):
            c.definir("TabIndex", "=0")
        elif c.tipo == "Rectangle" or (not c.dentro_de_galeria and c.tipo in ("Label", "Icon")):
            c.definir("TabIndex", "=-1")

    # 5. contorno de foco visível
    if c.tipo == "Label" and not c.dentro_de_galeria and c.prop("FocusedBorderThickness") in (None, "=0"):
        c.definir("FocusedBorderThickness", "=2")

    # 6. sombras explícitas
    if c.tipo == "GroupContainer" and c.pai is not None and c.prop("DropShadow") is None:
        c.definir("DropShadow", "=DropShadow.Light" if c.nome in CARTOES else "=DropShadow.None")


def _renomear(doc: dict, antigo: str, novo: str) -> int:
    """Renomeia um controlo e todas as referências em fórmulas (só no código)."""
    n = 0
    for c in list(yamlio.controlos(doc)):
        for k, v in list((c.corpo.get("Properties") or {}).items()):
            partes = pafx.partir(str(v))
            mudou = False
            for p in partes:
                if p.tipo == pafx.CODIGO and re.search(rf"\b{antigo}\b", p.texto):
                    p.texto = re.sub(rf"\b{antigo}\b", novo, p.texto)
                    mudou = True
            if mudou:
                c.corpo["Properties"][k] = "".join(p.texto for p in partes)
                n += 1

    def anda(lista):
        nonlocal n
        for item in lista or []:
            if antigo in item:
                item[novo] = item.pop(antigo)
                n += 1
            for corpo in item.values():
                anda(corpo.get("Children"))

    for corpo in (doc.get("Screens") or {}).values():
        anda(corpo.get("Children"))
    return n


def migrar_documento(doc: dict) -> None:
    if "App" in doc:
        p = doc["App"]["Properties"]
        p["Formulas"] = "=" + FORMULAS
        p["StartScreen"] = "=" + str(p["StartScreen"]).lstrip("=").strip()
        return
    _renomear(doc, "DataCardValue5", "cmbL2Estado")
    for c in list(yamlio.controlos(doc)):
        migrar_controlo(c)


def main(raiz: Path = projeto.RAIZ) -> int:
    mudados = 0
    for f in projeto.ficheiros_src(raiz):
        antes = f.read_text(encoding="utf-8")
        d = yamlio.ler(f)
        migrar_documento(d)
        depois = yamlio.escrever_texto(d)
        if depois != antes:
            f.write_text(depois, encoding="utf-8")
            mudados += 1
            print("migrado:", f.relative_to(raiz))
    print(f"m001: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
