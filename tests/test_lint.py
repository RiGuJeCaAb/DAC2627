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
        _c("Label1", "Label@2.5.1", {"TabIndex": "=-1", "FocusedBorderThickness": "=2"}),
        _c("lblTitulo", "Label@2.5.1", {"TabIndex": "=-1", "FocusedBorderThickness": "=2"}),
        _c("lblL1Ok", "Label@2.5.1", {"TabIndex": "=-1", "FocusedBorderThickness": "=2"}),
    ]))
    assert ("DAC101", "Label1") in r
    assert ("DAC101", "lblTitulo") in r
    assert ("DAC101", "lblL1Ok") not in r


def test_cor_literal_e_token_em_falta():
    r = _regras(_app(), _ecra("scrL1A", [
        _c("recL1A", "Rectangle@2.3.0", {"Fill": '=ColorValue("#FF0000")', "AccessibleLabel": '=""', "TabIndex": "=-1"}),
        _c("recL1B", "Rectangle@2.3.0", {"Fill": "=nfInexistente", "AccessibleLabel": '=""', "TabIndex": "=-1"}),
        _c("recL1C", "Rectangle@2.3.0", {"Fill": "=Color.White", "AccessibleLabel": '=""', "TabIndex": "=-1"}),
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
        _c("lblL1B", "Label@2.5.1", {"Text": "=locNunca", "TabIndex": "=-1", "FocusedBorderThickness": "=2"}),
    ]))
    assert ("DAC403", "btnL1A") in r
    assert sum(1 for x in r if x[0] == "DAC103") == 2
    assert ("DAC404", "lblL1B") in r


def test_navigate_define_loc_no_ecra_destino():
    r = _regras(_app(),
                _ecra("scrL3A", [_c("btnL3A", "Classic/Button@2.2.0", {
                    "OnSelect": "=Navigate(scrL3B, ScreenTransition.Cover, {locL3Sel: 1})"})]),
                _ecra("scrL3B", [_c("lblL3B", "Label@2.5.1", {
                    "Text": "=locL3Sel", "TabIndex": "=-1", "FocusedBorderThickness": "=2"})]))
    assert not any(x[0] == "DAC404" for x in r)


def test_acessibilidade():
    r = _regras(_app(), _ecra("scrL1A", [
        _c("icoL1A", "Classic/Icon@2.5.0", {"OnSelect": "=Back()", "Width": "=24", "Height": "=24"}),
        _c("txtL1B", "Classic/TextInput@2.3.2", {}),
        _c("lblL1C", "Label@2.5.1", {}),
    ]))
    assert ("DAC301", "icoL1A") in r and ("DAC301", "txtL1B") in r
    assert ("DAC302", "icoL1A") in r and ("DAC302", "lblL1C") in r
    assert ("DAC303", "lblL1C") in r
    assert ("DAC304", "icoL1A") in r


def test_excecao_precisa_de_motivo():
    doc = _ecra("scrL1A", [_c("lblL1C", "Label@2.5.1", {"FocusedBorderThickness": "=2"})])
    com = lint.Config(excecoes=[{"regra": "DAC302", "controlo": "lblL1C", "motivo": "teste"}])
    sem = lint.Config(excecoes=[{"regra": "DAC302", "controlo": "lblL1C"}])
    assert ("DAC302", "lblL1C") not in _regras(_app(), doc, cfg=com)
    r = _regras(_app(), doc, cfg=sem)
    assert ("DAC302", "lblL1C") in r and any(x[0] == "DAC900" for x in r)
