#!/usr/bin/env python3
"""CUSTOMER_360_REDESIGN.md v4 items 3 (events perturb the chain) and 4
(reaction closes the loop).

Item 3: each timeline entry gets a real, numeric "effect" -- what did this
event actually cause, using data the sim/company layers already compute
(no fabrication): physical life events (solar/EV/heat-pump/battery/
insulation/smart-meter) diff the household's own metered consumption
before/after; economic life events (job loss/income recovery/retirement/
new baby) read the real income-stress-trajectory step and payment-miss
drift already tracked per customer; renewals read the real unit-rate step
already patched into invoices by generate_invoice_data.py. Events with no
wired downstream mechanism in the sim (e.g. "home move") are left without
an effect rather than inventing one.

Item 4: reuses company/analytics/decision_event_ledger.build_customer_ledger
(already built for the Phase QP shadow case study) as the reaction-chain
data source -- bill-shock/journey-state/retention-decision/outcome/arrears
events, cause-linked, real EV numbers -- instead of new plumbing.

Output: patches "effect" onto existing timeline entries and adds a new
"reaction_chain" key into each site/data/customers/{cid}.json (same
read-existing/patch-key pattern as generate_invoice_data.py and
generate_customer_consumption.py). Must run after generate_customer_data,
generate_billing_ledger and generate_invoice_data, and generate_customer_consumption.
"""
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
LEDGER_PATH = PROJECT / "site" / "state" / "billing_ledger.json"
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"

_PHYSICAL_EVENTS = {
    "solar_install", "ev_acquired", "heat_pump_installed",
    "battery_installed", "insulation_upgraded", "smart_meter_installed",
    "boiler_replaced",
}
_ECONOMIC_EVENTS = {"job_loss", "income_recovery", "new_baby", "retirement_starts"}


def _base_id(cid):
    if cid.endswith("g") and len(cid) > 1:
        candidate = cid[:-1]
        if candidate:
            return candidate
    return cid


def _usage_effect(monthly, event_date):
    """Average kWh in the 3 months before vs the 3 months after event_date,
    from this account's own metered consumption -- real, not modelled."""
    if not monthly or not event_date:
        return None
    before = [m["kwh"] for m in monthly if m["month"] < event_date[:7]][-3:]
    after = [m["kwh"] for m in monthly if m["month"] >= event_date[:7]][:3]
    if len(before) < 2 or len(after) < 2:
        return None
    avg_before = sum(before) / len(before)
    avg_after = sum(after) / len(after)
    if avg_before <= 0:
        return None
    pct = (avg_after - avg_before) / avg_before * 100
    return "Usage moved {:+.0f}% (avg {:.0f} kWh/mo -> {:.0f} kWh/mo)".format(
        pct, avg_before, avg_after
    )


def _economic_effect(trajectory_stress, trajectory_miss, event_date):
    """Real income-stress-trajectory step and payment-miss drift around the
    event's year -- from company/crm's own tracked signals, not invented."""
    if not event_date:
        return None
    year = int(event_date[:4])
    stress_by_year = {t["year"]: t["stress"] for t in (trajectory_stress or [])}
    miss_by_year = {t["year"]: t for t in (trajectory_miss or [])}
    s_before, s_after = stress_by_year.get(year - 1), stress_by_year.get(year)
    m_before, m_after = miss_by_year.get(year - 1), miss_by_year.get(year)
    parts = []
    if s_before and s_after and s_before != s_after:
        parts.append("income stress {} -> {}".format(s_before, s_after))
    if m_before and m_after and m_before.get("total"):
        rate_before = m_before.get("late", 0) / m_before["total"]
        rate_after = m_after.get("late", 0) / max(m_after.get("total", 1), 1)
        if abs(rate_after - rate_before) > 1e-9:
            parts.append(
                "late-payment rate {:.0%} -> {:.0%}".format(rate_before, rate_after)
            )
    if not parts:
        return None
    return "Real downstream drift: " + "; ".join(parts)


def _renewal_effect(invoices, event_date, commodity):
    """Real unit-rate step either side of the renewal, from this account's
    own invoices (already patched from billing_ledger.json)."""
    if not invoices or not event_date:
        return None
    before = [i for i in invoices if i["date"] < event_date and i.get("unit_rate_p_per_kwh")]
    after = [i for i in invoices if i["date"] >= event_date and i.get("unit_rate_p_per_kwh")]
    if not before or not after:
        return None
    rate_before = before[-1]["unit_rate_p_per_kwh"]
    rate_after = after[0]["unit_rate_p_per_kwh"]
    if rate_before == rate_after:
        return None
    return "Unit rate stepped {:.2f}p/kWh -> {:.2f}p/kWh".format(rate_before, rate_after)


def _add_effects(timeline, invoices, consumption_monthly, pcb_entry):
    for ev in timeline:
        detail = ev.get("detail", "")
        etype = ev.get("type")
        date = ev.get("date")
        effect = None
        if etype == "renewed":
            effect = _renewal_effect(invoices, date, ev.get("commodity"))
        elif etype == "life_event":
            slug = detail.lower().replace(" ", "_")
            if slug in _PHYSICAL_EVENTS:
                effect = _usage_effect(consumption_monthly, date)
            elif slug in _ECONOMIC_EVENTS:
                effect = _economic_effect(
                    pcb_entry.get("income_stress_trajectory"),
                    pcb_entry.get("payment_miss_trajectory"),
                    date,
                )
        if effect:
            ev["effect"] = effect
    return timeline


def generate(run_json_path=None):
    path = Path(run_json_path) if run_json_path else RUN_OUTPUT
    if not path.exists() or not LEDGER_PATH.exists():
        print("Skipped: missing run output or billing ledger")
        return 0

    from tools.generate_dashboard_data import extract_customers

    run = json.loads(path.read_text())
    ledger = json.loads(LEDGER_PATH.read_text())
    ledger_customers = ledger.get("customers", {})
    pcb = run.get("per_customer_behavioral", {})
    dash_customers = extract_customers(run)
    events, retention, journey_log = (
        dash_customers["events"], dash_customers["retention"], dash_customers["journey_log"],
    )

    count = 0
    for cust_file in sorted(CUSTOMERS_DIR.glob("*.json")):
        if cust_file.name == "_index.json":
            continue
        cid = cust_file.stem
        obj = json.loads(cust_file.read_text())
        base = _base_id(cid)

        obj["timeline"] = _add_effects(
            obj.get("timeline", []),
            obj.get("invoices", []),
            obj.get("consumption", {}).get("monthly", []),
            pcb.get(base, {}),
        )

        from company.analytics.decision_event_ledger import build_customer_ledger
        obj["reaction_chain"] = build_customer_ledger(
            base, events, retention, journey_log, ledger_customers.get(cid)
        )

        cust_file.write_text(json.dumps(obj, indent=2))
        count += 1

    print("Updated", count, "customers with timeline effects + reaction_chain")
    return count


if __name__ == "__main__":
    generate(sys.argv[1] if len(sys.argv) > 1 else None)
