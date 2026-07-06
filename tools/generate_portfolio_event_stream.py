"""SUPPLIER_TAB_OVERHAUL.md THE SPINE: the portfolio decision event stream --
live feed of commercial events/decisions across the whole book (renewal
windows, offers with H1 EV, outcomes, arrears steps) -- as the real public
Supplier tab's centerpiece page, not just the shadow mirror.

company/analytics/decision_event_ledger.build_portfolio_event_stream already
does the aggregation (built for the Phase QP shadow case study). This patches
its output onto the already-generated site/data/dashboard.json under
customers.portfolio_event_stream, since billing_ledger.json (needed for the
arrears-opened events) is only written by generate_billing_ledger, which runs
after generate_dashboard_data in the run-complete pipeline -- same
read-existing/patch-key pattern as generate_customer_reaction_chain.py.

Must run after generate_dashboard_data.py and generate_billing_ledger.py.
"""
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
LEDGER_PATH = PROJECT / "site" / "state" / "billing_ledger.json"
DASHBOARD_PATH = PROJECT / "site" / "data" / "dashboard.json"


def generate(run_json_path=None):
    run_path = Path(run_json_path) if run_json_path else RUN_OUTPUT
    if not run_path.exists() or not LEDGER_PATH.exists() or not DASHBOARD_PATH.exists():
        print("Skipped: missing run output, billing ledger, or dashboard.json")
        return 0

    sys.path.insert(0, str(PROJECT))
    from tools.generate_dashboard_data import extract_customers
    from company.analytics.decision_event_ledger import build_portfolio_event_stream

    run = json.loads(run_path.read_text())
    ledger = json.loads(LEDGER_PATH.read_text())
    dash_customers = extract_customers(run)

    stream = build_portfolio_event_stream(
        dash_customers["events"], dash_customers["retention"],
        dash_customers["journey_log"], ledger, limit=200,
    )

    dashboard = json.loads(DASHBOARD_PATH.read_text())
    dashboard.setdefault("customers", {})["portfolio_event_stream"] = stream
    DASHBOARD_PATH.write_text(json.dumps(dashboard, separators=(",", ":")))

    print("Wrote", len(stream), "portfolio events to dashboard.json")
    return len(stream)


if __name__ == "__main__":
    generate(sys.argv[1] if len(sys.argv) > 1 else None)
