import pytest

from tools.dac import pafx


@pytest.mark.parametrize("inv, pt", [
    ('If(a, b, c)', 'If(a; b; c)'),
    ('Set(x, 1); Navigate(scrA)', 'Set(x; 1);; Navigate(scrA)'),
    ('RGBA(30, 42, 51, 0.55)', 'RGBA(30; 42; 51; 0,55)'),
    ('"Olá, mundo; fim"', '"Olá, mundo; fim"'),                 # texto não muda
    ("Filter('A, B', x)", "Filter('A, B'; x)"),                  # plicas não mudam
    ('"Diz ""olá, tu"""', '"Diz ""olá, tu"""'),                  # aspas escapadas
    ('x2.5', 'x2.5'),                                            # não é número decimal
    ('$"Olá, {Text(n, "0.0")}"', '$"Olá, {Text(n; "0.0")}"'),    # interpolação
    ('a // nota, com vírgula\n, b', 'a // nota, com vírgula\n; b'),
])
def test_conversao_pt(inv, pt):
    assert pafx.para_pt(inv) == pt
    assert pafx.para_invariante(pt) == inv


def test_equilibrio():
    assert pafx.verificar_equilibrio('If(a, (b), [c], {d: 1})') == []
    assert pafx.verificar_equilibrio('If(a, b') == ["falta fechar: ("]
    assert pafx.verificar_equilibrio('If(a, "(", b)') == []
    assert "sem abertura" in pafx.verificar_equilibrio('a)')[0]
    assert "por terminar" in pafx.verificar_equilibrio('"abc')[0]


def test_identificadores_ignora_chaves_de_registo_e_texto():
    ids = pafx.identificadores('Navigate(scrX, ScreenTransition.Cover, {locSel: galA.Selected}) & "locFalso"')
    assert "locSel" not in ids
    assert "locFalso" not in ids
    assert {"Navigate", "scrX", "ScreenTransition", "galA"} <= set(ids)


def test_so_codigo_apaga_texto():
    assert "Text(" not in pafx.so_codigo('"use Text(x) aqui"')
