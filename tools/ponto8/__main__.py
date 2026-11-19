"""Gera o documento do ponto 8 para o professor a partir de conteudo/ponto8.yaml.

    python -m tools.ponto8            # build/ponto8/AAAAMMDDHHMM_Ponto8_..._CLD.docx

O ecrã scrL4Complemento sai do mesmo ficheiro (migração m004): mudar o texto lá e gerar os dois.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

from tools.dac import projeto

MESES = ["jan.", "fev.", "mar.", "abr.", "maio", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."]
SITES = {"support.microsoft.com": "Microsoft Support", "learn.microsoft.com": "Microsoft Learn",
         "powerapps.microsoft.com": "Microsoft Power Apps", "www.microsoft.com": "Microsoft"}


def dados(raiz: Path, agora: datetime) -> dict:
    c = yaml.safe_load((raiz / "conteudo" / "ponto8.yaml").read_text(encoding="utf-8"))
    doc = c["documento"]
    # APA 7.ª: mesmo autor e sem data -> s.d.-a, s.d.-b... pela ordem alfabética dos títulos
    fontes = sorted(c["fontes"], key=lambda f: f["titulo"].lower())
    letra = {f["id"]: f"s.d.-{chr(97 + i)}" for i, f in enumerate(fontes)}
    data = f"{agora.day} de {MESES[agora.month - 1]} de {agora.year}"
    refs = [{"autor": "Microsoft.", "ano": letra[f["id"]], "titulo": f["titulo"],
             "site": SITES.get(f["url"].split("/")[2], "Microsoft"),
             "recuperado": f"Recuperado a {data}, de {f['url']}"} for f in fontes]
    servicos = []
    for s in c["servicos"]:
        anos = ", ".join(sorted(letra[r] for r in s["refs"]))
        servicos.append({**s, "citacao": f"(Microsoft, {anos})"})
    questoes = []
    for qq in doc.get("questoes", []):
        anos = ", ".join(sorted(letra[r] for r in qq["refs"]))
        questoes.append({"titulo": qq["titulo"], "pergunta": " ".join(qq["pergunta"].split()),
                         "resposta": qq["resposta"], "citacao": f"(Microsoft, {anos})"})
    todas = sorted(letra.values())
    return {
        "capa": doc["capa"], "introducao": doc["introducao"], "servicos": servicos,
        "criterios": c["criterios"], "comparacao_intro": doc["comparacao_intro"],
        "tabela_legenda": doc["tabela_legenda"],
        "tabela_fonte": f"Fonte: elaboração própria, a partir de Microsoft ({todas[0]} a {todas[-1]}).",
        "questoes": questoes, "conclusao": c["conclusao"], "referencias": refs,
    }


def main(raiz: Path = projeto.RAIZ) -> int:
    agora = datetime.now()
    d = dados(raiz, agora)
    destino = raiz / "build" / "ponto8"
    destino.mkdir(parents=True, exist_ok=True)
    js = destino / "ponto8.json"
    js.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    nome = yaml.safe_load((raiz / "conteudo" / "ponto8.yaml").read_text(encoding="utf-8"))["documento"]["ficheiro"]
    saida = destino / f"{agora:%Y%m%d%H%M}_{nome}_CLD.docx"
    subprocess.run(["node", str(Path(__file__).with_name("gerar_docx.js")), str(js), str(saida)], check=True)
    print(saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
