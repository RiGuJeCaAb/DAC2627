"""Leitura e escrita de ficheiros .pa.yaml no mesmo estilo do Power Apps Studio.

O objetivo é que ler e voltar a escrever um ficheiro exportado pelo Studio
produza exatamente os mesmos bytes. Assim, qualquer alteração feita por uma
ferramenta aparece no git como um diff mínimo, linha a linha.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

import yaml

_ESTRELAS = "# " + "*" * 96
CABECALHO = "\n".join([
    _ESTRELAS,
    "# Warning: YAML source code for Canvas Apps should only be used to review changes made within Power Apps Studio and for minor edits (Preview).",
    "# Use the maker portal to create and edit your Power Apps.",
    "# ",  # o espaço final faz parte do cabeçalho do Studio
    "# The schema file for Canvas Apps is available at https://go.microsoft.com/fwlink/?linkid=2304907",
    "# ",
    "# For more information, visit https://go.microsoft.com/fwlink/?linkid=2292623",
    _ESTRELAS,
]) + "\n"


def ler(caminho: str | Path) -> dict:
    with open(caminho, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _precisa_bloco(v: str) -> bool:
    return "\n" in v or ": " in v or " #" in v or v.endswith(":")


def _escalar(chave: str, v: Any, ind: int) -> list[str]:
    s = " " * ind
    if isinstance(v, bool):
        return [f"{s}{chave}: {'true' if v else 'false'}"]
    if isinstance(v, (int, float)):
        return [f"{s}{chave}: {v}"]
    v = str(v)
    if v != v.rstrip() and "\n" not in v:
        return [f"{s}{chave}: '" + v.replace("'", "''") + "'"]
    if _precisa_bloco(v):
        linhas = v.split("\n")
        return [f"{s}{chave}: |-"] + [(f"{s}  {ln}" if ln else "") for ln in linhas]
    return [f"{s}{chave}: {v}"]


def _no(chave: str, v: Any, ind: int) -> list[str]:
    s = " " * ind
    if isinstance(v, dict):
        out = [f"{s}{chave}:"]
        for k, x in v.items():
            out += _no(k, x, ind + 2)
        return out
    if isinstance(v, list):
        out = [f"{s}{chave}:"]
        for item in v:
            if isinstance(item, dict) and len(item) == 1:
                (nome, corpo), = item.items()
                if isinstance(corpo, dict):
                    out.append(f"{s}  - {nome}:")
                    for k, x in corpo.items():
                        out += _no(k, x, ind + 6)
                    continue
            out.append(f"{s}  - {item}")
        return out
    return _escalar(chave, v, ind)


def escrever_texto(d: dict, cabecalho: bool = True) -> str:
    linhas: list[str] = []
    for k, v in d.items():
        linhas += _no(k, v, 0)
    return (CABECALHO if cabecalho else "") + "\n".join(linhas) + "\n"


def escrever(caminho: str | Path, d: dict, cabecalho: bool = True) -> None:
    Path(caminho).write_text(escrever_texto(d, cabecalho), encoding="utf-8")


# ---------- percorrer a árvore de controlos ----------

class Controlo:
    """Vista de um controlo dentro da árvore (nome, tipo, propriedades, caminho)."""

    __slots__ = ("nome", "corpo", "caminho", "ecra", "pai")

    def __init__(self, nome: str, corpo: dict, caminho: tuple[str, ...], ecra: str, pai: "Controlo | None"):
        self.nome, self.corpo, self.caminho, self.ecra, self.pai = nome, corpo, caminho, ecra, pai

    @property
    def tipo(self) -> str:
        """Tipo sem versão nem prefixo Classic/: Label, Button, GroupContainer, ..."""
        c = self.corpo.get("Control", "")
        return c.split("@")[0].split("/")[-1]

    @property
    def variante(self) -> str:
        return self.corpo.get("Variant", "")

    @property
    def props(self) -> dict:
        return self.corpo.setdefault("Properties", {}) if "Properties" in self.corpo else {}

    def prop(self, nome: str) -> str | None:
        v = (self.corpo.get("Properties") or {}).get(nome)
        return None if v is None else str(v)

    def definir(self, nome: str, valor: str) -> None:
        """Define uma propriedade mantendo a ordem alfabética usada pelo Studio.

        As outras chaves do controlo (Control, Variant, Layout, MetadataKey, IsLocked,
        Children...) ficam exatamente onde estavam.
        """
        p = dict(self.corpo.get("Properties") or {})
        p[nome] = valor
        ordenado = dict(sorted(p.items(), key=lambda kv: kv[0]))
        if "Properties" in self.corpo:
            self.corpo["Properties"] = ordenado
            return
        novo = {}
        for k, v in self.corpo.items():
            if k == "Children":
                novo["Properties"] = ordenado
            novo[k] = v
        novo.setdefault("Properties", ordenado)
        self.corpo.clear()
        self.corpo.update(novo)

    @property
    def dentro_de_galeria(self) -> bool:
        p = self.pai
        while p is not None:
            if p.tipo == "Gallery":
                return True
            p = p.pai
        return False

    @property
    def dentro_de_formulario(self) -> bool:
        p = self.pai
        while p is not None:
            if p.tipo == "Form":
                return True
            p = p.pai
        return False

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.tipo} {self.nome}>"


def controlos(doc: dict) -> Iterator[Controlo]:
    """Percorre todos os controlos de todos os ecrãs de um documento, em profundidade."""

    def anda(lista, caminho, ecra, pai):
        for item in lista or []:
            for nome, corpo in item.items():
                c = Controlo(nome, corpo, caminho + (nome,), ecra, pai)
                yield c
                yield from anda(corpo.get("Children"), caminho + (nome,), ecra, c)

    for ecra, corpo in (doc.get("Screens") or {}).items():
        yield from anda(corpo.get("Children"), (ecra,), ecra, None)


def formulas(doc: dict) -> Iterator[tuple[str, str, str]]:
    """Devolve (onde, propriedade, fórmula sem o '=') para todas as fórmulas do documento."""
    app = doc.get("App")
    if app:
        for k, v in (app.get("Properties") or {}).items():
            yield ("App", k, str(v).lstrip("="))
    for ecra, corpo in (doc.get("Screens") or {}).items():
        for k, v in (corpo.get("Properties") or {}).items():
            yield (ecra, k, str(v).lstrip("="))
    for c in controlos(doc):
        for k, v in (c.corpo.get("Properties") or {}).items():
            yield (c.nome, k, str(v).lstrip("="))
