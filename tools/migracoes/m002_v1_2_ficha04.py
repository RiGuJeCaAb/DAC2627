"""Migração 002 · v1.2.0 · Ficha 04 coerente com as regras da casa e o complemento no ecrã inicial.

Corre sobre src/ depois da m001 e é idempotente: correr de novo não muda nada.

    python -m tools.migracoes.m002_v1_2_ficha04

O que faz:
  1. App.Formulas: nfVersao passa a "1.2.0".
  2. scrInicio: quinto cartão, «Ficha 04 · Complemento», e o OnSelect com os ramos 4 e 5.
  3. scrL4Pedidos, DAC104: os campos DataCardValueN passam a ter nomes da casa (txt, dte, cmb + L4 + campo).
  4. scrL4Pedidos, DAC301: AccessibleLabel nos campos dos formulários e no ícone da faixa.
  5. scrL4Pedidos, DAC201: as duas cores literais do selo do estado passam aos tokens nfAmbar e nfAmbarFundo.
  6. scrL4Pedidos, DAC501: tamanhos de letra fora da escala (10 e 17) passam a 11 e 18.
  7. scrL4Pedidos: a vista Todos da galeria passa a mostrar só pedidos ativos, como a contagem do separador.
  8. scrL4Pedidos: cartões dos formulários com largura por fórmula, para ficarem um por linha no telemóvel.
  9. scrL2Servicos: o mesmo nos cartões do frmL2Servico, mas pela largura do formulário, que no
     tablet ocupa só metade do ecrã: abaixo de 560 px um cartão por linha, acima disso dois.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.dac import projeto, yamlio
from tools.migracoes.m001_v1_1_qualidade import FORMULAS as FORMULAS_V11, _renomear

VERSAO = "1.2.0"
FORMULAS = FORMULAS_V11.replace('nfVersao = "1.1.0";', f'nfVersao = "{VERSAO}";')

ITENS_INICIO = '''=Table(
    {Num: 1, Ficha: "Ficha 01", Titulo: "Hello Cloud",
     Descricao: "Primeira Canvas app: três ecrãs, navegação e variável global.", Disponivel: true},
    {Num: 2, Ficha: "Ficha 02", Titulo: "Serviços Cloud",
     Descricao: "Inventário de serviços cloud em Dataverse, com criar, editar e remover num só ecrã.", Disponivel: true},
    {Num: 3, Ficha: "Ficha 03", Titulo: "Consulta de API",
     Descricao: "Utilizadores e publicações de uma API REST, com filtro por utilizador e tratamento de erros.", Disponivel: true},
    {Num: 4, Ficha: "Ficha 04", Titulo: "Clientes e Pedidos",
     Descricao: "Duas tabelas Dataverse com relação 1:N, pedidos por cliente e as vistas Pendentes e Concluídos.", Disponivel: true},
    {Num: 5, Ficha: "Ficha 04 · Complemento", Titulo: "SharePoint, Dataverse e SQL",
     Descricao: "Ponto 8 do Lab 4: as três origens de dados comparadas para os clientes e pedidos.", Disponivel: true}
)'''

ONSELECT_INICIO = '''=If(
    galInFichas.Selected.Disponivel,
    Switch(
        galInFichas.Selected.Num,
        1, Navigate(scrL1BoasVindas, ScreenTransition.Cover),
        2, Navigate(scrL2Servicos, ScreenTransition.Cover),
        3, Navigate(scrL3Lista, ScreenTransition.Cover),
        4, Navigate(scrL4Pedidos, ScreenTransition.Cover),
        5, Navigate(scrL4Complemento, ScreenTransition.Cover)
    )
)'''

NOMES = {
    "DataCardValue1": "txtL4CliNome",
    "DataCardValue4": "txtL4CliNIF",
    "DataCardValue2": "txtL4CliEmail",
    "DataCardValue3": "txtL4CliTelefone",
    "DataCardValue16": "cmbL4PedCliente",
    "DataCardValue10": "dteL4PedData",
    "DataCardValue12": "cmbL4PedEstado",
    "DataCardValue14": "txtL4PedValor",
    "DataCardValue11": "txtL4PedDescricao",
}

ROTULOS = {nome: "=Parent.DisplayName" for nome in NOMES.values()}
ROTULOS["icoL4MsgIcone"] = '=If(locL4MsgTipo = "erro", "Erro", "Sucesso")'

TODOS_ANTES = ("If(IsBlank(locL4Cliente), Sort(Pedidos, DataPedido, SortOrder.Descending), "
               "Sort(Filter(Pedidos, Clientes.Cliente = locL4Cliente.Cliente), DataPedido, SortOrder.Descending))")
TODOS_DEPOIS = ("If(IsBlank(locL4Cliente), Sort(Filter(Pedidos, Estado = 'Estado (Pedidos)'.Ativo), DataPedido, SortOrder.Descending), "
                "Sort(Filter(Pedidos, Estado = 'Estado (Pedidos)'.Ativo && Clientes.Cliente = locL4Cliente.Cliente), DataPedido, SortOrder.Descending))")

LARGURA_CLIENTE = ("=Switch(scrL4Pedidos.Size, ScreenSize.Small, Parent.Width - 1, "
                   "ScreenSize.Medium, RoundDown(Parent.Width / 2, 0) - 1, RoundDown(Parent.Width / 3, 0) - 1)")
LARGURA_PEDIDO = "=If(scrL4Pedidos.Size = ScreenSize.Small, Parent.Width - 1, RoundDown(Parent.Width / 2, 0) - 1)"
CARTOES_CLIENTE = {"Nome_DataCard1", "NIF_DataCard1", "Email_DataCard1", "Telefone_DataCard1"}
LARGURA_SERVICO = "=If(Parent.Width < 560, Parent.Width - 1, RoundDown(Parent.Width / 2, 0) - 1)"
CARTOES_SERVICO = {"Service Title_DataCard1", "Status_DataCard1", "Provider_DataCard1", "Service Model_DataCard1"}
CARTOES_PEDIDO = {"Cliente_DataCard1", "DataPedido_DataCard1", "Estado (dac_estado)_DataCard1", "Valor_DataCard1"}


def migrar_documento(doc: dict) -> None:
    if "App" in doc:
        p = doc["App"]["Properties"]
        # Uma migração posterior (m004, ...) pode já ter subido nfVersao: mantém-se a mais recente.
        atual = re.search(r'nfVersao = "([0-9.]+)"', str(p.get("Formulas") or ""))
        versao = atual.group(1) if atual and tuple(map(int, atual.group(1).split("."))) > tuple(map(int, VERSAO.split("."))) else VERSAO
        novo = "=" + FORMULAS.replace(f'nfVersao = "{VERSAO}";', f'nfVersao = "{versao}";')
        if str(p.get("Formulas") or "").rstrip() != novo.rstrip():  # linha em branco final do Studio: igual
            p["Formulas"] = novo
        return
    ecras = doc.get("Screens") or {}
    if "scrInicio" in ecras:
        for c in yamlio.controlos(doc):
            if c.nome == "galInFichas":
                # só acrescenta o quinto cartão; os textos dele podem ter mudado depois (m004)
                if "Num: 5" not in str(c.prop("Items")):
                    c.definir("Items", ITENS_INICIO)
                c.definir("OnSelect", ONSELECT_INICIO)
        return
    if "scrL2Servicos" in ecras:
        for c in yamlio.controlos(doc):
            if c.nome in CARTOES_SERVICO:
                c.definir("Width", LARGURA_SERVICO)
            if c.nome == "Service Description_DataCard1":
                c.definir("Width", "=Parent.Width - 1")
        return
    if "scrL4Pedidos" not in ecras:
        return
    for antigo, novo in NOMES.items():
        _renomear(doc, antigo, novo)
    for c in list(yamlio.controlos(doc)):
        if c.nome in ROTULOS:
            c.definir("AccessibleLabel", ROTULOS[c.nome])
        if c.nome == "btnL4PedEstado":
            for prop in ("Color", "Fill"):
                v = c.prop(prop) or ""
                v = v.replace('ColorValue("#9A5B00")', "nfAmbar")
                v = v.replace('ColorValue("#FFF4D8")', "nfAmbarFundo").replace('ColorValue("#FFF4DB")', "nfAmbarFundo")
                c.definir(prop, v)
        if c.nome in ("btnL4SepTodos", "btnL4SepPendentes", "btnL4SepConcluidos"):
            c.definir("Size", (c.prop("Size") or "").replace("ScreenSize.Small, 10,", "ScreenSize.Small, 11,"))
        if c.nome == "lblL4PainelTitulo":
            c.definir("Size", (c.prop("Size") or "").replace("ScreenSize.Small, 17,", "ScreenSize.Small, 18,"))
        if c.nome == "galL4Pedidos":
            c.definir("Items", (c.prop("Items") or "").replace(TODOS_ANTES, TODOS_DEPOIS))
        if c.nome in CARTOES_CLIENTE:
            c.definir("Width", LARGURA_CLIENTE)
        if c.nome in CARTOES_PEDIDO:
            c.definir("Width", LARGURA_PEDIDO)
        if c.nome == "Descricao_DataCard1":
            c.definir("Width", "=Parent.Width - 1")


def main(raiz: Path = projeto.RAIZ) -> int:
    mudados = 0
    for f in projeto.ficheiros_src(raiz):
        antes = f.read_text(encoding="utf-8")
        d = yamlio.ler(f)
        migrar_documento(d)
        depois = yamlio.escrever_texto(d)
        if depois != antes:
            f.write_text(depois, encoding="utf-8")
            mudados += 1
            print("migrado:", f.relative_to(raiz))
    print(f"m002: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
