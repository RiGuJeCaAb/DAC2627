"""Guia de colagem (tools/dac/ordem.py): ordem dos ecrãs e fontes de dados."""
import shutil

from tools.dac import cli, ordem, projeto, yamlio
from tools.dac.ordem import Fonte


def _ecra(nome, onselect="", items=""):
    props = {}
    if onselect:
        props["OnSelect"] = "=" + onselect
    if items:
        props["Items"] = "=" + items
    return {"Screens": {nome: {"Properties": {}, "Children": [
        {f"btn{nome}": {"Control": "Classic/Button@2.2.0", "Properties": props}}]}}}


def _docs(*ecras):
    return {f"f{i}": e for i, e in enumerate(ecras)}


def test_variavel_so_por_registo_do_navigate():
    docs = _docs(_ecra("scrA", 'Navigate(scrB, ScreenTransition.Cover, {locX: 1, locY: {a: 2}})'),
                 _ecra("scrB", "Navigate(scrA, ScreenTransition.None)"))
    assert ordem.variaveis_recebidas(docs) == {"scrB": {"locX": {"scrA"}, "locY": {"scrA"}}}


def test_quem_recebe_espera_por_quem_envia():
    docs = _docs(_ecra("scrPub"), _ecra("scrLista", 'Navigate(scrPub, ScreenTransition.Cover, {locPub: 1})'))
    g = ordem.calcular(docs, ["scrPub", "scrLista"], [])
    assert g.ordem == ["scrLista", "scrPub"] and not g.avisos


def test_ciclo_resolvido_por_um_terceiro_ecra():
    # o caso real da Ficha 03: Detalhe <-> Publicação, ambos alimentados pela Lista
    docs = _docs(
        _ecra("scrDet", 'Navigate(scrPub, ScreenTransition.Cover, {locPub: 1})'),
        _ecra("scrPub", 'Navigate(scrDet, ScreenTransition.Cover, {locSel: 1})'),
        _ecra("scrLista", 'Navigate(scrDet, ScreenTransition.Cover, {locSel: 1}); '
                          'Navigate(scrPub, ScreenTransition.Cover, {locPub: 1})'))
    g = ordem.calcular(docs, ["scrDet", "scrPub", "scrLista"], [])
    assert g.ordem[0] == "scrLista" and not g.avisos


def test_ciclo_sem_saida_gera_aviso():
    docs = _docs(_ecra("scrA", 'Navigate(scrB, ScreenTransition.Cover, {locB: 1})'),
                 _ecra("scrB", 'Navigate(scrA, ScreenTransition.Cover, {locA: 1})'))
    g = ordem.calcular(docs, ["scrA", "scrB"], [])
    assert g.ordem == ["scrA", "scrB"] and len(g.avisos) == 1 and "scrA" in g.avisos[0]


def test_ecras_nao_colados_contam_como_presentes():
    docs = _docs(_ecra("scrPub"), _ecra("scrLista", 'Navigate(scrPub, ScreenTransition.Cover, {locPub: 1})'))
    g = ordem.calcular(docs, ["scrPub"], [])
    assert g.ordem == ["scrPub"] and not g.avisos


def test_fontes_usadas():
    docs = _docs(_ecra("scrA", items="Filter('Cloud Service', true)"),
                 _ecra("scrB", items='ClearCollect(colX, Conector.Listar()); "Cloud Service em texto"'))
    usos = ordem.fontes_usadas(docs, [Fonte("Cloud Service"), Fonte("Conector"), Fonte("Nada")])
    assert usos == {"Cloud Service": ["scrA"], "Conector": ["scrB"], "Nada": []}


def test_ordem_do_projeto_respeita_as_variaveis():
    cfg = projeto.config()
    g = ordem.calcular(projeto.carregar(), projeto.ordem_ecras(), [Fonte(**f) for f in cfg["fontes"]])
    assert not g.avisos
    for ecra, vars_ in g.recebe.items():
        for var, envia in vars_.items():
            assert any(g.ordem.index(x) < g.ordem.index(ecra) for x in envia), (ecra, var)


def test_fontes_do_dac_yaml_cobrem_o_que_o_codigo_usa():
    cfg = projeto.config()
    nomes = {f["nome"] for f in cfg["fontes"]}
    assert set(cfg["lint"]["fontes_dataverse"]) <= nomes
    usos = ordem.fontes_usadas(projeto.carregar(), [Fonte(n) for n in nomes])
    assert all(usos[n] for n in nomes), f"fontes declaradas mas não usadas: {[n for n in nomes if not usos[n]]}"


def test_colar_escreve_ordem_md(tmp_path):
    assert cli.main(["colar", "--destino", str(tmp_path)]) == 0
    md = (tmp_path / "ORDEM.md").read_text(encoding="utf-8")
    assert "App.Formulas.pt.txt" in md and "Cloud Service" in md and "mcsft_cloudservice" in md
    # ecrãs iguais à exportação não entram na tabela de colagem, mas a ordem dos ficheiros mantém-se
    assert md.index("`scrL3Lista`") < md.index("`scrL3Detalhe`") < md.index("`scrL3Publicacao`")
    todos = list(yamlio.ler(tmp_path / "TODOS_OS_ECRAS.yaml")["Screens"])
    assert todos.index("scrL3Lista") < todos.index("scrL3Publicacao")


# ---- fontes contra a última exportação (msapp/References/DataSources.json)

def _copia(tmp_path):
    import shutil
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    shutil.copytree(projeto.RAIZ / "msapp" / "References", raiz / "msapp" / "References")
    shutil.copy2(projeto.RAIZ / "dac.yaml", raiz / "dac.yaml")
    return raiz


def _guia(raiz):
    fontes = [Fonte(**f) for f in projeto.config(raiz).get("fontes", [])]
    return ordem.calcular(projeto.carregar(raiz), projeto.ordem_ecras(raiz), fontes), fontes


def _mexer_datasources(raiz, f):
    import json
    ds = raiz / "msapp" / "References" / "DataSources.json"
    d = json.loads(ds.read_text(encoding="utf-8"))
    f(d)
    ds.write_text(json.dumps(d), encoding="utf-8")


def test_fontes_do_projeto_estao_na_exportacao():
    g, fontes = _guia(projeto.RAIZ)
    assert ordem.verificar_fontes(g, fontes, projeto.RAIZ) == []


def test_falta_uma_fonte_na_app(tmp_path):
    raiz = _copia(tmp_path)
    _mexer_datasources(raiz, lambda d: d.update(DataSources=[x for x in d["DataSources"] if x["Name"] != "Pedidos"]))
    g, fontes = _guia(raiz)
    problemas = ordem.verificar_fontes(g, fontes, raiz)
    assert len(problemas) == 1 and "'Pedidos'" in problemas[0] and "não está na app" in problemas[0]
    assert cli.main(["--raiz", str(raiz), "colar", "--estrito", "--destino", str(tmp_path / "b")]) == 1


def test_tabela_duplicada_com_o_mesmo_nome(tmp_path):
    raiz = _copia(tmp_path)

    def trocar(d):
        for x in d["DataSources"]:
            if x["Name"] == "Cloud Service":
                x["EntitySetName"] = "mcsft_cloudservice1s"
    _mexer_datasources(raiz, trocar)
    g, fontes = _guia(raiz)
    problemas = ordem.verificar_fontes(g, fontes, raiz)
    assert len(problemas) == 1 and "mcsft_cloudservice1s" in problemas[0]


def test_ordem_md_fluxos_no_painel_power_automate(tmp_path):
    """Os fluxos não aparecem no painel Dados (20/11/2026): têm passo próprio, no painel Power Automate."""
    assert cli.main(["colar", "--destino", str(tmp_path)]) == 0
    md = (tmp_path / "ORDEM.md").read_text(encoding="utf-8")
    dados = md[md.index("## 1 · Tabelas e conectores"):md.index("## 2 · Fluxos")]
    fluxos = md[md.index("## 2 · Fluxos"):md.index("## 3 · App.Formulas")]
    for f in projeto.config()["fontes"]:
        if f["tipo"].startswith("Fluxo"):
            assert f["nome"] in fluxos and f["nome"] not in dados, f["nome"]
        else:
            assert f["nome"] in dados and f["nome"] not in fluxos, f["nome"]


def test_ordem_md_so_cola_o_que_mudou(tmp_path):
    raiz = _copia(tmp_path)
    shutil.copytree(projeto.RAIZ / "msapp" / "Src", raiz / "msapp" / "Src")
    assert cli.main(["--raiz", str(raiz), "colar", "--destino", str(tmp_path / "c")]) == 0
    md = (tmp_path / "c" / "ORDEM.md").read_text(encoding="utf-8")
    tabela = md[md.index("## 4 · Ecrãs"):md.index("Não se colam")]
    assert "scrL2Servicos.yaml" not in tabela          # igual à exportação
    assert "`scrL4Entrar.yaml` | novo, só colar" in tabela
    # os ecrãs que saíram da app (dac.yaml › retirados) eliminam-se antes de colar
    assert "`scrL4Melhoramento`, `scrL4Revisao`" in md[md.index("## 4 · Ecrãs"):]


def test_colunas_em_falta_pedem_atualizar():
    f = Fonte("Pedidos", "Tabela Dataverse", colunas=["dac_valor", "dac_inexistente"])
    assert ordem.colunas_em_falta(f, {"Pedidos": '{"dac_valor": 1}'}) == ["dac_inexistente"]
    assert ordem.colunas_em_falta(f, {}) == []
