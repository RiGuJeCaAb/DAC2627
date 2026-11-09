"""Regras de qualidade da APP DAC2627.

Cada regra tem um código estável (DACnnn), uma gravidade e uma explicação curta.
As exceções vivem em dac.yaml e têm de dizer porquê; uma exceção sem motivo é um erro.

Famílias:
  DAC1xx  nomes e variáveis
  DAC2xx  cores e tema
  DAC3xx  acessibilidade (espelha o Verificador de aplicações do Studio)
  DAC4xx  dados, delegação e referências
  DAC5xx  convenções de layout do manual
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from . import pafx
from .yamlio import Controlo, controlos

ERRO, AVISO, INFO = "erro", "aviso", "info"

REGRAS: dict[str, tuple[str, str]] = {
    "DAC101": (AVISO, "Nome de controlo sem o prefixo do tipo ou sem o código da ficha"),
    "DAC102": (ERRO, "Nome de controlo repetido na app"),
    "DAC103": (AVISO, "Variável com prefixo errado (loc/gbl/col)"),
    "DAC104": (INFO, "Controlo de cartão de dados com o nome gerado pelo Studio"),
    "DAC201": (AVISO, "Cor literal fora de App.Formulas: use um token nf*"),
    "DAC202": (ERRO, "Token de cor nf* usado mas não definido em App.Formulas"),
    "DAC301": (AVISO, "AccessibleLabel em falta"),
    "DAC302": (AVISO, "TabIndex não definido"),
    "DAC303": (AVISO, "FocusedBorderThickness em falta ou a 0"),
    "DAC304": (AVISO, "Alvo de toque menor do que 44 × 44"),
    "DAC401": (AVISO, "CountRows sobre AllItems de uma galeria"),
    "DAC402": (ERRO, "Função não delegável dentro de Filter/LookUp sobre Dataverse"),
    "DAC403": (ERRO, "Referência a um controlo ou ecrã que não existe"),
    "DAC404": (AVISO, "Variável lida mas nunca definida"),
    "DAC501": (INFO, "Tamanho de letra fora da escala tipográfica"),
    "DAC502": (AVISO, "Etiqueta ou ícone dentro de galeria sem OnSelect = Select(Parent)"),
    "DAC503": (AVISO, "Contentor interior sem DropShadow explícito"),
    "DAC900": (ERRO, "Exceção em dac.yaml sem motivo"),
}

PREFIXOS = {
    "GroupContainer": "con", "Label": "lbl", "Button": "btn", "TextInput": "txt", "Icon": "ico",
    "Rectangle": "rec", "Gallery": "gal", "DropDown": "drp", "ComboBox": "cmb", "Form": "frm",
    "Timer": "tmr", "CheckBox": "chk", "Image": "img", "Toggle": "tgl", "DatePicker": "dte",
    "Radio": "rad", "HtmlViewer": "htm", "Slider": "sld", "Rating": "rtg",
}
PREFIXO_RE = re.compile(r"^(scr|" + "|".join(sorted(set(PREFIXOS.values()))) + r")[A-Z]")
FICHA_RE = re.compile(r"(In|L\d)")
GERADOS_RE = re.compile(r"^(DataCardKey|ErrorMessage|StarVisible|DataCardValue)\d+$")
CORES_PERMITIDAS = {"Color.White", "Color.Transparent"}
COR_LITERAL_RE = re.compile(r"ColorValue\(\s*\"#[0-9A-Fa-f]{3,8}\"\s*\)|RGBA\([^()]*\)|Color\.[A-Z][A-Za-z]+")
NAO_DELEGAVEIS = ("Text(", "Len(", "Left(", "Right(", "Mid(", "Lower(", "Upper(", "Trim(", " in ", "IsBlank(Trim")


@dataclass
class Achado:
    regra: str
    onde: str          # ecrã.controlo.propriedade
    mensagem: str
    gravidade: str = ""

    def __post_init__(self):
        if not self.gravidade:
            self.gravidade = REGRAS[self.regra][0]

    @property
    def controlo(self) -> str:
        partes = self.onde.split(".")
        return partes[1] if len(partes) > 1 else partes[0]


@dataclass
class Config:
    fontes_dataverse: list[str] = field(default_factory=lambda: ["Cloud Service"])
    tamanhos_letra: list[int] = field(default_factory=lambda: [11, 12, 13, 14, 15, 16, 18, 20, 22, 24, 26, 28, 30, 36, 40])
    excecoes: list[dict] = field(default_factory=list)

    @classmethod
    def ler(cls, caminho: Path | None) -> "Config":
        import yaml
        if caminho is None or not caminho.exists():
            return cls()
        d = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
        lint = d.get("lint", {})
        c = cls()
        for k in ("fontes_dataverse", "tamanhos_letra", "excecoes"):
            if k in lint:
                setattr(c, k, lint[k])
        return c


def _num(v: str | None) -> float | None:
    if v is None:
        return None
    try:
        return float(v.lstrip("="))
    except ValueError:
        return None


def _fx(v) -> str:
    return str(v).lstrip("=") if v is not None else ""


def _onselect_acao(c: Controlo) -> bool:
    """True quando o OnSelect faz alguma coisa além de passar a seleção à galeria."""
    v = _fx(c.prop("OnSelect")).strip()
    return bool(v) and v not in ("false", "Select(Parent)")


def _args_de(codigo: str, inicio: int) -> str:
    """Devolve o texto entre o '(' em codigo[inicio] e o ')' correspondente."""
    nivel = 0
    for j in range(inicio, len(codigo)):
        if codigo[j] == "(":
            nivel += 1
        elif codigo[j] == ")":
            nivel -= 1
            if nivel == 0:
                return codigo[inicio + 1:j]
    return codigo[inicio + 1:]


class Analise:
    def __init__(self, docs: dict[str, dict], cfg: Config | None = None):
        """docs: {caminho: documento} com o App.pa.yaml e os ecrãs."""
        self.cfg = cfg or Config()
        self.docs = docs
        self.achados: list[Achado] = []
        self.todos: list[Controlo] = [c for d in docs.values() for c in controlos(d)]
        self.ecras = [e for d in docs.values() for e in (d.get("Screens") or {})]
        self.app = next((d["App"] for d in docs.values() if "App" in d), {})
        self.app_formulas = _fx((self.app.get("Properties") or {}).get("Formulas", ""))
        self.tokens = set(re.findall(r"(?:^|[;\s])(nf[A-Za-z0-9]+)\s*=", self.app_formulas))
        self.nomes = {c.nome for c in self.todos} | set(self.ecras)

    def _add(self, regra, onde, msg):
        self.achados.append(Achado(regra, onde, msg))

    # ----- percorre tudo -----
    def correr(self) -> list[Achado]:
        self._nomes()
        self._variaveis()
        self._cores()
        self._acessibilidade()
        self._dados()
        self._layout()
        self._excecoes()
        ordem = {ERRO: 0, AVISO: 1, INFO: 2}
        self.achados.sort(key=lambda a: (ordem[a.gravidade], a.regra, a.onde))
        return self.achados

    # ----- DAC1xx -----
    def _nomes(self):
        conta = Counter(c.nome for c in self.todos)
        for c in self.todos:
            onde = f"{c.ecra}.{c.nome}"
            if conta[c.nome] > 1:
                self._add("DAC102", onde, f"'{c.nome}' aparece {conta[c.nome]} vezes")
            if c.tipo == "TypedDataCard":
                continue
            if c.dentro_de_formulario and GERADOS_RE.match(c.nome):
                if c.nome.startswith("DataCardValue"):
                    self._add("DAC104", onde, f"renomear para {PREFIXOS.get(c.tipo, '???')}<Ficha><Campo>")
                continue
            esperado = PREFIXOS.get(c.tipo)
            if esperado and not c.nome.startswith(esperado):
                self._add("DAC101", onde, f"{c.tipo} deve começar por '{esperado}'")
            elif esperado and not FICHA_RE.search(c.nome):
                self._add("DAC101", onde, "falta o código da ficha (In, L1, L2, L3...)")

    def _variaveis(self):
        definidas: dict[str, set] = defaultdict(set)   # ecrã -> loc*
        globais, colecoes = set(), set()
        lidas: list[tuple[str, str, str]] = []
        for caminho, d in self.docs.items():
            for ecra_ou_app, corpo, onde_base in self._fontes_formulas(d):
                for prop, fx in corpo:
                    try:
                        cod = pafx.so_codigo(fx)
                    except pafx.ErroLexico:
                        continue
                    for m in re.finditer(r"UpdateContext\(\s*\{", cod):
                        for chave in self._chaves_registo(cod, m.end() - 1):
                            definidas[ecra_ou_app].add(chave)
                            if not chave.startswith("loc"):
                                self._add("DAC103", f"{onde_base}.{prop}", f"'{chave}' em UpdateContext deve começar por loc")
                    for m in re.finditer(r"Navigate\(\s*(\w+)\s*,[^,]*,\s*\{", cod):
                        alvo = m.group(1)
                        for chave in self._chaves_registo(cod, m.end() - 1):
                            definidas[alvo].add(chave)
                            if not chave.startswith("loc"):
                                self._add("DAC103", f"{onde_base}.{prop}", f"'{chave}' passado no Navigate deve começar por loc")
                    for m in re.finditer(r"\bSet\(\s*(\w+)", cod):
                        globais.add(m.group(1))
                        if not m.group(1).startswith("gbl"):
                            self._add("DAC103", f"{onde_base}.{prop}", f"'{m.group(1)}' em Set deve começar por gbl")
                    for m in re.finditer(r"\b(?:ClearCollect|Collect)\(\s*(\w+)", cod):
                        colecoes.add(m.group(1))
                        if not m.group(1).startswith("col"):
                            self._add("DAC103", f"{onde_base}.{prop}", f"'{m.group(1)}' deve começar por col")
                    for ident in pafx.identificadores(fx):
                        if re.match(r"^(loc|gbl|col)[A-Z]", ident):
                            lidas.append((ecra_ou_app, f"{onde_base}.{prop}", ident))
        vistos = set()
        for ecra, onde, ident in lidas:
            ok = (ident in definidas.get(ecra, ()) if ident.startswith("loc")
                  else ident in globais if ident.startswith("gbl") else ident in colecoes)
            if not ok and (ecra, ident) not in vistos:
                vistos.add((ecra, ident))
                self._add("DAC404", onde, f"'{ident}' é lida mas nunca definida" + (f" no ecrã {ecra}" if ident.startswith("loc") else ""))

    def _fontes_formulas(self, d):
        if "App" in d:
            yield "App", [(k, _fx(v)) for k, v in (d["App"].get("Properties") or {}).items()], "App"
        for ecra, corpo in (d.get("Screens") or {}).items():
            props = [(k, _fx(v)) for k, v in (corpo.get("Properties") or {}).items()]
            for c in controlos({"Screens": {ecra: corpo}}):
                props += [(f"{c.nome}.{k}", _fx(v)) for k, v in (c.corpo.get("Properties") or {}).items()]
            yield ecra, props, ecra

    @staticmethod
    def _chaves_registo(cod: str, i: int) -> list[str]:
        """Chaves de topo do registo { ... } que começa em cod[i]."""
        nivel, chaves, atual = 0, [], []
        for j in range(i, len(cod)):
            ch = cod[j]
            if ch in "({[":
                nivel += 1
                if nivel == 1:
                    atual = []
                    continue
            elif ch in ")}]":
                nivel -= 1
                if nivel == 0:
                    break
            if nivel == 1:
                if ch == ":":
                    nome = "".join(atual).strip().strip("'")
                    if re.match(r"^\w+$", nome):
                        chaves.append(nome)
                    atual = []
                elif ch == ",":
                    atual = []
                else:
                    atual.append(ch)
        return chaves

    # ----- DAC2xx -----
    def _cores(self):
        usados = set()
        for c in self.todos:
            for k, v in (c.corpo.get("Properties") or {}).items():
                fx = _fx(v)
                try:
                    cod = pafx.so_codigo(fx)
                except pafx.ErroLexico:
                    continue
                for m in COR_LITERAL_RE.finditer(cod):
                    if m.group(0) not in CORES_PERMITIDAS:
                        self._add("DAC201", f"{c.ecra}.{c.nome}.{k}", m.group(0))
                usados |= set(re.findall(r"\bnf[A-Z][A-Za-z0-9]*", cod))
        for t in sorted(usados - self.tokens):
            self._add("DAC202", "App.Formulas", f"'{t}' não está definido")

    # ----- DAC3xx -----
    def _acessibilidade(self):
        for c in self.todos:
            onde = f"{c.ecra}.{c.nome}"
            if c.dentro_de_formulario and c.tipo in ("Label", "TypedDataCard"):
                continue
            al = c.prop("AccessibleLabel")
            precisa_al = c.tipo in ("Gallery", "TextInput", "DropDown", "ComboBox", "Rectangle", "Image") or (
                c.tipo == "Icon")
            if precisa_al and al is None:
                self._add("DAC301", onde, f"{c.tipo} sem AccessibleLabel" +
                          (" (decorativo: use \"\")" if c.tipo == "Rectangle" else ""))
            if al is not None and _fx(al) == '""' and c.tipo in ("Icon",) and _onselect_acao(c):
                self._add("DAC301", onde, "ícone com ação não pode ter AccessibleLabel vazio")
            if c.dentro_de_formulario:
                continue
            tab = _num(c.prop("TabIndex"))
            em_gal = c.dentro_de_galeria
            if c.tipo == "Button" and tab is not None and tab < 0:
                self._add("DAC302", onde, "botão com TabIndex -1 não recebe foco pelo teclado")
            elif c.prop("TabIndex") is None and (c.tipo == "Rectangle" or (
                    not em_gal and c.tipo in ("Label", "Icon", "Gallery"))):
                self._add("DAC302", onde, f"defina TabIndex ({'0' if _onselect_acao(c) or c.tipo == 'Gallery' else '-1'})")
            if c.tipo == "Label" and not em_gal:
                fb = _num(c.prop("FocusedBorderThickness"))
                if fb is None or fb <= 0:
                    self._add("DAC303", onde, "defina FocusedBorderThickness = 2")
            if c.tipo in ("Icon", "Button") and _onselect_acao(c) and _fx(c.prop("Visible")) != "false":
                w, h = _num(c.prop("Width")), _num(c.prop("Height"))
                if (w is not None and w < 44) or (h is not None and h < 44):
                    self._add("DAC304", onde, f"{int(w or 0)} × {int(h or 0)}")

    # ----- DAC4xx -----
    def _dados(self):
        fontes = "|".join(re.escape(f) for f in self.cfg.fontes_dataverse)
        rx_fonte = re.compile(r"\b(Filter|LookUp|Search|CountIf|SortByColumns)\(\s*'(" + fontes + r")'\s*,") if fontes else None
        rx_ref = re.compile(r"(?<![\w.'])((?:scr|con|lbl|btn|txt|ico|rec|gal|drp|cmb|frm|tmr|chk|img)[A-Z]\w*)")
        for d in self.docs.values():
            for ecra_ou_app, props, base in self._fontes_formulas(d):
                for prop, fx in props:
                    try:
                        cod = pafx.so_codigo(fx)
                    except pafx.ErroLexico:
                        continue
                    onde = f"{base}.{prop}"
                    if re.search(r"CountRows\(\s*\w+\.AllItems\s*\)", cod):
                        self._add("DAC401", onde, "AllItems só tem as linhas já carregadas; conte sobre a fonte")
                    if rx_fonte:
                        for m in rx_fonte.finditer(cod):
                            args = _args_de(cod, m.start() + len(m.group(1)))
                            # LookUp(Choices(...), Text(Value) = ...) é avaliado localmente: não conta
                            limpo = re.sub(r"LookUp\(\s*Choices\([^()]*\)\s*,[^()]*(\([^()]*\))?[^()]*\)", "", args)
                            for f in NAO_DELEGAVEIS:
                                if f in limpo:
                                    self._add("DAC402", onde, f"{f.strip()} dentro de {m.group(1)}('{m.group(2)}'): só os primeiros 500 registos")
                                    break
                    for m in rx_ref.finditer(cod):
                        nome = m.group(1)
                        if nome not in self.nomes:
                            self._add("DAC403", onde, f"'{nome}' não existe")

    # ----- DAC5xx -----
    def _layout(self):
        escala = set(self.cfg.tamanhos_letra)
        for c in self.todos:
            onde = f"{c.ecra}.{c.nome}"
            tam = c.prop("Size")
            if tam is not None and not c.dentro_de_formulario:
                for n in re.findall(r"(?<![\w.])(\d+)(?![\w.])", _fx(tam)):
                    if int(n) not in escala:
                        self._add("DAC501", f"{onde}.Size", f"{n} não está em {sorted(escala)}")
            if c.dentro_de_galeria and c.tipo in ("Label", "Icon") and _fx(c.prop("OnSelect")).strip() != "Select(Parent)" and not _onselect_acao(c):
                self._add("DAC502", onde, "acrescente OnSelect = Select(Parent)")
            if c.tipo == "GroupContainer" and c.pai is not None and c.prop("DropShadow") is None:
                self._add("DAC503", onde, "acrescente DropShadow = DropShadow.None")

    # ----- exceções -----
    def _excecoes(self):
        restantes = []
        for i, e in enumerate(self.cfg.excecoes):
            if not str(e.get("motivo", "")).strip():
                self._add("DAC900", f"dac.yaml.excecoes[{i}]", f"{e.get('regra')} em {e.get('controlo')}")
        for a in self.achados:
            if any(e.get("regra") == a.regra and e.get("controlo") == a.controlo and str(e.get("motivo", "")).strip()
                   for e in self.cfg.excecoes):
                continue
            restantes.append(a)
        self.achados = restantes
