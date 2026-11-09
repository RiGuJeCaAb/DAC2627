"""Análise léxica mínima de Power Fx, suficiente para converter separadores e fazer lint.

Distingue quatro tipos de pedaço:
  - código                       Filter(x, y > 0.5)
  - cadeia de texto              "Olá, mundo"  ("" dentro é uma aspa)
  - identificador entre plicas   'Service Title'  ('' dentro é uma plica)
  - comentário                   // até ao fim da linha, ou /* ... */

As cadeias interpoladas ($"Olá {nome}") são tratadas com uma pilha: o texto
fica como cadeia e o que está entre chavetas volta a ser código.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

CODIGO, TEXTO, PLICAS, COMENTARIO = "codigo", "texto", "plicas", "comentario"


@dataclass
class Pedaco:
    tipo: str
    texto: str


class ErroLexico(ValueError):
    pass


def partir(src: str) -> list[Pedaco]:
    """Parte uma fórmula em pedaços de código, texto, plicas e comentário."""
    out: list[Pedaco] = []
    buf: list[str] = []
    i, n = 0, len(src)
    # pilha de contextos: cada nível é "codigo" ou "interp" (dentro de $"...")
    pilha: list[str] = ["codigo"]
    chavetas: list[int] = [0]

    def despeja(tipo=CODIGO):
        if buf:
            out.append(Pedaco(tipo, "".join(buf)))
            buf.clear()

    while i < n:
        ch = src[i]
        if pilha[-1] == "interp":
            # dentro do texto de uma cadeia interpolada
            j = i
            while j < n:
                if src[j] == '"' and j + 1 < n and src[j + 1] == '"':
                    j += 2
                    continue
                if src[j] == "{" and j + 1 < n and src[j + 1] == "{":
                    j += 2
                    continue
                if src[j] in '"{':
                    break
                j += 1
            if j >= n:
                raise ErroLexico("cadeia interpolada por terminar")
            out.append(Pedaco(TEXTO, src[i:j + 1] if src[j] == '"' else src[i:j]))
            if src[j] == '"':
                pilha.pop()
                chavetas.pop()
                i = j + 1
            else:  # '{' abre código
                out.append(Pedaco(CODIGO, "{"))
                pilha.append("codigo")
                chavetas.append(0)
                i = j + 1
            continue

        if ch == "$" and i + 1 < n and src[i + 1] == '"':
            despeja()
            out.append(Pedaco(TEXTO, '$"'))
            pilha.append("interp")
            chavetas.append(0)
            i += 2
            continue
        if ch == '"':
            despeja()
            j = i + 1
            while True:
                if j >= n:
                    raise ErroLexico(f"cadeia de texto por terminar a partir da posição {i}")
                if src[j] == '"':
                    if j + 1 < n and src[j + 1] == '"':
                        j += 2
                        continue
                    break
                j += 1
            out.append(Pedaco(TEXTO, src[i:j + 1]))
            i = j + 1
            continue
        if ch == "'":
            despeja()
            j = i + 1
            while True:
                if j >= n:
                    raise ErroLexico(f"identificador entre plicas por terminar a partir da posição {i}")
                if src[j] == "'":
                    if j + 1 < n and src[j + 1] == "'":
                        j += 2
                        continue
                    break
                j += 1
            out.append(Pedaco(PLICAS, src[i:j + 1]))
            i = j + 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] in "/*":
            despeja()
            if src[i + 1] == "/":
                j = src.find("\n", i)
                j = n if j < 0 else j
            else:
                j = src.find("*/", i + 2)
                if j < 0:
                    raise ErroLexico("comentário /* por terminar")
                j += 2
            out.append(Pedaco(COMENTARIO, src[i:j]))
            i = j
            continue
        if len(pilha) > 1 and pilha[-1] == "codigo":
            if ch == "{":
                chavetas[-1] += 1
            elif ch == "}":
                if chavetas[-1] == 0:
                    despeja()
                    out.append(Pedaco(CODIGO, "}"))
                    pilha.pop()
                    chavetas.pop()
                    i += 1
                    continue
                chavetas[-1] -= 1
        buf.append(ch)
        i += 1
    if pilha[-1] == "interp":
        raise ErroLexico("cadeia interpolada por terminar")
    despeja()
    return out


def _troca_codigo(codigo: str, para_pt: bool) -> str:
    r: list[str] = []
    i, n = 0, len(codigo)
    while i < n:
        ch = codigo[i]
        if para_pt:
            # número decimal: dígito '.' dígito, e o número não faz parte de um identificador
            if ch == "." and i > 0 and codigo[i - 1].isdigit() and i + 1 < n and codigo[i + 1].isdigit():
                k = i - 1
                while k >= 0 and codigo[k].isdigit():
                    k -= 1
                if k < 0 or not (codigo[k].isalnum() or codigo[k] == "_"):
                    r.append(",")
                    i += 1
                    continue
            if ch == ";":
                r.append(";;")
            elif ch == ",":
                r.append(";")
            else:
                r.append(ch)
        else:
            if ch == ";" and i + 1 < n and codigo[i + 1] == ";":
                r.append(";")
                i += 2
                continue
            if ch == ";":
                r.append(",")
            elif ch == ",":
                r.append(".")
            else:
                r.append(ch)
        i += 1
    return "".join(r)


def para_pt(src: str) -> str:
    """Formato invariante (o dos ficheiros) -> formato português do Studio.

    , -> ;    ; -> ;;    0.55 -> 0,55   (só no código; texto e plicas ficam iguais)
    """
    return "".join(p.texto if p.tipo != CODIGO else _troca_codigo(p.texto, True) for p in partir(src))


def para_invariante(src: str) -> str:
    """Formato português do Studio -> formato invariante. Inverso de para_pt."""
    return "".join(p.texto if p.tipo != CODIGO else _troca_codigo(p.texto, False) for p in partir(src))


def so_codigo(src: str) -> str:
    """Substitui o conteúdo de textos e comentários por espaços (mantém plicas).

    Útil para procurar padrões sem apanhar palavras que estão dentro de mensagens.
    """
    r = []
    for p in partir(src):
        if p.tipo in (TEXTO, COMENTARIO):
            r.append('"' + " " * max(0, len(p.texto) - 2) + '"' if p.tipo == TEXTO else " " * len(p.texto))
        else:
            r.append(p.texto)
    return "".join(r)


_ID = re.compile(r"(?<![\w.])([A-Za-z_][A-Za-z0-9_]*)\b(?!\s*:)")  # exclui chaves de registo {nome: ...}


def identificadores(src: str) -> list[str]:
    """Identificadores simples (sem plicas) que aparecem no código, pela ordem."""
    return [m.group(1) for p in partir(src) if p.tipo == CODIGO for m in _ID.finditer(p.texto)]


def verificar_equilibrio(src: str) -> list[str]:
    """Devolve problemas de parênteses, chavetas e parênteses retos desequilibrados."""
    problemas = []
    try:
        pedacos = partir(src)
    except ErroLexico as e:
        return [str(e)]
    pares = {")": "(", "]": "[", "}": "{"}
    pilha: list[str] = []
    for p in pedacos:
        if p.tipo != CODIGO:
            continue
        for ch in p.texto:
            if ch in "([{":
                pilha.append(ch)
            elif ch in pares:
                if not pilha or pilha[-1] != pares[ch]:
                    problemas.append(f"'{ch}' sem abertura correspondente")
                    return problemas
                pilha.pop()
    if pilha:
        problemas.append(f"falta fechar: {''.join(pilha)}")
    return problemas
