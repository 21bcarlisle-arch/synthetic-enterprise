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

_SCENARIO_PROJECTION_MONTHS = 12

_SCENARIO_CONFIGS = {
    "base": {
        "label": "Base (normal OU, long-run mean start)",
        "regime": "normal",
        "seed": 42,
        "gas_start": None,
        "elec_start": None,
    },
    "bull": {
        "label": "Bull (prices below long-run mean — cheap energy)",
        "regime": "normal",
        "seed": 1,
        "gas_start": 35.0,
        "elec_start": 55.0,
    },
    "bear": {
        "label": "Bear (prices above long-run mean — expensive energy)",
        "regime": "normal",
        "seed": 2,
        "gas_start": 92.0,
        "elec_start": 145.0,
    },
    "crisis": {
        "label": "Crisis (high-vol regime forced — 2021-22 style shock)",
        "regime": "crisis",
        "seed": 3,
        "gas_start": 108.0,
        "elec_start": 213.0,
    },
}

SCENARIO_ANALYSIS_PATH = PROJECT / "site" / "state" / "scenario_analysis_latest.json"


def _scenario_market_state(cfg):
    """Return market state for a scenario using the configured starting prices.

    Scenarios represent PERSISTENT price levels (what if prices STAY here for 12 months?),
    not OU projections. Starting prices are the scenario's sustained market level.
    """
    from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter, FORWARD_CONTANGO_ANNUAL
    adapter = CorrelatedGeneratorAdapter(
        seed=cfg["seed"],
        regime=cfg["regime"],
        gas_start=cfg.get("gas_start"),
        elec_start=cfg.get("elec_start"),
    )
    elec = adapter._elec
    gas = adapter._gas
    return {
        "elec_spot_gbp_per_mwh": round(elec, 2),
        "gas_spot_gbp_per_mwh": round(gas, 2),
        "elec_12m_forward_gbp_per_mwh": round(elec * (1.0 + FORWARD_CONTANGO_ANNUAL), 2),
        "gas_12m_forward_gbp_per_mwh": round(gas * (1.0 + FORWARD_CONTANGO_ANNUAL), 2),
    }


def _portfolio_exposure_delta(customers, scenario_elec_fwd, scenario_gas_fwd, base_elec_fwd, base_gas_fwd):
    """Additional annual commodity cost exposure vs base (unhedged portion)."""
    total = 0.0
    for c in customers:
        eac = c.get("eac_kwh_per_year") or 0
        hf = c.get("hedge_fraction") or 0.0
        fuel = c.get("commodity", "electricity")
        delta_fwd = (scenario_gas_fwd - base_gas_fwd) if fuel == "gas" else (scenario_elec_fwd - base_elec_fwd)
        total += eac / 1000.0 * delta_fwd * (1.0 - hf)
    return round(total, 2)


def run_scenario_analysis(portfolio_path=None, out_dir=None):
    """Run renewal/hedge decisions under base/bull/bear/crisis market scenarios.

    Returns scenario_analysis dict; writes scenario_analysis_latest.json.
    """
    port_path = Path(portfolio_path) if portfolio_path else PORTFOLIO_PATH
    out = Path(out_dir) if out_dir else LIVE_DECISIONS_DIR
    portfolio = json.loads(port_path.read_text())
    customers = portfolio.get("customers", [])
    as_of = portfolio.get("generated_at", "2025-06-07")[:10]

    scenarios = {}
    for name, cfg in _SCENARIO_CONFIGS.items():
        mkt = _scenario_market_state(cfg)
        elec_fwd = mkt["elec_12m_forward_gbp_per_mwh"]
        gas_fwd = mkt["gas_12m_forward_gbp_per_mwh"]
        hedge_rec, hedge_affected = _hedge_recommendation(customers)
        flags = _renewal_flags(customers, as_of, elec_fwd, gas_fwd)
        scenarios[name] = {
            "label": cfg["label"],
            "elec_spot_gbp_per_mwh": mkt["elec_spot_gbp_per_mwh"],
            "gas_spot_gbp_per_mwh": mkt["gas_spot_gbp_per_mwh"],
            "elec_12m_forward_gbp_per_mwh": elec_fwd,
            "gas_12m_forward_gbp_per_mwh": gas_fwd,
            "hedge_recommendation": hedge_rec,
            "hedge_affected_customers": hedge_affected,
            "renewal_flags": flags,
        }

    base_elec_fwd = scenarios["base"]["elec_12m_forward_gbp_per_mwh"]
    base_gas_fwd = scenarios["base"]["gas_12m_forward_gbp_per_mwh"]
    margin_delta = {}
    for name in ("bull", "bear", "crisis"):
        s = scenarios[name]
        margin_delta[name] = _portfolio_exposure_delta(
            customers,
            s["elec_12m_forward_gbp_per_mwh"],
            s["gas_12m_forward_gbp_per_mwh"],
            base_elec_fwd,
            base_gas_fwd,
        )

    result = {
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "portfolio_as_of": portfolio.get("generated_at"),
        "active_customers": portfolio.get("active_customer_count"),
        "projection_months": _SCENARIO_PROJECTION_MONTHS,
        "scenarios": scenarios,
        "portfolio_exposure_delta_gbp": margin_delta,
    }
    out.mkdir(parents=True, exist_ok=True)
    out_file = out / "scenario_analysis_latest.json"
    out_file.write_text(json.dumps(result, indent=2))
    return result


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
