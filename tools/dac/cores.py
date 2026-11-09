"""Paleta nf* da app: leitura a partir de App.Formulas e contraste WCAG 2.2."""
from __future__ import annotations

import re

_HEX = re.compile(r"(nf[A-Za-z0-9]+)\s*=\s*ColorValue\(\s*\"#([0-9A-Fa-f]{6})\"\s*\)")
_RGBA = re.compile(r"(nf[A-Za-z0-9]+)\s*=\s*RGBA\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)")


def tokens(formulas: str) -> dict[str, tuple[int, int, int, float]]:
    """{nome: (r, g, b, alfa)} para cada nf* definido como ColorValue ou RGBA."""
    out = {}
    for nome, h in _HEX.findall(formulas):
        out[nome] = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
    for nome, r, g, b, a in _RGBA.findall(formulas):
        out[nome] = (int(r), int(g), int(b), float(a))
    return out


def _lin(c: int) -> float:
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(rgb) -> float:
    r, g, b = rgb[:3]
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contraste(a, b) -> float:
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def nivel(r: float, texto_grande: bool = False) -> str:
    if texto_grande:
        return "AAA" if r >= 4.5 else "AA" if r >= 3 else "falha"
    return "AAA" if r >= 7 else "AA" if r >= 4.5 else "falha"


def hexa(rgb) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb[:3])


BRANCO = (255, 255, 255, 1.0)

# Pares texto/fundo que a app usa de facto. Mudar a paleta obriga a manter estes pares acima de AA.
PARES = [
    ("nfTexto", "nfFundo", "Texto principal sobre o fundo dos ecrãs"),
    ("nfTexto", "Color.White", "Texto principal nos cartões"),
    ("nfTextoSuave", "nfFundo", "Texto secundário sobre o fundo"),
    ("nfTextoSuave", "Color.White", "Texto secundário nos cartões"),
    ("Color.White", "nfAzul", "Cabeçalho e botões primários"),
    ("nfAzul", "Color.White", "Botões secundários e títulos de ficha"),
    ("nfAzul", "nfAzulClaro", "Iniciais e linha selecionada"),
    ("nfAzul", "nfAzulFundo", "Etiqueta IaaS"),
    ("nfVerdeTexto", "nfVerdeFundo", "Mensagem de sucesso e etiqueta PaaS"),
    ("nfLaranja", "nfLaranjaFundo", "Etiqueta SaaS"),
    ("nfVermelhoTexto", "nfVermelhoFundo", "Faixas de erro"),
    ("nfVermelho", "Color.White", "Botão Remover"),
    ("Color.White", "nfVermelho", "Botão de confirmar remoção"),
    ("nfAmbar", "nfAmbarFundo", "Faixas de aviso"),
    ("nfVerde", "Color.White", "Ícone de sucesso"),
    ("nfBorda", "Color.White", "Contorno das caixas de texto (mínimo 3:1)"),
]
