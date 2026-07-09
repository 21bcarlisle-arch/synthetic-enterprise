#!/usr/bin/env python3
"""Generate per-customer site data with dual-fuel combined views and enriched metrics."""
import hashlib
import json, sys
from pathlib import Path
from collections import defaultdict

PROJECT = Path(__file__).resolve().parent.parent
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_DIR = PROJECT / "site" / "data" / "customers"

# GB electricity distributor (DNO) IDs actually in use (Elexon MPAS convention).
_DNO_IDS = ["10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]


def _digest_int(seed, n):
    """First n digits of a deterministic hash of seed -- a display identifier,
    not a claim about simulation internals (same status as account_id itself)."""
    h = hashlib.sha256(seed.encode()).hexdigest()
    return str(int(h, 16))[:n].zfill(n)


def _mpan_check_digit(core8):
    """Published Elexon modulus-11 check-digit algorithm for the MPAN core ID."""
    weights = [3, 5, 7, 13, 17, 19, 23, 29]
    total = sum(int(d) * w for d, w in zip(core8, weights))
    return str((total % 11) % 10)


def _mpan(account_id, segment):
    """MPAN bottom line (11 digits): DNO(2) + unique ref(8) + check digit(1),
    plus a top line of profile class(2) + meter timeswitch(2) + line loss factor(3)."""
    profile_class = "05" if segment == "I&C" else "01"
    meter_timeswitch = "00"
    line_loss_factor = _digest_int(account_id + "-llf", 3)
    dno = _DNO_IDS[int(hashlib.sha256(account_id.encode()).hexdigest(), 16) % len(_DNO_IDS)]
    core8 = _digest_int(account_id + "-core", 8)
    check = _mpan_check_digit(core8)
    return {
        "top_line": profile_class + meter_timeswitch + line_loss_factor,
        "bottom_line": dno + core8 + check,
    }


def _mprn(account_id):
    """MPRN: gas supply point identifier, 6-10 digits, no public checksum standard."""
    return _digest_int(account_id + "-mprn", 8)


def _tariff(segment, commodity):
    if segment == "I&C":
        return "Half-Hourly Industrial and Commercial"
    return "Standard Variable (" + commodity.capitalize() + ")"


def _meter(cid, segment):
    """Customer-facing meter type label.

    Was a hardcoded "HH for I&C, else always Smart" placeholder -- every
    non-I&C customer showed "Smart" regardless of their real status. That's
    exactly what let C1 display a "Smart" label while its actual meter-read
    data (site's Timeline/bills) behaved like a traditional meter: C1's
    saas.customers record carried no smart_meter flag at all, so
    simulation.meter_reads.meter_type_for_customer() silently defaulted it to
    "traditional" (Rich-flagged 2026-07-09; root cause fixed in
    saas/customers.py the same session -- this closes the matching label-side
    half of the same class of bug, not just C1's instance).
    """
    if segment == "I&C":
        return "HH"
    from saas.customers import get_customer
    from simulation.meter_reads import meter_type_for_customer
    record = get_customer(cid)
    if record is None:
        return "Traditional"
    return "Smart" if meter_type_for_customer(record) == "smart" else "Traditional"


def _base_id(cid):
    """Strip gas suffix: C1g -> C1, C_IC3g -> C_IC3."""
    if cid.endswith("g") and len(cid) > 1:
        candidate = cid[:-1]
        if candidate:
            return candidate
    return cid


_EVENT_LABELS = {
    "renewed": "Tariff renewed",
    "churned": "Churned",
}


def _timeline(run, base):
    """Household-level timeline: real renewal/churn events (customer_events,
    electricity-metered) + real life events (per_customer_behavioral), merged
    and sorted. No fabrication -- both sources already exist in the run
    artifact; this just assembles them per household for display."""
    events = []
    ce = run.get("customer_events", [])
    for e in ce:
        if e.get("customer_id") not in (base, base + "g"):
            continue
        etype = e.get("event_type")
        label = _EVENT_LABELS.get(etype, etype)
        rate = e.get("unit_rate_gbp_per_mwh")
        detail = label
        if etype == "renewed" and rate is not None:
            detail = label + " at " + str(round(rate, 0)) + " £/MWh"
        events.append({
            "date": e.get("event_date"),
            "type": etype,
            "commodity": e.get("commodity"),
            "detail": detail,
        })
    pcb = run.get("per_customer_behavioral", {})
    for life in pcb.get(base, {}).get("life_event_history", []):
        events.append({
            "date": life.get("date"),
            "type": "life_event",
            "commodity": None,
            "detail": life.get("event_type", "").replace("_", " ").capitalize(),
        })
    events.sort(key=lambda e: e.get("date") or "")
    return events


def _per_year_data(run, cid):
    """Collect per-year net/gross/revenue for a single customer."""
    years_out = []
    for yr in sorted(run.get("years", {}).keys()):
        ydata = run["years"][yr]
        per_cust = ydata.get("per_customer", {})
        cdata = per_cust.get(cid, {})
        if cdata:
            years_out.append({
                "year": int(yr),
                "revenue_gbp": round(cdata.get("revenue_gbp", 0), 2),
                "gross_gbp": round(cdata.get("gross_gbp", 0), 2),
                "net_gbp": round(cdata.get("net_gbp", 0), 2),
                "tariff_min": round(cdata.get("tariff_min_gbp_per_mwh", 0), 2),
                "tariff_max": round(cdata.get("tariff_max_gbp_per_mwh", 0), 2),
            })
    return years_out


def generate(run_json_path=None):
    path = Path(run_json_path) if run_json_path else RUN_OUTPUT
    run = json.loads(path.read_text())
    pcl = run.get("per_customer_lifetime", {})
    bba = run.get("by_billing_account", {})
    comm_pnl = run.get("per_cid_comm_pnl", {})

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    written = []
    for cid, cdata in pcl.items():
        segment = cdata.get("segment", "resi")
        commodity = cdata.get("commodity", "electricity")
        base = _base_id(cid)
        is_gas = cid.endswith("g") and cid != base

        # CLV / churn from by_billing_account (electricity account only)
        clv_data = bba.get(base, {}) if not is_gas else {}
        clv_gbp = round(clv_data.get("clv_gbp", 0), 2)
        churn_p = round(clv_data.get("latest_churn_probability", 0), 3)

        # Commodity-level P&L split
        comm = comm_pnl.get(cid, {})
        elec_comm = comm.get("electricity", {})
        gas_comm = comm.get("gas", {})

        # Dual-fuel companion account
        gas_id = base + "g"
        has_dual_fuel = (gas_id in pcl) and (not is_gas)
        gas_lifetime = pcl.get(gas_id, {}) if has_dual_fuel else None

        obj = dict(
            account_id=cid,
            base_account_id=base,
            segment=segment,
            commodity=commodity,
            is_dual_fuel=has_dual_fuel,
            acquisition_date=cdata.get("acquisition_date", "2016-01-01"),
            tariff_name=_tariff(segment, commodity),
            meter_type=_meter(cid, segment),
            mpan=(_mpan(cid, segment) if commodity == "electricity" else None),
            mprn=(_mprn(cid) if commodity == "gas" else None),
            lifetime_revenue_gbp=round(cdata.get("revenue_gbp", 0), 2),
            lifetime_gross_gbp=round(cdata.get("gross_gbp", 0), 2),
            lifetime_net_gbp=round(cdata.get("net_gbp", 0), 2),
            lifetime_net_after_cts_gbp=round(
                cdata.get("net_margin_after_cost_to_serve_gbp", 0), 2),
            cost_to_serve_gbp=round(cdata.get("cost_to_serve_gbp", 0), 2),
            pricing_action=cdata.get("pricing_action", "NONE"),
            clv_gbp=clv_gbp,
            churn_probability=churn_p,
            expected_lifetime_periods=round(clv_data.get("expected_lifetime_periods", 0), 2),
            commodity_split={
                "electricity": {
                    "net_gbp": round(elec_comm.get("net", 0), 2),
                    "revenue_gbp": round(elec_comm.get("revenue", 0), 2),
                } if elec_comm else None,
                "gas": {
                    "net_gbp": round(gas_comm.get("net", 0), 2),
                    "revenue_gbp": round(gas_comm.get("revenue", 0), 2),
                } if gas_comm else None,
            },
            dual_fuel_combined=(
                {
                    "gas_account_id": gas_id,
                    "gas_lifetime_net_gbp": round(gas_lifetime.get("net_gbp", 0), 2),
                    "gas_lifetime_revenue_gbp": round(gas_lifetime.get("revenue_gbp", 0), 2),
                    "combined_net_gbp": round(
                        cdata.get("net_gbp", 0) + gas_lifetime.get("net_gbp", 0), 2
                    ),
                    "combined_revenue_gbp": round(
                        cdata.get("revenue_gbp", 0) + gas_lifetime.get("revenue_gbp", 0), 2
                    ),
                }
                if (has_dual_fuel and gas_lifetime)
                else None
            ),
            annual_pnl=_per_year_data(run, cid),
            timeline=_timeline(run, base),
            invoices=[],
        )
        (OUT_DIR / (cid + ".json")).write_text(json.dumps(obj, indent=2))
        written.append(cid)

    index = sorted(pcl.keys())
    (OUT_DIR / "_index.json").write_text(json.dumps(index))
    print("Generated", len(written), "customer files in", str(OUT_DIR))
    return index


if __name__ == "__main__":
    generate(sys.argv[1] if len(sys.argv) > 1 else None)
