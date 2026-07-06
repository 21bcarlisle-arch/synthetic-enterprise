#!/usr/bin/env python3
"""Generate site/data/capabilities.json from a static capabilities register +
live headline numbers pulled from the latest run's dashboard.json.

PROJECT_TAB_OVERHAUL.md item 6: Capabilities cards must generate from a
register (name, one-liner, headline numbers FROM THE LATEST RUN, link to
evidence surface) instead of the 11 fully hand-written <div> cards in
site/project/index.html (frozen numbers, no evidence links). Per R-A, the
name/description prose is allowed to be static (it describes what the code
does, not a run-dependent fact); only the headline number must be generated,
and if no live field exists to source it from, the card simply carries no
number rather than a fabricated one.
"""
import json
from pathlib import Path as _P

PROJECT = _P(__file__).resolve().parent.parent
DASHBOARD_PATH = PROJECT / "site" / "data" / "dashboard.json"
OUT_PATH = PROJECT / "site" / "data" / "capabilities.json"


def _get(d, *path):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _settlement_engine_metric(d):
    bills = _get(d, "portfolio", "bills_total")
    window = _get(d, "build", "simulation_window")
    if bills is None:
        return None
    text = "{:,} bills settled".format(bills)
    return text + (" over " + window if window else "")


def _customer_model_metric(d):
    book = _get(d, "customers", "book_annual") or []
    if not book:
        return None
    last = book[-1]
    active = (last.get("active_elec") or 0) + (last.get("active_gas") or 0)
    return "{} active customer accounts ({})".format(active, last.get("year", ""))


def _churn_model_metric(d):
    perf = d.get("churn_model_performance") or {}
    recall, precision, f1 = perf.get("recall"), perf.get("precision"), perf.get("f1_score")
    if recall is None:
        return None
    return "recall {:.0%}, precision {:.0%}, F1 {:.0%} (live run)".format(recall, precision, f1 or 0.0)


def _payment_behaviour_metric(d):
    book = _get(d, "customers", "book_annual") or []
    if not book:
        return None
    last = book[-1]
    shocks = last.get("bill_shock_count")
    worst = last.get("worst_shock_pct")
    if shocks is None:
        return None
    text = "{} bill shocks in {}".format(shocks, last.get("year", ""))
    if worst is not None:
        text += ", worst {:.1f}%".format(worst)
    return text


def _hedging_metric(d):
    hedge = _get(d, "trading", "hedge_annual") or []
    if not hedge:
        return None
    last = hedge[-1]
    hf = last.get("avg_hf")
    if hf is None:
        return None
    return "avg hedge fraction {:.0%} ({})".format(hf, last.get("year", ""))


def _switching_metric(d):
    churns = _get(d, "portfolio", "churn_count")
    if churns is None:
        return None
    return "{} churn event(s) across the run".format(churns)


def _regulatory_metric(d):
    obligations = _get(d, "regulatory", "obligations") or []
    if not obligations:
        return None
    green = sum(1 for o in obligations if o.get("status") == "GREEN")
    return "{} obligations tracked, {} GREEN".format(len(obligations), green)


def _carbon_metric(d):
    return None  # no carbon field in dashboard.json yet -- honestly omitted, not fabricated


def _ic_segment_metric(d):
    segments = _get(d, "market", "segments") or []
    if not segments:
        return None
    return "{} customer segments modelled".format(len(segments))


def _margin_bridge_metric(d):
    net = _get(d, "portfolio", "net_margin_gbp")
    gross = _get(d, "portfolio", "gross_margin_gbp")
    if net is None:
        return None
    text = "net {:,.0f} GBP".format(net)
    if gross is not None:
        text += " (gross {:,.0f} GBP)".format(gross)
    return text


def _counterfactual_retention_metric(d):
    offers = _get(d, "portfolio", "retention_offers")
    retained = _get(d, "portfolio", "retention_retained")
    if offers is None:
        return None
    return "{} offer(s) made, {} retained".format(offers, retained)


def _board_pack_metric(d):
    book = _get(d, "customers", "book_annual") or []
    if not book:
        return None
    return "{} years of annual board reporting ({}-{})".format(
        len(book), book[0].get("year", ""), book[-1].get("year", ""))


CAPABILITIES = [
    dict(id="settlement-engine", name="Half-Hourly Settlement Engine",
         description="Full historical settlement against real Elexon SSP data. Every customer bill computed against actual historical wholesale prices, including the 2021-22 crisis peak.",
         evidence_link="../sim/", metric=_settlement_engine_metric),
    dict(id="customer-model", name="Four-Dimension Customer Model",
         description="Physical (EPC/heating/solar/EV), economic (income stress, life events), behavioural (switching propensity) and emotional (satisfaction accumulator) dimensions per customer.",
         evidence_link="../customers/", metric=_customer_model_metric),
    dict(id="churn-model", name="Three-Signal Churn Model",
         description="Company-side estimate combining bill shock count, payment behaviour and satisfaction. Calibration report: recall, precision, F1 per year against SIM ground truth.",
         evidence_link="../sim/", metric=_churn_model_metric),
    dict(id="payment-behaviour", name="Payment Behaviour Analytics",
         description="Per-customer payment record per month: on-time rate, late rate, DD failure rate, average days late. Drives the churn estimate and board risk dashboard.",
         evidence_link="../customers/", metric=_payment_behaviour_metric),
    dict(id="risk-hedging", name="Risk & Hedging Model",
         description="VaR at 98% confidence per term. Hedge fraction decision each renewal. Capital adequacy: equity greater than VaR plus credit stress. Gas pass-through correctly assigned zero VaR.",
         evidence_link="../", metric=_hedging_metric),
    dict(id="switching-model", name="Price-Elasticity Switching Model",
         description="Market switching rate from savings available (DESNZ 2016-2025), not price level. 2022 crisis paradox reproduced: high bills, low switching.",
         evidence_link="../sim/", metric=_switching_metric),
    dict(id="regulatory-stack", name="Full Regulatory Stack",
         description="RO, FiT, CCL, GSOP, WHD/ECO (EXEMPT), Carbon emissions, Settlement Reconciliation, TPI commission, Ofgem Supply Return, SLC Compliance Scorecard, FRA Capital Ratio. All using real published rates.",
         evidence_link="../project/#regulatory", metric=_regulatory_metric),
    dict(id="carbon-emissions", name="Carbon Emissions Reporting",
         description="Scope 2 electricity: real UK fuel mix 2016-2025. Scope 1 gas: fixed BEIS/DESNZ combustion factor. 10-year decarbonisation trend in the board section.",
         evidence_link="../project/#regulatory", metric=_carbon_metric),
    dict(id="ic-segment", name="I&C Segment Simulation",
         description="HH metering for large I&C. Gas pass-through (zero VaR, service-fee billing). TPI trail commission. Triad demand curtailment on alert days. Rate-sensitivity-only churn.",
         evidence_link="../", metric=_ic_segment_metric),
    dict(id="margin-bridge", name="Year-on-Year Margin Bridge",
         description="Net margin attribution year over year. Primary driver per year (price/volume/cost/mix). Payment portfolio health observatory. Portfolio concentration RAG.",
         evidence_link="../", metric=_margin_bridge_metric),
    dict(id="counterfactual-retention", name="Counterfactual Retention",
         description="Per-customer: was the retention offer worth making? Net value recovered vs offer cost. Threshold sensitivity: recall/precision/F1 across discount thresholds.",
         evidence_link="../customers/", metric=_counterfactual_retention_metric),
    dict(id="board-pack", name="Annual Board Pack",
         description="P&L, capital adequacy, churn performance, retention, regulatory compliance, carbon, payment health, margin bridge, portfolio composition, settlement reconciliation, licence health, compliance scorecard.",
         evidence_link="../", metric=_board_pack_metric),
]


def generate():
    try:
        dashboard = json.loads(DASHBOARD_PATH.read_text())
    except Exception:
        dashboard = {}

    cards = []
    for cap in CAPABILITIES:
        headline = None
        try:
            headline = cap["metric"](dashboard)
        except Exception:
            headline = None
        cards.append(dict(
            id=cap["id"], name=cap["name"], description=cap["description"],
            evidence_link=cap["evidence_link"], headline=headline,
        ))

    data = dict(
        generated_at=_get(dashboard, "meta", "generated_at"),
        git_commit=_get(dashboard, "meta", "git_commit"),
        phase=_get(dashboard, "build", "current_phase"),
        cards=cards,
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: %s (%s cards, %s with a live headline)" % (
        OUT_PATH, len(cards), sum(1 for c in cards if c["headline"])))
    return True


if __name__ == "__main__":
    generate()
