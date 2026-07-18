"""Consolidated Segmental Statement (CSS) — the regulator-shaped reporting backbone.

Atom E4_supplier_reporting_standard. Spec: docs/staging/in_progress/SUPPLIER_REPORTING_STANDARD.md
(§1 CSS-shaped segmental statement, §2 board KPI block).

Real UK suppliers above threshold must publish a Consolidated Segmental Statement in
Ofgem's defined format (SLC 19A). This module renders that statement as the annual-report
backbone: four segments (electricity/gas × domestic/non-domestic) plus an aggregate column,
a full P&L per segment, operational lines (volume, WACOE/WACOG, meter points), a
reconciliation from the CSS (settlement basis) to the statutory management accounts, and a
short hedging-policy note.

EPISTEMIC NOTE: the CSS is the company's OWN publication — every figure here is company-
knowable (its own settlement records, ledger, CRM segment/commodity tags). No simulation
internals are read.

DUAL-BASIS DESIGN (why two bases, honestly). Per-segment granularity exists ONLY in the
company's settlement-records view (`data['years'][*]['segment_split']`), which values energy
on a settlement (accrual-on-settled-volume) basis and totals ~£14.0m revenue. The statutory
management accounts (`data['management_accounts']`, ledger-derived) value on a billed basis
and total ~£18.9m revenue. The CSS segmental table is therefore presented on the SETTLEMENT
basis (the only per-segment source), and a reconciliation table bridges it to the statutory
accounts with each reconciling item named. R14: every figure carries its clock/basis.

NO HAND-TYPED FIGURES: every number is derived from `data` (the extracted run output).
Where a component genuinely does not exist yet (per-segment indirect allocation, D&A), it is
reported as an HONEST NAMED GAP, never a fabricated allocation.
"""

from __future__ import annotations

import math
from collections import defaultdict

KWH_PER_THERM = 29.3071  # 1 therm = 29.3071 kWh (gas volume conversion)

# The four CSS segments (+ aggregate rendered separately).
CSS_SEGMENTS = [
    "Electricity — Domestic",
    "Electricity — Non-Domestic",
    "Gas — Domestic",
    "Gas — Non-Domestic",
]

# Company CRM segment tags → CSS domestic/non-domestic. resi = domestic;
# SME and I&C (industrial & commercial) = non-domestic. Company-observable.
_DOMESTIC_TAGS = {"resi"}


def _css_seg(commodity: str, segment: str) -> str:
    comm = "Electricity" if commodity == "electricity" else "Gas"
    dom = "Domestic" if segment in _DOMESTIC_TAGS else "Non-Domestic"
    return f"{comm} — {dom}"


def _classify_split_key(split_key: str) -> str | None:
    """Map a segment_split key ('resi electricity', 'I&C gas', …) to a CSS segment."""
    parts = split_key.split()
    if len(parts) < 2:
        return None
    segment, commodity = parts[0], parts[-1]
    if commodity not in ("electricity", "gas"):
        return None
    return _css_seg(commodity, segment)


def _cid_segment_map(data: dict) -> dict[str, str]:
    """cid → CSS segment, from the company's own per-customer commodity/segment tags."""
    out: dict[str, str] = {}
    for cid, v in (data.get("per_customer_lifetime") or {}).items():
        commodity = v.get("commodity", "electricity")
        segment = v.get("segment", "resi")
        out[cid] = _css_seg(commodity, segment)
    return out


def build_css(data: dict) -> dict | None:
    """Assemble the CSS data structure from extracted run output.

    Returns None when the per-segment settlement source is absent (silent section).
    """
    years = data.get("years") or {}
    if not years:
        return None
    has_segment = any((yd.get("segment_split") for yd in years.values()))
    if not has_segment:
        return None

    # --- Per-segment P&L, settlement basis (aggregate segment_split across years) ---
    seg = {s: defaultdict(float) for s in CSS_SEGMENTS}
    for yd in years.values():
        for sk, sv in (yd.get("segment_split") or {}).items():
            css = _classify_split_key(sk)
            if css is None:
                continue
            for m in ("revenue_gbp", "gross_gbp", "capital_gbp", "net_gbp"):
                seg[css][m] += sv.get(m, 0.0)

    # --- Commodity-level transportation vs environmental split ratios (settlement basis) ---
    elec_transport = sum(yd.get("network_cost_gbp", 0.0) for yd in years.values())
    elec_env = sum(
        yd.get("ro_levy_gbp", 0.0) + yd.get("cfd_levy_gbp", 0.0)
        + yd.get("cm_levy_gbp", 0.0) + yd.get("fit_levy_gbp", 0.0)
        + yd.get("mutualization_levy_gbp", 0.0) + yd.get("ccl_gbp", 0.0)
        for yd in years.values()
    )
    gas_transport = sum(yd.get("gas_network_cost_gbp", 0.0) for yd in years.values())
    gas_env = sum(yd.get("gas_policy_cost_gbp", 0.0) for yd in years.values())

    def _ratio(t: float, e: float) -> tuple[float, float]:
        tot = t + e
        if tot == 0:
            return (0.5, 0.5)
        return (t / tot, e / tot)

    elec_tr, elec_er = _ratio(elec_transport, elec_env)
    gas_tr, gas_er = _ratio(gas_transport, gas_env)

    # --- Volume (MWh) and meter points, from per-customer monthly consumption ---
    cidmap = _cid_segment_map(data)
    volume_mwh = {s: 0.0 for s in CSS_SEGMENTS}
    monthly_active: dict[str, dict[str, set]] = {s: defaultdict(set) for s in CSS_SEGMENTS}
    for yd in years.values():
        pcm = yd.get("per_customer_monthly") or {}
        pc = yd.get("per_customer") or {}
        for cid, months in pcm.items():
            css = cidmap.get(cid)
            if css is None:
                commodity = (pc.get(cid) or {}).get("commodity", "electricity")
                segment = "I&C" if cid.startswith("C_IC") else "resi"
                css = _css_seg(commodity, segment)
            if css not in volume_mwh:
                continue
            for mo, mv in months.items():
                kwh = mv.get("consumption_kwh", 0.0) or 0.0
                volume_mwh[css] += kwh / 1000.0
                if kwh > 0:
                    monthly_active[css][mo].add(cid)

    meter_points = {}
    for s in CSS_SEGMENTS:
        counts = [len(v) for v in monthly_active[s].values()]
        meter_points[s] = (sum(counts) / len(counts)) if counts else 0.0

    # --- Build per-segment line items ---
    segments = {}
    for s in CSS_SEGMENTS:
        d = seg[s]
        revenue = d["revenue_gbp"]
        gross = d["gross_gbp"]
        capital = d["capital_gbp"]
        net = d["net_gbp"]
        fuel = revenue - gross                     # direct fuel cost
        non_commodity = gross - capital - net      # sim-attributed transport + environmental
        is_elec = s.startswith("Electricity")
        tr, er = (elec_tr, elec_er) if is_elec else (gas_tr, gas_er)
        transportation = non_commodity * tr
        environmental = non_commodity * er
        vol = volume_mwh[s]
        wacoe = (fuel / vol) if vol > 0 else None          # £/MWh
        wacog_p_per_th = None
        if not is_elec and vol > 0:
            fuel_p = fuel * 100.0                            # £ → pence
            therms = vol * 1000.0 / KWH_PER_THERM
            wacog_p_per_th = fuel_p / therms if therms else None
        segments[s] = {
            "revenue_gbp": revenue,
            "fuel_gbp": fuel,
            "gross_margin_gbp": gross,
            "transportation_gbp": transportation,
            "environmental_gbp": environmental,
            "non_commodity_gbp": non_commodity,
            "other_direct_gbp": capital,           # capital/collateral charges
            "contribution_gbp": net,               # segment EBITDA contribution before central indirect
            "volume_mwh": vol,
            "wacoe_gbp_per_mwh": wacoe,
            "wacog_p_per_th": wacog_p_per_th,
            "meter_points": meter_points[s],
        }

    # Aggregate column (settlement basis) — segments sum to this
    agg = {k: sum(segments[s][k] for s in CSS_SEGMENTS)
           for k in ("revenue_gbp", "fuel_gbp", "gross_margin_gbp", "transportation_gbp",
                     "environmental_gbp", "non_commodity_gbp", "other_direct_gbp",
                     "contribution_gbp", "volume_mwh")}
    agg["meter_points"] = sum(meter_points[s] for s in CSS_SEGMENTS)

    # --- Statutory group P&L (management accounts aggregate, billed basis) ---
    ma = data.get("management_accounts") or {}
    stat = defaultdict(float)
    for yv in ma.values():
        for k, x in (yv.get("income_statement") or {}).items():
            stat[k] += x
    statutory = {
        "revenue_gbp": stat.get("revenue_gbp", 0.0),
        "fuel_gbp": stat.get("wholesale_cost_gbp", 0.0),
        "non_commodity_gbp": stat.get("non_commodity_cost_gbp", 0.0),
        "gross_margin_gbp": stat.get("gross_margin_gbp", 0.0),
        "bad_debt_gbp": stat.get("bad_debt_gbp", 0.0),
        "cost_to_serve_gbp": stat.get("cost_to_serve_gbp", 0.0),
        "acquisition_gbp": stat.get("acquisition_spend_gbp", 0.0),
        "central_overhead_gbp": stat.get("fixed_cost_gbp", 0.0),
        "capital_charge_gbp": stat.get("capital_cost_gbp", 0.0),
        "total_indirect_gbp": stat.get("total_opex_gbp", 0.0),
        "ebitda_gbp": stat.get("net_margin_gbp", 0.0),   # == EBIT (no D&A layer yet)
        "tax_gbp": stat.get("corporation_tax_gbp", 0.0),
        "profit_for_year_gbp": stat.get("profit_for_year_gbp", 0.0),
    }

    # --- Reconciliation: CSS (settlement) → statutory (management accounts) ---
    ledger_pnl = data.get("ledger_pnl") or {}
    reconciliation = {
        "css_settlement_revenue_gbp": agg["revenue_gbp"],
        "statutory_billed_revenue_gbp": statutory["revenue_gbp"],
        "revenue_basis_difference_gbp": statutory["revenue_gbp"] - agg["revenue_gbp"],
        "css_settlement_fuel_gbp": agg["fuel_gbp"],
        "statutory_fuel_gbp": statutory["fuel_gbp"],
        "css_settlement_non_commodity_gbp": agg["non_commodity_gbp"],
        "statutory_non_commodity_gbp": statutory["non_commodity_gbp"],
        "css_settlement_contribution_gbp": agg["contribution_gbp"],
        "billed_total_gbp": ledger_pnl.get("total_billed_gbp"),
        "cash_collected_gbp": ledger_pnl.get("cash_collected_gbp"),
    }

    return {
        "segments": segments,
        "aggregate": agg,
        "statutory": statutory,
        "reconciliation": reconciliation,
        "cost_split_ratios": {
            "electricity": {"transportation": elec_tr, "environmental": elec_er},
            "gas": {"transportation": gas_tr, "environmental": gas_er},
        },
    }


# ------------------------------------------------------------- reconciliation control
#
# R15 (controls-that-cannot-fail): the CSS reconciliation invariants are extracted here
# as a SINGLE callable control that MUST be able to FAIL. It is wired into `render_css`
# (a violation renders a LOUD banner instead of a clean statement — closing the FAIL-
# SILENT hole where a broken CSS would otherwise be swallowed to "" by the annual-report
# wrapper) and is mutation-tested in tests/saas/test_e4_css_reconciliation_control.py:
# each named defect is injected and this function is asserted to report it.
#
# Independence note (honest): three of these checks are INTERNAL-consistency checks that
# guard the persisted/rendered artifact (a downstream transform, rounding, or serialisation
# bug cannot silently break the tie a reader sees) — waterfall, aggregate==sum-of-segments,
# and the settlement→billed bridge, whose reconciling item is a derived plug at BUILD time.
# One check is genuinely INDEPENDENT (a different data path): the CSS aggregate revenue,
# summed from the classified per-segment buckets, must tie to the top-line settlement
# revenue `sum(years[*].revenue_gbp)`. That fires when a `segment_split` key fails to
# classify and is silently dropped — the real FAIL-SILENT risk in `_classify_split_key`.

RECON_TOL_GBP = 1.0

_MONEY_KEYS = (
    "revenue_gbp", "fuel_gbp", "transportation_gbp", "environmental_gbp",
    "other_direct_gbp", "contribution_gbp", "non_commodity_gbp",
)


def _finite_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def verify_css_reconciliation(
    css: dict | None, data: dict | None = None, *, tol: float = RECON_TOL_GBP
) -> list[str]:
    """Return reconciliation violations (empty list == clean). The R15 control.

    FAIL-CLOSED by design: a missing/malformed structure or a non-finite figure is a
    violation, never a silent pass (guards the FAIL-OPEN and FAIL-SILENT killer patterns).
    """
    if not css or not isinstance(css, dict) or "segments" not in css or "aggregate" not in css:
        return ["css structure missing segments/aggregate (control fails closed)"]

    segs = css["segments"]
    agg = css["aggregate"]
    v: list[str] = []

    # FAIL-OPEN guard — every stored money figure must be a finite number.
    for s in CSS_SEGMENTS:
        if s not in segs:
            v.append(f"missing segment '{s}'")
            continue
        for k in _MONEY_KEYS:
            if not _finite_num(segs[s].get(k)):
                v.append(f"fail-open guard: {s}.{k} is non-finite ({segs[s].get(k)!r})")

    # Control A — per-segment waterfall reconciles to revenue (< tol).
    for s in CSS_SEGMENTS:
        x = segs.get(s) or {}
        if all(_finite_num(x.get(k)) for k in _MONEY_KEYS):
            wf = (x["fuel_gbp"] + x["transportation_gbp"] + x["environmental_gbp"]
                  + x["other_direct_gbp"] + x["contribution_gbp"])
            if abs(wf - x["revenue_gbp"]) > tol:
                v.append(f"waterfall '{s}': components sum {wf:,.2f} != revenue {x['revenue_gbp']:,.2f}")
            if abs((x["transportation_gbp"] + x["environmental_gbp"]) - x["non_commodity_gbp"]) > tol:
                v.append(f"transport+env '{s}' != non_commodity")

    # Control B — aggregate == sum of segments (persisted-artifact integrity).
    for k in ("revenue_gbp", "fuel_gbp", "gross_margin_gbp", "contribution_gbp",
              "transportation_gbp", "environmental_gbp", "volume_mwh"):
        seg_sum = sum((segs.get(s) or {}).get(k, 0.0) for s in CSS_SEGMENTS)
        if not _finite_num(agg.get(k)) or abs(agg[k] - seg_sum) > tol:
            v.append(f"aggregate '{k}' {agg.get(k)!r} != sum-of-segments {seg_sum:,.2f}")

    # Control B' — INDEPENDENT: aggregate revenue ties to top-line settlement revenue.
    # Different data path (year top-line vs summed segment buckets); fires on a
    # segment_split key that failed to classify and was silently dropped.
    if data is not None:
        yrs = data.get("years") or {}
        topline = sum(y.get("revenue_gbp", 0.0) for y in yrs.values())
        if topline and abs(agg.get("revenue_gbp", 0.0) - topline) > max(tol, abs(topline) * 1e-6):
            v.append(
                f"independent tie: aggregate revenue {agg.get('revenue_gbp', 0.0):,.2f} != "
                f"top-line settlement {topline:,.2f} (an unclassified segment_split key was dropped)"
            )

    # Control C — settlement→billed bridge (presentation integrity of the reconciling triple).
    rec = css.get("reconciliation") or {}
    a = rec.get("css_settlement_revenue_gbp")
    diff = rec.get("revenue_basis_difference_gbp")
    b = rec.get("statutory_billed_revenue_gbp")
    if all(_finite_num(x) for x in (a, diff, b)):
        if abs((a + diff) - b) > tol:
            v.append(f"bridge: settlement {a:,.2f} + basis diff {diff:,.2f} != statutory billed {b:,.2f}")
        if abs(a - agg.get("revenue_gbp", 0.0)) > tol:
            v.append("bridge: css_settlement_revenue != aggregate revenue")
    else:
        v.append("bridge: fail-open guard — non-finite reconciliation figure")

    return v


# --------------------------------------------------------------------------- render

def _g(v: float | None) -> str:
    if v is None:
        return "n/a"
    return f"£{v:,.0f}"


def _row(label: str, key: str, css: dict, *, paren: bool = False) -> str:
    segs = css["segments"]
    agg = css["aggregate"]
    cells = []
    for s in CSS_SEGMENTS + ["__agg__"]:
        v = agg[key] if s == "__agg__" else segs[s][key]
        cell = f"({_g(v)})" if (paren and v) else _g(v)
        cells.append(cell)
    return f"| {label} | " + " | ".join(cells) + " |"


def render_css(data: dict) -> str:
    css = build_css(data)
    if css is None:
        return ""
    segs = css["segments"]
    stat = css["statutory"]
    rec = css["reconciliation"]

    # R15: run the reconciliation control and render a LOUD banner on any violation.
    # This closes the FAIL-SILENT hole — a broken CSS is visible in the report, not
    # swallowed to "" by the annual-report wrapper's broad except.
    _violations = verify_css_reconciliation(css, data)
    _recon_banner = ""
    if _violations:
        _recon_banner = (
            "\n> **⚠ CSS RECONCILIATION CONTROL FIRED** — the segmental statement below "
            "did NOT reconcile and is shown for diagnosis only, NOT as an audited figure "
            "(R15: an unavailable/failed check is a failed check, surfaced loudly):\n"
            + "\n".join(f">  - {x}" for x in _violations)
            + "\n"
        )

    hdr = "| £, settlement basis | " + " | ".join(
        [s.replace("Electricity", "Elec").replace("Non-Domestic", "Non-Dom")
         for s in CSS_SEGMENTS] + ["**Aggregate**"]) + " |"
    sep = "|" + "---|" * (len(CSS_SEGMENTS) + 2)

    lines = [
        "## Consolidated Segmental Statement (CSS)",
        "",
        "*Ofgem-format segmental statement (SLC 19A shape) — the reporting backbone. "
        "Company's own publication; every figure derived from settlement records and the "
        "ledger, none hand-typed.*",
    ]
    if _recon_banner:
        lines.append(_recon_banner)
    lines += [
        "",
        "**Basis (R14):** the segmental P&L below is on a **settlement basis** (accrual on "
        "settled volume) — the only basis at which the company attributes P&L per segment. "
        "It reconciles to the statutory (billed-basis) management accounts in the "
        "reconciliation table further down.",
        "",
        "### P&L by segment",
        "",
        hdr,
        sep,
        _row("Revenue from sale of energy", "revenue_gbp", css),
        _row("Direct fuel costs", "fuel_gbp", css, paren=True),
        _row("**Gross margin**", "gross_margin_gbp", css),
        _row("Transportation (TNUoS/DUoS/BSUoS/gas transport)", "transportation_gbp", css, paren=True),
        _row("Environmental & social obligation costs", "environmental_gbp", css, paren=True),
        _row("Other direct costs (capital/collateral charges)", "other_direct_gbp", css, paren=True),
        _row("**Segment contribution** (EBITDA, before central indirect)", "contribution_gbp", css),
        "",
        "> Transportation and environmental are shown split by the commodity-level "
        "transport:environmental ratio applied to each segment's sim-attributed non-commodity "
        "total (elec {:.0%}/{:.0%}, gas {:.0%}/{:.0%}); the per-segment non-commodity TOTAL is "
        "exact (settlement-attributed). CCL is non-domestic-only in reality — the ratio split "
        "is a disclosed approximation for the sub-line only.".format(
            css["cost_split_ratios"]["electricity"]["transportation"],
            css["cost_split_ratios"]["electricity"]["environmental"],
            css["cost_split_ratios"]["gas"]["transportation"],
            css["cost_split_ratios"]["gas"]["environmental"]),
        "",
        "### Operational lines by segment",
        "",
        "| Metric | " + " | ".join(
            [s.replace("Electricity", "Elec").replace("Non-Domestic", "Non-Dom")
             for s in CSS_SEGMENTS]) + " |",
        "|" + "---|" * (len(CSS_SEGMENTS) + 1),
        "| Volume net of losses (MWh) | " + " | ".join(
            f"{segs[s]['volume_mwh']:,.1f}" for s in CSS_SEGMENTS) + " |",
        "| WACOE/WACOG (£/MWh) | " + " | ".join(
            (f"{segs[s]['wacoe_gbp_per_mwh']:,.2f}" if segs[s]['wacoe_gbp_per_mwh'] is not None else "n/a")
            for s in CSS_SEGMENTS) + " |",
        "| WACOG (p/therm, gas) | " + " | ".join(
            (f"{segs[s]['wacog_p_per_th']:,.2f}" if segs[s]['wacog_p_per_th'] is not None else "—")
            for s in CSS_SEGMENTS) + " |",
        "| Meter points (12-mo avg of monthly closing) | " + " | ".join(
            f"{segs[s]['meter_points']:,.2f}" for s in CSS_SEGMENTS) + " |",
        "",
        "> WACOE/WACOG = direct fuel cost ÷ volume. Meter points are a 12-month average of "
        "monthly closing counts; the sim runs a small book of *representative* billing accounts, "
        "so these are single-digit by design (representative-account scale, not a real "
        "50k+ portfolio).",
        "",
    ]

    # Group P&L bridge to statutory / EBIT
    da_gap = ("£0 — **honest gap**: no fixed-asset / amortisation layer exists yet (no "
              "capitalised assets to depreciate). Registered, not fabricated.")
    lines += [
        "### Group P&L — indirect costs, EBITDA, D&A, EBIT (statutory basis)",
        "",
        "*Indirect costs and D&A are group-level: the company does not yet attribute indirect "
        "cost to segments (no activity-driver model), so per-segment indirect allocation is an "
        "**honest named gap** — not a fabricated split. Figures below are on the statutory "
        "(billed/ledger) basis.*",
        "",
        "| Line | £ |",
        "|---|---:|",
        f"| Gross margin (statutory) | {_g(stat['gross_margin_gbp'])} |",
        f"| Indirect — bad debt | ({_g(stat['bad_debt_gbp'])}) |",
        f"| Indirect — cost-to-serve (customer service; metering/PSR/R&D not yet split) | ({_g(stat['cost_to_serve_gbp'])}) |",
        f"| Indirect — sales & marketing / acquisition | ({_g(stat['acquisition_gbp'])}) |",
        f"| Indirect — central overhead | ({_g(stat['central_overhead_gbp'])}) |",
        f"| Indirect — capital/collateral charge | ({_g(stat['capital_charge_gbp'])}) |",
        f"| **EBITDA** | {_g(stat['ebitda_gbp'])} |",
        f"| Depreciation & amortisation | {da_gap} |",
        f"| **EBIT** | {_g(stat['ebitda_gbp'])} |",
        f"| Corporation tax | ({_g(stat['tax_gbp'])}) |",
        f"| **Profit for the year** | {_g(stat['profit_for_year_gbp'])} |",
        "",
        "> Indirect cost-to-serve is a single line; CSS guidance also names metering, PSR "
        "cost-to-serve and R&D as sub-components — these are **named gaps** (no sub-decomposition "
        "model yet), reported here rather than fabricated.",
        "",
    ]

    # Reconciliation table
    rev_diff = rec["revenue_basis_difference_gbp"]
    lines += [
        "### Reconciliation — CSS (settlement) → statutory management accounts",
        "",
        "| Reconciling item | £ |",
        "|---|---:|",
        f"| CSS revenue (settlement basis) | {_g(rec['css_settlement_revenue_gbp'])} |",
        f"| + Settled-to-billed basis difference (standing charges, estimated vs settled "
        f"volume, restatements) | {_g(rev_diff)} |",
        f"| = Statutory revenue (billed basis) | {_g(rec['statutory_billed_revenue_gbp'])} |",
        f"| Memo: total billed (accrued) | {_g(rec['billed_total_gbp'])} |",
        f"| Memo: cash collected (banked) | {_g(rec['cash_collected_gbp'])} |",
        "",
        "*R14 clocks: **settled** = CSS segmental P&L; **billed** = statutory revenue / total "
        "billed; **banked** = cash collected. The revenue basis difference is the single largest "
        "reconciling item and is expected — the CSS values energy on settled volume, the "
        "statutory accounts on what was billed.*",
        "",
    ]

    # Consolidated R10 named-simplifications block — every gap declared in ONE visible
    # place with rationale, so the statement is honest about what is NOT modelled rather
    # than fabricating a D&A layer or an activity-driver allocation to hide it.
    lines += [
        "### Named simplifications (R10) — what this statement does NOT model",
        "",
        "*These are declared, not fabricated. Building a speculative fixed-asset or "
        "activity-driver layer to fill them would be a fidelity regression, not an "
        "improvement — the honest L3 move is to name them.*",
        "",
        "| Item | Treatment | Rationale |",
        "|---|---|---|",
        "| Depreciation & amortisation | **Not modelled — reported £0** | No fixed-asset / "
        "capitalisation / amortisation layer exists, so there is nothing to depreciate. EBITDA "
        "therefore equals EBIT. A fabricated D&A charge would be a made-up number. |",
        "| Per-segment indirect cost allocation | **Group-level only (not attributed to "
        "segments)** | No activity-driver / cost-to-serve-by-segment model exists. Indirect "
        "costs (bad debt, cost-to-serve, acquisition, overhead, capital charge) are shown at "
        "group level; splitting them across segments without a driver model would be an "
        "arbitrary allocation presented as fact. |",
        "| Transportation vs environmental sub-split | **Commodity-ratio approximation "
        "(disclosed)** | The per-segment non-commodity TOTAL is exact (settlement-attributed); "
        "only its transport/environmental SUB-split uses the commodity-level "
        "transport:environmental ratio. CCL is non-domestic-only in reality, so the ratio split "
        "of that sub-line is approximate. |",
        "| Cost-to-serve sub-components (metering, PSR, R&D) | **Single line — not "
        "decomposed** | CSS guidance names these sub-components; no sub-decomposition model "
        "exists yet, so they are reported as one cost-to-serve line rather than fabricated. |",
        "",
    ]

    # Hedging policy note
    heff = data.get("hedge_effectiveness_total") or {}
    add = heff.get("hedging_value_add_gbp")
    hedge_add = (f" Over the window, hedging {'added' if (add or 0) >= 0 else 'cost'} "
                 f"£{abs(add):,.0f} versus a fully unhedged book.") if add is not None else ""
    lines += [
        "### Hedging policy note",
        "",
        "The company hedges wholesale volume forward to lock supply margin at the point of "
        "tariff sign-up. **Default (SVT-style) tariffs** are hedged on a rolling forward basis "
        "tracking the cap-implied demand curve; **fixed-term tariffs** are hedged to their "
        "contracted term at sign-up so the margin is fixed for the customer's term. **Volume "
        "risk** (weather / consumption deviation vs the hedged shape) is borne by the company, "
        "not the customer, on both tariff types — the customer's unit rate is fixed within term "
        "and the company absorbs the settlement volume variance." + hedge_add,
        "",
    ]

    return "\n".join(lines)


# --------------------------------------------------------------------- board KPIs

def build_board_kpis(data: dict) -> dict | None:
    years = data.get("years") or {}
    if not years:
        return None
    css = build_css(data)

    n_years = len(years)
    # Average book size (representative billing accounts) from CSS meter points
    avg_book = css["aggregate"]["meter_points"] if css else 0.0

    # Churn: distinct churned accounts over window, annualised vs average book
    churned = len(data.get("churned_billing_accounts") or [])
    churn_pct = (churned / n_years / avg_book) if (avg_book and n_years) else None

    # Complaints per 1,000 customers (annualised)
    comp = data.get("complaint_annual_summaries") or {}
    total_complaints = sum(v.get("total", 0) for v in comp.values())
    complaints_per_1000 = ((total_complaints / n_years) / avg_book * 1000.0) if avg_book else None

    # ARPU by segment (settlement revenue ÷ meter points ÷ years)
    arpu = {}
    if css:
        for s in CSS_SEGMENTS:
            mp = css["segments"][s]["meter_points"]
            rev = css["segments"][s]["revenue_gbp"]
            arpu[s] = (rev / mp / n_years) if mp else None

    # CSAT / NPS from satisfaction machinery (company-measured, not SIM-true)
    nps = data.get("nps_annual_summaries") or {}
    nps_responses = sum(v.get("responses", 0) for v in nps.values())
    nps_vals = [v.get("nps") for v in nps.values() if v.get("nps") is not None]
    nps_avg = (sum(nps_vals) / len(nps_vals)) if nps_vals else None
    survey = data.get("feedback_survey_log") or []
    csat_scores = [s.get("csat_score_0_10") for s in survey if s.get("csat_score_0_10") is not None]
    csat_avg = (sum(csat_scores) / len(csat_scores)) if csat_scores else None

    # Direct Debit share
    dd = (data.get("dd_collection_book") or {}).get("summary") or {}
    dd_total = dd.get("total", 0)
    dd_active = dd.get("active", 0)

    # Estimated-read rate
    mrl = data.get("meter_read_log") or []
    est = sum(1 for r in mrl if r.get("status") == "estimated")
    read_total = len(mrl)
    est_rate = (est / read_total) if read_total else None

    # GSOP / SLC14 — contact-centre SLA breaches as the service-standard proxy
    ccl = data.get("contact_centre_log") or []
    sla_breaches = sum(1 for r in ccl if r.get("breached_sla"))

    return {
        "n_years": n_years,
        "avg_book": avg_book,
        "churned": churned,
        "churn_pct": churn_pct,
        "total_complaints": total_complaints,
        "complaints_per_1000": complaints_per_1000,
        "arpu": arpu,
        "nps_responses": nps_responses,
        "nps_avg": nps_avg,
        "csat_avg": csat_avg,
        "csat_responses": len(csat_scores),
        "dd_total": dd_total,
        "dd_active": dd_active,
        "est_rate": est_rate,
        "read_total": read_total,
        "sla_breaches": sla_breaches,
        "sla_total": len(ccl),
    }


def render_board_kpis(data: dict) -> str:
    k = build_board_kpis(data)
    if k is None:
        return ""

    def pct(v):
        return f"{v * 100:.1f}%" if v is not None else "n/a"

    lines = [
        "## Board KPI Block",
        "",
        "*Board-grade KPI set paired with the CSS financials. Customer-experience metrics are "
        "company-**measured** (survey machinery), not SIM-true — the company side of the wall.*",
        "",
        "| KPI | Value | Basis / note |",
        "|---|---:|---|",
        f"| Churn % (of avg customers, annualised) | {pct(k['churn_pct'])} | {k['churned']} churned accounts over {k['n_years']}y; Centrica-style definition |",
    ]
    if k["complaints_per_1000"] is not None:
        lines.append(f"| Complaints per 1,000 customers (annualised) | {k['complaints_per_1000']:.1f} | {k['total_complaints']} complaints over window (Ofgem/CitA league-table metric) |")
    else:
        lines.append("| Complaints per 1,000 | n/a | no book size |")
    if k["csat_avg"] is not None:
        lines.append(f"| CSAT (avg score 0–10) | {k['csat_avg']:.1f} | {k['csat_responses']} survey responses (measured) |")
    else:
        lines.append(f"| CSAT (avg 0–10) | n/a | {k['csat_responses']} responses — too few to report |")
    if k["nps_avg"] is not None:
        lines.append(f"| NPS (avg annual) | {k['nps_avg']:.0f} | {k['nps_responses']} responses — **low volume, indicative only** |")
    else:
        lines.append(f"| NPS | n/a | {k['nps_responses']} responses |")
    lines += [
        f"| Direct Debit share | {pct(k['dd_active'] / k['dd_total'] if k['dd_total'] else None)} | {k['dd_active']}/{k['dd_total']} mandates active |",
        f"| Estimated-read rate | {pct(k['est_rate'])} | {k['read_total']} meter reads; lower is better |",
        f"| Contact-centre SLA breaches (SLC14-style) | {k['sla_breaches']} | of {k['sla_total']} contacts; GSOP statutory-payment detail in the GSOP Obligations section |",
        "",
        "### ARPU by segment (settlement revenue ÷ meter points, annualised)",
        "",
        "| Segment | ARPU £/yr |",
        "|---|---:|",
    ]
    arpu = k["arpu"]
    for s in CSS_SEGMENTS:
        v = arpu.get(s)
        lines.append(f"| {s} | {('£%s' % format(v, ',.0f')) if v is not None else 'n/a'} |")
    lines += [
        "",
        "> **Awaiting market backdrop (named gap):** relative metrics — churn spread vs "
        "rest-of-market and price-vs-cap positioning (the best-in-class AGL/Octopus pattern) — "
        "are blocked on the simulated competitor field, an already-identified Epoch-2 missing "
        "piece. Named here rather than omitted silently.",
        "",
    ]
    return "\n".join(lines)
