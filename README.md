# APP DAC2627 — código-fonte

Canvas app do Power Apps com os laboratórios da UC **Desenvolvimento de Aplicações na Cloud** (CTeSP Computação Cloud, ESTGL/IPV, 2026/27). Este repositório tem o código da solução **DAC2627** e as ferramentas que o mantêm verificável: validação contra o schema oficial, lint com regras da casa, testes e CI.

| Item | Valor |
|---|---|
| App | `DAC2627_RGJCA` (Canvas, tablet/responsiva), versão **1.1.0** em `src/` |
| Última exportação | Solução `DAC2627` 1.0.0.0, não gerida, 8/11/2026 (`_export/`) |
| Ambiente | Ambiente de RICARDO GUILHERME DE JESUS CAEIRO DE ABREU 26103 (`94d3a652-b3a8-e2dd-9b54-025090fe6659`) |
| Ecrã inicial | `scrInicio` |
| Dados | Dataverse `mcsft_cloudservice` (375 registos) e a API REST `jsonplaceholder.typicode.com` |
| Manual | [Manual ABC · APP DAC2627](https://claude.ai/artifact/KBTUodvciyxM4pzJ9kdhxL) (parte H: este repositório) |

> `src/` está à frente da exportação: as alterações da v1.1.0 (migração m001) ainda têm de ser coladas no Studio. `python -m tools.dac deriva` lista o que falta.

## Começar

```bash
python3 -m pip install -e ".[dev]"
```

```bash
make verificar
```

`make verificar` corre o mesmo que o CI: validação, formato, lint estrito, contraste, documentos gerados e testes. Sem `make` (Windows), use os comandos `python -m tools.dac ...` da tabela abaixo.

## Ferramenta `dac`

| Comando | O que faz |
|---|---|
| `python -m tools.dac validar` | YAML, [schema oficial v3.0](schemas/NOTICE.md) e parênteses/aspas de todas as fórmulas |
| `python -m tools.dac lint` | Regras DAC1xx–DAC5xx: nomes, variáveis, cores, acessibilidade, delegação, referências ([catálogo](docs/regras-lint.md)) |
| `python -m tools.dac pt scrL1Pedido` | Fórmulas como o manual as mostra, `Controlo.Propriedade = ...`, já com `;` e `;;` |
| `python -m tools.dac colar` | `build/colar/`: ecrãs prontos a colar no Studio e `App.Formulas` em PT |
| `python -m tools.dac inventario` | [`docs/inventario.md`](docs/inventario.md): controlos, variáveis, fontes de dados e mapa de navegação |
| `python -m tools.dac paleta` | [`docs/paleta.md`](docs/paleta.md): tokens `nf*` e contraste WCAG 2.2 dos pares usados |
| `python -m tools.dac deriva` | Diferenças entre `src/` e a última exportação |
| `python -m tools.dac sincronizar X.zip` | Atualiza `solution/`, `msapp/` e `src/` a partir de uma exportação nova |
| `python -m tools.dac formatar` | Reescreve `src/` no formato exato do Studio |

## Estrutura

```
src/
  app/App.pa.yaml            Formulas (paleta nf*, nfVersao), StartScreen, Theme
  screens/*.pa.yaml          Um ficheiro por ecrã (Power Fx YAML, formato invariante: , e ;)
tools/
  dac/                       Ferramenta de linha de comandos (Python 3.10+, pyyaml, jsonschema)
  migracoes/m001_*.py        Alterações em massa, idempotentes e documentadas
  legacy/                    gen.py e bundle.py antigos (já não geram src/; ver o README lá dentro)
tests/                       pytest: conversão PT, lint, ida e volta byte a byte, migração, sincronização
docs/                        alm.md, regras-lint.md, inventario.md e paleta.md (estes dois gerados)
schemas/pa.schema.v3.0.yaml  Schema oficial dos .pa.yaml (Microsoft, MIT)
dac.yaml                     Ordem dos ecrãs, escala tipográfica, exceções do lint com motivo
dataverse/schema.md          Tabela Cloud Service: colunas, escolhas e limites
connector/openapi.json       Conector JSONPlaceholderDAC (GET /users, GET /posts)
data/                        cloud_service_375.csv e o levantamento em Excel
solution/  msapp/            Exportação em bruto (não editar; atualizada por dac sincronizar)
_export/                     Zips das exportações
.github/workflows/           verificar.yml (CI) e modelos de ALM (exportar/importar)
```

## Ecrãs

| Ficha | Ecrã | Função |
|---|---|---|
| — | `scrInicio` | Galeria de fichas e versão da app no rodapé |
| 01 | `scrL1BoasVindas` → `scrL1Pedido` → `scrL1Saudacao` | Três ecrãs, navegação e variável global com o nome |
| 02 | `scrL2Servicos` | CRUD sobre a tabela Cloud Service: lista filtrável e delegável, formulário, validação, diálogo, mensagens |
| 03 | `scrL3Lista` → `scrL3Detalhe` → `scrL3Publicacao` | API JSONPlaceholder com filtro por utilizador, erro (vermelho) e aviso de dados vazios (âmbar) |

## Fluxo de trabalho

Resumo de [`docs/alm.md`](docs/alm.md):

1. **Studio → git**: exportar a solução e correr `python -m tools.dac sincronizar <zip>`.
2. **Alterar**: editar `src/` ou escrever uma migração; `make verificar`.
3. **git → Studio**: `python -m tools.dac colar`; colar primeiro `App.Formulas.pt.txt` e depois os ecrãs (Ctrl+V na Vista de árvore).
4. **Confirmar**: correr o Verificador de aplicações e os testes do manual (G2), exportar de novo e correr `dac deriva`.

## O que mudou na v1.1.0

Ver [`CHANGELOG.md`](CHANGELOG.md).
