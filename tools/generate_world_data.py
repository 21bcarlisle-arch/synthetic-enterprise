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
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
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
    pre = [a for a in annual if not a.get("is_crisis") and isinstance(a.get("mean"), (int, float))]
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
        company_view_unit="£/MWh mean, pre-crisis calm the company priced within",
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
# The anchors register.
# ---------------------------------------------------------------------------
def _anchors_runtime(anchoring):
    """Runtime calibration: sim outcomes vs external benchmarks, RAG as kept."""
    if not isinstance(anchoring, dict):
        return dict(available=False)
    lrc = anchoring.get("long_run_comparison", {}) or {}
    cards = []
    if lrc:
        cards.append(dict(
            metric="Churn rate (long-run)",
            sim_value=(str(lrc.get("sim_avg_pct")) + "%" if lrc.get("sim_avg_pct") is not None else None),
            benchmark_value=(str(lrc.get("ofgem_avg_pct")) + "% (Ofgem)" if lrc.get("ofgem_avg_pct") is not None else None),
            ratio=lrc.get("ratio"), rag=lrc.get("rag"), note=lrc.get("note"),
        ))

    def _latest(lst, val_key, lo_key=None, hi_key=None, unit="%"):
        rows = [r for r in (lst or []) if isinstance(r, dict)]
        return rows[-1] if rows else {}

    bd = (anchoring.get("bad_debt_vs_benchmark") or [])
    if bd:
        r = bd[-1]
        cards.append(dict(
            metric="Bad debt rate (" + str(r.get("year")) + ")",
            sim_value=(str(r.get("bad_debt_rate")) + "%" if r.get("bad_debt_rate") is not None else None),
            benchmark_value=(str(r.get("benchmark_low_pct")) + "-" + str(r.get("benchmark_high_pct")) + "% (Ofgem/EUA)"),
            ratio=None, rag=r.get("rag"), note="of revenue",
        ))
    cp = (anchoring.get("complaints_vs_benchmark") or [])
    if cp:
        r = cp[-1]
        cards.append(dict(
            metric="Complaint rate (" + str(r.get("year")) + ")",
            sim_value=(str(r.get("complaint_rate_pct")) + "%" if r.get("complaint_rate_pct") is not None else None),
            benchmark_value=(str(r.get("benchmark_lo")) + "-" + str(r.get("benchmark_green_hi")) + "% (Ofgem QoS)"),
            ratio=None, rag=r.get("rag"), note=("crisis year" if r.get("is_crisis_year") else "normal year"),
        ))
    ar = (anchoring.get("arrears_vs_benchmark") or [])
    if ar:
        r = ar[-1]
        cards.append(dict(
            metric="Arrears rate (" + str(r.get("year")) + ")",
            sim_value=(str(r.get("ic_aggregate_rate_pct")) + "% (I&C agg.)" if r.get("ic_aggregate_rate_pct") is not None else None),
            benchmark_value="I&C <8% normal / <12% crisis (DESNZ)",
            ratio=None, rag=r.get("rag"), note=None,
        ))
    return dict(
        available=True,
        overall_rag=anchoring.get("overall_rag"),
        cards=cards,
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
                  "an open refresh, it is shown, not smoothed.",
            runtime=_anchors_runtime(anchoring),
            library=_anchors_library(md_text),
        ),
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: " + str(OUT_PATH))
    return data


if __name__ == "__main__":
    generate()
