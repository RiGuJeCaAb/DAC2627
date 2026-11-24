"""Migração 009 · v1.7.0 · Ficha 04 numa só app, em três modos sobre o mesmo ecrã.

Corre sobre src/ depois da m008 e é idempotente: correr de novo não muda nada.

    python -m tools.migracoes.m009_v1_7_ficha04_tres_modos

Pedido do utilizador (24/11/2026): a Ficha 04 é uma app só, por passos. A Ficha 04 (Lab 4) é a base, o
Melhoramento (aula 7) é a mesma experiência com acrescentos, e a Revisão é tudo isto atrás da entrada com
password e perfis. Até à v1.6.0 eram três ecrãs separados, ligados só pelas tabelas.

O que faz:
  1. scrL4Pedidos recebe o nível pela navegação, locL4Nivel = "pedidos", "melhoramento" ou "revisao"
     (Navigate com registo, a partir do scrInicio e do scrL4Entrar). Em "pedidos" fica igual à v1.6.0.
  2. Acrescentos do Melhoramento, prefixo L4c (visíveis em "melhoramento" e "revisao"): segunda fila de
     separadores (Automático, Revisão, Erro), pílula do tratamento e justificação em cada linha da lista,
     detalhe do pedido (conL4cDetalhe) com o processamento, Atualizar estado e Reprocessar, a consulta
     ao estado depois de criar (tmrL4cEstado) e os botões de teste da aula por baixo do formulário.
  3. Acrescentos da Revisão, prefixo L4d (visíveis em "revisao"): quem entrou no cabeçalho, com Sair,
     perfis (o Cliente só vê e regista para o seu cliente, o Gestor propõe, o Admin decide), separador
     «Por decidir», proposta e decisão no detalhe, Registado por ao criar, e as áreas Utilizadores (Admin)
     e A minha password, abertas por ícones no cabeçalho.
  4. scrInicio: os cartões 4 e 6 abrem o scrL4Pedidos com o nível, o 7 abre o scrL4Entrar.
  5. scrL4Entrar: depois de entrar, abre o scrL4Pedidos em "revisao".
  6. Retira os ecrãs scrL4Melhoramento e scrL4Revisao (o conteúdo passou para o scrL4Pedidos).
  7. App.Formulas: nfVersao passa a "1.7.0".
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.dac import projeto, yamlio
from tools.migracoes import m008_v1_6_ficha04_revisao as B
from tools.migracoes.m007_v1_5_ficha04_melhoramento import (
    _botao, _contentor, _ctl, _etiqueta, _pilula as _pilula_tratamento, _raio, _s, _cores_tratamento,
)

VERSAO = "1.7.0"
ECRA = "scrL4Pedidos"
ENT = "scrL4Entrar"
RETIRADOS = ("scrL4Melhoramento", "scrL4Revisao")
PEQ = f"{ECRA}.Size = ScreenSize.Small"
TR = "'Tratamento (Pedidos)'"
DEC = "'Decisao (Pedidos)'"
SES = "gblL4dSessao"
PERF = f"{SES}.perfil"
P = "locL4Pedido"

NIV = "locL4Nivel"
M = f'({NIV} = "melhoramento" || {NIV} = "revisao")'     # acrescentos do Melhoramento (também na Revisão)
R = f'{NIV} = "revisao"'                                  # acrescentos da Revisão
CLI = f'({R} && {PERF} = "Cliente")'                      # perfil Cliente: só o seu cliente
C_ID = f'GUID(Coalesce({SES}.clienteid, "00000000-0000-0000-0000-000000000000"))'
EM_REVISAO = f"{P}.Tratamento = {TR}.Revisão"
FINAL = f"({P}.Decisao = {DEC}.Aprovado || {P}.Decisao = {DEC}.Rejeitado)"
POR_DECIDIR = f"Tratamento = {TR}.Revisão, Decisao <> {DEC}.Aprovado, Decisao <> {DEC}.Rejeitado"

# O que vem da m008 (ecrã scrL4Revisao) passa a viver no scrL4Pedidos: o tamanho é o deste ecrã,
# o pedido é o locL4Pedido da Ficha 04, as mensagens usam a faixa conL4Mensagem e as vistas passam a áreas.
MAPA = (
    ("scrL4Revisao.Size", f"{ECRA}.Size"),
    ("locL4dPedido", P),
    ("locL4dMsgTipo", "locL4MsgTipo"),
    ("locL4dMsg", "locL4Msg"),
    ("locL4dTimer", "locL4Timer"),
    ('locL4dVista = "utilizadores"', 'locL4Area = "utilizadores"'),
    ('locL4dVista = "password"', 'locL4Area = "password"'),
)


def _remap(obj):
    if isinstance(obj, str):
        for de, para in MAPA:
            obj = obj.replace(de, para)
        return obj
    if isinstance(obj, list):
        return [_remap(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _remap(v) for k, v in obj.items()}
    return obj


def _procurar(lista: list, nome: str) -> dict | None:
    for item in lista or []:
        for n, corpo in item.items():
            if n == nome:
                return item
            achado = _procurar(corpo.get("Children"), nome)
            if achado:
                return achado
    return None


def _props(item: dict) -> dict:
    return next(iter(item.values())).setdefault("Properties", {})


# ======================================================================== lista de pedidos
def _vista(cond: str) -> str:
    """Pedidos de uma vista, de todos os clientes ou só do escolhido: dois Filter delegáveis escolhidos por fora."""
    return (f"If(IsBlank(locL4Cliente), Sort(Filter(Pedidos, {cond}), DataPedido, SortOrder.Descending), "
            f"Sort(Filter(Pedidos, {cond}, Clientes.Cliente = locL4Cliente.Cliente), DataPedido, SortOrder.Descending))")


def _contar(cond: str) -> str:
    return (f"If(IsBlank(locL4Cliente), CountRows(Filter(Pedidos, {cond})), "
            f"CountRows(Filter(Pedidos, {cond}, Clientes.Cliente = locL4Cliente.Cliente)))")


# as três vistas do Lab 4, como estavam na v1.6.0
LAB4_PENDENTES = ("If(IsBlank(locL4Cliente), Sort(Filter(Pedidos, 'Pedidos (Vistas)'.'Pedidos Pendentes'), DataPedido, SortOrder.Descending), "
                  "Sort(Filter(Pedidos, 'Pedidos (Vistas)'.'Pedidos Pendentes', Clientes.Cliente = locL4Cliente.Cliente), DataPedido, SortOrder.Descending))")
LAB4_CONCLUIDOS = ("If(IsBlank(locL4Cliente), Sort(Filter(Pedidos, 'Pedidos (Vistas)'.'Pedidos Concluídos'), DataPedido, SortOrder.Descending), "
                   "Sort(Filter(Pedidos, 'Pedidos (Vistas)'.'Pedidos Concluídos', Clientes.Cliente = locL4Cliente.Cliente), DataPedido, SortOrder.Descending))")
LAB4_TODOS = ("If(IsBlank(locL4Cliente), Sort(Filter(Pedidos, Estado = 'Estado (Pedidos)'.Ativo), DataPedido, SortOrder.Descending), "
              "Sort(Filter(Pedidos, Estado = 'Estado (Pedidos)'.Ativo && Clientes.Cliente = locL4Cliente.Cliente), DataPedido, SortOrder.Descending))")
ITENS = (
    "=Switch(locL4Vista,\n"
    f'    "pendentes", {LAB4_PENDENTES},\n'
    f'    "concluidos", {LAB4_CONCLUIDOS},\n'
    f'    "auto", {_vista(f"Tratamento = {TR}.Automático")},\n'
    f'    "revisao", If({R}, {_vista(POR_DECIDIR)}, {_vista(f"Tratamento = {TR}.Revisão")}),\n'
    f'    "erro", {_vista(f"Tratamento = {TR}.Erro")},\n'
    f"    {LAB4_TODOS}\n"
    ")"
)
RESUMO = (
    '=Switch(locL4Vista, "pendentes", "Vista do Dataverse «Pedidos Pendentes» · mais recentes primeiro", '
    '"concluidos", "Vista do Dataverse «Pedidos Concluídos» · mais recentes primeiro", '
    '"auto", "Classificados Automático pelo fluxo · mais recentes primeiro", '
    f'"revisao", If({R}, "Em revisão e ainda sem decisão final · mais recentes primeiro", '
    '"Classificados Revisão pelo fluxo · mais recentes primeiro"), '
    '"erro", "Classificados Erro pelo fluxo, sem valor ou com uma falha técnica · mais recentes primeiro", '
    '"Todos os pedidos ativos · mais recentes primeiro")'
)
SELECIONAR_LAB4 = ('UpdateContext({locL4Pedido: ThisItem, locL4Modo: "pedido", locL4Acao: "editar", locL4Msg: "", '
                   'locL4Timer: false}); EditForm(frmL4Pedido)')
SELECIONAR = (
    f"=If({M},\n"
    f'    UpdateContext({{{P}: ThisItem, locL4Modo: "detalhe", locL4Acao: "", locL4cAguardar: false, locL4Msg: "", '
    "locL4Timer: false}); Reset(txtL4dComentario),\n"
    f"    {SELECIONAR_LAB4}\n"
    ")"
)


def _separador(nome: str, chave: str, texto: str) -> dict:
    """Separador com o aspeto dos do Lab 4 (btnL4SepTodos)."""
    ativo = f'locL4Vista = "{chave}"'
    return _ctl(nome, "Classic/Button@2.2.0", {
        "BorderColor": "=nfAzul", "Color": f"=If({ativo}, Color.White, nfAzul)", "Fill": f"=If({ativo}, nfAzul, Color.White)",
        "FillPortions": "=1", "Height": "=44", "HoverColor": f"=If({ativo}, Color.White, nfAzul)",
        "HoverFill": f"=If({ativo}, nfAzul, nfAzulClaro)", "LayoutMinWidth": "=0", "OnSelect": f'=UpdateContext({{locL4Vista: "{chave}"}})',
        "PressedColor": f"=If({ativo}, Color.White, nfAzul)", "PressedFill": f"=If({ativo}, nfAzul, nfAzulClaro)",
        "Size": f"=Switch({ECRA}.Size, ScreenSize.Small, 11, ScreenSize.Medium, 11, 13)", "Text": "=" + texto, "Width": "=150",
        **_raio(12)})


def _separadores_processamento() -> dict:
    return _contentor("conL4cSeparadores", [
        _separador("btnL4cSepAuto", "auto", f'"Automático (" & {_contar(f"Tratamento = {TR}.Automático")} & ")"'),
        _separador("btnL4cSepRevisao", "revisao",
                   f'If({R}, "Por decidir (" & {_contar(POR_DECIDIR)} & ")", "Revisão (" & {_contar(f"Tratamento = {TR}.Revisão")} & ")")'),
        _separador("btnL4cSepErro", "erro", f'"Erro (" & {_contar(f"Tratamento = {TR}.Erro")} & ")"'),
    ], vertical=False, FillPortions="=0", Height="=44", LayoutGap="=8", Visible=f"={M} && IsBlank(locL4Modo)")


def _linha_galeria() -> list:
    """Terceira linha de cada pedido: a justificação do fluxo e a pílula do tratamento (na Revisão, a da decisão)."""
    t_tr, c_tr, f_tr = _cores_tratamento("ThisItem")
    t_de, c_de, f_de = B._cores_decisao("ThisItem")
    dec = f"{R} && ThisItem.Tratamento = {TR}.Revisão && !IsBlank(ThisItem.Decisao)"
    y = f"If({PEQ}, 90, 72)"
    return [
        _ctl("lblL4cGObs", "Label@2.5.1", {
            "Color": "=nfTextoSuave", "Height": "=24", "OnSelect": "=Select(Parent)", "Size": "=12",
            "Text": '=Coalesce(ThisItem.ObservacoesProcessamento, If(IsBlank(ThisItem.Tratamento), "Ainda não processado pelo fluxo.", ""))',
            "Visible": "=" + M, "Width": "=Parent.TemplateWidth - 32 - 158", "Wrap": "=false", "X": "=16", "Y": "=" + y}),
        _ctl("btnL4cGTratamento", "Classic/Button@2.2.0", {
            "BorderThickness": "=0", "Color": f"=If({dec}, {c_de}, {c_tr})", "DisabledColor": "=Self.Color", "DisabledFill": "=Self.Fill",
            "DisplayMode": "=DisplayMode.View", "Fill": f"=If({dec}, {f_de}, {f_tr})", "FontWeight": "=FontWeight.Bold", "Height": "=26",
            "HoverColor": "=Self.Color", "HoverFill": "=Self.Fill", "OnSelect": "=Select(Parent)", "PressedFill": "=Self.Fill",
            "Size": "=11", "TabIndex": "=-1", "Text": f"=If({dec}, {t_de}, {t_tr})", "Visible": "=" + M, "Width": "=150",
            "X": "=Parent.TemplateWidth - Self.Width - 16", "Y": f"=If({PEQ}, 89, 71)", **_raio(13)}),
    ]


# ======================================================================== detalhe do pedido (Melhoramento e Revisão)
REFRESCAR = f"Refresh(Pedidos); UpdateContext({{{P}: LookUp(Pedidos, Pedido = {P}.Pedido)}})"
REPROCESSAR = (
    "With(\n"
    "    {r: IfError(\n"
    f"        DAC2627_Pedido_Reprocessar.Run(Text({P}.Pedido)),\n"
    '        {resultado: "erro", mensagem: "Não foi possível chamar o fluxo. " & FirstError.Message}\n'
    "    )},\n"
    '    If(r.resultado = "ok",\n'
    '        UpdateContext({locL4cAguardar: true, locL4cTentativas: 0, locL4MsgTipo: "ok", locL4Timer: true, locL4Msg: r.mensagem}),\n'
    '        UpdateContext({locL4MsgTipo: "erro", locL4Timer: false, locL4Msg: r.mensagem})\n'
    "    )\n"
    ")"
)
SONDAR = (
    "=Refresh(Pedidos);\n"
    f"UpdateContext({{{P}: LookUp(Pedidos, Pedido = {P}.Pedido), locL4cTentativas: locL4cTentativas + 1}});\n"
    "If(\n"
    f"    {P}.Processado,\n"
    f'    UpdateContext({{locL4cAguardar: false, locL4MsgTipo: If({P}.Tratamento = {TR}.Erro, "erro", "ok"), locL4Timer: true,\n'
    f'        locL4Msg: "Pedido " & {P}.NumeroPedido & " processado: " & Text({P}.Tratamento) & "."}}),\n'
    "    locL4cTentativas >= 20,\n"
    '    UpdateContext({locL4cAguardar: false, locL4MsgTipo: "erro", locL4Timer: false,\n'
    '        locL4Msg: "O fluxo ainda não terminou ao fim de 60 s. Use Atualizar estado mais tarde."})\n'
    ")"
)
REGRA = ("O fluxo DAC2627_Pedido_Classificar trata o pedido em segundo plano, sem a app ficar à espera. Até ao limite de "
         "revisão (variável de ambiente, 500 €) fica Automático, acima dele fica em Revisão e o fluxo DAC2627_Pedido_Notificar "
         "avisa os Gestores por email, e sem valor ou com uma falha técnica fica em Erro.")
NOTA_DECISAO = (
    f'"Decisão: " & If(IsBlank({P}.Decisao), "—", Text({P}.Decisao))'
    f' & If(IsBlank({P}.DataDecisao), "", " em " & Text({P}.DataDecisao, "dd/mm/yyyy hh:mm"))'
    f' & If(IsBlank({P}.ComentarioDecisao), "", Char(10) & {P}.ComentarioDecisao)'
    f' & If({FINAL}, "", Char(10) & "A proposta e a decisão fazem-se com perfis, na Ficha 04 · Revisão (sétimo cartão do início).")'
)


def _revisao_no_detalhe() -> list:
    """Proposta, decisão e ações da Revisão, tiradas do detalhe da m008 e só visíveis com o pedido em revisão."""
    origem = _remap(B._vista_revisao())
    filhos = next(iter(_procurar([origem], "conL4dDetalhe").values()))["Children"]
    nomes = ("lblL4dDetProposta", "lblL4dDetDecisao", "lblL4dDetEspera", "lblL4dSoLeitura", "lblL4dComentarioRot",
             "txtL4dComentario", "conL4dAcoesGestor", "conL4dAcoesAdmin")
    escolhidos = []
    for nome in nomes:
        item = next(f for f in filhos if nome in f)
        p = _props(item)
        p["Visible"] = f"={R} && {EM_REVISAO} && ({p['Visible'].lstrip('=')})"
        escolhidos.append(item)
    return escolhidos


def _detalhe() -> dict:
    tem_rev = f"({EM_REVISAO} || !IsBlank({P}.Decisao))"
    cab = _contentor("conL4cDetCab", [
        _etiqueta("lblL4cDetCliente", f"{P}.Clientes.Nome", AlignInContainer="=AlignInContainer.Center", AutoHeight="=false",
                  FillPortions="=1", FontWeight="=FontWeight.Semibold", Height="=32", Size="=16", Wrap="=false"),
        _pilula_tratamento("btnL4cTratamento", P, AlignInContainer="=AlignInContainer.Center"),
    ], vertical=False, FillPortions="=0", Height="=36", LayoutAlignItems="=LayoutAlignItems.Center", LayoutGap="=12")
    filhos = [
        cab,
        B._linha("conL4cDetLinha", "nfLinha"),
        B._linha_info("conL4cDetData", "Data", f'Text({P}.DataPedido, "dd/mm/yyyy")'
                      f' & If(IsBlank({P}.\'Registado por\'), "", "  ·  registado por " & {P}.\'Registado por\'.Nome)', 104),
        B._linha_info("conL4cDetEstado", "Estado", f"Text({P}.EstadoPedido)", 104),
        B._linha_info("conL4cDetValor", "Valor", f'If(IsBlank({P}.Valor), "sem valor", Text({P}.Valor, "[$-pt-PT]0,00") & " €")', 104),
        B._linha_info("conL4cDetDescricao", "Descrição", f'Coalesce({P}.\'Descrição\', "—")', 104),
        _etiqueta("lblL4cProcTitulo", _s("Processamento automático"), Color="=nfAzul", FontWeight="=FontWeight.Bold", Size="=16"),
        _etiqueta("lblL4cAguarda",
                  '"A aguardar o fluxo DAC2627_Pedido_Classificar · consulta " & (locL4cTentativas + 1) & " de 20, a cada 3 s."',
                  Color="=nfAmbar", Fill="=nfAmbarFundo", FontWeight="=FontWeight.Semibold", PaddingBottom="=10",
                  PaddingLeft="=14", PaddingRight="=14", PaddingTop="=10", Visible="=locL4cAguardar"),
        B._linha_info("conL4cDetProcessado", "Processado",
                      f'If({P}.Processado, "Sim, em " & Text({P}.DataProcessamento, "dd/mm/yyyy hh:mm:ss"), "Ainda não")', 104),
        B._linha_info("conL4cDetObs", "Justificação", f'Coalesce({P}.ObservacoesProcessamento, "—")', 104),
        B._linha_info("conL4cDetExecucao", "Execução", f'Coalesce({P}.IdExecucao, "—")', 104),
        _contentor("conL4cAcoes", [
            _botao("btnL4cAtualizar", _s("Atualizar estado"), REFRESCAR, primario=False, Width="=180"),
            _botao("btnL4cReprocessar", _s("Reprocessar"), REPROCESSAR,
                   DisplayMode="=If(locL4cAguardar, DisplayMode.Disabled, DisplayMode.Edit)", Visible=f"=!{CLI}", Width="=160"),
        ], vertical=False, FillPortions="=0", Height=f"=If({PEQ}, 100, 44)", LayoutGap="=12", LayoutWrap="=true"),
        _etiqueta("lblL4cProcNota", _s(REGRA), Color="=nfTextoSuave", Size="=13"),
        B._linha("conL4cDetLinhaRev", "nfLinha", Visible="=" + tem_rev),
        _etiqueta("lblL4cRevTitulo", _s("Revisão humana"), Color="=nfAzul", FontWeight="=FontWeight.Bold", Size="=16",
                  Visible="=" + tem_rev),
        B._caixa("lblL4cDecisao", NOTA_DECISAO, "nfAmbar", "nfAmbarFundo", f"!({R}) && {tem_rev}"),
        *_revisao_no_detalhe(),
    ]
    return _contentor("conL4cDetalhe", filhos, LayoutGap="=10", LayoutOverflowY="=LayoutOverflow.Scroll",
                      Visible=f'={M} && locL4Modo = "detalhe"')


def _testes() -> dict:
    def teste(valor: str, texto: str, largura: int) -> dict:
        return _botao(f"btnL4cTeste{texto.replace(' ', '')}", _s(texto),
                      f'UpdateContext({{locL4cValorTeste: "{valor}"}}); Reset(txtL4PedValor)', primario=False, BorderThickness="=1",
                      Size="=13", Width=f"={largura}")
    return _contentor("conL4cTestes", [
        _etiqueta("lblL4cTestesRot", _s("Testes da aula:"), AlignInContainer="=AlignInContainer.Center", AutoHeight="=false",
                  Color="=nfTextoSuave", Height="=44", Size="=13", Width="=110"),
        teste("100", "100", 72), teste("500", "500", 72), teste("750", "750", 72), teste("sem", "Sem valor", 120),
    ], vertical=False, FillPortions="=0", Height=f"=If({PEQ}, 96, 44)", LayoutAlignItems="=LayoutAlignItems.Center",
       LayoutGap="=8", LayoutWrap="=true", Visible=f'={M} && locL4Modo = "pedido" && locL4Acao = "criar"')


def _rodape(nome: str, texto: str, acao: str, primario: bool, visivel: str) -> dict:
    """Botão do rodapé com o aspeto dos do Lab 4 (btnL4Cancelar, btnL4Guardar)."""
    cor = {"Color": "=Color.White", "Fill": "=nfAzul"} if primario else {
        "BorderColor": "=nfAzul", "BorderThickness": "=1", "Color": "=nfAzul", "Fill": "=Color.White"}
    return _ctl(nome, "Classic/Button@2.2.0", {
        **cor, "FillPortions": f"=If({PEQ}, 1, 0)", "Height": "=44", "LayoutMinWidth": "=0", "OnSelect": "=" + acao,
        "Size": f"=If({PEQ}, 11, 13)", "Text": "=" + texto, "Visible": "=" + visivel, "Width": "=150", **_raio(12)})


# ======================================================================== cabeçalho e áreas da Revisão
def _cabecalho_revisao() -> list:
    iniciais = B._pilula("btnL4dIniciais", B.INICIAIS, "nfAzul", "Color.White", Height="=36", Size="=13", Visible="=" + R,
                         Width="=36", **_raio(18))
    quem = _ctl("lblL4dQuem", "Label@2.5.1", {
        "Color": "=Color.White", "FocusedBorderThickness": "=2", "Height": "=44", "Size": "=14", "Text": f"={SES}.nome",
        "Visible": f"={R} && {ECRA}.Size > ScreenSize.Small", "Width": "=Min(220, Len(Self.Text) * 9 + 8)", "Wrap": "=false"})
    perfil = B._pilula("btnL4dPerfil", PERF, "nfAzul", "nfAzulClaro", Visible=f"={R} && {ECRA}.Size > ScreenSize.Small", Width="=76")

    def icone(nome: str, icon: str, rotulo: str, area: str, visivel: str) -> dict:
        return _ctl(nome, "Classic/Icon@2.5.0", {
            "AccessibleLabel": "=" + _s(rotulo), "Color": "=Color.White", "Height": "=44", "Icon": "=" + icon,
            "OnSelect": f'=UpdateContext({{locL4Area: If(locL4Area = "{area}", "", "{area}"), locL4dUtil: Blank()}})',
            "PaddingBottom": "=10", "PaddingLeft": "=10", "PaddingRight": "=10", "PaddingTop": "=10", "TabIndex": "=0",
            "Visible": "=" + visivel, "Width": "=44"})
    sair = _botao("btnL4dSair", _s("Sair"), f"Set({SES}, Blank()); Navigate({ENT}, ScreenTransition.UnCover)", primario=False,
                  BorderColor="=Color.White", BorderThickness="=1", Color="=Color.White", Fill="=Color.Transparent",
                  HoverColor="=nfAzul", HoverFill="=Color.White", PressedColor="=nfAzul", PressedFill="=Color.White",
                  Visible="=" + R, Width=f"=If({PEQ}, 64, 80)")
    return [iniciais, quem, perfil,
            icone("icoL4dUtilizadores", "Icon.People", "Gerir os utilizadores", "utilizadores", f'{R} && {PERF} = "Admin"'),
            icone("icoL4dPassword", "Icon.Lock", "Mudar a minha password", "password", R),
            sair]


def _areas() -> list:
    topo = _contentor("conL4dAreaTopo", [
        _etiqueta("lblL4dAreaTitulo", 'If(locL4Area = "utilizadores", "Utilizadores", "A minha password")',
                  AlignInContainer="=AlignInContainer.Center", AutoHeight="=false", FillPortions="=1", FontWeight="=FontWeight.Bold",
                  Height="=44", Size=f"=If({PEQ}, 18, 22)", Wrap="=false"),
        _botao("btnL4dAreaVoltar", _s("‹ Pedidos"), 'UpdateContext({locL4Area: "", locL4dUtil: Blank()})', primario=False,
               BorderThickness="=1", Width="=130"),
    ], vertical=False, FillPortions="=0", Height="=44", LayoutGap="=12", Visible="=!IsBlank(locL4Area)")
    utilizadores = _remap(B._vista_utilizadores())
    _props(utilizadores)["Visible"] = f'={R} && locL4Area = "utilizadores" && {PERF} = "Admin"'
    password = _remap(B._vista_password())
    _props(password)["Visible"] = f'={R} && locL4Area = "password"'
    return [topo, utilizadores, password]


# ======================================================================== scrL4Pedidos
ON_VISIBLE = (
    f'=UpdateContext({{locL4Vista: "todos", locL4Painel: {CLI}, locL4Cliente: If({CLI}, LookUp(Clientes, Cliente = {C_ID})), '
    'locL4Pedido: Blank(), locL4Modo: "", locL4Acao: "", locL4Confirmar: "", locL4UltimaConf: "", locL4Msg: "", locL4MsgTipo: "", '
    'locL4Timer: false, locL4Area: "", locL4cAguardar: false, locL4cTentativas: 0, locL4cValorTeste: "", locL4dUtil: Blank()});\n'
    "ResetForm(frmL4Cliente); ResetForm(frmL4Pedido)"
)
TITULO = (f'=If({PEQ} && {R}, "Ficha 04", Switch({NIV}, "melhoramento", "Ficha 04 · Melhoramento", '
          '"revisao", "Ficha 04 · Revisão", "Ficha 04 · Clientes e Pedidos"))')
CRIADO = (
    f'=If({R} && locL4Acao = "criar", Patch(Pedidos, frmL4Pedido.LastSubmit, '
    f"{{'Registado por': LookUp(Utilizadores, Utilizador = GUID({SES}.utilizadorid))}}));\n"
    f'UpdateContext({{{P}: frmL4Pedido.LastSubmit, locL4Modo: If({M}, "detalhe", ""), locL4cAguardar: {M} && locL4Acao = "criar", '
    'locL4cTentativas: 0, locL4cValorTeste: "", locL4MsgTipo: "ok", locL4Timer: true, '
    'locL4Msg: If(locL4Acao = "criar", "Pedido " & frmL4Pedido.LastSubmit.NumeroPedido & " criado." & '
    f'If({M}, " O fluxo está a classificá-lo.", ""), "Alterações ao pedido " & frmL4Pedido.LastSubmit.NumeroPedido & " guardadas.")}})'
)
VALOR_DEFAULT = ('=If(frmL4Pedido.Mode = FormMode.New && locL4cValorTeste = "sem", "", '
                 "frmL4Pedido.Mode = FormMode.New && !IsBlank(locL4cValorTeste), locL4cValorTeste, "
                 'IsBlank(Parent.Default), "", Text(Parent.Default, "[$-pt-PT]0,00"))')
CANCELAR = ("=ResetForm(frmL4Cliente);\nResetForm(frmL4Pedido);\n"
            f'UpdateContext({{locL4Modo: If({M} && locL4Modo = "pedido" && locL4Acao = "editar", "detalhe", ""), '
            'locL4Confirmar: "", locL4cValorTeste: ""})')
EM_FORMULARIO = '=locL4Modo = "cliente" || locL4Modo = "pedido"'
NOVO_PEDIDO = ('=NewForm(frmL4Pedido);\nUpdateContext({locL4Pedido: Blank(), locL4Modo: "pedido", locL4Acao: "criar", '
               'locL4cValorTeste: "", locL4cAguardar: false, locL4Msg: "", locL4Timer: false})')
PAINEL_TITULO = (
    '=Switch(locL4Modo, "cliente", If(locL4Acao = "criar", "Novo cliente", "Editar cliente"), '
    '"pedido", If(locL4Acao = "criar", "Novo pedido · " & locL4Cliente.Nome, "Pedido " & locL4Pedido.NumeroPedido), '
    '"detalhe", "Pedido " & locL4Pedido.NumeroPedido, '
    'If(IsBlank(locL4Cliente), "Todos os clientes", locL4Cliente.Nome))'
)
CLIENTES_LISTA = (f"=If({CLI}, Filter(Clientes, Cliente = {C_ID}), "
                  "Sort(Filter(Clientes, StartsWith(Nome, txtL4Pesquisa.Text)), Nome))")

# propriedades dos controlos do Lab 4 que mudam: valor final (idempotente)
PROPRIEDADES = {
    "conCabL4": {"LayoutGap": f"=If({PEQ}, 8, 12)", "PaddingLeft": f"=If({PEQ}, 12, 24)", "PaddingRight": f"=If({PEQ}, 12, 24)"},
    "lblCabL4": {"Text": TITULO, "Wrap": "=false"},
    "conConteudoL4": {"LayoutOverflowY": "=If(IsBlank(locL4Area), LayoutOverflow.Hide, LayoutOverflow.Scroll)"},
    "conL4Barra": {"Visible": f"=!({PEQ} && locL4Painel) && IsBlank(locL4Area) && !{CLI}"},
    "conL4Corpo": {"Visible": "=IsBlank(locL4Area)"},
    "galL4Clientes": {"Items": CLIENTES_LISTA},
    "btnL4VoltarLista": {"Visible": f"={PEQ} && IsBlank(locL4Modo) && !{CLI}"},
    "lblL4PainelTitulo": {"Text": PAINEL_TITULO},
    "lblL4Resumo": {"Text": RESUMO},
    "galL4Pedidos": {"Items": ITENS, "OnSelect": SELECIONAR,
                     "TemplateSize": f"=If({PEQ}, 96, 80) + If({M}, 32, 0)"},
    "frmL4Pedido": {"OnSuccess": CRIADO},
    "Estado (dac_estado)_DataCard1": {"DisplayMode": f"=If({CLI}, DisplayMode.View, Parent.DisplayMode)"},
    "txtL4PedValor": {"Default": VALOR_DEFAULT},
    "btnL4RemoverCliente": {"Visible": f"=IsBlank(locL4Modo) && !IsBlank(locL4Cliente) && !{CLI}"},
    "btnL4EditarCliente": {"Visible": f"=IsBlank(locL4Modo) && !IsBlank(locL4Cliente) && !{CLI}"},
    "btnL4NovoCliente": {"Visible": f"=IsBlank(locL4Modo) && !{CLI}"},
    "btnL4NovoPedido": {"OnSelect": NOVO_PEDIDO},
    "btnL4RemoverPedido": {"Visible": f'=locL4Modo = "pedido" && locL4Acao = "editar" && !{CLI}'},
    "btnL4Cancelar": {"OnSelect": CANCELAR, "Visible": EM_FORMULARIO},
    "btnL4Guardar": {"Visible": EM_FORMULARIO},
    "conL4Mensagem": {"Height": "=Max(56, lblL4Mensagem.Height + 32)"},
    "lblL4Mensagem": {"AutoHeight": "=true"},
}


def _por(lista: list, novo: dict, depois_de: str | None = None, no_inicio: bool = False) -> None:
    """Põe o controlo novo na lista (a seguir a depois_de, no início ou no fim), tirando primeiro o que lá estiver com o mesmo nome."""
    nome = next(iter(novo))
    lista[:] = [x for x in lista if nome not in x]
    if no_inicio:
        lista.insert(0, novo)
    elif depois_de is None:
        lista.append(novo)
    else:
        i = next(i for i, x in enumerate(lista) if depois_de in x)
        lista.insert(i + 1, novo)


def _filhos(doc: dict, nome: str) -> list:
    return next(iter(_procurar(doc["Screens"][ECRA]["Children"], nome).values())).setdefault("Children", [])


def migrar_pedidos(doc: dict) -> None:
    ecra = doc["Screens"][ECRA]
    ecra.setdefault("Properties", {})["OnVisible"] = ON_VISIBLE
    for ctl in yamlio.controlos(doc):
        for k, v in PROPRIEDADES.get(ctl.nome, {}).items():
            ctl.definir(k, v)
    # cabeçalho: quem entrou, áreas e Sair (Revisão)
    cab = _filhos(doc, "conCabL4")
    anterior = "lblCabL4"
    for novo in _cabecalho_revisao():
        _por(cab, novo, anterior)
        anterior = next(iter(novo))
    # áreas Utilizadores e A minha password (Revisão)
    conteudo = _filhos(doc, "conConteudoL4")
    anterior = "conL4Corpo"
    for novo in _areas():
        _por(conteudo, novo, anterior)
        anterior = next(iter(novo))
    # painel: separadores do processamento, detalhe e testes da aula (Melhoramento)
    painel = _filhos(doc, "conL4Painel")
    _por(painel, _separadores_processamento(), "conL4Separadores")
    _por(painel, _detalhe(), "frmL4Pedido")
    _por(painel, _testes(), "conL4cDetalhe")
    rodape = _filhos(doc, "conL4Rodape")
    _por(rodape, _rodape("btnL4cEditar", _s("Editar pedido"),
                         'UpdateContext({locL4Modo: "pedido", locL4Acao: "editar", locL4cAguardar: false, locL4cValorTeste: ""}); '
                         "EditForm(frmL4Pedido)", True, f'locL4Modo = "detalhe" && !{CLI}'), no_inicio=True)
    _por(rodape, _rodape("btnL4cVoltar", _s("‹ Pedidos"), 'UpdateContext({locL4Modo: "", locL4cAguardar: false})', False,
                         'locL4Modo = "detalhe"'), no_inicio=True)
    # linha de cada pedido: justificação e tratamento
    linha = _filhos(doc, "galL4Pedidos")
    for novo in _linha_galeria():
        _por(linha, novo, "btnL4PedEstado")
    # consulta ao estado depois de criar
    _por(ecra["Children"], _ctl("tmrL4cEstado", "Timer@2.1.0", {
        "Duration": "=3000", "OnTimerEnd": SONDAR, "Repeat": "=locL4cAguardar", "Start": "=locL4cAguardar", "Visible": "=false"}),
        "tmrL4Mensagem")


# ======================================================================== scrInicio, scrL4Entrar e App
CARTOES = {
    6: ("Ficha 04 · Melhoramento", "Processamento na cloud",
        "A Ficha 04 com o processamento da aula 7: cada pedido é classificado por um fluxo Power Automate, com estado, erros e reprocessamento."),
    7: ("Ficha 04 · Revisão", "Revisão com perfis",
        "A Ficha 04 com entrada por password (hash PBKDF2 no Azure) e perfis Admin, Gestor e Cliente, que decidem os pedidos em revisão."),
}
NAVEGAR = {
    4: f'Navigate({ECRA}, ScreenTransition.Cover, {{{NIV}: "pedidos"}})',
    6: f'Navigate({ECRA}, ScreenTransition.Cover, {{{NIV}: "melhoramento"}})',
    7: f"Navigate({ENT}, ScreenTransition.Cover)",
}


def migrar_inicio(doc: dict) -> None:
    for ctl in yamlio.controlos(doc):
        if ctl.nome != "galInFichas":
            continue
        itens = str(ctl.prop("Items"))
        for num, (ficha, titulo, desc) in CARTOES.items():
            itens = re.sub(r'\{Num: ' + str(num) + r', Ficha: "[^"]*", Titulo: "[^"]*",(\s*)Descricao: "[^"]*"',
                           lambda m, f=ficha, t=titulo, d=desc: f'{{Num: {num}, Ficha: "{f}", Titulo: "{t}",{m.group(1)}Descricao: "{d}"', itens)
        ctl.definir("Items", itens)
        sel = str(ctl.prop("OnSelect"))
        for num, nav in NAVEGAR.items():
            sel = re.sub(r"(\n\s*" + str(num) + r", )Navigate\([^\n]*?\)(?=,?\n)", lambda m, n=nav: m.group(1) + n, sel)
        ctl.definir("OnSelect", sel)


def ecra_entrar() -> dict:
    d = B.ecra_entrar()
    for c in yamlio.controlos(d):
        if c.nome == "btnL4dEntrar":
            c.definir("OnSelect", str(c.prop("OnSelect")).replace(
                "Navigate(scrL4Revisao, ScreenTransition.Cover)", f'Navigate({ECRA}, ScreenTransition.Cover, {{{NIV}: "revisao"}})'))
    return d


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
    if "scrInicio" in ecras:
        migrar_inicio(doc)
    if ECRA in ecras:
        migrar_pedidos(doc)


def main(raiz: Path = projeto.RAIZ) -> int:
    mudados = 0
    for f in projeto.ficheiros_src(raiz):
        if any(f.name == f"{r}.pa.yaml" for r in RETIRADOS):
            continue
        antes = f.read_text(encoding="utf-8")
        d = yamlio.ler(f)
        migrar_documento(d)
        depois = yamlio.escrever_texto(d)
        if depois != antes:
            f.write_text(depois, encoding="utf-8")
            mudados += 1
            print("migrado:", f.relative_to(raiz))
    ent = raiz / "src" / "screens" / f"{ENT}.pa.yaml"
    texto = yamlio.escrever_texto(ecra_entrar())
    if not ent.exists() or ent.read_text(encoding="utf-8") != texto:
        ent.write_text(texto, encoding="utf-8")
        mudados += 1
        print("escrito:", ent.relative_to(raiz))
    for r in RETIRADOS:
        velho = raiz / "src" / "screens" / f"{r}.pa.yaml"
        if velho.exists():
            velho.unlink()
            mudados += 1
            print("retirado:", velho.relative_to(raiz))
    print(f"m009: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
