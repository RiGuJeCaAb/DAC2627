"""Legenda de todos os elementos da app: ecrãs, controlos, variáveis, fórmulas com nome, funções e fontes de dados.

Gerada a partir de src/ por `python -m tools.dac legenda` (docs/legenda.md). Serve de anexo ao Manual ABC: para cada
elemento diz o que é, onde está e em que secção do Manual é construído. As descrições saem das próprias fórmulas
(texto de uma etiqueta, ação de um botão, origem de uma galeria), por isso acompanham o código sem trabalho à mão.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

from tools.dac import pafx, projeto, yamlio

# ficha (pelo código no nome) -> secção do Manual ABC
FICHA = {"scrInicio": "Início", "scrL1BoasVindas": "Ficha 01", "scrL1Pedido": "Ficha 01", "scrL1Saudacao": "Ficha 01",
         "scrL2Servicos": "Ficha 02", "scrL3Lista": "Ficha 03", "scrL3Detalhe": "Ficha 03", "scrL3Publicacao": "Ficha 03",
         "scrL4Pedidos": "Ficha 04 (três modos)", "scrL4Complemento": "Ficha 04 · Complemento",
         "scrL4Entrar": "Ficha 04 · Revisão (entrada)"}
TIPO = {"GroupContainer": "Contentor", "Label": "Etiqueta", "Button": "Botão", "TextInput": "Caixa de texto",
        "Icon": "Ícone", "Rectangle": "Retângulo", "Gallery": "Galeria", "DropDown": "Lista pendente",
        "ComboBox": "Caixa de combinação", "Form": "Formulário", "Timer": "Temporizador", "CheckBox": "Caixa de verificação",
        "DatePicker": "Seletor de data", "TypedDataCard": "Cartão de dados", "Toggle": "Alternar", "Image": "Imagem"}
# o que faz cada função Power Fx usada na app (frase curta, para o anexo)
FUNCOES = {
    "AddColumns": "acrescenta colunas calculadas a uma tabela", "And": "e lógico", "Back": "volta ao ecrã anterior",
    "Blank": "valor vazio", "Char": "carácter pelo código (Char(10) é a mudança de linha)",
    "Choices": "opções de uma coluna de escolha", "ClearCollect": "esvazia e enche uma coleção",
    "Coalesce": "primeiro valor não vazio", "Collect": "acrescenta registos a uma coleção", "ColorValue": "cor a partir de um código",
    "Concat": "junta os textos de uma tabela", "CountRows": "conta as linhas de uma tabela",
    "DateAdd": "soma tempo a uma data", "Defaults": "registo novo com os valores por omissão", "EditForm": "põe um formulário a editar",
    "Error": "provoca um erro", "Filter": "linhas que cumprem condições", "First": "primeira linha", "FirstN": "primeiras N linhas",
    "GUID": "identificador único a partir de texto", "If": "escolhe pelo primeiro teste verdadeiro", "IfError": "apanha erros e dá alternativa",
    "IsBlank": "testa se está vazio", "IsEmpty": "testa se a tabela não tem linhas", "IsMatch": "testa um texto contra um padrão",
    "Last": "última linha", "Left": "primeiros caracteres", "Len": "número de caracteres", "LookUp": "primeira linha que cumpre a condição",
    "Lower": "texto em minúsculas", "Max": "o maior valor", "Mid": "caracteres a meio", "Min": "o menor valor",
    "Navigate": "muda de ecrã", "NewForm": "põe um formulário a criar", "Not": "negação", "Now": "data e hora atuais", "Or": "ou lógico",
    "Patch": "cria ou altera um registo", "Proper": "maiúscula no início de cada palavra", "Refresh": "volta a ler a fonte de dados",
    "Remove": "apaga um registo", "Reset": "repõe o valor inicial de um controlo", "ResetForm": "repõe um formulário",
    "RGBA": "cor por componentes", "RoundDown": "arredonda para baixo", "Select": "faz como se o controlo fosse tocado",
    "Set": "define uma variável global", "ShowColumns": "fica só com algumas colunas", "Sort": "ordena uma tabela",
    "Split": "parte um texto numa tabela", "StartsWith": "testa o início de um texto", "SubmitForm": "grava um formulário",
    "Substitute": "troca partes de um texto", "Switch": "escolhe pelo valor", "Table": "tabela escrita na fórmula",
    "Text": "valor como texto, com formato", "Today": "data de hoje", "Trim": "tira espaços a mais", "Ungroup": "desfaz agrupamentos",
    "UpdateContext": "define variáveis de contexto do ecrã", "Upper": "texto em maiúsculas", "Value": "texto como número",
    "With": "dá nome a valores dentro de uma fórmula", "DataSourceInfo": "informação sobre a fonte de dados",
    "Distinct": "valores únicos de uma coluna", "Index": "linha pela posição", "Notify": "mostra uma notificação",
    "Search": "procura texto em colunas", "Round": "arredonda", "Sum": "soma", "Abs": "valor absoluto",
}
VAR_RE = re.compile(r"^(loc|gbl|col)[A-Z]\w*$")
FUNC_RE = re.compile(r"\b([A-Z][A-Za-z]+)\s*\(")


SECCAO_ECRA = {"scrInicio": "B", "scrL1BoasVindas": "C2", "scrL1Pedido": "C3", "scrL1Saudacao": "C4", "scrL2Servicos": "D",
               "scrL3Lista": "E5, E6", "scrL3Detalhe": "E7", "scrL3Publicacao": "E7", "scrL4Pedidos": "F2 a F7",
               "scrL4Complemento": "F8", "scrL4Entrar": "F11.5"}


def _seccao(nome: str, ecra: str) -> str:
    """Secção do Manual onde o controlo é construído: a do ecrã, ou F10 e F11 para os acrescentos L4c e L4d."""
    if ecra == "scrL4Pedidos":
        if re.search(r"L4c[A-Z]", nome):
            return "F10"
        if re.search(r"L4d[A-Z]", nome):
            return "F11.5"
    return SECCAO_ECRA.get(ecra, "—")


def _curto(texto: str, n: int = 90) -> str:
    t = " ".join(str(texto).split())
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def _cel(texto: str) -> str:
    return texto.replace("|", "\\|")


def _literal(fx: str) -> str | None:
    m = re.fullmatch(r'\s*"((?:[^"]|"")*)"\s*', fx)
    return m.group(1).replace('""', '"') if m else None


def _acao(fx: str) -> str:
    """Resumo do que um OnSelect faz, pelas funções e destinos que tem."""
    cod = pafx.so_codigo(fx)
    partes = []
    for m in re.finditer(r"Navigate\(\s*(\w+)", cod):
        partes.append(f"abre {m.group(1)}")
    for m in re.finditer(r"(\w+)\.Run\(", cod):
        partes.append(f"chama o fluxo {m.group(1)}")
    for f, frase in (("SubmitForm", "grava o formulário"), ("Patch", "grava no Dataverse"), ("Remove", "apaga um registo"),
                     ("NewForm", "abre o formulário a criar"), ("EditForm", "abre o formulário a editar"),
                     ("Refresh", "volta a ler os dados"), ("ClearCollect", "carrega uma coleção")):
        if re.search(rf"\b{f}\(", cod):
            partes.append(frase)
    for m in re.finditer(r"Set\(\s*(\w+)", cod):
        partes.append(f"define {m.group(1)}")
    chaves = re.findall(r"UpdateContext\(\s*\{([^}]*)\}", cod)
    nomes = sorted({k.strip().split(":")[0].strip() for bloco in chaves for k in bloco.split(",") if ":" in k})
    if nomes:
        partes.append("muda " + ", ".join(nomes[:4]) + (" …" if len(nomes) > 4 else ""))
    if not partes and "Select(Parent)" in cod:
        return "passa o toque à linha da galeria"
    vistos, uniq = set(), []
    for p in partes:
        if p not in vistos:
            vistos.add(p)
            uniq.append(p)
    return "; ".join(uniq[:5]) if uniq else _curto(fx, 60)


def descrever(c: yamlio.Controlo) -> str:
    p = {k: pafx.para_pt(str(v).lstrip("=")) for k, v in (c.corpo.get("Properties") or {}).items()}
    t = c.tipo
    if t == "Label":
        lit = _literal(p.get("Text", ""))
        return f"Texto fixo «{_curto(lit, 70)}»" if lit is not None else f"Mostra {_curto(p.get('Text', '—'), 80)}"
    if t == "Button":
        lit = _literal(p.get("Text", ""))
        rotulo = f"«{_curto(lit, 40)}»" if lit is not None else _curto(p.get("Text", ""), 50)
        if p.get("DisplayMode") == "DisplayMode.View":
            return f"Pílula decorativa {rotulo}"
        return f"Botão {rotulo}: {_acao(p.get('OnSelect', ''))}" if p.get("OnSelect") else f"Botão {rotulo}"
    if t == "Icon":
        icone = p.get("Icon", "").replace("Icon.", "")
        rot = _literal(p.get("AccessibleLabel", "")) or ""
        acao = _acao(p["OnSelect"]) if p.get("OnSelect") else "decorativo"
        return f"Ícone {icone}{' («' + rot + '»)' if rot else ''}: {acao}"
    if t in ("TextInput",):
        rot = _literal(p.get("AccessibleLabel", "")) or _literal(p.get("HintText", "")) or ""
        modo = " (password)" if "Password" in p.get("Mode", "") else ""
        return f"Entrada de texto{modo}{': ' + rot if rot else ''}"
    if t in ("DropDown", "ComboBox"):
        return f"Escolha de {_curto(p.get('Items', '—'), 70)}"
    if t == "Gallery":
        fontes = [f for f in ("Pedidos", "Clientes", "Utilizadores", "'Cloud Service'", "colL3Utilizadores", "colL3Publicacoes",
                              "Table(") if f in p.get("Items", "")]
        return "Galeria de " + (", ".join(fontes).replace("Table(", "uma tabela escrita na fórmula") if fontes else _curto(p.get("Items", "—"), 60))
    if t == "GroupContainer":
        dirc = "horizontal" if "Horizontal" in p.get("LayoutDirection", "") else "vertical"
        extras = []
        if p.get("BorderThickness") and p.get("BorderThickness") != "0":
            extras.append("caixa com contorno")
        if "Scroll" in p.get("LayoutOverflowY", ""):
            extras.append("desloca")
        if not c.corpo.get("Children") and p.get("Height") in ("1", "2"):
            return "Linha de separação (contentor vazio)"
        if c.pai is None:
            extras.append("raiz do ecrã")
        return f"Contentor {dirc}" + (f", {', '.join(extras)}" if extras else "")
    if t == "Rectangle":
        if p.get("Width") == "4":
            return "Barra de cor à esquerda da linha"
        if p.get("Height") == "1" or "TemplateHeight - 1" in p.get("Y", ""):
            return "Linha de separação"
        if "nfVeu" in p.get("Fill", ""):
            return "Véu por trás do diálogo"
        return "Fundo de cartão" if "BorderColor" in p else "Retângulo"
    if t == "Timer":
        return f"Temporizador de {p.get('Duration', '?')} ms: {_acao(p.get('OnTimerEnd', ''))}"
    if t == "Form":
        return f"Formulário de {p.get('DataSource', '—')}"
    if t == "TypedDataCard":
        rot = _literal(p.get("DisplayName", "")) or ""
        return f"Cartão do formulário{': ' + rot if rot else ''}"
    if t == "CheckBox":
        return f"Caixa de verificação «{_literal(p.get('Text', '')) or ''}»"
    return TIPO.get(t, t)


def gerar(raiz: Path = projeto.RAIZ) -> str:
    docs = projeto.carregar(raiz)
    ordem = projeto.ordem_ecras(raiz)
    controlos: dict[str, list] = defaultdict(list)
    app_formulas = ""
    escritas: dict[str, set] = defaultdict(set)
    leituras: dict[str, set] = defaultdict(set)
    funcoes: dict[str, set] = defaultdict(set)
    usos_nf: Counter = Counter()
    for d in docs.values():
        if "App" in d:
            app_formulas = str((d["App"].get("Properties") or {}).get("Formulas") or "")
        for c in yamlio.controlos(d):
            controlos[c.ecra].append(c)
        for ecra, corpo in (d.get("Screens") or {}).items():
            pares = [(ecra, k, str(v)) for k, v in (corpo.get("Properties") or {}).items()]
            pares += [(c.nome, k, str(v)) for c in yamlio.controlos({"Screens": {ecra: corpo}})
                      for k, v in (c.corpo.get("Properties") or {}).items()]
            for onde, prop, fx in pares:
                cod = pafx.so_codigo(fx.lstrip("="))
                for f in FUNC_RE.findall(cod):
                    if f in FUNCOES:
                        funcoes[f].add(ecra)
                for i in pafx.identificadores(fx.lstrip("=")):
                    if VAR_RE.match(i):
                        leituras[i].add(f"{ecra}")
                    if i.startswith("nf"):
                        usos_nf[i] += 1
                for m in re.finditer(r"\bSet\(\s*(\w+)", cod):
                    escritas[m.group(1)].add(f"{onde}.{prop}")
                for m in re.finditer(r"\b(?:ClearCollect|Collect)\(\s*(\w+)", cod):
                    escritas[m.group(1)].add(f"{onde}.{prop}")
                for bloco in re.findall(r"UpdateContext\(\s*\{(.*?)\}\s*\)", cod, re.S):
                    for k in re.findall(r"(?:^|,)\s*(loc\w+)\s*:", bloco):
                        escritas[k].add(f"{onde}.{prop}")
                for m in re.finditer(r"Navigate\([^,()]+,[^,()]+,\s*\{([^}]*)\}", cod):
                    for k in re.findall(r"(loc\w+)\s*:", m.group(1)):
                        escritas[k].add(f"{onde}.{prop} (Navigate)")
    total = sum(len(v) for v in controlos.values())
    L = ["# Anexo · Legenda dos elementos da APP DAC2627", "",
         "Gerado por `python -m tools.dac legenda` a partir de `src/`. Não editar à mão: mudar o código e voltar a gerar.", "",
         f"A app tem {len(ordem)} ecrãs e {total} controlos. Para cada elemento, a legenda diz o que é, onde está e em que "
         "secção do Manual ABC é construído. Os nomes seguem a convenção da A2: o prefixo diz o tipo (`lbl`, `btn`, `con`…), "
         "o código diz a ficha (`In`, `L1` a `L4`, com `L4b` para o Complemento, `L4c` para o Melhoramento e `L4d` para "
         "a Revisão) e o resto diz a função. As descrições saem das próprias fórmulas: o texto de uma etiqueta, o que um botão "
         "faz, a origem de uma galeria.", "",
         "## Ecrãs", "", "| Ecrã | Ficha | Controlos | Secção do Manual |", "|---|---|---:|---|"]
    for e in ordem:
        L.append(f"| `{e}` | {FICHA.get(e, '—')} | {len(controlos.get(e, []))} | {_seccao(e, e)} |")
    for e in ordem:
        L += ["", f"## {e}", "", "| Controlo | Tipo | Dentro de | O que é | Manual |", "|---|---|---|---|---|"]
        for c in controlos.get(e, []):
            pai = f"`{c.pai.nome}`" if c.pai else "ecrã"
            L.append(f"| `{c.nome}` | {TIPO.get(c.tipo, c.tipo)} | {pai} | {_cel(descrever(c))} | {_seccao(c.nome, e)} |")
    L += ["", "## Variáveis", "",
          "As globais (`gbl`) definem-se com `Set` e valem em toda a app. As de contexto (`loc`) definem-se com "
          "`UpdateContext` ou com o terceiro argumento do `Navigate` e valem num só ecrã. As coleções (`col`) enchem-se com "
          "`ClearCollect`.", "", "| Variável | Tipo | Definida em | Aparece nos ecrãs |", "|---|---|---|---|"]
    for v in sorted(set(escritas) | {x for x in leituras if VAR_RE.match(x)}):
        if not VAR_RE.match(v):
            continue
        tipo = {"gbl": "global", "loc": "de contexto", "col": "coleção"}[v[:3]]
        defs = sorted(escritas.get(v, []))
        onde = ", ".join(f"`{x}`" for x in defs[:4]) + (f" e mais {len(defs) - 4}" if len(defs) > 4 else "")
        L.append(f"| `{v}` | {tipo} | {onde or '—'} | {', '.join(sorted(leituras.get(v, []))) or '—'} |")
    L += ["", "## Fórmulas com nome (App.Formulas)", "",
          "Cores, versão e textos comuns. As cores só se usam por estes nomes (lint DAC201); os contrastes estão em "
          "`docs/paleta.md`.", "", "| Nome | Valor | Usos |", "|---|---|---:|"]
    for nome, valor in re.findall(r"(nf\w+)\s*=\s*(.*?);(?=\s*(?:nf\w+\s*=|$))", app_formulas, re.S):
        L.append(f"| `{nome}` | `{_cel(_curto(valor, 60))}` | {usos_nf.get(nome, 0)} |")
    L += ["", "## Funções Power Fx usadas", "", "| Função | O que faz | Ecrãs onde aparece |", "|---|---|---|"]
    for f in sorted(funcoes):
        L.append(f"| `{f}` | {FUNCOES[f]} | {', '.join(sorted(funcoes[f]))} |")
    cfg = projeto.config(raiz)
    L += ["", "## Fontes de dados e fluxos", "", "| Nome | Tipo | Nota |", "|---|---|---|"]
    for f in cfg.get("fontes", []):
        L.append(f"| {f['nome']} | {f['tipo']} | {_cel(f.get('nota', ''))} |")
    return "\n".join(L) + "\n"
