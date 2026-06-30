#!/usr/bin/env python3
"""Generate per-customer site data with dual-fuel combined views and enriched metrics."""
import json, sys
from pathlib import Path
from collections import defaultdict

PROJECT = Path(__file__).resolve().parent.parent
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_DIR = PROJECT / "site" / "data" / "customers"


def _tariff(segment, commodity):
    if segment == "I&C":
        return "Half-Hourly Industrial and Commercial"
    return "Standard Variable (" + commodity.capitalize() + ")"


def _meter(segment):
    return "HH" if segment == "I&C" else "Smart"


def _base_id(cid):
    """Strip gas suffix: C1g -> C1, C_IC3g -> C_IC3."""
    if cid.endswith("g") and len(cid) > 1:
        candidate = cid[:-1]
        if candidate:
            return candidate
    return cid


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
            meter_type=_meter(segment),
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
