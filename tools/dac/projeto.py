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
    return {str(p.relative_to(raiz)): yamlio.ler(p) for p in ficheiros_src(raiz)}


def ordem_ecras(raiz: Path = RAIZ) -> list[str]:
    """Ordem dos ecrãs: a do dac.yaml, se existir; senão a alfabética."""
    import yaml
    cfg = raiz / "dac.yaml"
    if cfg.exists():
        d = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
        if d.get("ecras"):
            return list(d["ecras"])
    return sorted(p.stem.replace(".pa", "") for p in (raiz / "src" / "screens").glob("*.pa.yaml"))
