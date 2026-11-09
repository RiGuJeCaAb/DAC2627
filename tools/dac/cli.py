"""dac — ferramentas de linha de comandos da APP DAC2627.

    python -m tools.dac validar           YAML, schema oficial v3.0 e sintaxe das fórmulas
    python -m tools.dac lint              Regras da casa (nomes, cores, acessibilidade, delegação)
    python -m tools.dac pt scrL1Pedido    Fórmulas no formato português do Studio (; e ;;)
    python -m tools.dac colar             Blocos prontos a colar no Studio (build/colar/)
    python -m tools.dac inventario        docs/inventario.md (controlos, variáveis, navegação)
    python -m tools.dac paleta            docs/paleta.md e verificação de contraste WCAG
    python -m tools.dac deriva            Diferenças entre src/ e a última exportação (msapp/Src)
    python -m tools.dac sincronizar Z.zip Atualiza solution/, msapp/ e src/ a partir de uma exportação
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from . import cores, lint, pafx, projeto, yamlio

# ---------------------------------------------------------------- utilitários

def _p(*a, **k):
    print(*a, **k)
    sys.stdout.flush()


def _linhas_de(caminho: Path) -> list[str]:
    return caminho.read_text(encoding="utf-8").splitlines()


def localizar(raiz: Path, onde: str) -> tuple[str, int]:
    """Converte 'ecrã.controlo.Propriedade' em (ficheiro relativo, linha)."""
    partes = onde.split(".")
    if partes[0] in ("App",):
        f = raiz / "src" / "app" / "App.pa.yaml"
        alvo = partes[1] if len(partes) > 1 else None
        linhas = _linhas_de(f)
        for i, ln in enumerate(linhas, 1):
            if alvo and ln.strip().startswith(f"{alvo}:"):
                return str(f.relative_to(raiz)), i
        return str(f.relative_to(raiz)), 1
    f = raiz / "src" / "screens" / f"{partes[0]}.pa.yaml"
    if not f.exists():
        return onde, 1
    linhas = _linhas_de(f)
    linha = 1
    if len(partes) > 1:
        for i, ln in enumerate(linhas, 1):
            if ln.strip() == f"- {partes[1]}:":
                linha = i
                break
        if len(partes) > 2:
            ind = len(linhas[linha - 1]) - len(linhas[linha - 1].lstrip())
            for j in range(linha, len(linhas)):
                ln = linhas[j]
                if ln.strip().startswith("- ") and len(ln) - len(ln.lstrip()) <= ind:
                    break
                if ln.strip().startswith(f"{partes[2]}:"):
                    linha = j + 1
                    break
    return str(f.relative_to(raiz)), linha


# ---------------------------------------------------------------- validar

def cmd_validar(a) -> int:
    import jsonschema
    import yaml

    raiz = Path(a.raiz)
    schema = yaml.safe_load((raiz / "schemas" / "pa.schema.v3.0.yaml").read_text(encoding="utf-8"))
    validador = jsonschema.Draft7Validator(schema)
    erros = 0
    ficheiros = projeto.ficheiros_src(raiz)
    for f in ficheiros:
        rel = f.relative_to(raiz)
        try:
            d = yamlio.ler(f)
        except yaml.YAMLError as e:
            _p(f"ERRO {rel}: YAML inválido: {e}")
            erros += 1
            continue
        for e in validador.iter_errors(d):
            _p(f"ERRO {rel}: schema: {'/'.join(map(str, e.absolute_path))}: {e.message[:200]}")
            erros += 1
        for onde, prop, fx in yamlio.formulas(d):
            for prob in pafx.verificar_equilibrio(fx):
                _p(f"ERRO {rel}: {onde}.{prop}: {prob}")
                erros += 1
        if not a.sem_formato and f.read_text(encoding="utf-8") != yamlio.escrever_texto(d):
            _p(f"AVISO {rel}: formato diferente do Studio (corra 'dac formatar')")
    ecras_ficheiro = {f.name.replace(".pa.yaml", "") for f in ficheiros if f.parent.name == "screens"}
    ordem = set(projeto.ordem_ecras(raiz))
    if ordem and ordem != ecras_ficheiro:
        _p(f"ERRO dac.yaml: a lista 'ecras' não coincide com src/screens: {sorted(ordem ^ ecras_ficheiro)}")
        erros += 1
    _p(f"validar: {len(ficheiros)} ficheiros, {erros} erro(s)")
    return 1 if erros else 0


def cmd_formatar(a) -> int:
    raiz = Path(a.raiz)
    mudados = 0
    for f in projeto.ficheiros_src(raiz):
        orig = f.read_text(encoding="utf-8")
        novo = yamlio.escrever_texto(yamlio.ler(f))
        if orig != novo:
            mudados += 1
            if not a.verificar:
                f.write_text(novo, encoding="utf-8")
            _p(("por formatar: " if a.verificar else "formatado: ") + str(f.relative_to(raiz)))
    return 1 if (a.verificar and mudados) else 0


# ---------------------------------------------------------------- lint

def cmd_lint(a) -> int:
    raiz = Path(a.raiz)
    cfg = lint.Config.ler(raiz / "dac.yaml")
    achados = lint.Analise(projeto.carregar(raiz), cfg).correr()
    if a.regra:
        achados = [x for x in achados if x.regra in a.regra]
    conta = Counter(x.gravidade for x in achados)
    if a.formato == "github":
        nivel = {"erro": "error", "aviso": "warning", "info": "notice"}
        for x in achados:
            f, ln = localizar(raiz, x.onde)
            _p(f"::{nivel[x.gravidade]} file={f},line={ln},title={x.regra}::{x.onde}: {x.mensagem}")
    elif a.formato == "sarif":
        _p(json.dumps(_sarif(raiz, achados), ensure_ascii=False, indent=1))
    elif a.formato == "md":
        _p("| Gravidade | Regra | Onde | Mensagem |\n|---|---|---|---|")
        for x in achados:
            _p(f"| {x.gravidade} | {x.regra} | `{x.onde}` | {x.mensagem.replace('|', '\\|')} |")
    else:
        for x in achados:
            _p(f"{x.gravidade.upper():5} {x.regra} {x.onde}: {x.mensagem}")
    if a.formato != "sarif":
        resumo = ", ".join(f"{conta[g]} {g}(s)" for g in ("erro", "aviso", "info"))
        por_regra = Counter(x.regra for x in achados)
        _p(f"lint: {resumo}" + (" · " + ", ".join(f"{r}×{n}" for r, n in sorted(por_regra.items())) if por_regra else ""),
           file=sys.stderr if a.formato == "github" else sys.stdout)
    if conta["erro"] or (a.estrito and conta["aviso"]):
        return 1
    return 0


def _sarif(raiz: Path, achados) -> dict:
    nivel = {"erro": "error", "aviso": "warning", "info": "note"}
    regras = [{"id": r, "shortDescription": {"text": t}, "defaultConfiguration": {"level": nivel[g]}}
              for r, (g, t) in lint.REGRAS.items()]
    resultados = []
    for x in achados:
        f, ln = localizar(raiz, x.onde)
        resultados.append({
            "ruleId": x.regra, "level": nivel[x.gravidade],
            "message": {"text": f"{x.onde}: {x.mensagem}"},
            "locations": [{"physicalLocation": {"artifactLocation": {"uri": f}, "region": {"startLine": ln}}}],
        })
    return {"version": "2.1.0", "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [{"tool": {"driver": {"name": "dac-lint", "rules": regras}}, "results": resultados}]}


# ---------------------------------------------------------------- pt

def _ficheiro_de(raiz: Path, nome: str) -> Path:
    if nome.lower() == "app":
        return raiz / "src" / "app" / "App.pa.yaml"
    p = raiz / "src" / "screens" / f"{nome}.pa.yaml"
    if not p.exists():
        raise SystemExit(f"Ecrã desconhecido: {nome}")
    return p


def cmd_pt(a) -> int:
    """Escreve as fórmulas como o manual as mostra: Controlo.Propriedade = fórmula, em formato PT."""
    raiz = Path(a.raiz)
    d = yamlio.ler(_ficheiro_de(raiz, a.alvo))
    saida = []
    for onde, prop, fx in yamlio.formulas(d):
        if a.controlo and onde not in a.controlo:
            continue
        if a.propriedade and prop not in a.propriedade:
            continue
        if not a.tudo and onde != "App" and prop in _PROPS_TRIVIAIS:
            continue
        conv = fx if a.invariante else pafx.para_pt(fx)
        linhas = conv.split("\n")
        saida.append(f"{onde}.{prop} = {linhas[0]}" + "".join("\n" + ln for ln in linhas[1:]))
    texto = "\n".join(saida)
    _p(f"```\n{texto}\n```" if a.md else texto)
    return 0


_PROPS_TRIVIAIS = {"BorderColor", "LayoutMinHeight", "LayoutMinWidth", "Font", "HoverBorderColor", "HoverColor",
                   "HoverFill", "PressedBorderColor", "PressedColor", "PressedFill", "DisabledBorderColor",
                   "DisabledColor", "DisabledFill", "FocusedBorderThickness", "TabIndex"}


# ---------------------------------------------------------------- colar

def cmd_colar(a) -> int:
    raiz = Path(a.raiz)
    destino = Path(a.destino) if a.destino else raiz / "build" / "colar"
    destino.mkdir(parents=True, exist_ok=True)
    ecras = a.ecras or projeto.ordem_ecras(raiz)
    todos: dict = {"Screens": {}}
    for e in ecras:
        d = yamlio.ler(_ficheiro_de(raiz, e))
        (destino / f"{e}.yaml").write_text(yamlio.escrever_texto(d, cabecalho=False), encoding="utf-8")
        todos["Screens"].update(d["Screens"])
    (destino / "TODOS_OS_ECRAS.yaml").write_text(yamlio.escrever_texto(todos, cabecalho=False), encoding="utf-8")
    app = yamlio.ler(raiz / "src" / "app" / "App.pa.yaml")["App"]["Properties"]
    f = str(app["Formulas"]).lstrip("=")
    (destino / "App.Formulas.invariante.txt").write_text(f + "\n", encoding="utf-8")
    (destino / "App.Formulas.pt.txt").write_text(pafx.para_pt(f) + "\n", encoding="utf-8")
    _p(f"colar: {len(ecras)} ecrã(s) em {destino.relative_to(raiz) if destino.is_relative_to(raiz) else destino}")
    _p("  1. App.Formulas: copie App.Formulas.pt.txt para a propriedade Formulas do objeto App.")
    _p("  2. Ecrãs: apague (ou renomeie) o ecrã antigo, abra o .yaml, copie tudo e faça Ctrl+V na Vista de árvore.")
    return 0


# ---------------------------------------------------------------- inventário

def cmd_inventario(a) -> int:
    raiz = Path(a.raiz)
    docs = projeto.carregar(raiz)
    ordem = projeto.ordem_ecras(raiz)
    por_ecra: dict[str, list] = defaultdict(list)
    for d in docs.values():
        for c in yamlio.controlos(d):
            por_ecra[c.ecra].append(c)
    nav: set[tuple[str, str]] = set()
    variaveis: dict[str, set] = defaultdict(set)
    fontes: dict[str, set] = defaultdict(set)
    for d in docs.values():
        for ecra, corpo in (d.get("Screens") or {}).items():
            fxs = [str(v) for v in (corpo.get("Properties") or {}).values()]
            fxs += [str(v) for c in yamlio.controlos({"Screens": {ecra: corpo}}) for v in (c.corpo.get("Properties") or {}).values()]
            for fx in fxs:
                cod = pafx.so_codigo(fx.lstrip("="))
                for m in re.finditer(r"Navigate\(\s*(\w+)", cod):
                    nav.add((ecra, m.group(1)))
                for i in pafx.identificadores(fx.lstrip("=")):
                    if re.match(r"^(loc|gbl|col)[A-Z]", i):
                        variaveis[ecra].add(i)
                if "'Cloud Service'" in cod:
                    fontes[ecra].add("Dataverse · Cloud Service")
                if "JSONPlaceholderDAC." in cod:
                    fontes[ecra].add("Conector · JSONPlaceholderDAC")
    L = ["# Inventário da APP DAC2627", "",
         "Gerado por `python -m tools.dac inventario` a partir de `src/`. Não editar à mão.", ""]
    total = sum(len(v) for v in por_ecra.values())
    L += [f"{len(ordem)} ecrãs e {total} controlos.", "", "## Navegação", "", "```mermaid", "flowchart LR"]
    for o, dst in sorted(nav):
        L.append(f"  {o} --> {dst}")
    L += ["```", "", "## Resumo por ecrã", "",
          "| Ecrã | Controlos | Tipos mais usados | Variáveis | Dados |", "|---|---:|---|---|---|"]
    for e in ordem:
        cs = por_ecra.get(e, [])
        tipos = Counter(c.tipo for c in cs).most_common(4)
        L.append(f"| `{e}` | {len(cs)} | " + ", ".join(f"{t} {n}" for t, n in tipos) +
                 f" | {', '.join(f'`{v}`' for v in sorted(variaveis[e])) or '—'} | {', '.join(sorted(fontes[e])) or '—'} |")
    for e in ordem:
        L += ["", f"## {e}", "", "```"]
        for c in por_ecra.get(e, []):
            prof = len(c.caminho) - 2
            L.append("  " * prof + f"{c.nome}  [{c.tipo}{'/' + c.variante if c.variante else ''}]")
        L.append("```")
    destino = raiz / "docs" / "inventario.md"
    texto = "\n".join(L) + "\n"
    if a.verificar:
        if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
            _p("inventario: docs/inventario.md está desatualizado (corra 'dac inventario')")
            return 1
        return 0
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    _p(f"inventario: {destino.relative_to(raiz)} ({total} controlos)")
    return 0


# ---------------------------------------------------------------- paleta

def cmd_paleta(a) -> int:
    raiz = Path(a.raiz)
    app = yamlio.ler(raiz / "src" / "app" / "App.pa.yaml")["App"]["Properties"]
    tk = cores.tokens(str(app["Formulas"]))
    tk["Color.White"] = cores.BRANCO
    falhas = 0
    L = ["# Paleta e contraste", "",
         "Gerado por `python -m tools.dac paleta` a partir de `App.Formulas`. Não editar à mão.", "",
         "## Tokens", "", "| Token | Cor | Contraste com branco |", "|---|---|---:|"]
    for nome, rgba in tk.items():
        if nome == "Color.White":
            continue
        cor = cores.hexa(rgba) + (f" · alfa {rgba[3]}" if rgba[3] < 1 else "")
        L.append(f"| `{nome}` | `{cor}` | {cores.contraste(rgba, cores.BRANCO):.2f}:1 |")
    L += ["", "## Pares usados na app", "",
          "AA exige 4,5:1 para texto normal e 3:1 para texto grande e contornos (WCAG 2.2, 1.4.3 e 1.4.11).", "",
          "| Texto / primeiro plano | Fundo | Contraste | Nível | Uso |", "|---|---|---:|---|---|"]
    for fg, bg, uso in cores.PARES:
        if fg not in tk or bg not in tk:
            L.append(f"| `{fg}` | `{bg}` | — | token em falta | {uso} |")
            falhas += 1
            continue
        r = cores.contraste(tk[fg], tk[bg])
        contorno = "mínimo 3:1" in uso
        nv = ("AA" if r >= 3 else "falha") if contorno else cores.nivel(r)
        if nv == "falha":
            falhas += 1
        L.append(f"| `{fg}` | `{bg}` | {r:.2f}:1 | {nv} | {uso} |")
    destino = raiz / "docs" / "paleta.md"
    texto = "\n".join(L) + "\n"
    if a.verificar:
        if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
            _p("paleta: docs/paleta.md está desatualizado (corra 'dac paleta')")
            falhas += 1
    else:
        destino.write_text(texto, encoding="utf-8")
        _p(f"paleta: {destino.relative_to(raiz)} ({len(tk) - 1} tokens, {falhas} par(es) abaixo de AA)")
    return 1 if falhas else 0


# ---------------------------------------------------------------- deriva

def cmd_deriva(a) -> int:
    raiz = Path(a.raiz)
    diferentes = []
    for f in projeto.ficheiros_src(raiz):
        exp = raiz / "msapp" / "Src" / f.name
        if not exp.exists():
            diferentes.append((f.name, "só em src/"))
            continue
        if yamlio.ler(f) != yamlio.ler(exp):
            diferentes.append((f.name, "diferente da exportação"))
    if not diferentes:
        _p("deriva: src/ igual à última exportação")
        return 0
    for n, m in diferentes:
        _p(f"deriva: {n}: {m}")
    _p(f"deriva: {len(diferentes)} ficheiro(s) com alterações por levar ao Studio (use 'dac colar')")
    return 1 if a.falhar else 0


# ---------------------------------------------------------------- sincronizar

def _extrair_seguro(z: zipfile.ZipFile, destino: Path) -> None:
    """Extrai um zip recusando caminhos fora do destino.

    Os .msapp são criados no Windows e usam '\\' como separador ("Src\\App.pa.yaml"):
    normaliza-se para '/' para funcionar também em Linux e macOS (CI incluído).
    """
    destino = destino.resolve()
    destino.mkdir(parents=True, exist_ok=True)
    for m in z.infolist():
        nome = m.filename.replace("\\", "/")
        alvo = (destino / nome).resolve()
        if not alvo.is_relative_to(destino) or nome.startswith("/"):
            raise SystemExit(f"Entrada perigosa no zip: {m.filename}")
        if nome.endswith("/"):
            alvo.mkdir(parents=True, exist_ok=True)
            continue
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_bytes(z.read(m))


def cmd_sincronizar(a) -> int:
    raiz = Path(a.raiz)
    zipf = Path(a.zip)
    if not zipf.exists():
        raise SystemExit(f"Não encontro {zipf}")
    sol, msapp = raiz / "solution", raiz / "msapp"
    for p in (sol, msapp):
        if p.exists():
            shutil.rmtree(p)
    with zipfile.ZipFile(zipf) as z:
        _extrair_seguro(z, sol)
    apps = sorted((sol / "CanvasApps").glob("*.msapp"))
    if len(apps) != 1:
        raise SystemExit(f"Esperava uma Canvas app na solução, encontrei {len(apps)}")
    with zipfile.ZipFile(apps[0]) as z:
        _extrair_seguro(z, msapp)
    (raiz / "_export").mkdir(exist_ok=True)
    if zipf.resolve().parent != (raiz / "_export").resolve():
        shutil.copy2(zipf, raiz / "_export" / zipf.name)
    copiados = 0
    if not a.sem_src:
        for f in sorted((msapp / "Src").glob("*.pa.yaml")):
            if f.name.startswith("_"):
                continue
            dst = raiz / "src" / ("app" if f.name == "App.pa.yaml" else "screens") / f.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
            copiados += 1
    _p(f"sincronizar: solução e msapp extraídos de {zipf.name}; {copiados} ficheiro(s) copiados para src/")
    _p("  Reveja com 'git diff src/' e corra 'dac validar' e 'dac lint' antes de fazer commit.")
    return 0


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="dac", description="Ferramentas da APP DAC2627")
    ap.add_argument("--raiz", default=str(projeto.RAIZ), help="raiz do projeto (por omissão, a do repositório)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("validar", help="YAML, schema oficial e sintaxe das fórmulas")
    s.add_argument("--sem-formato", action="store_true", help="não avisar sobre diferenças de formatação")
    s.set_defaults(f=cmd_validar)

    s = sub.add_parser("formatar", help="reescreve src/ no formato exato do Studio")
    s.add_argument("--verificar", action="store_true", help="só verifica, não escreve")
    s.set_defaults(f=cmd_formatar)

    s = sub.add_parser("lint", help="regras da casa")
    s.add_argument("--formato", choices=["texto", "md", "github", "sarif"], default="texto")
    s.add_argument("--estrito", action="store_true", help="avisos também fazem falhar")
    s.add_argument("--regra", nargs="*", help="só estas regras (ex.: DAC301 DAC302)")
    s.set_defaults(f=cmd_lint)

    s = sub.add_parser("pt", help="fórmulas em formato PT (; e ;;) como no manual")
    s.add_argument("alvo", help="nome do ecrã ou App")
    s.add_argument("--controlo", nargs="*")
    s.add_argument("--propriedade", nargs="*")
    s.add_argument("--tudo", action="store_true", help="inclui propriedades triviais (bordas, hover, ...)")
    s.add_argument("--invariante", action="store_true", help="mantém , e ; (formato dos ficheiros)")
    s.add_argument("--md", action="store_true", help="envolve num bloco de código Markdown")
    s.set_defaults(f=cmd_pt)

    s = sub.add_parser("colar", help="gera os blocos para colar no Studio")
    s.add_argument("ecras", nargs="*")
    s.add_argument("--destino")
    s.set_defaults(f=cmd_colar)

    s = sub.add_parser("inventario", help="gera docs/inventario.md")
    s.add_argument("--verificar", action="store_true")
    s.set_defaults(f=cmd_inventario)

    s = sub.add_parser("paleta", help="gera docs/paleta.md e verifica contraste")
    s.add_argument("--verificar", action="store_true")
    s.set_defaults(f=cmd_paleta)

    s = sub.add_parser("deriva", help="compara src/ com a última exportação")
    s.add_argument("--falhar", action="store_true")
    s.set_defaults(f=cmd_deriva)

    s = sub.add_parser("sincronizar", help="importa uma nova exportação da solução")
    s.add_argument("zip")
    s.add_argument("--sem-src", action="store_true", help="não copiar os .pa.yaml para src/")
    s.set_defaults(f=cmd_sincronizar)

    a = ap.parse_args(argv)
    return a.f(a)
