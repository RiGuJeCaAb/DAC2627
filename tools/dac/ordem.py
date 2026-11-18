"""Guia de colagem: em que ordem colar os ecrãs e o que tem de estar na app antes.

Porque é que a ordem conta
--------------------------
Uma variável de contexto que chega a um ecrã pelo Navigate,

    Navigate(scrL3Publicacao, ScreenTransition.Cover, {locL3Pub: ...})   // em scrL3Lista

só existe para o Studio se o ecrã que a envia já estiver na app quando o ecrã que a recebe
é colado. Se o scrL3Publicacao entrar primeiro, locL3Pub fica marcada como nome inválido, e o
Studio não volta a verificar quando o scrL3Lista chega depois (aconteceu a 10/11/2026: 24 erros).

Basta UM dos ecrãs que enviam a variável estar colado antes. É isso que resolve ciclos como
scrL3Detalhe ⇄ scrL3Publicacao: o scrL3Lista envia as duas variáveis e entra primeiro.

Fontes de dados
---------------
Os .yaml dos ecrãs usam os nomes das fontes ('Cloud Service', Clientes, JSONPlaceholderDAC...)
mas não as trazem: a ligação vive na app. Apagar ecrãs pode deixar a app sem elas.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from dataclasses import dataclass, field

from . import pafx, yamlio


@dataclass
class Fonte:
    nome: str
    tipo: str = ""
    nota: str = ""
    conjunto: str = ""     # conjunto de entidades no Dataverse (vazio nos conectores)


@dataclass
class Guia:
    ordem: list[str]
    recebe: dict[str, dict[str, set[str]]]          # ecrã -> {variável: {ecrãs que a enviam}}
    fontes: dict[str, list[str]]                     # nome da fonte -> ecrãs que a usam
    avisos: list[str] = field(default_factory=list)


_NAV = re.compile(r"\bNavigate\(\s*(\w+)\s*,")


def _registo_apos(cod: str, i: int) -> list[str]:
    """Chaves de topo do 3.º argumento do Navigate que começa em cod[i] ('(' de Navigate)."""
    nivel, args, atual = 0, [], []
    for j in range(i, len(cod)):
        ch = cod[j]
        if ch in "([{":
            nivel += 1
            if nivel == 1:
                continue
        elif ch in ")]}":
            nivel -= 1
            if nivel == 0:
                args.append("".join(atual))
                break
        if nivel == 1 and ch == ",":
            args.append("".join(atual))
            atual = []
            continue
        atual.append(ch)
    if len(args) < 3:
        return []
    reg = args[2].strip()
    if not reg.startswith("{"):
        return []
    # chaves de topo: identificador seguido de ':' ao nível 1 do registo
    chaves, nivel = [], 0
    for m in re.finditer(r"[{}()\[\]]|(\w+)\s*:", reg):
        t = m.group(0)
        if t in "{([":
            nivel += 1
        elif t in "})]":
            nivel -= 1
        elif nivel == 1 and m.group(1):
            chaves.append(m.group(1))
    return chaves


def variaveis_recebidas(docs: dict[str, dict]) -> dict[str, dict[str, set[str]]]:
    recebe: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for d in docs.values():
        for ecra, corpo in (d.get("Screens") or {}).items():
            fxs = [str(v) for v in (corpo.get("Properties") or {}).values()]
            fxs += [str(v) for c in yamlio.controlos({"Screens": {ecra: corpo}})
                    for v in (c.corpo.get("Properties") or {}).values()]
            for fx in fxs:
                try:
                    cod = pafx.so_codigo(fx.lstrip("="))
                except pafx.ErroLexico:
                    continue
                for m in _NAV.finditer(cod):
                    alvo = m.group(1)
                    for var in _registo_apos(cod, m.end() - len(m.group(0)) + len("Navigate")):
                        if alvo != ecra:
                            recebe[alvo][var].add(ecra)
    return {k: dict(v) for k, v in recebe.items()}


def fontes_usadas(docs: dict[str, dict], fontes: list[Fonte]) -> dict[str, list[str]]:
    usos: dict[str, list[str]] = {f.nome: [] for f in fontes}
    for d in docs.values():
        for ecra, corpo in (d.get("Screens") or {}).items():
            fxs = [str(v) for c in yamlio.controlos({"Screens": {ecra: corpo}})
                   for v in (c.corpo.get("Properties") or {}).values()]
            fxs += [str(v) for v in (corpo.get("Properties") or {}).values()]
            cod = "\n".join(pafx.so_codigo(f.lstrip("=")) for f in fxs)
            for f in fontes:
                padrao = (re.escape(f"'{f.nome}'") if " " in f.nome
                          else r"(?<![\w.'])" + re.escape(f.nome) + r"(?![\w'])")
                if re.search(padrao, cod) and ecra not in usos[f.nome]:
                    usos[f.nome].append(ecra)
    return usos


def fontes_na_exportacao(raiz: Path) -> dict[str, str] | None:
    """Fontes da última exportação: nome -> conjunto de entidades ('' nos conectores). None sem exportação."""
    ds = raiz / "msapp" / "References" / "DataSources.json"
    if not ds.exists():
        return None
    out: dict[str, str] = {}
    for x in json.loads(ds.read_text(encoding="utf-8")).get("DataSources", []):
        if x.get("Type") == "NativeCDSDataSourceInfo":
            out[x["Name"]] = x.get("EntitySetName", "")
        elif x.get("Type") == "ServiceInfo":
            out[x["Name"]] = ""
    return out


def verificar_fontes(guia: "Guia", fontes: list[Fonte], raiz: Path) -> list[str]:
    """O que o lint não vê: uma fonte usada no código que falta na app, ou que aponta para outra tabela.

    Compara com a última exportação. A 10/11/2026 o lint estava a zero e o Studio mostrou 205 erros,
    101 deles por faltar a tabela Cloud Service.
    """
    na_app = fontes_na_exportacao(raiz)
    if na_app is None:
        return ["Não há exportação em msapp/: corra 'dac sincronizar' antes de colar."]
    problemas = []
    for f in fontes:
        usos = guia.fontes.get(f.nome, [])
        if not usos:
            continue
        if f.nome not in na_app:
            problemas.append(f"'{f.nome}' é usada em {', '.join(usos)} mas não está na app exportada. "
                             f"Adicione-a em Dados antes de colar.")
        elif f.conjunto and na_app[f.nome] != f.conjunto:
            problemas.append(f"'{f.nome}' aponta para '{na_app[f.nome]}' e devia apontar para '{f.conjunto}'. "
                             f"Há tabelas com o mesmo nome a apresentar: confirme a tabela em Dados.")
    return problemas


def calcular(docs: dict[str, dict], preferida: list[str], fontes: list[Fonte]) -> Guia:
    """Ordem de colagem: a ordem preferida (dac.yaml), adiada só o necessário.

    Um ecrã pode entrar quando, para cada variável que recebe, pelo menos um ecrã que a envia
    já entrou. Se nenhum ecrã puder entrar (ciclo sem saída), entra o primeiro da ordem
    preferida e fica um aviso: será preciso colá-lo outra vez no fim.
    """
    recebe = variaveis_recebidas(docs)
    todos = {e for d in docs.values() for e in (d.get("Screens") or {})}
    fora = todos - set(preferida)          # ecrãs que não vão ser colados: já estão na app
    falta = [e for e in preferida]
    ordem: list[str] = []
    avisos: list[str] = []
    while falta:
        pronto = next((e for e in falta
                       if all(envia & (set(ordem) | fora) for envia in recebe.get(e, {}).values())), None)
        if pronto is None:
            pronto = falta[0]
            vars_ = ", ".join(sorted(v for v, envia in recebe[pronto].items() if not envia & (set(ordem) | fora)))
            avisos.append(f"{pronto} entra antes de quem lhe envia {vars_}: cole-o outra vez no fim.")
        ordem.append(pronto)
        falta.remove(pronto)
    return Guia(ordem, recebe, fontes_usadas(docs, fontes), avisos)


def gerar_md(guia: Guia, fontes: list[Fonte], versao: str, pilulas: int, fora: set[str] | None = None) -> str:
    fora = fora or set()
    L = [f"# Colar a v{versao} no Studio", "",
         "Gerado por `python -m tools.dac colar`. Siga os passos por esta ordem e marque cada um.", "",
         "## 0 · Antes de começar", "",
         "- [ ] Exportar a solução tal como está (**Soluções › DAC2627 › Exportar › Não gerida**), como cópia de segurança.",
         "", "## 1 · Fontes de dados", "",
         "No painel **Dados** (ícone do cilindro), confirme que estão todas. Se faltar alguma, **Adicionar dados**.", "",
         "| Fonte | Tipo | Usada em | Atenção |", "|---|---|---|---|"]
    for f in fontes:
        usos = guia.fontes.get(f.nome, [])
        if not usos:
            continue
        L.append(f"| **{f.nome}** | {f.tipo} | {', '.join(f'`{u}`' for u in usos)} | {f.nota} |")
    L += ["", "- [ ] Todas as fontes da tabela estão no painel Dados, com estes nomes exatos.", "",
          "## 2 · App.Formulas", "",
          "- [ ] Na Vista de árvore, clicar em **App** (sem colar aí).",
          "- [ ] Na barra de fórmulas, escolher **Formulas**, clicar **dentro da caixa de texto**, Ctrl+A e colar o conteúdo de `App.Formulas.pt.txt`.",
          "", "Colado na Vista de árvore, o texto dá o erro `PA1001 ... YamlInvalidSyntax`: não estraga nada, mas não fica gravado.",
          "", "## 3 · Ecrãs, por esta ordem", "",
          "Para cada ecrã: **eliminar** o antigo (não renomear: renomear muda as fórmulas dos outros ecrãs para o nome novo),",
          "abrir o `.yaml` no Bloco de Notas, Ctrl+A, Ctrl+C, clicar na Vista de árvore e Ctrl+V. Confirmar que o nome não ganhou `_1`.", "",
          "| # | Ficheiro | Porquê nesta posição |", "|---|---|---|"]
    colados: list[str] = []
    for i, e in enumerate(guia.ordem, 1):
        motivos = []
        for var, envia in sorted(guia.recebe.get(e, {}).items()):
            antes = sorted(envia & (set(colados) | fora))
            if antes:
                motivos.append(f"recebe `{var}` de {', '.join(f'`{x}`' for x in antes)}, "
                               + ("já colado" if len(antes) == 1 else "já colados"))
        usa = [f for f, us in guia.fontes.items() if e in us]
        if usa:
            motivos.append("precisa de " + ", ".join(f"**{f}**" for f in usa))
        L.append(f"| {i} | `{e}.yaml` | {'; '.join(motivos) or '—'} |")
        colados.append(e)
    for a in guia.avisos:
        L += ["", f"> Aviso: {a}"]
    L += ["", "- [ ] Os ecrãs foram colados todos, pela ordem da tabela, sem `_1` nos nomes.", "",
          "Entre eliminar e colar, os outros ecrãs podem mostrar erros de ligação (`Navigate` para um ecrã que ainda não existe). "
          "Desaparecem quando esse ecrã entra. Erros de **variável** (`loc...` não é válido) não desaparecem sozinhos: "
          "elimine e cole outra vez esse ecrã.", "",
          "## 4 · Confirmar", "",
          "- [ ] Painel de erros de fórmulas: **0 erros**.",
          "- [ ] **Verificador de aplicações**: sem erros. Os avisos de acessibilidade que ficam são todos de controlos "
          f"decorativos com `TabIndex = -1` ou `AccessibleLabel` vazio, incluindo as {pilulas} pílulas (ver `docs/alm.md`). "
          "Avisos de foco, rótulo ou tabulação num controlo **interativo** são para corrigir.",
          f"- [ ] **F5**: rodapé do ecrã inicial mostra `v{versao}`; testes da secção G2 do manual.",
          "", "## 5 · Guardar e fechar o ciclo", "",
          "- [ ] **Guardar** e **Publicar**. A exportação da solução leva a versão **publicada**: só guardado, a "
          "exportação sai igual à anterior (aconteceu com a 1.0.0.2, a 16/11/2026), e os alunos continuam a abrir a versão antiga.",
          "- [ ] Exportar a solução (não gerida) e, no repositório:", "",
          "```", "python -m tools.dac sincronizar <caminho do zip>", "python -m tools.dac deriva", "```", "",
          "- [ ] `deriva` responde `src/ igual à última exportação`, e o `git diff src/` só mostra valores por omissão "
          "que o Studio apagou (`TabIndex -1`, `AccessibleLabel \"\"`, `DropShadow.Light`...).", ""]
    return "\n".join(L)
