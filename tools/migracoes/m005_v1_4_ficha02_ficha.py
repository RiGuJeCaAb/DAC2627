"""Migração 005 · v1.4.0 · Ficha 02: ficha do serviço com cor e áreas delimitadas.

Corre sobre src/ depois da m004 e é idempotente: correr de novo não muda nada.

    python -m tools.migracoes.m005_v1_4_ficha02_ficha

Porquê: em modo de leitura, o painel da Ficha 02 mostrava o formulário frmL2Servico com os rótulos do
Dataverse em inglês (Service Title, Provider...) e os valores soltos sobre branco, sem cor nem divisões.
A Ficha 04 já mostrava os dados do cliente com etiquetas de estado coloridas e linhas a separar as áreas.

O que faz:
  1. conL2Ficha: vista de leitura própria, no lugar do formulário quando este está em modo View.
     - Três cartões de factos (Fornecedor, Modelo de serviço, Estado), com as cores das etiquetas da lista:
       IaaS azul, PaaS verde, SaaS laranja; Ativo verde, Em avaliação âmbar, Descontinuado vermelho.
     - Descrição numa caixa com contorno.
     - «Quem gere o quê»: o que fica a cargo do fornecedor e do cliente no modelo do serviço
       (modelo de responsabilidade partilhada, NIST SP 800-145).
  2. frmL2Servico só aparece a criar ou a editar (Visible = Self.Mode <> FormMode.View).
  3. Rótulos do formulário em português (os DisplayName do Dataverse estão em inglês), também no
     AccessibleLabel e na Tooltip dos controlos de entrada.
  4. App.Formulas: nfVersao passa a "1.4.0".
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.dac import projeto, yamlio

VERSAO = "1.4.0"
ECRA = "scrL2Servicos"
S = f"{ECRA}.Size"
# lado a lado só com espaço para os três cartões: no monitor vertical o painel tem ~560 px e cortava os rótulos
LARGO = "conL2Ficha.Width >= 720"
ALTURA = 100  # cartões de factos
VER = "frmL2Servico.Mode = FormMode.View && !IsBlank(locSel)"
MODELO = "Text(locSel.'Service Model')"
ESTADO = "Text(locSel.Status)"

ROTULOS = {  # DataCardKey de cada cartão do formulário
    "Service Title_DataCard1": "Nome do serviço",
    "Status_DataCard1": "Estado",
    "Provider_DataCard1": "Fornecedor",
    "Service Model_DataCard1": "Modelo de serviço",
    "Service Description_DataCard1": "Descrição",
}

RESPONSABILIDADE = {
    "IaaS": "O fornecedor gere os centros de dados, o hardware, a rede e a virtualização. "
            "O cliente instala e mantém o sistema operativo, o runtime, os dados e as aplicações.",
    "PaaS": "O fornecedor gere também o sistema operativo, o runtime e a escala. "
            "O cliente concentra-se no código, na configuração e nos dados da sua aplicação.",
    "SaaS": "O fornecedor entrega a aplicação pronta e gere toda a pilha. "
            "O cliente configura o serviço, gere os utilizadores e responde pelos seus dados.",
}


def _s(texto: str) -> str:
    return '"' + str(texto).replace('"', '""') + '"'


def _ctl(nome: str, controlo: str, props: dict, filhos: list | None = None, variante: str | None = None) -> dict:
    corpo: dict = {"Control": controlo}
    if variante:
        corpo["Variant"] = variante
    tipo = controlo.split("@")[0].split("/")[-1]
    corpo["Properties"] = {k: props[k] for k in sorted(props) if yamlio.omissao(tipo, k) != props[k]}
    if filhos:
        corpo["Children"] = filhos
    return {nome: corpo}


def _etiqueta(nome: str, texto: str, **extra) -> dict:
    p = {"AlignInContainer": "=AlignInContainer.Stretch", "Color": "=nfTexto", "FocusedBorderThickness": "=2",
         "Height": "=24", "Size": "=14", "Text": "=" + texto}
    p.update(extra)
    return _ctl(nome, "Label@2.5.1", p)


def _contentor(nome: str, filhos: list, **extra) -> dict:
    p = {"DropShadow": "=DropShadow.None", "FillPortions": "=0", "LayoutDirection": "=LayoutDirection.Vertical"}
    p.update(extra)
    return _ctl(nome, "GroupContainer@1.5.0", p, filhos, "AutoLayout")


def _raio(r: int) -> dict:
    return {k: f"={r}" for k in ("RadiusBottomLeft", "RadiusBottomRight", "RadiusTopLeft", "RadiusTopRight")}


def _cartao(chave: str, rotulo: str, valor: str, nota: str, cor: str, fundo: str, contorno: str) -> dict:
    """Cartão de um facto: rótulo pequeno em maiúsculas, valor em destaque e uma nota."""
    filhos = [
        _etiqueta(f"lblL2Ficha{chave}Rotulo", _s(rotulo.upper()), Color="=" + cor, FontWeight="=FontWeight.Semibold",
                  Height="=18", Size="=11", Wrap="=false"),
        _etiqueta(f"lblL2Ficha{chave}", valor, Color="=" + cor, FontWeight="=FontWeight.Bold", Height="=30", Size="=18",
                  Wrap="=false"),
        _etiqueta(f"lblL2Ficha{chave}Nota", nota, Color="=" + cor, Height="=20", Size="=12", Wrap="=false"),
    ]
    # Altura com folga (conteúdo 96) e sem esticar na vertical quando estão lado a lado: esticado ao
    # contentor, o contorno de baixo ficava cortado no ecrã inteiro.
    return _contentor(f"conL2Ficha{chave}", filhos,
                      AlignInContainer=f"=If({LARGO}, AlignInContainer.Start, AlignInContainer.Stretch)",
                      BorderColor="=" + contorno, BorderThickness="=1", Fill="=" + fundo,
                      FillPortions=f"=If({LARGO}, 1, 0)", Height=f"={ALTURA}", LayoutGap="=2", LayoutMinWidth="=0",
                      PaddingBottom="=12", PaddingLeft="=16", PaddingRight="=16", PaddingTop="=12", **_raio(8))


def _seccao(chave: str, titulo: str) -> dict:
    return _etiqueta(f"lblL2Ficha{chave}Tit", _s(titulo), Color="=nfAzul", FontWeight="=FontWeight.Semibold",
                     Height="=36", PaddingTop="=12", Size="=15")


def conteudo_ficha() -> dict:
    # Sem valor (nenhuma coluna é obrigatória na tabela), o cartão fica neutro em vez de cair na última cor
    cor_modelo = f'Switch({MODELO}, "IaaS", nfAzul, "PaaS", nfVerdeTexto, "SaaS", nfLaranja, nfTexto)'
    fundo_modelo = f'Switch({MODELO}, "IaaS", nfAzulFundo, "PaaS", nfVerdeFundo, "SaaS", nfLaranjaFundo, nfSuperficie)'
    cor_estado = f'Switch({ESTADO}, "Ativo", nfVerdeTexto, "Em avaliação", nfAmbar, "Descontinuado", nfVermelhoTexto, nfTexto)'
    fundo_estado = f'Switch({ESTADO}, "Ativo", nfVerdeFundo, "Em avaliação", nfAmbarFundo, "Descontinuado", nfVermelhoFundo, nfSuperficie)'
    nota_modelo = (f'Switch({MODELO}, "IaaS", "Infraestrutura como serviço", "PaaS", "Plataforma como serviço", '
                   f'"SaaS", "Software como serviço", "Modelo por indicar")')
    nota_estado = (f'Switch({ESTADO}, "Ativo", "Em uso no inventário", "Em avaliação", "Em análise, ainda sem uso", '
                   f'"Descontinuado", "Já não é usado", "Estado por indicar")')
    nota_fornecedor = ("With({n: CountRows(Filter('Cloud Service', Provider = locSel.Provider))}, "
                       'n & If(n = 1, " serviço", " serviços") & " deste fornecedor")')
    factos = _contentor("conL2FichaFactos", [
        _cartao("Fornecedor", "Fornecedor", "locSel.Provider", nota_fornecedor, "nfTexto", "nfSuperficie", "nfLinhaForte"),
        _cartao("Modelo", "Modelo de serviço", f'If(IsBlank(locSel.\'Service Model\'), "—", {MODELO})', nota_modelo,
                cor_modelo, fundo_modelo, f'If(IsBlank(locSel.\'Service Model\'), nfLinhaForte, {cor_modelo})'),
        _cartao("Estado", "Estado", f'If(IsBlank(locSel.Status), "—", {ESTADO})', nota_estado,
                cor_estado, fundo_estado, f'If(IsBlank(locSel.Status), nfLinhaForte, {cor_estado})'),
    ], Height=f"=If({LARGO}, {ALTURA}, 3 * {ALTURA} + 2 * 12) + 4", LayoutDirection=f"=If({LARGO}, LayoutDirection.Horizontal, LayoutDirection.Vertical)",
        LayoutGap="=12", PaddingBottom="=2", PaddingLeft="=1", PaddingRight="=1", PaddingTop="=2")  # o contorno dos cartões não fica rente ao corte
    def caixa(chave: str, texto: str, fundo: str, contorno: str | None) -> dict:
        """Caixa de texto com cantos redondos: a etiqueta não tem Radius, por isso vai dentro de um contentor."""
        lbl = _etiqueta(f"lblL2Ficha{chave}", texto, AutoHeight="=true", Height="=48", PaddingBottom="=14",
                        PaddingLeft="=16", PaddingRight="=16", PaddingTop="=14", Size="=14")
        extra = {"BorderColor": "=" + contorno, "BorderThickness": "=1"} if contorno else {}
        return _contentor(f"conL2Ficha{chave}", [lbl], Fill="=" + fundo, Height=f"=lblL2Ficha{chave}.Height + 2",
                          PaddingBottom="=1", PaddingLeft="=1", PaddingRight="=1", PaddingTop="=1", **extra, **_raio(8))
    descricao = caixa("Descricao", "If(IsBlank(Trim(locSel.'Service Description')), \"Sem descrição.\", locSel.'Service Description')",
                      "nfSuperficie", "nfLinhaForte")
    resp = " ".join(f'"{m}", {_s(t)},' for m, t in RESPONSABILIDADE.items())
    responsabilidade = caixa("Responsabilidade", f"Switch({MODELO}, {resp} {_s('Indique o modelo de serviço para ver o que fica a cargo do fornecedor e do cliente.')})",
                             "nfAzulClaro", None)
    filhos = [factos, _seccao("Descricao", "Descrição"), descricao,
              _seccao("Responsabilidade", "Quem gere o quê"), responsabilidade]
    return _ctl("conL2Ficha", "GroupContainer@1.5.0", {
        "DropShadow": "=DropShadow.None", "FillPortions": "=1", "LayoutDirection": "=LayoutDirection.Vertical",
        "LayoutGap": "=10", "LayoutMinHeight": "=0", "LayoutOverflowY": "=LayoutOverflow.Scroll", "Visible": "=" + VER,
    }, filhos, "AutoLayout")


def migrar_documento(doc: dict) -> None:
    if "App" in doc:
        p = doc["App"]["Properties"]
        atual = re.search(r'nfVersao = "([0-9.]+)"', str(p.get("Formulas") or ""))
        if atual and tuple(map(int, atual.group(1).split("."))) < tuple(map(int, VERSAO.split("."))):
            p["Formulas"] = re.sub(r'nfVersao = "[0-9.]+";', f'nfVersao = "{VERSAO}";', str(p["Formulas"]))
        return
    if ECRA not in (doc.get("Screens") or {}):
        return
    for ctl in yamlio.controlos(doc):
        if ctl.nome == "frmL2Servico":
            ctl.definir("Visible", "=Self.Mode <> FormMode.View")
        elif ctl.nome in ROTULOS:
            for filho in ctl.corpo.get("Children") or []:
                (nome, corpo), = filho.items()
                if nome.startswith("DataCardKey"):
                    corpo.setdefault("Properties", {})["Text"] = "=" + _s(ROTULOS[ctl.nome])
                elif nome.startswith(("txtL2", "cmbL2")):
                    # o leitor de ecrã e a dica diziam o DisplayName do Dataverse, em inglês
                    for prop in ("AccessibleLabel", "Tooltip"):
                        corpo.setdefault("Properties", {})[prop] = "=" + _s(ROTULOS[ctl.nome])
        elif ctl.nome == "conL2Painel":
            filhos = ctl.corpo["Children"]
            filhos[:] = [f for f in filhos if "conL2Ficha" not in f]
            i = next(n for n, f in enumerate(filhos) if "frmL2Servico" in f)
            filhos.insert(i + 1, conteudo_ficha())


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
    print(f"m005: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
