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
        # Wholesale value-chain organs (VALUE_CHAIN mint): who the hedges sit
        # with, per-counterparty credit exposure, and the margin-call book. All
        # company-observable (own netted MtM, own margin calls, public ratings).
        wholesale=trading.get("wholesale") or {"available": False},
        passport=dict(
            sources=[
                "site/data/dashboard.json (trading.hedge_annual, .forward_terms)",
                "docs/reports/run_output_latest.json "
                "(trading_book, wholesale_credit_exposure, margin_call_book)",
            ],
            note="Hedge fraction is the share of forecast volume forward-bought; "
                 "basis-risk error is the company's own curve vs the sim's ground "
                 "truth (the company never reads sim internals -- epistemic wall). "
                 "Wholesale credit exposure is ISDA-netted MtM owed TO the company, "
                 "marked at a point-in-time forward curve; peak is the mid-run high "
                 "(exposure peaks at a price shock, not run-end). Collateral held is "
                 "reported as 0 (an UPPER-BOUND simplification -- CSA/variation-margin "
                 "postings are not yet modelled); the observation-window credit cap is "
                 "live but dormant (it erodes a line only on observed counterparty "
                 "default conduct, whose producer is a walled coupled SIM atom); the "
                 "MC-2 collateral death-test is not yet built (its difficulty is "
                 "director-owned curriculum).",
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


def _cost_to_serve_distribution(sample):
    """Per-customer cost-to-serve as a DISTRIBUTION, never a bare total (RC6 §C,
    DIRECTOR 2026-07-23: "distributions across coverage cells ... certainly not
    totals from a random sample of customers"). Cost-to-serve is a lifetime
    cumulative figure (settled clock). Built from customer_sample.json -- the same
    real named accounts the household drill-down uses -- so it is not a fresh,
    un-cross-checkable aggregate. The raw per-customer values are emitted (sorted)
    so the page renders the SPREAD, and the segment split gives the coverage-cell
    distribution the director asked for. Activity-based pricing (a standing project
    constraint) needs the per-customer figure, not the average: a flat margin makes
    the high-cost-to-serve tail net-negative, and only the distribution shows it.

    FAIL-CLOSED (R15): an empty/uncomputable sample returns available:False, never
    a silently-zero total the page would render as a real figure."""
    custs = ((sample or {}).get("customers")) or {}
    rows = []
    for cid, c in custs.items():
        cts = c.get("cost_to_serve_gbp")
        if cts is None:
            continue
        seg = "ic" if "IC" in str(cid) else "resi"
        rows.append((float(cts), seg, c))
    if not rows:
        return {"available": False, "n": 0}

    def _stats(vs):
        s = sorted(vs)
        n = len(s)
        median = s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0
        return dict(
            n=n,
            min_gbp=round(s[0], 2),
            median_gbp=round(median, 2),
            mean_gbp=round(sum(s) / n, 2),
            max_gbp=round(s[-1], 2),
        )

    by_segment = []
    for seg in ("resi", "ic"):
        segvals = [v for v, s, _ in rows if s == seg]
        if segvals:
            st = _stats(segvals)
            st["segment"] = seg
            by_segment.append(st)

    # RC6 §C follow-on (DIRECTOR "distributions across coverage cells"): cost-to-serve
    # broken out across ADDITIONAL cells the director named beyond resi/IC, built from
    # the SAME drawn accounts. payment_channel is the load-bearing activity-based-pricing
    # cell (standard-credit customers cost materially more to serve than direct-debit);
    # tenure is a secondary cell. Customers whose cell attribute is absent (gas legs /
    # I&C accounts carry no residential attribute) are SKIPPED, never bucketed as a
    # fabricated cell. A cell group is emitted only when >=2 distinct populated cells
    # exist -- a single-cell "distribution" is theatre, so it collapses to nothing (the
    # total already covers it). Reads cost_to_serve_gbp + the cell key ONLY (no P&L
    # field), so R12/R13 no-goal-seek holds for the cells too.
    def _by_cell(field):
        cells = {}
        for v, _s, c in rows:
            key = c.get(field)
            if key is None or key == "":
                continue
            cells.setdefault(str(key), []).append(v)
        if len(cells) < 2:
            return []
        out_cells = []
        for key in sorted(cells):
            st = _stats(cells[key])
            st["cell"] = key
            out_cells.append(st)
        return out_cells

    out = _stats([v for v, _, _ in rows])
    out.update(
        dict(
            available=True,
            clock="settled",
            basis="lifetime cost-to-serve per customer · settled clock · drawn sample",
            values_gbp=[round(v, 2) for v, _, _ in sorted(rows, key=lambda r: r[0])],
            by_segment=by_segment,
            by_payment_channel=_by_cell("payment_channel"),
            by_tenure=_by_cell("tenure"),
        )
    )
    return out


def _arrears_distribution(sample, ledger):
    """Per-customer ARREARS-£ balance as a DISTRIBUTION -- the sibling of
    cost-to-serve, and the last remainder of DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE
    §C (arrears-£-per-customer). A real UK supplier carries a customer-level
    aged-debt ledger and provisions against it; bad debt is one of the largest
    cost-to-serve line items and is heavily segment-shaped (standard-credit and
    early-tenure accounts carry materially more arrears than direct-debit).

    THROUGH-THE-WALL OBSERVABLE (epistemic wall): arrears = Σ(bills issued) -
    Σ(payments received) per customer, read ONLY from the company's OWN
    billed-vs-banked ledger (billing_ledger.json: total_billed_gbp,
    total_paid_gbp). No sim-internal hardship/churn truth is read -- a real
    supplier knows its own bills and its own receipts and nothing more. The
    company's belief-vs-truth GAP against the sim's true arrears is a separate
    HARNESS measure (coupled-triad), out of scope here.

    R14 (basis clock): the balance is billed MINUS banked -- every figure carries
    that clock. R12 (anti-goal-seek): arrears is a DIAGNOSTIC, never a target; no
    parameter is tuned toward a plausible arrears band. FAIL-CLOSED (R15): a
    ledger with no customer carrying BOTH a billed and a paid figure returns
    available:False, never a silently-zero total the page renders as real.

    RC7 / FRONT_MISSION_BLOCK wall: this is a cohort-derived £ figure, so it may
    only appear behind a /company drill-down -- never a lead slot -- with N, a
    FLOOR framing (gross exposure is a floor on the bad-debt base, not a point
    estimate) and its missing-lines enumerated. Those are carried on the JSON so
    the render cannot drop them."""
    led_custs = ((ledger or {}).get("customers")) or {}
    samp_custs = ((sample or {}).get("customers")) or {}
    rows = []  # (arrears_gbp, segment, sample_customer_or_None, ledger_customer)
    for cid, lc in led_custs.items():
        billed = lc.get("total_billed_gbp")
        paid = lc.get("total_paid_gbp")
        if billed is None or paid is None:
            continue
        arrears = round(float(billed) - float(paid), 2)
        seg = lc.get("segment") or "unknown"
        rows.append((arrears, seg, samp_custs.get(cid) or {}, lc))
    if not rows:
        return {"available": False, "n": 0}

    def _stats(vs):
        s = sorted(vs)
        n = len(s)
        median = s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0
        return dict(
            n=n,
            min_gbp=round(s[0], 2),
            median_gbp=round(median, 2),
            mean_gbp=round(sum(s) / n, 2),
            max_gbp=round(s[-1], 2),
        )

    # Segment split (resi / SME / I&C carry structurally different arrears scale).
    by_segment = []
    for seg in sorted({r[1] for r in rows}):
        segvals = [a for a, s, _, _ in rows if s == seg]
        if segvals:
            st = _stats(segvals)
            st["segment"] = seg
            by_segment.append(st)

    # Additional coverage cells from the SAME accounts, joined to customer_sample
    # for the cell attribute (payment_channel is the load-bearing activity cell:
    # standard-credit accounts run materially higher arrears than direct-debit;
    # tenure is secondary). A cell key absent on an account (I&C legs carry no
    # residential attribute) is SKIPPED, never bucketed as a fabricated cell; a
    # group with <2 populated cells collapses to nothing (a one-cell
    # "distribution" is theatre). Reads the cell key only -- no P&L field -- so
    # R12/R13 no-goal-seek holds for the cells too.
    def _by_cell(field):
        cells = {}
        for a, _s, sc, _lc in rows:
            key = (sc or {}).get(field)
            if key is None or key == "":
                continue
            cells.setdefault(str(key), []).append(a)
        if len(cells) < 2:
            return []
        out_cells = []
        for key in sorted(cells):
            st = _stats(cells[key])
            st["cell"] = key
            out_cells.append(st)
        return out_cells

    in_arrears = sum(1 for a, _, _, _ in rows if a > 0.005)
    in_credit = sum(1 for a, _, _, _ in rows if a < -0.005)
    # Accounts square to the penny (billed == banked) are neither -- counted so
    # the split adds up to N (a veteran smell-test: 14 + 3 must not read as < N).
    settled = len(rows) - in_arrears - in_credit
    # FLOOR (RC7 floor-not-figure): gross exposure is Sigma of the POSITIVE
    # balances only -- credit balances do not net off a bad-debt provision base,
    # so this is a floor on what is owed to us, not a tidy net point estimate.
    gross_exposure = round(sum(a for a, _, _, _ in rows if a > 0), 2)

    out = _stats([a for a, _, _, _ in rows])
    out.update(
        dict(
            available=True,
            clock="billed_minus_banked",
            basis="per-customer arrears balance = total billed - total banked "
                  "(cumulative, own ledger) - drawn sample",
            in_arrears=in_arrears,
            in_credit=in_credit,
            settled=settled,
            gross_exposure_gbp=gross_exposure,
            gross_exposure_is_floor=True,
            values_gbp=[round(a, 2) for a, _, _, _ in sorted(rows, key=lambda r: r[0])],
            by_segment=by_segment,
            by_payment_channel=_by_cell("payment_channel"),
            by_tenure=_by_cell("tenure"),
            # Missing-lines enumeration (RC7): what this balance does NOT yet
            # capture, stated so the panel cannot read as a complete aged-debt
            # picture. Honest-absent, not smoothed.
            missing_lines=[
                "no aged-debt bucketing (30/60/90+ days) -- a single cumulative "
                "balance, not a dunning-stage split",
                "write-offs and provisions not yet deducted -- gross owed, not "
                "net-of-provision",
                "timing: a balance may include bills issued but not yet due, so "
                "it overstates true overdue arrears",
                "the drawn sample, not the full book -- a floor across N, never "
                "a book total",
            ],
        )
    )
    return out


# ---------------------------------------------------------------------------
# SEGMENT DISCLOSURE (SITE_EH1_segment_disclosure, 2026-07-30).
#
# THE DEFECT this exists to close (cold-eyes Expert Hour on SITE1, its single
# most damaging finding): /company/ led its finance panel with a BLENDED
# "Net margin / customer" and "Revenue / customer" -- correctly clock-labelled
# (R14) and honestly showing its denominator (÷19) -- over a book whose revenue
# is ~99% Industrial & Commercial, under a household-carbon narrative in which
# I&C appeared ZERO times. R14 discipline was fully present and pointed at the
# WRONG AXIS: the CLOCK was labelled on every figure and the SEGMENT on none.
# A blended £/customer over this book describes no customer the company has.
#
# This is a DISCLOSURE change only. It does NOT touch the book's composition --
# which segments the company serves is CURRICULUM (R13, the director's
# instrument), and reweighting a population to make a published figure read
# better is goal-seeking (R12). If a figure reads badly once split honestly, it
# is left to read badly.
# ---------------------------------------------------------------------------

# The canonical segment taxonomy. Keys are the `segment_split` prefixes the run
# emits (dashboard.financial.segment_annual keys are "<prefix>_<commodity>",
# already lower-cased), and they match customer_sample's own `segment` field
# lower-cased -- so ACCOUNT COUNTS and REVENUE join on the same token with no
# second naming convention. `population_class` is the axis a published benchmark
# has to agree with (see tools/generate_world_data.py): domestic households are
# not a business book and the two are not each other's benchmark.
_SEGMENTS = {
    "resi": dict(label="Residential", population_class="domestic"),
    "sme": dict(label="SME (small business)", population_class="non_domestic"),
    "i&c": dict(label="Industrial & Commercial", population_class="non_domestic"),
}
# Above this share of revenue, the book IS that population class for benchmarking
# purposes. Below it in both directions the book is genuinely mixed and only a
# whole-market benchmark can grade it. Chosen once, stated here, never tuned to
# an outcome (R12).
_DOMINANCE_SHARE_PCT = 80.0


def _segment_prefix(segment_annual_key):
    """'i&c_electricity' -> 'i&c'. The commodity is the LAST underscore-delimited
    token; everything before it is the segment. Returns the raw prefix even when
    it is unknown to _SEGMENTS -- an unrecognised segment must show up as
    unclassified revenue, never be silently dropped from the denominator (the
    exact fail-silent shape saas/reporting/css_statement.py guards against)."""
    return str(segment_annual_key).rsplit("_", 1)[0]


def segment_revenue_mix(segment_annual):
    """The book's revenue mix by segment, cumulative over the whole run window.

    Reads dashboard.financial.segment_annual, which is the run's OWN settlement
    records view of per-segment revenue (`data['years'][*]['segment_split']`,
    settled clock -- see saas/reporting/css_statement.py). Pure function of its
    argument so the front-door coherence gate in generate_dashboard_data.py can
    compute the same share without reaching through company.json.

    FAIL-CLOSED (R15): a missing/empty/malformed segment_annual returns
    available=False with no shares, never a silently-zero mix the page would
    render as "0% I&C" -- which would read as a DOMESTIC book, the precise lie
    this whole atom exists to prevent.
    """
    rows = [r for r in (segment_annual or []) if isinstance(r, dict)]
    if not rows:
        return dict(available=False, reason="segment_annual missing or empty")

    revenue = {}
    unclassified = {}
    for row in rows:
        for key, cell in row.items():
            if key == "year" or not isinstance(cell, dict):
                continue
            rev = cell.get("revenue_gbp")
            if not isinstance(rev, (int, float)):
                continue
            prefix = _segment_prefix(key)
            bucket = revenue if prefix in _SEGMENTS else unclassified
            bucket[prefix] = bucket.get(prefix, 0.0) + float(rev)

    total = sum(revenue.values()) + sum(unclassified.values())
    if total <= 0:
        return dict(available=False, reason="segment_annual carries no positive revenue")

    def _share(v):
        return round(100.0 * v / total, 2)

    by_class = {"domestic": 0.0, "non_domestic": 0.0}
    for prefix, amount in revenue.items():
        by_class[_SEGMENTS[prefix]["population_class"]] += amount

    domestic_pct = _share(by_class["domestic"])
    non_domestic_pct = _share(by_class["non_domestic"])
    if non_domestic_pct >= _DOMINANCE_SHARE_PCT:
        composition_class = "non_domestic"
    elif domestic_pct >= _DOMINANCE_SHARE_PCT:
        composition_class = "domestic"
    else:
        composition_class = "mixed"

    return dict(
        available=True,
        total_revenue_gbp=round(total, 2),
        domestic_revenue_share_pct=domestic_pct,
        non_domestic_revenue_share_pct=non_domestic_pct,
        unclassified_revenue_gbp=round(sum(unclassified.values()), 2),
        unclassified_segments=sorted(unclassified),
        composition_class=composition_class,
        dominance_threshold_pct=_DOMINANCE_SHARE_PCT,
        revenue_by_segment={k: round(v, 2) for k, v in revenue.items()},
        share_by_segment={k: _share(v) for k, v in revenue.items()},
        years=[r.get("year") for r in rows],
    )


def _account_counts_by_segment(sample):
    """Account counts per segment, read from each drawn account's OWN `segment`
    field -- NOT from an id substring. stress_bands (below) buckets on `"IC" in
    cid`, which silently files the two SME accounts under "residential"; the
    per-segment denominators here must not inherit that, because an n that is
    wrong by 2 is a wrong £/customer figure. An account whose segment is absent
    or unrecognised is counted as UNCLASSIFIED, never folded into a real
    segment's denominator."""
    custs = ((sample or {}).get("customers")) or {}
    counts = {}
    unclassified = 0
    for c in custs.values():
        seg = str(c.get("segment") or "").strip().lower()
        if seg in _SEGMENTS:
            counts[seg] = counts.get(seg, 0) + 1
        else:
            unclassified += 1
    return counts, unclassified, len(custs)


def _book_mix(dashboard, sample):
    """The segment disclosure block: the revenue mix, and per-customer unit
    economics SPLIT BY SEGMENT with each segment's own n.

    Scope item 1 of the atom: "Every per-customer tile splits by segment (a
    blended per-customer figure over a 98.75% I&C book is the defect; show resi
    and I&C separately, each with its own n)."

    Clock (R14): the per-segment revenue/net legs come from the run's segment
    split, which is SETTLED. The blended tiles this replaces were BILLED
    (management accounts). That is a real clock difference and it is stated on
    every tile rather than quietly harmonised -- the settled<->billed gap is the
    bridge's job, not this block's.
    """
    financial = (dashboard or {}).get("financial", {}) or {}
    mix = segment_revenue_mix(financial.get("segment_annual"))
    if not mix.get("available"):
        return dict(available=False, reason=mix.get("reason"))

    rows = [r for r in (financial.get("segment_annual") or []) if isinstance(r, dict)]
    latest = rows[-1]
    latest_year = latest.get("year")

    counts, n_unclassified, n_total = _account_counts_by_segment(sample)

    # Latest-year revenue/net per segment (summed across that segment's commodity legs).
    latest_rev, latest_net = {}, {}
    for key, cell in latest.items():
        if key == "year" or not isinstance(cell, dict):
            continue
        prefix = _segment_prefix(key)
        if prefix not in _SEGMENTS:
            continue
        latest_rev[prefix] = latest_rev.get(prefix, 0.0) + float(cell.get("revenue_gbp") or 0.0)
        latest_net[prefix] = latest_net.get(prefix, 0.0) + float(cell.get("net_gbp") or 0.0)

    segments = []
    for prefix in sorted(mix["revenue_by_segment"], key=lambda p: -mix["revenue_by_segment"][p]):
        n = counts.get(prefix)
        present = prefix in latest_rev
        rev = latest_rev.get(prefix)
        net = latest_net.get(prefix)
        # FAIL-CLOSED: no n (or n=0) means NO per-customer figure. Falling back to
        # the whole-book denominator is exactly the blend this atom removes.
        divisible = bool(n) and present
        segments.append(dict(
            segment=prefix,
            label=_SEGMENTS[prefix]["label"],
            population_class=_SEGMENTS[prefix]["population_class"],
            n_accounts=n,
            revenue_gbp=mix["revenue_by_segment"][prefix],
            revenue_share_pct=mix["share_by_segment"][prefix],
            latest_year_present=present,
            latest_year_revenue_gbp=(round(rev, 2) if rev is not None else None),
            latest_year_net_margin_gbp=(round(net, 2) if net is not None else None),
            revenue_per_customer_gbp=(round(rev / n, 2) if divisible else None),
            net_margin_per_customer_gbp=(round(net / n, 2) if divisible else None),
            per_customer_unavailable_reason=(
                None if divisible
                else ("no account of this segment in the drawn book" if not n
                      else "this segment billed no revenue in " + str(latest_year))
            ),
        ))

    dominant = segments[0] if segments else None
    # The blended figure is KEPT (it is a real reading and R12 forbids hiding an
    # inconvenient diagnostic) but STRIPPED OF HEADLINE STATUS, with the reason
    # attached. latest_year_* here are the BILLED management-accounts figures the
    # old blended tiles used, so the number a reader saw yesterday is still
    # findable and reconcilable rather than silently vanished.
    ma = ((dashboard or {}).get("management_accounts", {}) or {}).get("annual", []) or []
    latest_ma = ma[-1] if ma else {}
    blended = None
    if n_total and latest_ma:
        blended = dict(
            n_accounts=n_total,
            clock="billed",
            revenue_per_customer_gbp=round((latest_ma.get("revenue_gbp") or 0.0) / n_total, 2),
            net_margin_per_customer_gbp=round((latest_ma.get("net_margin_gbp") or 0.0) / n_total, 2),
            withheld_as_headline=True,
            reason=(
                "A blended £/customer across " + str(n_total) + " accounts describes no customer "
                "this company has: " + (
                    "{:.1f}% of revenue is earned by {} {} account(s)".format(
                        dominant["revenue_share_pct"], dominant["n_accounts"], dominant["label"])
                    if dominant else "the book is dominated by one segment"
                ) + ". It is kept here as a reconcilable diagnostic, never as a headline (R12: a "
                "metric is a diagnostic, never a target)."
            ),
        )

    return dict(
        available=True,
        clock="settled",
        basis=(
            "per-segment revenue and net margin from the run's own settlement segment split · "
            "settled clock · £/customer divides each segment's latest-year figure by THAT "
            "segment's own account count in the drawn book"
        ),
        latest_year=latest_year,
        window_years=[y for y in mix["years"] if y is not None],
        n_accounts_total=n_total,
        n_accounts_unclassified=n_unclassified,
        segments=segments,
        blended=blended,
        dominant_segment=(dominant or {}).get("segment"),
        dominant_label=(dominant or {}).get("label"),
        dominant_share_pct=(dominant or {}).get("revenue_share_pct"),
        domestic_revenue_share_pct=mix["domestic_revenue_share_pct"],
        non_domestic_revenue_share_pct=mix["non_domestic_revenue_share_pct"],
        composition_class=mix["composition_class"],
        dominance_threshold_pct=mix["dominance_threshold_pct"],
        unclassified_revenue_gbp=mix["unclassified_revenue_gbp"],
        total_revenue_gbp=mix["total_revenue_gbp"],
        # MISSION REWRITE 2026-08-28 (director, direct; CLAUDE.md + THE MODEL ON A PAGE §The
        # mission). The old note named "household carbon abatement through personalisation",
        # which has been superseded. The note's JOB is unchanged and is why it exists: state the
        # composition before any claim, and hold the mission-vs-book question open as the
        # director's. What the new mission changes is that the question got SHARPER rather than
        # softer -- a mission about finding individual customers makes the book a direct
        # statement about which customers the method has actually found.
        mission_note=(
            "The front door's mission is finding individual customers we can create value for and "
            "sharing in that value -- saving them money, time and carbon. This book is what that "
            "method has found so far, and the composition below is therefore evidence about the "
            "method, not incidental to it. Whether the mission and the book should agree is a "
            "DIRECTOR question (values, one-way door 6) and is escalated, not decided here; "
            "what this panel owes the reader is the composition, stated before any claim."
        ),
        evidence="site/data/dashboard.json -> financial.segment_annual; site/data/customer_sample.json (segment field)",
        evidence_url="../data/dashboard.json",
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
        book_mix=_book_mix(dashboard, sample),
        finance=_three_clock_finance(dashboard, bridge, ledger),
        trading_risk=_trading_risk(dashboard),
        household=_household(sample, ledger),
        cost_to_serve=_cost_to_serve_distribution(sample),
        arrears=_arrears_distribution(sample, ledger),
        stress_bands=_stress_bands(sample),
        compliance=_compliance(dashboard),
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: " + str(OUT_PATH))
    return data


if __name__ == "__main__":
    generate()
