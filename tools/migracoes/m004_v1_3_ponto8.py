"""Migração 004 · v1.3.0 · ponto 8 do Lab 4 com apresentação, a favor e contra, e a tabela num botão.

Corre sobre src/ depois da m003 e é idempotente: correr de novo não muda nada.

    python -m tools.migracoes.m004_v1_3_ponto8

O que faz:
  1. scrL4Complemento: o conteúdo passa a ter duas vistas, por locL4bVista.
     «texto»: o que é cada serviço (SharePoint, Dataverse, SQL), o que tem a favor e contra,
     e no fim o botão «Ver a tabela comparativa».
     «tabela»: os sete critérios do enunciado (Estrutura, Relações, Desenvolvimento Power Apps,
     Interface pronta, Lógica, Gestão, Caso de uso sugerido) e a conclusão.
     Os textos vêm de conteudo/ponto8.yaml, a mesma fonte do documento para o professor.
     Nada tem altura fixa: as etiquetas usam AutoHeight e cada linha da tabela tem a altura da
     etiqueta mais alta. A versão anterior usava uma galeria com TemplateSize fixo, que cortava texto.
  2. scrInicio: o quinto cartão passa a chamar-se «Origens de dados». «SharePoint, Dataverse e SQL»
     não cabia numa linha a 20 pt e aparecia cortado no monitor vertical.
  3. App.Formulas: nfVersao passa a "1.3.0".
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from tools.dac import projeto, yamlio

VERSAO = "1.3.0"
ECRA = "scrL4Complemento"
S = f"{ECRA}.Size"
PEQ = f"{S} = ScreenSize.Small"
TEXTO = 'locL4bVista <> "tabela"'
TABELA = 'locL4bVista = "tabela"'
LARG_CRIT = f"If({S} = ScreenSize.Medium, 150, 190)"


def _conteudo(raiz: Path) -> dict:
    return yaml.safe_load((raiz / "conteudo" / "ponto8.yaml").read_text(encoding="utf-8"))


def _s(texto: str) -> str:
    """Texto para uma fórmula Power Fx: entre aspas, com as aspas internas dobradas."""
    return '"' + " ".join(str(texto).split()).replace('"', '""') + '"'


def _lista(itens: list[str]) -> str:
    return " & Char(10) & ".join(_s("• " + i) for i in itens)


def _ctl(nome: str, controlo: str, props: dict, filhos: list | None = None, variante: str | None = None) -> dict:
    corpo: dict = {"Control": controlo}
    if variante:
        corpo["Variant"] = variante
    tipo = controlo.split("@")[0].split("/")[-1]
    # sem os valores por omissão, que o Studio apagaria ao guardar (yamlio.OMISSAO, lint DAC504)
    corpo["Properties"] = {k: props[k] for k in sorted(props) if yamlio.omissao(tipo, k) != props[k]}
    if filhos:
        corpo["Children"] = filhos
    return {nome: corpo}


def _etiqueta(nome: str, texto: str, visivel: str, **extra) -> dict:
    p = {"AlignInContainer": "=AlignInContainer.Stretch", "AutoHeight": "=true", "Color": "=nfTexto",
         "FocusedBorderThickness": "=2", "Size": "=14", "Text": "=" + texto, "Visible": "=" + visivel}
    p.update({k: v for k, v in extra.items()})
    return _ctl(nome, "Label@2.5.1", p)


def _caixa(nome: str, texto: str, visivel: str, fundo: str = "Color.White", cor: str = "nfTexto", **extra) -> dict:
    """Etiqueta com fundo e margens interiores: faz de cartão sem precisar de altura fixa."""
    p = {"Fill": "=" + fundo, "Color": "=" + cor, "PaddingTop": "=12", "PaddingBottom": "=12",
         "PaddingLeft": "=16", "PaddingRight": "=16"}
    p.update(extra)
    return _etiqueta(nome, texto, visivel, **p)


def _botao(nome: str, texto: str, acao: str, visivel: str, primario: bool) -> dict:
    p = {"AlignInContainer": "=AlignInContainer.Start", "BorderColor": "=nfAzul", "BorderThickness": "=2",
         "Color": "=" + ("Color.White" if primario else "nfAzul"), "Fill": "=" + ("nfAzul" if primario else "Color.White"),
         "FontWeight": "=FontWeight.Semibold", "Height": "=44", "HoverColor": "=" + ("Color.White" if primario else "nfAzul"),
         "HoverFill": "=" + ("nfAzul" if primario else "nfAzulClaro"), "OnSelect": "=" + acao,
         "PressedColor": "=" + ("Color.White" if primario else "nfAzul"), "PressedFill": "=" + ("nfAzul" if primario else "nfAzulClaro"),
         "RadiusBottomLeft": "=12", "RadiusBottomRight": "=12", "RadiusTopLeft": "=12", "RadiusTopRight": "=12",
         "Size": "=14", "TabIndex": "=0", "Text": "=" + _s(texto), "Visible": "=" + visivel,
         "Width": f"=If({PEQ}, Parent.Width - Parent.PaddingLeft - Parent.PaddingRight, 280)"}
    return _ctl(nome, "Classic/Button@2.2.0", p)


def _linha_tabela(i: int, c: dict) -> dict:
    n = str(i)
    nomes = [f"lblL4bCrit{n}", f"lblL4bSp{n}", f"lblL4bDv{n}", f"lblL4bSql{n}"]
    alturas = ", ".join(f"{x}.Height" for x in nomes)
    fundo = "Color.White" if i % 2 else "nfSuperficie"
    comuns = {"AutoHeight": "=true", "Color": "=nfTexto", "FocusedBorderThickness": "=2", "PaddingTop": "=10",
              "PaddingBottom": "=10", "PaddingLeft": "=12", "PaddingRight": "=12", "Size": "=13",
              "AlignInContainer": f"=If({PEQ}, AlignInContainer.Stretch, AlignInContainer.Start)"}
    crit = dict(comuns, FontWeight="=FontWeight.Semibold", Size="=14", Text="=" + _s(c["criterio"]),
                PaddingLeft="=16", Width=f"={LARG_CRIT}")
    filhos = [_ctl(nomes[0], "Label@2.5.1", crit)]
    for nome, chave, rotulo in ((nomes[1], "Sp", "SharePoint"), (nomes[2], "Dv", "Dataverse"), (nomes[3], "Sql", "SQL")):
        p = dict(comuns, FillPortions=f"=If({PEQ}, 0, 1)",
                 Text=f'=If({PEQ}, "{rotulo} · ", "") & {_s(c[chave])}')
        if chave == "Dv":
            p["Fill"] = "=nfAzulClaro"
        filhos.append(_ctl(nome, "Label@2.5.1", p))
    props = {"DropShadow": "=DropShadow.None", "Fill": "=" + fundo, "FillPortions": "=0",
             "Height": f"=If({PEQ}, {' + '.join(f'{x}.Height' for x in nomes)}, Max({alturas}))",
             "LayoutDirection": f"=If({PEQ}, LayoutDirection.Vertical, LayoutDirection.Horizontal)",
             "Visible": "=" + TABELA}
    return _ctl(f"conL4bLinha{n}", "GroupContainer@1.5.0", props, filhos, "AutoLayout")


def _cabecalho() -> dict:
    def cab(nome, texto, **extra):
        p = {"AlignInContainer": "=AlignInContainer.Stretch", "Color": "=nfTexto", "FocusedBorderThickness": "=2",
             "FontWeight": "=FontWeight.Bold", "PaddingLeft": "=12", "Size": "=14", "Text": "=" + texto}
        p.update(extra)
        return _ctl(nome, "Label@2.5.1", p)
    filhos = [cab("lblL4bCabCriterio", _s("Critério"), PaddingLeft="=16", Width=f"={LARG_CRIT}"),
              cab("lblL4bCabSharePoint", _s("SharePoint (listas)"), FillPortions="=1"),
              cab("lblL4bCabDataverse", f'If({S} = ScreenSize.Medium, "Dataverse", "Dataverse · usado nesta ficha")',
                  FillPortions="=1", Fill="=nfAzul", Color="=Color.White"),
              cab("lblL4bCabSQL", _s("SQL (Azure SQL)"), FillPortions="=1")]
    props = {"DropShadow": "=DropShadow.None", "Fill": "=nfLinha", "FillPortions": "=0", "Height": "=48",
             "LayoutDirection": "=LayoutDirection.Horizontal", "Visible": f"={TABELA} && {S} > ScreenSize.Small"}
    return _ctl("conL4bCabecalho", "GroupContainer@1.5.0", props, filhos, "AutoLayout")


def conteudo_l4b(c: dict) -> list:
    """Filhos de conConteudoL4b, gerados a partir de conteudo/ponto8.yaml."""
    f: list = [
        _etiqueta("lblL4bTitulo", f'If({TABELA}, "Comparação por critério", {_s(c["titulo"])})', "true",
                  FontWeight="=FontWeight.Bold", Size=f"=If({PEQ}, 20, 24)"),
        _etiqueta("lblL4bIntro", _s(c["intro"]), TEXTO, Color="=nfTextoSuave"),
    ]
    for sv in c["servicos"]:
        i = sv["id"]
        f += [
            _etiqueta(f"lblL4b{i}Nome", _s(sv["nome"]), TEXTO, Color="=nfAzul", FontWeight="=FontWeight.Bold",
                      Size="=20", PaddingTop="=12"),
            _caixa(f"lblL4b{i}OQue", _s(sv["oque"]), TEXTO),
            _caixa(f"lblL4b{i}FavorTit", _s("A favor"), TEXTO, fundo="nfVerdeFundo", cor="nfVerdeTexto",
                   FontWeight="=FontWeight.Semibold", PaddingTop="=8", PaddingBottom="=8"),
            _caixa(f"lblL4b{i}Favor", _lista(sv["favor"]), TEXTO),
            _caixa(f"lblL4b{i}ContraTit", _s("Contra"), TEXTO, fundo="nfAmbarFundo", cor="nfAmbar",
                   FontWeight="=FontWeight.Semibold", PaddingTop="=8", PaddingBottom="=8"),
            _caixa(f"lblL4b{i}Contra", _lista(sv["contra"]), TEXTO),
        ]
    f.append(_botao("btnL4bVerTabela", "Ver a tabela comparativa", 'UpdateContext({locL4bVista: "tabela"})', TEXTO, True))
    f.append(_etiqueta("lblL4bTabIntro", _s("Os sete critérios do enunciado do Lab 4, lado a lado. "
                                            "A coluna Dataverse é a origem usada na Ficha 04."),
                       TABELA, Color="=nfTextoSuave"))
    f.append(_cabecalho())
    f += [_linha_tabela(n, cr) for n, cr in enumerate(c["criterios"], 1)]
    f.append(_caixa("lblL4bConclusao", _s(c["conclusao"]), TABELA, fundo="nfAzulClaro", cor="nfAzul"))
    f.append(_botao("btnL4bVoltarTexto", "Voltar ao texto", 'UpdateContext({locL4bVista: "texto"})', TABELA, False))
    return f


def migrar_documento(doc: dict, c: dict) -> None:
    if "App" in doc:
        p = doc["App"]["Properties"]
        p["Formulas"] = re.sub(r'nfVersao = "[0-9.]+";', f'nfVersao = "{VERSAO}";', str(p["Formulas"]))
        return
    ecras = doc.get("Screens") or {}
    if "scrInicio" in ecras:
        for ctl in yamlio.controlos(doc):
            if ctl.nome == "galInFichas":
                itens = str(ctl.prop("Items"))
                itens = itens.replace('Titulo: "SharePoint, Dataverse e SQL"', 'Titulo: "Origens de dados"')
                itens = itens.replace(
                    'Descricao: "Ponto 8 do Lab 4: as três origens de dados comparadas para os clientes e pedidos."',
                    'Descricao: "Ponto 8 do Lab 4: SharePoint, Dataverse e SQL, o que são, a favor e contra, e a comparação."')
                ctl.definir("Items", itens)
    if ECRA in ecras:
        ecras[ECRA]["Properties"] = {"Fill": "=nfFundo", "OnVisible": '=UpdateContext({locL4bVista: "texto"})'}
        for ctl in yamlio.controlos(doc):
            if ctl.nome == "conConteudoL4b":
                largura = "Max(If(scrL4Complemento.Size = ScreenSize.Small, 16, 24), (Parent.Width - 1000) / 2)"
                ctl.definir("LayoutOverflow", "=LayoutOverflow.Scroll")
                ctl.definir("PaddingLeft", "=" + largura)
                ctl.definir("PaddingRight", "=" + largura)
                ctl.corpo["Children"] = conteudo_l4b(c)


def main(raiz: Path = projeto.RAIZ) -> int:
    c = _conteudo(raiz)
    mudados = 0
    for f in projeto.ficheiros_src(raiz):
        antes = f.read_text(encoding="utf-8")
        d = yamlio.ler(f)
        migrar_documento(d, c)
        depois = yamlio.escrever_texto(d)
        if depois != antes:
            f.write_text(depois, encoding="utf-8")
            mudados += 1
            print("migrado:", f.relative_to(raiz))
    print(f"m004: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
