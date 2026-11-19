"""Localização dos ficheiros do projeto e carregamento dos documentos .pa.yaml."""
from __future__ import annotations

from pathlib import Path

from . import yamlio

RAIZ = Path(__file__).resolve().parents[2]
SRC = RAIZ / "src"
MSAPP = RAIZ / "msapp"
SOLUCAO = RAIZ / "solution"
SCHEMA = RAIZ / "schemas" / "pa.schema.v3.0.yaml"
CONFIG = RAIZ / "dac.yaml"
BUILD = RAIZ / "build"
DOCS = RAIZ / "docs"


def ficheiros_src(raiz: Path = RAIZ) -> list[Path]:
    src = raiz / "src"
    return sorted(src.glob("app/*.pa.yaml")) + sorted(src.glob("screens/*.pa.yaml"))


def carregar(raiz: Path = RAIZ) -> dict[str, dict]:
    return {str(p.relative_to(raiz)): yamlio.ler_tolerante(p)[0] for p in ficheiros_src(raiz)}


def ordem_ecras(raiz: Path = RAIZ) -> list[str]:
    """Ordem dos ecrãs: a do dac.yaml, se existir; senão a alfabética."""
    import yaml
    cfg = raiz / "dac.yaml"
    if cfg.exists():
        d = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
        if d.get("ecras"):
            return list(d["ecras"])
    return sorted(p.stem.replace(".pa", "") for p in (raiz / "src" / "screens").glob("*.pa.yaml"))


def config(raiz: Path = RAIZ) -> dict:
    import yaml
    cfg = raiz / "dac.yaml"
    return (yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}) if cfg.exists() else {}


def propriedades_exportadas(raiz: Path = RAIZ) -> dict[str, set[str]]:
    """Propriedades que o Studio conhece por tipo de controlo, tiradas da exportação (msapp/Controls).

    Chave: nome do modelo em minúsculas (label, groupcontainer, gallery...). Junta as regras
    e as propriedades dinâmicas (as que o contentor com AutoLayout dá aos filhos). As do modelo
    da galeria (OnSelect, TemplateFill) contam como da galeria, que é onde o YAML as escreve.
    Sem exportação devolve um dicionário vazio e a verificação não corre.
    """
    import json
    from collections import defaultdict
    conhecidas: dict[str, set[str]] = defaultdict(set)

    def anda(no: dict) -> None:
        nome = ((no.get("Template") or {}).get("Name") or "").lower()
        if nome == "gallerytemplate":
            nome = "gallery"
        for r in no.get("Rules") or []:
            conhecidas[nome].add(r["Property"])
        for r in no.get("DynamicProperties") or []:
            if r.get("PropertyName"):
                conhecidas[nome].add(r["PropertyName"])
        for c in no.get("Children") or []:
            anda(c)

    for f in sorted((raiz / "msapp" / "Controls").glob("*.json")):
        anda(json.loads(f.read_text(encoding="utf-8")).get("TopParent") or {})
    return dict(conhecidas)
