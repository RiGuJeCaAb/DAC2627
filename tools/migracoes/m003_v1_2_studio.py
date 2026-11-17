"""Migração 003 · v1.2.0 · o que a primeira exportação publicada (1.0.0.3, 17/11/2026) mostrou.

Corre sobre src/ depois da m002 e é idempotente: correr de novo não muda nada.

    python -m tools.migracoes.m003_v1_2_studio

O que faz:
  1. DAC303: FocusedBorderThickness = 2 nas etiquetas dos cartões dos formulários (DataCardKey,
     StarVisible, ErrorMessage) e no lblL4PedCliente. São os 43 avisos «foco invisível» do Verificador.
  2. DAC503: conEcraL2 passa a DropShadow.None. Era o único contentor de ecrã sem ele, por isso tinha a
     sombra por omissão (Light) e os cartões conL2Lista e conL2Painel ficavam com sombra dentro de sombra.
  3. scrInicio: lblInFicha com a largura do cartão. Sem Width, ficava com a largura por omissão e
     «Ficha 04 · Complemento» partia em duas linhas, cortada a meio.

Não toca nos valores por omissão que o Studio apagou ao guardar (TabIndex -1, AccessibleLabel "",
DropShadow.Light, ...): yamlio já os trata como ausentes e o lint lê-os assim (DAC504).
"""
from __future__ import annotations

import sys
from pathlib import Path

from tools.dac import projeto, yamlio

LARGURA_FICHA = "=Parent.TemplateWidth - 48"


def _num(v: str | None) -> float | None:
    try:
        return float(str(v).lstrip("="))
    except (TypeError, ValueError):
        return None


def migrar_documento(doc: dict) -> None:
    if "App" in doc:
        return
    for c in yamlio.controlos(doc):
        if c.tipo == "Label" and not c.dentro_de_galeria:
            fb = _num(c.prop("FocusedBorderThickness"))
            if fb is None or fb <= 0:
                c.definir("FocusedBorderThickness", "=2")
        if c.nome == "conEcraL2":
            c.definir("DropShadow", "=DropShadow.None")
        if c.nome == "lblInFicha":
            c.definir("Width", LARGURA_FICHA)


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
    print(f"m003: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
