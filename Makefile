VENV            = .venv
VENV_BIN        = $(VENV)/bin
V_PYTHON        = $(VENV_BIN)/python
MAIN            = a_maze_ing.py
VERSION         = 1.0.0
OUTPUT_FILE     = mazegen-$(VERSION)-py3-none-any.whl

LOCAL_LIBS	= lib/mlx-2.2-py3-none-any.whl

FLAKE8           = $(VENV_BIN)/flake8
MYPY            = $(VENV_BIN)/mypy
MYPY_FLAGS      = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

SRCS            =  $(wildcard ./src/mazegen/*.py)
export UV_LINK_MODE=copy


all: install

install: build $(VENV)
	uv pip install --python $(V_PYTHON) $(LOCAL_LIBS)
	uv pip install --python $(V_PYTHON) "$(OUTPUT_FILE)[dev]" --force-reinstall

build: $(OUTPUT_FILE)

$(OUTPUT_FILE): $(SRCS) pyproject.toml
	@echo "Building package with uv..."
	uv build
	cp ./dist/$(OUTPUT_FILE) .

$(VENV):
	uv venv $(VENV)

run: install
	uv run $(MAIN) config.txt
	
debug: install
	$(V_PYTHON) -m pdb $(MAIN) config.txt

clean:
	rm -rf $(VENV) dist $(OUTPUT_FILE) .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint: install
	@$(FLAKE8) . --exclude $(VENV)
	@$(MYPY) $(MYPY_FLAGS) src

lint-strict: install
	$(FLAKE8) . --exclude $(VENV)
	$(MYPY) $(MYPY_FLAGS) --strict src

.PHONY: all install build run debug clean lint lint-strict
