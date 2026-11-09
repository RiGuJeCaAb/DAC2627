# Atalhos. Em Windows sem make, use os comandos python -m tools.dac ... diretamente.
PY ?= python3

.PHONY: instalar verificar lint colar docs testes deriva

instalar:            ## dependências (uma vez)
	$(PY) -m pip install -e ".[dev]"

verificar:           ## tudo o que o CI corre
	$(PY) -m tools.dac validar
	$(PY) -m tools.dac formatar --verificar
	$(PY) -m tools.dac lint --estrito
	$(PY) -m tools.dac paleta --verificar
	$(PY) -m tools.dac inventario --verificar
	$(PY) -m pytest

lint:
	$(PY) -m tools.dac lint

colar:               ## blocos para colar no Studio em build/colar/
	$(PY) -m tools.dac colar

docs:                ## regenera docs/inventario.md e docs/paleta.md
	$(PY) -m tools.dac inventario
	$(PY) -m tools.dac paleta

testes:
	$(PY) -m pytest

deriva:
	$(PY) -m tools.dac deriva
