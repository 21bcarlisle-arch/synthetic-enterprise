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
#   MUST SAY SO, in the text a reader actually sees, next to the rating --
#   and a row that declares no population at all FAILS THE PUBLISH.
#
# Any future anchors card added without declaring its population lands in
# _ANCHOR_POPULATIONS-absent territory and is therefore UNSTATED, which the gate
# below REJECTS. The class fails by default; a new card cannot slip through by
# silence.
#
# THE WALL THIS ATOM WORKS INSIDE (why the RAG is NOT touched). This atom is
# DISCLOSURE ONLY: change no RAG rating, no benchmark value, no sim value. A
# rival implementation of this same atom suppressed the published `rag` to null
# whenever a population mismatched. That is a re-grading decision, not a
# disclosure -- it substitutes the machine's judgement about whether a benchmark
# is applicable for the measured rating, on the same surface, and it destroys the
# reader's ability to see WHAT was laundered (a GREEN standing over a 2.5x miss
# is the evidence; blanking it to UNKNOWN hides the crime along with the excuse).
# So the measured RAG is published EXACTLY as measured, and the mismatch is
# rendered LOUDLY beside it. Whether a mismatched benchmark should also lose its
# grade is a real question -- and a separate, non-disclosure one.
#
# INDEPENDENCE (R15 anti-tautology). Three separate sources, so the check can
# genuinely disagree with the thing it checks:
#   * the RAG being disclosed against comes from
#     site/state/population_anchoring.json;
#   * the BENCHMARK's population is declared below, keyed to the benchmark's own
#     cited source string in that file's `meta` (Ofgem Retail Market Indicators
#     switching data is a DOMESTIC series; DESNZ business energy debt is a
#     NON-DOMESTIC series) -- an editorial choice already implicit in picking
#     that benchmark, now written down where it can be checked;
#   * the MEASURED population, for any row measured over the whole book, is
#     DERIVED at run time from dashboard.financial.segment_annual -- a different
#     file entirely. So if the book ever really did become domestic, the churn
#     row would legitimately match again. Nothing here is hard-coded to today's
#     verdict, and no share is pinned to a generated value.
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


def _population_declaration(metric_key, rag, dashboard):
    """The population fields for one row. DISCLOSURE ONLY -- `rag` is passed
    through untouched in every branch (see the wall note above).

    Three outcomes:
      UNSTATED  -- either side undeclared/unknown  -> gate REJECTS the publish
      MISMATCH  -- benchmark population != measured -> rendered loudly, rag kept
      MATCHED   -- same population                  -> rendered plainly, rag kept
    """
    decl = _ANCHOR_POPULATIONS.get(metric_key)
    if not decl:
        return dict(
            benchmark_population=_POP_UNSTATED,
            benchmark_population_label=None,
            measured_population=_POP_UNSTATED,
            measured_population_label=None,
            population_status="UNSTATED",
            population_mismatch=False,
            population_reason=(
                "POPULATION " + _POP_UNSTATED.upper() + " (" + _POP_UNSTATED + "): this "
                "benchmark does not state which population it "
                "measures, so nothing can be said about whether it applies to the book it "
                "is being compared against. An undeclared population is a GAP, not a pass. "
                "The rating beside it is the measured rating and is published unchanged; "
                "read it as unverified against its own population."
            ),
            rag=rag,
        )

    bench = decl["benchmark_class"]
    bench_label = decl["benchmark_label"]
    if decl["measured_scope"] == "whole_book":
        measured, detail = _book_population_class(dashboard)
        measured_label = decl["measured_label"] + " -- " + detail
    else:
        measured, measured_label = decl["measured_scope"], decl["measured_label"]

    if bench == _POP_UNSTATED or measured == _POP_UNSTATED:
        status, mismatch = "UNSTATED", False
        reason = (
            "POPULATION " + _POP_UNSTATED.upper() + ": the population on one side is "
            + _POP_UNSTATED + " (benchmark="
            + str(bench) + ", measured=" + str(measured) + "), so this comparison cannot be "
            "checked against its own population. An undeclared population is a GAP, not a "
            "pass. The measured rating beside it is published unchanged."
        )
    elif bench != measured:
        status, mismatch = "MISMATCH", True
        reason = (
            "POPULATION MISMATCH -- the benchmark measures " + bench + " (" + bench_label
            + ") while the sim figure is measured over " + measured + " (" + measured_label
            + "). These are two different populations, so a note explaining the difference "
            "away is not a pass: it is the reason the comparison does not hold. The measured "
            "rating is published EXACTLY as measured (this atom is disclosure, it re-rates "
            "nothing) -- read it as unverified against its own population, not as a clean "
            "result."
        )
    else:
        status, mismatch = "MATCHED", False
        reason = (
            "Populations agree (" + bench + "): benchmark = " + bench_label
            + "; measured over " + measured_label + "."
        )

    return dict(
        benchmark_population=bench,
        benchmark_population_label=bench_label,
        measured_population=measured,
        measured_population_label=measured_label,
        population_status=status,
        population_mismatch=mismatch,
        population_reason=reason,
        rag=rag,
    )


def _anchor_card(metric_key, metric, sim_value, benchmark_value, ratio, rag, note, dashboard):
    """Build one anchors row with its population axis attached.

    The population statement is PREPENDED to the rendered `note` -- a field
    site/world/index.html already renders -- so the disclosure lands on the live
    page today with no template change (this atom's file_scope does not include
    the world door). The original note is PRESERVED after it, labelled: the
    excuse stays on the page rather than being quietly deleted, which is what
    makes the benchmark-shopping visible instead of merely absent.
    """
    pop = _population_declaration(metric_key, rag, dashboard)
    parts = [pop["population_reason"]]
    if note:
        parts.append("Measured note, kept verbatim: " + str(note))
    card = dict(
        metric_key=metric_key,
        metric=metric,
        sim_value=sim_value,
        benchmark_value=benchmark_value,
        ratio=ratio,
        note=" ".join(parts),
    )
    card.update(pop)
    return card


# ---------------------------------------------------------------------------
# The anchors register.
# ---------------------------------------------------------------------------
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
        cards.append(_anchor_card(
            "bad_debt",
            "Bad debt rate (" + str(r.get("year")) + ")",
            (str(r.get("bad_debt_rate")) + "%" if r.get("bad_debt_rate") is not None else None),
            (str(r.get("benchmark_low_pct")) + "-" + str(r.get("benchmark_high_pct")) + "% (Ofgem/EUA)"),
            None, r.get("rag"), "of revenue", dashboard,
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

    # Row-level disclosure is not enough on its own: an overall verdict standing over
    # mismatched rows with no caveat re-opens the same hole one level up (R10 -- close the
    # class, not the instance). The overall RAG is likewise published EXACTLY as measured;
    # what is added is the caveat next to it.
    mismatched = [c["metric"] for c in cards if c.get("population_status") == "MISMATCH"]
    unstated = [c["metric"] for c in cards if c.get("population_status") == "UNSTATED"]
    unmatched = mismatched + unstated
    overall_measured = anchoring.get("overall_rag")
    overall_caveat = None
    if unmatched:
        overall_caveat = (
            "This overall rating is published as measured, but " + str(len(unmatched))
            + " of " + str(len(cards)) + " benchmark(s) below are not measured over the "
            "population they grade -- " + "; ".join(unmatched) + ". It therefore aggregates "
            "comparisons that do not all hold, and is not evidence that the sim matches the "
            "GB market on those axes."
        )

    # The book composition, stated ONCE at the register level as well -- so the
    # composition is disclosed where it does NOT excuse anything, not only in the
    # note where it does (the aggravating half of the defect).
    book_class, book_detail = _book_population_class(dashboard)

    return dict(
        available=True,
        overall_rag=overall_measured,
        overall_rag_caveat=overall_caveat,
        cards=cards,
        book_composition=dict(
            population_class=book_class,
            detail=book_detail,
            evidence="site/data/dashboard.json -> financial.segment_annual",
        ),
        # The disclosure's own report, so a reader (and a future renderer) can see how
        # many benchmarks are actually comparable to the book they grade.
        population_disclosure=dict(
            rule=(
                "Every runtime row states WHICH POPULATION its external benchmark measures "
                "and which population the sim figure is measured over. A mismatch is "
                "DISCLOSED in the text a reader sees; a row that declares no population at "
                "all FAILS THE PUBLISH. No RAG rating, benchmark value or sim value is "
                "changed by this disclosure (R12: a rating is a diagnostic, never a target; "
                "R13: the book's composition is curriculum). R10 class fix for benchmark "
                "shopping; R15-proven in tests/tools/test_site_eh1_segment_disclosure.py."
            ),
            total=len(cards),
            matched=len([c for c in cards if c.get("population_status") == "MATCHED"]),
            mismatched=len(mismatched),
            unstated=len(unstated),
            mismatched_metrics=mismatched,
            unstated_metrics=unstated,
        ),
        meta=anchoring.get("meta", {}),
        evidence="site/state/population_anchoring.json",
        evidence_url="../state/population_anchoring.json",
    )


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

    data = dict(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        dashboard_generated_at=meta.get("generated_at"),
        git_commit=meta.get("git_commit"),
        phase=_get(dashboard, "build", "current_phase"),
        sim_window=(str(sim_meta.get("period_from")) + " to " + str(sim_meta.get("period_to"))
                    if sim_meta.get("period_from") else None),
        sim_total_records=sim_meta.get("total_records"),
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
                  "is measured over -- so where the two differ, the reader sees the mismatch "
                  "beside the rating instead of an excuse that reads as a pass.",
            runtime=_anchors_runtime(anchoring, dashboard),
            library=_anchors_library(md_text),
        ),
    )
    if not check_anchor_populations(data):
        raise SystemExit(1)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: " + str(OUT_PATH))
    return data


def check_anchor_populations(data):
    """R15 CONTROL for the aggravating half of SITE_EH1_segment_disclosure.

    NAMED DEFECT it must fire on: an anchors-register row rating a sim outcome
    against an external benchmark WITHOUT stating, in the text a reader sees,
    which population that benchmark measures -- the exact condition under which a
    2.5x domestic-churn miss was cleared GREEN by an I&C note.

    NOT A TAUTOLOGY: this function never calls ``_population_declaration`` or
    ``_anchor_card``. It re-reads each published card's own strings and
    INDEPENDENTLY re-decides whether the declared benchmark population conflicts
    with the book's measured composition (re-derived here from the dashboard's
    segment split, a different file). Mutating the classifier or the note text is
    therefore caught here rather than agreed with.

    NOT FAIL-OPEN: an available register with no cards FAILS; a card with no
    population field FAILS; an UNSTATED population FAILS (an undeclared
    population is a FAILED check, not a skipped one); a real mismatch whose
    MISMATCH is not present in the RENDERED note FAILS; an empty note FAILS.

    NOT FAIL-SILENT: it asserts the population words are actually inside the
    string the page renders, never merely that some field exists.

    NO PINNED VALUES: it asserts the RELATIONSHIP (declared population vs
    measured composition, and disclosure present where they differ), never a
    particular share, segment or RAG -- a run whose book legitimately becomes
    domestic passes without an edit.
    """
    problems = []
    runtime = (((data or {}).get("anchors") or {}).get("runtime")) or {}
    if not runtime.get("available"):
        # No runtime register at all -> nothing is being rated, which is allowed.
        return _anchor_pop_verdict(problems)

    cards = runtime.get("cards") or []
    if not cards:
        problems.append("runtime register is available but publishes no anchor cards")

    book = runtime.get("book_composition") or {}
    measured_book = book.get("population_class")
    if not measured_book:
        problems.append(
            "runtime register does not disclose the book composition its benchmarks are "
            "rated against (book_composition.population_class) -- composition must be "
            "published where it does NOT excuse a rating, not only where it does")

    for card in cards:
        metric = (card or {}).get("metric") or "<unnamed>"
        pop = (card or {}).get("benchmark_population")
        note = str((card or {}).get("note") or "")
        if not pop:
            problems.append("{}: no benchmark_population declared".format(metric))
            continue
        if pop == _POP_UNSTATED:
            problems.append(
                "{}: benchmark population is UNSTATED -- this row rates a sim value against "
                "an external benchmark without saying which population that benchmark "
                "measures (an undeclared population is a failed check, not a skipped "
                "one)".format(metric))
        if not note.strip():
            problems.append("{}: no rendered population note".format(metric))
            continue
        if pop not in note:
            problems.append(
                "{}: declared population {!r} does not appear in the RENDERED note {!r} -- "
                "a field nobody sees is not a disclosure".format(metric, pop, note))
        # Independent re-decision of the mismatch from the card's own published
        # fields plus the separately-derived book composition.
        measured = card.get("measured_population")
        want_mismatch = bool(
            pop and measured and pop != _POP_UNSTATED and measured != _POP_UNSTATED
            and pop != measured)
        if want_mismatch:
            if not card.get("population_mismatch"):
                problems.append(
                    "{}: benchmark measures {!r} while the figure is measured over {!r}, "
                    "but population_mismatch is not set".format(metric, pop, measured))
            if "MISMATCH" not in note.upper():
                problems.append(
                    "{}: the population mismatch is not stated in the rendered note {!r} -- "
                    "the mismatch must be VISIBLE, not only machine-readable".format(
                        metric, note))
        elif card.get("population_mismatch"):
            problems.append(
                "{}: population_mismatch is set but {!r} does not conflict with {!r}".format(
                    metric, pop, measured))
        # DISCLOSURE-ONLY WALL, self-policed: this atom may not change a rating.
        if "rag_measured" in (card or {}) and card.get("rag") != card.get("rag_measured"):
            problems.append(
                "{}: published rag {!r} differs from the measured rag {!r} -- this atom is "
                "DISCLOSURE ONLY and may not re-rate a benchmark".format(
                    metric, card.get("rag"), card.get("rag_measured")))
    return _anchor_pop_verdict(problems)


def _anchor_pop_verdict(problems):
    if problems:
        print(
            "ANCHOR-POPULATION GATE FAILED ({} problem(s)): {}\n"
            "  Every anchors-register row must state which population its benchmark measures, "
            "in the text a reader sees (atom SITE_EH1_segment_disclosure). Fix the "
            "DISCLOSURE -- never the RAG rating (R12) and never the book's composition "
            "(R13).".format(len(problems), "; ".join(problems)),
            file=sys.stderr)
        return False
    return True


if __name__ == "__main__":
    generate()
