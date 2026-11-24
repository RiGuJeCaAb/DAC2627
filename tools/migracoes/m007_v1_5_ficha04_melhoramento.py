"""Migração 007 · v1.5.0 · Ficha 04 · Melhoramento: o Lab 4 com o processamento na cloud da aula 7.

Corre sobre src/ depois da m005 e é idempotente: correr de novo não muda nada.

    python -m tools.migracoes.m007_v1_5_ficha04_melhoramento

(A m006 fica livre de propósito: é o número do exercício da secção H11 do Manual ABC.)

O que faz:
  1. Cria src/screens/scrL4Melhoramento.pa.yaml, o ecrã da Ficha 04 · Melhoramento:
     - «Registar um pedido»: cliente, valor (com os valores de teste 100, 500 e 750 da aula) e descrição.
       Patch no Dataverse e mais nada: a app não espera pelo fluxo (processamento assíncrono).
       A caixa «Simular dado inválido» grava o pedido sem valor, para ver o ramo de erro do fluxo.
     - «Acompanhar o processamento»: o estado do pedido (Tratamento, Processado, data, observações,
       identificador da execução e decisão humana). O temporizador tmrL4cEstado consulta o Dataverse a cada
       3 s, no máximo 20 vezes, até Processado = Sim. O botão Reprocessar chama o fluxo instantâneo
       DAC2627_Pedido_Reprocessar (gatilho Power Apps V2), que responde logo, dentro dos 120 s.
     - «Pedidos processados»: os últimos 25, com filtro por tratamento.
  2. scrInicio: sexto cartão, «Ficha 04 · Melhoramento».
  3. App.Formulas: nfVersao passa a "1.5.0".

Os fluxos e as colunas novas do Pedido estão na solução DAC2627 (ver dataverse/schema.md e
dataverse/fluxos.md). Antes de colar, Atualizar a tabela Pedidos em Dados e adicionar o fluxo
DAC2627_Pedido_Reprocessar no painel Power Automate (build/colar/ORDEM.md).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.dac import projeto, yamlio

VERSAO = "1.5.0"
ECRA = "scrL4Melhoramento"
S = f"{ECRA}.Size"
PEQ = f"{S} = ScreenSize.Small"
TR = "'Tratamento (Pedidos)'"
DEC = "'Decisao (Pedidos)'"
P = "locL4cPedido"
TEM = f"!IsBlank({P})"
# num contentor horizontal, Stretch cortava o contorno de baixo dos cartões (CLAUDE.md, Ficha 02)
ALINHAR = f"=If({PEQ}, AlignInContainer.Stretch, AlignInContainer.Start)"



# Caixa de escolha do cliente fora de formulário (24/11/2026). Com Items = Clientes ou Choices([@Pedidos].dac_Cliente)
# e DisplayFields = ["dac_nome"], a lista abria com as linhas mas sem texto, na app publicada e no Studio.
# Uma coluna acrescentada com AddColumns mostra o nome. O Sort e o filtro correm no Dataverse e o AddColumns
# sobre o resultado, por isso a lista vê até ao limite de linhas da app (500 por omissão), que chega para os clientes.
ITENS_CLIENTES = "AddColumns(Sort(Clientes, Nome), NomeCliente, Nome)"

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


def _s(texto: str) -> str:
    return '"' + " ".join(str(texto).split()).replace('"', '""') + '"'


def _raio(r: int) -> dict:
    return {f"Radius{c}": f"={r}" for c in ("TopLeft", "TopRight", "BottomLeft", "BottomRight")}


def _contentor(nome: str, filhos: list, vertical: bool = True, **props) -> dict:
    p = {"DropShadow": "=DropShadow.None",
         "LayoutDirection": "=LayoutDirection." + ("Vertical" if vertical else "Horizontal")}
    p.update(props)
    return _ctl(nome, "GroupContainer@1.5.0", p, filhos, "AutoLayout")


def _cartao(nome: str, filhos: list, **props) -> dict:
    p = {"BorderColor": "=nfLinha", "BorderThickness": "=1", "Fill": "=Color.White", "LayoutGap": "=10",
         "PaddingBottom": "=20", "PaddingLeft": "=20", "PaddingRight": "=20", "PaddingTop": "=20", **_raio(16)}
    p.update(props)
    return _contentor(nome, filhos, True, **p)


def _etiqueta(nome: str, texto: str, **extra) -> dict:
    p = {"AlignInContainer": "=AlignInContainer.Stretch", "AutoHeight": "=true", "Color": "=nfTexto",
         "FocusedBorderThickness": "=2", "Size": "=14", "Text": "=" + texto}
    p.update(extra)
    return _ctl(nome, "Label@2.5.1", p)


def _rotulo(nome: str, texto: str) -> dict:
    return _etiqueta(nome, _s(texto), Color="=nfTextoSuave", FontWeight="=FontWeight.Semibold", Size="=13")


def _botao(nome: str, texto: str, acao: str, primario: bool = True, **extra) -> dict:
    cor, fundo, hover = ("Color.White", "nfAzul", "nfAzul") if primario else ("nfAzul", "Color.White", "nfAzulClaro")
    p = {"BorderColor": "=nfAzul", "BorderThickness": "=2", "Color": "=" + cor, "Fill": "=" + fundo,
         "FontWeight": "=FontWeight.Semibold", "Height": "=44", "HoverColor": "=" + cor, "HoverFill": "=" + hover,
         "OnSelect": "=" + acao, "PressedColor": "=" + cor, "PressedFill": "=" + hover, "Size": "=14",
         "TabIndex": "=0", "Text": "=" + texto, **_raio(12)}
    p.update(extra)
    return _ctl(nome, "Classic/Button@2.2.0", p)


def _cores_tratamento(alvo: str) -> tuple[str, str, str]:
    """(texto, cor, fundo) da pílula do tratamento, com as cores das mensagens da app."""
    def sw(por, auto, rev, erro, vazio):
        return (f"If(IsBlank({alvo}.Tratamento), {vazio}, {alvo}.Tratamento = {TR}.'Por processar', {por}, "
                f"{alvo}.Tratamento = {TR}.Automático, {auto}, {alvo}.Tratamento = {TR}.Revisão, {rev}, {erro})")
    texto = f'If(IsBlank({alvo}.Tratamento), "Não processado", Text({alvo}.Tratamento))'
    return (texto, sw("nfAzul", "nfVerdeTexto", "nfAmbar", "nfVermelhoTexto", "nfTextoSuave"),
            sw("nfAzulFundo", "nfVerdeFundo", "nfAmbarFundo", "nfVermelhoFundo", "nfLinha"))


def _pilula(nome: str, alvo: str, **extra) -> dict:
    texto, cor, fundo = _cores_tratamento(alvo)
    p = {"BorderThickness": "=0", "Color": "=" + cor, "DisabledColor": "=Self.Color", "DisabledFill": "=Self.Fill",
         "DisplayMode": "=DisplayMode.View", "Fill": "=" + fundo, "FontWeight": "=FontWeight.Bold", "Height": "=26",
         "HoverColor": "=Self.Color", "HoverFill": "=Self.Fill", "PressedFill": "=Self.Fill", "Size": "=11",
         "TabIndex": "=-1", "Text": "=" + texto, "Width": "=128", **_raio(13)}
    p.update(extra)
    return _ctl(nome, "Classic/Button@2.2.0", p)


# ---------------------------------------------------------------- 1 · Registar um pedido
REGISTAR = (
    "If(\n"
    "    IsBlank(cmbL4cCliente.Selected) || IsBlank(Trim(txtL4cDescricao.Text)) || (!chkL4cSemValor.Value && IsBlank(txtL4cValor.Text)),\n"
    '    UpdateContext({locL4cMsgTipo: "erro", locL4cTimer: false, locL4cMsg: "Escolha o cliente e preencha o valor e a descrição."}),\n'
    "    IfError(\n"
    "        UpdateContext({locL4cPedido: Patch(Pedidos, Defaults(Pedidos), {\n"
    "            Clientes: cmbL4cCliente.Selected,\n"
    "            DataPedido: Today(),\n"
    "            EstadoPedido: 'EstadoPedido (Pedidos)'.Pendente,\n"
    "            Valor: If(chkL4cSemValor.Value, Blank(), Value(txtL4cValor.Text)),\n"
    "            'Descrição': Trim(txtL4cDescricao.Text)\n"
    "        })}),\n"
    '        UpdateContext({locL4cMsgTipo: "erro", locL4cTimer: false, locL4cMsg: "Não foi possível registar o pedido. " & FirstError.Message}),\n'
    "        UpdateContext({locL4cAguardar: true, locL4cTentativas: 0, locL4cMsgTipo: \"ok\", locL4cTimer: true,\n"
    '            locL4cMsg: "Pedido " & locL4cPedido.NumeroPedido & " registado. O fluxo está a classificá-lo."});\n'
    '        UpdateContext({locL4cValorTeste: ""});\n'
    "        Reset(txtL4cValor);\n"
    "        Reset(txtL4cDescricao);\n"
    "        Reset(chkL4cSemValor)\n"
    "    )\n"
    ")"
)


def _teste(valor: int) -> dict:
    return _botao(f"btnL4cTeste{valor}", _s(str(valor)), f'UpdateContext({{locL4cValorTeste: "{valor}"}}); Reset(txtL4cValor)',
                  primario=False, Width="=72")


def _novo() -> dict:
    entrada = {"BorderColor": "=nfBorda", "Height": "=48", "HoverBorderColor": "=nfAzul", **_raio(12)}
    filhos = [
        _etiqueta("lblL4cNovoTitulo", _s("1 · Registar um pedido"), Color="=nfAzul", FontWeight="=FontWeight.Bold", Size="=18"),
        _rotulo("lblL4cClienteRot", "Cliente"),
        _ctl("cmbL4cCliente", "Classic/ComboBox@2.4.0", {
            "AccessibleLabel": '="Cliente do pedido"', "Width": "=Parent.Width - Parent.PaddingLeft - Parent.PaddingRight",
            "BorderColor": "=nfBorda", "ChevronBackground": "=nfAzul", "ChevronFill": "=Color.White",
            "DefaultSelectedItems": "=Blank()", "DisplayFields": '=["NomeCliente"]', "Height": "=48",
            "HoverFill": "=nfAzulFundo", "InputTextPlaceholder": '="Escolher o cliente"', "Items": "=" + ITENS_CLIENTES,
            "PressedColor": "=Color.White", "PressedFill": "=nfAzul", "SearchFields": '=["NomeCliente"]',
            "SelectMultiple": "=false", "SelectionColor": "=Color.White", "SelectionFill": "=nfAzul", "TabIndex": "=0"}),
        _rotulo("lblL4cValorRot", "Valor (€)"),
        _ctl("txtL4cValor", "Classic/TextInput@2.3.2", {
            "AccessibleLabel": '="Valor do pedido em euros"', "AlignInContainer": "=AlignInContainer.Stretch",
            "Default": "=locL4cValorTeste", "DisplayMode": "=If(chkL4cSemValor.Value, DisplayMode.Disabled, DisplayMode.Edit)",
            "Format": "=TextFormat.Number", "HintText": '="Ex.: 750"', "TabIndex": "=0", **entrada}),
        _contentor("conL4cTestes", [
            _etiqueta("lblL4cTestesRot", _s("Testes da aula:"), AlignInContainer="=AlignInContainer.Center",
                      AutoHeight="=false", Color="=nfTextoSuave", Height="=44", Size="=13", Width="=110"),
            _teste(100), _teste(500), _teste(750),
        ], vertical=False, FillPortions="=0", Height="=If(" + PEQ + ", 96, 44)", LayoutAlignItems="=LayoutAlignItems.Center",
           LayoutGap="=8", LayoutWrap="=true"),
        _rotulo("lblL4cDescRot", "Descrição"),
        _ctl("txtL4cDescricao", "Classic/TextInput@2.3.2", {
            "AccessibleLabel": '="Descrição do pedido"', "AlignInContainer": "=AlignInContainer.Stretch", "Default": '=""',
            "HintText": '="Ex.: Licenças de software anuais"', "Mode": "=TextMode.MultiLine", "TabIndex": "=0",
            **dict(entrada, Height="=80")}),
        _ctl("chkL4cSemValor", "Classic/CheckBox@2.1.0", {
            "BorderColor": "=nfBorda", "CheckboxBorderColor": "=nfVermelho", "CheckboxSize": "=24", "CheckmarkFill": "=nfTexto",
            "Color": "=nfTextoSuave", "Default": "=false", "Height": "=32", "HoverColor": "=nfAzul", "Size": "=13",
            "TabIndex": "=0", "Text": '="Simular dado inválido (gravar sem valor)"', "AlignInContainer": "=AlignInContainer.Stretch"}),
        _botao("btnL4cRegistar", _s("Registar pedido"), REGISTAR,
               DisplayMode="=If(locL4cAguardar, DisplayMode.Disabled, DisplayMode.Edit)",
               Width=f"=If({PEQ}, Parent.Width - Parent.PaddingLeft - Parent.PaddingRight, 220)"),
    ]
    altura = ("40 + 9 * 10 + lblL4cNovoTitulo.Height + lblL4cClienteRot.Height + 48 + lblL4cValorRot.Height + 48"
              " + conL4cTestes.Height + lblL4cDescRot.Height + 80 + 32 + 44")
    return _cartao("conL4cNovo", filhos, AlignInContainer=ALINHAR, FillPortions=f"=If({PEQ}, 0, 1)",
                   Height="=" + altura, LayoutMinWidth="=300")


# ---------------------------------------------------------------- 2 · Acompanhar o processamento
REFRESCAR = f"Refresh(Pedidos); UpdateContext({{{P}: LookUp(Pedidos, Pedido = {P}.Pedido)}})"
DETALHES = (
    f'"Valor: " & If(IsBlank({P}.Valor), "sem valor", Text({P}.Valor, "[$-pt-PT]0,00") & " €")'
    f' & "   ·   Processado: " & If({P}.Processado, "Sim", "Não")'
    f' & Char(10) & "Processado em: " & If(IsBlank({P}.DataProcessamento), "—", Text({P}.DataProcessamento, "dd/mm/yyyy hh:mm:ss"))'
    f' & Char(10) & "Observações: " & Coalesce({P}.ObservacoesProcessamento, "—")'
    f' & Char(10) & "Execução do fluxo: " & Coalesce({P}.IdExecucao, "—")'
)
DECISAO = (
    f'"Revisão humana: " & If(IsBlank({P}.Decisao), "—", Text({P}.Decisao))'
    f' & If(IsBlank({P}.DataDecisao), "", " em " & Text({P}.DataDecisao, "dd/mm/yyyy hh:mm"))'
    f' & If(IsBlank({P}.ComentarioDecisao), "", Char(10) & {P}.ComentarioDecisao)'
    f' & If({P}.Decisao = {DEC}.\'Aguarda decisão\', Char(10) & "O aprovador recebeu um email com as opções Aprovar e Rejeitar. Use Atualizar estado depois de ele responder.", "")'
)
REPROCESSAR = (
    "With(\n"
    "    {r: IfError(\n"
    f"        DAC2627_Pedido_Reprocessar.Run(Text({P}.Pedido)),\n"
    '        {resultado: "erro", mensagem: "Não foi possível chamar o fluxo. " & FirstError.Message}\n'
    "    )},\n"
    '    If(r.resultado = "ok",\n'
    '        UpdateContext({locL4cAguardar: true, locL4cTentativas: 0, locL4cMsgTipo: "ok", locL4cTimer: true, locL4cMsg: r.mensagem}),\n'
    '        UpdateContext({locL4cMsgTipo: "erro", locL4cTimer: false, locL4cMsg: r.mensagem})\n'
    "    )\n"
    ")"
)


def _estado() -> dict:
    caixa = {"Fill": "=nfSuperficie", "PaddingBottom": "=12", "PaddingLeft": "=16", "PaddingRight": "=16", "PaddingTop": "=12"}
    filhos = [
        _etiqueta("lblL4cEstadoTitulo", _s("2 · Acompanhar o processamento"), Color="=nfAzul", FontWeight="=FontWeight.Bold", Size="=18"),
        _etiqueta("lblL4cSemPedido", _s("Registe um pedido ou escolha um na lista de baixo para ver o estado do processamento."),
                  Color="=nfTextoSuave", Visible=f"=IsBlank({P})"),
        _contentor("conL4cResumo", [
            _etiqueta("lblL4cNumero", f'{P}.NumeroPedido & "  ·  " & {P}.Clientes.Nome', AlignInContainer="=AlignInContainer.Center",
                      FillPortions="=1", FontWeight="=FontWeight.Semibold", Size="=15"),
            _pilula("btnL4cTratamento", P, AlignInContainer="=AlignInContainer.Center"),
        ], vertical=False, FillPortions="=0", Height="=Max(36, lblL4cNumero.Height + 4)", LayoutAlignItems="=LayoutAlignItems.Center",
           LayoutGap="=12", Visible="=" + TEM),
        _etiqueta("lblL4cAguarda",
                  '"A aguardar o fluxo DAC2627_Pedido_Classificar · consulta " & (locL4cTentativas + 1) & " de 20, a cada 3 s."',
                  Color="=nfAmbar", Fill="=nfAmbarFundo", FontWeight="=FontWeight.Semibold", Visible="=locL4cAguardar",
                  **{k: v for k, v in caixa.items() if k != "Fill"}),
        _etiqueta("lblL4cDetalhes", DETALHES, Visible="=" + TEM, **caixa),
        _etiqueta("lblL4cDecisao", DECISAO, Color="=nfAmbar", Fill="=nfAmbarFundo",
                  Visible=f"={TEM} && ({P}.Tratamento = {TR}.Revisão || !IsBlank({P}.Decisao))",
                  **{k: v for k, v in caixa.items() if k != "Fill"}),
        _contentor("conL4cAcoes", [
            _botao("btnL4cAtualizar", _s("Atualizar estado"), REFRESCAR, primario=False,
                   DisplayMode=f"=If({TEM}, DisplayMode.Edit, DisplayMode.Disabled)", Width="=180"),
            _botao("btnL4cReprocessar", _s("Reprocessar"), REPROCESSAR,
                   DisplayMode=f"=If({TEM} && !locL4cAguardar, DisplayMode.Edit, DisplayMode.Disabled)", Width="=160"),
        ], vertical=False, FillPortions="=0", Height="=If(" + PEQ + ", 100, 44)", LayoutGap="=12", LayoutWrap="=true",
           Visible="=" + TEM),
    ]
    vis = lambda c, h: f"If({c}.Visible, 10 + {h}, 0)"
    altura = " + ".join(["40 + lblL4cEstadoTitulo.Height", vis("lblL4cSemPedido", "lblL4cSemPedido.Height"),
                         vis("conL4cResumo", "conL4cResumo.Height"), vis("lblL4cAguarda", "lblL4cAguarda.Height"),
                         vis("lblL4cDetalhes", "lblL4cDetalhes.Height"), vis("lblL4cDecisao", "lblL4cDecisao.Height"),
                         vis("conL4cAcoes", "conL4cAcoes.Height")])
    return _cartao("conL4cEstado", filhos, AlignInContainer=ALINHAR, FillPortions=f"=If({PEQ}, 0, 1)",
                   Height="=" + altura, LayoutMinWidth="=300")


# ---------------------------------------------------------------- 3 · Pedidos processados
def _filtro(nome: str, chave: str, texto: str) -> dict:
    ativo = f'locL4cFiltro = "{chave}"'
    return _botao(nome, _s(texto), f'UpdateContext({{locL4cFiltro: "{chave}"}})', primario=False,
                  Color=f"=If({ativo}, Color.White, nfAzul)", Fill=f"=If({ativo}, nfAzul, Color.White)",
                  HoverColor=f"=If({ativo}, Color.White, nfAzul)", HoverFill=f"=If({ativo}, nfAzul, nfAzulClaro)",
                  PressedColor=f"=If({ativo}, Color.White, nfAzul)", PressedFill=f"=If({ativo}, nfAzul, nfAzulClaro)",
                  Width="=130")


ITENS = (
    "=FirstN(Sort(Switch(locL4cFiltro,\n"
    f'    "auto", Filter(Pedidos, Tratamento = {TR}.Automático),\n'
    f'    "revisao", Filter(Pedidos, Tratamento = {TR}.Revisão),\n'
    f'    "erro", Filter(Pedidos, Tratamento = {TR}.Erro),\n'
    "    Filter(Pedidos, Processado = true)\n"
    "), DataProcessamento, SortOrder.Descending), 25)"
)


def _galeria() -> dict:
    texto, cor, fundo = _cores_tratamento("ThisItem")
    filhos = [
        _ctl("lblL4cGNumero", "Label@2.5.1", {
            "Color": "=nfTexto", "FontWeight": "=FontWeight.Semibold", "Height": "=28", "OnSelect": "=Select(Parent)",
            "Size": "=14", "Text": '=ThisItem.NumeroPedido & "  ·  " & ThisItem.Clientes.Nome',
            "Width": f"=Parent.TemplateWidth - If({PEQ}, 160, 300)", "Wrap": "=false", "X": "=16", "Y": "=8"}),
        _ctl("lblL4cGObs", "Label@2.5.1", {
            "Color": "=nfTextoSuave", "Height": "=24", "OnSelect": "=Select(Parent)", "Size": "=12",
            "Text": '=Coalesce(ThisItem.ObservacoesProcessamento, "")', "Width": "=Parent.TemplateWidth - 32",
            "Wrap": "=false", "X": "=16", "Y": "=38"}),
        _ctl("lblL4cGValor", "Label@2.5.1", {
            "Align": "=Align.Right", "Color": "=nfTexto", "FontWeight": "=FontWeight.Bold", "Height": "=28",
            "OnSelect": "=Select(Parent)", "Size": "=14",
            "Text": '=If(IsBlank(ThisItem.Valor), "—", Text(ThisItem.Valor, "[$-pt-PT]0,00") & " €")',
            "Visible": "=" + S + " > ScreenSize.Small", "Width": "=130", "X": "=Parent.TemplateWidth - 284", "Y": "=8"}),
        _ctl("btnL4cGTratamento", "Classic/Button@2.2.0", {
            "BorderThickness": "=0", "Color": "=" + cor, "DisabledColor": "=Self.Color", "DisabledFill": "=Self.Fill",
            "DisplayMode": "=DisplayMode.View", "Fill": "=" + fundo, "FontWeight": "=FontWeight.Bold", "Height": "=26",
            "HoverColor": "=Self.Color", "HoverFill": "=Self.Fill", "OnSelect": "=Select(Parent)", "PressedFill": "=Self.Fill",
            "Size": "=11", "TabIndex": "=-1", "Text": "=" + texto, "Width": "=128", "X": "=Parent.TemplateWidth - Self.Width - 16",
            "Y": "=9", **_raio(13)}),
        _ctl("recL4cGSeparador", "Rectangle@2.3.0", {"Fill": "=nfLinha", "Height": "=1", "Width": "=Parent.TemplateWidth",
                                                     "Y": "=Parent.TemplateHeight - 1"}),
    ]
    return _ctl("galL4cPedidos", "Gallery@2.15.0", {
        "AccessibleLabel": '="Pedidos processados"', "AlignInContainer": "=AlignInContainer.Stretch", "FillPortions": "=0",
        "Height": "=Max(1, Self.AllItemsCount) * Self.TemplateHeight", "Items": ITENS, "LayoutMinHeight": "=0",
        "OnSelect": f"=UpdateContext({{{P}: ThisItem, locL4cAguardar: false}})", "TabIndex": "=0", "TemplatePadding": "=0",
        "TemplateSize": "=70"}, filhos, "Vertical")


def _lista() -> list:
    return [
        _etiqueta("lblL4cListaTitulo", _s("3 · Pedidos processados"), Color="=nfAzul", FontWeight="=FontWeight.Bold",
                  PaddingTop="=8", Size="=18"),
        _contentor("conL4cFiltros", [
            _filtro("btnL4cFiltroTodos", "todos", "Todos"),
            _filtro("btnL4cFiltroAuto", "auto", "Automático"),
            _filtro("btnL4cFiltroRevisao", "revisao", "Revisão"),
            _filtro("btnL4cFiltroErro", "erro", "Erro"),
        ], vertical=False, FillPortions="=0", Height="=If(" + PEQ + ", 96, 44)", LayoutGap="=8", LayoutWrap="=true"),
        _etiqueta("lblL4cListaVazia", _s("Não há pedidos processados com este tratamento."), Color="=nfTextoSuave",
                  Visible="=galL4cPedidos.AllItemsCount = 0"),
        _contentor("conL4cListaCartao", [_galeria()], BorderColor="=nfLinha", BorderThickness="=1", Fill="=Color.White",
                   FillPortions="=0", Height="=galL4cPedidos.Height + 2", PaddingBottom="=1", PaddingLeft="=1",
                   PaddingRight="=1", PaddingTop="=1", **_raio(12)),
    ]


# ---------------------------------------------------------------- ecrã
INTRO = ("Lab 4 com o processamento da aula 7. A app grava o pedido no Dataverse e não fica à espera: o fluxo "
         "DAC2627_Pedido_Classificar trata-o em segundo plano. Até ao limite de revisão (variável de ambiente, 500 €) "
         "o pedido fica Automático, acima dele fica em Revisão e o fluxo DAC2627_Pedido_Aprovar pede uma decisão "
         "humana por email, e sem valor ou com uma falha técnica fica em Erro. Em todos os casos o fluxo regista a data, "
         "a justificação e o identificador da execução, para se encontrar a execução no histórico do Power Automate.")

ON_VISIBLE = ('=UpdateContext({locL4cPedido: Blank(), locL4cAguardar: false, locL4cTentativas: 0, locL4cFiltro: "todos", '
              'locL4cValorTeste: "", locL4cMsg: "", locL4cMsgTipo: "", locL4cTimer: false});\n'
              "Reset(cmbL4cCliente);\nReset(txtL4cValor);\nReset(txtL4cDescricao);\nReset(chkL4cSemValor)")

SONDAR = (
    "=Refresh(Pedidos);\n"
    f"UpdateContext({{{P}: LookUp(Pedidos, Pedido = {P}.Pedido), locL4cTentativas: locL4cTentativas + 1}});\n"
    "If(\n"
    f"    {P}.Processado,\n"
    '    UpdateContext({locL4cAguardar: false, locL4cMsgTipo: If(' + P + ".Tratamento = " + TR + '.Erro, "erro", "ok"), locL4cTimer: true,\n'
    f'        locL4cMsg: "Pedido " & {P}.NumeroPedido & " processado: " & Text({P}.Tratamento) & "."}}),\n'
    "    locL4cTentativas >= 20,\n"
    '    UpdateContext({locL4cAguardar: false, locL4cMsgTipo: "erro", locL4cTimer: false,\n'
    '        locL4cMsg: "O fluxo ainda não terminou ao fim de 60 s. Use Atualizar estado mais tarde."})\n'
    ")"
)


def ecra() -> dict:
    cab = _contentor("conCabL4c", [
        _ctl("icoInicioL4c", "Classic/Icon@2.5.0", {
            "AccessibleLabel": '="Voltar ao início"', "Color": "=Color.White", "Height": "=44", "Icon": "=Icon.Home",
            "OnSelect": "=Navigate(scrInicio, ScreenTransition.UnCover)", "TabIndex": "=0", "Width": "=44"}),
        _ctl("lblCabL4c", "Label@2.5.1", {
            "Color": "=Color.White", "FillPortions": "=1", "FocusedBorderThickness": "=2", "FontWeight": "=FontWeight.Semibold",
            "Height": "=44", "Size": "=16", "Text": '="Ficha 04 · Melhoramento"'}),
    ], vertical=False, Fill="=nfAzul", FillPortions="=0", Height="=64", LayoutAlignItems="=LayoutAlignItems.Center",
       LayoutGap="=12", PaddingLeft="=24", PaddingRight="=24")
    margem = f"Max(If({PEQ}, 16, 24), (Parent.Width - 1100) / 2)"
    conteudo = _contentor("conConteudoL4c", [
        _etiqueta("lblL4cTitulo", _s("Processamento automático de pedidos"), FontWeight="=FontWeight.Bold",
                  Size=f"=If({PEQ}, 20, 24)"),
        _etiqueta("lblL4cIntro", _s(INTRO), Color="=nfTextoSuave"),
        _contentor("conL4cTopo", [_novo(), _estado()], vertical=False, FillPortions="=0",
                   Height=f"=If({PEQ}, conL4cNovo.Height + conL4cEstado.Height + 16, Max(conL4cNovo.Height, conL4cEstado.Height)) + 2",
                   PaddingBottom="=2",
                   LayoutDirection=f"=If({PEQ}, LayoutDirection.Vertical, LayoutDirection.Horizontal)", LayoutGap="=16"),
        *_lista(),
    ], LayoutGap="=12", LayoutOverflowY="=LayoutOverflow.Scroll", PaddingBottom=f"=If({PEQ}, 16, 24)",
       PaddingLeft="=" + margem, PaddingRight="=" + margem, PaddingTop=f"=If({PEQ}, 16, 24)")
    raiz = _contentor("conEcraL4c", [cab, conteudo], Fill="=nfFundo", Height="=Parent.Height", Width="=Parent.Width")

    mensagem = _ctl("conL4cMensagem", "GroupContainer@1.5.0", {
        "DropShadow": "=DropShadow.Regular", "Fill": '=If(locL4cMsgTipo = "erro", nfVermelhoFundo, nfVerdeFundo)',
        "Height": "=56", "LayoutAlignItems": "=LayoutAlignItems.Center", "LayoutDirection": "=LayoutDirection.Horizontal",
        "LayoutGap": "=12", "PaddingBottom": "=16", "PaddingLeft": "=16", "PaddingRight": "=16", "PaddingTop": "=16",
        **_raio(12), "Visible": "=!IsBlank(locL4cMsg)", "Width": "=Min(560, Parent.Width - 32)",
        "X": "=(Parent.Width - Self.Width) / 2", "Y": "=76"}, [
        _ctl("icoL4cMsgIcone", "Classic/Icon@2.5.0", {
            "AccessibleLabel": '=If(locL4cMsgTipo = "erro", "Erro", "Sucesso")',
            "Color": '=If(locL4cMsgTipo = "erro", nfVermelho, nfVerde)', "Height": "=24",
            "Icon": '=If(locL4cMsgTipo = "erro", Icon.Warning, Icon.Check)', "Width": "=24"}),
        _ctl("lblL4cMensagem", "Label@2.5.1", {
            "Color": '=If(locL4cMsgTipo = "erro", nfVermelhoTexto, nfVerdeTexto)', "FillPortions": "=1",
            "FocusedBorderThickness": "=2", "FontWeight": "=FontWeight.Semibold", "Text": "=locL4cMsg"}),
        _ctl("icoL4cFecharMsg", "Classic/Icon@2.5.0", {
            "AccessibleLabel": '="Fechar mensagem"', "Color": "=nfTextoSuave", "Height": "=44", "Icon": "=Icon.Cancel",
            "OnSelect": '=UpdateContext({locL4cMsg: "", locL4cTimer: false})', "TabIndex": "=0", "Width": "=44"}),
    ], "AutoLayout")
    tmr_msg = _ctl("tmrL4cMensagem", "Timer@2.1.0", {
        "Duration": "=4000", "OnTimerEnd": '=UpdateContext({locL4cMsg: "", locL4cTimer: false})', "Start": "=locL4cTimer",
        "Visible": "=false"})
    tmr_estado = _ctl("tmrL4cEstado", "Timer@2.1.0", {
        "Duration": "=3000", "OnTimerEnd": SONDAR, "Repeat": "=locL4cAguardar", "Start": "=locL4cAguardar",
        "Visible": "=false"})
    return {"Screens": {ECRA: {"Properties": {"Fill": "=nfFundo", "OnVisible": ON_VISIBLE},
                               "Children": [raiz, mensagem, tmr_msg, tmr_estado]}}}


CARTAO = ('{Num: 6, Ficha: "Ficha 04 · Melhoramento", Titulo: "Processamento na cloud",\n'
          '     Descricao: "Aula 7: o pedido é classificado por um fluxo Power Automate, com estado, erros, reprocessamento e aprovação.", Disponivel: true}')


def migrar_documento(doc: dict) -> None:
    if "App" in doc:
        p = doc["App"]["Properties"]
        atual = re.search(r'nfVersao = "([0-9.]+)"', str(p.get("Formulas") or ""))
        if not atual or tuple(map(int, atual.group(1).split("."))) < tuple(map(int, VERSAO.split("."))):
            p["Formulas"] = re.sub(r'nfVersao = "[0-9.]+";', f'nfVersao = "{VERSAO}";', str(p["Formulas"]))
        return
    ecras = doc.get("Screens") or {}
    if "scrInicio" in ecras:
        for ctl in yamlio.controlos(doc):
            if ctl.nome == "galInFichas":
                itens = str(ctl.prop("Items"))
                if "Num: 6" not in itens:
                    itens = re.sub(r'(Disponivel: true\})\s*\n(\s*)\)\s*$', r'\1,\n\2    ' + CARTAO.replace("\\", "\\\\") + r'\n\2)', itens)
                    ctl.definir("Items", itens)
                sel = str(ctl.prop("OnSelect"))
                if "scrL4Melhoramento" not in sel:
                    sel = sel.replace("5, Navigate(scrL4Complemento, ScreenTransition.Cover)",
                                      "5, Navigate(scrL4Complemento, ScreenTransition.Cover),\n"
                                      "        6, Navigate(scrL4Melhoramento, ScreenTransition.Cover)")
                    ctl.definir("OnSelect", sel)


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
    novo = raiz / "src" / "screens" / f"{ECRA}.pa.yaml"
    texto = yamlio.escrever_texto(ecra())
    if not novo.exists() or novo.read_text(encoding="utf-8") != texto:
        novo.write_text(texto, encoding="utf-8")
        mudados += 1
        print("escrito:", novo.relative_to(raiz))
    print(f"m007: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
