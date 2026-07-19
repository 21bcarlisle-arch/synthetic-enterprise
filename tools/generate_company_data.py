#!/usr/bin/env python3
"""Generate site/data/company.json -- Door 3 "THE COMPANY" data source.

SITE_CONSTITUTION.md Door 3: "THE COMPANY -- board pack assembled largely from
existing Supplier sections (keep-list) + passports + the household drill-down
absorbed as-is." The board-pack view of the company: trading/risk, three-clock
finance (settled/billed/banked), the household drill-down (a real named
customer), compliance organs.

Everything here is a RENDERING of data this project already keeps honestly
(SITE_CONSTITUTION rule 3: "the site is a rendering, never an author"). Sources,
all real:
  1. three-clock finance   -- dashboard.portfolio.basis (R14 clock labels),
     margin_bridge.json (settled<->billed reconciliation), and
     docs/state/billing_ledger.json (billed vs banked/collected cash).
  2. trading & risk         -- dashboard.trading (hedge fraction, VaR limit,
     forward-curve basis-risk error).
  3. household drill-down    -- site/data/customer_sample.json (a real named
     customer, C1) + billing_ledger.json (its billed/banked/arrears history).
  4. compliance organs       -- dashboard.regulatory (SLC obligations register)
     + dashboard.risk_tiered_compliance (tiered controls, held bills).

R14 (SITE_CONSTITUTION binding rule 2): EVERY financial figure carries its clock
(settled / billed / banked). No number is emitted without a `clock` field or an
explicit `//`-basis note. No number appears without its evidence source.
"""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DASHBOARD_PATH = PROJECT / "site" / "data" / "dashboard.json"
BRIDGE_PATH = PROJECT / "site" / "data" / "margin_bridge.json"
SAMPLE_PATH = PROJECT / "site" / "data" / "customer_sample.json"
LEDGER_PATH = PROJECT / "docs" / "state" / "billing_ledger.json"
OUT_PATH = PROJECT / "site" / "data" / "company.json"

# The household we drill into. C1 is a real named account present in every
# source (customer_sample, billing_ledger, dashboard lifetime table): a
# residential, dual-fuel, direct-debit, smart-metered household acquired
# 2016-01-01 -- old enough to have a full ten-year story with real arrears.
DRILLDOWN_ID = "C1"


def _load(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return None


def _rag_counts(items, key="status"):
    return dict(Counter((i.get(key) or "UNKNOWN") for i in items))


def _three_clock_finance(dashboard, bridge, ledger):
    """The three clocks, made explicit (R14). settled = settlement-derived P&L;
    billed = the bill-derived ledger; banked = cash actually collected. Each
    figure carries its clock and its evidence source."""
    portfolio = (dashboard or {}).get("portfolio", {})
    basis = portfolio.get("basis", {})
    ma = ((dashboard or {}).get("management_accounts", {}) or {}).get("annual", []) or []
    latest_ma = ma[-1] if ma else {}

    # billed vs banked at revenue level, summed from the real invoice ledger.
    billed_revenue = banked_revenue = outstanding = None
    collection_rate = None
    ledger_meta = {}
    if ledger and isinstance(ledger.get("customers"), dict):
        custs = ledger["customers"].values()
        billed_revenue = round(sum(c.get("total_billed_gbp", 0) for c in custs), 2)
        banked_revenue = round(sum(c.get("total_paid_gbp", 0) for c in custs), 2)
        outstanding = round(billed_revenue - banked_revenue, 2)
        if billed_revenue:
            collection_rate = round(100 * banked_revenue / billed_revenue, 2)
        ledger_meta = ledger.get("meta", {}) or {}

    b = bridge or {}
    dominant = (b.get("items") or [{}])[0]

    return dict(
        # The headline three-clock reconciliation of NET MARGIN.
        settled_net_margin_gbp=portfolio.get("net_margin_gbp"),
        settled_basis=basis.get("net_margin_gbp", {}),
        billed_net_margin_gbp=b.get("ledger_net_margin_gbp"),
        reconciliation=dict(
            gap_gbp=b.get("total_gap_gbp"),
            gap_ratio_x=b.get("gap_ratio_x"),
            fully_explained=b.get("fully_explained"),
            unexplained_remainder_gbp=b.get("unexplained_remainder_gbp"),
            dominant_item_label=dominant.get("label"),
            dominant_item_gbp=dominant.get("amount_gbp"),
            item_count=len(b.get("items") or []),
            note=b.get("note"),
            evidence="site/data/margin_bridge.json",
            evidence_url="../data/margin_bridge.json",
        ),
        # Revenue: billed vs banked (cash collected), from the invoice ledger.
        billed_revenue_gbp=billed_revenue,
        banked_revenue_gbp=banked_revenue,
        outstanding_gbp=outstanding,
        collection_rate_pct=collection_rate,
        invoice_count=ledger_meta.get("invoice_count"),
        held_bill_count=ledger_meta.get("held_bill_count"),
        # Treasury = banked cash on hand (the bank clock at portfolio level).
        treasury_start_gbp=portfolio.get("treasury_start_gbp"),
        treasury_end_gbp=portfolio.get("treasury_end_gbp"),
        # Latest management-accounts year (billed-clock statutory view).
        latest_year=latest_ma.get("year"),
        latest_year_revenue_gbp=latest_ma.get("revenue_gbp"),
        latest_year_net_margin_gbp=latest_ma.get("net_margin_gbp"),
        latest_year_corporation_tax_gbp=latest_ma.get("corporation_tax_gbp"),
        latest_year_profit_for_year_gbp=latest_ma.get("profit_for_year_gbp"),
        gross_margin_gbp=portfolio.get("gross_margin_gbp"),
        enterprise_value_gbp=portfolio.get("enterprise_value_gbp"),
        enterprise_value_basis=basis.get("enterprise_value_gbp", {}),
        passport=dict(
            sources=[
                "site/data/dashboard.json (portfolio, management_accounts)",
                "site/data/margin_bridge.json (settled<->billed bridge)",
                "docs/state/billing_ledger.json (billed vs banked cash)",
            ],
            rule="R14 -- every financial figure carries its clock (settled/billed/banked)",
        ),
    )


def _trading_risk(dashboard):
    """The board's trading/risk position: hedge coverage, the VaR limit, and the
    forward-curve basis-risk error the company runs against sim ground truth."""
    trading = (dashboard or {}).get("trading", {})
    hedge_annual = trading.get("hedge_annual", []) or []
    latest_hedge = hedge_annual[-1] if hedge_annual else {}
    forward_terms = trading.get("forward_terms", []) or []
    # Basis-risk: mean absolute error of the company's own forward curve vs the
    # sim's -- the company builds its curve from observables, never reads truth.
    errs = [t.get("error_pct") for t in forward_terms if isinstance(t.get("error_pct"), (int, float))]
    mean_abs_err = round(sum(abs(e) for e in errs) / len(errs), 4) if errs else None
    return dict(
        latest_hedge_year=latest_hedge.get("year"),
        latest_avg_hf=latest_hedge.get("avg_hf"),
        latest_min_hf=latest_hedge.get("min_hf"),
        latest_max_hf=latest_hedge.get("max_hf"),
        hedge_annual=[
            dict(year=h.get("year"), avg_hf=h.get("avg_hf"),
                 min_hf=h.get("min_hf"), max_hf=h.get("max_hf"))
            for h in hedge_annual
        ],
        var_limit_pct_of_term_revenue=trading.get("var_limit_pct_of_term_revenue"),
        forward_term_count=len(forward_terms),
        forward_curve_mean_abs_error_pct=mean_abs_err,
        passport=dict(
            sources=["site/data/dashboard.json (trading.hedge_annual, .forward_terms)"],
            note="Hedge fraction is the share of forecast volume forward-bought; "
                 "basis-risk error is the company's own curve vs the sim's ground "
                 "truth (the company never reads sim internals -- epistemic wall).",
        ),
    )


def _household(sample, ledger):
    """The household drill-down, absorbed as-is: one real named account seen from
    every angle -- demographics, lifetime P&L (settled net), and its own three
    clocks (billed vs banked cash) with the real arrears cases behind them."""
    cust = (((sample or {}).get("customers")) or {}).get(DRILLDOWN_ID)
    if not cust:
        return dict(available=False, id=DRILLDOWN_ID)

    led = (((ledger or {}).get("customers")) or {}).get(DRILLDOWN_ID, {})
    arrears = led.get("arrears_history", []) or []
    # Latest satisfaction + latest income stress, honestly the tail of the series.
    sat = cust.get("satisfaction_score_trajectory", []) or []
    stress = cust.get("income_stress_trajectory", []) or []
    life = cust.get("life_event_history", []) or []

    return dict(
        available=True,
        id=cust.get("account_id"),
        segment=cust.get("segment"),
        commodity=cust.get("commodity"),
        dual_fuel=cust.get("dual_fuel"),
        smart_meter=cust.get("smart_meter"),
        payment_channel=cust.get("payment_channel"),
        engagement_level=cust.get("engagement_level"),
        tenure=cust.get("tenure"),
        occupancy=cust.get("occupancy"),
        home_type=cust.get("home_type"),
        fuel_poverty=cust.get("fuel_poverty"),
        acquisition_date=cust.get("acquisition_date"),
        # Lifetime P&L -- settlement-derived net (the settled clock).
        lifetime_revenue_gbp=cust.get("lifetime_revenue_gbp"),
        lifetime_gross_gbp=cust.get("lifetime_gross_gbp"),
        lifetime_net_gbp=cust.get("lifetime_net_gbp"),
        cost_to_serve_gbp=cust.get("cost_to_serve_gbp"),
        clv_gbp=cust.get("clv_gbp"),
        latest_churn_probability=cust.get("latest_churn_probability"),
        expected_lifetime_periods=cust.get("expected_lifetime_periods"),
        # This household's OWN three clocks (billed vs banked cash).
        billed_gbp=led.get("total_billed_gbp"),
        banked_gbp=led.get("total_paid_gbp"),
        balance_gbp=led.get("balance_gbp"),
        invoice_count=led.get("invoice_count"),
        failed_payment_count=led.get("failed_payment_count"),
        arrears_case_count=led.get("arrears_case_count"),
        arrears_cases=[
            dict(
                case_id=a.get("case_id"),
                arrears_gbp=a.get("arrears_gbp"),
                opened_date=a.get("opened_date"),
                stages=[dict(stage=s.get("stage"), date=s.get("date"),
                             note=s.get("note"), amount_gbp=s.get("amount_gbp"))
                        for s in (a.get("stages") or [])],
            )
            for a in arrears
        ],
        annual_pnl=cust.get("annual_pnl", []),
        life_events=life,
        latest_satisfaction=(sat[-1] if sat else None),
        latest_income_stress=(stress[-1] if stress else None),
        passport=dict(
            sources=[
                "site/data/customer_sample.json (demographics, lifetime P&L, CLV)",
                "docs/state/billing_ledger.json (billed vs banked, arrears history)",
            ],
            note="A real named account. Lifetime net is settlement-derived "
                 "(settled clock); billed/banked are its own invoice-ledger cash clocks.",
        ),
    )


def _compliance(dashboard):
    """The compliance organs: the SLC obligations register (a real supplier's
    licence conditions, RAG-rated) and the tiered risk-control view (which
    obligations get full-population testing vs sampling, and the held bills)."""
    reg = (dashboard or {}).get("regulatory", {})
    obligations = reg.get("obligations", []) or []
    tiered = (dashboard or {}).get("risk_tiered_compliance", {})
    by_tier = tiered.get("by_tier", {}) or {}

    tiers = []
    for tier_key in sorted(by_tier.keys()):
        items = by_tier[tier_key] or []
        tiers.append(dict(
            tier=tier_key,
            item_count=len(items),
            status_counts=_rag_counts(items),
            items=[
                dict(
                    id=i.get("id"), name=i.get("name"), source=i.get("source"),
                    status=i.get("status"), basis=i.get("basis"),
                    control_type=i.get("control_type"),
                    testing_depth=i.get("testing_depth"),
                    testing_frequency=i.get("testing_frequency"),
                )
                for i in items
            ],
        ))

    return dict(
        obligations_register=dict(
            latest_year=reg.get("latest_year"),
            overall_rag=reg.get("overall_rag"),
            count=len(obligations),
            status_counts=_rag_counts(obligations),
            domain_counts=_rag_counts(obligations, key="domain"),
            items=[
                dict(code=o.get("code"), description=o.get("description"),
                     domain=o.get("domain"), status=o.get("status"),
                     notes=o.get("notes"))
                for o in obligations
            ],
        ),
        tiered_controls=dict(
            overall_rag=tiered.get("overall_rag"),
            held_bill_count=tiered.get("held_bill_count"),
            obligation_count=tiered.get("obligation_count"),
            tiers=tiers,
        ),
        passport=dict(
            sources=[
                "site/data/dashboard.json (regulatory.obligations)",
                "site/data/dashboard.json (risk_tiered_compliance.by_tier)",
            ],
            note="The obligations register is the company's own compliance reading "
                 "of published law (regulation-commons doctrine); a real supplier "
                 "can misread it and be fined -- so RED/AMBER is kept, never smoothed.",
        ),
    )


def _stress_bands(sample):
    """The book by each customer's latest income-stress band -- re-homed from the
    retired SIM-Explorer 'Customers' tab into The Company (v4 §4①, affordability/
    collections). Categorical, from the tail of each customer's
    income_stress_trajectory. The switching insight is CODE-backed (not lost with
    the old page): simulation/switching_propensity.py."""
    custs = ((sample or {}).get("customers")) or {}
    high = mod = low = ic = 0
    for cid, c in custs.items():
        if "IC" in str(cid):
            ic += 1
        traj = c.get("income_stress_trajectory") or []
        s = ((traj[-1].get("stress") if traj else "low") or "low").upper()
        if s == "HIGH":
            high += 1
        elif s == "MODERATE":
            mod += 1
        else:
            low += 1
    total = len(custs)
    return dict(
        total=total, ic=ic, residential=total - ic,
        high_stress=high, moderate_stress=mod, low_stress=low,
        switching_insight=(
            "Financially stressed customers switch LESS, not more: friction costs "
            "(deposits, DD setup, mental load) suppress switching hardest for HIGH-stress "
            "households (x0.65) vs LOW-stress (x1.10) — a fixed function of stress, "
            "simulation/switching_propensity.py."
        ),
    )


def generate():
    dashboard = _load(DASHBOARD_PATH) or {}
    bridge = _load(BRIDGE_PATH) or {}
    sample = _load(SAMPLE_PATH) or {}
    ledger = _load(LEDGER_PATH) or {}

    meta = dashboard.get("meta", {}) or {}
    data = dict(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        dashboard_generated_at=meta.get("generated_at"),
        git_commit=meta.get("git_commit"),
        finance=_three_clock_finance(dashboard, bridge, ledger),
        trading_risk=_trading_risk(dashboard),
        household=_household(sample, ledger),
        stress_bands=_stress_bands(sample),
        compliance=_compliance(dashboard),
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: " + str(OUT_PATH))
    return data


if __name__ == "__main__":
    generate()
