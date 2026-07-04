"""Daily live decision engine -- produces timestamped decision log for paper-trading.

As-of date: last available SSP data (2025-06-07). Portfolio: frozen at final simulation
state. Decisions are timestamped with today real date + as-of context for reproducibility.
"""
import json, datetime as dt
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
PORTFOLIO_PATH = PROJECT / "site" / "state" / "live_portfolio.json"
LIVE_DECISIONS_DIR = PROJECT / "site" / "state"
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"

_RENEWAL_WINDOW_DAYS = 60
_HEDGE_MIN = 0.50
_HEDGE_MAX = 0.90
_NON_COMMODITY_ELEC_GBP_MWH = 52.0
_NON_COMMODITY_GAS_GBP_MWH = 8.0
_SVT_PREMIUM = 1.15
_SEGMENT_MARGINS = {
    "resi": 28.0, "sme": 22.0, "I&C": 12.0, "unknown": 18.0
}

def _load_portfolio():
    return json.loads(PORTFOLIO_PATH.read_text())

def _load_run_output():
    try: return json.loads(RUN_OUTPUT.read_text())
    except: return {}

def _days_until(renewal_str, as_of_str):
    if not renewal_str: return None
    r = dt.date.fromisoformat(renewal_str)
    a = dt.date.fromisoformat(as_of_str)
    return (r - a).days

def _hedge_recommendation(customers):
    below = [c["cid"] for c in customers if c.get("hedge_fraction", 0) < _HEDGE_MIN]
    above = [c["cid"] for c in customers if c.get("hedge_fraction", 0) > _HEDGE_MAX]
    if below: return "INCREASE", below
    if above: return "REDUCE", above
    return "HOLD", []

def _renewal_flags(customers, as_of_date, elec_fwd, gas_fwd):
    flags = []
    for c in customers:
        days = _days_until(c.get("next_renewal_estimate"), as_of_date)
        if days is None: continue
        if days < 0 or days > _RENEWAL_WINDOW_DAYS: continue
        fuel = c.get("commodity", "electricity")
        fwd = gas_fwd if fuel == "gas" else elec_fwd
        seg = c.get("segment", "unknown")
        margin = _SEGMENT_MARGINS.get(seg, 18.0)
        non_comm = _NON_COMMODITY_GAS_GBP_MWH if fuel == "gas" else _NON_COMMODITY_ELEC_GBP_MWH
        proposed = round(fwd + non_comm + margin, 2)
        svt = round(fwd * _SVT_PREMIUM, 2)
        eac = c.get("eac_kwh_per_year") or 0
        flags.append({
            "cid": c["cid"],
            "segment": seg,
            "commodity": fuel,
            "days_to_renewal": days,
            "renewal_date": c["next_renewal_estimate"],
            "current_rate_gbp_per_mwh": c.get("current_rate_gbp_per_mwh"),
            "proposed_rate_gbp_per_mwh": proposed,
            "svt_approx_gbp_per_mwh": svt,
            "eac_kwh": eac,
            "expected_gross_margin_gbp_pa": round(margin * eac / 1000, 2) if eac else None,
        })
    return sorted(flags, key=lambda x: x["days_to_renewal"])

def _acquisition_prices(elec_fwd, gas_fwd):
    return {
        "resi_elec_gbp_per_mwh": round(elec_fwd + _NON_COMMODITY_ELEC_GBP_MWH + _SEGMENT_MARGINS["resi"], 2),
        "sme_elec_gbp_per_mwh": round(elec_fwd + _NON_COMMODITY_ELEC_GBP_MWH + _SEGMENT_MARGINS["sme"], 2),
        "ic_elec_gbp_per_mwh": round(elec_fwd + _NON_COMMODITY_ELEC_GBP_MWH + _SEGMENT_MARGINS["I&C"], 2),
        "ic_gas_gbp_per_mwh": round(gas_fwd + _NON_COMMODITY_GAS_GBP_MWH + _SEGMENT_MARGINS["I&C"], 2),
    }

def run_decisions(portfolio_path=None, run_output_path=None, out_dir=None, market_adapter=None):
    from tools.market_adapters import get_market_adapter
    port_path = Path(portfolio_path) if portfolio_path else PORTFOLIO_PATH
    out = Path(out_dir) if out_dir else LIVE_DECISIONS_DIR
    portfolio = json.loads(port_path.read_text())
    adapter = market_adapter if market_adapter is not None else get_market_adapter()
    market = adapter.get_market_summary()
    as_of = market["as_of_date"]
    elec_fwd = market["elec_12m_forward_gbp_per_mwh"]
    gas_fwd = market["gas_12m_forward_gbp_per_mwh"]
    customers = portfolio.get("customers", [])
    hedge_rec, hedge_affected = _hedge_recommendation(customers)
    flags = _renewal_flags(customers, as_of, elec_fwd, gas_fwd)
    acq = _acquisition_prices(elec_fwd, gas_fwd)
    decision = {
        "decision_run_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "portfolio_as_of": portfolio.get("generated_at"),
        "market_as_of_date": as_of,
        "elec_spot_gbp_per_mwh": market["elec_spot_gbp_per_mwh"],
        "gas_spot_gbp_per_mwh": market["gas_spot_gbp_per_mwh"],
        "elec_12m_forward_gbp_per_mwh": elec_fwd,
        "gas_12m_forward_gbp_per_mwh": gas_fwd,
        "treasury_gbp": portfolio.get("treasury_gbp"),
        "active_customers": portfolio.get("active_customer_count"),
        "hedge_recommendation": hedge_rec,
        "hedge_affected_customers": hedge_affected,
        "renewal_window_days": _RENEWAL_WINDOW_DAYS,
        "renewal_flags": flags,
        "acquisition_prices": acq,
    }
    out.mkdir(parents=True, exist_ok=True)
    date_tag = as_of.replace("-", "")
    out_file = out / ("live_decisions_" + date_tag + ".json")
    latest = out / "live_decisions_latest.json"
    out_file.write_text(json.dumps(decision, indent=2))
    latest.write_text(json.dumps(decision, indent=2))
    return decision

if __name__ == "__main__":
    d = run_decisions()
    print("Decision run at:", d["decision_run_at"])
    print("Market as-of:", d["market_as_of_date"])
    print("Elec spot:", d["elec_spot_gbp_per_mwh"])
    print("Elec 12m fwd:", d["elec_12m_forward_gbp_per_mwh"])
    print("Hedge recommendation:", d["hedge_recommendation"])
    print("Renewal flags:", len(d["renewal_flags"]))
    for f in d["renewal_flags"][:3]:
        print(" ", f["cid"], f["days_to_renewal"], "days", f["proposed_rate_gbp_per_mwh"])
    print("Acquisition prices:", d["acquisition_prices"])
