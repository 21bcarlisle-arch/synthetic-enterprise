.PHONY: check lint test report

check: lint test

lint:
	ruff check .

test:
	pytest tests/ -v --tb=short

fix:
	ruff check . --fix

report:
	python3 -m saas.reporting.annual_report
