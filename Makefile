.PHONY: check lint test report publish-report run run-fast

check: lint test

lint:
	ruff check .

test:
	pytest tests/ -v --tb=short

fix:
	ruff check . --fix

report:
	python3 -m saas.reporting.annual_report

publish-report: report
	python3 -m tools.publish_report_gist

# Full 2016-2025 simulation run with LLM risk committee — generates report + JSON
run:
	rm -f docs/reports/run_output_latest.json
	python3 -m saas.reporting.annual_report --save-json docs/reports/run_output_latest.json

# Fast iteration run (deterministic committee, truncated window) — no LLM calls
run-fast:
	python3 -m saas.reporting.annual_report --fast --end-year 2020 --save-json /tmp/run_output_fast.json --output /tmp/ANNUAL_REPORT_fast.md

# Full 2016-2025 segment model run — generates SEGMENT_REPORT.md + saves JSON
run-segments:
	python3 -m saas.reporting.segment_report --save-json docs/reports/run_output_segments_latest.json

# Regenerate segment report from saved JSON (fast, no simulation re-run)
segment-report:
	python3 -m saas.reporting.segment_report --from-json docs/reports/run_output_segments_latest.json
