"""Previsão dos avisos de Acessibilidade do Verificador de aplicações do Studio, a partir dos ficheiros .pa.yaml.

O Verificador não corre fora do Studio, mas a exportação leva o último resultado (msapp/AppCheckerResult.sarif).
As duas regras de Acessibilidade que a app tem foram deduzidas dessa exportação e reproduzem-na controlo a controlo
(há um teste que o exige):

- acc-TabIndexShouldBeDefinedForInteractiveControl («Tabulação em falta»): etiqueta, ícone, retângulo ou botão com
  TabIndex -1. Etiquetas, ícones e retângulos com algum OnSelect (dentro de galerias, Select(Parent)) não contam.
  Os botões contam sempre. Ausente, o TabIndex vale -1, exceto nos botões, onde vale 0.
- acc-AccessibleLabelNeeded: retângulo sem AccessibleLabel e sem OnSelect.

Os contentores, as entradas e as galerias não entram nestas regras. A categoria Desempenho não vem na exportação:
a regra app-use-delayoutput-text-input está no lint (DAC409).
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from tools.dac import yamlio

TABULACAO = "acc-TabIndexShouldBeDefinedForInteractiveControl"
ROTULO = "acc-AccessibleLabelNeeded"


def _fx(v) -> str:
    return str(v).lstrip("= ").strip() if v is not None else ""


def prever(pasta: Path) -> list[tuple[str, str, str]]:
    """(regra, ecrã, controlo) para cada aviso previsto nos scr*.pa.yaml da pasta."""
    avisos = []
    for f in sorted(Path(pasta).glob("scr*.pa.yaml")):
        doc, _ = yamlio.ler_tolerante(f)
        for c in yamlio.controlos(doc):
            p = c.corpo.get("Properties") or {}
            omissao = "0" if c.tipo == "Button" else "-1"
            tab = _fx(p.get("TabIndex")) or omissao
            tem_onselect = bool(_fx(p.get("OnSelect")))
            if c.tipo in ("Label", "Icon", "Rectangle", "Button") and tab == "-1" and (c.tipo == "Button" or not tem_onselect):
                avisos.append((TABULACAO, c.ecra, c.nome))
            if c.tipo == "Rectangle" and not _fx(p.get("AccessibleLabel")).strip('"') and not tem_onselect:
                avisos.append((ROTULO, c.ecra, c.nome))
    return avisos


def ler_sarif(caminho: Path) -> list[tuple[str, str, str]]:
    """(regra, ecrã, controlo) dos avisos de Acessibilidade guardados numa exportação."""
    d = json.loads(Path(caminho).read_text(encoding="utf-8-sig"))
    avisos = []
    for run in d.get("runs", []):
        for r in run.get("results", []):
            if not r["ruleId"].startswith("acc-"):
                continue
            tipo = r["locations"][0]["properties"]["type"].split(".")
            avisos.append((r["ruleId"], tipo[0], tipo[-1]))
    return avisos


def resumo(avisos: list[tuple[str, str, str]]) -> str:
    por_regra = Counter(a[0] for a in avisos)
    por_ecra = Counter(a[1] for a in avisos)
    linhas = [f"Acessibilidade: {len(avisos)} aviso(s)"]
    linhas += [f"  {n:4d}  {r}" for r, n in por_regra.most_common()]
    linhas.append("Por ecrã:")
    linhas += [f"  {n:4d}  {e}" for e, n in sorted(por_ecra.items())]
    return "\n".join(linhas)
