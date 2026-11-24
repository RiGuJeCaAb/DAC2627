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
    colunas: list[str] = field(default_factory=list)  # colunas (nomes lógicos) que a tabela tem de ter na app

    @property
    def fluxo(self) -> bool:
        return self.tipo.lower().startswith("fluxo")


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
        elif x.get("Name") and x.get("Type") not in ("OptionSetInfo", "ViewInfo", "StaticDataSourceInfo"):
            out.setdefault(x["Name"], "")   # conectores (ServiceInfo) e fluxos, qualquer que seja o tipo
    return out


def definicoes_na_exportacao(raiz: Path) -> dict[str, str]:
    """Texto da definição (TableDefinition) de cada tabela Dataverse da última exportação."""
    ds = raiz / "msapp" / "References" / "DataSources.json"
    if not ds.exists():
        return {}
    return {x["Name"]: str(x.get("TableDefinition", ""))
            for x in json.loads(ds.read_text(encoding="utf-8")).get("DataSources", [])
            if x.get("Type") == "NativeCDSDataSourceInfo"}


def colunas_em_falta(f: Fonte, definicoes: dict[str, str]) -> list[str]:
    """Colunas que a app usa e que a definição da tabela na app ainda não tem: pedem Atualizar no painel Dados."""
    texto = definicoes.get(f.nome)
    if texto is None:
        return []
    return [c for c in f.colunas if f'"{c}"' not in texto and c not in texto]


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
            onde = "no painel Power Automate (Adicionar fluxo)" if f.fluxo else "no painel Dados (Adicionar dados)"
            problemas.append(f"'{f.nome}' é usada em {', '.join(usos)} mas não está na app exportada. "
                             f"Adicione-a {onde} antes de colar.")
        elif f.conjunto and na_app[f.nome] != f.conjunto:
            problemas.append(f"'{f.nome}' aponta para '{na_app[f.nome]}' e devia apontar para '{f.conjunto}'. "
                             f"Há tabelas com o mesmo nome a apresentar: confirme a tabela em Dados.")
        elif faltam := colunas_em_falta(f, definicoes_na_exportacao(raiz)):
            problemas.append(f"'{f.nome}' está na app sem as colunas {', '.join(faltam)}: "
                             f"no painel Dados, «…» ao lado de {f.nome} › Atualizar.")
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


def _passo_fontes(guia: Guia, fontes: list[Fonte], na_app: dict[str, str] | None,
                  definicoes: dict[str, str]) -> list[str]:
    """Passos 1 e 2: o que acrescentar ou atualizar, separado pelo painel onde se faz."""
    usadas = [f for f in fontes if guia.fontes.get(f.nome)]
    sem_exp = na_app is None
    def estado(f: Fonte) -> tuple[str, str]:
        if sem_exp:
            return "?", "Confirmar que está na app; se não estiver, acrescentar."
        if f.nome not in na_app:
            return "**falta**", "Acrescentar."
        if faltam := colunas_em_falta(f, definicoes):
            return "**desatualizada**", f"Atualizar: faltam as colunas {', '.join(f'`{c}`' for c in faltam)}."
        return "já está", "Nada."
    L = ["## 1 · Tabelas e conectores (painel Dados)", "",
         "No Studio, no trilho da esquerda, o ícone do cilindro abre o painel **Dados**. "
         "Para **acrescentar**: **Adicionar dados**, escrever o nome na pesquisa e escolher a tabela "
         "(num conector, escolher a ligação que já existe). Para **atualizar**: no painel Dados, «…» ao lado do nome › **Atualizar**.", "",
         "| Fonte | Na app | O que fazer | Atenção |", "|---|---|---|---|"]
    for f in (x for x in usadas if not x.fluxo):
        e, o = estado(f)
        L.append(f"| **{f.nome}** ({f.tipo}) | {e} | {o} | {f.nota} |")
    L += ["", "- [ ] As linhas com «falta» ou «desatualizada» estão tratadas.", "",
          "## 2 · Fluxos (painel Power Automate)", "",
          "Os fluxos **não aparecem no painel Dados**. No trilho da esquerda do Studio, «…» (Mais) › **Power Automate** "
          "(o ícone parecido com um robô é o dos Agentes, não serve). No painel, **Adicionar fluxo** e escolher o fluxo na lista. "
          "A lista só mostra fluxos ativos com o gatilho Power Apps (V2) neste ambiente. Se um não aparecer, fechar e reabrir o Studio.", "",
          "| Fluxo | Na app | O que fazer |", "|---|---|---|"]
    fluxos = [x for x in usadas if x.fluxo]
    for f in fluxos:
        e, o = estado(f)
        L.append(f"| **{f.nome}** | {e} | {o} |")
    if not fluxos:
        L.append("| — | — | A app não chama fluxos. |")
    L += ["", "- [ ] Os fluxos que faltavam aparecem no painel Power Automate.", ""]
    return L


def gerar_md(guia: Guia, fontes: list[Fonte], versao: str, pilulas: int, fora: set[str] | None = None,
             na_app: dict[str, str] | None = None, definicoes: dict[str, str] | None = None,
             iguais: set[str] | None = None, novos: set[str] | None = None,
             retirados: list[str] | None = None) -> str:
    """ORDEM.md. na_app e definicoes vêm da última exportação; iguais são os ecrãs iguais a essa exportação,
    que não precisam de ser colados (continuam na ordem, porque podem enviar variáveis a outros).
    retirados são ecrãs que saíram da app (dac.yaml › retirados): eliminam-se antes de colar."""
    fora, iguais, novos, definicoes = fora or set(), iguais or set(), novos or set(), definicoes or {}
    L = [f"# Colar a v{versao} no Studio", "",
         "Gerado por `python -m tools.dac colar`. Siga os passos por esta ordem e marque cada um.", "",
         "## 0 · Antes de começar", "",
         "- [ ] Exportar a solução tal como está (**Soluções › DAC2627 › Exportar › Não gerida**), como cópia de segurança.",
         "- [ ] Abrir a app para editar: **Soluções › DAC2627 › Aplicações › DAC2627_RGJCA › Editar**.", ""]
    L += _passo_fontes(guia, fontes, na_app, definicoes)
    L += ["## 3 · App.Formulas", "",
          "- [ ] Na Vista de árvore, clicar em **App** (sem colar aí).",
          "- [ ] Na barra de fórmulas, escolher **Formulas**, clicar **dentro da caixa de texto**, Ctrl+A e colar o conteúdo de `App.Formulas.pt.txt`.",
          "", "Colado na Vista de árvore, o texto dá o erro `PA1001 ... YamlInvalidSyntax`: não estraga nada, mas não fica gravado.",
          "", "## 4 · Ecrãs, por esta ordem", "",
          "Para cada ecrã da tabela: se já existe na app, **eliminar** o antigo (não renomear: renomear muda as fórmulas dos outros ecrãs para o nome novo). "
          "Abrir o `.yaml` no Bloco de Notas, Ctrl+A, Ctrl+C, clicar na Vista de árvore e Ctrl+V. Confirmar que o nome não ganhou `_1`.", "",
          ]
    if retirados:
        L += ["- [ ] Antes de colar, **eliminar** da app, se ainda lá estiverem, os ecrãs que saíram: "
              + ", ".join(f"`{e}`" for e in retirados) + ". O conteúdo deles passou para outros ecrãs desta versão "
              "(ver `CHANGELOG.md`).", ""]
    L += ["| # | Ficheiro | Na app | Porquê nesta posição |", "|---|---|---|---|"]
    colados: list[str] = []
    n = 0
    for e in guia.ordem:
        if e in iguais:
            colados.append(e)
            continue
        motivos = []
        for var, envia in sorted(guia.recebe.get(e, {}).items()):
            antes = sorted(envia & (set(colados) | fora))
            if antes:
                motivos.append(f"recebe `{var}` de {', '.join(f'`{x}`' for x in antes)}, já na app")
        usa = [f for f, us in guia.fontes.items() if e in us]
        if usa:
            motivos.append("precisa de " + ", ".join(f"**{f}**" for f in usa))
        n += 1
        L.append(f"| {n} | `{e}.yaml` | {'novo, só colar' if e in novos else 'eliminar o antigo e colar'} | {'; '.join(motivos) or '—'} |")
        colados.append(e)
    if iguais:
        L += ["", "Não se colam, porque estão iguais à última exportação: " + ", ".join(f"`{e}`" for e in guia.ordem if e in iguais) + "."]
    for a in guia.avisos:
        L += ["", f"> Aviso: {a}"]
    L += ["", "- [ ] Os ecrãs da tabela foram colados, por esta ordem, sem `_1` nos nomes.", "",
          "Entre eliminar e colar, os outros ecrãs podem mostrar erros de ligação (`Navigate` para um ecrã que ainda não existe). "
          "Desaparecem quando esse ecrã entra. Erros de **variável** (`loc...` não é válido) não desaparecem sozinhos: "
          "elimine e cole outra vez esse ecrã.", "",
          "## 5 · Confirmar", "",
          "- [ ] Painel de erros de fórmulas: **0 erros**.",
          "- [ ] **Verificador de aplicações**: sem erros. Os avisos de acessibilidade que ficam são todos de controlos "
          f"decorativos com `TabIndex = -1` ou `AccessibleLabel` vazio, incluindo as {pilulas} pílulas (ver `docs/alm.md`). "
          "Avisos de foco, rótulo ou tabulação num controlo **interativo** são para corrigir.",
          f"- [ ] **F5**: rodapé do ecrã inicial mostra `v{versao}`; testes da secção G2 do manual.",
          "", "## 6 · Guardar e fechar o ciclo", "",
          "- [ ] **Guardar** e **Publicar**. A exportação da solução leva a versão **publicada**: só guardado, a "
          "exportação sai igual à anterior (aconteceu com a 1.0.0.2, a 16/11/2026), e os alunos continuam a abrir a versão antiga.",
          "- [ ] Exportar a solução (não gerida) e, no repositório:", "",
          "```", "python -m tools.dac sincronizar <caminho do zip>", "python -m tools.dac deriva", "```", "",
          "- [ ] `deriva` responde `src/ igual à última exportação`, e o `git diff src/` só mostra valores por omissão "
          "que o Studio apagou (`TabIndex -1`, `AccessibleLabel \"\"`, `DropShadow.Light`...).", ""]
    return "\n".join(L)
