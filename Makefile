.PHONY: backend-test backend-lint frontend-install frontend-lint frontend-format test lint format bootstrap

bootstrap:
	py -3.13 -m pip install --upgrade uv
	py -3.13 -m uv venv .venv
	py -3.13 -m uv pip install --python .venv -e .\lib[dev]
	py -3.13 -m uv pip install --python .venv pre-commit ruff
	corepack enable
	pnpm --dir frontend install
	.\.venv\Scripts\pre-commit install

backend-test:
	python -m pytest tests -q

backend-lint:
	ruff check apps tests
	ruff format --check apps tests

frontend-install:
	pnpm --dir frontend install

frontend-lint:
	pnpm --dir frontend lint

frontend-format:
	pnpm --dir frontend format

test: backend-test

lint: backend-lint frontend-lint

format:
	ruff format apps tests
	pnpm --dir frontend format
