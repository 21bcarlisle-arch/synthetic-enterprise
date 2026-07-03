import json
import pathlib
import datetime

PROJECT = pathlib.Path(__file__).resolve().parent.parent


def _base_id(cid: str) -> str:
    if cid.endswith("g") and len(cid) > 1:
        return cid[:-1]
    return cid


def generate(run_json_path=None, out_path=None):
    if run_json_path is None:
        run_json_path = PROJECT / "docs" / "reports" / "run_output_latest.json"
    if out_path is None:
        out_path = PROJECT / "site" / "data" / "customers.json"

    data = json.loads(pathlib.Path(run_json_path).read_text())
    pcl = data.get("per_customer_lifetime", {})
    bills = data.get("bills", [])

    bill_agg = {}
    for bill in bills:
        cid = bill["customer_id"]
        kwh = bill.get("total_consumption_kwh", 0) or 0
        rate = bill.get("average_unit_rate_gbp_per_mwh", 0) or 0
        if cid not in bill_agg:
            bill_agg[cid] = {"total_kwh": 0.0, "bill_count": 0, "rate_x_kwh": 0.0}
        bill_agg[cid]["total_kwh"] += kwh
        bill_agg[cid]["bill_count"] += 1
        bill_agg[cid]["rate_x_kwh"] += rate * kwh

    groups = {}
    for cid, lifetime in pcl.items():
        base = _base_id(cid)
        if base not in groups:
            groups[base] = {}
        commodity = lifetime.get("commodity", "electricity")
        agg = bill_agg.get(cid, {})
        total_kwh = agg.get("total_kwh", 0.0)
        rate_x_kwh = agg.get("rate_x_kwh", 0.0)
        groups[base][commodity] = {
            "cid": cid,
            "commodity": commodity,
            "segment": lifetime.get("segment", "unknown"),
            "acquisition_date": lifetime.get("acquisition_date", ""),
            "revenue_gbp": round(lifetime.get("revenue_gbp", 0), 2),
            "gross_gbp": round(lifetime.get("gross_gbp", 0), 2),
            "capital_gbp": round(lifetime.get("capital_gbp", 0), 2),
            "net_gbp": round(lifetime.get("net_gbp", 0), 2),
            "cost_to_serve_gbp": round(lifetime.get("cost_to_serve_gbp", 0), 2),
            "total_kwh": round(total_kwh, 0),
            "avg_rate_gbp_per_mwh": round(rate_x_kwh / total_kwh if total_kwh > 0 else 0, 2),
            "bill_count": agg.get("bill_count", 0),
        }

    customers = []
    for base_id in sorted(groups.keys()):
        legs = groups[base_id]
        first = next(iter(legs.values()))
        combined = {
            "revenue_gbp": round(sum(l["revenue_gbp"] for l in legs.values()), 2),
            "gross_gbp": round(sum(l["gross_gbp"] for l in legs.values()), 2),
            "capital_gbp": round(sum(l["capital_gbp"] for l in legs.values()), 2),
            "net_gbp": round(sum(l["net_gbp"] for l in legs.values()), 2),
            "cost_to_serve_gbp": round(sum(l["cost_to_serve_gbp"] for l in legs.values()), 2),
            "total_kwh": round(sum(l["total_kwh"] for l in legs.values()), 0),
        }
        customers.append({
            "customer_group": base_id,
            "segment": first["segment"],
            "acquisition_date": first["acquisition_date"],
            "fuels": sorted(legs.keys()),
            "legs": legs,
            "combined": combined,
        })

    result = {
        "generated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "customer_count": len(customers),
        "customers": customers,
    }

    out = pathlib.Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    generate()
