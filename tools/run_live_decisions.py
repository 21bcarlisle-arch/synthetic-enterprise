"""Daily live decision engine -- produces timestamped decision log for paper-trading.

Market as-of date: last available SSP data (frozen cache, currently pinned at 2025-06-07 --
see tools/live_market.py). Portfolio: frozen at final simulation state. Decisions are
timestamped with today's real date.

Two decoupled clocks (Phase RX / S1 Option B, docs/staging/S1_SHADOW_LIVE_TRACK_RECORD_DESIGN.md):
1. Market price freshness -- genuinely bounded by what real Elexon settlement data exists
   in the frozen cache (`market_as_of_date` below, honestly labelled with its real age via
   `market_data_stale_days`). Extending this forward is Option A (a rolling live fetch),
   explicitly out of scope here.
2. Wall-clock elapsed time -- what a renewal countdown and a realised/predicted grading
   mechanism actually need. `days_to_renewal` is computed against real wall-clock "today",
   not against the market data's as-of date, so renewal windows genuinely count down even
   while Option A is unbuilt.
"""
import json, datetime as dt
from pathlib import Path

from company.crm.enriched_churn_estimate import enriched_churn_estimate
from company.analytics.counterfactual_retention import (
    RESI_OFFER_COST_GBP, IC_OFFER_COST_GBP, _RETENTION_EFFECTIVENESS,
)

PROJECT = Path(__file__).resolve().parent.parent
PORTFOLIO_PATH = PROJECT / "site" / "state" / "live_portfolio.json"
LIVE_DECISIONS_DIR = PROJECT / "site" / "state"
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
DECISION_LOG_PATH = PROJECT / "site" / "state" / "live_decisions_log.jsonl"

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

def _utc_now():
    """Real wall-clock UTC now. Factored out (rather than inlined) so tests can patch a
    single, deterministic clock instead of depending on the actual calendar date."""
    return dt.datetime.now(dt.timezone.utc)

def _days_until(renewal_str, clock_date_str):
    if not renewal_str: return None
    r = dt.date.fromisoformat(renewal_str)
    a = dt.date.fromisoformat(clock_date_str)
    return (r - a).days

def _hedge_recommendation(customers):
    below = [c["cid"] for c in customers if c.get("hedge_fraction", 0) < _HEDGE_MIN]
    above = [c["cid"] for c in customers if c.get("hedge_fraction", 0) > _HEDGE_MAX]
    if below: return "INCREASE", below
    if above: return "REDUCE", above
    return "HOLD", []

def _offer_cost_gbp(segment):
    """Retention-offer cost assumption -- reused unchanged from Phase QQ's
    counterfactual_retention.py rather than inventing a new figure here."""
    return IC_OFFER_COST_GBP if segment == "I&C" else RESI_OFFER_COST_GBP

def _tenure_years(last_renewal_date, clock_date_str):
    """Company-observable tenure proxy: years elapsed since the customer's last known
    renewal date, per live_portfolio.json.

    This is a conservative LOWER BOUND on true customer tenure, not a SIM-internal value:
    live_portfolio.json's snapshot generator (tools/project_portfolio_to_2026.py) does not
    carry the original acquisition date forward, only the most recent renewal event -- so
    a customer's real relationship length may be longer than this. It is never shorter, and
    it is something a real supplier genuinely knows (it executed that renewal itself), so
    using it as a floor for the tenure-discount term is honest even though it may understate.
    """
    if not last_renewal_date:
        return 0.0
    try:
        last = dt.date.fromisoformat(last_renewal_date)
        clock = dt.date.fromisoformat(clock_date_str)
    except ValueError:
        return 0.0
    return max(0.0, (clock - last).days / 365.25)

def _retention_ev(old_rate, proposed_rate, customer, segment, fuel, expected_margin, clock_date_str):
    """Expected value (GBP) of proactively offering a retention discount at this renewal.

    Epistemic note (S1 Option B, docs/staging/S1_SHADOW_LIVE_TRACK_RECORD_DESIGN.md): every
    input here is something a real UK supplier could compute from its own records alone --
    its own live churn-risk model (company/crm/enriched_churn_estimate.py, the same
    observable-only estimation path exposed through company/interfaces/sim_interface.py's
    get_churn_estimate), its own last-known and proposed rates, its own meter-read
    consumption (eac_kwh_per_year), its own hedging records (hedge_fraction), and its own
    offer-cost/effectiveness assumptions (reused unchanged from counterfactual_retention.py,
    not invented here). Nothing here imports simulation/ or reads a sim_* ground-truth field
    -- that usage is only legitimate for RETROSPECTIVE scoring of a decision whose outcome
    is already known (counterfactual_retention.py's own use case), which this prospective,
    still-open decision is not. If the observable inputs needed are missing, this returns
    (None, None) rather than fabricating a number.
    """
    if old_rate is None or expected_margin is None:
        return None, None
    tenure_years = _tenure_years(customer.get("last_renewal_date"), clock_date_str)
    churn_est = enriched_churn_estimate(
        old_rate,
        proposed_rate,
        tenure_years,
        customer.get("eac_kwh_per_year") or 0.0,
        fuel=fuel,
        hedge_fraction=customer.get("hedge_fraction") or 0.0,
        segment=segment,
    )
    offer_cost = _offer_cost_gbp(segment)
    retention_lift = churn_est * _RETENTION_EFFECTIVENESS
    value_recovered = retention_lift * expected_margin
    ev_gbp = round(value_recovered - offer_cost, 2)
    return round(churn_est, 4), ev_gbp

def _renewal_flags(customers, clock_date, elec_fwd, gas_fwd):
    flags = []
    for c in customers:
        days = _days_until(c.get("next_renewal_estimate"), clock_date)
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
        old_rate = c.get("current_rate_gbp_per_mwh")
        expected_margin = round(margin * eac / 1000, 2) if eac else None
        churn_est, retention_ev_gbp = _retention_ev(
            old_rate, proposed, c, seg, fuel, expected_margin, clock_date,
        )
        flags.append({
            "cid": c["cid"],
            "segment": seg,
            "commodity": fuel,
            "days_to_renewal": days,
            "renewal_date": c["next_renewal_estimate"],
            "current_rate_gbp_per_mwh": old_rate,
            "proposed_rate_gbp_per_mwh": proposed,
            "svt_approx_gbp_per_mwh": svt,
            "eac_kwh": eac,
            "expected_gross_margin_gbp_pa": expected_margin,
            "company_churn_estimate": churn_est,
            "retention_ev_gbp": retention_ev_gbp,
            "retention_ev_note": None if retention_ev_gbp is not None else
                "ungraded -- missing observable inputs (current rate or annual consumption)",
        })
    return sorted(flags, key=lambda x: x["days_to_renewal"])

def append_decision_log(decision, log_path=None):
    """Append decision to the persistent daily track record (site/state/live_decisions_log.jsonl).

    One entry per UTC calendar day of decision_run_at -- the first decision logged
    for a given day is locked in and never overwritten by later re-runs the same day,
    so the log is a genuine, falsifiable record of what was recommended and when
    (not just the latest re-run's answer restated under an unchanged timestamp).
    """
    log_path = Path(log_path) if log_path else DECISION_LOG_PATH
    run_date = decision["decision_run_at"][:10]
    existing_dates = set()
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            existing_dates.add(json.loads(line)["decision_run_at"][:10])
    if run_date in existing_dates:
        return False
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(decision) + "\n")
    return True


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

    # Two decoupled clocks (Phase RX / S1 Option B) -- see module docstring.
    now_utc = _utc_now()
    clock_date = now_utc.date().isoformat()
    market_data_stale_days = (now_utc.date() - dt.date.fromisoformat(as_of)).days if as_of else None

    flags = _renewal_flags(customers, clock_date, elec_fwd, gas_fwd)
    acq = _acquisition_prices(elec_fwd, gas_fwd)
    decision = {
        "decision_run_at": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "portfolio_as_of": portfolio.get("generated_at"),
        "market_as_of_date": as_of,
        "market_data_stale_days": market_data_stale_days,
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
    append_decision_log(decision, out / "live_decisions_log.jsonl")
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
    print("Market as-of:", d["market_as_of_date"], "(stale", d["market_data_stale_days"], "days)")
    print("Elec spot:", d["elec_spot_gbp_per_mwh"])
    print("Elec 12m fwd:", d["elec_12m_forward_gbp_per_mwh"])
    print("Hedge recommendation:", d["hedge_recommendation"])
    print("Renewal flags:", len(d["renewal_flags"]))
    for f in d["renewal_flags"][:3]:
        print(" ", f["cid"], f["days_to_renewal"], "days", f["proposed_rate_gbp_per_mwh"],
              "churn_est=", f["company_churn_estimate"], "retention_ev=", f["retention_ev_gbp"])
    print("Acquisition prices:", d["acquisition_prices"])
