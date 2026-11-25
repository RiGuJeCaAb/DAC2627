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


def test_migracao_m003_idempotente(tmp_path):
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    from tools.migracoes import m003_v1_2_studio as m
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


def test_migracao_m004_idempotente(tmp_path):
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    shutil.copytree(projeto.RAIZ / "conteudo", raiz / "conteudo")
    from tools.migracoes import m004_v1_3_ponto8 as m
    antes = {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    m.main(raiz)
    assert antes == {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}


def test_migracao_m005_idempotente_e_ficha(tmp_path):
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    from tools.migracoes import m005_v1_4_ficha02_ficha as m
    antes = {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    m.main(raiz)
    assert antes == {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    ctl = {c.nome: c for c in yamlio.controlos(yamlio.ler(raiz / "src" / "screens" / "scrL2Servicos.pa.yaml"))}
    # a vista de leitura substitui o formulário em modo View; o formulário fica para criar e editar
    assert ctl["frmL2Servico"].prop("Visible") == "=Self.Mode <> FormMode.View"
    assert "FormMode.View" in ctl["conL2Ficha"].prop("Visible")
    for nome in ("conL2FichaFornecedor", "conL2FichaModelo", "conL2FichaEstado", "conL2FichaDescricao",
                 "conL2FichaResponsabilidade"):
        assert ctl[nome].pai.nome in ("conL2Ficha", "conL2FichaFactos"), nome
    assert ctl["lblL2FichaDescricao"].pai.nome == "conL2FichaDescricao"
    rotulos = {c.prop("Text") for c in ctl.values() if c.nome.startswith("DataCardKey")}
    assert not any("DisplayName" in str(r) for r in rotulos), "rótulos do formulário ainda em inglês"


def test_migracao_m005_a_partir_do_estado_anterior(tmp_path):
    """A m005 sobre o ecrã como estava antes dela (sem a ficha, rótulos do Dataverse, v1.3.0) dá o ecrã atual."""
    from tools.migracoes import m005_v1_4_ficha02_ficha as m
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    ecra, app = raiz / "src" / "screens" / "scrL2Servicos.pa.yaml", raiz / "src" / "app" / "App.pa.yaml"
    esperado = {f: f.read_text(encoding="utf-8") for f in (ecra, app)}
    d = yamlio.ler(ecra)
    for c in yamlio.controlos(d):
        if c.nome == "frmL2Servico":
            c.corpo["Properties"]["Visible"] = "=Self.Mode <> FormMode.View || !IsBlank(locSel)"
        elif c.nome == "conL2Painel":
            c.corpo["Children"] = [f for f in c.corpo["Children"] if "conL2Ficha" not in f]
        elif c.nome.startswith("DataCardKey") and c.pai.nome in m.ROTULOS:
            c.corpo["Properties"]["Text"] = "=Parent.DisplayName"
        elif c.nome.startswith(("txtL2", "cmbL2")) and c.pai and c.pai.nome in m.ROTULOS:
            c.corpo["Properties"].update(AccessibleLabel="=Parent.DisplayName", Tooltip="=Parent.DisplayName")
    yamlio.escrever(ecra, d)
    app.write_text(esperado[app].replace('nfVersao = "1.4.0"', 'nfVersao = "1.3.0"'), encoding="utf-8")
    assert ecra.read_text(encoding="utf-8") != esperado[ecra]
    m.main(raiz)
    assert {f: f.read_text(encoding="utf-8") for f in (ecra, app)} == esperado


def test_ponto8_conteudo_e_ecra_coerentes():
    import yaml
    c = yaml.safe_load((projeto.RAIZ / "conteudo" / "ponto8.yaml").read_text(encoding="utf-8"))
    # os sete critérios do enunciado do Lab 4, pela ordem do enunciado, e depois os dois da perspetiva cloud
    assert [x["criterio"] for x in c["criterios"]] == [
        "Estrutura", "Relações", "Desenvolvimento Power Apps", "Interface pronta", "Lógica", "Gestão",
        "Caso de uso sugerido", "Modelo de serviço cloud", "Custo e licenciamento"]
    # cada fonte citada existe, e cada fonte listada é citada (APA: nada na lista que não esteja no texto)
    ids = {f["id"] for f in c["fontes"]}
    citadas = {r for s in c["servicos"] for r in s["refs"]} | {r for q in c["documento"]["questoes"] for r in q["refs"]}
    assert citadas == ids
    assert [s["id"] for s in c["servicos"]] == ["Sp", "Dv", "Sql"]
    assert all(set(x) == {"criterio", "Sp", "Dv", "Sql"} for x in c["criterios"])
    assert all(s["favor"] and s["contra"] and s["oque"] for s in c["servicos"])
    d = yamlio.ler(projeto.RAIZ / "src" / "screens" / "scrL4Complemento.pa.yaml")
    nomes = {x.nome for x in yamlio.controlos(d)}
    assert {f"conL4bLinha{i}" for i in range(1, len(c["criterios"]) + 1)} <= nomes
    assert {"btnL4bVerTabela", "btnL4bVoltarTexto", "lblL4bConclusao"} <= nomes


def _copia(tmp_path):
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    shutil.copytree(projeto.RAIZ / "schemas", raiz / "schemas")
    shutil.copytree(projeto.RAIZ / "msapp", raiz / "msapp")
    shutil.copy2(projeto.RAIZ / "dac.yaml", raiz / "dac.yaml")
    return raiz


def _projeto_com_tabulador(tmp_path, entre_aspas=False):
    """Cópia do projeto com um tabulador colado no fim de um texto, como o Studio exporta.

    Devolve (raiz, ficheiro, número da linha alterada)."""
    raiz = _copia(tmp_path)
    f = raiz / "src" / "screens" / "scrL1BoasVindas.pa.yaml"
    t = f.read_text(encoding="utf-8")
    i = t.index('Text: ="') + len('Text: ="')
    j = t.index('"', i)
    if entre_aspas:
        # Valor YAML entre aspas simples: o PyYAML lê o tabulador sem erro
        ini = t.rindex("Text: ", 0, i) + len("Text: ")
        fim = t.index("\n", j)
        t = t[:ini] + "'" + t[ini:j].replace("'", "''") + "\t" + t[j:fim].replace("'", "''") + "'" + t[fim:]
    else:
        t = t[:j] + "\t" + t[j:]
    f.write_text(t, encoding="utf-8")
    return raiz, f, t[:j].count("\n") + 1


def test_validar_avisa_tabulador_sem_falhar(tmp_path, capsys):
    raiz, f, linha = _projeto_com_tabulador(tmp_path)
    assert cli.main(["--raiz", str(raiz), "validar"]) == 0
    out = capsys.readouterr().out
    assert f"AVISO src/screens/scrL1BoasVindas.pa.yaml:{linha}:" in out and "1 aviso(s)" in out


def test_tabulador_na_indentacao_continua_a_ser_erro(tmp_path, capsys):
    raiz = _copia(tmp_path)
    f = raiz / "src" / "screens" / "scrL1BoasVindas.pa.yaml"
    linhas = f.read_text(encoding="utf-8").split("\n")
    n = next(k for k, ln in enumerate(linhas) if ln.startswith("        ") and ":" in ln)
    linhas[n] = "\t" + linhas[n][8:]
    f.write_text("\n".join(linhas), encoding="utf-8")
    assert cli.main(["--raiz", str(raiz), "validar"]) == 1
    assert "YAML inválido" in capsys.readouterr().out


@pytest.mark.parametrize("entre_aspas", [False, True])
def test_formatar_nao_reescreve_ficheiro_com_tabulador(tmp_path, capsys, entre_aspas):
    raiz, f, _ = _projeto_com_tabulador(tmp_path, entre_aspas)
    antes = f.read_text(encoding="utf-8")
    assert cli.main(["--raiz", str(raiz), "formatar"]) == 1   # saltou um ficheiro: não é sucesso
    assert f.read_text(encoding="utf-8") == antes              # o tabulador não vira espaço em silêncio
    assert cli.main(["--raiz", str(raiz), "formatar", "--verificar"]) == 1
    assert "não formatado" in capsys.readouterr().out


def test_lint_le_ficheiro_com_tabulador(tmp_path):
    raiz, _, _ = _projeto_com_tabulador(tmp_path)
    assert "src/screens/scrL1BoasVindas.pa.yaml" in projeto.carregar(raiz)


def test_deriva_distingue_tabulador_de_espaco(tmp_path):
    raiz, f, linha = _projeto_com_tabulador(tmp_path)
    # Exportação igual a src/ em tudo, para o deriva só poder reagir à diferença testada
    for s in projeto.ficheiros_src(raiz):
        shutil.copy2(s, raiz / "msapp" / "Src" / s.name)
    assert cli.main(["--raiz", str(raiz), "deriva", "--falhar"]) == 0
    exp = raiz / "msapp" / "Src" / f.name
    linhas = f.read_text(encoding="utf-8").split("\n")
    linhas[linha - 1] = linhas[linha - 1].replace("\t", " ")
    exp.write_text("\n".join(linhas), encoding="utf-8")          # exportação com espaço, src com tabulador
    assert cli.main(["--raiz", str(raiz), "deriva", "--falhar"]) == 1


def test_pt_avisa_quando_mostra_espaco_no_lugar_do_tabulador(tmp_path, capsys):
    raiz, _, linha = _projeto_com_tabulador(tmp_path)
    assert cli.main(["--raiz", str(raiz), "pt", "scrL1BoasVindas"]) == 0
    assert f"tabulador nas linhas {linha}" in capsys.readouterr().err


def test_colar_le_app_com_tabulador(tmp_path, capsys):
    raiz = _copia(tmp_path)
    app = raiz / "src" / "app" / "App.pa.yaml"
    t = app.read_text(encoding="utf-8")
    i = t.index('nfVersao = "') + len('nfVersao = "')
    app.write_text(t[:i] + "\t" + t[i:], encoding="utf-8")
    assert cli.main(["--raiz", str(raiz), "colar", "--destino", str(tmp_path / "out")]) == 0
    assert "AVISO App.pa.yaml" in capsys.readouterr().out


def test_migracao_m009_idempotente_e_tres_modos(tmp_path):
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    from tools.migracoes import m009_v1_7_ficha04_tres_modos as m
    from tools.migracoes import m010_v1_8_ficha04_visual as m10
    from tools.migracoes import m011_v1_9_caixas_na_app as m11
    from tools.migracoes import m012_v1_9_1_verificador as m12
    antes = {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    # a m009 gera os três modos (e o scrL4Entrar), a m010 e a m011 dão-lhes o aspeto e a m012 acerta o que o
    # Verificador apontou: a cadeia é que tem de ser idempotente
    m.main(raiz)
    m10.main(raiz)
    m11.main(raiz)
    m12.main(raiz)
    assert antes == {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    ecras = raiz / "src" / "screens"
    # o Melhoramento e a Revisão são modos do scrL4Pedidos, não ecrãs
    assert not (ecras / "scrL4Melhoramento.pa.yaml").exists() and not (ecras / "scrL4Revisao.pa.yaml").exists()
    inicio = (ecras / "scrInicio.pa.yaml").read_text(encoding="utf-8")
    # o modo vai numa global, posta antes do Navigate: existe mesmo que o scrL4Pedidos ainda não esteja na app
    assert 'Set(gblL4Nivel, "pedidos"); Navigate(scrL4Pedidos' in inicio
    assert 'Set(gblL4Nivel, "melhoramento"); Navigate(scrL4Pedidos' in inicio
    ent = (ecras / "scrL4Entrar.pa.yaml").read_text(encoding="utf-8")
    assert 'Set(gblL4Nivel, "revisao");' in ent and "Navigate(scrL4Pedidos, ScreenTransition.Cover)" in ent
    # a password vai só para o fluxo: nunca para uma variável
    assert "Set(gblL4dSessao, {token: r.token" in ent
    assert not any("Set(" in linha and "txtL4dPassword" in linha for linha in ent.splitlines())
    ped = (ecras / "scrL4Pedidos.pa.yaml").read_text(encoding="utf-8")
    for velho in ("scrL4Revisao", "scrL4Melhoramento", "locL4dPedido", "locL4dMsg", "locL4dTimer", "locL4dVista", "locL4Nivel"):
        assert velho not in ped, velho
    ctl = {c.nome: c for c in yamlio.controlos(yamlio.ler(ecras / "scrL4Pedidos.pa.yaml"))}
    itens = str(ctl["galL4Pedidos"].prop("Items"))
    # vistas escolhidas por fora: cada uma com dois Filter delegáveis, nenhum If dentro de um Filter
    assert itens.count("Filter(Pedidos") == 14 and "Filter(Pedidos, If(" not in itens
    # no modo da Ficha 04 a linha continua a abrir o formulário, como no Lab 4
    assert m.SELECIONAR_LAB4 in str(ctl["galL4Pedidos"].prop("OnSelect"))
    for nome in ("conL4cDetalhe", "conL4cSeparadores", "conL4cTestes", "tmrL4cEstado", "btnL4dSair",
                 "conL4dVistaUtilizadores", "conL4dVistaPassword", "btnL4dAprovar", "btnL4dProporAprovar"):
        assert nome in ctl, nome


def test_migracao_m010_caixas_na_ficha04(tmp_path):
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    from tools.migracoes import m010_v1_8_ficha04_visual as m
    antes = {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    m.main(raiz)
    assert antes == {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    d = yamlio.ler(raiz / "src" / "screens" / "scrL4Pedidos.pa.yaml")
    ctl = {c.nome: c for c in yamlio.controlos(d)}
    # detalhe em três caixas, cada uma com a altura calculada pelos filhos
    from tools.migracoes.m009_v1_7_ficha04_tres_modos import _procurar
    conteudo = next(iter(_procurar(d["Screens"]["scrL4Pedidos"]["Children"], "conL4cDetConteudo").values()))
    assert [next(iter(x)) for x in conteudo["Children"]] == ["conL4cSecDados", "conL4cSecProc", "conL4cSecRev"]
    for sec in ("conL4cSecDados", "conL4cSecProc", "conL4cSecRev"):
        assert str(ctl[sec].prop("Fill")) == "=nfSuperficie" and ".Height" in str(ctl[sec].prop("Height"))
    # o cabeçalho antigo do detalhe sai: a pílula do tratamento vai para a banda do painel
    for velho in ("conL4cDetCab", "lblL4cDetCliente", "conL4cDetLinha", "conL4cDetLinhaRev", "recL4PedSeparador"):
        assert velho not in ctl, velho
    topo = next(iter(_procurar(d["Screens"]["scrL4Pedidos"]["Children"], "conL4PainelTopo").values()))
    assert [next(iter(x)) for x in topo["Children"]][-2:] == ["conL4PainelTit", "btnL4cTratamento"]
    # pedidos em cartões: o cartão e a barra ficam por baixo das etiquetas e passam o toque à linha
    linha = next(iter(_procurar(d["Screens"]["scrL4Pedidos"]["Children"], "galL4Pedidos").values()))["Children"]
    assert [next(iter(x)) for x in linha][:2] == ["recL4PedCartao", "recL4PedBarra"]
    for nome in ("recL4PedCartao", "recL4PedBarra", "recL4CliMarca", "btnL4CliIniciais"):
        assert str(ctl[nome].prop("OnSelect")) == "=Select(Parent)", nome
    # painéis com a sombra por omissão: sem DropShadow escrito
    assert ctl["conL4Painel"].prop("DropShadow") is None and ctl["conL4Lista"].prop("DropShadow") is None


def test_migracao_m011_caixas_na_app(tmp_path):
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    from tools.migracoes import m011_v1_9_caixas_na_app as m
    antes = {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    m.main(raiz)
    assert antes == {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    ctl = {}
    for f in projeto.ficheiros_src(raiz):
        ctl.update({c.nome: c for c in yamlio.controlos(yamlio.ler(f))})
    # cartões com contorno e a sombra por omissão
    for ecra, nomes in m.CARTOES.items():
        for nome in nomes:
            assert str(ctl[nome].prop("BorderColor")) == "=nfLinha" and ctl[nome].prop("DropShadow") is None, nome
    # listas em cartões: o fundo passa o toque à linha e as linhas de separação saem
    for nome in ("recL2ItemCartao", "recL2ItemBarra", "recL3ItemCartao", "recL3PubCartao"):
        assert str(ctl[nome].prop("OnSelect")) == "=Select(Parent)", nome
    for velho in ("recL2Separador", "recL3Separador", "recL3PubSeparador"):
        assert velho not in ctl, velho
    # bandas e calha
    assert str(ctl["conL2PainelTopo"].prop("Fill")) == "=nfAzulClaro" and str(ctl["conL3bTopo"].prop("Fill")) == "=nfAzulClaro"
    assert str(ctl["conL3Separadores"].prop("Fill")) == "=nfSuperficie"


def test_migracao_m012_verificador(tmp_path):
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    from tools.migracoes import m012_v1_9_1_verificador as m
    antes = {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    m.main(raiz)
    assert antes == {f: f.read_text(encoding="utf-8") for f in projeto.ficheiros_src(raiz)}
    ctl = {}
    for f in projeto.ficheiros_src(raiz):
        ctl.update({c.nome: c for c in yamlio.controlos(yamlio.ler(f))})
    for (ecra, nome), props in m.PROPRIEDADES.items():
        assert ctl[nome].ecra == ecra
        for k, v in props.items():
            assert str(ctl[nome].prop(k)) == v, (nome, k)


def test_verificador_reproduz_a_exportacao():
    from tools.dac import verificador
    previstos = verificador.prever(projeto.MSAPP / "Src")
    reais = verificador.ler_sarif(projeto.MSAPP / "AppCheckerResult.sarif")
    assert sorted(previstos) == sorted(reais)


def test_verificador_so_avisa_decorativos_e_veus():
    # o que fica no Verificador é de propósito: decorativos com TabIndex -1, as pílulas com exceção DAC302 e os véus
    from tools.dac import verificador
    rotulos = sorted(n for r, _, n in verificador.prever(projeto.SRC / "screens") if r == verificador.ROTULO)
    assert rotulos == ["recL2Veu", "recL4Veu"]
