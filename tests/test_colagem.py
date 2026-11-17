"""Verificações antes de colar: fontes de dados e dependências entre ecrãs."""
import json
import shutil

from tools.dac import cli, colagem, projeto


def _copia(tmp_path):
    raiz = tmp_path / "p"
    shutil.copytree(projeto.RAIZ / "src", raiz / "src")
    shutil.copytree(projeto.RAIZ / "msapp" / "References", raiz / "msapp" / "References")
    shutil.copy2(projeto.RAIZ / "dac.yaml", raiz / "dac.yaml")
    return raiz


def _datasources(raiz):
    return raiz / "msapp" / "References" / "DataSources.json"


def test_projeto_sem_problemas_de_fontes():
    assert colagem.verificar_fontes() == []


def test_fontes_usadas_ignoram_texto_entre_aspas():
    usadas = colagem.fontes_usadas()
    # "Clientes e Pedidos" aparece como texto no scrInicio, mas o ecrã não usa as tabelas
    assert usadas["Clientes"] == ["scrL4Pedidos"]
    assert usadas["Cloud Service"] == ["scrL2Servicos"]


def test_falta_uma_fonte_na_app(tmp_path):
    raiz = _copia(tmp_path)
    d = json.loads(_datasources(raiz).read_text(encoding="utf-8"))
    d["DataSources"] = [x for x in d["DataSources"] if x["Name"] != "Pedidos"]
    _datasources(raiz).write_text(json.dumps(d), encoding="utf-8")
    problemas = colagem.verificar_fontes(raiz)
    assert len(problemas) == 1 and "'Pedidos'" in problemas[0] and "não está na app" in problemas[0]
    assert cli.main(["--raiz", str(raiz), "colar", "--estrito", "--destino", str(tmp_path / "b")]) == 1


def test_tabela_duplicada_com_o_mesmo_nome(tmp_path):
    raiz = _copia(tmp_path)
    d = json.loads(_datasources(raiz).read_text(encoding="utf-8"))
    for x in d["DataSources"]:
        if x["Name"] == "Cloud Service":
            x["EntitySetName"] = "mcsft_cloudservice1s"
    _datasources(raiz).write_text(json.dumps(d), encoding="utf-8")
    problemas = colagem.verificar_fontes(raiz)
    assert len(problemas) == 1 and "mcsft_cloudservice1s" in problemas[0]


def test_navegacoes_com_variaveis_da_ficha03():
    navs = {(n.origem, n.destino): n.variaveis for n in colagem.navegacoes()}
    assert navs[("scrL3Lista", "scrL3Detalhe")] == ("locL3Sel",)
    assert navs[("scrL3Detalhe", "scrL3Publicacao")] == ("locL3Pub",)


def test_leia_me_pela_ordem(tmp_path):
    texto = colagem.leia_me()
    posicoes = [texto.index(p) for p in ("1. Fontes", "2. App.Formulas", "3. Ecrãs antigos",
                                          "4. Ecrãs novos", "6. Guardar e Publicar", "7. Prova")]
    assert posicoes == sorted(posicoes)
    assert "PUBLICADA" in texto and "dac deriva" in texto
