"""Migração 010 · v1.8.0 · Ficha 04 com caixas: painéis, lista em cartões e detalhe por secções.

Corre sobre src/ depois da m009 e é idempotente: correr de novo não muda nada. A m009 continua a gerar os três modos;
esta só muda o aspeto, por isso a cadeia m009 → m010 também é idempotente (o teste corre as duas).

    python -m tools.migracoes.m010_v1_8_ficha04_visual

Pedido do utilizador (25/11/2026): «o quão sem sabor estão os quadros, tudo branco, sem grandes boxs a separar as
coisas». Proposta aprovada no mesmo dia. Vale para os três modos do scrL4Pedidos.

O que faz:
  1. Os dois painéis (lista de clientes e painel da direita) passam a cartões: contorno nfLinha e a sombra por omissão
     do contentor, sobre o fundo nfFundo do ecrã.
  2. Clientes: iniciais num círculo e uma barra azul à esquerda na linha escolhida.
  3. O topo do painel passa a uma banda nfAzulClaro com o título e, por baixo, os dados do cliente (na lista) ou o
     nome do cliente (no pedido). No detalhe, a pílula do tratamento fica na banda.
  4. Separadores em controlo segmentado: uma calha nfSuperficie com o separador ativo cheio. Na segunda fila
     (Automático, Revisão ou Por decidir, Erro) cada separador tem a cor do seu estado.
  5. Pedidos em cartões numa área nfSuperficie: cada linha tem contorno e uma barra de cor à esquerda (o tratamento
     do fluxo no Melhoramento e na Revisão, o estado do pedido no Lab 4).
  6. Detalhe do pedido em três caixas: Dados do pedido, Processamento automático (com os passos Registado,
     Classificado e Decisão) e Revisão humana. Cada caixa calcula a altura pelos filhos, como o detalhe já fazia.
  7. Botões de teste numa caixa e uma linha por cima do rodapé.
  8. App.Formulas: nfVersao passa a "1.8.0".
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.dac import projeto, yamlio
from tools.migracoes import m008_v1_6_ficha04_revisao as B
from tools.migracoes.m007_v1_5_ficha04_melhoramento import _contentor, _ctl, _etiqueta, _raio, _s
from tools.migracoes.m009_v1_7_ficha04_tres_modos import (
    DEC, ECRA, FINAL, M, P, PEQ, R, TR, _por, _procurar, _props,
)

VERSAO = "1.8.0"
EST = "'EstadoPedido (Pedidos)'"


def _definir(item: dict, **props) -> None:
    """Escreve as propriedades num controlo que já existe, sem os valores por omissão (o Studio apagá-los-ia)."""
    corpo = next(iter(item.values()))
    tipo = corpo["Control"].split("@")[0].split("/")[-1]
    p = corpo.setdefault("Properties", {})
    for k, v in props.items():
        if v is None or yamlio.omissao(tipo, k) == v:
            p.pop(k, None)
        else:
            p[k] = v
    corpo["Properties"] = {k: p[k] for k in sorted(p)}


def _item(doc: dict, nome: str) -> dict:
    achado = _procurar(doc["Screens"][ECRA]["Children"], nome)
    if achado is None:
        raise KeyError(nome)
    return achado


def _filhos(item: dict) -> list:
    return next(iter(item.values())).setdefault("Children", [])


def _tirar(doc: dict, nome: str) -> dict | None:
    """Tira o controlo do sítio onde estiver e devolve-o (None se não existir)."""
    def em(lista: list) -> dict | None:
        for i, it in enumerate(lista or []):
            n, corpo = next(iter(it.items()))
            if n == nome:
                return lista.pop(i)
            achado = em(corpo.get("Children"))
            if achado:
                return achado
        return None
    return em(doc["Screens"][ECRA]["Children"])


# ======================================================================== 1 · painéis
def _paineis(doc: dict) -> None:
    cartao = {"BorderColor": "=nfLinha", "BorderThickness": "=1", "DropShadow": None}
    _definir(_item(doc, "conL4Lista"), **cartao, PaddingBottom="=8", PaddingLeft="=1", PaddingRight="=1", PaddingTop="=1")
    _definir(_item(doc, "conL4Painel"), **cartao)


# ======================================================================== 2 · clientes
SEL_CLI = "!IsBlank(locL4Cliente) && ThisItem.Cliente = locL4Cliente.Cliente"
INICIAIS_CLI = ('With({p: Filter(Split(Trim(ThisItem.Nome), " "), Len(Value) > 3)}, '
                'Upper(If(CountRows(p) > 1, Left(First(p).Value, 1) & Left(Last(FirstN(p, 2)).Value, 1), Left(ThisItem.Nome, 2))))')


def _clientes(doc: dict) -> None:
    linha = _filhos(_item(doc, "galL4Clientes"))
    marca = _ctl("recL4CliMarca", "Rectangle@2.3.0", {
        "Fill": "=nfAzul", "Height": "=Parent.TemplateHeight", "OnSelect": "=Select(Parent)", "Visible": "=" + SEL_CLI, "Width": "=4"})
    iniciais = B._pilula("btnL4CliIniciais", INICIAIS_CLI, f"If({SEL_CLI}, Color.White, nfAzul)",
                         f"If({SEL_CLI}, nfAzul, nfAzulClaro)", Height="=36", OnSelect="=Select(Parent)", Size="=12",
                         Width="=36", X="=16", Y="=(Parent.TemplateHeight - Self.Height) / 2", **_raio(18))
    _por(linha, marca, no_inicio=True)
    _por(linha, iniciais, "recL4CliMarca")
    for nome in ("lblL4CliNome", "lblL4CliInfo"):
        _definir(next(x for x in linha if nome in x), X="=64", Width="=Parent.TemplateWidth - 104")


# ======================================================================== 3 · banda no topo do painel
DADOS_TEXTO = (
    '=Switch(locL4Modo,\n'
    f'    "detalhe", {P}.Clientes.Nome,\n'
    f'    "pedido", {P}.Clientes.Nome,\n'
    '    If(IsBlank(locL4Cliente),\n'
    '        "Pedidos de todos os clientes. Escolha um cliente na lista para ver só os dele.",\n'
    '        "NIF " & locL4Cliente.NIF & "  ·  " & locL4Cliente.Email & "  ·  " & locL4Cliente.Telefone))'
)
DADOS_VISIVEL = '=IsBlank(locL4Modo) || locL4Modo = "detalhe" || (locL4Modo = "pedido" && locL4Acao = "editar")'


def _banda(doc: dict) -> None:
    topo = _item(doc, "conL4PainelTopo")
    titulo = _tirar(doc, "lblL4PainelTitulo")
    dados = _tirar(doc, "lblL4ClienteDados")
    # Depois de correr a m009 outra vez há duas: a da banda e a que ela volta a pôr no detalhe (mais abaixo na árvore).
    primeira = _tirar(doc, "btnL4cTratamento")
    pilula = _tirar(doc, "btnL4cTratamento") or primeira
    _definir(titulo, AlignInContainer="=AlignInContainer.Stretch", Color="=nfAzul", FillPortions=None, Height="=32")
    _definir(dados, AlignInContainer="=AlignInContainer.Stretch", Color="=nfTextoSuave", Size="=13", Text=DADOS_TEXTO,
             Visible=DADOS_VISIVEL)
    tit = _contentor("conL4PainelTit", [titulo, dados], FillPortions="=1", LayoutGap="=2", LayoutMinWidth="=0",
                     Height="=lblL4PainelTitulo.Height + If(lblL4ClienteDados.Visible, lblL4ClienteDados.Height + 2, 0)")
    _definir(pilula, AlignInContainer="=AlignInContainer.Center", Visible=f'={M} && locL4Modo = "detalhe"')
    filhos = _filhos(topo)
    filhos[:] = [x for x in filhos if "conL4PainelTit" not in x]
    filhos.append(tit)
    filhos.append(pilula)
    _definir(topo, Fill="=nfAzulClaro", Height="=Max(64, conL4PainelTit.Height + 20)", PaddingBottom="=10",
             PaddingLeft=f"=If({PEQ}, 12, 16)", PaddingRight=f"=If({PEQ}, 12, 16)", PaddingTop="=10", **_raio(12))


# ======================================================================== 4 · separadores segmentados
CALHA = {"BorderColor": "=nfLinha", "BorderThickness": "=1", "Fill": "=nfSuperficie", "Height": "=54", "LayoutGap": "=4",
         "PaddingBottom": "=4", "PaddingLeft": "=4", "PaddingRight": "=4", "PaddingTop": "=4", **_raio(12)}
CORES_PROC = {   # separador: (cor do texto parado, cor cheia quando ativo)
    "btnL4cSepAuto": ("nfVerdeTexto", "nfVerde"),
    "btnL4cSepRevisao": ("nfAmbar", "nfAmbar"),
    "btnL4cSepErro": ("nfVermelhoTexto", "nfVermelho"),
}


def _separador(item: dict, texto: str, cheio: str, pairado: str) -> None:
    chave = re.search(r'locL4Vista: "([a-z]+)"', str(_props(item)["OnSelect"])).group(1)
    ativo = f'locL4Vista = "{chave}"'
    _definir(item, BorderThickness="=0", Color=f"=If({ativo}, Color.White, {texto})", FontWeight=f"=If({ativo}, FontWeight.Semibold, FontWeight.Normal)",
             Fill=f"=If({ativo}, {cheio}, Color.Transparent)", Height="=44",
             HoverColor=f"=If({ativo}, Color.White, {texto})", HoverFill=f"=If({ativo}, {cheio}, {pairado})",
             PressedColor=f"=If({ativo}, Color.White, {texto})", PressedFill=f"=If({ativo}, {cheio}, {pairado})",
             BorderColor=None, **_raio(8))


def _separadores(doc: dict) -> None:
    for con in ("conL4Separadores", "conL4cSeparadores"):
        _definir(_item(doc, con), **CALHA)
    for nome in ("btnL4SepTodos", "btnL4SepPendentes", "btnL4SepConcluidos"):
        _separador(_item(doc, nome), "nfTextoSuave", "nfAzul", "nfAzulClaro")
    for nome, (texto, cheio) in CORES_PROC.items():
        _separador(_item(doc, nome), texto, cheio, "Color.White")


# ======================================================================== 5 · pedidos em cartões
BARRA_PROC = (f"If(IsBlank(ThisItem.Tratamento) || ThisItem.Tratamento = {TR}.'Por processar', nfLinhaForte, "
              f"ThisItem.Tratamento = {TR}.Automático, nfVerde, ThisItem.Tratamento = {TR}.Revisão, nfAmbar, nfVermelho)")
BARRA_LAB4 = (f"If(ThisItem.EstadoPedido = {EST}.Pendente, nfAmbar, ThisItem.EstadoPedido = {EST}.'Em Processamento', nfAzul, "
              f"ThisItem.EstadoPedido = {EST}.Concluído, nfVerde, nfVermelho)")


def _cartoes(doc: dict) -> None:
    gal = _item(doc, "galL4Pedidos")
    _definir(gal, Fill="=nfSuperficie", TemplatePadding="=0", TemplateSize=f"=If({PEQ}, 104, 88)")
    linha = _filhos(gal)
    linha[:] = [x for x in linha if "recL4PedSeparador" not in x]   # o contorno do cartão faz de separador
    cartao = _ctl("recL4PedCartao", "Rectangle@2.3.0", {
        "BorderColor": "=nfLinha", "BorderThickness": "=1", "Fill": "=Color.White", "Height": "=Parent.TemplateHeight - 8",
        "OnSelect": "=Select(Parent)", "Width": "=Parent.TemplateWidth", "Y": "=4"})
    barra = _ctl("recL4PedBarra", "Rectangle@2.3.0", {
        "Fill": f"=If({M}, {BARRA_PROC}, {BARRA_LAB4})", "Height": "=Parent.TemplateHeight - 8", "OnSelect": "=Select(Parent)",
        "Width": "=4", "Y": "=4"})
    _por(linha, cartao, no_inicio=True)
    _por(linha, barra, "recL4PedCartao")
    posicoes = {"lblL4PedNumero": {"X": "=20", "Y": "=14"}, "lblL4PedDescricao": {"X": "=20", "Y": "=44"},
                "lblL4PedValor": {"Y": "=14"}, "btnL4PedEstado": {"Y": "=46"}, "btnL4cGTratamento": {"Y": "=46"}}
    for nome, props in posicoes.items():
        _definir(next(x for x in linha if nome in x), **props)


# ======================================================================== 6 · detalhe em caixas
DADOS = ("conL4cDetData", "conL4cDetEstado", "conL4cDetValor", "conL4cDetDescricao")
PROC = ("lblL4cProcTitulo", "conL4cPassos", "lblL4cAguarda", "conL4cDetProcessado", "conL4cDetObs", "conL4cDetExecucao",
        "conL4cAcoes", "lblL4cProcNota")
REV = ("lblL4cRevTitulo", "lblL4cDecisao", "lblL4dDetProposta", "lblL4dDetDecisao", "lblL4dDetEspera", "lblL4dSoLeitura",
       "lblL4dComentarioRot", "txtL4dComentario", "conL4dAcoesGestor", "conL4dAcoesAdmin")
FIXAS = {"conL4cPassos": "28", "txtL4dComentario": "80", "conL4dAcoesGestor": "44", "conL4dAcoesAdmin": "44",
         "conL4cAcoes": f"If({PEQ}, 100, 44)"}
TEM_REV = f"({P}.Tratamento = {TR}.Revisão || !IsBlank({P}.Decisao))"
PROPOSTA = f"({P}.Decisao = {DEC}.'Proposta: aprovar' || {P}.Decisao = {DEC}.'Proposta: rejeitar')"

FUTURO = ("Color.White", "nfTextoSuave")
FEITO = ("nfAzul", "Color.White")


def _passo(nome: str, texto: str, fundo: str, cor: str, contorno: str) -> dict:
    return B._pilula(nome, texto, cor, fundo, BorderColor="=nfLinhaForte", BorderThickness=f"=If({contorno}, 1, 0)",
                     FontWeight="=FontWeight.Semibold", Height="=28", PaddingLeft="=4", PaddingRight="=4",
                     Width=f"=If({PEQ}, 84, 120)", **_raio(14))


def _passos() -> dict:
    proc, agu = f"{P}.Processado", "locL4cAguardar"
    t2 = f'If({agu}, "A classificar", {proc}, "Classificado", "Classificação")'
    f2 = f"If({agu}, nfAmbarFundo, {proc}, {FEITO[0]}, {FUTURO[0]})"
    c2 = f"If({agu}, nfAmbar, {proc}, {FEITO[1]}, {FUTURO[1]})"
    tr = f"{P}.Tratamento"
    t3 = (f'If(!{proc}, "Decisão", {tr} = {TR}.Automático, "Automático", {tr} = {TR}.Erro, "Erro", '
          f'{P}.Decisao = {DEC}.Aprovado, "Aprovado", {P}.Decisao = {DEC}.Rejeitado, "Rejeitado", {PROPOSTA}, "Proposta", "Por decidir")')
    f3 = (f"If(!{proc}, {FUTURO[0]}, {tr} = {TR}.Automático || {P}.Decisao = {DEC}.Aprovado, nfVerdeFundo, "
          f"{tr} = {TR}.Erro || {P}.Decisao = {DEC}.Rejeitado, nfVermelhoFundo, {PROPOSTA}, nfAzulFundo, nfAmbarFundo)")
    c3 = (f"If(!{proc}, {FUTURO[1]}, {tr} = {TR}.Automático || {P}.Decisao = {DEC}.Aprovado, nfVerdeTexto, "
          f"{tr} = {TR}.Erro || {P}.Decisao = {DEC}.Rejeitado, nfVermelhoTexto, {PROPOSTA}, nfAzul, nfAmbar)")
    feito2 = f"{proc} && ({tr} <> {TR}.Revisão || {FINAL})"

    def traco(nome: str, feito: str) -> dict:
        return _contentor(nome, [], AlignInContainer="=AlignInContainer.Center", Fill=f"=If({feito}, nfAzul, nfLinhaForte)",
                          FillPortions="=1", Height="=2", LayoutMinWidth="=8")
    return _contentor("conL4cPassos", [
        _passo("btnL4cPasso1", _s("Registado"), FEITO[0], FEITO[1], "false"),
        traco("conL4cPassoTraco1", proc),
        _passo("btnL4cPasso2", t2, f2, c2, f"!{agu} && !{proc}"),
        traco("conL4cPassoTraco2", feito2),
        _passo("btnL4cPasso3", t3, f3, c3, f"!{proc}"),
    ], vertical=False, FillPortions="=0", Height="=28", LayoutAlignItems="=LayoutAlignItems.Center")


def _altura(filhos: list) -> str:
    partes = []
    for f in filhos:
        nome, corpo = next(iter(f.items()))
        h = FIXAS.get(nome, f"{nome}.Height")
        partes.append(f"If({nome}.Visible, {h} + 10, 0)" if "Visible" in corpo.get("Properties", {}) else f"{h} + 10")
    return " + ".join(partes)


def _caixa(nome: str, filhos: list, **extra) -> dict:
    # 16 de margem em cima e em baixo, 1 de contorno de cada lado, menos o último intervalo de 10
    return _contentor(nome, filhos, AlignInContainer="=AlignInContainer.Stretch", BorderColor="=nfLinha", BorderThickness="=1",
                      Fill="=nfSuperficie", FillPortions="=0", Height="=24 + " + _altura(filhos), LayoutGap="=10",
                      PaddingBottom="=16", PaddingLeft=f"=If({PEQ}, 12, 16)", PaddingRight=f"=If({PEQ}, 12, 16)", PaddingTop="=16",
                      **_raio(12), **extra)


def _titulo(nome: str, texto: str) -> dict:
    return _etiqueta(nome, texto, Color="=nfAzul", FontWeight="=FontWeight.Bold", Size="=15")


def _detalhe(doc: dict) -> None:
    conteudo = _item(doc, "conL4cDetConteudo")
    pecas: dict[str, dict] = {}

    def recolher(lista: list) -> None:
        for it in lista or []:
            n, corpo = next(iter(it.items()))
            if n.startswith("conL4cSec"):
                recolher(corpo.get("Children"))
            else:
                pecas[n] = it
    recolher(_filhos(conteudo))
    pecas["lblL4cSecDadosTit"] = _titulo("lblL4cSecDadosTit", _s("Dados do pedido"))
    pecas["conL4cPassos"] = _passos()
    _definir(pecas["lblL4cProcTitulo"], Size="=15")
    _definir(pecas["lblL4cRevTitulo"], Size="=15", Visible=None)
    dados = _caixa("conL4cSecDados", [pecas["lblL4cSecDadosTit"], *(pecas[n] for n in DADOS)])
    proc = _caixa("conL4cSecProc", [pecas[n] for n in PROC])
    rev = _caixa("conL4cSecRev", [pecas[n] for n in REV], Visible="=" + TEM_REV)
    seccoes = [dados, proc, rev]
    _filhos(conteudo)[:] = seccoes
    _definir(conteudo, Height="=" + " + ".join(
        f"If({next(iter(s))}.Visible, {next(iter(s))}.Height + 12, 0)" if "Visible" in _props(s) else f"{next(iter(s))}.Height + 12"
        for s in seccoes), LayoutGap="=12")


# ======================================================================== 7 · testes e rodapé
def _testes_e_rodape(doc: dict) -> None:
    _definir(_item(doc, "conL4cTestes"), BorderColor="=nfLinha", BorderThickness="=1", Fill="=nfSuperficie",
             Height=f"=If({PEQ}, 112, 60)", PaddingBottom="=6", PaddingLeft="=12", PaddingRight="=12", PaddingTop="=6", **_raio(12))
    painel = _filhos(_item(doc, "conL4Painel"))
    _por(painel, B._linha("conL4RodapeLinha", "nfLinha"), "conL4cDetalhe")


def migrar_pedidos(doc: dict) -> None:
    _paineis(doc)
    _clientes(doc)
    _banda(doc)
    _separadores(doc)
    _cartoes(doc)
    _detalhe(doc)
    _testes_e_rodape(doc)


def migrar_app(doc: dict) -> None:
    p = doc["App"]["Properties"]
    atual = re.search(r'nfVersao = "([0-9.]+)"', str(p.get("Formulas") or ""))
    if not atual or tuple(map(int, atual.group(1).split("."))) < tuple(map(int, VERSAO.split("."))):
        p["Formulas"] = re.sub(r'nfVersao = "[0-9.]+";', f'nfVersao = "{VERSAO}";', str(p["Formulas"]))


def migrar_documento(doc: dict) -> None:
    if "App" in doc:
        migrar_app(doc)
    elif ECRA in (doc.get("Screens") or {}):
        migrar_pedidos(doc)


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
    print(f"m010: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
