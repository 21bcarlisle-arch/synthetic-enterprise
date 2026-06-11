.PHONY: check lint test

check: lint test

lint:
	ruff check .

test:
	pytest tests/ -v --tb=short

fix:
	ruff check . --fix
