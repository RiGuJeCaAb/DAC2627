from tools.dac import lint


def _app(formulas='nfAzul = ColorValue("#1F4E79");'):
    return {"App": {"Properties": {"Formulas": "=" + formulas}}}


def _ecra(nome, filhos, props=None):
    return {"Screens": {nome: {"Properties": props or {}, "Children": filhos}}}


def _c(nome, controlo, props=None, filhos=None, variante=None):
    corpo = {"Control": controlo}
    if variante:
        corpo["Variant"] = variante
    corpo["Properties"] = props or {}
    if filhos:
        corpo["Children"] = filhos
    return {nome: corpo}


def _regras(*docs, cfg=None):
    d = {f"f{i}": x for i, x in enumerate(docs)}
    return [(a.regra, a.controlo) for a in lint.Analise(d, cfg).correr()]


def test_prefixo_e_ficha():
    r = _regras(_app(), _ecra("scrL1A", [
        _c("Label1", "Label@2.5.1", {"FocusedBorderThickness": "=2"}),
        _c("lblTitulo", "Label@2.5.1", {"FocusedBorderThickness": "=2"}),
        _c("lblL1Ok", "Label@2.5.1", {"FocusedBorderThickness": "=2"}),
    ]))
    assert ("DAC101", "Label1") in r
    assert ("DAC101", "lblTitulo") in r
    assert ("DAC101", "lblL1Ok") not in r


def test_cor_literal_e_token_em_falta():
    r = _regras(_app(), _ecra("scrL1A", [
        _c("recL1A", "Rectangle@2.3.0", {"Fill": '=ColorValue("#FF0000")'}),
        _c("recL1B", "Rectangle@2.3.0", {"Fill": "=nfInexistente"}),
        _c("recL1C", "Rectangle@2.3.0", {"Fill": "=Color.White"}),
    ]))
    assert ("DAC201", "recL1A") in r
    assert any(x[0] == "DAC202" for x in r)
    assert not any(c == "recL1C" for _, c in r)


def test_delegacao():
    item_mau = "=Filter('Cloud Service', Text('Service Model') = \"IaaS\")"
    item_bom = ("=Filter('Cloud Service', 'Service Model' = LookUp(Choices('Cloud Service'.'Service Model'), "
                "Text(Value) = drpL2M.Selected.Value).Value)")
    base = {"AccessibleLabel": '="x"', "TabIndex": "=0"}
    r = _regras(_app(), _ecra("scrL2A", [
        _c("galL2Mau", "Gallery@2.15.0", dict(base, Items=item_mau), variante="Vertical"),
        _c("galL2Bom", "Gallery@2.15.0", dict(base, Items=item_bom), variante="Vertical"),
        _c("drpL2M", "Classic/DropDown@2.3.1", {"AccessibleLabel": '="m"'}),
    ]))
    assert ("DAC402", "galL2Mau") in r
    assert ("DAC402", "galL2Bom") not in r


def test_referencia_inexistente_e_variaveis():
    r = _regras(_app(), _ecra("scrL1A", [
        _c("btnL1A", "Classic/Button@2.2.0", {
            "OnSelect": '=Select(btnL1Fantasma); UpdateContext({aviso: true}); Set(nome, 1); Navigate(scrL1A)'}),
        _c("lblL1B", "Label@2.5.1", {"Text": "=locNunca", "FocusedBorderThickness": "=2"}),
    ]))
    assert ("DAC403", "btnL1A") in r
    assert sum(1 for x in r if x[0] == "DAC103") == 2
    assert ("DAC404", "lblL1B") in r


def test_navigate_define_loc_no_ecra_destino():
    r = _regras(_app(),
                _ecra("scrL3A", [_c("btnL3A", "Classic/Button@2.2.0", {
                    "OnSelect": "=Navigate(scrL3B, ScreenTransition.Cover, {locL3Sel: 1})"})]),
                _ecra("scrL3B", [_c("lblL3B", "Label@2.5.1", {
                    "Text": "=locL3Sel", "FocusedBorderThickness": "=2"})]))
    assert not any(x[0] == "DAC404" for x in r)


def test_acessibilidade():
    r = _regras(_app(), _ecra("scrL1A", [
        _c("icoL1A", "Classic/Icon@2.5.0", {"OnSelect": "=Back()", "Width": "=24", "Height": "=24"}),
        _c("txtL1B", "Classic/TextInput@2.3.2", {}),
        _c("lblL1C", "Label@2.5.1", {}),
        _c("recL1D", "Rectangle@2.3.0", {}),
        _c("btnL1E", "Classic/Button@2.2.0", {"OnSelect": "=Back()", "TabIndex": "=-1"}),
    ]))
    assert ("DAC301", "icoL1A") in r and ("DAC301", "txtL1B") in r
    # ícone com ação: TabIndex ausente vale -1, fica fora da ordem de tabulação
    assert ("DAC302", "icoL1A") in r and ("DAC302", "btnL1E") in r
    assert ("DAC303", "lblL1C") in r
    assert ("DAC304", "icoL1A") in r
    # etiqueta e retângulo decorativos: TabIndex e AccessibleLabel ausentes são -1 e "", como o Studio guarda
    assert ("DAC302", "lblL1C") not in r and ("DAC302", "recL1D") not in r and ("DAC301", "recL1D") not in r


def test_valor_por_omissao_escrito():
    r = _regras(_app(), _ecra("scrL1A", [
        _c("lblL1A", "Label@2.5.1", {"TabIndex": "=-1", "FocusedBorderThickness": "=2", "Size": "=13"}),
        _c("conL1B", "GroupContainer@1.5.0", {"DropShadow": "=DropShadow.Light"}),
        _c("btnL1C", "Classic/Button@2.2.0", {"OnSelect": "=Back()", "Width": "=120", "Height": "=44"}),
        _c("btnL1D", "Classic/Button@2.2.0", {"OnSelect": "=Back()", "TabIndex": "=0", "Width": "=120", "Height": "=44"}),
    ]))
    assert ("DAC504", "lblL1A") in r and ("DAC504", "conL1B") in r
    # o Studio apaga TabIndex 0 nos botões (visto na 1.0.0.4)
    assert ("DAC504", "btnL1D") in r and ("DAC504", "btnL1C") not in r
    assert sum(1 for x in r if x[0] == "DAC504") == 4


def test_sombra_dentro_de_sombra():
    pai = _c("conL1A", "GroupContainer@1.5.0", {})
    pai["conL1A"]["Children"] = [_c("conL1B", "GroupContainer@1.5.0", {}),
                                 _c("conL1C", "GroupContainer@1.5.0", {"DropShadow": "=DropShadow.None"})]
    r = _regras(_app(), _ecra("scrL1A", [pai]))
    assert ("DAC503", "conL1B") in r and ("DAC503", "conL1C") not in r and ("DAC503", "conL1A") not in r


def test_definir_valor_por_omissao_apaga_a_linha():
    from tools.dac import yamlio
    doc = _ecra("scrL1A", [_c("lblL1A", "Label@2.5.1", {"TabIndex": "=-1", "Text": '="a"'})])
    c = next(yamlio.controlos(doc))
    c.definir("TabIndex", "=-1")
    assert c.prop("TabIndex") is None and c.prop("Text") == '="a"'
    c.definir("TabIndex", "=0")
    assert c.prop("TabIndex") == "=0"


def test_excecao_precisa_de_motivo():
    doc = _ecra("scrL1A", [_c("btnL1C", "Classic/Button@2.2.0", {"TabIndex": "=-1", "Width": "=120", "Height": "=44"})])
    com = lint.Config(excecoes=[{"regra": "DAC302", "controlo": "btnL1C", "motivo": "teste"}])
    sem = lint.Config(excecoes=[{"regra": "DAC302", "controlo": "btnL1C"}])
    assert ("DAC302", "btnL1C") not in _regras(_app(), doc, cfg=com)
    r = _regras(_app(), doc, cfg=sem)
    assert ("DAC302", "btnL1C") in r and any(x[0] == "DAC900" for x in r)


def test_propriedade_desconhecida():
    conhecidas = {"groupcontainer": {"LayoutOverflowY", "LayoutDirection"}, "label": {"Text"},
                  "dropdown": {"Items"}, "screen": {"Fill"}}
    ecra = _ecra("scrL1A", [
        _c("conL1A", "GroupContainer@1.5.0", {"LayoutOverflow": "=LayoutOverflow.Scroll"}, variante="AutoLayout"),
        _c("conL1B", "GroupContainer@1.5.0", {"LayoutOverflowY": "=LayoutOverflow.Scroll"}, variante="AutoLayout"),
        _c("drpL1C", "DropDown@0.0.45", {"Items.Value": "=Value"}),
        _c("tmrL1D", "Timer@2.1.0", {"Qualquer": "=1"}),
    ], props={"Fill": "=nfFundo", "Cor": "=1"})
    d = {"a": _app(), "b": ecra}
    r = [(a.regra, a.onde) for a in lint.Analise(d, None, conhecidas).correr() if a.regra == "DAC405"]
    assert r == [("DAC405", "scrL1A.Cor"), ("DAC405", "scrL1A.conL1A.LayoutOverflow")]
    # sem exportação a regra não corre
    assert not [a for a in lint.Analise(d).correr() if a.regra == "DAC405"]


def test_propriedades_da_exportacao_do_projeto():
    from tools.dac import projeto
    p = projeto.propriedades_exportadas()
    assert "LayoutOverflowY" in p["groupcontainer"] and "LayoutOverflow" not in p["groupcontainer"]
    assert {"OnSelect", "TemplateFill"} <= p["gallery"]
    assert "FillPortions" in p["label"]


def test_navigate_no_onvisible_e_no_onstart():
    # o Studio recusa Navigate no OnVisible de um ecrã (mesmo dentro de um If) e no App.OnStart
    app = _app()
    app["App"]["Properties"]["OnStart"] = "=Set(gblL1X, 1); Navigate(scrL1A)"
    r = [(a.regra, a.onde) for a in lint.Analise({
        "a": app,
        "b": _ecra("scrL1A", [], {"OnVisible": "=If(IsBlank(gblL1X), Navigate(scrL1B, ScreenTransition.None))"}),
        "c": _ecra("scrL1B", [], {"OnVisible": '=UpdateContext({locL1T: "Navigate(scrL1A)"})'}),
    }).correr() if a.regra == "DAC406"]
    assert r == [("DAC406", "App.OnStart"), ("DAC406", "scrL1A.OnVisible")]


def test_combobox_fora_de_formulario_avisa_e_dentro_nao():
    def cmb(nome, items):
        return {nome: {"Control": "Classic/ComboBox@2.4.0",
                       "Properties": {"AccessibleLabel": '="Cliente"', "Items": items, "TabIndex": "=0"}}}
    cartao = _c("Cliente_DataCard1", "TypedDataCard@1.0.7", {}, [cmb("cmbL1FormCliente", "=Choices([@Pedidos].dac_Cliente)")])
    form = _c("frmL1Pedido", "Form@2.4.4", {"DataSource": "=Pedidos"}, [cartao])
    r = [a.onde for a in lint.Analise({
        "a": _app(),
        "b": _ecra("scrL1A", [cmb("cmbL1Tabela", "=AddColumns(Sort(Clientes, Nome), NomeCliente, Nome)"),
                              cmb("cmbL1Colecao", "=colL1Clientes"), form,
                              _c("drpL1Cliente", "Classic/DropDown@2.3.1", {"Items": "=Sort(Clientes, Nome)", "Items.Value": "=Nome"})]),
    }).correr() if a.regra == "DAC407"]
    assert sorted(r) == ["scrL1A.cmbL1Colecao", "scrL1A.cmbL1Tabela"]


def test_reset_de_controlo_de_formulario_feito_de_fora():
    caixa = {"txtL1Valor": {"Control": "Classic/TextInput@2.3.2", "Properties": {"AccessibleLabel": '="Valor"', "TabIndex": "=0"}}}
    repor_dentro = {"btnL1Dentro": {"Control": "Classic/Button@2.2.0",
                                    "Properties": {"OnSelect": "=Reset(txtL1Valor)", "TabIndex": "=0", "Text": '="A"'}}}
    cartao = _c("Valor_DataCard1", "TypedDataCard@1.0.7", {}, [caixa, repor_dentro])
    form = _c("frmL1Pedido", "Form@2.4.4", {"DataSource": "=Pedidos"}, [cartao])
    fora = {"btnL1Fora": {"Control": "Classic/Button@2.2.0",
                          "Properties": {"OnSelect": "=UpdateContext({locX: 1}); Reset(txtL1Valor)", "TabIndex": "=0", "Text": '="B"'}}}
    livre = {"txtL1Livre": {"Control": "Classic/TextInput@2.3.2", "Properties": {"AccessibleLabel": '="Livre"', "TabIndex": "=0"}}}
    repor_livre = {"btnL1Livre": {"Control": "Classic/Button@2.2.0",
                                  "Properties": {"OnSelect": "=Reset(txtL1Livre)", "TabIndex": "=0", "Text": '="C"'}}}
    r = [a.onde for a in lint.Analise({"a": _app(), "b": _ecra("scrL1A", [form, fora, livre, repor_livre])}).correr()
         if a.regra == "DAC408"]
    assert r == ["scrL1A.btnL1Fora.OnSelect"]


def test_caixa_de_pesquisa_sem_delayoutput():
    def caixa(nome, props=None):
        return {nome: {"Control": "Classic/TextInput@2.3.2",
                       "Properties": {"AccessibleLabel": '="Pesquisa"', "TabIndex": "=0", **(props or {})}}}
    gal = _c("galL1Lista", "Gallery@2.15.0", {"Items": '=Filter(Pedidos, StartsWith(Nome, txtL1Pesquisa.Text))',
                                              "AccessibleLabel": '="Lista"', "TabIndex": "=0"})
    botao = {"btnL1Ok": {"Control": "Classic/Button@2.2.0",
                         "Properties": {"OnSelect": '=Patch(Pedidos, Defaults(Pedidos), {Nome: txtL1Nome.Text})',
                                        "TabIndex": "=0", "Text": '="Ok"'}}}
    lbl = _c("lblL1Conta", "Label@2.5.1", {"Text": '=CountRows(Filter(Pedidos, Nome = txtL1Atrasada.Text))',
                                           "FocusedBorderThickness": "=2"})
    r = [a.onde for a in lint.Analise({"a": _app(), "b": _ecra("scrL1A", [
        caixa("txtL1Pesquisa"), caixa("txtL1Nome"), caixa("txtL1Atrasada", {"DelayOutput": "=true"}), gal, botao, lbl,
    ])}).correr() if a.regra == "DAC409"]
    # a pesquisa filtra a galeria; o nome só é lido num OnSelect; a terceira já tem DelayOutput
    assert r == ["scrL1A.txtL1Pesquisa"]


def test_retangulo_em_galeria_sem_select_parent():
    gal = _c("galL1Lista", "Gallery@2.15.0", {"Items": "=Pedidos", "AccessibleLabel": '="Lista"', "TabIndex": "=0"}, [
        _c("recL1Sep", "Rectangle@2.3.0", {}),
        _c("recL1Fundo", "Rectangle@2.3.0", {"OnSelect": "=Select(Parent)"}),
    ])
    r = [a.controlo for a in lint.Analise({"a": _app(), "b": _ecra("scrL1A", [gal])}).correr() if a.regra == "DAC502"]
    assert r == ["recL1Sep"]


def test_index_em_vez_de_last_firstn():
    r = [a.onde for a in lint.Analise({"a": _app(), "b": _ecra("scrL1A", [
        _c("lblL1Dois", "Label@2.5.1", {"Text": '=Last(FirstN(colL1Nomes, 2)).Value', "FocusedBorderThickness": "=2"}),
        _c("lblL1Fim", "Label@2.5.1", {"Text": '=First( LastN(colL1Nomes, 3)).Value', "FocusedBorderThickness": "=2"}),
        _c("lblL1Bom", "Label@2.5.1", {"Text": '=Index(colL1Nomes, 2).Value & "Last(FirstN("', "FocusedBorderThickness": "=2"}),
    ])}).correr() if a.regra == "DAC410"]
    assert r == ["scrL1A.lblL1Dois.Text", "scrL1A.lblL1Fim.Text"]


def test_ecra_com_demasiados_controlos():
    muitos = [_c(f"lblL1E{i}", "Label@2.5.1", {"FocusedBorderThickness": "=2"}) for i in range(lint.MAX_CONTROLOS + 1)]
    poucos = [_c(f"lblL1P{i}", "Label@2.5.1", {"FocusedBorderThickness": "=2"}) for i in range(lint.MAX_CONTROLOS)]
    r = [a.onde for a in lint.Analise({"a": _app(), "b": _ecra("scrL1A", muitos), "c": _ecra("scrL1B", poucos)}).correr()
         if a.regra == "DAC411"]
    assert r == ["scrL1A"]


def _faixa(mostra_visible="=locMsg <> \"\"", anunciadora=None):
    filhos = [_c("conL2Mensagem", "GroupContainer@1.5.0", {"Visible": mostra_visible, "DropShadow": "=DropShadow.None"},
                 [_c("lblL2Mensagem", "Label@2.5.1", {"Text": "=locMsg", "FocusedBorderThickness": "=2"})],
                 variante="AutoLayout")]
    if anunciadora:
        filhos.append(_c("lblL2Anuncio", "Label@2.5.1", dict({"Text": "=locMsg", "FocusedBorderThickness": "=2"}, **anunciadora)))
    return _ecra("scrL2A", filhos, {"OnVisible": '=UpdateContext({locMsg: ""})'})


def test_dac305_mensagem_sem_regiao_viva():
    assert ("DAC305", "lblL2Mensagem") in _regras(_app(), _faixa())


def test_dac305_anunciadora_sempre_visivel_resolve():
    assert not any(r == "DAC305" for r, _ in _regras(_app(), _faixa(anunciadora={"Live": "=Live.Polite"})))


def test_dac305_live_numa_faixa_que_desaparece_nao_chega():
    # Live na própria etiqueta, mas dentro de um contentor com Visible condicional: não conta como região viva
    doc = _ecra("scrL2A", [_c("conL2Mensagem", "GroupContainer@1.5.0", {"Visible": '=locMsg <> ""', "DropShadow": "=DropShadow.None"},
                              [_c("lblL2Mensagem", "Label@2.5.1", {"Text": "=locMsg", "Live": "=Live.Polite",
                                                                   "FocusedBorderThickness": "=2"})], variante="AutoLayout")],
                {"OnVisible": '=UpdateContext({locMsg: ""})'})
    assert ("DAC305", "lblL2Mensagem") in _regras(_app(), doc)


def test_dac305_anunciadora_com_live_off_nao_conta():
    assert ("DAC305", "lblL2Mensagem") in _regras(_app(), _faixa(anunciadora={"Live": "=Live.Off"}))
