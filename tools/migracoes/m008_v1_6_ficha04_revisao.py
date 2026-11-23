"""Migração 008 · v1.6.0 · Ficha 04 · Revisão: entrada com password (hash PBKDF2) e perfis Admin, Gestor e Cliente.

Corre sobre src/ depois da m007 e é idempotente: correr de novo não muda nada.

    python -m tools.migracoes.m008_v1_6_ficha04_revisao

O que faz:
  1. Cria src/screens/scrL4Entrar.pa.yaml: email e password. O botão Entrar chama o fluxo DAC2627_Utilizador_Entrar,
     que verifica a password no serviço de hash (Azure App Service, PBKDF2-SHA256) e devolve um testemunho de sessão.
     A app guarda o testemunho, o nome e o perfil em gblL4dSessao e apaga a password da caixa logo a seguir.
  2. Cria src/screens/scrL4Revisao.pa.yaml, com quatro vistas (locL4dVista):
     - «Pedidos em revisão»: o Gestor propõe aprovar ou rejeitar, o Admin decide, o Cliente acompanha os seus.
       Propostas e decisões passam pelo fluxo DAC2627_Pedido_Decidir, que lê o perfil da sessão e não da app.
     - «Registar pedido»: o Cliente regista para o seu cliente, o Gestor e o Admin para qualquer um. Fica em Registado por.
     - «Utilizadores» (só Admin): criar, editar, ativar, desbloquear e definir a password (fluxo DefinirPassword).
     - «A minha password»: mudar a própria, com a password atual.
     O Gestor e o Admin têm ainda o atalho para a Ficha 04 (CRUD de clientes e pedidos).
  3. scrInicio: sétimo cartão, «Ficha 04 · Revisão».
  4. scrL4Melhoramento: os textos deixam de falar do email com botões (o fluxo Aprovar passou a Notificar).
  5. App.Formulas: nfVersao passa a "1.6.0".

O login dentro da app organiza o ecrã: quem protege os dados no Dataverse são as funções de segurança.
Fluxos, tabela Utilizador e serviço de hash: dataverse/fluxos.md, dataverse/schema.md e azure/servico-hash/.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.dac import projeto, yamlio
from tools.migracoes.m007_v1_5_ficha04_melhoramento import (
    _botao, _cartao, _contentor, _ctl, _etiqueta, _raio, _rotulo, _s,
)

VERSAO = "1.6.0"
ENT, REV = "scrL4Entrar", "scrL4Revisao"
SES = "gblL4dSessao"
PERF = f"{SES}.perfil"
TR = "'Tratamento (Pedidos)'"
DEC = "'Decisao (Pedidos)'"
PU = "'Perfil (Utilizadores)'"
P = "locL4dPedido"
U = "locL4dUtil"
FINAL = f"({P}.Decisao = {DEC}.Aprovado || {P}.Decisao = {DEC}.Rejeitado)"
# resposta de recurso com os mesmos campos que os fluxos devolvem, para o IfError ter o mesmo tipo
FALHA = '{resultado: "erro", mensagem: "Não foi possível contactar o fluxo. " & FirstError.Message, token: "", nome: "", perfil: "", utilizadorid: "", clienteid: ""}'


def peq(ecra: str) -> str:
    return f"{ecra}.Size = ScreenSize.Small"


def _entrada(nome: str, rotulo: str, default: str = '=""', password: bool = False, **extra) -> dict:
    p = {"AccessibleLabel": "=" + _s(rotulo), "AlignInContainer": "=AlignInContainer.Stretch", "BorderColor": "=nfBorda",
         "Default": default, "Height": "=48", "HoverBorderColor": "=nfAzul", "TabIndex": "=0", **_raio(12)}
    if password:
        p["Mode"] = "=TextMode.Password"
    p.update(extra)
    return _ctl(nome, "Classic/TextInput@2.3.2", p)


def _pilula(nome: str, texto: str, cor: str, fundo: str, **extra) -> dict:
    p = {"BorderThickness": "=0", "Color": "=" + cor, "DisabledColor": "=Self.Color", "DisabledFill": "=Self.Fill",
         "DisplayMode": "=DisplayMode.View", "Fill": "=" + fundo, "FontWeight": "=FontWeight.Bold", "Height": "=26",
         "HoverColor": "=Self.Color", "HoverFill": "=Self.Fill", "PressedFill": "=Self.Fill", "Size": "=11",
         "TabIndex": "=-1", "Text": "=" + texto, "Width": "=128", **_raio(13)}
    p.update(extra)
    return _ctl(nome, "Classic/Button@2.2.0", p)


def _cores_decisao(alvo: str) -> tuple[str, str, str]:
    d = f"{alvo}.Decisao"
    sw = lambda ag, pr, ap, rj: (f"If({d} = {DEC}.Aprovado, {ap}, {d} = {DEC}.Rejeitado, {rj}, "
                                 f"{d} = {DEC}.'Proposta: aprovar' || {d} = {DEC}.'Proposta: rejeitar', {pr}, {ag})")
    return (f'If(IsBlank({d}), "Sem decisão", Text({d}))',
            sw("nfAmbar", "nfAzul", "nfVerdeTexto", "nfVermelhoTexto"),
            sw("nfAmbarFundo", "nfAzulFundo", "nfVerdeFundo", "nfVermelhoFundo"))


def _cabecalho(sufixo: str, titulo: str, extra: list | None = None) -> dict:
    return _contentor(f"conCab{sufixo}", [
        _ctl(f"icoInicio{sufixo}", "Classic/Icon@2.5.0", {
            "AccessibleLabel": '="Voltar ao início"', "Color": "=Color.White", "Height": "=44", "Icon": "=Icon.Home",
            "OnSelect": "=Navigate(scrInicio, ScreenTransition.UnCover)", "TabIndex": "=0", "Width": "=44"}),
        _ctl(f"lblCab{sufixo}", "Label@2.5.1", {
            "Color": "=Color.White", "FillPortions": "=1", "FocusedBorderThickness": "=2", "FontWeight": "=FontWeight.Semibold",
            "Height": "=44", "Size": "=16", "Text": "=" + _s(titulo)}),
        *(extra or []),
    ], vertical=False, Fill="=nfAzul", FillPortions="=0", Height="=64", LayoutAlignItems="=LayoutAlignItems.Center",
       LayoutGap="=12", PaddingLeft="=24", PaddingRight="=24")


def _mensagem(pref: str) -> list:
    """Faixa de mensagem por cima do ecrã e o temporizador que a esconde (o mesmo padrão do scrL4Melhoramento)."""
    return [
        _ctl(f"con{pref}Mensagem", "GroupContainer@1.5.0", {
            "DropShadow": "=DropShadow.Regular", "Fill": '=If(locL4dMsgTipo = "erro", nfVermelhoFundo, nfVerdeFundo)',
            "Height": "=Max(56, lbl" + pref + "Mensagem.Height + 16)", "LayoutAlignItems": "=LayoutAlignItems.Center",
            "LayoutDirection": "=LayoutDirection.Horizontal", "LayoutGap": "=12", "PaddingBottom": "=8", "PaddingLeft": "=16",
            "PaddingRight": "=8", "PaddingTop": "=8", **_raio(12), "Visible": "=!IsBlank(locL4dMsg)",
            "Width": "=Min(560, Parent.Width - 32)", "X": "=(Parent.Width - Self.Width) / 2", "Y": "=76"}, [
            _ctl(f"ico{pref}MsgIcone", "Classic/Icon@2.5.0", {
                "AccessibleLabel": '=If(locL4dMsgTipo = "erro", "Erro", "Sucesso")',
                "Color": '=If(locL4dMsgTipo = "erro", nfVermelho, nfVerde)', "Height": "=24",
                "Icon": '=If(locL4dMsgTipo = "erro", Icon.Warning, Icon.Check)', "Width": "=24"}),
            _ctl(f"lbl{pref}Mensagem", "Label@2.5.1", {
                "AutoHeight": "=true", "Color": '=If(locL4dMsgTipo = "erro", nfVermelhoTexto, nfVerdeTexto)', "FillPortions": "=1",
                "FocusedBorderThickness": "=2", "FontWeight": "=FontWeight.Semibold", "Text": "=locL4dMsg"}),
            _ctl(f"ico{pref}FecharMsg", "Classic/Icon@2.5.0", {
                "AccessibleLabel": '="Fechar mensagem"', "Color": "=nfTextoSuave", "Height": "=44", "Icon": "=Icon.Cancel",
                "OnSelect": '=UpdateContext({locL4dMsg: "", locL4dTimer: false})', "TabIndex": "=0", "Width": "=44"}),
        ], "AutoLayout"),
        _ctl(f"tmr{pref}Mensagem", "Timer@2.1.0", {
            "Duration": "=5000", "OnTimerEnd": '=UpdateContext({locL4dMsg: "", locL4dTimer: false})', "Start": "=locL4dTimer",
            "Visible": "=false"}),
    ]


def _msg(tipo: str, texto: str) -> str:
    timer = "true" if tipo == "ok" else "false"
    return f'UpdateContext({{locL4dMsgTipo: "{tipo}", locL4dTimer: {timer}, locL4dMsg: {texto}}})'


def _conteudo(sufixo: str, ecra: str, filhos: list, largura: int) -> dict:
    margem = f"Max(If({peq(ecra)}, 16, 24), (Parent.Width - {largura}) / 2)"
    return _contentor(f"conConteudo{sufixo}", filhos, LayoutGap="=12", LayoutOverflowY="=LayoutOverflow.Scroll",
                      PaddingBottom=f"=If({peq(ecra)}, 16, 24)", PaddingLeft="=" + margem, PaddingRight="=" + margem,
                      PaddingTop=f"=If({peq(ecra)}, 16, 24)")


def _altura(cabeca: str, itens: list[tuple[str, str]], gap: int = 10) -> str:
    """Altura de um cartão vertical: padding (40) + elementos sempre visíveis + os condicionais (visível → gap + altura)."""
    partes = [cabeca]
    for vis, h in itens:
        partes.append(f"{gap} + {h}" if vis is None else f"If({vis}, {gap} + {h}, 0)")
    return "=" + " + ".join(partes)


# ======================================================================== 1 · scrL4Entrar
ENTRAR = (
    "If(\n"
    "    IsBlank(Trim(txtL4dEmail.Text)) || IsBlank(txtL4dPassword.Text),\n"
    f"    {_msg('erro', _s('Escreva o email e a password.'))},\n"
    "    UpdateContext({locL4dAEntrar: true});\n"
    "    With(\n"
    f"        {{r: IfError(DAC2627_Utilizador_Entrar.Run(Lower(Trim(txtL4dEmail.Text)), txtL4dPassword.Text), {FALHA})}},\n"
    "        Reset(txtL4dPassword);\n"
    "        UpdateContext({locL4dAEntrar: false});\n"
    '        If(r.resultado = "ok",\n'
    f"            Set({SES}, {{token: r.token, nome: r.nome, perfil: r.perfil, utilizadorid: r.utilizadorid, clienteid: r.clienteid}});\n"
    f"            Navigate({REV}, ScreenTransition.Cover),\n"
    f"            {_msg('erro', 'r.mensagem')}\n"
    "        )\n"
    "    )\n"
    ")"
)
INTRO_ENT = ("A revisão dos pedidos acima do limite tem três perfis. O Cliente regista pedidos e acompanha os seus. "
             "O Gestor gere clientes e pedidos e propõe aprovar ou rejeitar. O Admin decide, valida as propostas do "
             "Gestor e gere os utilizadores.")
COMO = ("A password não fica guardada em lado nenhum. O fluxo DAC2627_Utilizador_Entrar envia-a ao serviço de hash "
        "(Azure App Service), que recalcula o PBKDF2-SHA256 com o salt do utilizador (600 000 iterações) e compara "
        "o resultado em tempo constante. À quinta tentativa falhada a conta fica bloqueada 15 minutos. "
        "Esta entrada organiza a app: quem protege os dados no Dataverse são as funções de segurança.")


def ecra_entrar() -> dict:
    cartao = _cartao("conL4dEntrar", [
        _etiqueta("lblL4dEntrarTitulo", _s("Entrar"), Color="=nfAzul", FontWeight="=FontWeight.Bold", Size="=18"),
        _rotulo("lblL4dEmailRot", "Email"),
        _entrada("txtL4dEmail", "Email", HintText='="nome@exemplo.pt"'),
        _rotulo("lblL4dPasswordRot", "Password"),
        _entrada("txtL4dPassword", "Password", password=True, HintText='="Password"'),
        _botao("btnL4dEntrar", 'If(locL4dAEntrar, "A verificar…", "Entrar")', ENTRAR,
               DisplayMode="=If(locL4dAEntrar, DisplayMode.Disabled, DisplayMode.Edit)",
               Width="=Parent.Width - Parent.PaddingLeft - Parent.PaddingRight"),
    ], FillPortions="=0", Height="=40 + 5 * 10 + lblL4dEntrarTitulo.Height + lblL4dEmailRot.Height + 48 + lblL4dPasswordRot.Height + 48 + 44")
    como = _cartao("conL4dComo", [
        _etiqueta("lblL4dComoTitulo", _s("Como funciona"), FontWeight="=FontWeight.Semibold", Size="=15"),
        _etiqueta("lblL4dComo", _s(COMO), Color="=nfTextoSuave", Size="=13"),
    ], FillPortions="=0", Fill="=nfSuperficie", Height="=40 + 10 + lblL4dComoTitulo.Height + lblL4dComo.Height")
    conteudo = _conteudo("L4dE", ENT, [
        _etiqueta("lblL4dTitulo", _s("Revisão de pedidos com perfis"), FontWeight="=FontWeight.Bold", Size=f"=If({peq(ENT)}, 20, 24)"),
        _etiqueta("lblL4dIntro", _s(INTRO_ENT), Color="=nfTextoSuave"),
        cartao, como,
    ], 560)
    raiz = _contentor("conEcraL4dE", [_cabecalho("L4dE", "Ficha 04 · Revisão"), conteudo], Fill="=nfFundo",
                      Height="=Parent.Height", Width="=Parent.Width")
    on_visible = ('=UpdateContext({locL4dAEntrar: false, locL4dMsg: "", locL4dMsgTipo: "", locL4dTimer: false});\n'
                  "Reset(txtL4dPassword)")
    return {"Screens": {ENT: {"Properties": {"Fill": "=nfFundo", "OnVisible": on_visible},
                              "Children": [raiz, *_mensagem("L4dE")]}}}


# ======================================================================== 2 · scrL4Revisao
def _separador(nome: str, chave: str, texto: str, visivel: str | None = None) -> dict:
    ativo = f'locL4dVista = "{chave}"'
    extra = {"Visible": "=" + visivel} if visivel else {}
    return _botao(nome, _s(texto), f'UpdateContext({{locL4dVista: "{chave}"}})', primario=False,
                  Color=f"=If({ativo}, Color.White, nfAzul)", Fill=f"=If({ativo}, nfAzul, Color.White)",
                  HoverColor=f"=If({ativo}, Color.White, nfAzul)", HoverFill=f"=If({ativo}, nfAzul, nfAzulClaro)",
                  PressedColor=f"=If({ativo}, Color.White, nfAzul)", PressedFill=f"=If({ativo}, nfAzul, nfAzulClaro)",
                  Width="=180", **extra)


def _decidir(acao: str) -> str:
    return (
        "With(\n"
        f'    {{r: IfError(DAC2627_Pedido_Decidir.Run({SES}.token, Text({P}.Pedido), "{acao}", txtL4dComentario.Text), {FALHA})}},\n'
        '    If(r.resultado = "ok",\n'
        f"        Refresh(Pedidos);\n"
        f"        UpdateContext({{{P}: LookUp(Pedidos, Pedido = {P}.Pedido)}});\n"
        "        Reset(txtL4dComentario);\n"
        f"        {_msg('ok', 'r.mensagem')},\n"
        f"        {_msg('erro', 'r.mensagem')}\n"
        "    )\n"
        ")"
    )


def _itens_pedidos() -> str:
    """Quatro Filter delegáveis escolhidos por fora (perfil e separador), nunca um If dentro do Filter,
    que deixaria de ser delegável (a regra do galL2Servicos.Items, no CLAUDE.md)."""
    decididos = f"(Decisao = {DEC}.Aprovado || Decisao = {DEC}.Rejeitado)"
    por_decidir = f"Decisao <> {DEC}.Aprovado, Decisao <> {DEC}.Rejeitado"
    def f(cliente: bool, final: bool) -> str:
        cond = [f"Tratamento = {TR}.Revisão"] + (["ThisRecord.Clientes.Cliente = c"] if cliente else []) + [decididos if final else por_decidir]
        return f"Sort(Filter(Pedidos, {', '.join(cond)}), DataProcessamento, SortOrder.Descending)"
    return (
        f'=With({{c: GUID(Coalesce({SES}.clienteid, "00000000-0000-0000-0000-000000000000"))}},\n'
        f'    If({PERF} = "Cliente",\n'
        f'        If(locL4dFiltro = "decididos", {f(True, True)},\n            {f(True, False)}),\n'
        f'        If(locL4dFiltro = "decididos", {f(False, True)},\n            {f(False, False)})\n'
        "    )\n)"
    )


ITENS_PED = _itens_pedidos()

DADOS = (
    f'"Valor: " & Text({P}.Valor, "[$-pt-PT]0,00") & " €   ·   Registado em " & Text({P}.DataPedido, "dd/mm/yyyy")'
    f' & If(IsBlank({P}.\'Registado por\'), "", " por " & {P}.\'Registado por\'.Nome)'
    f' & Char(10) & "Descrição: " & Coalesce({P}.\'Descrição\', "—")'
    f' & Char(10) & "Classificação: " & Coalesce({P}.ObservacoesProcessamento, "—")'
)
PROPOSTA = (
    f'"Proposta de " & {P}.\'Proposta por\'.Nome & " em " & Text({P}.\'Data da proposta\', "dd/mm/yyyy hh:mm")'
    f' & If({P}.Decisao = {DEC}.\'Proposta: aprovar\', ": aprovar", {P}.Decisao = {DEC}.\'Proposta: rejeitar\', ": rejeitar", "")'
    f' & If(IsBlank({P}.\'Comentário da proposta\'), "", Char(10) & {P}.\'Comentário da proposta\')'
)
DECISAO = (
    f'"Decisão final: " & Lower(Text({P}.Decisao)) & If(IsBlank({P}.\'Decidido por\'), "", " por " & {P}.\'Decidido por\'.Nome)'
    f' & If(IsBlank({P}.DataDecisao), "", " em " & Text({P}.DataDecisao, "dd/mm/yyyy hh:mm"))'
    f' & If(IsBlank({P}.ComentarioDecisao), "", Char(10) & {P}.ComentarioDecisao)'
)


def _galeria_pedidos() -> dict:
    texto, cor, fundo = _cores_decisao("ThisItem")
    filhos = [
        _ctl("lblL4dGNumero", "Label@2.5.1", {
            "Color": "=nfTexto", "FontWeight": "=FontWeight.Semibold", "Height": "=28", "OnSelect": "=Select(Parent)", "Size": "=14",
            "Text": '=ThisItem.NumeroPedido & "  ·  " & ThisItem.Clientes.Nome', "Width": "=Parent.TemplateWidth - 176",
            "Wrap": "=false", "X": "=16", "Y": "=8"}),
        _ctl("lblL4dGValor", "Label@2.5.1", {
            "Color": "=nfTextoSuave", "Height": "=24", "OnSelect": "=Select(Parent)", "Size": "=13",
            "Text": '=Text(ThisItem.Valor, "[$-pt-PT]0,00") & " €  ·  " & Text(ThisItem.DataPedido, "dd/mm/yyyy")',
            "Width": "=Parent.TemplateWidth - 32", "Wrap": "=false", "X": "=16", "Y": "=38"}),
        _pilula("btnL4dGDecisao", texto, cor, fundo, OnSelect="=Select(Parent)", Width="=140",
                X="=Parent.TemplateWidth - Self.Width - 16", Y="=9"),
        _ctl("recL4dGSeparador", "Rectangle@2.3.0", {"Fill": "=nfLinha", "Height": "=1", "Width": "=Parent.TemplateWidth",
                                                     "Y": "=Parent.TemplateHeight - 1"}),
    ]
    return _ctl("galL4dPedidos", "Gallery@2.15.0", {
        "AccessibleLabel": '="Pedidos em revisão"', "AlignInContainer": "=AlignInContainer.Stretch", "FillPortions": "=0",
        "Height": "=Max(1, Self.AllItemsCount) * Self.TemplateHeight", "Items": ITENS_PED, "LayoutMinHeight": "=0",
        "OnSelect": f"=UpdateContext({{{P}: ThisItem}}); Reset(txtL4dComentario)", "TabIndex": "=0", "TemplatePadding": "=0",
        "TemplateFill": f"=If(ThisItem.Pedido = {P}.Pedido, nfAzulFundo, Color.White)", "TemplateSize": "=70"}, filhos, "Vertical")


def _filtro(nome: str, chave: str, texto: str) -> dict:
    ativo = f'locL4dFiltro = "{chave}"'
    return _botao(nome, _s(texto), f'UpdateContext({{locL4dFiltro: "{chave}", {P}: Blank()}})', primario=False,
                  Color=f"=If({ativo}, Color.White, nfAzul)", Fill=f"=If({ativo}, nfAzul, Color.White)",
                  HoverColor=f"=If({ativo}, Color.White, nfAzul)", HoverFill=f"=If({ativo}, nfAzul, nfAzulClaro)",
                  PressedColor=f"=If({ativo}, Color.White, nfAzul)", PressedFill=f"=If({ativo}, nfAzul, nfAzulClaro)",
                  Width="=140")


def _vista_revisao() -> dict:
    lista = _contentor("conL4dLista", [
        _contentor("conL4dFiltros", [_filtro("btnL4dFiltroPorDecidir", "pordecidir", "Por decidir"),
                                     _filtro("btnL4dFiltroDecididos", "decididos", "Decididos")],
                   vertical=False, FillPortions="=0", Height="=44", LayoutGap="=8"),
        _etiqueta("lblL4dListaVazia", _s("Não há pedidos em revisão nesta lista."), Color="=nfTextoSuave",
                  Visible="=galL4dPedidos.AllItemsCount = 0"),
        _contentor("conL4dListaCartao", [_galeria_pedidos()], BorderColor="=nfLinha", BorderThickness="=1", Fill="=Color.White",
                   FillPortions="=0", Height="=galL4dPedidos.Height + 2", PaddingBottom="=1", PaddingLeft="=1",
                   PaddingRight="=1", PaddingTop="=1", **_raio(12)),
    ], AlignInContainer=f"=If({peq(REV)}, AlignInContainer.Stretch, AlignInContainer.Start)", FillPortions=f"=If({peq(REV)}, 0, 1)",
       Height="=44 + If(lblL4dListaVazia.Visible, 12 + lblL4dListaVazia.Height, 0) + 12 + conL4dListaCartao.Height",
       LayoutGap="=12", LayoutMinWidth="=300")

    tem = f"!IsBlank({P})"
    gestor_pode = f'{tem} && {PERF} = "Gestor" && !{FINAL}'
    admin_pode = f'{tem} && {PERF} = "Admin" && !{FINAL}'
    caixa = {"PaddingBottom": "=12", "PaddingLeft": "=16", "PaddingRight": "=16", "PaddingTop": "=12"}
    acoes = lambda nome, a, b: _contentor(nome, [a, b], vertical=False, FillPortions="=0", Height=f"=If({peq(REV)}, 100, 44)",
                                          LayoutGap="=12", LayoutWrap="=true")
    filhos = [
        _etiqueta("lblL4dDetTitulo", f'If({tem}, {P}.NumeroPedido & "  ·  " & {P}.Clientes.Nome, "Escolha um pedido na lista")',
                  Color="=nfAzul", FontWeight="=FontWeight.Bold", Size="=18"),
        _etiqueta("lblL4dDetDados", DADOS, Fill="=nfSuperficie", Visible="=" + tem, **caixa),
        _etiqueta("lblL4dDetProposta", PROPOSTA, Color="=nfAzul", Fill="=nfAzulFundo", Visible=f"={tem} && !IsBlank({P}.'Proposta por')",
                  **caixa),
        _etiqueta("lblL4dDetDecisao", DECISAO, Color=f"=If({P}.Decisao = {DEC}.Aprovado, nfVerdeTexto, nfVermelhoTexto)",
                  Fill=f"=If({P}.Decisao = {DEC}.Aprovado, nfVerdeFundo, nfVermelhoFundo)", Visible=f"={tem} && {FINAL}", **caixa),
        _etiqueta("lblL4dDetEspera", f'If({P}.Decisao = {DEC}.\'Aguarda decisão\', "Aguarda a proposta de um Gestor.", "Aguarda a decisão final do Admin.")',
                  Color="=nfAmbar", Fill="=nfAmbarFundo", FontWeight="=FontWeight.Semibold", Visible=f"={tem} && !{FINAL}", **caixa),
        _etiqueta("lblL4dSoLeitura", _s("O perfil Cliente acompanha os pedidos mas não decide."), Color="=nfTextoSuave",
                  Visible=f'={tem} && {PERF} = "Cliente"'),
        _rotulo("lblL4dComentarioRot", "Comentário (obrigatório para rejeitar)"),
        _entrada("txtL4dComentario", "Comentário da proposta ou da decisão", Mode="=TextMode.MultiLine", Height="=80"),
        acoes("conL4dAcoesGestor",
              _botao("btnL4dProporAprovar", _s("Propor aprovar"), _decidir("propor_aprovar"), Width="=170"),
              _botao("btnL4dProporRejeitar", _s("Propor rejeitar"), _decidir("propor_rejeitar"), primario=False, Width="=170")),
        acoes("conL4dAcoesAdmin",
              _botao("btnL4dAprovar", _s("Aprovar"), _decidir("aprovar"), Width="=150"),
              _botao("btnL4dRejeitar", _s("Rejeitar"), _decidir("rejeitar"), primario=False, Width="=150")),
    ]
    # o rótulo e a caixa do comentário só aparecem a quem pode agir
    pode = f"({gestor_pode}) || ({admin_pode})"
    for f in filhos:
        nome = next(iter(f))
        if nome in ("lblL4dComentarioRot", "txtL4dComentario"):
            f[nome]["Properties"]["Visible"] = "=" + pode
    filhos[-2]["conL4dAcoesGestor"]["Properties"]["Visible"] = "=" + gestor_pode
    filhos[-1]["conL4dAcoesAdmin"]["Properties"]["Visible"] = "=" + admin_pode
    vis = [(f"{n}.Visible", f"{n}.Height") for n in ("lblL4dDetDados", "lblL4dDetProposta", "lblL4dDetDecisao", "lblL4dDetEspera",
                                                    "lblL4dSoLeitura", "lblL4dComentarioRot")]
    vis += [("txtL4dComentario.Visible", "80"), ("conL4dAcoesGestor.Visible", "conL4dAcoesGestor.Height"),
            ("conL4dAcoesAdmin.Visible", "conL4dAcoesAdmin.Height")]
    detalhe = _cartao("conL4dDetalhe", filhos, AlignInContainer=f"=If({peq(REV)}, AlignInContainer.Stretch, AlignInContainer.Start)",
                      FillPortions=f"=If({peq(REV)}, 0, 1)", Height=_altura("40 + lblL4dDetTitulo.Height", vis), LayoutMinWidth="=300")
    return _contentor("conL4dVistaRevisao", [lista, detalhe], vertical=False, FillPortions="=0",
                      Height=f"=If({peq(REV)}, conL4dLista.Height + conL4dDetalhe.Height + 16, Max(conL4dLista.Height, conL4dDetalhe.Height)) + 2",
                      LayoutDirection=f"=If({peq(REV)}, LayoutDirection.Vertical, LayoutDirection.Horizontal)", LayoutGap="=16",
                      PaddingBottom="=2", Visible='=locL4dVista = "revisao"')


# ---------------------------------------------------------------- Registar pedido
REGISTAR = (
    "If(\n"
    f'    ({PERF} <> "Cliente" && IsBlank(cmbL4dCliente.Selected)) || IsBlank(txtL4dValor.Text) || IsBlank(Trim(txtL4dDescricao.Text)),\n'
    f"    {_msg('erro', _s('Preencha o cliente, o valor e a descrição.'))},\n"
    "    IfError(\n"
    "        UpdateContext({locL4dNovoPedido: Patch(Pedidos, Defaults(Pedidos), {\n"
    f'            Clientes: If({PERF} = "Cliente", LookUp(Clientes, Cliente = GUID({SES}.clienteid)), cmbL4dCliente.Selected),\n'
    "            DataPedido: Today(),\n"
    "            EstadoPedido: 'EstadoPedido (Pedidos)'.Pendente,\n"
    "            Valor: Value(txtL4dValor.Text),\n"
    "            'Descrição': Trim(txtL4dDescricao.Text),\n"
    f"            'Registado por': LookUp(Utilizadores, Utilizador = GUID({SES}.utilizadorid))\n"
    "        })}),\n"
    f"        {_msg('erro', '\"Não foi possível registar o pedido. \" & FirstError.Message')},\n"
    f"        {_msg('ok', '\"Pedido \" & locL4dNovoPedido.NumeroPedido & \" registado. Acima do limite entra em Revisão e os Gestores são avisados por email.\"')};\n"
    "        Reset(txtL4dValor);\n"
    "        Reset(txtL4dDescricao);\n"
    "        Reset(cmbL4dCliente)\n"
    "    )\n"
    ")"
)


def _vista_registar() -> dict:
    cliente_fixo = f'"Cliente: " & LookUp(Clientes, Cliente = GUID(Coalesce({SES}.clienteid, "00000000-0000-0000-0000-000000000000"))).Nome'
    filhos = [
        _etiqueta("lblL4dRegTitulo", _s("Registar um pedido"), Color="=nfAzul", FontWeight="=FontWeight.Bold", Size="=18"),
        _etiqueta("lblL4dRegCliente", cliente_fixo, FontWeight="=FontWeight.Semibold", Visible=f'={PERF} = "Cliente"'),
        _rotulo("lblL4dRegClienteRot", "Cliente"),
        _ctl("cmbL4dCliente", "Classic/ComboBox@2.4.0", {
            "AccessibleLabel": '="Cliente do pedido"', "Width": "=Parent.Width - Parent.PaddingLeft - Parent.PaddingRight",
            "BorderColor": "=nfBorda", "ChevronBackground": "=nfAzul", "ChevronFill": "=Color.White",
            "DefaultSelectedItems": "=Blank()", "DisplayFields": '=["dac_nome"]', "Height": "=48",
            "HoverFill": "=nfAzulFundo", "InputTextPlaceholder": '="Escolher o cliente"', "Items": "=Choices([@Pedidos].dac_Cliente)",
            "PressedColor": "=Color.White", "PressedFill": "=nfAzul", "SearchFields": '=["dac_nome"]',
            "SelectMultiple": "=false", "SelectionColor": "=Color.White", "SelectionFill": "=nfAzul", "TabIndex": "=0",
            "Visible": f'={PERF} <> "Cliente"'}),
        _rotulo("lblL4dRegValorRot", "Valor (€)"),
        _entrada("txtL4dValor", "Valor do pedido em euros", Format="=TextFormat.Number", HintText='="Ex.: 750"'),
        _rotulo("lblL4dRegDescRot", "Descrição"),
        _entrada("txtL4dDescricao", "Descrição do pedido", Mode="=TextMode.MultiLine", Height="=80",
                 HintText='="Ex.: Renovação do contrato de alojamento"'),
        _botao("btnL4dRegistar", _s("Registar pedido"), REGISTAR, Width=f"=If({peq(REV)}, Parent.Width - Parent.PaddingLeft - Parent.PaddingRight, 220)"),
        _etiqueta("lblL4dRegNota", _s("O fluxo DAC2627_Pedido_Classificar trata o pedido em segundo plano. Acima de 500 € fica em "
                                      "Revisão e aparece na lista «Pedidos em revisão»."), Color="=nfTextoSuave", Size="=13"),
    ]
    filhos[2]["lblL4dRegClienteRot"]["Properties"]["Visible"] = f'={PERF} <> "Cliente"'
    vis = [("lblL4dRegCliente.Visible", "lblL4dRegCliente.Height"), ("lblL4dRegClienteRot.Visible", "lblL4dRegClienteRot.Height"),
           ("cmbL4dCliente.Visible", "48"), (None, "lblL4dRegValorRot.Height"), (None, "48"), (None, "lblL4dRegDescRot.Height"),
           (None, "80"), (None, "44"), (None, "lblL4dRegNota.Height")]
    return _cartao("conL4dVistaRegistar", filhos, FillPortions="=0", Height=_altura("40 + lblL4dRegTitulo.Height", vis),
                   Visible='=locL4dVista = "registar"')


# ---------------------------------------------------------------- Utilizadores (Admin)
ITER = "'Iterações'"
GUARDADO = f'If(IsBlank({U}.{ITER}), "Utilizador guardado. Defina-lhe a password para poder entrar.", "Utilizador guardado.")'
GUARDAR_UTIL = (
    "If(\n"
    "    IsBlank(Trim(txtL4dUtilNome.Text)) || !IsMatch(Trim(txtL4dUtilEmail.Text), Match.Email) || IsBlank(cmbL4dUtilPerfil.Selected),\n"
    f"    {_msg('erro', _s('Preencha o nome, um email válido e o perfil.'))},\n"
    f"    cmbL4dUtilPerfil.Selected.Value = {PU}.Cliente && IsBlank(cmbL4dUtilCliente.Selected),\n"
    f"    {_msg('erro', _s('Um utilizador com o perfil Cliente tem de ter um cliente associado.'))},\n"
    "    IfError(\n"
    f"        UpdateContext({{{U}: Patch(Utilizadores, If(IsBlank({U}), Defaults(Utilizadores), {U}), {{\n"
    "            Nome: Trim(txtL4dUtilNome.Text),\n"
    "            Email: Lower(Trim(txtL4dUtilEmail.Text)),\n"
    "            Perfil: cmbL4dUtilPerfil.Selected.Value,\n"
    f"            Cliente: If(cmbL4dUtilPerfil.Selected.Value = {PU}.Cliente, cmbL4dUtilCliente.Selected, Blank()),\n"
    "            Ativo: chkL4dUtilAtivo.Value\n"
    "        })}),\n"
    f"        {_msg('erro', '\"Não foi possível guardar (o email já existe?). \" & FirstError.Message')},\n"
    f"        {_msg('ok', GUARDADO)}\n"
    "    )\n"
    ")"
)
DEFINIR_UTIL = (
    "If(\n"
    f"    IsBlank({U}),\n"
    f"    {_msg('erro', _s('Guarde primeiro o utilizador.'))},\n"
    "    With(\n"
    f'        {{r: IfError(DAC2627_Utilizador_DefinirPassword.Run({SES}.token, Text({U}.Utilizador), txtL4dUtilPassword.Text, ""), {FALHA})}},\n'
    "        Reset(txtL4dUtilPassword);\n"
    '        If(r.resultado = "ok",\n'
    f"            Refresh(Utilizadores); UpdateContext({{{U}: LookUp(Utilizadores, Utilizador = {U}.Utilizador)}}); {_msg('ok', 'r.mensagem')},\n"
    f"            {_msg('erro', 'r.mensagem')}\n"
    "        )\n"
    "    )\n"
    ")"
)
BLOQ = "'Bloqueado até'"


def _vista_utilizadores() -> dict:
    estado = lambda a: (f'If(!{a}.Ativo, "Inativo", !IsBlank({a}.{BLOQ}) && {a}.{BLOQ} > Now(), "Bloqueado", IsBlank({a}.{ITER}), "Sem password", "Ativo")')
    cor = lambda a, at, ou: f'If({estado(a)} = "Ativo", {at}, {ou})'
    galeria = _ctl("galL4dUtilizadores", "Gallery@2.15.0", {
        "AccessibleLabel": '="Utilizadores"', "AlignInContainer": "=AlignInContainer.Stretch", "FillPortions": "=0",
        "Height": "=Max(1, Self.AllItemsCount) * Self.TemplateHeight", "Items": "=Sort(Utilizadores, Nome)", "LayoutMinHeight": "=0",
        "OnSelect": f"=UpdateContext({{{U}: ThisItem}}); Reset(txtL4dUtilNome); Reset(txtL4dUtilEmail); Reset(cmbL4dUtilPerfil); "
                    "Reset(cmbL4dUtilCliente); Reset(chkL4dUtilAtivo); Reset(txtL4dUtilPassword)",
        "TabIndex": "=0", "TemplateFill": f"=If(ThisItem.Utilizador = {U}.Utilizador, nfAzulFundo, Color.White)",
        "TemplatePadding": "=0", "TemplateSize": "=70"}, [
        _ctl("lblL4dGUtilNome", "Label@2.5.1", {
            "Color": "=nfTexto", "FontWeight": "=FontWeight.Semibold", "Height": "=28", "OnSelect": "=Select(Parent)", "Size": "=14",
            "Text": '=ThisItem.Nome & "  ·  " & Text(ThisItem.Perfil)', "Width": "=Parent.TemplateWidth - 176", "Wrap": "=false",
            "X": "=16", "Y": "=8"}),
        _ctl("lblL4dGUtilEmail", "Label@2.5.1", {
            "Color": "=nfTextoSuave", "Height": "=24", "OnSelect": "=Select(Parent)", "Size": "=13", "Text": "=ThisItem.Email",
            "Width": "=Parent.TemplateWidth - 32", "Wrap": "=false", "X": "=16", "Y": "=38"}),
        _pilula("btnL4dGUtilEstado", estado("ThisItem"), cor("ThisItem", "nfVerdeTexto", "nfAmbar"), cor("ThisItem", "nfVerdeFundo", "nfAmbarFundo"),
                OnSelect="=Select(Parent)", Width="=140", X="=Parent.TemplateWidth - Self.Width - 16", Y="=9"),
        _ctl("recL4dGUtilSeparador", "Rectangle@2.3.0", {"Fill": "=nfLinha", "Height": "=1", "Width": "=Parent.TemplateWidth",
                                                         "Y": "=Parent.TemplateHeight - 1"}),
    ], "Vertical")
    novo = (f"UpdateContext({{{U}: Blank()}}); Reset(txtL4dUtilNome); Reset(txtL4dUtilEmail); Reset(cmbL4dUtilPerfil); "
            "Reset(cmbL4dUtilCliente); Reset(chkL4dUtilAtivo); Reset(txtL4dUtilPassword)")
    lista = _contentor("conL4dUtilLista", [
        _botao("btnL4dUtilNovo", _s("Novo utilizador"), novo, primario=False, Width="=180"),
        _contentor("conL4dUtilCartao", [galeria], BorderColor="=nfLinha", BorderThickness="=1", Fill="=Color.White",
                   FillPortions="=0", Height="=galL4dUtilizadores.Height + 2", PaddingBottom="=1", PaddingLeft="=1",
                   PaddingRight="=1", PaddingTop="=1", **_raio(12)),
    ], AlignInContainer=f"=If({peq(REV)}, AlignInContainer.Stretch, AlignInContainer.Start)", FillPortions=f"=If({peq(REV)}, 0, 1)",
       Height="=44 + 12 + conL4dUtilCartao.Height", LayoutGap="=12", LayoutMinWidth="=300")

    combo = {"Width": "=Parent.Width - Parent.PaddingLeft - Parent.PaddingRight", "BorderColor": "=nfBorda", "ChevronBackground": "=nfAzul",
             "ChevronFill": "=Color.White", "Height": "=48", "HoverFill": "=nfAzulFundo", "PressedColor": "=Color.White",
             "PressedFill": "=nfAzul", "SelectMultiple": "=false", "SelectionColor": "=Color.White", "SelectionFill": "=nfAzul",
             "TabIndex": "=0"}
    e_cliente = f"cmbL4dUtilPerfil.Selected.Value = {PU}.Cliente"
    desbloquear = (f"Patch(Utilizadores, {U}, {{'Tentativas falhadas': 0, {BLOQ}: Blank()}}); "
                   f"UpdateContext({{{U}: LookUp(Utilizadores, Utilizador = {U}.Utilizador)}}); " + _msg("ok", _s("Utilizador desbloqueado.")))
    filhos = [
        _etiqueta("lblL4dUtilTitulo", f'If(IsBlank({U}), "Novo utilizador", {U}.Nome)', Color="=nfAzul", FontWeight="=FontWeight.Bold", Size="=18"),
        _rotulo("lblL4dUtilNomeRot", "Nome"),
        _entrada("txtL4dUtilNome", "Nome do utilizador", default=f"={U}.Nome"),
        _rotulo("lblL4dUtilEmailRot", "Email"),
        _entrada("txtL4dUtilEmail", "Email do utilizador", default=f"={U}.Email"),
        _rotulo("lblL4dUtilPerfilRot", "Perfil"),
        _ctl("cmbL4dUtilPerfil", "Classic/ComboBox@2.4.0", {
            **combo, "AccessibleLabel": '="Perfil do utilizador"', "DefaultSelectedItems": f"=If(IsBlank({U}), Blank(), [{U}.Perfil])",
            "DisplayFields": '=["Value"]', "InputTextPlaceholder": '="Escolher o perfil"', "Items": f"=Choices({PU})",
            "SearchFields": '=["Value"]'}),
        _rotulo("lblL4dUtilClienteRot", "Cliente associado"),
        _ctl("cmbL4dUtilCliente", "Classic/ComboBox@2.4.0", {
            **combo, "AccessibleLabel": '="Cliente associado ao utilizador"',
            "DefaultSelectedItems": f"=If(IsBlank({U}.Cliente), Blank(), [{U}.Cliente])", "DisplayFields": '=["dac_nome"]',
            "InputTextPlaceholder": '="Escolher o cliente"', "Items": "=Choices([@Utilizadores].dac_Cliente)",
            "SearchFields": '=["dac_nome"]', "Visible": "=" + e_cliente}),
        _ctl("chkL4dUtilAtivo", "Classic/CheckBox@2.1.0", {
            "AlignInContainer": "=AlignInContainer.Stretch", "BorderColor": "=nfBorda", "CheckboxSize": "=24", "CheckmarkFill": "=nfTexto",
            "Color": "=nfTexto", "Default": f"=If(IsBlank({U}), true, {U}.Ativo)", "Height": "=44", "HoverColor": "=nfAzul", "Size": "=14",
            "TabIndex": "=0", "Text": '="Ativo (pode entrar)"'}),
        _contentor("conL4dUtilAcoes", [
            _botao("btnL4dUtilGuardar", _s("Guardar"), GUARDAR_UTIL, Width="=150"),
            _botao("btnL4dUtilDesbloquear", _s("Desbloquear"), desbloquear, primario=False, Width="=160",
                   Visible=f"=!IsBlank({U}.{BLOQ}) && {U}.{BLOQ} > Now()"),
        ], vertical=False, FillPortions="=0", Height="=44", LayoutGap="=12"),
        _rotulo("lblL4dUtilPassRot", "Definir a password (mínimo 8 caracteres)"),
        _entrada("txtL4dUtilPassword", "Nova password do utilizador", password=True, HintText='="Nova password"'),
        _botao("btnL4dUtilDefinir", _s("Definir password"), DEFINIR_UTIL, primario=False, Width="=200",
               DisplayMode=f"=If(IsBlank({U}) || Len(txtL4dUtilPassword.Text) < 8, DisplayMode.Disabled, DisplayMode.Edit)"),
    ]
    filhos[7]["lblL4dUtilClienteRot"]["Properties"]["Visible"] = "=" + e_cliente
    vis = [(None, "lblL4dUtilNomeRot.Height"), (None, "48"), (None, "lblL4dUtilEmailRot.Height"), (None, "48"),
           (None, "lblL4dUtilPerfilRot.Height"), (None, "48"), ("lblL4dUtilClienteRot.Visible", "lblL4dUtilClienteRot.Height"),
           ("cmbL4dUtilCliente.Visible", "48"), (None, "44"), (None, "44"), (None, "lblL4dUtilPassRot.Height"), (None, "48"), (None, "44")]
    form = _cartao("conL4dUtilForm", filhos, AlignInContainer=f"=If({peq(REV)}, AlignInContainer.Stretch, AlignInContainer.Start)",
                   FillPortions=f"=If({peq(REV)}, 0, 1)", Height=_altura("40 + lblL4dUtilTitulo.Height", vis), LayoutMinWidth="=300")
    return _contentor("conL4dVistaUtilizadores", [lista, form], vertical=False, FillPortions="=0",
                      Height=f"=If({peq(REV)}, conL4dUtilLista.Height + conL4dUtilForm.Height + 16, Max(conL4dUtilLista.Height, conL4dUtilForm.Height)) + 2",
                      LayoutDirection=f"=If({peq(REV)}, LayoutDirection.Vertical, LayoutDirection.Horizontal)", LayoutGap="=16",
                      PaddingBottom="=2", Visible=f'=locL4dVista = "utilizadores" && {PERF} = "Admin"')


# ---------------------------------------------------------------- A minha password
MUDAR = (
    "If(\n"
    "    Len(txtL4dPassNova.Text) < 8 || Len(txtL4dPassNova.Text) > 128,\n"
    f"    {_msg('erro', _s('A nova password tem de ter entre 8 e 128 caracteres.'))},\n"
    "    txtL4dPassNova.Text <> txtL4dPassConfirma.Text,\n"
    f"    {_msg('erro', _s('A confirmação não é igual à nova password.'))},\n"
    "    With(\n"
    f'        {{r: IfError(DAC2627_Utilizador_DefinirPassword.Run({SES}.token, "", txtL4dPassNova.Text, txtL4dPassAtual.Text), {FALHA})}},\n'
    "        Reset(txtL4dPassAtual); Reset(txtL4dPassNova); Reset(txtL4dPassConfirma);\n"
    f"        If(r.resultado = \"ok\", {_msg('ok', 'r.mensagem')}, {_msg('erro', 'r.mensagem')})\n"
    "    )\n"
    ")"
)


def _vista_password() -> dict:
    filhos = [
        _etiqueta("lblL4dPassTitulo", _s("Mudar a minha password"), Color="=nfAzul", FontWeight="=FontWeight.Bold", Size="=18"),
        _rotulo("lblL4dPassAtualRot", "Password atual"),
        _entrada("txtL4dPassAtual", "Password atual", password=True),
        _rotulo("lblL4dPassNovaRot", "Nova password (8 a 128 caracteres)"),
        _entrada("txtL4dPassNova", "Nova password", password=True),
        _rotulo("lblL4dPassConfirmaRot", "Confirmar a nova password"),
        _entrada("txtL4dPassConfirma", "Confirmar a nova password", password=True),
        _botao("btnL4dPassMudar", _s("Mudar password"), MUDAR, Width=f"=If({peq(REV)}, Parent.Width - Parent.PaddingLeft - Parent.PaddingRight, 220)"),
    ]
    vis = [(None, "lblL4dPassAtualRot.Height"), (None, "48"), (None, "lblL4dPassNovaRot.Height"), (None, "48"),
           (None, "lblL4dPassConfirmaRot.Height"), (None, "48"), (None, "44")]
    return _cartao("conL4dVistaPassword", filhos, FillPortions="=0", Height=_altura("40 + lblL4dPassTitulo.Height", vis),
                   Visible='=locL4dVista = "password"')


def ecra_revisao() -> dict:
    sair = _botao("btnL4dSair", _s("Sair"), f"Set({SES}, Blank()); Navigate({ENT}, ScreenTransition.UnCover)", primario=False,
                  Width="=90", BorderColor="=Color.White")
    quem = _ctl("lblL4dQuem", "Label@2.5.1", {
        "Align": "=Align.Right", "Color": "=Color.White", "FocusedBorderThickness": "=2", "Height": "=44", "Size": "=13",
        "Text": f'={SES}.nome & "  ·  " & {PERF}', "Visible": f"={REV}.Size > ScreenSize.Small", "Width": "=260"})
    separadores = _contentor("conL4dSeparadores", [
        _separador("btnL4dSepRevisao", "revisao", "Pedidos em revisão"),
        _separador("btnL4dSepRegistar", "registar", "Registar pedido"),
        _separador("btnL4dSepUtilizadores", "utilizadores", "Utilizadores", f'{PERF} = "Admin"'),
        _separador("btnL4dSepPassword", "password", "A minha password"),
        _botao("btnL4dFicha04", _s("Clientes e pedidos (Ficha 04)"), "Navigate(scrL4Pedidos, ScreenTransition.Cover)",
               primario=False, Width="=250", Visible=f'={PERF} <> "Cliente"'),
    ], vertical=False, FillPortions="=0", Height=f"=If({peq(REV)}, 200, If({REV}.Size = ScreenSize.Medium, 100, 44))",
       LayoutGap="=8", LayoutWrap="=true")
    conteudo = _conteudo("L4dR", REV, [
        _etiqueta("lblL4dRevTitulo", f'"Olá, " & {SES}.nome', FontWeight="=FontWeight.Bold", Size=f"=If({peq(REV)}, 20, 24)"),
        _etiqueta("lblL4dRevIntro", f'Switch({PERF}, "Admin", "Perfil Admin: decide os pedidos em revisão, valida as propostas dos Gestores e gere os utilizadores.", '
                                    f'"Gestor", "Perfil Gestor: propõe aprovar ou rejeitar os pedidos em revisão e gere clientes e pedidos na Ficha 04.", '
                                    '"Perfil Cliente: regista pedidos e acompanha os seus. A decisão é do Admin, depois da proposta de um Gestor.")',
                  Color="=nfTextoSuave"),
        separadores,
        _vista_revisao(), _vista_registar(), _vista_utilizadores(), _vista_password(),
    ], 1100)
    raiz = _contentor("conEcraL4dR", [_cabecalho("L4dR", "Ficha 04 · Revisão", [quem, sair]), conteudo], Fill="=nfFundo",
                      Height="=Parent.Height", Width="=Parent.Width")
    # Sem Navigate: o Studio recusa-o no OnVisible (DAC406). Só se chega aqui pelo scrL4Entrar, com sessão,
    # e uma sessão caducada é recusada pelos fluxos, que leem o perfil no Dataverse.
    on_visible = (f'=UpdateContext({{locL4dVista: "revisao", locL4dFiltro: "pordecidir", {P}: Blank(), {U}: Blank(), '
                  'locL4dMsg: "", locL4dMsgTipo: "", locL4dTimer: false});\n'
                  "Refresh(Pedidos)")
    return {"Screens": {REV: {"Properties": {"Fill": "=nfFundo", "OnVisible": on_visible},
                              "Children": [raiz, *_mensagem("L4dR")]}}}


# ======================================================================== scrInicio e scrL4Melhoramento
CARTAO = ('{Num: 7, Ficha: "Ficha 04 · Revisão", Titulo: "Revisão com perfis",\n'
          '     Descricao: "Entrada com password guardada em hash PBKDF2 (serviço no Azure) e perfis Admin, Gestor e Cliente para decidir os pedidos em revisão.", Disponivel: true}')
INTRO_MELHORAMENTO = (
    "Lab 4 com o processamento da aula 7. A app grava o pedido no Dataverse e não fica à espera: o fluxo "
    "DAC2627_Pedido_Classificar trata-o em segundo plano. Até ao limite de revisão (variável de ambiente, 500 €) "
    "o pedido fica Automático, acima dele fica em Revisão e o fluxo DAC2627_Pedido_Notificar avisa os Gestores por email, "
    "e sem valor ou com uma falha técnica fica em Erro. A proposta e a decisão fazem-se no ecrã Ficha 04 · Revisão, com perfis. "
    "Em todos os casos o fluxo regista a data, a justificação e o identificador da execução, para se encontrar a execução "
    "no histórico do Power Automate.")
DECISAO_MELHORAMENTO = (
    '="Revisão humana: " & If(IsBlank(locL4cPedido.Decisao), "—", Text(locL4cPedido.Decisao))'
    ' & If(IsBlank(locL4cPedido.DataDecisao), "", " em " & Text(locL4cPedido.DataDecisao, "dd/mm/yyyy hh:mm"))'
    ' & If(IsBlank(locL4cPedido.ComentarioDecisao), "", Char(10) & locL4cPedido.ComentarioDecisao)'
    " & If(locL4cPedido.Decisao = 'Decisao (Pedidos)'.Aprovado || locL4cPedido.Decisao = 'Decisao (Pedidos)'.Rejeitado, \"\","
    ' Char(10) & "Os Gestores foram avisados por email. A proposta e a decisão fazem-se no ecrã Ficha 04 · Revisão (sétimo cartão do início).")'
)


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
                if "Num: 7" not in itens:
                    itens = re.sub(r'(Disponivel: true\})\s*\n(\s*)\)\s*$', r'\1,\n\2    ' + CARTAO.replace("\\", "\\\\") + r'\n\2)', itens)
                    ctl.definir("Items", itens)
                sel = str(ctl.prop("OnSelect"))
                if ENT not in sel:
                    sel = sel.replace("6, Navigate(scrL4Melhoramento, ScreenTransition.Cover)",
                                      "6, Navigate(scrL4Melhoramento, ScreenTransition.Cover),\n"
                                      f"        7, Navigate({ENT}, ScreenTransition.Cover)")
                    ctl.definir("OnSelect", sel)
    if "scrL4Melhoramento" in ecras:
        for ctl in yamlio.controlos(doc):
            if ctl.nome == "lblL4cIntro":
                ctl.definir("Text", "=" + _s(INTRO_MELHORAMENTO))
            elif ctl.nome == "lblL4cDecisao":
                ctl.definir("Text", DECISAO_MELHORAMENTO)


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
    for nome, gerar in ((ENT, ecra_entrar), (REV, ecra_revisao)):
        novo = raiz / "src" / "screens" / f"{nome}.pa.yaml"
        texto = yamlio.escrever_texto(gerar())
        if not novo.exists() or novo.read_text(encoding="utf-8") != texto:
            novo.write_text(texto, encoding="utf-8")
            mudados += 1
            print("escrito:", novo.relative_to(raiz))
    print(f"m008: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
