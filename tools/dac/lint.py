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
from .yamlio import omissao as yamlio_omissao

ERRO, AVISO, INFO = "erro", "aviso", "info"

REGRAS: dict[str, tuple[str, str]] = {
    "DAC101": (AVISO, "Nome de controlo sem o prefixo do tipo ou sem o código da ficha"),
    "DAC102": (ERRO, "Nome de controlo repetido na app"),
    "DAC103": (AVISO, "Variável com prefixo errado (loc/gbl/col)"),
    "DAC104": (INFO, "Controlo de cartão de dados com o nome gerado pelo Studio"),
    "DAC201": (AVISO, "Cor literal fora de App.Formulas: use um token nf*"),
    "DAC202": (ERRO, "Token de cor nf* usado mas não definido em App.Formulas"),
    "DAC301": (AVISO, "AccessibleLabel em falta num controlo interativo"),
    "DAC302": (AVISO, "Controlo interativo fora da ordem de tabulação"),
    "DAC303": (AVISO, "FocusedBorderThickness em falta ou a 0"),
    "DAC304": (AVISO, "Alvo de toque menor do que 44 × 44"),
    "DAC305": (AVISO, "Mensagem dinâmica sem região viva sempre visível: o leitor de ecrã não a anuncia"),
    "DAC401": (AVISO, "CountRows sobre AllItems de uma galeria"),
    "DAC402": (ERRO, "Função não delegável dentro de Filter/LookUp sobre Dataverse"),
    "DAC403": (ERRO, "Referência a um controlo ou ecrã que não existe"),
    "DAC404": (AVISO, "Variável lida mas nunca definida"),
    "DAC405": (ERRO, "Propriedade que o Studio não conhece neste tipo de controlo"),
    "DAC407": (AVISO, "Caixa de combinação clássica fora de formulário: a lista abre vazia depois de carregar a app"),
    "DAC406": (ERRO, "Navigate no OnVisible de um ecrã ou no App.OnStart: o Studio não aceita"),
    "DAC408": (ERRO, "Reset de um controlo de formulário ou galeria feito de fora desse formulário ou galeria"),
    "DAC409": (AVISO, "Caixa de texto que filtra dados sem DelayOutput = true"),
    "DAC410": (AVISO, "Last(FirstN(t, n)) ou First(LastN(t, n)) em vez de Index"),
    "DAC411": (AVISO, "Ecrã com demasiados controlos: o Verificador marca-o em Desempenho"),
    "DAC501": (INFO, "Tamanho de letra fora da escala tipográfica"),
    "DAC502": (AVISO, "Etiqueta, ícone ou retângulo dentro de galeria sem OnSelect = Select(Parent)"),
    "DAC503": (AVISO, "Sombra dentro de sombra"),
    "DAC504": (AVISO, "Valor por omissão escrito no código: o Studio apaga-o ao guardar"),
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


# DAC411: o Verificador deu ao scrL4Pedidos complexidade 302 para um máximo de 300, com 219 controlos no repositório
# (25/11/2026). Não diz como a calcula, por isso o lint avisa com folga, a partir de 200 controlos (≈ 276).
MAX_CONTROLOS = 200


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


def _com_sombra(c: Controlo) -> bool:
    """Contentor com sombra. Ausente vale DropShadow.Light, o valor por omissão (o Studio apaga-o)."""
    v = c.prop("DropShadow")
    return v is None or "DropShadow.None" not in _fx(v)


def _antepassado_com_sombra(c: Controlo) -> bool:
    p = c.pai
    while p is not None:
        if p.tipo == "GroupContainer" and _com_sombra(p):
            return True
        p = p.pai
    return False


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
    def __init__(self, docs: dict[str, dict], cfg: Config | None = None,
                 conhecidas: dict[str, set[str]] | None = None):
        """docs: {caminho: documento} com o App.pa.yaml e os ecrãs.

        conhecidas: propriedades por tipo de controlo (projeto.propriedades_exportadas).
        Sem elas a regra DAC405 não corre.
        """
        self.cfg = cfg or Config()
        self.conhecidas = conhecidas or {}
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
        self._propriedades()
        self._navegacao()
        self._escolhas()
        self._repor()
        self._atraso()
        self._indice()
        self._tamanho()
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
                    # sem comentários, mas com o texto: o "#hex" de ColorValue está dentro de aspas
                    sem_coment = "".join(p.texto for p in pafx.partir(fx) if p.tipo != pafx.COMENTARIO)
                    cod = pafx.so_codigo(fx)
                except pafx.ErroLexico:
                    continue
                for m in COR_LITERAL_RE.finditer(sem_coment):
                    if m.group(0) not in CORES_PERMITIDAS:
                        self._add("DAC201", f"{c.ecra}.{c.nome}.{k}", m.group(0))
                usados |= set(re.findall(r"\bnf[A-Z][A-Za-z0-9]*", cod))
        for t in sorted(usados - self.tokens):
            self._add("DAC202", "App.Formulas", f"'{t}' não está definido")

    # ----- DAC3xx -----
    # O Studio apaga ao guardar as propriedades iguais ao valor por omissão (exportação 1.0.0.3:
    # 86 × TabIndex -1, 15 × AccessibleLabel "", 8 × DropShadow.Light). Uma propriedade ausente
    # vale o valor por omissão, e as regras leem-na assim: o que o Studio exporta tem de passar.
    def _regioes_vivas(self):
        """DAC305. Uma mensagem guardada numa variável (loc…Msg, loc…Erro) e mostrada numa etiqueta só é lida
        pelo leitor de ecrã se uma etiqueta com Live (Polite ou Assertive) e sempre visível tiver essa variável
        no Text. A Microsoft pede a região viva sempre visível: alguns leitores de ecrã não a detetam quando
        desaparece e reaparece, como as faixas de mensagem (accessible-apps-live-regions, «Best practices»)."""
        rx_var = re.compile(r"\bloc\w*(?:Msg|Erro)\b")
        por_ecra: dict[str, dict[str, list]] = defaultdict(lambda: {"mostra": [], "vivas": []})
        for c in self.todos:
            if c.tipo != "Label" or c.dentro_de_formulario:
                continue
            try:
                vars_ = set(rx_var.findall(pafx.so_codigo(_fx(c.prop("Text")))))
            except pafx.ErroLexico:
                continue
            if not vars_:
                continue
            live = _fx(c.prop("Live")).strip()
            visivel = _fx(c.prop("Visible")).strip() in ("", "true")
            sempre = visivel and all(_fx(p.prop("Visible")).strip() in ("", "true") for p in self._antepassados(c))
            if live in ("Live.Polite", "Live.Assertive") and sempre:
                por_ecra[c.ecra]["vivas"].append(vars_)
            else:
                por_ecra[c.ecra]["mostra"].append((c, vars_))
        for ecra, d in por_ecra.items():
            anunciadas = set().union(*d["vivas"]) if d["vivas"] else set()
            for c, vars_ in d["mostra"]:
                for v in sorted(vars_ - anunciadas):
                    self._add("DAC305", f"{ecra}.{c.nome}",
                              f"'{v}' não é anunciada: acrescente ao ecrã uma etiqueta sempre visível com "
                              f"Live = Live.Polite (Assertive para erros) e Text = {v}")

    @staticmethod
    def _antepassados(c):
        p = c.pai
        while p is not None:
            yield p
            p = p.pai

    def _acessibilidade(self):
        self._regioes_vivas()
        for c in self.todos:
            onde = f"{c.ecra}.{c.nome}"
            if c.tipo == "TypedDataCard":
                continue
            em_form = c.dentro_de_formulario
            em_gal = c.dentro_de_galeria
            acao = _onselect_acao(c)
            if not em_form:
                al = c.prop("AccessibleLabel")
                vazio = al is None or _fx(al).strip() in ('""', "")
                sempre = c.tipo in ("Gallery", "TextInput", "DropDown", "ComboBox")
                if vazio and (sempre or (acao and c.tipo in ("Icon", "Image", "Rectangle"))):
                    self._add("DAC301", onde, f"{c.tipo} interativo sem AccessibleLabel" if al is None
                              else f"{c.tipo} interativo com AccessibleLabel vazio")
                tab = _num(c.prop("TabIndex"))
                if c.tipo == "Button" and tab is not None and tab < 0:
                    self._add("DAC302", onde, "botão com TabIndex -1 não recebe foco pelo teclado")
                elif c.tipo == "Gallery" and tab is None:
                    self._add("DAC302", onde, "defina TabIndex = 0")
                elif acao and not em_gal and c.tipo in ("Label", "Icon", "Image", "Rectangle") and (tab is None or tab < 0):
                    self._add("DAC302", onde, "tem ação no OnSelect: defina TabIndex = 0 (por omissão é -1)")
            if c.tipo == "Label" and not em_gal:
                fb = _num(c.prop("FocusedBorderThickness"))
                if fb is None or fb <= 0:
                    self._add("DAC303", onde, "defina FocusedBorderThickness = 2")
            if not em_form and c.tipo in ("Icon", "Button") and acao and _fx(c.prop("Visible")) != "false":
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

    def _navegacao(self):
        """DAC406: o Studio recusa Navigate no OnVisible de um ecrã, mesmo dentro de um If
        («navegaria sempre automaticamente para fora do ecrã»), e no App.OnStart (usa-se App.StartScreen)."""
        alvos = [("App.OnStart", (self.app.get("Properties") or {}).get("OnStart"))]
        for d in self.docs.values():
            for ecra, corpo in (d.get("Screens") or {}).items():
                alvos.append((f"{ecra}.OnVisible", (corpo.get("Properties") or {}).get("OnVisible")))
        for onde, fx in alvos:
            if not fx:
                continue
            try:
                cod = pafx.so_codigo(_fx(fx))
            except pafx.ErroLexico:
                continue
            if re.search(r"\bNavigate\s*\(", cod):
                self._add("DAC406", onde, "Navigate não é aceite aqui: navegar a partir do botão que abre o ecrã")

    def _escolhas(self):
        """DAC407: a caixa de combinação clássica (ComboBox) fora de um formulário abriu a lista vazia depois de carregar
        a app, na app publicada e no Studio, com qualquer Items (Choices de uma pesquisa, a tabela, AddColumns, uma coleção).
        Só funcionava na sessão em que a fórmula era editada (24/11/2026). A lista pendente clássica (DropDown) funciona.
        Nos cartões dos formulários a caixa é a que o Studio gera e funciona."""
        for c in self.todos:
            if c.tipo == "ComboBox" and not c.dentro_de_formulario:
                self._add("DAC407", f"{c.ecra}.{c.nome}",
                          "use Classic/DropDown com Items, Items.Value e AllowEmptySelection = true")

    def _repor(self):
        """DAC408: Reset(X) com X dentro de um formulário ou de uma galeria só é aceite a partir do mesmo formulário ou
        galeria. Fora deles a app dá erro em execução («A função Reset só pode ser utilizada com um controlo
        reinicializável»), sem aviso no Studio (botões de teste do valor da Ficha 04, 24/11/2026). Para mudar o valor,
        mude o Default (por exemplo, por uma variável); para repor o formulário, ResetForm."""
        por_nome = {c.nome: c for c in self.todos}

        def contentor(c):
            p = c.pai
            while p is not None:
                if p.tipo in ("Form", "Gallery"):
                    return p.nome
                p = p.pai
            return None
        for c in self.todos:
            for prop, fx in (c.props or {}).items():
                try:
                    cod = pafx.so_codigo(_fx(fx))
                except pafx.ErroLexico:
                    continue
                for alvo in re.findall(r"\bReset\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)", cod):
                    x = por_nome.get(alvo)
                    if x is None:
                        continue
                    dono = contentor(x)
                    if dono and dono != c.nome and contentor(c) != dono:
                        self._add("DAC408", f"{c.ecra}.{c.nome}.{prop}",
                                  f"{alvo} está dentro de {dono}: mude o Default por uma variável ou use ResetForm({dono})")

    def _atraso(self):
        """DAC409: uma caixa de texto lida numa fórmula de dados (Items, Text...) com Filter, Search, LookUp ou uma
        contagem refaz a consulta a cada tecla. O Verificador marca-a em Desempenho (regra app-use-delayoutput-text-input)
        e a Microsoft recomenda DelayOutput = true, que espera meio segundo depois da última tecla
        ([Otimização de código](https://learn.microsoft.com/power-apps/guidance/coding-guidelines/code-optimization)).
        As fórmulas de comportamento (On*) não contam: só correm quando o utilizador carrega num botão."""
        consulta = re.compile(r"\b(Filter|Search|LookUp|CountRows|CountIf)\s*\(")
        caixas = [c for c in self.todos if c.tipo == "TextInput" and _fx(c.prop("DelayOutput")).strip() != "true"]
        if not caixas:
            return
        dados = []
        for c in self.todos:
            for prop, fx in (c.props or {}).items():
                if prop.startswith("On"):
                    continue
                try:
                    cod = pafx.so_codigo(_fx(fx))
                except pafx.ErroLexico:
                    continue
                if consulta.search(cod):
                    dados.append(cod)
        for cx in caixas:
            ref = re.compile(r"\b" + re.escape(cx.nome) + r"\.(Text|Value)\b")
            if any(ref.search(cod) for cod in dados):
                self._add("DAC409", f"{cx.ecra}.{cx.nome}", "defina DelayOutput = true")

    def _indice(self):
        """DAC410: Last(FirstN(t, n)) e First(LastN(t, n)) copiam a tabela até n linhas só para devolver uma.
        Index(t, n) devolve o registo diretamente. O Verificador marca-o em Desempenho («Utilizar o Index para ler um
        registo numa posição específica», btnL4CliIniciais, 25/11/2026). Com n fora do intervalo o Index dá erro: quando
        n pode passar de CountRows(t), usar Index(t, Min(CountRows(t), n))."""
        padrao = re.compile(r"\b(Last\s*\(\s*FirstN|First\s*\(\s*LastN)\s*\(")
        for c in self.todos:
            for prop, fx in (c.props or {}).items():
                try:
                    cod = pafx.so_codigo(_fx(fx))
                except pafx.ErroLexico:
                    continue
                if padrao.search(cod):
                    self._add("DAC410", f"{c.ecra}.{c.nome}.{prop}", "use Index(t, n)")

    def _tamanho(self):
        """DAC411: «Demasiados controlos num ecrã» (regra app-reduce-screen-controls). A Microsoft recomenda dividir o
        ecrã ([Sugestões de desempenho](https://learn.microsoft.com/power-apps/maker/canvas-apps/performance-tips))."""
        conta = {}
        for c in self.todos:
            conta[c.ecra] = conta.get(c.ecra, 0) + 1
        for ecra, n in sorted(conta.items()):
            if n > MAX_CONTROLOS:
                self._add("DAC411", ecra, f"{n} controlos (máximo {MAX_CONTROLOS}): divida o ecrã")

    # ----- DAC5xx -----
    # o YAML e a exportação nem sempre dão o mesmo nome ao tipo
    TIPO_MODELO = {"textinput": "text"}

    def _propriedades(self):
        if not self.conhecidas:
            return
        for d in self.docs.values():
            for ecra, corpo in (d.get("Screens") or {}).items():
                for k in (corpo.get("Properties") or {}):
                    if k not in self.conhecidas.get("screen", {k}):
                        self._add("DAC405", f"{ecra}.{k}", f"Screen não tem a propriedade '{k}'")
        for c in self.todos:
            base = c.tipo.split("@")[0].lower()
            sabidas = self.conhecidas.get(self.TIPO_MODELO.get(base, base))
            if sabidas is None:
                continue  # tipo que ainda não está na exportação: nada a comparar
            for k in (c.corpo.get("Properties") or {}):
                if k.split(".")[0] not in sabidas and k not in sabidas:
                    self._add("DAC405", f"{c.ecra}.{c.nome}.{k}",
                              f"{c.tipo} não tem a propriedade '{k}': o Studio recusa a colagem (PA2108)")

    def _layout(self):
        escala = set(self.cfg.tamanhos_letra)
        for c in self.todos:
            onde = f"{c.ecra}.{c.nome}"
            tam = c.prop("Size")
            if tam is not None and not c.dentro_de_formulario:
                for n in re.findall(r"(?<![\w.])(\d+)(?![\w.])", _fx(tam)):
                    if int(n) not in escala:
                        self._add("DAC501", f"{onde}.Size", f"{n} não está em {sorted(escala)}")
            if c.dentro_de_galeria and c.tipo in ("Label", "Icon", "Rectangle") and _fx(c.prop("OnSelect")).strip() != "Select(Parent)" and not _onselect_acao(c):
                self._add("DAC502", onde, "acrescente OnSelect = Select(Parent)")
            for k, v in (c.corpo.get("Properties") or {}).items():
                if yamlio_omissao(c.tipo, k) == str(v):
                    self._add("DAC504", f"{onde}.{k}", f"{v} é o valor por omissão: retire a linha")
            if c.tipo == "GroupContainer" and _com_sombra(c) and _antepassado_com_sombra(c):
                self._add("DAC503", onde, "sombra dentro de sombra: DropShadow = DropShadow.None")

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
