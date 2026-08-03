#!/usr/bin/env python3
"""Generate site/data/world.json -- Door 5 "THE WORLD" data source.

SITE_CONSTITUTION.md Door 5: "THE WORLD -- two-sided wall page; sim depth
re-homed; anchors register." The door that shows BOTH SIDES of the epistemic
wall: what the SIM knows (ground truth) versus what the COMPANY observes and
believes, and the honest DIVERGENCE between them -- the core architectural law
("the company cannot see inside the sim") made visible and checkable. Plus the
anchors register: the real external data the sim is calibrated against.

Everything here is a RENDERING of data this project already keeps honestly
(SITE_CONSTITUTION rule: "the site is a rendering, never an author"). Sources,
all real:
  1. FORWARD-CURVE BASIS RISK -- dashboard.trading.forward_terms
     (company_fwd vs sim_fwd, per customer, with error_pct) +
     dashboard.market.forward_premium_annual (the company's forecast error vs
     realised outturn, per year). The company builds its curve from observables;
     it never reads the sim's ground-truth forward. The gap is basis risk.
  2. DEMAND ESTIMATION -- dashboard.monthly_ops.demand_estimation_annual: the
     company forecasts annual volume at renewal from prior billing; the sim
     knows the actual outturn. mean_abs_error_pct is the volume-side wall gap.
  3. METER READ estimate-vs-actual -- dashboard.customers.meter_read_log: the
     company bills partly on ESTIMATED reads (traditional meters, read delay);
     the sim knows true half-hourly consumption. The BSC settlement-run ladder
     (SF -> R1 -> R2 -> R3 -> RF, company/market/bsc_settlement_run_register.py)
     is the real mechanism that progressively replaces estimates with actuals.
  4. POINT-IN-TIME BLINDFOLD -- sim_data.json (real Elexon SSP price series,
     incl. the 2021-22 crisis the sim knows in full) + dashboard.market.
     contango_monthly: the company prices forward under blindness to the future
     spike; the sim holds the whole realised path.

Anchors register:
  - RUNTIME calibration: site/state/population_anchoring.json -- sim outcomes vs
    external Ofgem/DESNZ benchmarks, RAG-rated (churn, bad debt, complaints,
    arrears). The divergence is measured and kept, never smoothed.
  - LIBRARY: docs/market_research/ASSUMPTIONS.md -- the human-readable assumption
    library, each row a sim value vs an industry benchmark with a source and a
    checked status. Parsed as-is; ? / warn statuses are surfaced, not hidden.

R14 (binding): every financial figure carries its basis/clock. Forward prices
are point-in-time as-known (blindfold enforced); SSP is real Elexon settlement;
divergences are stated in their own units (£/MWh, % error, share). No number
appears without its evidence source. R12: divergence is a DIAGNOSTIC and the
whole point of the wall -- never a target to tune away; the "band" is magnitude,
not a pass/fail verdict on the company.
"""
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
# Run directly (`python3 tools/generate_world_data.py`) sys.path[0] is tools/, not the
# project root, so the sibling `tools.generate_company_data` import the population gate
# needs would fail -- and a FAILED import silently degrades every whole-book row to
# UNSTATED. Making the import work in BOTH invocation modes keeps the fail-closed path
# reserved for real failures rather than a path accident (R15 fail-silent).
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))
DASHBOARD_PATH = PROJECT / "site" / "data" / "dashboard.json"
SIM_DATA_PATH = PROJECT / "site" / "data" / "sim_data.json"
ANCHORING_PATH = PROJECT / "site" / "state" / "population_anchoring.json"
ASSUMPTIONS_PATH = PROJECT / "docs" / "market_research" / "ASSUMPTIONS.md"
OUT_PATH = PROJECT / "site" / "data" / "world.json"

GH_PAGES = "https://21bcarlisle-arch.github.io/synthetic-enterprise/"


def _load(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return None


def _get(d, *path, default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return default if cur is None else cur


def _band(magnitude, amber, red):
    """Divergence-magnitude band (NOT a value judgement -- R12). A larger wall
    gap is not a defect; it is the wall working. GREEN/AMBER/RED here only says
    how big the observed gap is, so a reader can see it at a glance."""
    if magnitude is None:
        return "UNKNOWN"
    if magnitude >= red:
        return "RED"
    if magnitude >= amber:
        return "AMBER"
    return "GREEN"


# ---------------------------------------------------------------------------
# The two-sided wall: four real crossings, each SIM-truth | COMPANY-view | gap.
# ---------------------------------------------------------------------------
def _crossing_forward_basis(dashboard):
    terms = _get(dashboard, "trading", "forward_terms", default=[]) or []
    errs, sims, comps = [], [], []
    for t in terms:
        e = t.get("error_pct")
        s = t.get("sim_fwd")
        c = t.get("company_fwd")
        if isinstance(e, (int, float)):
            errs.append(abs(e))
        if isinstance(s, (int, float)):
            sims.append(s)
        if isinstance(c, (int, float)):
            comps.append(c)
    mean_abs_err_pct = round(100 * sum(errs) / len(errs), 2) if errs else None
    mean_sim = round(sum(sims) / len(sims), 2) if sims else None
    mean_comp = round(sum(comps) / len(comps), 2) if comps else None
    fpa = _get(dashboard, "market", "forward_premium_annual", default=[]) or []
    series = [
        dict(year=r.get("year"), value=r.get("mean_error_gbp_per_mwh"), count=r.get("count"))
        for r in fpa if isinstance(r.get("mean_error_gbp_per_mwh"), (int, float))
    ]
    return dict(
        id="forward_basis",
        name="Forward-curve basis risk",
        subtitle="The hedge wall -- the company prices its own forward curve; it never reads the sim's.",
        sim_truth_label="SIM ground-truth forward",
        sim_truth_value=(str(mean_sim) if mean_sim is not None else None),
        sim_truth_unit="£/MWh (mean across live forward terms)",
        company_view_label="COMPANY forward (built from observables)",
        company_view_value=(str(mean_comp) if mean_comp is not None else None),
        company_view_unit="£/MWh (120-day trailing mean + risk premium)",
        divergence_label="Mean absolute basis error",
        divergence_value=(str(mean_abs_err_pct) + "%" if mean_abs_err_pct is not None else None),
        divergence_magnitude=mean_abs_err_pct,
        rag=_band(mean_abs_err_pct, 10.0, 25.0),
        term_count=len(terms),
        basis="£/MWh forward price, point-in-time as-known (Point-in-Time Blindfold enforced -- the company cannot see future settlement)",
        mechanism="The company constructs its forward curve from observable market data only (a trailing mean plus a risk premium) and hedges against it. The sim holds the ground-truth forward. The company can never read it -- so it carries the gap as real basis risk, exactly as a licensed supplier does.",
        series=series,
        series_unit="mean forecast error, £/MWh (company premium vs realised outturn)",
        evidence="site/data/dashboard.json -> trading.forward_terms, market.forward_premium_annual",
        evidence_url="../data/dashboard.json",
    )


def _crossing_demand_estimation(dashboard):
    dea = _get(dashboard, "monthly_ops", "demand_estimation_annual", default=[]) or []
    series, latest = [], None
    for r in dea:
        v = r.get("mean_abs_error_pct")
        if isinstance(v, (int, float)):
            series.append(dict(year=r.get("year"), value=v, max=r.get("max_abs_error_pct"),
                               count=r.get("renewal_count")))
            latest = r
    latest_err = latest.get("mean_abs_error_pct") if latest else None
    max_err = latest.get("max_abs_error_pct") if latest else None
    return dict(
        id="demand_estimation",
        name="Demand estimation",
        subtitle="The volume wall -- the company forecasts annual volume at renewal; the sim knows the outturn.",
        sim_truth_label="SIM actual outturn volume",
        sim_truth_value="known exactly",
        sim_truth_unit="the realised billed volume (ground truth)",
        company_view_label="COMPANY renewal forecast",
        company_view_value=(str(latest_err) + "% mean error" if latest_err is not None else None),
        company_view_unit="forecast from prior billing history",
        divergence_label="Mean / max absolute forecast error (latest year)",
        divergence_value=((str(latest_err) + "% / " + str(max_err) + "%")
                          if latest_err is not None and max_err is not None else None),
        divergence_magnitude=latest_err,
        rag=_band(latest_err, 3.0, 8.0),
        basis="% error, forecast annual volume vs actual outturn (billed-volume basis)",
        mechanism="At renewal the company estimates each account's forward annual volume from its own prior billing -- it cannot query the sim's true forward demand. The mean absolute error is the volume-side wall gap it prices and hedges against.",
        series=series,
        series_unit="mean absolute forecast error, %",
        evidence="site/data/dashboard.json -> monthly_ops.demand_estimation_annual",
        evidence_url="../data/dashboard.json",
    )


def _crossing_meter_reads(dashboard):
    mrl = _get(dashboard, "customers", "meter_read_log", default=[]) or []
    total = len(mrl)
    estimated = sum(1 for m in mrl if m.get("status") == "estimated")
    traditional = sum(1 for m in mrl if m.get("meter_type") == "traditional")
    delays = [m.get("delay_days") for m in mrl if isinstance(m.get("delay_days"), (int, float))]
    est_pct = round(100 * estimated / total, 1) if total else None
    trad_pct = round(100 * traditional / total, 1) if total else None
    mean_delay = round(sum(delays) / len(delays), 2) if delays else None
    # The BSC settlement-run ladder -- the real mechanism that replaces estimates
    # with actuals over time (company/market/bsc_settlement_run_register.py).
    settlement_ladder = [
        dict(run="SF", name="Initial Settlement", timing="T + 14 days", reads="estimated reads"),
        dict(run="R1", name="First Reconciliation", timing="T + 5 months", reads="first smart/actual reads"),
        dict(run="R2", name="Second Reconciliation", timing="T + 14 months", reads="validated reads"),
        dict(run="R3", name="Third Reconciliation", timing="T + 26 months", reads="further corrections"),
        dict(run="RF", name="Final Reconciliation", timing="T + 28 months", reads="final, no further runs"),
    ]
    return dict(
        id="meter_reads",
        name="Meter reads: estimated vs actual",
        subtitle="The billing wall -- the company bills partly on estimates; the sim holds true consumption.",
        sim_truth_label="SIM true consumption",
        sim_truth_value="known half-hourly",
        sim_truth_unit="ground-truth kWh for every period",
        company_view_label="COMPANY billed reads",
        company_view_value=(str(est_pct) + "% estimated" if est_pct is not None else None),
        company_view_unit=("of " + str(total) + " read-months; " + (str(trad_pct) if trad_pct is not None else "?") + "% on traditional meters"),
        divergence_label="Share billed on estimated reads",
        divergence_value=(str(est_pct) + "%" if est_pct is not None else None),
        divergence_magnitude=est_pct,
        rag=_band(est_pct, 20.0, 40.0),
        mean_read_delay_days=mean_delay,
        read_count=total,
        estimated_count=estimated,
        traditional_count=traditional,
        basis="read-months, share billed on estimated vs actual reads (mean read delay " + (str(mean_delay) if mean_delay is not None else "?") + " days)",
        mechanism="Where a real read is not yet in, the company bills on an ESTIMATE and cannot ask the sim for the truth. UK settlement then corrects it: the BSC run ladder (SF -> R1 -> R2 -> R3 -> RF) progressively swaps estimates for actuals over ~28 months, each run a credit/debit adjustment the company observes via its PCAN statements -- never by reading the sim's meter.",
        settlement_ladder=settlement_ladder,
        evidence="site/data/dashboard.json -> customers.meter_read_log; company/market/bsc_settlement_run_register.py",
        evidence_url="../data/dashboard.json",
    )


def _crossing_blindfold(dashboard, sim):
    annual = _get(sim, "annual", default=[]) or []
    crisis = [a for a in annual if a.get("is_crisis")]

    # PRE-crisis means BEFORE the crisis -- not "every year that isn't a crisis
    # year". The old filter (`not a.get("is_crisis")`) swept in 2023/24/25, three
    # years AFTER the crisis it is compared against, so the figure labelled
    # "COMPANY knowable-at-T view" was computed with hindsight: £58.74 over eight
    # non-crisis years instead of £43.60 over the five genuinely-prior ones, and
    # the headline multiple read 2.66x instead of 3.58x (cold-eyes forensic audit
    # 2026-07-29, arithmetic reproduced from the panel's own published series).
    # This is the showcase panel for the Point-in-Time Blindfold, so a foresight
    # leak here is the worst possible place for one: the surface whose entire job
    # is to demonstrate the company cannot see the future was using the future.
    # Deriving the boundary from the crisis years themselves (rather than a
    # hardcoded 2021) keeps it correct if the curriculum window moves -- the
    # boundary is a FACT about the data, never a tuned constant (R13).
    def _yr(a):
        try:
            return int(a.get("year"))
        except (TypeError, ValueError):
            return None

    crisis_years = [y for y in (_yr(a) for a in crisis) if y is not None]
    first_crisis_year = min(crisis_years) if crisis_years else None
    pre = [
        a for a in annual
        if not a.get("is_crisis")
        and isinstance(a.get("mean"), (int, float))
        and (first_crisis_year is None or (_yr(a) is not None and _yr(a) < first_crisis_year))
    ]
    pre_mean = round(sum(a["mean"] for a in pre) / len(pre), 2) if pre else None
    crisis_peak = max((a.get("max") for a in crisis if isinstance(a.get("max"), (int, float))), default=None)
    crisis_mean = round(sum(a["mean"] for a in crisis) / len(crisis), 2) if crisis else None
    ratio = round(crisis_mean / pre_mean, 2) if (crisis_mean and pre_mean) else None
    contango = _get(dashboard, "market", "contango_monthly", default=[]) or []
    series = [
        dict(year=a.get("year"), mean=a.get("mean"), p95=a.get("p95"), max=a.get("max"),
             is_crisis=a.get("is_crisis"))
        for a in annual if isinstance(a.get("mean"), (int, float))
    ]
    return dict(
        id="blindfold",
        name="Point-in-time blindfold",
        subtitle="The time wall -- the sim holds the whole realised price path; the company sees only up to now.",
        sim_truth_label="SIM realised SSP series",
        sim_truth_value=(str(crisis_mean) if crisis_mean is not None else None),
        sim_truth_unit="£/MWh mean across crisis years 2021-22 (peak " + (str(crisis_peak) if crisis_peak is not None else "?") + " £/MWh)",
        company_view_label="COMPANY knowable-at-T view",
        company_view_value=(str(pre_mean) if pre_mean is not None else None),
        # State the window on the figure itself -- a "pre-crisis" mean whose
        # period is unstated is exactly how the hindsight above went unnoticed.
        company_view_unit=(
            "£/MWh mean over the "
            + str(len(pre))
            + " pre-crisis years"
            + (" (to " + str(first_crisis_year - 1) + ")" if first_crisis_year else "")
            + ", the calm the company priced within -- strictly pre-crisis, no hindsight"
        ),
        divergence_label="Crisis vs pre-crisis mean price",
        divergence_value=(str(ratio) + "x" if ratio is not None else None),
        divergence_magnitude=(100 * (ratio - 1) if ratio is not None else None),
        rag=_band((100 * (ratio - 1) if ratio is not None else None), 50.0, 150.0),
        basis="£/MWh system sell price (SSP), real Elexon settlement; means are annual",
        mechanism="The sim is settled half-hourly against the REAL Elexon SSP series and holds the entire realised path, crisis and all. The company is blindfolded to the future: it prices and hedges on what was knowable at time T. It survives the 2021-22 spike (which killed ~30 real UK suppliers) because it priced under blindness, not because it saw it coming.",
        series=series,
        series_unit="£/MWh annual mean SSP (real Elexon settlement)",
        contango_sample=[
            dict(month=c.get("month"), spot=c.get("spot"), forward=c.get("forward"),
                 premium_pct=c.get("premium_pct"))
            for c in contango[:12]
        ],
        sim_window=_get(sim, "metadata", "period_from") and (
            str(_get(sim, "metadata", "period_from")) + " to " + str(_get(sim, "metadata", "period_to"))),
        sim_total_records=_get(sim, "metadata", "total_records"),
        evidence="site/data/sim_data.json (real Elexon SSP); site/data/dashboard.json -> market.contango_monthly",
        evidence_url="../data/sim_data.json",
    )


# ---------------------------------------------------------------------------
# THE POPULATION AXIS -- the R10 class fix for BENCHMARK SHOPPING.
# (SITE_EH1_segment_disclosure, 2026-07-30, scope item 3)
#
# THE DEFECT, verbatim from the atom: "/data/world.json rates a 2.5x churn miss
# (sim 5.5% vs Ofgem 13.6%, ratio 0.4) GREEN via the note 'SIM portfolio is
# predominantly I&C' -- so the one disclosure of the book's true composition
# exists ONLY where it excuses a failed benchmark, and nowhere it would change
# how a reader reads the money."
#
# A note that explains away a miss is not a control; it is benchmark shopping.
# The instance fix (re-word that note) is FORBIDDEN by R10 -- an absurdity-class
# defect may only be closed by making the whole CLASS fail automatically. So the
# POPULATION becomes an explicit FIELD of every anchors row, and the rule is:
#
#   A row whose benchmark population does not match its measured population
#   CANNOT BE GRADED GREEN. Ever. Whatever its note says.
#
# Any future anchors card added without declaring its population lands in
# _ANCHOR_POPULATIONS-absent territory and is therefore UNSTATED -> not gradeable
# green. The class fails by default; a new card cannot slip through by silence.
#
# INDEPENDENCE (R15 anti-tautology). Three separate sources, so the check can
# genuinely disagree with the thing it checks:
#   * the RAG being gated comes from site/state/population_anchoring.json;
#   * the BENCHMARK's population is declared below, keyed to the benchmark's own
#     cited source string in that file's `meta` (Ofgem Retail Market Indicators
#     switching data is a DOMESTIC series; DESNZ business energy debt is a
#     NON-DOMESTIC series) -- an editorial choice already implicit in picking
#     that benchmark, now written down where it can be checked;
#   * the MEASURED population, for any row measured over the whole book, is
#     DERIVED at run time from dashboard.financial.segment_annual -- a different
#     file entirely. So if the book ever really did become domestic, the churn
#     row would legitimately grade again. Nothing here is hard-coded to today's
#     verdict.
#
# WHAT THIS IS NOT: it is not a re-rating of the sim, and it does not touch the
# measured divergence. `rag_measured` keeps the original RAG verbatim (R12: a
# diagnostic is never destroyed to make a page look better). Only the PUBLISHED
# grade is gated, and only in the GREEN direction -- an AMBER/RED row keeps its
# magnitude, because a bad grade was never the thing being laundered.
# ---------------------------------------------------------------------------

# Population classes. A benchmark measured over one class may not grade a figure
# measured over another -- households are not a business book.
_POP_DOMESTIC = "domestic"
_POP_NON_DOMESTIC = "non_domestic"
_POP_MIXED = "mixed"
_POP_UNSTATED = "unstated"

# Per-metric population declarations. `benchmark_class` is the population the
# EXTERNAL benchmark measures; `measured_scope` says how to obtain the population
# the SIM figure is measured over: "whole_book" derives it from the run's actual
# revenue mix, anything else names a fixed class directly.
_ANCHOR_POPULATIONS = {
    "churn_long_run": dict(
        benchmark_class=_POP_DOMESTIC,
        benchmark_label=(
            "GB DOMESTIC (household) supply market -- Ofgem Retail Market Indicators "
            "switching data is a domestic series"
        ),
        measured_scope="whole_book",
        measured_label="the company's whole book (all segments, every renewal)",
    ),
    "bad_debt": dict(
        benchmark_class=_POP_MIXED,
        benchmark_label=(
            "all GB suppliers, all segments -- an industry-wide bad-debt-to-revenue range "
            "(Ofgem/EUA), dominated in reality by domestic supply"
        ),
        measured_scope="whole_book",
        measured_label="the company's whole book (bad debt as a share of all revenue)",
    ),
    "complaints": dict(
        benchmark_class=_POP_NON_DOMESTIC,
        benchmark_label=(
            "non-domestic (I&C) complaint rates -- the Ofgem QoS survey band explicitly "
            "I&C-adjusted in this project's own benchmark note"
        ),
        measured_scope="whole_book",
        measured_label="the company's whole book (complaints per active account)",
    ),
    "arrears": dict(
        benchmark_class=_POP_NON_DOMESTIC,
        benchmark_label="GB NON-DOMESTIC (business) energy debt -- DESNZ business energy debt series",
        measured_scope=_POP_NON_DOMESTIC,
        measured_label="the company's I&C accounts only (ic_aggregate_rate_pct)",
    ),
}


def _book_population_class(dashboard):
    """The population class the company's WHOLE BOOK actually belongs to this run,
    derived from the run's own revenue mix -- NOT declared, so a real change in the
    book changes the verdict. Reuses the one canonical mix helper rather than
    re-deriving a second segment taxonomy (SIMPLICITY GUARD).

    FAIL-CLOSED: an unreadable/unavailable mix returns UNSTATED, which makes every
    whole-book row non-gradeable. An unavailable check is a FAILED check (R15).
    """
    try:
        from tools.generate_company_data import segment_revenue_mix
    except Exception:
        return _POP_UNSTATED, "the segment-mix helper could not be imported"
    mix = segment_revenue_mix(((dashboard or {}).get("financial") or {}).get("segment_annual"))
    if not mix.get("available"):
        return _POP_UNSTATED, "the book's revenue mix is unavailable (" + str(mix.get("reason")) + ")"
    cls = mix.get("composition_class")
    if cls not in (_POP_DOMESTIC, _POP_NON_DOMESTIC, _POP_MIXED):
        return _POP_UNSTATED, "the book's composition class could not be determined"
    detail = "{:.2f}% of revenue non-domestic, {:.2f}% domestic".format(
        mix.get("non_domestic_revenue_share_pct") or 0.0,
        mix.get("domestic_revenue_share_pct") or 0.0,
    )
    return cls, detail


def _population_gate(metric_key, rag, dashboard):
    """THE CONTROL. Returns the population fields plus the GATED rag for one row.

    Three outcomes, and the GREEN direction is the only one gated:
      UNSTATED  -- either side undeclared/unknown  -> not gradeable (fail-closed)
      MISMATCH  -- benchmark population != measured -> not gradeable
      MATCHED   -- same population                  -> gradeable, rag untouched

    A non-gradeable row publishes rag=None (the world door's own ragBadge renders
    that as a muted UNKNOWN badge) and keeps the measured RAG in `rag_measured`.
    """
    decl = _ANCHOR_POPULATIONS.get(metric_key)
    if not decl:
        return dict(
            benchmark_population=_POP_UNSTATED,
            benchmark_population_label=None,
            measured_population=_POP_UNSTATED,
            measured_population_label=None,
            population_status="UNSTATED",
            gradeable=False,
            population_reason=(
                "NOT GRADEABLE: this benchmark does not declare which population it "
                "measures, so nothing can be said about whether it applies to the book "
                "it is being compared against. A benchmark without a population cannot "
                "clear anything."
            ),
            rag=None,
            rag_measured=rag,
        )

    bench = decl["benchmark_class"]
    bench_label = decl["benchmark_label"]
    if decl["measured_scope"] == "whole_book":
        measured, detail = _book_population_class(dashboard)
        measured_label = decl["measured_label"] + " -- " + detail
    else:
        measured, measured_label = decl["measured_scope"], decl["measured_label"]

    if bench == _POP_UNSTATED or measured == _POP_UNSTATED:
        status, gradeable = "UNSTATED", False
        reason = (
            "NOT GRADEABLE: the population on one side is unstated (benchmark=" + str(bench)
            + ", measured=" + str(measured) + "), so this comparison cannot be graded."
        )
    elif bench != measured:
        status, gradeable = "MISMATCH", False
        reason = (
            "NOT GRADEABLE -- POPULATION MISMATCH: the benchmark measures " + bench
            + " (" + bench_label + ") and the sim figure is measured over " + measured
            + " (" + measured_label + "). A benchmark for one population cannot grade a "
            "figure measured over another, and a note explaining the difference does not "
            "convert a miss into a pass. This is the benchmark-shopping class, closed by "
            "rule rather than by re-wording."
        )
    else:
        status, gradeable = "MATCHED", True
        reason = (
            "Populations agree (" + bench + "): benchmark = " + bench_label
            + "; measured over " + measured_label + ". Gradeable."
        )

    return dict(
        benchmark_population=bench,
        benchmark_population_label=bench_label,
        measured_population=measured,
        measured_population_label=measured_label,
        population_status=status,
        gradeable=gradeable,
        population_reason=reason,
        rag=(rag if gradeable else None),
        rag_measured=rag,
    )


def _anchor_card(metric_key, metric, sim_value, benchmark_value, ratio, rag, note, dashboard):
    """Build one anchors row with its population axis attached. The population
    statement is PREPENDED to the rendered note, so the disclosure lands on the
    live page today rather than waiting for a renderer to learn a new field."""
    gate = _population_gate(metric_key, rag, dashboard)
    parts = [gate["population_reason"]]
    if note:
        parts.append("Measured note (kept verbatim): " + str(note))
    if not gate["gradeable"] and rag:
        parts.append("Measured RAG was " + str(rag) + "; it is NOT published as a grade here.")
    card = dict(
        metric_key=metric_key,
        metric=metric,
        sim_value=sim_value,
        benchmark_value=benchmark_value,
        ratio=ratio,
        note=" ".join(parts),
    )
    card.update(gate)
    return card


# ---------------------------------------------------------------------------
# The anchors register.
# ---------------------------------------------------------------------------
_RAG_ORDER = {"GREEN": 0, "AMBER": 1, "RED": 2}


def _worse_rag(a, b):
    """Worst-of two RAG ratings (RED > AMBER > GREEN > unknown). An unrated
    input is never treated as better than a rated one."""
    return a if _RAG_ORDER.get(a, 0) >= _RAG_ORDER.get(b, 0) else b


def _anchors_runtime(anchoring, dashboard=None):
    """Runtime calibration: sim outcomes vs external benchmarks. The measured RAG is
    kept verbatim in `rag_measured`; the PUBLISHED `rag` is population-gated (a
    benchmark may not grade a population it does not measure -- see above)."""
    if not isinstance(anchoring, dict):
        return dict(available=False)
    lrc = anchoring.get("long_run_comparison", {}) or {}
    cards = []
    if lrc:
        cards.append(_anchor_card(
            "churn_long_run",
            "Churn rate (long-run)",
            (str(lrc.get("sim_avg_pct")) + "%" if lrc.get("sim_avg_pct") is not None else None),
            (str(lrc.get("ofgem_avg_pct")) + "% (Ofgem)" if lrc.get("ofgem_avg_pct") is not None else None),
            lrc.get("ratio"), lrc.get("rag"), lrc.get("note"), dashboard,
        ))

    def _latest(lst, val_key, lo_key=None, hi_key=None, unit="%"):
        rows = [r for r in (lst or []) if isinstance(r, dict)]
        return rows[-1] if rows else {}

    bd = (anchoring.get("bad_debt_vs_benchmark") or [])
    if bd:
        r = bd[-1]
        rate = r.get("bad_debt_rate")
        rag = r.get("rag")
        note = "of revenue"
        # SITE_EH3 MAJOR-4 (2026-07-29 cold-eyes Expert Hour): a non-positive
        # bad-debt rate is a SIGN/MEASUREMENT ERROR (the annual write-off
        # series can go negative -- see financial.bad_debt_reconciliation on
        # dashboard.json), never a calibration nudge -- must be a hard RED
        # with a named cause, never AMBER. R15: reject non-finite FIRST,
        # before any <= comparison, so a malformed rate can't silently pass
        # through whatever rag the upstream file happened to carry.
        # Adopted THROUGH _anchor_card (not around it), so the sign-error RED
        # composes with the population gate rather than bypassing it -- the gate
        # only ever withholds a GREEN, so a RED set here survives it intact.
        if rate is None or not isinstance(rate, (int, float)) or not math.isfinite(rate):
            rag = "RED"
            note = "of revenue -- rate missing/malformed: treated as a hard failure, never a silent pass"
        elif rate <= 0:
            rag = "RED"
            note = (
                "of revenue -- NON-POSITIVE bad-debt rate is a sign/measurement error "
                "(the annual write-off series can go negative when a recovery/reversal "
                "event outweighs that period's new write-offs; see "
                "financial.bad_debt_reconciliation on dashboard.json for the two "
                "divergent published bad-debt figures), never a calibration nudge -- "
                "rated RED, not AMBER."
            )
        cards.append(_anchor_card(
            "bad_debt",
            "Bad debt rate (" + str(r.get("year")) + ")",
            (str(rate) + "%" if rate is not None else None),
            (str(r.get("benchmark_low_pct")) + "-" + str(r.get("benchmark_high_pct")) + "% (Ofgem/EUA)"),
            None, rag, note, dashboard,
        ))
    cp = (anchoring.get("complaints_vs_benchmark") or [])
    if cp:
        r = cp[-1]
        cards.append(_anchor_card(
            "complaints",
            "Complaint rate (" + str(r.get("year")) + ")",
            (str(r.get("complaint_rate_pct")) + "%" if r.get("complaint_rate_pct") is not None else None),
            (str(r.get("benchmark_lo")) + "-" + str(r.get("benchmark_green_hi")) + "% (Ofgem QoS)"),
            None, r.get("rag"), ("crisis year" if r.get("is_crisis_year") else "normal year"), dashboard,
        ))
    ar = (anchoring.get("arrears_vs_benchmark") or [])
    if ar:
        r = ar[-1]
        cards.append(_anchor_card(
            "arrears",
            "Arrears rate (" + str(r.get("year")) + ")",
            (str(r.get("ic_aggregate_rate_pct")) + "% (I&C agg.)" if r.get("ic_aggregate_rate_pct") is not None else None),
            "I&C <8% normal / <12% crisis (DESNZ)",
            None, r.get("rag"), r.get("portfolio_type_note"), dashboard,
        ))

    # SITE_EH3: the overall verdict is escalated to the WORST published row first --
    # an upstream "overall_rag: GREEN" standing over a RED card (e.g. the non-positive
    # bad-debt sign error above) is exactly the unflagged-implausible-figure defect.
    # This runs BEFORE the gradeability gate so the two compose in the safe direction:
    # escalation can only worsen, the gate can only withhold a GREEN.
    overall_measured = anchoring.get("overall_rag") or "GREEN"
    for c in cards:
        overall_measured = _worse_rag(overall_measured, c.get("rag") or "GREEN")

    # Row-level gating is not enough on its own: a GREEN *overall* verdict standing over
    # non-gradeable rows would re-open the same hole one level up (R10 -- close the class,
    # not the instance). Same rule, same direction: only GREEN is gated, the measured
    # value is preserved.
    ungradeable = [c["metric"] for c in cards if not c.get("gradeable")]
    overall_published = overall_measured
    overall_reason = None
    if ungradeable and str(overall_measured).upper() == "GREEN":
        overall_published = None
        overall_reason = (
            "NOT GRADEABLE: the overall calibration cannot be GREEN while "
            + str(len(ungradeable)) + " benchmark(s) are not gradeable against the "
            "population they are measured over -- " + "; ".join(ungradeable) + "."
        )

    return dict(
        available=True,
        overall_rag=overall_published,
        overall_rag_measured=overall_measured,
        overall_rag_reason=overall_reason,
        cards=cards,
        # The gate's own report, so a reader (and a future renderer) can see how many
        # benchmarks are actually comparable to the book they grade.
        population_gate=dict(
            rule=(
                "A benchmark may only grade a figure measured over the SAME population. "
                "A population mismatch, or an undeclared population on either side, is "
                "NOT GRADEABLE -- and specifically can never be GREEN. Notes explaining a "
                "difference away carry no grading power (R10 class fix for benchmark shopping; "
                "R15: this control fires on its own named defect, see "
                "site/company/test_segment_disclosure.py)."
            ),
            total=len(cards),
            matched=len([c for c in cards if c.get("population_status") == "MATCHED"]),
            mismatched=len([c for c in cards if c.get("population_status") == "MISMATCH"]),
            unstated=len([c for c in cards if c.get("population_status") == "UNSTATED"]),
            green_blocked=[
                c["metric"] for c in cards
                if not c.get("gradeable") and str(c.get("rag_measured")).upper() == "GREEN"
            ],
            not_gradeable=ungradeable,
        ),
        meta=anchoring.get("meta", {}),
        evidence="site/state/population_anchoring.json",
        evidence_url="../state/population_anchoring.json",
    )


# Margin plausibility bands (SITE_EH3 MAJOR-5, 2026-07-29 cold-eyes Expert
# Hour): margin had NO anchor at all -- the one metric where R12's band
# matters most. R12 BINDS HARD here: these bands are read from EXTERNAL
# sources FIRST (never reverse-engineered from what the sim happens to
# publish) and this function changes NOTHING about how margin is computed --
# it only reads the already-published net_margin_pct figures and rates them.
# Sources (read, cited honestly, not fabricated -- docs/market_research/
# ASSUMPTIONS.md): "Ofgem price cap EBIT allowance" row (~1.9-2.6%, current
# Direct-Debit/Standard-Credit/Prepayment cap components); "Net margin as %
# of revenue" rows (2-5%, Ofgem Retail Market Report / Cornwall Insight);
# "EBIT% -- dom electricity (CSS recovery/2024)" rows (real crisis-year
# domestic losses of roughly -4% to -10%); "EBIT% -- non-dom electricity
# (CSS 2023-2024)" row (1.7-4.5%, EDF/British Gas CSS filings -- I&C supply
# runs THINNER than domestic). GREEN covers the real normal-year domestic/cap
# band with headroom for a real crisis-year loss; AMBER doubles the
# tolerance either side (matching this file's own long-run churn-ratio
# convention below); anything further out is RED.
_MARGIN_GREEN_LO_PCT = -10.0
_MARGIN_GREEN_HI_PCT = 5.0
_MARGIN_AMBER_LO_PCT = -20.0
_MARGIN_AMBER_HI_PCT = 10.0
_MARGIN_BENCHMARK_NOTE = (
    "-10 to 5% (Ofgem cap EBIT allowance ~1.9-2.6%; real domestic net margin "
    "2-5%, Ofgem Retail Market Report/Cornwall Insight; real crisis-year "
    "domestic losses to -10%, EDF/BG CSS filings -- docs/market_research/"
    "ASSUMPTIONS.md)"
)


def _margin_rag(pct):
    """R15: reject non-finite/missing FIRST -- a margin figure that can't be
    read is a hard failure, never a silent GREEN pass."""
    if pct is None or not isinstance(pct, (int, float)) or not math.isfinite(pct):
        return "RED"
    if _MARGIN_GREEN_LO_PCT <= pct <= _MARGIN_GREEN_HI_PCT:
        return "GREEN"
    if _MARGIN_AMBER_LO_PCT <= pct <= _MARGIN_AMBER_HI_PCT:
        return "AMBER"
    return "RED"


def _anchors_margin(financial):
    """Builds the margin anchor card(s) MAJOR-5 says are missing. Reads
    dashboard.json's financial.annual/segment_annual -- never re-derives or
    adjusts a margin figure. Partial-year rows (MAJOR-6's period_partial
    flag) are excluded, the same class-closing invariant as the period-
    coverage fix: a part-year figure is not a fair annual reading to anchor."""
    if not isinstance(financial, dict):
        return []
    cards = []
    annual = financial.get("annual") or []
    complete_annual = [r for r in annual if not r.get("period_partial")]
    if complete_annual:
        latest = complete_annual[-1]
        pct = latest.get("net_margin_pct")
        cards.append(dict(
            metric="Net margin rate (portfolio, " + str(latest.get("year")) + ")",
            sim_value=(str(pct) + "%" if pct is not None else None),
            benchmark_value=_MARGIN_BENCHMARK_NOTE,
            ratio=None, rag=_margin_rag(pct),
            note=(
                "R12: a plausibility anchor, never a tuning target -- no margin "
                "calculation changes as a result of this row existing. Previously "
                "the one metric where R12's band mattered most had no anchor at all "
                "(2026-07-29 cold-eyes Expert Hour MAJOR-5)."
            ),
        ))
    seg_annual = [r for r in (financial.get("segment_annual") or []) if not r.get("period_partial")]
    ic_rows = [r for r in seg_annual if isinstance(r.get("i&c_electricity"), dict)]
    if ic_rows:
        seg_row = ic_rows[-1]
        ic = seg_row["i&c_electricity"]
        pct = ic.get("net_margin_pct")
        cards.append(dict(
            metric="Net margin rate (I&C electricity segment, " + str(seg_row.get("year")) + ")",
            sim_value=(str(pct) + "%" if pct is not None else None),
            benchmark_value="1.7-4.5% (EDF/British Gas CSS 2023-24, non-dom electricity -- "
                             "docs/market_research/ASSUMPTIONS.md)",
            ratio=None, rag=_margin_rag(pct),
            note=(
                "I&C supply runs THINNER than domestic in real CSS filings, not "
                "richer -- this was the least believable ratio the 2026-07-29 "
                "cold-eyes Expert Hour found on the site (MAJOR-5)."
            ),
        ))
    return cards


_STATUS_MAP = [
    ("✓", "OK"), ("⚠", "WARN"), ("?", "REFRESH"), ("n/a", "N/A"), ("Gap", "GAP"),
]


def _clean_cell(s):
    return re.sub(r"\*\*|\*|`", "", s or "").strip()


def _status_of(raw):
    r = raw or ""
    for glyph, label in _STATUS_MAP:
        if glyph in r:
            return label
    return "OTHER"


def _anchors_library(md_text):
    """Parse ASSUMPTIONS.md's markdown tables as-is into an anchors register:
    each row is a sim value vs an industry benchmark with a source and a checked
    status. Warn/refresh/gap statuses are surfaced, never hidden."""
    if not md_text:
        return dict(available=False, sections=[], counts={})
    sections = []
    counts = {}
    current = None
    for line in md_text.splitlines():
        h = re.match(r"^##\s+(.*)$", line.strip())
        if h:
            current = dict(section=_clean_cell(h.group(1)), rows=[])
            sections.append(current)
            continue
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        joined = " ".join(cells).lower()
        if "assumption" in joined and "benchmark" in joined:
            continue  # header row
        if set("".join(cells).replace("-", "").replace(":", "").replace(" ", "")) == set():
            continue  # separator row
        if re.match(r"^:?-{2,}", cells[0]):
            continue
        assumption = _clean_cell(cells[0])
        if not assumption:
            continue
        status = _status_of(cells[-1])  # status is always the last column (robust to a stray 7-col row)
        counts[status] = counts.get(status, 0) + 1
        if current is None:
            current = dict(section="(unsectioned)", rows=[])
            sections.append(current)
        current["rows"].append(dict(
            assumption=assumption,
            sim_value=_clean_cell(cells[1]),
            benchmark=_clean_cell(cells[2]),
            source=_clean_cell(cells[3]),
            last_checked=_clean_cell(cells[4]),
            status=status,
        ))
    sections = [s for s in sections if s["rows"]]
    total = sum(len(s["rows"]) for s in sections)
    return dict(
        available=total > 0,
        section_count=len(sections),
        row_count=total,
        counts=counts,
        sections=sections,
        evidence="docs/market_research/ASSUMPTIONS.md",
        evidence_url=GH_PAGES + "market_research/ASSUMPTIONS.md",
    )


def generate():
    dashboard = _load(DASHBOARD_PATH) or {}
    sim = _load(SIM_DATA_PATH) or {}
    anchoring = _load(ANCHORING_PATH) or {}
    try:
        md_text = ASSUMPTIONS_PATH.read_text()
    except Exception:
        md_text = ""

    meta = dashboard.get("meta", {}) or {}
    sim_meta = sim.get("metadata", {}) or {}

    crossings = [
        _crossing_forward_basis(dashboard),
        _crossing_demand_estimation(dashboard),
        _crossing_meter_reads(dashboard),
        _crossing_blindfold(dashboard, sim),
    ]

    financial = dashboard.get("financial") or {}
    runtime = _anchors_runtime(anchoring, dashboard)
    margin_cards = _anchors_margin(financial)
    if margin_cards:
        runtime = dict(runtime)
        runtime["cards"] = list(runtime.get("cards") or []) + margin_cards
        # Escalate the MEASURED verdict with the margin rows, then re-apply the
        # population gate's withholding. Escalating `overall_rag` directly would
        # fail OPEN: a withheld (None) grade would be read as "GREEN" by the `or`
        # below and republished as GREEN, silently undoing the gate.
        overall = runtime.get("overall_rag_measured") or "GREEN"
        for c in margin_cards:
            overall = _worse_rag(overall, c.get("rag") or "GREEN")
        runtime["overall_rag_measured"] = overall
        withheld = runtime.get("overall_rag") is None and runtime.get("overall_rag_reason")
        runtime["overall_rag"] = None if (withheld and overall == "GREEN") else overall

    # SITE_EH3 MAJOR-6 (R10 class-closing invariant, period coverage):
    # summarise which published annual row (if any) is a PART YEAR, computed
    # from dashboard.json's own period_coverage_fraction/period_partial
    # fields (themselves derived from the real sim window, never hardcoded)
    # -- so /world/ can state it plainly rather than let a partial row render
    # as an undifferentiated annual figure (MAJOR-6: a 5.2-month 2025 stub
    # read as a 57% YoY "collapse").
    annual_rows = financial.get("annual") or []
    partial_rows = [r for r in annual_rows if r.get("period_partial")]
    latest_partial = partial_rows[-1] if partial_rows else None
    period_coverage = dict(
        available=bool(annual_rows),
        latest_partial_year=(latest_partial.get("year") if latest_partial else None),
        latest_partial_fraction=(latest_partial.get("period_coverage_fraction") if latest_partial else None),
        latest_partial_note=(latest_partial.get("period_note") if latest_partial else None),
        evidence="site/data/dashboard.json financial.annual[].period_coverage_fraction",
        evidence_url="../data/dashboard.json",
    )

    data = dict(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        dashboard_generated_at=meta.get("generated_at"),
        git_commit=meta.get("git_commit"),
        phase=_get(dashboard, "build", "current_phase"),
        sim_window=(str(sim_meta.get("period_from")) + " to " + str(sim_meta.get("period_to"))
                    if sim_meta.get("period_from") else None),
        sim_total_records=sim_meta.get("total_records"),
        period_coverage=period_coverage,
        wall=dict(
            intro="The company operates under the same information constraints as a real UK "
                  "energy supplier: it cannot see inside the simulation it runs in. It discovers "
                  "its world only through observable interfaces -- market feeds, meter reads, "
                  "bills, settlement statements -- and its models are approximations built from "
                  "those observations, never reads of ground truth. Below are four real crossings "
                  "of that wall: on each, the SIM's ground truth on one side, the COMPANY's own "
                  "view on the other, and the honest gap between them. The gap is not a defect -- "
                  "it is the wall working. A supplier that could see the truth would not be a "
                  "supplier; it would be cheating.",
            band_note="RAG below is divergence MAGNITUDE, not a verdict (R12: a metric is a "
                      "diagnostic, never a target). It says how wide the gap is, so you can see "
                      "it at a glance -- a wide gap that is correctly priced is the design, not a bug.",
            crossings=crossings,
        ),
        anchors=dict(
            intro="The anchors register: the real external data the sim is calibrated against. "
                  "Runtime calibration compares the sim's own outcomes to published Ofgem/DESNZ "
                  "benchmarks and keeps the RAG rating as measured; the assumption library is the "
                  "human-readable provenance trail, each row a sim value against an industry "
                  "benchmark with its source and a checked status. Where a status is a warning or "
                  "an open refresh, it is shown, not smoothed. Every runtime row also states "
                  "WHICH POPULATION its benchmark measures and which population the sim figure "
                  "is measured over: a benchmark may only grade the population it measures, so a "
                  "mismatch is NOT GRADEABLE rather than green-with-an-excuse.",
            # `runtime` (not a fresh _anchors_runtime call) -- it carries the margin
            # plausibility cards added above, which an inline recompute would drop.
            runtime=runtime,
            library=_anchors_library(md_text),
        ),
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: " + str(OUT_PATH))
    return data


if __name__ == "__main__":
    generate()
