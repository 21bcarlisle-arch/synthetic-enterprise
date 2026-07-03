import json
import pathlib
import datetime

PROJECT = pathlib.Path(__file__).resolve().parent.parent


def generate(run_json_path=None, out_path=None):
    if run_json_path is None:
        run_json_path = PROJECT / "docs" / "reports" / "run_output_latest.json"
    if out_path is None:
        out_path = PROJECT / "site" / "data" / "supplier.json"

    data = json.loads(pathlib.Path(run_json_path).read_text())
    years_data = data.get("years", {})

    years_summary = []
    for yr_str in sorted(years_data.keys()):
        yr = years_data[yr_str]
        years_summary.append({
            "year": int(yr_str),
            "revenue_gbp": round(yr.get("revenue_gbp", 0), 0),
            "gross_gbp": round(yr.get("gross_gbp", 0), 0),
            "net_gbp": round(yr.get("net_gbp", 0), 0),
            "bad_debt_gbp": round(yr.get("bad_debt_gbp", 0), 0),
            "treasury_end_gbp": round(yr.get("treasury_end_gbp", 0), 0),
            "active_customers": len(yr.get("active_customer_ids", [])),
            "policy_cost_gbp": round(yr.get("policy_cost_gbp", 0), 0),
            "network_cost_gbp": round(yr.get("network_cost_gbp", 0), 0),
            "segment_split": yr.get("segment_split", {}),
            "commodity_split": yr.get("commodity_split", {}),
        })

    result = {
        "generated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "simulation_window": "2016-2025",
        "portfolio_summary": {
            "total_revenue_gbp": round(data.get("total_revenue_gbp", 0), 0),
            "total_gross_gbp": round(data.get("total_gross_gbp", 0), 0),
            "total_net_gbp": round(data.get("total_net_gbp", 0), 0),
            "total_bad_debt_gbp": round(data.get("total_bad_debt_gbp", 0), 0),
            "final_treasury_gbp": round(data.get("final_treasury_gbp", 0), 0),
            "enterprise_value_gbp": round(data.get("enterprise_value_gbp", 0), 0),
            "cost_to_serve_portfolio_gbp": round(data.get("cost_to_serve_portfolio_gbp", 0), 0),
        },
        "years": years_summary,
        "fra_ratio_series": data.get("fra_ratio_series", []),
    }

    out = pathlib.Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    generate()
