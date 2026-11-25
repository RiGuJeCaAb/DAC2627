"""Migração 013 · v1.10.0 · as áreas Utilizadores e A minha password saem do scrL4Pedidos para um ecrã próprio.

Corre sobre src/ depois da m012 e é idempotente: correr de novo não muda nada.

    python -m tools.migracoes.m013_v1_10_ecra_conta

Depois de colar a v1.9.0 (25/11/2026), o Verificador marcou o scrL4Pedidos em Desempenho: «Demasiados controlos
num ecrã», com complexidade estimada 302 para um máximo recomendado de 300 (219 controlos no repositório). O
utilizador escolheu tirar do ecrã a gestão da conta da Revisão, que não tem a ver com a lista nem com o detalhe
dos pedidos:
  1. scrL4Conta (ecrã novo): o cabeçalho com Início e os ícones Utilizadores (só Admin) e A minha password, o topo
     da área com o título e «‹ Pedidos», as duas vistas da m008 e a faixa de mensagem com o temporizador. A área
     vem na global gblL4dArea ("utilizadores" ou "password"), posta com Set antes do Navigate, como o gblL4Nivel
     (m009): uma variável de contexto enviada pelo Navigate ficava sem ecrã se o scrL4Conta ainda não existisse.
  2. scrL4Pedidos: saem conL4dAreaTopo, conL4dVistaUtilizadores e conL4dVistaPassword (38 controlos) e a variável
     locL4Area. Os ícones do cabeçalho passam a abrir o scrL4Conta.
  3. App.Formulas: nfVersao passa a "1.10.0".
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.dac import projeto, yamlio
from tools.migracoes import m008_v1_6_ficha04_revisao as B
from tools.migracoes.m007_v1_5_ficha04_melhoramento import _botao, _contentor, _ctl, _etiqueta, _s

VERSAO = "1.10.0"
PED = "scrL4Pedidos"
CONTA = "scrL4Conta"
AREA = "gblL4dArea"
NIV = "gblL4Nivel"
R = f'{NIV} = "revisao"'
ADMIN = f'{B.PERF} = "Admin"'
PEQ = f"{CONTA}.Size = ScreenSize.Small"
RETIRAR = ("conL4dAreaTopo", "conL4dVistaUtilizadores", "conL4dVistaPassword")

# As vistas da m008 foram escritas para o scrL4Revisao, com as vistas em locL4dVista.
MAPA = (
    ("scrL4Revisao.Size", f"{CONTA}.Size"),
    ('locL4dVista = "utilizadores"', f'{AREA} = "utilizadores"'),
    ('locL4dVista = "password"', f'{AREA} = "password"'),
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


def abrir(area: str) -> str:
    return f'Set({AREA}, "{area}"); Navigate({CONTA}, ScreenTransition.Cover)'


def _icone(nome: str, icon: str, rotulo: str, acao: str, visivel: str) -> dict:
    return _ctl(nome, "Classic/Icon@2.5.0", {
        "AccessibleLabel": "=" + _s(rotulo), "Color": "=Color.White", "Height": "=44", "Icon": "=" + icon,
        "OnSelect": "=" + acao, "PaddingBottom": "=10", "PaddingLeft": "=10", "PaddingRight": "=10", "PaddingTop": "=10",
        "TabIndex": "=0", "Visible": "=" + visivel, "Width": "=44"})


LIMPAR = 'UpdateContext({locL4dUtil: Blank(), locL4dMsg: "", locL4dTimer: false})'


def ecra_conta() -> dict:
    icones = [
        _icone("icoL4dCUtilizadores", "Icon.People", "Gerir os utilizadores", f'Set({AREA}, "utilizadores"); {LIMPAR}', ADMIN),
        _icone("icoL4dCPassword", "Icon.Lock", "Mudar a minha password", f'Set({AREA}, "password"); {LIMPAR}', "true"),
    ]
    topo = _contentor("conL4dAreaTopo", [
        _etiqueta("lblL4dAreaTitulo", f'If({AREA} = "utilizadores", "Utilizadores", "A minha password")',
                  AlignInContainer="=AlignInContainer.Center", AutoHeight="=false", FillPortions="=1", FontWeight="=FontWeight.Bold",
                  Height="=44", Size=f"=If({PEQ}, 18, 22)", Wrap="=false"),
        _botao("btnL4dAreaVoltar", _s("‹ Pedidos"), f"Navigate({PED}, ScreenTransition.UnCover)", primario=False,
               BorderThickness="=1", Width="=130"),
    ], vertical=False, FillPortions="=0", Height="=44", LayoutGap="=12")
    utilizadores = _remap(B._vista_utilizadores())
    next(iter(utilizadores.values()))["Properties"]["Visible"] = f'={R} && {AREA} = "utilizadores" && {ADMIN}'
    password = _remap(B._vista_password())
    next(iter(password.values()))["Properties"]["Visible"] = f'={R} && {AREA} = "password"'
    # a linha de cada utilizador passa o toque à galeria (DAC502, m012)
    for c in yamlio.controlos({"Screens": {CONTA: {"Children": [utilizadores]}}}):
        if c.nome == "recL4dGUtilSeparador":
            c.definir("OnSelect", "=Select(Parent)")
    conteudo = B._conteudo("L4dC", CONTA, [topo, utilizadores, password], 1100)
    raiz = _contentor("conEcraL4dC", [B._cabecalho("L4dC", "Ficha 04 · Revisão", icones), conteudo], Fill="=nfFundo",
                      Height="=Parent.Height", Width="=Parent.Width")
    # Sem Navigate no OnVisible (DAC406). Só se chega aqui pelo scrL4Pedidos na Revisão, com sessão; os fluxos que
    # alteram dados leem o perfil da sessão no Dataverse.
    on_visible = ('=UpdateContext({locL4dUtil: Blank(), locL4dMsg: "", locL4dMsgTipo: "", locL4dTimer: false});\n'
                  "Reset(txtL4dPassAtual); Reset(txtL4dPassNova); Reset(txtL4dPassConfirma)")
    return {"Screens": {CONTA: {"Properties": {"Fill": "=nfFundo", "OnVisible": on_visible},
                                "Children": [raiz, *B._mensagem("L4dC")]}}}


def _tirar(lista: list, nomes: tuple) -> None:
    lista[:] = [x for x in lista if next(iter(x)) not in nomes]
    for x in lista:
        filhos = next(iter(x.values())).get("Children")
        if filhos:
            _tirar(filhos, nomes)


def migrar_pedidos(doc: dict) -> None:
    ecra = doc["Screens"][PED]
    _tirar(ecra["Children"], RETIRAR)
    p = ecra["Properties"]
    p["OnVisible"] = str(p["OnVisible"]).replace('locL4Area: "", ', "").replace(", locL4dUtil: Blank()", "")
    for c in yamlio.controlos(doc):
        if c.nome == "icoL4dUtilizadores":
            c.definir("OnSelect", "=" + abrir("utilizadores"))
        elif c.nome == "icoL4dPassword":
            c.definir("OnSelect", "=" + abrir("password"))
        elif c.nome == "conConteudoL4":
            c.definir("LayoutOverflowY", "=LayoutOverflow.Hide")
        elif c.nome == "conL4Corpo":
            c.definir("Visible", "=true")
        elif c.nome == "conL4Barra":
            c.definir("Visible", str(c.prop("Visible")).replace(" && IsBlank(locL4Area)", ""))


def migrar_app(doc: dict) -> None:
    p = doc["App"]["Properties"]
    atual = re.search(r'nfVersao = "([0-9.]+)"', str(p.get("Formulas") or ""))
    if not atual or tuple(map(int, atual.group(1).split("."))) < tuple(map(int, VERSAO.split("."))):
        p["Formulas"] = re.sub(r'nfVersao = "[0-9.]+";', f'nfVersao = "{VERSAO}";', str(p["Formulas"]))


def migrar_documento(doc: dict) -> None:
    if "App" in doc:
        migrar_app(doc)
    elif PED in (doc.get("Screens") or {}):
        migrar_pedidos(doc)


def main(raiz: Path = projeto.RAIZ) -> int:
    mudados = 0
    for f in projeto.ficheiros_src(raiz):
        if f.name == f"{CONTA}.pa.yaml":
            continue
        antes = f.read_text(encoding="utf-8")
        d = yamlio.ler(f)
        migrar_documento(d)
        depois = yamlio.escrever_texto(d)
        if depois != antes:
            f.write_text(depois, encoding="utf-8")
            mudados += 1
            print("migrado:", f.relative_to(raiz))
    conta = raiz / "src" / "screens" / f"{CONTA}.pa.yaml"
    texto = yamlio.escrever_texto(ecra_conta())
    if not conta.exists() or conta.read_text(encoding="utf-8") != texto:
        conta.write_text(texto, encoding="utf-8")
        mudados += 1
        print("escrito:", conta.relative_to(raiz))
    print(f"m013: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
