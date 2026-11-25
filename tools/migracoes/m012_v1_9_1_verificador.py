"""Migração 012 · v1.9.1 · avisos do Verificador de aplicações que a v1.9.0 trouxe e que têm correção.

Corre sobre src/ depois da m011 e é idempotente: correr de novo não muda nada.

    python -m tools.migracoes.m012_v1_9_1_verificador

Depois de colar a v1.9.0 (25/11/2026), o Verificador mostrou 275 avisos de Acessibilidade e 3 de Desempenho.
O `dac verificador` reproduz os 275 a partir do repositório: 270 de tabulação e 5 de AccessibleLabel, quase todos
de etiquetas, ícones e pílulas decorativas que ficam de propósito (docs/alm.md). Esta migração trata dos que não
são de propósito:
  1. Desempenho (regra app-use-delayoutput-text-input, lint DAC409): as três caixas de pesquisa que filtram uma
     galeria e uma contagem passam a DelayOutput = true. A consulta corre meio segundo depois da última tecla, em
     vez de a cada tecla.
  2. Acessibilidade (lint DAC502): as três linhas de separação que ainda estão dentro de galerias passam o toque à
     linha com OnSelect = Select(Parent), como os retângulos de fundo da m010 e da m011. Cada uma contava duas
     vezes (tabulação e AccessibleLabel): saem seis avisos.
  3. App.Formulas: nfVersao passa a "1.9.1".
Ficam os dois véus dos diálogos de confirmação (recL2Veu, recL4Veu): estão fora de galerias e não fazem nada ao
toque, só tapam o ecrã. Um AccessibleLabel faria o leitor de ecrã anunciá-los.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.dac import projeto, yamlio

VERSAO = "1.9.1"

PROPRIEDADES = {
    ("scrL2Servicos", "txtL2Pesquisa"): {"DelayOutput": "=true"},
    ("scrL3Lista", "txtL3Pesquisa"): {"DelayOutput": "=true"},
    ("scrL4Pedidos", "txtL4Pesquisa"): {"DelayOutput": "=true"},
    ("scrL3Detalhe", "recL3PubsUtilSep"): {"OnSelect": "=Select(Parent)"},
    ("scrL4Pedidos", "recL4CliSeparador"): {"OnSelect": "=Select(Parent)"},
    ("scrL4Conta", "recL4dGUtilSeparador"): {"OnSelect": "=Select(Parent)"},
}


def migrar_app(doc: dict) -> None:
    p = doc["App"]["Properties"]
    atual = re.search(r'nfVersao = "([0-9.]+)"', str(p.get("Formulas") or ""))
    if not atual or tuple(map(int, atual.group(1).split("."))) < tuple(map(int, VERSAO.split("."))):
        p["Formulas"] = re.sub(r'nfVersao = "[0-9.]+";', f'nfVersao = "{VERSAO}";', str(p["Formulas"]))


def migrar_documento(doc: dict) -> None:
    if "App" in doc:
        migrar_app(doc)
        return
    for c in yamlio.controlos(doc):
        props = PROPRIEDADES.get((c.ecra, c.nome))
        if not props:
            continue
        p = c.corpo.setdefault("Properties", {})
        p.update(props)
        c.corpo["Properties"] = {k: p[k] for k in sorted(p)}


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
    print(f"m012: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
