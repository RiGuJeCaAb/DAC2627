"""Testes sobre o próprio projeto: o que está em src/ tem de estar sempre em ordem."""
import shutil
import subprocess
import sys
import zipfile

import pytest

from tools.dac import cli, cores, projeto, yamlio


def test_ida_e_volta_byte_a_byte():
    for f in projeto.ficheiros_src() + sorted((projeto.MSAPP / "Src").glob("*.pa.yaml")):
        assert f.read_text(encoding="utf-8") == yamlio.escrever_texto(yamlio.ler(f)), f


@pytest.mark.parametrize("cmd", [["validar"], ["lint", "--estrito"], ["paleta", "--verificar"],
                                 ["inventario", "--verificar"], ["formatar", "--verificar"]])
def test_comandos_passam(cmd):
    assert cli.main(cmd) == 0


def test_contraste_wcag():
    assert round(cores.contraste((0, 0, 0), (255, 255, 255)), 2) == 21.0
    assert cores.nivel(4.6) == "AA" and cores.nivel(7.1) == "AAA" and cores.nivel(3) == "falha"


def test_migracao_idempotente(tmp_path):
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    from tools.migracoes import m001_v1_1_qualidade as m
    antes = {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    m.main(raiz)
    assert antes == {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}


def test_migracao_m002_idempotente(tmp_path):
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    from tools.migracoes import m002_v1_2_ficha04 as m
    antes = {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    m.main(raiz)
    assert antes == {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}


def test_colar_gera_yaml_valido(tmp_path):
    assert cli.main(["colar", "--destino", str(tmp_path)]) == 0
    d = yamlio.ler(tmp_path / "TODOS_OS_ECRAS.yaml")
    assert list(d["Screens"]) == projeto.ordem_ecras()
    assert ";;" in (tmp_path / "App.Formulas.pt.txt").read_text(encoding="utf-8")


def test_sincronizar_recusa_zip_perigoso(tmp_path):
    z = tmp_path / "mau.zip"
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("../fora.txt", "x")
    raiz = tmp_path / "proj"
    (raiz / "src").mkdir(parents=True)
    with pytest.raises(SystemExit):
        cli.main(["--raiz", str(raiz), "sincronizar", str(z)])


def test_sincronizar_exportacao_original(tmp_path):
    raiz = tmp_path / "proj"
    (raiz / "src").mkdir(parents=True)
    assert cli.main(["--raiz", str(raiz), "sincronizar",
                     str(projeto.RAIZ / "_export" / "DAC2627_1_0_0_0.zip")]) == 0
    assert (raiz / "src" / "screens" / "scrL2Servicos.pa.yaml").exists()
    assert (raiz / "src" / "app" / "App.pa.yaml").exists()


def test_modulo_executavel():
    r = subprocess.run([sys.executable, "-m", "tools.dac", "--help"], cwd=projeto.RAIZ, capture_output=True, text=True)
    assert r.returncode == 0 and "validar" in r.stdout


def test_todas_as_regras_estao_documentadas():
    from tools.dac import lint
    doc = (projeto.DOCS / "regras-lint.md").read_text(encoding="utf-8")
    em_falta = [r for r in lint.REGRAS if f"| {r} |" not in doc]
    assert not em_falta, f"Regras sem documentação em docs/regras-lint.md: {em_falta}"


def _projeto_com_tabulador(tmp_path):
    """Cópia de src/ com um tabulador colado no fim de um texto, como o Studio exporta."""
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    shutil.copytree(projeto.RAIZ / "schemas", raiz / "schemas")
    shutil.copy2(projeto.RAIZ / "dac.yaml", raiz / "dac.yaml")
    f = raiz / "src" / "screens" / "scrL1BoasVindas.pa.yaml"
    t = f.read_text(encoding="utf-8")
    i = t.index('Text: ="') + len('Text: ="')
    j = t.index('"', i)
    f.write_text(t[:j] + "\t" + t[j:], encoding="utf-8")
    return raiz, f


def test_validar_avisa_tabulador_sem_falhar(tmp_path, capsys):
    raiz, f = _projeto_com_tabulador(tmp_path)
    assert cli.main(["--raiz", str(raiz), "validar"]) == 0
    out = capsys.readouterr().out
    assert "AVISO src/screens/scrL1BoasVindas.pa.yaml:" in out and "1 aviso(s)" in out


def test_formatar_nao_reescreve_ficheiro_com_tabulador(tmp_path, capsys):
    raiz, f = _projeto_com_tabulador(tmp_path)
    antes = f.read_text(encoding="utf-8")
    cli.main(["--raiz", str(raiz), "formatar"])
    assert f.read_text(encoding="utf-8") == antes          # o tabulador não vira espaço em silêncio
    assert cli.main(["--raiz", str(raiz), "formatar", "--verificar"]) == 1
    assert "não formatado" in capsys.readouterr().out


def test_lint_le_ficheiro_com_tabulador(tmp_path):
    raiz, _ = _projeto_com_tabulador(tmp_path)
    assert "scrL1BoasVindas" in str(list(projeto.carregar(raiz)))
