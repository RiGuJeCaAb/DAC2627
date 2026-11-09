# Gera o pacote de construção da APP DAC2627 a partir das fórmulas do Manual ABC.
# Fórmulas escritas como no manual (locale PT: ; e ;;) e convertidas para o formato
# invariante usado no código YAML do estúdio (, e ;).
import re, json, os
OUT = os.path.dirname(os.path.abspath(__file__))

# Versões dos controlos: CONFIRMAR no estúdio (inserir um de cada e ver "Ver código")
CT = {
  'con': ('GroupContainer@1.5.0', 'AutoLayout'),
  'lbl': ('Label@2.5.1', None),
  'btn': ('Classic/Button@2.2.0', None),
  'txt': ('Classic/TextInput@2.3.2', None),
  'ico': ('Classic/Icon@2.5.0', None),
  'rec': ('Rectangle@2.3.0', None),
  'gal': ('Gallery@2.15.0', 'Vertical'),
  'drp': ('Classic/DropDown@2.3.1', None),
  'tmr': ('Timer@2.1.0', None),
}

def pt2inv(f):
    f = f.replace(';;', '\x00').replace(';', ',').replace('\x00', ';')
    return f

def fx(v):
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, (int, float)): return str(v)
    return v

def C(name, kind, props=None, kids=None, variant=None):
    return {'name': name, 'kind': kind, 'props': props or {}, 'kids': kids or [], 'variant': variant}

def V(name, props=None, kids=None): # contentor vertical
    p = {'LayoutDirection': 'LayoutDirection.Vertical'}; p.update(props or {}); return C(name, 'con', p, kids)
def H(name, props=None, kids=None): # contentor horizontal
    p = {'LayoutDirection': 'LayoutDirection.Horizontal'}; p.update(props or {}); return C(name, 'con', p, kids)

def radius(r): return {'RadiusTopLeft': r, 'RadiusTopRight': r, 'RadiusBottomLeft': r, 'RadiusBottomRight': r}
def pad(p): return {'PaddingTop': p, 'PaddingBottom': p, 'PaddingLeft': p, 'PaddingRight': p}
def bradius(r): return {'RadiusTopLeft': r, 'RadiusTopRight': r, 'RadiusBottomLeft': r, 'RadiusBottomRight': r}

def emit(c, ind=0):
    s = ' ' * ind
    ctl, var = CT[c['kind']]
    if c['variant']: var = c['variant']
    out = [f"{s}- {c['name']}:", f"{s}    Control: {ctl}"]
    if var: out.append(f"{s}    Variant: {var}")
    if c['props']:
        out.append(f"{s}    Properties:")
        for k in sorted(c['props']):
            v = pt2inv(str(fx(c['props'][k])))
            lines = v.split('\n')
            if len(lines) == 1 and ': ' not in v and ' #' not in v and not v.endswith(':'):
                out.append(f"{s}      {k}: ={v}")
                continue
            out.append(f"{s}      {k}: |-")
            out.append(f"{s}        ={lines[0]}")
            for ln in lines[1:]:
                out.append(f"{s}        {ln}")
    if c['kids']:
        out.append(f"{s}    Children:")
        for k in c['kids']:
            out += emit(k, ind + 6)
    return out

# ---------- peças comuns (A8, A9) ----------
def ecra(code, titulo, conteudo_props, conteudo_kids, inicio=True, extra_cab=None, fora=None, scr=None):
    cab = []
    if inicio:
        cab.append(C(f'icoInicio{code}', 'ico', {'Icon': 'Icon.Home', 'Color': 'Color.White', 'Width': 44, 'Height': 44,
             'OnSelect': 'Navigate(scrInicio; ScreenTransition.UnCover)', 'AccessibleLabel': '"Voltar ao início"'}))
    cab += (extra_cab or [])
    cab.append(C(f'lblCab{code}', 'lbl', {'Text': titulo, 'Color': 'Color.White', 'Size': 16,
             'FontWeight': 'FontWeight.Semibold', 'FillPortions': 1, 'Height': 44}))
    cp = {'FillPortions': 1, 'LayoutGap': 16, 'AlignInContainer': 'AlignInContainer.Stretch'}
    cp.update(pad(f'If({scr}.Size = ScreenSize.Small; 16; 24)' if scr else 24)); cp.update(conteudo_props)
    raiz = V(f'conEcra{code}', {'X': 0, 'Y': 0, 'Width': 'Parent.Width', 'Height': 'Parent.Height', 'Fill': 'nfFundo', 'LayoutGap': 0}, [
        H(f'conCab{code}', {'Height': 64, 'FillPortions': 0, 'Fill': 'nfAzul', 'PaddingLeft': 24, 'PaddingRight': 24,
            'LayoutAlignItems': 'LayoutAlignItems.Center', 'LayoutGap': 12, 'AlignInContainer': 'AlignInContainer.Stretch'}, cab),
        V(f'conConteudo{code}', cp, conteudo_kids)])
    return [raiz] + (fora or [])

def btn_pri(name, text, onselect, extra=None):
    p = {'Text': text, 'Fill': 'nfAzul', 'Color': 'Color.White', 'Height': 48, 'OnSelect': onselect}; p.update(bradius(12)); p.update(extra or {}); return C(name, 'btn', p)
def btn_sec(name, text, onselect, extra=None, cor='nfAzul'):
    p = {'Text': text, 'Fill': 'Color.White', 'Color': cor, 'BorderColor': cor, 'BorderThickness': 2, 'Height': 48, 'OnSelect': onselect}
    p.update(bradius(12)); p.update(extra or {}); return C(name, 'btn', p)
def cartao(name, extra=None, kids=None):
    p = {'Fill': 'Color.White', 'DropShadow': 'DropShadow.Light'}; p.update(bradius(16)); p.update(extra or {}); return V(name, p, kids)

def pill(name, props, galeria=False):
    # Botão sem ação a fazer de etiqueta arredondada: as etiquetas clássicas não têm cantos arredondados
    p = {'BorderThickness': 0, 'HoverFill': 'Self.Fill', 'PressedFill': 'Self.Fill', 'HoverColor': 'Self.Color',
         'PressedColor': 'Self.Color', 'DisabledFill': 'Self.Fill', 'DisabledColor': 'Self.Color', 'TabIndex': -1,
         'Font': "Font.'Open Sans'"}
    if galeria: p['OnSelect'] = 'Select(Parent)'
    p.update(props); return C(name, 'btn', p)

def faixa(con_name, lbl_name, lbl_props, con_props):
    p = {'LayoutAlignItems': 'LayoutAlignItems.Center', 'PaddingLeft': 16, 'PaddingRight': 16, 'Height': 44, 'AlignInContainer': 'AlignInContainer.Stretch'}
    p.update(bradius(10)); p.update(con_props)
    lp = {'FillPortions': 1, 'Height': 40}; lp.update(lbl_props)
    return H(con_name, p, [C(lbl_name, 'lbl', lp)])

SCREENS = {}

# ---------- B · scrInicio ----------
SCREENS['scrInicio'] = {
 'props': {'Fill': 'nfFundo'},
 'controls': ecra('In', '"APP DAC2627"', {}, [
    C('lblInTitulo', 'lbl', {'Text': '"Laboratórios de DAC 2026/27"', 'Size': 'If(scrInicio.Size = ScreenSize.Small; 22; 28)', 'FontWeight': 'FontWeight.Bold', 'Color': 'nfTexto', 'AutoHeight': True, 'AlignInContainer': 'AlignInContainer.Stretch'}),
    C('lblInSubtitulo', 'lbl', {'Text': '"Escolha a ficha que quer abrir."', 'Size': 15, 'Color': 'nfTextoSuave', 'AutoHeight': True, 'AlignInContainer': 'AlignInContainer.Stretch'}),
    C('galInFichas', 'gal', {
        'FillPortions': 1, 'AlignInContainer': 'AlignInContainer.Stretch',
        'Items': '''Table(
    {Num: 1; Ficha: "Ficha 01"; Titulo: "Hello Cloud";
     Descricao: "Primeira Canvas app: três ecrãs, navegação e variável global."; Disponivel: true};
    {Num: 2; Ficha: "Ficha 02"; Titulo: "Serviços Cloud";
     Descricao: "Inventário de serviços cloud em Dataverse, com criar, editar e remover num só ecrã."; Disponivel: true};
    {Num: 3; Ficha: "Ficha 03"; Titulo: "Consulta de API";
     Descricao: "Utilizadores e publicações de uma API REST, com filtro por utilizador e tratamento de erros."; Disponivel: true};
    {Num: 4; Ficha: "Ficha 04"; Titulo: "Próximo laboratório";
     Descricao: "Reservado para a próxima ficha do docente."; Disponivel: false}
)''',
        'WrapCount': 'Switch(scrInicio.Size; ScreenSize.Small; 1; ScreenSize.Medium; 2; 3)',
        'TemplateSize': 228, 'TemplatePadding': 12,
        'OnSelect': '''If(
    galInFichas.Selected.Disponivel;
    Switch(
        galInFichas.Selected.Num;
        1; Navigate(scrL1BoasVindas; ScreenTransition.Cover);
        2; Navigate(scrL2Servicos; ScreenTransition.Cover);
        3; Navigate(scrL3Lista; ScreenTransition.Cover)
    )
)'''}, [
        C('conInCartao', 'con', dict({'X': 0, 'Y': 0, 'Width': 'Parent.TemplateWidth', 'Height': 'Parent.TemplateHeight',
            'Fill': 'If(ThisItem.Disponivel; Color.White; nfFundo)', 'BorderColor': 'If(ThisItem.Disponivel; nfLinha; ColorValue("#C5CBD1"))',
            'BorderStyle': 'If(ThisItem.Disponivel; BorderStyle.Solid; BorderStyle.Dashed)', 'BorderThickness': 'If(ThisItem.Disponivel; 1; 2)',
            'DropShadow': 'If(ThisItem.Disponivel; DropShadow.Light; DropShadow.None)'}, **bradius(16)), variant='ManualLayout'),
        C('lblInFicha', 'lbl', {'X': 24, 'Y': 20, 'Height': 24, 'Text': 'ThisItem.Ficha', 'Size': 12, 'FontWeight': 'FontWeight.Bold', 'Color': 'nfAzul'}),
        C('lblInFichaTitulo', 'lbl', {'X': 24, 'Y': 46, 'Height': 34, 'Wrap': False, 'Text': 'ThisItem.Titulo', 'Size': 20, 'FontWeight': 'FontWeight.Bold', 'Width': 'Parent.TemplateWidth - 48', 'Color': 'If(ThisItem.Disponivel; nfTexto; nfTextoSuave)'}),
        C('lblInFichaDescricao', 'lbl', {'X': 24, 'Y': 84, 'Text': 'ThisItem.Descricao', 'Width': 'Parent.TemplateWidth - 48', 'Height': 72, 'Color': 'nfTextoSuave', 'VerticalAlign': 'VerticalAlign.Top'}),
        C('btnInAbrir', 'btn', dict({'X': 24, 'Width': 140, 'Height': 44, 'Y': 'Parent.TemplateHeight - 64',
            'Text': 'If(ThisItem.Disponivel; "Abrir"; "Em breve")', 'Fill': 'nfAzul', 'Color': 'Color.White',
            'DisplayMode': 'If(ThisItem.Disponivel; DisplayMode.Edit; DisplayMode.Disabled)', 'OnSelect': 'Select(Parent)'}, **bradius(12))),
    ]),
    C('lblInRodape', 'lbl', {'Text': '"Desenvolvimento de Aplicações na Cloud · CTeSP Computação Cloud"', 'Size': 12, 'Align': 'Align.Center', 'Color': 'nfTextoSuave', 'AlignInContainer': 'AlignInContainer.Stretch', 'AutoHeight': True}),
 ], inicio=False, scr='scrInicio')}

# ---------- C · Ficha 01 ----------
def card_l1(code, scr, kids, h=400, hp=None):
    p = {'Width': f'Min(640; Parent.Width - If({scr}.Size = ScreenSize.Small; 32; 48))', 'Height': f'If({scr}.Size = ScreenSize.Small; {hp or h}; {h})',
         'LayoutGap': 20, 'LayoutAlignItems': 'LayoutAlignItems.Center', 'LayoutJustifyContent': 'LayoutJustifyContent.Center'}
    p.update(pad(f'If({scr}.Size = ScreenSize.Small; 24; 40)')); return cartao(f'conL1{code}Cartao', p, kids)
cent = {'LayoutJustifyContent': 'LayoutJustifyContent.Center', 'LayoutAlignItems': 'LayoutAlignItems.Center'}
icoVoltar = lambda n: C(n, 'ico', {'Icon': 'Icon.ChevronLeft', 'Color': 'Color.White', 'Width': 44, 'Height': 44, 'AccessibleLabel': '"Voltar"', 'OnSelect': 'Back()'})

SCREENS['scrL1BoasVindas'] = {'props': {'Fill': 'nfFundo'}, 'controls': ecra('L1a', '"Ficha 01 · Hello Cloud"', cent, [card_l1('a', 'scrL1BoasVindas', [
    C('lblL1Titulo', 'lbl', {'Text': '"Bem-vindo à Cloud"', 'Size': 'If(scrL1BoasVindas.Size = ScreenSize.Small; 28; 36)', 'FontWeight': 'FontWeight.Bold', 'Align': 'Align.Center', 'Color': 'nfTexto', 'AlignInContainer': 'AlignInContainer.Stretch', 'AutoHeight': True}),
    C('lblL1Subtitulo', 'lbl', {'Text': '"A sua primeira aplicação Power Apps, criada, executada e partilhada a partir da cloud."', 'Align': 'Align.Center', 'Color': 'nfTextoSuave', 'AlignInContainer': 'AlignInContainer.Stretch', 'AutoHeight': True, 'Size': 15}),
    btn_pri('btnL1Comecar', '"Começar"', 'Navigate(scrL1Pedido; ScreenTransition.Cover)', {'Width': 220, 'Height': 52}),
 ])], scr='scrL1BoasVindas')}

SCREENS['scrL1Pedido'] = {'props': {'Fill': 'nfFundo', 'OnVisible': 'Reset(txtL1Nome);; UpdateContext({locAviso: false})'},
 'controls': ecra('L1b', '"Ficha 01 · Passo 1 de 2"', cent, [card_l1('b', 'scrL1Pedido', [
    C('lblL1Pergunta', 'lbl', {'Text': '"Como se chama?"', 'Size': 'If(scrL1Pedido.Size = ScreenSize.Small; 24; 28)', 'FontWeight': 'FontWeight.Bold', 'Color': 'nfTexto', 'AlignInContainer': 'AlignInContainer.Stretch', 'AutoHeight': True}),
    C('txtL1Nome', 'txt', dict({'HintText': '"Indique o seu nome"', 'Default': 'gblL1Nome', 'Height': 52, 'AlignInContainer': 'AlignInContainer.Stretch', 'BorderColor': 'ColorValue("#7D8993")'}, **bradius(12))),
    faixa('conL1Aviso', 'lblL1Aviso', {'Text': '"Introduza o seu nome."', 'Color': 'ColorValue("#8A3B0F")', 'FontWeight': 'FontWeight.Semibold'},
          {'Fill': 'ColorValue("#FDF1E7")', 'Visible': 'locAviso && IsBlank(Trim(txtL1Nome.Text))'}),
    btn_pri('btnL1Saudar', '"Saudar"', '''If(
    IsBlank(Trim(txtL1Nome.Text));
    UpdateContext({locAviso: true});
    Set(gblL1Nome; Trim(txtL1Nome.Text));; Navigate(scrL1Saudacao; ScreenTransition.Fade)
)''', {'Height': 52, 'AlignInContainer': 'AlignInContainer.Stretch'}),
 ])], extra_cab=[icoVoltar('icoL1Voltar')], scr='scrL1Pedido')}

SCREENS['scrL1Saudacao'] = {'props': {'Fill': 'nfFundo'}, 'controls': ecra('L1c', '"Ficha 01 · Passo 2 de 2"', cent, [card_l1('c', 'scrL1Saudacao', [
    C('icoL1Sucesso', 'ico', {'Icon': 'Icon.Check', 'Color': 'nfVerde', 'Width': 64, 'Height': 64}),
    C('lblL1BoasVindas', 'lbl', {'Text': '"Bem-vindo à Cloud"', 'Color': 'nfVerde', 'FontWeight': 'FontWeight.Bold', 'Align': 'Align.Center', 'AlignInContainer': 'AlignInContainer.Stretch', 'Height': 32, 'Size': 16}),
    C('lblL1Saudacao', 'lbl', {'Text': 'If(IsBlank(gblL1Nome); "Introduza o seu nome."; "Olá, " & gblL1Nome & "!")', 'Size': 'If(scrL1Saudacao.Size = ScreenSize.Small; 30; 40)', 'FontWeight': 'FontWeight.Bold', 'Align': 'Align.Center', 'Color': 'nfTexto', 'AlignInContainer': 'AlignInContainer.Stretch', 'AutoHeight': True}),
    H('conL1Botoes', {'LayoutGap': 16, 'LayoutJustifyContent': 'LayoutJustifyContent.Center', 'LayoutWrap': True, 'AlignInContainer': 'AlignInContainer.Stretch', 'Height': 'If(scrL1Saudacao.Size = ScreenSize.Small; 112; 52)'}, [
        btn_sec('btnL1Alterar', '"Alterar nome"', 'Back()', {'Width': 200}),
        btn_pri('btnL1Terminar', '"Terminar"', 'Set(gblL1Nome; Blank());; Navigate(scrL1BoasVindas; ScreenTransition.UnCoverRight)', {'Width': 200}),
    ]),
 ], h=420, hp=480)], scr='scrL1Saudacao')}

# ---------- D · Ficha 02 ----------
dm_bloq = 'If(frmL2Servico.Mode = FormMode.View; DisplayMode.Edit; DisplayMode.Disabled)'
SCREENS['scrL2Servicos'] = {'props': {'Fill': 'nfFundo', 'OnVisible': '''UpdateContext({locSel: Blank(); locTentou: false; locAcao: ""; locUltimaAcao: "";
               locMsg: ""; locMsgTipo: "ok"; locTimer: false});;
ViewForm(frmL2Servico)'''},
 'controls': ecra('L2', '"Ficha 02 · Serviços Cloud"', {}, [
    H('conL2Barra', {'Height': 'If(scrL2Servicos.Size = ScreenSize.Small; 168; 52)', 'Visible': '!(scrL2Servicos.Size = ScreenSize.Small && (!IsBlank(locSel) || frmL2Servico.Mode <> FormMode.View))', 'LayoutGap': 12, 'LayoutWrap': True, 'LayoutAlignItems': 'LayoutAlignItems.Center', 'AlignInContainer': 'AlignInContainer.Stretch'}, [
        C('txtL2Pesquisa', 'txt', dict({'HintText': '"Pesquisar pelo início do nome"', 'Default': '""', 'FillPortions': 1, 'LayoutMinWidth': 220, 'Height': 48, 'DisplayMode': dm_bloq}, **bradius(12))),
        C('drpL2Modelo', 'drp', {'Items': '["Todos"; "IaaS"; "PaaS"; "SaaS"]', 'Default': '"Todos"', 'Width': 160, 'Height': 48, 'DisplayMode': dm_bloq}),
        C('lblL2Contagem', 'lbl', {'Text': 'With({n: If(drpL2Modelo.Selected.Value = "Todos";\n    CountRows(Filter(\'Cloud Service\'; StartsWith(\'Service Title\'; txtL2Pesquisa.Text)));\n    CountRows(Filter(\'Cloud Service\'; StartsWith(\'Service Title\'; txtL2Pesquisa.Text) && \'Service Model\' = LookUp(Choices(\'Cloud Service\'.\'Service Model\'); Text(Value) = drpL2Modelo.Selected.Value).Value)))};\n    If(n = 1; "1 serviço"; n & " serviços"))', 'Width': 110, 'Height': 48, 'Color': 'nfTextoSuave'}),
        btn_pri('btnL2Novo', '"+  Novo serviço"', 'NewForm(frmL2Servico);;\n    UpdateContext({locTentou: false; locMsg: ""; locTimer: false})', {'Width': 180, 'DisplayMode': dm_bloq}),
    ]),
    H('conL2Corpo', {'FillPortions': 1, 'LayoutGap': 24, 'LayoutAlignItems': 'LayoutAlignItems.Stretch', 'AlignInContainer': 'AlignInContainer.Stretch'}, [
        cartao('conL2Lista', dict({'FillPortions': 'If(scrL2Servicos.Size = ScreenSize.Medium; 1; 2)', 'Visible': 'scrL2Servicos.Size > ScreenSize.Small ||\n    (IsBlank(locSel) && frmL2Servico.Mode = FormMode.View)'}, **bradius(12)), [
            C('lblL2Vazio', 'lbl', {'Text': '"Nenhum serviço encontrado com estes critérios."', 'Align': 'Align.Center', 'Visible': 'IsEmpty(galL2Servicos.AllItems)', 'Color': 'nfTextoSuave', 'AlignInContainer': 'AlignInContainer.Stretch', 'Height': 80}),
            C('galL2Servicos', 'gal', {'FillPortions': 1, 'AlignInContainer': 'AlignInContainer.Stretch', 'TemplateSize': 72, 'TemplatePadding': 0,
                'Items': '''If(drpL2Modelo.Selected.Value = "Todos";
    Sort(Filter('Cloud Service'; StartsWith('Service Title'; txtL2Pesquisa.Text)); 'Service Title');
    Sort(Filter('Cloud Service'; StartsWith('Service Title'; txtL2Pesquisa.Text) &&
        'Service Model' = LookUp(Choices('Cloud Service'.'Service Model'); Text(Value) = drpL2Modelo.Selected.Value).Value);
        'Service Title'))''', 'OnSelect': 'UpdateContext({locSel: galL2Servicos.Selected; locTentou: false})', 'DisplayMode': dm_bloq,
                'TemplateFill': "If(ThisItem.'Cloud Service' = locSel.'Cloud Service'; nfAzulClaro; Color.White)"}, [
                C('lblL2ItemTitulo', 'lbl', {'X': 20, 'Y': 12, 'Height': 28, 'Text': "ThisItem.'Service Title'", 'Wrap': False, 'Width': 'Parent.TemplateWidth - 120', 'Size': 14, 'FontWeight': 'FontWeight.Semibold', 'Color': 'nfTexto'}),
                C('lblL2ItemFornecedor', 'lbl', {'X': 20, 'Y': 40, 'Height': 22, 'Width': 'Parent.TemplateWidth - 120', 'Text': 'ThisItem.Provider', 'Size': 12, 'Color': 'nfTextoSuave'}),
                pill('btnL2ItemModelo', dict({'Width': 64, 'Height': 28, 'Y': 22, 'Text': "Text(ThisItem.'Service Model')", 'X': 'Parent.TemplateWidth - 90', 'FontWeight': 'FontWeight.Bold', 'Size': 11,
                    'Fill': 'Switch(Text(ThisItem.\'Service Model\');\n    "IaaS"; ColorValue("#DCE7F2"); "PaaS"; nfVerdeFundo; ColorValue("#FBEBD9"))',
                    'Color': 'Switch(Text(ThisItem.\'Service Model\');\n    "IaaS"; nfAzul; "PaaS"; ColorValue("#1F5E43"); ColorValue("#8A3B0F"))'}, **bradius(14)), galeria=True),
                C('recL2Separador', 'rec', {'X': 0, 'Height': 1, 'Width': 'Parent.TemplateWidth', 'Y': 'Parent.TemplateHeight - 1', 'Fill': 'nfLinha'}),
            ]),
        ]),
        cartao('conL2Painel', dict({'FillPortions': 'If(scrL2Servicos.Size = ScreenSize.Medium; 1; 3)', 'LayoutGap': 12, 'Visible': 'scrL2Servicos.Size > ScreenSize.Small ||\n    !IsBlank(locSel) || frmL2Servico.Mode <> FormMode.View'}, **bradius(12), **pad(24)), [
            H('conL2PainelTopo', {'Height': 48, 'LayoutGap': 12, 'LayoutAlignItems': 'LayoutAlignItems.Center', 'AlignInContainer': 'AlignInContainer.Stretch'}, [
                btn_sec('btnL2VoltarLista', '"‹ Lista"', 'UpdateContext({locSel: Blank()})', {'Width': 96, 'Height': 44, 'Visible': 'scrL2Servicos.Size = ScreenSize.Small && frmL2Servico.Mode = FormMode.View'}),
                C('lblL2PainelTitulo', 'lbl', {'Text': 'If(frmL2Servico.Mode = FormMode.New; "Novo serviço";\n   frmL2Servico.Mode = FormMode.Edit; "Editar serviço";\n   locSel.\'Service Title\')', 'FillPortions': 1, 'Size': 'If(scrL2Servicos.Size = ScreenSize.Small; 18; 22)', 'Wrap': False, 'FontWeight': 'FontWeight.Bold', 'Color': 'nfTexto', 'Height': 44}),
            ]),
            faixa('conL2ErroGeral', 'lblL2ErroGeral', {'Text': '"Preencha os campos obrigatórios assinalados."', 'Color': 'ColorValue("#8E1F25")', 'FontWeight': 'FontWeight.Semibold'},
                  {'Fill': 'nfVermelhoFundo', 'Visible': 'locTentou && (IsBlank(Trim(txtL2Titulo.Text)) ||\n    IsBlank(Trim(txtL2Fornecedor.Text)) || IsBlank(cmbL2Modelo.Selected))'}),
            # frmL2Servico: inserir à mão aqui (D5, passo 3), depois de colar
            C('lblL2PainelVazio', 'lbl', {'Text': '"Selecione um serviço na lista ou crie um novo."', 'FillPortions': 1, 'Align': 'Align.Center', 'Color': 'nfTextoSuave', 'AlignInContainer': 'AlignInContainer.Stretch', 'Visible': 'frmL2Servico.Mode = FormMode.View && IsBlank(locSel)'}),
            H('conL2Acoes', {'Height': 48, 'LayoutGap': 12, 'LayoutAlignItems': 'LayoutAlignItems.Center', 'AlignInContainer': 'AlignInContainer.Stretch'}, [
                btn_sec('btnL2Remover', '"Remover"', 'UpdateContext({locAcao: "remover"; locMsg: ""; locTimer: false})', {'Width': 130, 'Visible': 'frmL2Servico.Mode = FormMode.View && !IsBlank(locSel)'}, cor='nfVermelho'),
                C('lblL2Espaco', 'lbl', {'Text': '""', 'FillPortions': 1, 'LayoutMinWidth': 0}),
                btn_sec('btnL2Cancelar', '"Cancelar"', 'ResetForm(frmL2Servico);; ViewForm(frmL2Servico);;\n    UpdateContext({locTentou: false})', {'Width': 130, 'Visible': 'frmL2Servico.Mode <> FormMode.View'}),
                btn_pri('btnL2Editar', '"Editar"', 'EditForm(frmL2Servico);;\n    UpdateContext({locTentou: false; locMsg: ""; locTimer: false})', {'Width': 130, 'Visible': 'frmL2Servico.Mode = FormMode.View && !IsBlank(locSel)'}),
                btn_pri('btnL2Guardar', '"Guardar"', '''If(
    IsBlank(Trim(txtL2Titulo.Text)) || IsBlank(Trim(txtL2Fornecedor.Text)) ||
    IsBlank(cmbL2Modelo.Selected);
    UpdateContext({locTentou: true});
    UpdateContext({locAcao: If(frmL2Servico.Mode = FormMode.New; "criar"; "editar")})
)''', {'Width': 130, 'Visible': 'frmL2Servico.Mode <> FormMode.View'}),
            ]),
        ]),
    ]),
 ], fora=[
    C('recL2Veu', 'rec', {'X': 0, 'Y': 0, 'Width': 'Parent.Width', 'Height': 'Parent.Height', 'Fill': 'RGBA(30; 42; 51; 0.55)', 'Visible': 'locAcao <> ""'}),
    V('conL2Dialogo', dict({'Fill': 'Color.White', 'LayoutGap': 12, 'Width': 'Min(480; Parent.Width - 32)', 'Height': 240,
        'X': '(Parent.Width - Self.Width) / 2', 'Y': '(Parent.Height - Self.Height) / 2', 'Visible': 'locAcao <> ""', 'DropShadow': 'DropShadow.Bold'}, **bradius(16), **pad(28)), [
        C('lblL2ConfTitulo', 'lbl', {'Text': 'Switch(locAcao;\n    "criar"; "Criar serviço?";\n    "editar"; "Guardar alterações?";\n    "Remover serviço?")', 'Size': 22, 'FontWeight': 'FontWeight.Bold', 'Color': 'nfTexto', 'Height': 40, 'AlignInContainer': 'AlignInContainer.Stretch'}),
        C('lblL2ConfTexto', 'lbl', {'Text': 'Switch(locAcao;\n    "criar"; "O serviço " & Trim(txtL2Titulo.Text) & " vai ser acrescentado à tabela Cloud Service.";\n    "editar"; "As alterações a " & locSel.\'Service Title\' & " vão ser gravadas na tabela Cloud Service.";\n    "O serviço " & locSel.\'Service Title\' & " vai ser removido da tabela Cloud Service. Esta ação não pode ser anulada.")', 'FillPortions': 1, 'Color': 'nfTextoSuave', 'VerticalAlign': 'VerticalAlign.Top', 'AlignInContainer': 'AlignInContainer.Stretch'}),
        H('conL2ConfBotoes', {'LayoutJustifyContent': 'LayoutJustifyContent.End', 'LayoutGap': 12, 'Height': 48, 'AlignInContainer': 'AlignInContainer.Stretch'}, [
            btn_sec('btnL2ConfCancelar', '"Cancelar"', 'UpdateContext({locAcao: ""})', {'Width': 130}),
            btn_pri('btnL2ConfOk', 'Switch(locAcao; "criar"; "Criar"; "editar"; "Guardar"; "Remover")', '''UpdateContext({locUltimaAcao: locAcao; locAcao: ""});;
If(
    locUltimaAcao = "remover";
    IfError(
        Remove('Cloud Service'; locSel);
        UpdateContext({locMsg: "Não foi possível remover o serviço."; locMsgTipo: "erro"});
        UpdateContext({locMsg: "Serviço " & locSel.'Service Title' & " removido."; locMsgTipo: "ok"; locTimer: true});;
        UpdateContext({locSel: Blank()})
    );
    SubmitForm(frmL2Servico)
)''', {'Width': 130, 'Fill': 'If(locAcao = "remover"; nfVermelho; nfAzul)'}),
        ]),
    ]),
    H('conL2Mensagem', dict({'DropShadow': 'DropShadow.Medium', 'LayoutGap': 12, 'LayoutAlignItems': 'LayoutAlignItems.Center',
        'Width': 'Min(520; Parent.Width - 32)', 'Height': 56, 'X': '(Parent.Width - Self.Width) / 2', 'Y': 76,
        'Fill': 'If(locMsgTipo = "erro"; nfVermelhoFundo; nfVerdeFundo)', 'Visible': 'locMsg <> ""'}, **bradius(12), **pad(16)), [
        C('icoL2MsgIcone', 'ico', {'Icon': 'If(locMsgTipo = "erro"; Icon.Warning; Icon.Check)', 'Color': 'If(locMsgTipo = "erro"; nfVermelho; nfVerde)', 'Width': 24, 'Height': 24}),
        C('lblL2Mensagem', 'lbl', {'Text': 'locMsg', 'FillPortions': 1, 'FontWeight': 'FontWeight.Semibold', 'Height': 40, 'Color': 'If(locMsgTipo = "erro"; ColorValue("#8E1F25"); ColorValue("#1F5E43"))'}),
        C('icoL2FecharMsg', 'ico', {'Icon': 'Icon.Cancel', 'AccessibleLabel': '"Fechar mensagem"', 'OnSelect': 'UpdateContext({locMsg: ""; locTimer: false})', 'Width': 44, 'Height': 44, 'Color': 'nfTextoSuave'}),
    ]),
    C('tmrL2Mensagem', 'tmr', {'Duration': 3500, 'Start': 'locTimer', 'AutoStart': False, 'Repeat': False, 'Visible': False, 'OnTimerEnd': 'UpdateContext({locMsg: ""; locTimer: false})'}),
 ])}

# ---------- E · Ficha 03 ----------
chev = lambda n: C(n, 'ico', {'Icon': 'Icon.ChevronRight', 'Color': 'ColorValue("#7D8993")', 'Width': 24, 'Height': 24})
SCREENS['scrL3Lista'] = {'props': {'Fill': 'nfFundo', 'OnVisible': 'If(IsEmpty(colL3Utilizadores) || IsEmpty(colL3Publicacoes); Select(btnL3Carregar))'},
 'controls': ecra('L3a', '"Ficha 03 · Consulta de API"', {}, [
    H('conL3Separadores', {'Height': 48, 'LayoutGap': 8, 'AlignInContainer': 'AlignInContainer.Stretch'}, [
        C('btnL3SepUtil', 'btn', dict({'Width': 200, 'FillPortions': 'If(scrL3Lista.Size = ScreenSize.Small; 1; 0)', 'LayoutMinWidth': 0, 'Size': 'If(scrL3Lista.Size = ScreenSize.Small; 13; 15)', 'Height': 48, 'BorderColor': 'nfAzul', 'BorderThickness': 2,
            'Text': '"Utilizadores (" & CountRows(colL3Utilizadores) & ")"', 'OnSelect': 'UpdateContext({locL3Vista: "utilizadores"});; Reset(txtL3Pesquisa);; Reset(drpL3Utilizador)',
            'Fill': 'If(locL3Vista <> "publicacoes"; nfAzul; Color.White)', 'Color': 'If(locL3Vista <> "publicacoes"; Color.White; nfAzul)'}, **bradius(12))),
        C('btnL3SepPub', 'btn', dict({'Width': 200, 'FillPortions': 'If(scrL3Lista.Size = ScreenSize.Small; 1; 0)', 'LayoutMinWidth': 0, 'Size': 'If(scrL3Lista.Size = ScreenSize.Small; 13; 15)', 'Height': 48, 'BorderColor': 'nfAzul', 'BorderThickness': 2,
            'Text': '"Publicações (" & CountRows(colL3Publicacoes) & ")"', 'OnSelect': 'UpdateContext({locL3Vista: "publicacoes"});; Reset(txtL3Pesquisa);; Reset(drpL3Utilizador)',
            'Fill': 'If(locL3Vista = "publicacoes"; nfAzul; Color.White)', 'Color': 'If(locL3Vista = "publicacoes"; Color.White; nfAzul)'}, **bradius(12))),
    ]),
    H('conL3Barra', {'Height': '''If(scrL3Lista.Size = ScreenSize.Small;
    If(locL3Vista = "publicacoes"; 168; 108);
    scrL3Lista.Size = ScreenSize.Medium && locL3Vista = "publicacoes"; 108;
    52)''', 'LayoutWrap': True, 'LayoutGap': 12, 'LayoutAlignItems': 'LayoutAlignItems.Center', 'AlignInContainer': 'AlignInContainer.Stretch'}, [
        C('txtL3Pesquisa', 'txt', dict({'HintText': 'If(locL3Vista = "publicacoes";\n                                "Pesquisar por título ou texto";\n                                "Pesquisar por nome ou email")', 'Default': '""', 'FillPortions': 1, 'LayoutMinWidth': 220, 'Height': 48}, **bradius(12))),
        C('drpL3Utilizador', 'drp', {'Width': 'If(scrL3Lista.Size = ScreenSize.Small; Parent.Width; 260)', 'Height': 48, 'Visible': 'locL3Vista = "publicacoes"',
            'Items': 'Ungroup(\n    Table(\n        {grp: Table({id: 0; name: "Todos os utilizadores"})};\n        {grp: Sort(ShowColumns(colL3Utilizadores; id; name); name)}\n    );\n    grp\n)',
            'Items.Value': 'name', 'Default': '"Todos os utilizadores"', 'AccessibleLabel': '"Filtrar publicações por utilizador"'}),
        C('lblL3Contagem', 'lbl', {'Width': 'If(scrL3Lista.Size = ScreenSize.Small; 150; 210)', 'Size': 'If(scrL3Lista.Size = ScreenSize.Small; 12; 13)', 'Height': 48, 'Color': 'nfTextoSuave', 'Text': 'If(locL3Vista = "publicacoes";\n    CountRows(galL3Publicacoes.AllItems) & " de " &\n        CountRows(colL3Publicacoes) & " publicações";\n    CountRows(galL3Utilizadores.AllItems) & " de " &\n        CountRows(colL3Utilizadores) & " utilizadores")'}),
        btn_sec('btnL3Atualizar', '"Atualizar"', 'Select(btnL3Carregar)', {'Width': 150, 'DisplayMode': 'If(locL3ACarregar; DisplayMode.Disabled; DisplayMode.Edit)'}),
        C('btnL3Carregar', 'btn', {'Visible': False, 'Width': 10, 'Height': 10, 'Text': '"Carregar"', 'OnSelect': '''UpdateContext({locL3ACarregar: true; locL3Erro: ""});;
Clear(colL3Utilizadores);;
Clear(colL3Publicacoes);;
IfError(
    ClearCollect(colL3Utilizadores; JSONPlaceholderDAC.ListarUtilizadores());
    UpdateContext({locL3Erro: "Não foi possível obter os utilizadores. " & FirstError.Message})
);;
IfError(
    ClearCollect(colL3Publicacoes; JSONPlaceholderDAC.ListarPublicacoes());
    UpdateContext({locL3Erro: Trim(locL3Erro & " Não foi possível obter as publicações. " & FirstError.Message)})
);;
UpdateContext({locL3ACarregar: false})'''}),
    ]),
    H('conL3Erro', dict({'Fill': 'nfVermelhoFundo', 'Visible': '!IsBlank(locL3Erro)', 'Height': 88, 'LayoutGap': 16, 'LayoutAlignItems': 'LayoutAlignItems.Center', 'AlignInContainer': 'AlignInContainer.Stretch'}, **bradius(12), **pad(16)), [
        C('icoL3Aviso', 'ico', {'Icon': 'Icon.Warning', 'Color': 'nfVermelho', 'Width': 28, 'Height': 28}),
        C('lblL3Erro', 'lbl', {'Text': 'locL3Erro', 'FillPortions': 1, 'Color': 'ColorValue("#8E1F25")', 'Height': 56}),
        btn_pri('btnL3Repetir', '"Tentar novamente"', 'Select(btnL3Carregar)', {'Width': 190}),
    ]),
    C('lblL3ACarregar', 'lbl', {'Text': '"A carregar dados da API…"', 'Visible': 'locL3ACarregar', 'Align': 'Align.Center', 'Color': 'nfTextoSuave', 'Height': 60, 'AlignInContainer': 'AlignInContainer.Stretch'}),
    C('lblL3Vazio', 'lbl', {'Text': 'If(locL3Vista = "publicacoes";\n                        "A API não devolveu nenhuma publicação.";\n                        "A API não devolveu nenhum utilizador.")', 'Visible': '!locL3ACarregar && IsBlank(locL3Erro) &&\n    If(locL3Vista = "publicacoes"; IsEmpty(colL3Publicacoes); IsEmpty(colL3Utilizadores))', 'Align': 'Align.Center', 'Color': 'nfTextoSuave', 'Height': 60, 'AlignInContainer': 'AlignInContainer.Stretch'}),
    C('lblL3SemResultados', 'lbl', {'Text': '"Nada corresponde à pesquisa."', 'Visible': 'If(locL3Vista = "publicacoes";\n    !IsEmpty(colL3Publicacoes) && IsEmpty(galL3Publicacoes.AllItems);\n    !IsEmpty(colL3Utilizadores) && IsEmpty(galL3Utilizadores.AllItems))', 'Align': 'Align.Center', 'Color': 'nfTextoSuave', 'Height': 60, 'AlignInContainer': 'AlignInContainer.Stretch'}),
    C('galL3Utilizadores', 'gal', {'FillPortions': 1, 'TemplateSize': 80, 'TemplatePadding': 0, 'AlignInContainer': 'AlignInContainer.Stretch', 'TemplateFill': 'Color.White',
        'Items': 'Sort(\n    Filter(colL3Utilizadores;\n        txtL3Pesquisa.Text in name || txtL3Pesquisa.Text in email);\n    name\n)',
        'Visible': 'IsBlank(locL3Erro) && locL3Vista <> "publicacoes"', 'OnSelect': 'Navigate(scrL3Detalhe; ScreenTransition.Cover;\n    {locL3Sel: galL3Utilizadores.Selected})'}, [
        pill('btnL3Iniciais', dict({'X': 24, 'Y': 16, 'Width': 48, 'Height': 48, 'Fill': 'nfAzulClaro', 'Color': 'nfAzul', 'FontWeight': 'FontWeight.Bold', 'Size': 16, 'Text': 'Upper(Left(ThisItem.name; 1))'}, **bradius(24)), galeria=True),
        C('lblL3ItemNome', 'lbl', {'X': 88, 'Y': 14, 'Height': 28, 'Width': 'Parent.TemplateWidth - If(scrL3Lista.Size = ScreenSize.Small; 140; 380)', 'Wrap': False, 'Text': 'ThisItem.name', 'FontWeight': 'FontWeight.Semibold', 'Color': 'nfTexto'}),
        C('lblL3ItemEmail', 'lbl', {'X': 88, 'Y': 40, 'Height': 24, 'Width': 'Parent.TemplateWidth - If(scrL3Lista.Size = ScreenSize.Small; 140; 380)', 'Wrap': False, 'Text': 'ThisItem.email', 'Color': 'nfTextoSuave', 'Size': 12}),
        C('lblL3ItemEmpresa', 'lbl', {'X': 'Parent.TemplateWidth - 280', 'Y': 26, 'Width': 220, 'Height': 28, 'Text': 'ThisItem.company.name', 'Align': 'Align.Right', 'Color': 'nfTexto', 'Visible': 'scrL3Lista.Size > ScreenSize.Small'}),
        dict(chev('icoL3Abrir'), props=dict(chev('icoL3Abrir')['props'], X='Parent.TemplateWidth - 48', Y=28)),
        C('recL3Separador', 'rec', {'X': 0, 'Height': 1, 'Width': 'Parent.TemplateWidth', 'Y': 'Parent.TemplateHeight - 1', 'Fill': 'nfLinha'}),
    ]),
    C('galL3Publicacoes', 'gal', {'FillPortions': 1, 'TemplateSize': 96, 'TemplatePadding': 0, 'AlignInContainer': 'AlignInContainer.Stretch', 'TemplateFill': 'Color.White',
        'Items': 'Sort(\n    Filter(colL3Publicacoes;\n        (drpL3Utilizador.Selected.id = 0 || userId = drpL3Utilizador.Selected.id) &&\n        (txtL3Pesquisa.Text in title || txtL3Pesquisa.Text in body));\n    id\n)',
        'Visible': 'IsBlank(locL3Erro) && locL3Vista = "publicacoes"', 'OnSelect': 'Navigate(scrL3Publicacao; ScreenTransition.Cover;\n    {locL3Pub: galL3Publicacoes.Selected})'}, [
        C('lblL3PubItemTitulo', 'lbl', {'X': 24, 'Y': 10, 'Height': 28, 'Width': 'Parent.TemplateWidth - 96', 'Wrap': False, 'Text': 'ThisItem.title', 'FontWeight': 'FontWeight.Semibold', 'Color': 'nfTexto'}),
        C('lblL3PubItemAutor', 'lbl', {'X': 24, 'Y': 38, 'Height': 22, 'Width': 'Parent.TemplateWidth - 96', 'Wrap': False, 'Size': 12, 'Text': '"Publicação " & ThisItem.id & " · " &\n    Coalesce(LookUp(colL3Utilizadores; id = ThisItem.userId).name;\n             "Utilizador " & ThisItem.userId)', 'Color': 'nfTextoSuave'}),
        C('lblL3PubItemResumo', 'lbl', {'X': 24, 'Y': 62, 'Height': 24, 'Width': 'Parent.TemplateWidth - 96', 'Wrap': False, 'Size': 12, 'Text': 'Left(ThisItem.body; 100) & "…"', 'Color': 'nfTexto'}),
        dict(chev('icoL3PubAbrir'), props=dict(chev('icoL3PubAbrir')['props'], X='Parent.TemplateWidth - 48', Y=36)),
        C('recL3PubSeparador', 'rec', {'X': 0, 'Height': 1, 'Width': 'Parent.TemplateWidth', 'Y': 'Parent.TemplateHeight - 1', 'Fill': 'nfLinha'}),
    ]),
 ], scr='scrL3Lista')}

titulo_bloco = lambda n, t: C(n, 'lbl', {'Text': t, 'Size': 12, 'FontWeight': 'FontWeight.Bold', 'Color': 'nfTextoSuave', 'Height': 24, 'AlignInContainer': 'AlignInContainer.Stretch'})
linha = lambda n, t, extra=None: C(n, 'lbl', dict({'Text': t, 'Color': 'nfTexto', 'Height': 26, 'AlignInContainer': 'AlignInContainer.Stretch'}, **(extra or {})))
def bloco(n, kids):
    p = {'FillPortions': 1, 'LayoutMinWidth': 240, 'Fill': 'ColorValue("#F7F8F9")', 'BorderColor': 'nfLinha', 'BorderThickness': 1, 'LayoutGap': 6, 'Height': 160}
    p.update(bradius(12)); p.update(pad(16)); return V(n, p, kids)
def cart_l3(n, vis, kids, scr, extra=None):
    p = {'Width': f'Min(900; Parent.Width - If({scr}.Size = ScreenSize.Small; 32; 48))', 'LayoutGap': 20, 'FillPortions': 1, 'Visible': vis}
    p.update(pad(f'If({scr}.Size = ScreenSize.Small; 20; 32)')); p.update(extra or {})
    return cartao(n, p, kids)
cent_top = {'LayoutAlignItems': 'LayoutAlignItems.Center'}

SCREENS['scrL3Detalhe'] = {'props': {'Fill': 'nfFundo'}, 'controls': ecra('L3b', '"Ficha 03 · Detalhe"', cent_top, [
    C('lblL3SemSel', 'lbl', {'Text': '"Escolha um utilizador na lista."', 'Visible': 'IsBlank(locL3Sel)', 'Align': 'Align.Center', 'Color': 'nfTextoSuave', 'Height': 60, 'Width': 400}),
    cart_l3('conL3bCartao', '!IsBlank(locL3Sel)', scr='scrL3Detalhe', extra={'LayoutOverflowY': 'If(scrL3Detalhe.Size = ScreenSize.Small; LayoutOverflow.Scroll; LayoutOverflow.Hide)'}, kids=[
        H('conL3bTopo', {'Height': 'If(scrL3Detalhe.Size = ScreenSize.Small; 100; 76)', 'LayoutGap': 20, 'LayoutAlignItems': 'LayoutAlignItems.Center', 'AlignInContainer': 'AlignInContainer.Stretch'}, [
            pill('btnL3bIniciais', dict({'Width': 64, 'Height': 64, 'Fill': 'nfAzulClaro', 'Color': 'nfAzul', 'FontWeight': 'FontWeight.Bold', 'Size': 24, 'Text': 'Upper(Left(locL3Sel.name; 1))'}, **bradius(32))),
            V('conL3bNomes', {'FillPortions': 1, 'Height': 'If(scrL3Detalhe.Size = ScreenSize.Small; 100; 76)', 'LayoutGap': 0, 'LayoutJustifyContent': 'LayoutJustifyContent.Center'}, [
                C('lblL3Nome', 'lbl', {'Text': 'locL3Sel.name', 'Size': 'If(scrL3Detalhe.Size = ScreenSize.Small; 20; 28)', 'FontWeight': 'FontWeight.Bold', 'Color': 'nfTexto', 'AutoHeight': True, 'AlignInContainer': 'AlignInContainer.Stretch'}),
                C('lblL3Utilizador', 'lbl', {'Text': '"@" & locL3Sel.username', 'Color': 'nfTextoSuave', 'Height': 26, 'AlignInContainer': 'AlignInContainer.Stretch'}),
            ]),
        ]),
        H('conL3Blocos', {'LayoutWrap': True, 'LayoutGap': 24, 'AlignInContainer': 'AlignInContainer.Stretch', 'Height': 'Switch(scrL3Detalhe.Size; ScreenSize.Small; 528; ScreenSize.Medium; 344; 160)'}, [
            bloco('conL3Contacto', [titulo_bloco('lblL3TitContacto', '"CONTACTO"'), linha('lblL3Email', 'locL3Sel.email'), linha('lblL3Telefone', 'Coalesce(locL3Sel.phone; "Sem telefone")'), linha('lblL3Site', 'Coalesce(locL3Sel.website; "Sem site")')]),
            bloco('conL3Morada', [titulo_bloco('lblL3TitMorada', '"MORADA"'), linha('lblL3Rua', 'locL3Sel.address.street & ", " & locL3Sel.address.suite'), linha('lblL3Cidade', 'locL3Sel.address.zipcode & " " & locL3Sel.address.city')]),
            bloco('conL3Empresa', [titulo_bloco('lblL3TitEmpresa', '"EMPRESA"'), linha('lblL3Empresa', 'locL3Sel.company.name'), linha('lblL3Lema', 'locL3Sel.company.catchPhrase', {'Italic': True, 'Color': 'nfTextoSuave', 'Height': 48, 'VerticalAlign': 'VerticalAlign.Top'})]),
        ]),
        V('conL3PubsUtil', {'FillPortions': 'If(scrL3Detalhe.Size = ScreenSize.Small; 0; 1)', 'Height': 320, 'LayoutGap': 8, 'AlignInContainer': 'AlignInContainer.Stretch'}, [
            titulo_bloco('lblL3TituloPubs', '"PUBLICAÇÕES (" & CountRows(galL3PubsUtil.AllItems) & ")"'),
            C('galL3PubsUtil', 'gal', {'Items': 'Sort(Filter(colL3Publicacoes; userId = locL3Sel.id); id)', 'FillPortions': 1, 'TemplateSize': 52, 'TemplatePadding': 0, 'AlignInContainer': 'AlignInContainer.Stretch',
                'OnSelect': 'Navigate(scrL3Publicacao; ScreenTransition.Cover;\n    {locL3Pub: galL3PubsUtil.Selected})'}, [
                C('lblL3PubsUtilNum', 'lbl', {'X': 16, 'Y': 12, 'Width': 40, 'Height': 28, 'Text': 'ThisItem.id', 'FontWeight': 'FontWeight.Bold', 'Color': 'nfAzul', 'Size': 12}),
                C('lblL3PubsUtilItem', 'lbl', {'X': 60, 'Y': 12, 'Height': 28, 'Width': 'Parent.TemplateWidth - 110', 'Wrap': False, 'Text': 'ThisItem.title', 'Color': 'nfTexto'}),
                dict(chev('icoL3PubsUtilAbrir'), props=dict(chev('icoL3PubsUtilAbrir')['props'], X='Parent.TemplateWidth - 44', Y=14)),
                C('recL3PubsUtilSep', 'rec', {'X': 0, 'Height': 1, 'Width': 'Parent.TemplateWidth', 'Y': 'Parent.TemplateHeight - 1', 'Fill': 'nfLinha'}),
            ]),
        ]),
    ]),
 ], extra_cab=[icoVoltar('icoL3Voltar')], scr='scrL3Detalhe')}

SCREENS['scrL3Publicacao'] = {'props': {'Fill': 'nfFundo'}, 'controls': ecra('L3c', '"Ficha 03 · Publicação"', cent_top, [
    C('lblL3SemPub', 'lbl', {'Text': '"Escolha uma publicação na lista."', 'Visible': 'IsBlank(locL3Pub)', 'Align': 'Align.Center', 'Color': 'nfTextoSuave', 'Height': 60, 'Width': 400}),
    cart_l3('conL3cCartao', '!IsBlank(locL3Pub)', scr='scrL3Publicacao', kids=[
        C('lblL3PubNumero', 'lbl', {'Text': '"PUBLICAÇÃO N.º " & locL3Pub.id', 'Size': 12, 'Color': 'nfTextoSuave', 'FontWeight': 'FontWeight.Bold', 'Height': 24, 'AlignInContainer': 'AlignInContainer.Stretch'}),
        C('lblL3PubTitulo', 'lbl', {'Text': 'locL3Pub.title', 'Size': 'If(scrL3Publicacao.Size = ScreenSize.Small; 20; 26)', 'FontWeight': 'FontWeight.Bold', 'Color': 'nfTexto', 'AutoHeight': True, 'AlignInContainer': 'AlignInContainer.Stretch'}),
        H('conL3PubAutor', dict({'Height': 'If(scrL3Publicacao.Size = ScreenSize.Small; 136; 76)', 'LayoutWrap': True, 'LayoutGap': 14, 'LayoutAlignItems': 'LayoutAlignItems.Center', 'Fill': 'ColorValue("#F7F8F9")', 'BorderColor': 'nfLinha', 'BorderThickness': 1, 'AlignInContainer': 'AlignInContainer.Stretch'}, **bradius(12), **pad(14)), [
            pill('btnL3PubIniciais', dict({'Width': 48, 'Height': 48, 'Fill': 'nfAzulClaro', 'Color': 'nfAzul', 'FontWeight': 'FontWeight.Bold', 'Size': 16, 'Text': 'Upper(Left(LookUp(colL3Utilizadores; id = locL3Pub.userId).name; 1))'}, **bradius(24))),
            C('lblL3PubAutor', 'lbl', {'FillPortions': 1, 'Height': 44, 'FontWeight': 'FontWeight.Semibold', 'Color': 'nfTexto', 'Text': 'With({autor: LookUp(colL3Utilizadores; id = locL3Pub.userId)};\n    If(IsBlank(autor); "Utilizador " & locL3Pub.userId;\n       autor.name & " · @" & autor.username))'}),
            btn_sec('btnL3VerAutor', '"Ver autor"', 'Navigate(scrL3Detalhe; ScreenTransition.Cover;\n    {locL3Sel: LookUp(colL3Utilizadores; id = locL3Pub.userId)})', {'Width': 140, 'Height': 44,
                'DisplayMode': 'If(IsBlank(LookUp(colL3Utilizadores; id = locL3Pub.userId));\n    DisplayMode.Disabled; DisplayMode.Edit)'}),
        ]),
        C('lblL3PubTexto', 'lbl', {'Text': 'locL3Pub.body', 'Size': 16, 'Color': 'ColorValue("#2F3B45")', 'FillPortions': 1, 'VerticalAlign': 'VerticalAlign.Top', 'AlignInContainer': 'AlignInContainer.Stretch'}),
        C('lblL3PubNota', 'lbl', {'Text': '"Dados fictícios devolvidos pela API de demonstração JSONPlaceholder."', 'Size': 11, 'Color': 'nfTextoSuave', 'Height': 24, 'AlignInContainer': 'AlignInContainer.Stretch'}),
    ]),
 ], extra_cab=[icoVoltar('icoL3cVoltar')], scr='scrL3Publicacao')}

FORMULAS = '''nfAzul      = ColorValue("#1F4E79");;
nfAzulClaro = ColorValue("#E8EFF6");;
nfVerde     = ColorValue("#2E7D5B");;
nfVerdeFundo = ColorValue("#DDEFE6");;
nfVermelho  = ColorValue("#A4262C");;
nfVermelhoFundo = ColorValue("#FBE9EA");;
nfFundo     = ColorValue("#F6F4EF");;
nfTexto     = ColorValue("#1E2A33");;
nfTextoSuave = ColorValue("#46525C");;
nfLinha     = ColorValue("#E4E7EA");;'''

if __name__ == '__main__':
    import yaml
    names = []
    def walk(cs):
        for c in cs:
            names.append(c['name']); walk(c['kids'])
    # Correcções verificadas no Studio (ver Manual, nota B3):
    # - contentores de altura fixa dentro de um contentor automático precisam de FillPortions 0;
    # - contentores sem sombra explícita herdam DropShadow.Light, por isso ficam com None;
    # - etiquetas e ícones dentro de galerias precisam de OnSelect = Select(Parent).
    def corrige(cs, pai_auto=False, em_galeria=False):
        for c in cs:
            p = c['props']
            if c['kind'] == 'con':
                if pai_auto and 'FillPortions' not in p and 'Height' in p: p['FillPortions'] = 0
                p.setdefault('DropShadow', 'DropShadow.None')
                if p.get('DropShadow') == 'DropShadow.Medium': p['DropShadow'] = 'DropShadow.Regular'
            if em_galeria and c['kind'] in ('lbl', 'ico') and 'OnSelect' not in p: p['OnSelect'] = 'Select(Parent)'
            auto = c['kind'] == 'con' and (c['variant'] or CT['con'][1]) == 'AutoLayout'
            corrige(c['kids'], auto, em_galeria or c['kind'] == 'gal')
    for scr, d in SCREENS.items():
        corrige(d['controls'])
        txt ='\n'.join(sum((emit(c) for c in d['controls']), [])) + '\n'
        yaml.safe_load(txt)  # valida YAML
        open(os.path.join(OUT, 'yaml', f'{scr}.controls.yaml'), 'w').write(txt)
        props = {k: pt2inv(v) for k, v in d['props'].items()}
        open(os.path.join(OUT, 'yaml', f'{scr}.screen-props.json'), 'w').write(json.dumps({k: '=' + v for k, v in props.items()}, ensure_ascii=False, indent=1))
        walk(d['controls'])
    dup = {n for n in names if names.count(n) > 1}
    print('controlos:', len(names), 'duplicados:', dup)
    open(os.path.join(OUT, 'yaml', 'App.Formulas.pt.txt'), 'w').write(FORMULAS + '\n')
    open(os.path.join(OUT, 'yaml', 'App.Formulas.invariante.txt'), 'w').write(pt2inv(FORMULAS) + '\n')
