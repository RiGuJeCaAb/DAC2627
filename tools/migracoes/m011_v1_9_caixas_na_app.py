"""Migração 011 · v1.9.0 · o aspeto da Ficha 04 (v1.8.0) nas outras fichas.

Corre sobre src/ depois da m010 e é idempotente: correr de novo não muda nada.

    python -m tools.migracoes.m011_v1_9_caixas_na_app

Pedido do utilizador (25/11/2026): depois de validar a Ficha 04 com caixas, levar as mesmas peças à app toda.
Usa as peças da m010, não outras:
  1. Cartões com contorno nfLinha e a sombra por omissão: Fichas 01 (três ecrãs), 02 (lista e painel),
     03 (detalhe e publicação) e o cartão de entrada da Revisão.
  2. Banda nfAzulClaro no topo dos painéis: Ficha 02 (título do serviço) e Ficha 03 · Detalhe (iniciais e nome).
  3. Separadores da Ficha 03 · Lista na calha nfSuperficie, com o ativo cheio.
  4. Listas em cartões, com retângulos de fundo que passam o toque à linha (Select(Parent)): serviços da Ficha 02
     numa área nfSuperficie, com a barra da cor do modelo de serviço (IaaS, PaaS, SaaS) e o escolhido a azul-claro;
     utilizadores e publicações da Ficha 03, sobre o fundo do ecrã. Saem as linhas de separação, que o contorno
     do cartão substitui.
  5. App.Formulas: nfVersao passa a "1.9.0".
Fica de fora o scrL4Complemento: é texto do ponto 8 e a tabela já tem linhas alternadas.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.dac import projeto, yamlio
from tools.migracoes.m007_v1_5_ficha04_melhoramento import _ctl, _raio
from tools.migracoes.m009_v1_7_ficha04_tres_modos import _por, _procurar
from tools.migracoes.m010_v1_8_ficha04_visual import CALHA, _definir, _separador

VERSAO = "1.9.0"
CARTAO = {"BorderColor": "=nfLinha", "BorderThickness": "=1", "DropShadow": None}

CARTOES = {
    "scrL1BoasVindas": ("conL1aCartao",),
    "scrL1Pedido": ("conL1bCartao",),
    "scrL1Saudacao": ("conL1cCartao",),
    "scrL2Servicos": ("conL2Lista", "conL2Painel"),
    "scrL3Detalhe": ("conL3bCartao",),
    "scrL3Publicacao": ("conL3cCartao",),
    "scrL4Entrar": ("conL4dEntrar",),
}


def _item(doc: dict, ecra: str, nome: str) -> dict:
    achado = _procurar(doc["Screens"][ecra]["Children"], nome)
    if achado is None:
        raise KeyError(f"{ecra}.{nome}")
    return achado


def _filhos(item: dict) -> list:
    return next(iter(item.values())).setdefault("Children", [])


def _lista_em_cartoes(gal: dict, prefixo: str, separador: str, tamanho: str, posicoes: dict, fundo: str = "Color.White",
                      barra: str | None = None, area: str | None = None) -> None:
    """Linhas da galeria em cartões: retângulo branco com contorno (e barra de cor opcional) por baixo das etiquetas,
    com 4 px de folga em cima e em baixo. Valores finais escritos, para correr outra vez não deslocar nada."""
    _definir(gal, Fill=f"={area}" if area else None, TemplateFill="=Color.Transparent", TemplatePadding="=0", TemplateSize=tamanho)
    linha = _filhos(gal)
    linha[:] = [x for x in linha if separador not in x]
    cartao = _ctl(f"rec{prefixo}Cartao", "Rectangle@2.3.0", {
        "BorderColor": "=nfLinha", "BorderThickness": "=1", "Fill": "=" + fundo, "Height": "=Parent.TemplateHeight - 8",
        "OnSelect": "=Select(Parent)", "Width": "=Parent.TemplateWidth", "Y": "=4"})
    _por(linha, cartao, no_inicio=True)
    if barra:
        _por(linha, _ctl(f"rec{prefixo}Barra", "Rectangle@2.3.0", {
            "Fill": "=" + barra, "Height": "=Parent.TemplateHeight - 8", "OnSelect": "=Select(Parent)", "Width": "=4", "Y": "=4"}),
            f"rec{prefixo}Cartao")
    for nome, props in posicoes.items():
        _definir(next(x for x in linha if nome in x), **props)


def _banda(item: dict, peq: str, **extra) -> None:
    _definir(item, Fill="=nfAzulClaro", PaddingLeft=f"=If({peq}, 12, 16)", PaddingRight=f"=If({peq}, 12, 16)", **_raio(12), **extra)


# ======================================================================== Ficha 02
SEL_L2 = "ThisItem.'Cloud Service' = locSel.'Cloud Service'"
BARRA_L2 = "Switch(Text(ThisItem.'Service Model'), \"IaaS\", nfAzul, \"PaaS\", nfVerde, nfLaranja)"


def migrar_l2(doc: dict) -> None:
    e, peq = "scrL2Servicos", "scrL2Servicos.Size = ScreenSize.Small"
    _definir(_item(doc, e, "conL2Lista"), PaddingBottom="=8", PaddingLeft="=1", PaddingRight="=1", PaddingTop="=1")
    _banda(_item(doc, e, "conL2PainelTopo"), peq, Height="=64", PaddingBottom="=10", PaddingTop="=10")
    _definir(_item(doc, e, "lblL2PainelTitulo"), Color="=nfAzul")
    _lista_em_cartoes(_item(doc, e, "galL2Servicos"), "L2Item", "recL2Separador", "=80", {
        "lblL2ItemTitulo": {"Y": "=16"}, "lblL2ItemFornecedor": {"Y": "=44"}, "btnL2ItemModelo": {"Y": "=26"}},
        fundo=f"If({SEL_L2}, nfAzulClaro, Color.White)", barra=BARRA_L2, area="nfSuperficie")


# ======================================================================== Ficha 03
def migrar_l3_lista(doc: dict) -> None:
    e = "scrL3Lista"
    _definir(_item(doc, e, "conL3Separadores"), **CALHA)
    _separador(_item(doc, e, "btnL3SepUtil"), "nfTextoSuave", "nfAzul", "nfAzulClaro", 'locL3Vista <> "publicacoes"')
    _separador(_item(doc, e, "btnL3SepPub"), "nfTextoSuave", "nfAzul", "nfAzulClaro", 'locL3Vista = "publicacoes"')
    _lista_em_cartoes(_item(doc, e, "galL3Utilizadores"), "L3Item", "recL3Separador", "=88", {
        "btnL3Iniciais": {"Y": "=20"}, "lblL3ItemNome": {"Y": "=18"}, "lblL3ItemEmail": {"Y": "=44"},
        "lblL3ItemEmpresa": {"Y": "=30"}, "icoL3Abrir": {"Y": "=32"}})
    _lista_em_cartoes(_item(doc, e, "galL3Publicacoes"), "L3Pub", "recL3PubSeparador", "=104", {
        "lblL3PubItemTitulo": {"Y": "=14"}, "lblL3PubItemAutor": {"Y": "=42"}, "lblL3PubItemResumo": {"Y": "=66"},
        "icoL3PubAbrir": {"Y": "=40"}})


def migrar_l3_detalhe(doc: dict) -> None:
    e, peq = "scrL3Detalhe", "scrL3Detalhe.Size = ScreenSize.Small"
    altura = f"=If({peq}, 112, 100)"
    _banda(_item(doc, e, "conL3bTopo"), peq, Height=altura, LayoutMinHeight=altura, PaddingBottom="=6", PaddingTop="=6")
    _definir(_item(doc, e, "btnL3bIniciais"), Color="=Color.White", Fill="=nfAzul")


# ======================================================================== App e ciclo
def migrar_app(doc: dict) -> None:
    p = doc["App"]["Properties"]
    atual = re.search(r'nfVersao = "([0-9.]+)"', str(p.get("Formulas") or ""))
    if not atual or tuple(map(int, atual.group(1).split("."))) < tuple(map(int, VERSAO.split("."))):
        p["Formulas"] = re.sub(r'nfVersao = "[0-9.]+";', f'nfVersao = "{VERSAO}";', str(p["Formulas"]))


def migrar_documento(doc: dict) -> None:
    if "App" in doc:
        migrar_app(doc)
        return
    ecras = doc.get("Screens") or {}
    for ecra, nomes in CARTOES.items():
        if ecra in ecras:
            for nome in nomes:
                _definir(_item(doc, ecra, nome), **CARTAO)
    if "scrL2Servicos" in ecras:
        migrar_l2(doc)
    if "scrL3Lista" in ecras:
        migrar_l3_lista(doc)
    if "scrL3Detalhe" in ecras:
        migrar_l3_detalhe(doc)


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
    print(f"m011: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
