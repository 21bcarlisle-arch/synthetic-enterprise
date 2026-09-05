"""Extract and project the 2025-12-31 portfolio state for live daily decision engine.

Reads run_output_latest.json and produces site/state/live_portfolio.json with:
  - Active customers as of the final simulation year
  - Current rates and next-renewal estimates
  - Treasury position
  - Hedge fractions
"""
import json
import datetime as dt
import sys
from pathlib import Path
from collections import defaultdict

PROJECT = Path(__file__).resolve().parent.parent
# THIRD INSTANCE OF THIS DEFECT IN ONE SESSION. `python3 tools/project_portfolio_to_2026.py` runs
# this as a SCRIPT, so `sys.path[0]` is `tools/` and not the repo root, and `_live_seam`'s
# `from company.interfaces.sim_interface import LiveSimInterface` raises ModuleNotFoundError.
# Measured before this guard: all 145 accounts came back with `payment_method: None` from the real
# generator while the same call answered correctly under pytest.
#
# The other two were `tools/next_step_gate.py` (dead in its commit-msg hook) and
# `tools/generate_project_state.py` (published "not stated in CLAUDE.md" over a live figure).
# Every control was green in all three cases, because pytest fixes the path before any test can
# import the module -- so this class is invisible to any test that does.
#
# It was caught here ONLY because `_payment_method` falls to None rather than to the majority
# channel: a `direct_debit` default would have applied the direct-debit engagement factor to the
# entire book and looked exactly like a measurement.
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_PATH = PROJECT / "site" / "state" / "live_portfolio.json"

_DEFAULT_TERM_MONTHS = 12


def _last_renewal_by_cid(customer_events: list[dict]) -> dict[str, dict]:
    """Return the most recent event dict per customer_id from customer_events."""
    last = {}
    for ev in customer_events:
        cid = ev["customer_id"]
        if cid not in last or ev["event_date"] > last[cid]["event_date"]:
            last[cid] = ev
    return last


def _estimate_next_renewal(last_event_date: str, term_months: int = _DEFAULT_TERM_MONTHS) -> str:
    """Estimate next renewal date as last_event_date + term_months."""
    d = dt.date.fromisoformat(last_event_date)
    month = d.month + term_months
    year = d.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    try:
        return dt.date(year, month, d.day).isoformat()
    except ValueError:
        return dt.date(year, month, 28).isoformat()


def _live_seam():
    """The approved SIM/company seam, or None if it cannot be built.

    None rather than a raise: the portfolio is the input to every live decision, and a whole
    portfolio withheld because one observable is unavailable is a worse outcome than a portfolio
    whose payment methods are absent. `_payment_method` makes the absence explicit rather than
    guessing, so nothing downstream can read a missing field as "direct debit".
    """
    try:
        from company.interfaces.sim_interface import LiveSimInterface
        return LiveSimInterface()
    except Exception:  # noqa: BLE001 -- an unavailable observable, never a failed portfolio
        return None


def _payment_method(seam, cid: str, fuel: str):
    """`direct_debit` / `standard_credit` / `prepayment`, or None when it cannot be established.

    NOT defaulted to the majority channel here, deliberately, and this is the opposite choice from
    `LiveSimInterface.get_payment_method`'s own fallback -- for a reason worth stating, because the
    two look inconsistent side by side. There, the argument is a broken CRM record for a customer
    the supplier is still billing, so the majority channel is the best available answer. HERE the
    question is whether the observable is available AT ALL, and answering "direct debit" for an
    entire portfolio the seam could not be built for would silently apply the direct-debit
    engagement factor to every account and look exactly like a measurement.
    """
    if seam is None or not cid:
        return None
    try:
        return seam.get_payment_method(cid, fuel)
    except Exception:  # noqa: BLE001
        return None


def generate(run_output_path=None, out_path=None) -> dict:
    """Build and write live_portfolio.json. Returns the portfolio dict."""
    run_path = Path(run_output_path) if run_output_path else RUN_OUTPUT
    out = Path(out_path) if out_path else OUT_PATH

    data = json.loads(run_path.read_text())

    years = data.get("years", {})
    last_year_key = max(years.keys(), key=lambda y: int(y)) if years else None
    last_year = years.get(last_year_key, {}) if last_year_key else {}

    active_ids = last_year.get("active_customer_ids", [])
    per_customer = last_year.get("per_customer", {})
    hedge_fractions = last_year.get("hedge_fractions", {})
    treasury_end = last_year.get("treasury_end_gbp", data.get("final_treasury_gbp", 0.0))

    last_renewals = _last_renewal_by_cid(data.get("customer_events", []))

    # HOW EACH ACCOUNT PAYS. A supplier knows its own billing arrangement for its own customers --
    # it is the most ordinary CRM field there is -- so it belongs on the record here rather than
    # being fetched at decision time. Read once through the approved seam
    # (`company/interfaces/sim_interface.py`), which is the only route by which anything about the
    # world reaches the company.
    #
    # THIS FIELD IS WHY R1's SEAM WAS DOING NOTHING. `enriched_churn_estimate` gained a
    # `payment_method` argument in 99d2befb4 and the live path never passed one, so the factor
    # defaulted to 1.0 on every real decision: the observable crossed the wall and stopped.
    _seam = _live_seam()
    customers = []
    for cid in active_ids:
        pc = per_customer.get(cid, {})
        ev = last_renewals.get(cid, {})
        last_date = ev.get("event_date")
        current_rate = ev.get("unit_rate_gbp_per_mwh") or pc.get("tariff_max_gbp_per_mwh", 0.0)
        next_renewal = _estimate_next_renewal(last_date) if last_date else None
        hf_data = hedge_fractions.get(cid, {})
        customers.append({
            "cid": cid,
            "commodity": pc.get("commodity", "electricity"),
            "segment": data.get("per_customer_lifetime", {}).get(cid, {}).get("segment", "unknown"),
            "current_rate_gbp_per_mwh": round(current_rate, 4) if current_rate else None,
            "last_renewal_date": last_date,
            "next_renewal_estimate": next_renewal,
            "eac_kwh_per_year": _estimate_eac(cid, per_customer, data),
            "hedge_fraction": round(hf_data.get("avg_hf", 0.0), 4),
            "net_gbp_2025": round(pc.get("net_gbp", 0.0), 2),
            "payment_method": _payment_method(_seam, cid, pc.get("commodity", "electricity")),
        })

    portfolio = {
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_year": int(last_year_key) if last_year_key else None,
        "treasury_gbp": round(treasury_end, 2),
        "active_customer_count": len(active_ids),
        "customers": customers,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(portfolio, indent=2))
    return portfolio


def _estimate_eac(cid: str, per_customer: dict, data: dict) -> float | None:
    """Rough EAC estimate: annual revenue / tariff rate."""
    pc = per_customer.get(cid, {})
    rate = pc.get("tariff_max_gbp_per_mwh", 0.0)
    rev = pc.get("gross_gbp", 0.0)
    if rate and rate > 0 and rev > 0:
        bills = data.get("bills", [])
        cid_bills = [b for b in bills if b["customer_id"] == cid]
        if cid_bills:
            total_kwh = sum(b.get("total_consumption_kwh", 0.0) for b in cid_bills)
            months = len(set(b.get("period_start", "")[:7] for b in cid_bills))
            if months > 0:
                return round(total_kwh / months * 12, 0)
    return None


if __name__ == "__main__":
    p = generate()
    print(f"Generated live_portfolio.json: {p['active_customer_count']} customers, treasury GBP{p['treasury_gbp']:,.0f}")
