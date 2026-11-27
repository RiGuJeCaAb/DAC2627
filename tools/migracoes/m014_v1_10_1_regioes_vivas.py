"""Migração 014 · v1.10.1 · regiões vivas: o leitor de ecrã passa a anunciar as mensagens, erros e avisos.

Corre sobre src/ depois da m013 e é idempotente: correr de novo não muda nada.

    python -m tools.migracoes.m014_v1_10_1_regioes_vivas

Até aqui nenhuma etiqueta de mensagem tinha Live, por isso um utilizador de leitor de ecrã não ouvia «Serviço
criado», «Não foi possível obter os utilizadores» nem «Introduza o seu nome». Pôr Live nessas etiquetas não
chega: estão dentro de faixas que aparecem e desaparecem (conL2Mensagem.Visible = locMsg <> ""), e a Microsoft
pede a região viva sempre visível e sem mudar de Live, porque alguns leitores de ecrã não detetam regiões que
desaparecem e reaparecem (Microsoft Learn, «Announce dynamic changes with live regions», Best practices).

Cada ecrã ganha uma etiqueta anunciadora na raiz: sempre visível, 1 × 1 no canto, texto transparente, Live fixo e
o Text igual à mensagem, vazio quando não há nada (com o texto vazio o leitor de ecrã não diz nada). A falha da API
da Ficha 03 tem uma anunciadora própria em Assertive, para interromper; o resto é Polite. A faixa visível fica
como estava. Regra do lint DAC305.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.dac import projeto, yamlio
from tools.migracoes.m007_v1_5_ficha04_melhoramento import _ctl

VERSAO = "1.10.1"

# ecrã -> [(nome, Live, Text)]
ANUNCIOS: dict[str, list[tuple[str, str, str]]] = {
    "scrL1Pedido": [
        ("lblL1Anuncio", "Polite", 'If(conL1Aviso.Visible, lblL1Aviso.Text, "")'),
    ],
    "scrL2Servicos": [
        ("lblL2Anuncio", "Polite",
         'If(!IsBlank(locMsg), locMsg, conL2ErroGeral.Visible, lblL2ErroGeral.Text, '
         'lblL2Vazio.Visible, lblL2Vazio.Text, "")'),
    ],
    "scrL3Lista": [
        ("lblL3AnuncioErro", "Assertive", "locL3Erro"),
        ("lblL3Anuncio", "Polite",
         'If(lblL3ACarregar.Visible, lblL3ACarregar.Text, conL3Aviso.Visible, lblL3Vazio.Text, '
         'lblL3SemResultados.Visible, lblL3SemResultados.Text, "")'),
    ],
    "scrL4Pedidos": [("lblL4Anuncio", "Polite", "locL4Msg")],
    "scrL4Conta": [("lblL4dCAnuncio", "Polite", "locL4dMsg")],
    "scrL4Entrar": [("lblL4dEAnuncio", "Polite", "locL4dMsg")],
}


def anunciadora(nome: str, live: str, texto: str) -> dict:
    return _ctl(nome, "Label@2.5.1", {
        "Color": "=Color.Transparent",
        "FocusedBorderThickness": "=2",
        "Height": "=1",
        "Live": f"=Live.{live}",
        "Text": "=" + texto,
        "Width": "=1",
        "X": "=0",
        "Y": "=0",
    })


def migrar_documento(doc: dict) -> None:
    if "App" in doc:
        p = doc["App"]["Properties"]
        atual = re.search(r'nfVersao = "([0-9.]+)"', str(p.get("Formulas") or ""))
        if not atual or tuple(map(int, atual.group(1).split("."))) < tuple(map(int, VERSAO.split("."))):
            p["Formulas"] = re.sub(r'nfVersao = "[0-9.]+";', f'nfVersao = "{VERSAO}";', str(p["Formulas"]))
        return
    for ecra, corpo in (doc.get("Screens") or {}).items():
        filhos = corpo.setdefault("Children", [])
        for nome, live, texto in ANUNCIOS.get(ecra, []):
            novo = anunciadora(nome, live, texto)
            for i, item in enumerate(filhos):
                if nome in item:
                    filhos[i] = novo          # idempotente: repõe a definição desta migração
                    break
            else:
                filhos.append(novo)


def main(raiz: Path = projeto.RAIZ) -> int:
    mudados = 0
    for f in projeto.ficheiros_src(raiz):
        antes = f.read_text(encoding="utf-8")
        d = yamlio.ler(f)
        migrar_documento(d)
        depois = yamlio.escrever_texto(d)
        if depois != antes:
            f.write_text(depois, encoding="utf-8")
            mudados += 1
            print("migrado:", f.relative_to(raiz))
    print(f"m014: {mudados} ficheiro(s) alterado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
