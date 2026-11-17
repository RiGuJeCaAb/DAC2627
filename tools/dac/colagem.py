"""Verificações antes de colar no Studio: o que o lint não vê.

O lint lê só o código. Não sabe que fontes de dados estão ligadas na app nem que ecrãs
dependem de outros. Foi assim que, a 10/11/2026, o lint estava a zero e o Studio mostrou
205 erros. Este módulo compara o código com a última exportação (msapp/References) e
gera a lista de verificação build/colar/LEIA-ME.txt.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from . import projeto, yamlio

_TEXTO = re.compile(r'"(?:[^"]|"")*"')
_NAVIGATE = re.compile(r"Navigate\(\s*(scr\w+)\s*,[^,{)]*,\s*\{(.*?)\}\s*\)", re.S)
_CHAVE = re.compile(r"(?:^|,)\s*(\w+)\s*:")


@dataclass(frozen=True)
class Navegacao:
    origem: str
    destino: str
    variaveis: tuple[str, ...]


def fontes_esperadas(raiz: Path = projeto.RAIZ) -> dict[str, str]:
    """Fonte de dados -> nome do conjunto de entidades no Dataverse ('conector' para conectores)."""
    cfg = raiz / "dac.yaml"
    if not cfg.exists():
        return {}
    d = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
    return {str(k): str(v) for k, v in (d.get("fontes") or {}).items()}


def _padrao(fonte: str) -> re.Pattern:
    if re.fullmatch(r"\w+", fonte):
        return re.compile(rf"(?<![.\w']){re.escape(fonte)}\b")
    return re.compile(re.escape(f"'{fonte}'"))


def fontes_usadas(raiz: Path = projeto.RAIZ) -> dict[str, list[str]]:
    """Fonte de dados -> ecrãs (ou App) cujas fórmulas a usam. Ignora o texto entre aspas."""
    padroes = {f: _padrao(f) for f in fontes_esperadas(raiz)}
    usadas: dict[str, set[str]] = {}
    for f in projeto.ficheiros_src(raiz):
        doc = yamlio.ler(f)
        onde = "App" if "App" in doc else next(iter(doc.get("Screens") or {"?": 0}))
        for _, _, formula in yamlio.formulas(doc):
            limpa = _TEXTO.sub('""', formula)
            for fonte, p in padroes.items():
                if p.search(limpa):
                    usadas.setdefault(fonte, set()).add(onde)
    return {k: sorted(v) for k, v in sorted(usadas.items())}


def fontes_na_exportacao(raiz: Path = projeto.RAIZ) -> dict[str, str] | None:
    """Fontes de dados da última exportação: nome -> conjunto de entidades ('conector'). None se não houver."""
    ds = raiz / "msapp" / "References" / "DataSources.json"
    if not ds.exists():
        return None
    out: dict[str, str] = {}
    for x in json.loads(ds.read_text(encoding="utf-8")).get("DataSources", []):
        if x.get("Type") == "NativeCDSDataSourceInfo":
            out[x["Name"]] = x.get("EntitySetName", "")
        elif x.get("Type") == "ServiceInfo":
            out[x["Name"]] = "conector"
    return out


def verificar_fontes(raiz: Path = projeto.RAIZ) -> list[str]:
    """Problemas que fariam a colagem falhar por falta (ou troca) de fontes de dados."""
    esperadas = fontes_esperadas(raiz)
    usadas = fontes_usadas(raiz)
    na_app = fontes_na_exportacao(raiz)
    problemas = []
    if na_app is None:
        return ["Não há exportação em msapp/: corra 'dac sincronizar' antes de colar."]
    for fonte, ecras in usadas.items():
        alvo = esperadas[fonte]
        if fonte not in na_app:
            problemas.append(f"'{fonte}' é usada em {', '.join(ecras)} mas não está na app exportada. "
                             f"Adicione-a em Dados antes de colar.")
        elif na_app[fonte] != alvo:
            problemas.append(f"'{fonte}' aponta para '{na_app[fonte]}' e devia apontar para '{alvo}'. "
                             f"Há tabelas com o mesmo nome a apresentar: confirme a tabela em Dados.")
    for fonte in esperadas:
        if fonte not in usadas:
            problemas.append(f"'{fonte}' está em dac.yaml mas nenhum ecrã a usa.")
    return problemas


def navegacoes(raiz: Path = projeto.RAIZ) -> list[Navegacao]:
    """Navigate com registo de contexto: o ecrã de destino precisa destas variáveis."""
    out = []
    for f in projeto.ficheiros_src(raiz):
        doc = yamlio.ler(f)
        for ecra in doc.get("Screens") or {}:
            for _, _, formula in yamlio.formulas(doc):
                for m in _NAVIGATE.finditer(_TEXTO.sub('""', formula)):
                    nav = Navegacao(ecra, m.group(1), tuple(_CHAVE.findall(m.group(2))))
                    if nav not in out:
                        out.append(nav)
    return out


def leia_me(raiz: Path = projeto.RAIZ, ecras: list[str] | None = None) -> str:
    """Lista de verificação para colar no Studio, pela ordem certa."""
    ecras = ecras or projeto.ordem_ecras(raiz)
    usadas = fontes_usadas(raiz)
    esperadas = fontes_esperadas(raiz)
    linhas = ["COLAR NO STUDIO: LISTA DE VERIFICAÇÃO", "",
              "Siga a ordem. Cada passo depende do anterior.", "",
              "1. Fontes de dados. Em Dados, confirme que estão todas antes de mexer nos ecrãs:"]
    for fonte, onde in usadas.items():
        alvo = esperadas[fonte]
        tipo = "conector personalizado" if alvo == "conector" else f"tabela {alvo}"
        linhas.append(f"   - {fonte} ({tipo}), usada em {', '.join(onde)}")
    linhas += ["   Se houver duas tabelas com o mesmo nome a apresentar, escolha a do nome lógico indicado.",
               "",
               "2. App.Formulas. Copie App.Formulas.pt.txt para a propriedade Formulas do objeto App,",
               "   substituindo tudo. Os ecrãs usam estes tokens: sem eles, cada ecrã colado dá erros.",
               "",
               "3. Ecrãs antigos. Apague-os. Renomear só o ecrã não chega: os nomes dos controlos são únicos",
               "   na app inteira e o Studio poria _1 nos controlos colados. Logo a seguir, volte ao passo 1:",
               "   apagar o último ecrã que usa uma fonte de dados pode tirá-la da app.",
               "",
               f"4. Ecrãs novos. Cole TODOS_OS_ECRAS.yaml de uma só vez ({len(ecras)} ecrãs), com Ctrl+V",
               "   na Vista de árvore. Colar um a um obriga a uma ordem, porque estes ecrãs dependem uns dos outros:"]
    for n in navegacoes(raiz):
        vs = ", ".join(n.variaveis) if n.variaveis else "sem variáveis"
        linhas.append(f"   - {n.origem} abre {n.destino} e passa {vs}")
    linhas += ["",
               "5. Erros. A barra de verificação tem de mostrar 0 erros de fórmula. Corra o Verificador de",
               "   aplicações e confira os avisos com docs/alm.md.",
               "",
               "6. Guardar e Publicar. Guardar não chega: a exportação da solução leva a última versão",
               "   PUBLICADA, e é essa que os alunos abrem.",
               "",
               "7. Prova. Exporte a solução (não gerida), corra 'dac sincronizar <zip>' e 'dac deriva'.",
               "   'deriva' tem de dizer que src/ é igual à exportação. Sem isto, a colagem não está feita.",
               ""]
    return "\n".join(linhas)
