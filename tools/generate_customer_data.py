#!/usr/bin/env python3
import json, sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_DIR = PROJECT / "site" / "data" / "customers"

def _tariff(segment, commodity):
    if segment == "I&C":
        return "Half-Hourly Industrial and Commercial"
    return "Standard Variable (" + commodity.capitalize() + ")"

def _meter(segment):
    return "HH" if segment == "I&C" else "Smart"

def generate(run_json_path=None):
    path = Path(run_json_path) if run_json_path else RUN_OUTPUT
    run = json.loads(path.read_text())
    pcl = run.get("per_customer_lifetime", {})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for cid, cdata in pcl.items():
        segment = cdata.get("segment", "resi")
        commodity = cdata.get("commodity", "electricity")
        obj = dict(
            account_id=cid,
            segment=segment,
            commodity=commodity,
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
            invoices=[],
        )
        (OUT_DIR / (cid + ".json")).write_text(json.dumps(obj, indent=2))
        count += 1
    index = sorted(pcl.keys())
    (OUT_DIR / "_index.json").write_text(json.dumps(index))
    print("Generated", count, "customer files in", str(OUT_DIR))
    return index

if __name__ == "__main__":
    generate(sys.argv[1] if len(sys.argv) > 1 else None)
