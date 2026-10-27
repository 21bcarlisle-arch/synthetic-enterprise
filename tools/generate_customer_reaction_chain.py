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

Also the move-out, its final bill, and for a change-of-tenancy (`OCC-`) account the account it
succeeded at the same meter point (`docs/market_research/home_moves.md` §8.8).

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
LEDGER_PATH = PROJECT / "docs" / "state" / "billing_ledger.json"
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"

_PHYSICAL_EVENTS = {
    "solar_install", "ev_acquired", "heat_pump_installed",
    "battery_installed", "insulation_upgraded", "smart_meter_installed",
    "boiler_replaced",
}
_ECONOMIC_EVENTS = {
    "job_loss", "reemployed", "income_scar_ended", "income_recovery", "new_baby", "retirement_starts",
}


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


#: Other arrivals that move a home's electricity, so a year either side of the car that holds one
#: cannot be read as the car's.
_ELECTRICITY_CONFOUNDERS = {"solar_install", "heat_pump_installed", "battery_installed"}


def _months_either_side(event_date, n=12):
    y, m = int(event_date[:4]), int(event_date[5:7])
    after = ["{}-{:02d}".format(y + (m + k - 1) // 12, (m + k - 1) % 12 + 1) for k in range(1, n + 1)]
    before = ["{}-{:02d}".format(y + (m - k - 1) // 12, (m - k - 1) % 12 + 1) for k in range(1, n + 1)]
    return before, after


def _ev_effect(commodity, is_dual_fuel, monthly, event_date, timeline):
    """A car charges on the home's electricity, so this account reads its effect only if it is
    the electricity leg, over the twelve whole months either side of the arrival month (each side
    holds every season once). The household still has an electricity supply when we hold only its
    gas -- the car is real, the effect is just not ours to see
    (`docs/market_research/ev_charging_and_the_saving_against_petrol_and_diesel_2026-10-25.md` s.10).
    Not weather-normalised (GAP): a colder year on one side moves the difference."""
    if not event_date:
        return None
    if commodity != "electricity":
        if is_dual_fuel:
            return "Read on this household's electricity account, not its gas"
        return "Not observable by us: the car charges on an electricity supply we do not hold"
    before, after = _months_either_side(event_date)
    mon = {m["month"]: m.get("kwh") or 0.0 for m in monthly or []}
    if not mon or event_date[:7] > max(mon):
        return "Not observable by us: the car arrived after we stopped supplying this home"
    if event_date[:7] < min(mon):
        return "Not observable by us: the car arrived before we supplied this home"
    if not all(x in mon for x in before + after):
        return "Not observable by us: we hold no full year of its electricity either side of the car"
    lo_month, hi_month = before[0], after[-1]
    if any(e.get("type") == "life_event" and e.get("date")
           and lo_month <= e["date"][:7] <= hi_month
           and (e.get("detail") or "").lower().replace(" ", "_") in _ELECTRICITY_CONFOUNDERS
           for e in timeline):
        return ("Not separable by us: another electrical arrival falls in the year either side "
                "of the car")
    from tools.generate_explore_cast import EV_ADDED_KWH_BAND
    yr_before = sum(mon[x] for x in before)
    yr_after = sum(mon[x] for x in after)
    if yr_before <= 0:
        return None
    added = yr_after - yr_before
    lo, hi = EV_ADDED_KWH_BAND
    band = ("within" if lo <= added <= hi else "outside") + \
        " the {:,.0f}-{:,.0f} kWh a year an EV adds at home".format(lo, hi)
    return ("Electricity moved {:+.0f}% over the 12 months after the car against the 12 before "
            "(avg {:.0f} kWh/mo -> {:.0f} kWh/mo, {:+,.0f} kWh a year, {}; not weather-normalised)"
            ).format(added / yr_before * 100, yr_before / 12, yr_after / 12, added, band)


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


def _add_effects(timeline, invoices, consumption_monthly, pcb_entry, commodity=None, is_dual_fuel=False):
    for ev in timeline:
        detail = ev.get("detail", "")
        etype = ev.get("type")
        date = ev.get("date")
        effect = None
        if etype == "renewed":
            effect = _renewal_effect(invoices, date, ev.get("commodity"))
        elif etype == "life_event":
            slug = detail.lower().replace(" ", "_")
            if slug == "ev_acquired":
                effect = _ev_effect(commodity, is_dual_fuel, consumption_monthly, date, timeline)
            elif slug in _PHYSICAL_EVENTS:
                effect = _usage_effect(consumption_monthly, date)
            elif slug in _ECONOMIC_EVENTS:
                effect = _economic_effect(
                    pcb_entry.get("income_stress_trajectory"),
                    pcb_entry.get("payment_miss_trajectory"),
                    date,
                )
        if effect:
            ev["effect"] = effect
        elif etype == "life_event":
            ev.pop("effect", None)
    return timeline


#: The timeline entries this module writes, removed before each write so a re-run never doubles them.
_MOVE_EVENT_TYPES = {"moved_out", "final_bill"}


def _move_out_events(cid, move_outs, final_bills):
    """A move-out and the final bill that closed it, from the run's move-out register and the
    supplier's own bills (home_moves.md §8.8). A final bill with no move is a departure's."""
    events = []
    for m in move_outs or []:
        if m.get("customer_id") == cid:
            events.append({"type": "moved_out", "date": m["move_date"], "detail": "Moved out",
                           "commodity": m.get("commodity")})
    for b in final_bills.get(cid, []):
        basis = b.get("billing_basis")
        events.append({
            "type": "final_bill", "date": b.get("issue_date") or b["period_end"],
            "detail": "Final bill", "commodity": b.get("commodity"),
            "effect": "Closing read {}; billed £{:.2f}".format(
                basis or "not recorded", b.get("total_amount_gbp") or 0.0),
        })
    return events


def _predecessor(cid, successions):
    """For a change-of-tenancy account, the account it succeeded at the same meter point, or None
    with the reason. Only an `OCC-` account has one."""
    if not cid.startswith("OCC-"):
        return None, None
    if successions is None:
        return None, "the run predates occupier_successions"
    for s in successions:
        if s.get("account_id") == cid:
            return s.get("predecessor_account_id"), None
    return None, "the run lists no succession for this account"


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

    # The company desk's collections journeys, keyed by the account the triad posts to (`ACC-<cid>`,
    # one per fuel leg). Absent from a run published before the report carried them.
    journeys_by_account = {}
    for j in run.get("collections_journeys") or []:
        journeys_by_account.setdefault(j.get("account_id"), []).append(j)

    move_outs = run.get("home_move_outs")
    successions = run.get("occupier_successions")
    final_bills = {}
    for b in run.get("bills") or []:
        if b.get("final_bill"):
            final_bills.setdefault(b["customer_id"], []).append(b)

    count = 0
    for cust_file in sorted(CUSTOMERS_DIR.glob("*.json")):
        if cust_file.name == "_index.json":
            continue
        cid = cust_file.stem
        obj = json.loads(cust_file.read_text())
        base = _base_id(cid)

        timeline = [e for e in obj.get("timeline", []) if e.get("type") not in _MOVE_EVENT_TYPES]
        timeline = sorted(timeline + _move_out_events(cid, move_outs, final_bills),
                          key=lambda e: e.get("date") or "")
        predecessor, why_not = _predecessor(cid, successions)
        if cid.startswith("OCC-"):
            obj["predecessor_account_id"] = predecessor
            obj["predecessor_unavailable_because"] = why_not
        obj["timeline"] = _add_effects(
            timeline,
            obj.get("invoices", []),
            obj.get("consumption", {}).get("monthly", []),
            pcb.get(base, {}),
            commodity=obj.get("commodity"),
            # A dual household's gas file is `<cid>g` and carries is_dual_fuel False on itself.
            is_dual_fuel=bool(obj.get("is_dual_fuel")) or base != cid,
        )

        from company.analytics.decision_event_ledger import build_customer_ledger
        obj["reaction_chain"] = build_customer_ledger(
            base, events, retention, journey_log, ledger_customers.get(cid),
            collections_journeys=journeys_by_account.get("ACC-" + cid, []),
        )

        cust_file.write_text(json.dumps(obj, indent=2))
        count += 1

    print("Updated", count, "customers with timeline effects + reaction_chain")
    return count


if __name__ == "__main__":
    generate(sys.argv[1] if len(sys.argv) > 1 else None)
