#!/usr/bin/env python3
"""What a value-pricing supplier would DO with this book, beside what today's supplier does.

REUSE: tools/couple_value_based_pricing.py
CLASS: PATTERN-REUSE
INDEX: searched "couple", "baseline", "arm", "control", "counterfactual", "clv". The COUPLED-
       RUNNER pattern is taken wholesale from `tools/couple_pb3_book_growth.py` and its
       siblings: harness code in `tools/`, outside the wall by design, the only layer allowed to
       hold the company's belief and the world's outcome side by side
       (COUPLED_TRIAD_DESIGN 1.3). The decision itself is
       `company/pricing/value_based_renewal.decide_margin` and nothing is recomputed here.
       `company/analytics/counterfactual_retention.py` was read and is NOT the same thing: it
       scores retention OFFERS against a fixed effectiveness assumption; this compares two
       PRICING RULES on the same book.

WHY IT EXISTS
-------------
Director, 2026-08-25: *"there has to be a baseline to beat. Average behaviour is the control —
the same book run by a supplier applying flat rules with no per-customer view. Without that
comparison, 'it performed well' means nothing."*

The control is free, because today's company IS it: a flat £2.00/MWh for every account. So this
runs both arms over the real book and reports what they would decide differently.

WHAT IT MEASURES, AND WHAT IT CANNOT
------------------------------------
DECISIONS, not earnings. It reports what each arm would OFFER and what each arm BELIEVES that
offer is worth. It does not report what either would earn, and it must not be read as though it
did: the value arm maximises the company's own expected value, so scoring the arms on expected
value lets the value arm win by construction — R15's tautology with money in it.

The honest earnings comparison is REALISED: the same book, the same world, run once per arm,
scored on what actually happened. That needs two full runs and is the next step.

AND IT DOES NOT MEASURE THE COMPANY'S INFERENCE, which is the thing the thesis is actually
about. The belief-versus-truth block below holds the company's churn estimate beside the world's
response, and both descend from ONE published series -- the DESNZ 2015-2025 switching counts
(`shared_calibration_holds` reads that off each side's own source rather than asserting it here).
A gap between two fits of one series is those fits disagreeing about noise; it is not a supplier
knowing something. Nor is most of the book scored where the world is observing: past
`_CALIBRATED_SAVINGS_CEILING_GBP` of annual shortfall the world continues its last informed
slope, and the median account here sits well beyond that. So the pair REFUSES to be published as
evidence of inference while that holds -- the summary carries the refusal, the verdict paragraph
carries it, and the ledger write declines. What would discharge it is recorded beside it.

WHAT IT FOUND ON ITS FIRST RUN, which is why the arm is not wired to the renewal desk. See
`value_based_renewal.max_supported_rate_increase_pct` for the mechanism.

Run:  python3 -m tools.couple_value_based_pricing
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from background.gap_metric import _normalise, write_gap_entry
from company.crm.enriched_churn_estimate import enriched_churn_estimate
from company.pricing.regulated_average_margin import (
    AverageMarginUnavailable,
    average_player_margin,
)
from company.pricing.value_based_renewal import (
    FLAT_RULES,
    VALUE_BASED,
    MarginDecisionUnavailable,
    decide_margin,
    max_supported_rate_increase_pct,
)
from saas.non_commodity import standing_charge_rate
from saas.payment_behaviour import (
    CREDIT_RISK_BY_CUSTOMER,
    DEFAULT_CREDIT_RISK,
    PAYMENT_TIMING_DAYS_BY_CREDIT_RISK,
)
from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH
from simulation.churn_ceiling import WORLD_MAX_CHURN_PROBABILITY
from simulation.customer_events import _price_differential_vs_market
from simulation.market_switching_propensity import (
    _CALIBRATED_SAVINGS_CEILING_GBP,
    CALIBRATION_ANNUAL_BILL_GBP,
    churn_position_multiplier,
)
from tools import maturity_map_store as map_store

PROJECT = Path(__file__).resolve().parent.parent
BOOK_PATH = PROJECT / "site" / "data" / "customers.json"
OUT_PATH = PROJECT / "docs" / "observability" / "value_based_pricing_arms.json"

#: Renewal year the comparison is struck at. The arms are compared at ONE moment so the
#: difference between them is the RULE and never the calendar.
AS_OF_YEAR = 2025

#: Months per year, for turning a bill count into the years a meter has been on supply. The book
#: publishes `bill_count` and `total_kwh` and not an EAC, so the annualisation is stated here
#: rather than hidden in an expression.
BILLS_PER_YEAR = 12.0

#: THE ONE SERIES BOTH SIDES OF THIS PAIR WERE FITTED FROM. The coupled measurement below is
#: read as "the company's inference against the world's truth", and that reading requires the two
#: to be INDEPENDENT. They are not. The world's response and the company's estimator descend from
#: the same published market-level switching counts, so the gap between them is, at least in part,
#: two calibrations of one series disagreeing about noise -- an arithmetic residue wearing the
#: costume of a company knowing something.
SHARED_CALIBRATION_SERIES = (
    "DESNZ electricity switching series 2015-2025, cross-referenced with the Ofgem Consumer "
    "Engagement Survey"
)

#: Each side's OWN SOURCE saying so, so the claim is READ OFF THE TREE rather than asserted here
#: by the tool that would benefit from asserting it (R15 tautology: a provenance claim written
#: down beside the measurement is checked by nothing and goes stale silently). If either side is
#: ever genuinely re-calibrated from an independent source, its witness leaves its source file and
#: the refusal below lifts by itself -- which is what makes it a control and not a comment.
_PROVENANCE_WITNESSES = (
    ("world", "simulation/market_switching_propensity.py",
     "Calibrated from DESNZ electricity switching series 2015-2025",
     "`churn_position_multiplier` is the reciprocal of the win leg below saturation, and that "
     "leg IS `_savings_to_rate` -- the piecewise curve fitted to the series"),
    ("company", "company/crm/market_conditions.py",
     "from the same public DESNZ/Ofgem series",
     "`market_conditions_multiplier` scales every `enriched_churn_estimate`, and its own "
     "docstring says it mirrors `simulation.market_switching_propensity`, reimplemented rather "
     "than re-derived"),
)


def shared_calibration_holds() -> dict:
    """Do the company's estimator and the world's response still descend from ONE series?

    FAIL-CLOSED, DELIBERATELY. A witness file that cannot be read leaves the pair recorded as
    CO-CALIBRATED and therefore unpublishable, because "we could not check" is not "they are
    independent" -- an unavailable check is a failed check (R15 fail-silent).

    Returns the record itself rather than a bare bool: a reader of
    `docs/observability/value_based_pricing_arms.json` must be able to see the shared provenance,
    both witnesses, and what would discharge it, without opening a source file.
    """
    sides, unreadable = {}, []
    for side, relpath, witness, reaches in _PROVENANCE_WITNESSES:
        entry = {"source": relpath, "witness": witness, "why_it_reaches_this_pair": reaches}
        try:
            entry["cites_the_series"] = witness in (PROJECT / relpath).read_text(encoding="utf-8")
        except OSError as exc:
            entry["cites_the_series"] = None
            entry["why_unknown"] = f"{exc.__class__.__name__}: {str(exc)[:80]}"
            unreadable.append(relpath)
        sides[side] = entry
    co_calibrated = bool(unreadable) or all(s["cites_the_series"] for s in sides.values())
    return {
        "co_calibrated": co_calibrated,
        "series": SHARED_CALIBRATION_SERIES,
        "sides": sides,
        "unreadable": unreadable,
        "why_it_disqualifies_the_gap": (
            "A belief-versus-truth gap is quotable as evidence of the company's INFERENCE only if "
            "the two sides were arrived at independently. Both of these were fitted from the same "
            "market-level switching counts, so a small gap can be shared arithmetic and a large "
            "one can be two fits disagreeing about noise. Neither reading distinguishes a company "
            "that knows something from one that shares a source with the world it is being "
            "scored against."
        ),
        "what_would_discharge_it": (
            "ONE of: (a) the world leg re-calibrated from a series the company cannot read -- a "
            "SUPPLIER-level churn series against that supplier's own position versus the market "
            "(the 2018-19 small-supplier failures and the SoLR events are where to look), which "
            "`churn_position_multiplier` already names as the thing that would settle its own "
            "extrapolation; or (b) the company estimator re-fitted from its OWN observed "
            "departures rather than the published market series, which is what a real supplier "
            "actually has and this one does not yet use. Scoring the pair inside the calibrated "
            "window does NOT discharge it -- that removes the extrapolation flag below and leaves "
            "the shared source untouched. Neither does the realised two-run earnings comparison "
            "named in this module's docstring, but that comparison does not need this to be "
            "discharged: it scores what happened, not two curves against each other."
        ),
    }


def latest_run_output() -> Path:
    """The newest dated run output. Raises rather than returning None: an arms comparison with
    no book is not an empty comparison, it is one that did not run."""
    dated = [p for p in glob.glob(str(PROJECT / "docs" / "reports" / "run_output_*.json"))
             if "2026" in Path(p).name]
    if not dated:
        raise MarginDecisionUnavailable("no dated run output to read a book from")
    return Path(max(dated, key=lambda p: p.rsplit("_", 1)[-1]))


def _legs(book: dict) -> dict:
    out = {}
    for customer in book.get("customers") or []:
        for leg in (customer.get("legs") or {}).values():
            cid = leg.get("cid")
            if cid:
                out[cid] = leg
    return out


def belief_versus_truth(*, offered_rate: float, current_rate: float, tenure_years: float,
                        eac_kwh: float, segment: str, term_start: str) -> dict | None:
    """What the COMPANY believes would happen at its own chosen price, against what the WORLD
    would actually do. The coupled-triad measurement, at the price the decision picks.

    HARNESS ONLY, and this file is where that is allowed: `tools/` sits outside the wall and is
    the one layer permitted to hold the company's belief and the world's outcome side by side
    (COUPLED_TRIAD_DESIGN 1.3). Nothing here is reachable from `company/`.

    WHY IT IS WORTH MEASURING NOW AND WAS NOT THIS MORNING. Until `baec3efb2` the world's churn
    did not read the supplier's own price at all, so both sides were blind and the gap was
    identically zero by construction -- a guaranteed zero contributes nothing to a score. The
    world now responds, and `fbe8b0ab6` let that response reach the world's ceiling. The
    company's model still saturates at 0.95 with a floor of customers who never leave. So the
    gap is real for the first time, and it points the way the thesis says it should: a company
    that predicts badly should lose.
    """
    differential = _price_differential_vs_market(offered_rate, term_start)
    if differential is None:
        return None
    believed = float(enriched_churn_estimate(
        current_rate, offered_rate, tenure_years, float(eac_kwh), segment=segment))
    # The world's response to this position, applied to the same base the company started from,
    # so the comparison isolates the PRICE response and not the rest of the chain.
    base = float(enriched_churn_estimate(current_rate, current_rate, tenure_years,
                                         float(eac_kwh), segment=segment))
    actual = min(base * churn_position_multiplier(differential), WORLD_MAX_CHURN_PROBABILITY)
    # WHERE ON THE WORLD'S CURVE THIS ACCOUNT WAS SCORED, per account, because the curve stops
    # being a measurement partway along it. `churn_position_multiplier` reads the differential as
    # an annual shortfall against a GBP 1,700 bill and the DESNZ series informs it only to
    # GBP 400 of that; past there the world continues the LAST INFORMED SLOPE, which is a named
    # simplification and not an observation. An account scored out there is being compared against
    # an extrapolation, and a reader of one row cannot tell unless the row says so.
    shortfall_gbp = differential * CALIBRATION_ANNUAL_BILL_GBP
    beyond = differential > 0.0 and shortfall_gbp > _CALIBRATED_SAVINGS_CEILING_GBP
    if beyond:
        basis = ("EXTRAPOLATED -- GBP {:.0f}/yr past the GBP {:.0f} the series informs, on the "
                 "last measured slope".format(shortfall_gbp - _CALIBRATED_SAVINGS_CEILING_GBP,
                                              _CALIBRATED_SAVINGS_CEILING_GBP))
    elif -shortfall_gbp > _CALIBRATED_SAVINGS_CEILING_GBP:
        # THE CHEAP SIDE IS NOT THE SAME CASE and calling it "inside the window" would be false.
        # Past the ceiling the WIN leg is flat at `_MAX_RATE`, and the world defends that as a
        # real bound rather than an extrapolation: you cannot win more customers than the market
        # has engaged households to give. Not an observation either -- a saturation.
        basis = ("saturated -- GBP {:.0f}/yr of saving, past the ceiling, where the win leg is "
                 "flat at the engaged-segment maximum the world defends as a real bound".format(
                     -shortfall_gbp))
    else:
        basis = "observed -- inside the calibrated window"
    return {
        "price_differential_vs_svt": round(differential, 4),
        "company_believes_p_leave": round(believed, 4),
        "world_would_p_leave": round(actual, 4),
        "belief_error_pp": round(100.0 * (believed - actual), 1),
        "world_annual_shortfall_gbp": round(shortfall_gbp, 2),
        "world_calibration_ceiling_gbp": _CALIBRATED_SAVINGS_CEILING_GBP,
        "world_curve_beyond_calibration": beyond,
        "world_curve_basis": basis,
        #: NOT INDEPENDENT, said on the row itself. See `shared_calibration_holds`.
        "both_sides_calibrated_from": SHARED_CALIBRATION_SERIES,
    }


def _average_player(*, annual_revenue_gbp: float, eac_kwh: float) -> dict | None:
    """What Ofgem's published EBIT allowance says an efficient supplier earns on this customer.

    THE BILL BASIS IS NAMED RATHER THAN ASSUMED. The allowance's variable component scales with
    the cap level EXCLUDING EBIT, headroom and VAT. What this book publishes is `revenue_gbp` --
    this company's own revenue, which includes its GBP 2.00/MWh margin and excludes VAT. Using it
    as the base slightly OVERSTATES the average player's variable component, by 1.3975% of a
    margin that is itself tiny -- about a penny a year. Named because an unnamed approximation in
    a control is how a control stops being one.
    """
    try:
        result = average_player_margin(annual_revenue_gbp, eac_kwh, fuels=1)
    except AverageMarginUnavailable as exc:
        return {"available": False, "why": str(exc)[:120]}
    return {
        "available": True,
        "low": round(result.low_gbp_per_mwh, 2),
        "high": round(result.high_gbp_per_mwh, 2),
        "low_gbp_per_year": round(result.low_gbp_per_year, 2),
        "high_gbp_per_year": round(result.high_gbp_per_year, 2),
    }


def _average_player_summary(rows: list[dict]) -> dict:
    """THE QUESTION THE ARMS COMPARISON COULD NOT ANSWER UNTIL NOW: is the control a credible
    average player?

    Director, 2026-08-25: *"there has to be a baseline to beat. Average behaviour is the control
    ... Without that comparison, 'it performed well' means nothing."* The control has been this
    company's own flat rule, and nothing in the tree could say whether that rule was anywhere
    near average. Ofgem's Default Tariff Cap publishes the regulator's own answer.
    """
    scored = [r["average_player_gbp_per_mwh"] for r in rows
              if (r.get("average_player_gbp_per_mwh") or {}).get("available")]
    if not scored:
        return {"available": False,
                "why": "no account carried both a bill and a consumption, so no average-player "
                       "margin could be computed for any of them"}
    lows = sorted(s["low"] for s in scored)
    highs = sorted(s["high"] for s in scored)
    n = len(lows)
    median_low, median_high = lows[n // 2], highs[n // 2]
    return {
        "available": True,
        "accounts_scored": n,
        "source": "Ofgem Default Tariff Cap EBIT allowance, decision 25 August 2023, cap period "
                  "11a -- docs/domain_artefact_library/regulatory/price_cap_ebit_allowance.md",
        "median_gbp_per_mwh_low": round(median_low, 2),
        "median_gbp_per_mwh_high": round(median_high, 2),
        "this_companys_flat_rule_gbp_per_mwh": TARGET_MARGIN_GBP_PER_MWH,
        "flat_rule_as_share_of_average_low": round(TARGET_MARGIN_GBP_PER_MWH / median_low, 3)
        if median_low else None,
        "flat_rule_as_share_of_average_high": round(TARGET_MARGIN_GBP_PER_MWH / median_high, 3)
        if median_high else None,
        "what_it_means": (
            "The control this comparison scores the value arm against is this company's own flat "
            "rule. If that rule sits well below what the regulator allows an efficient supplier "
            "to earn, then an arm 'beating' it has demonstrated the control's implausibility and "
            "not its own inference -- which is the one thing the director's frame says the "
            "comparison must not do. A RANGE rather than a figure because the published "
            "allowance is dual fuel and this book is single fuel; see the source."
        ),
    }


def compare(run: dict, book: dict, as_of_year: int = AS_OF_YEAR) -> dict:
    """Both arms over every account the company has enough of its own record to price."""
    legs = _legs(book)
    per_account, skipped = [], collections.Counter()

    for cid, record in (run.get("per_customer_lifetime") or {}).items():
        leg = legs.get(cid) or {}
        total_kwh = float(leg.get("total_kwh") or 0.0)
        avg_rate = float(leg.get("avg_rate_gbp_per_mwh") or 0.0)
        bills = float(leg.get("bill_count") or 0.0)
        years = max(1.0, bills / BILLS_PER_YEAR)
        eac = total_kwh / years
        if eac <= 0.0 or avg_rate <= 0.0:
            # NAMED, not dropped. An account the company cannot price is a fact about its own
            # records, and a comparison that silently covers 200 of 263 accounts is a different
            # claim from one that covers all of them.
            skipped["no consumption or rate on this company's own record"] += 1
            continue
        common = dict(
            customer_id=cid,
            current_rate_gbp_per_mwh=avg_rate,
            base_rate_gbp_per_mwh=avg_rate - TARGET_MARGIN_GBP_PER_MWH,
            eac_kwh=eac,
            tenure_years=years,
            cost_to_serve_gbp_per_year=float(record.get("cost_to_serve_gbp") or 0.0) / years,
            expected_periods=min(6.0, years),
            segment=record.get("segment") or "resi",
            renewal_year=as_of_year,
            # EXPECTED COST, from the company's own records. Credit risk is the supplier's own
            # segmentation (`CREDIT_RISK_BY_CUSTOMER`, seed estimates, defaulting to medium for
            # an account it has not segmented -- which is 259 of 263 and is itself worth
            # noticing); payment timing is that segment's own expected delay; and the standing
            # charge is what this customer really pays per day and the first version forgot.
            credit_risk=CREDIT_RISK_BY_CUSTOMER.get(cid, DEFAULT_CREDIT_RISK),
            payment_delay_days=PAYMENT_TIMING_DAYS_BY_CREDIT_RISK.get(
                CREDIT_RISK_BY_CUSTOMER.get(cid, DEFAULT_CREDIT_RISK)),
            annual_revenue_gbp=float(leg.get("revenue_gbp") or 0.0) / years,
            fixed_revenue_gbp_per_year=365.0 * standing_charge_rate(
                record.get("commodity") or "electricity", record.get("segment") or "resi"),
        )
        try:
            flat = decide_margin(arm=FLAT_RULES, **common)
            value = decide_margin(arm=VALUE_BASED, **common)
        except MarginDecisionUnavailable as exc:
            skipped[str(exc)[:60]] += 1
            continue
        per_account.append({
            "customer_id": cid,
            "segment": common["segment"],
            "eac_kwh": round(eac, 1),
            "flat_margin_gbp_per_mwh": flat.margin_gbp_per_mwh,
            "value_margin_gbp_per_mwh": value.margin_gbp_per_mwh,
            "value_over_flat_multiple": round(
                value.margin_gbp_per_mwh / flat.margin_gbp_per_mwh, 1) if flat.margin_gbp_per_mwh else None,
            "implied_bill_change_pct": round(
                100.0 * (value.margin_gbp_per_mwh - flat.margin_gbp_per_mwh) / avg_rate, 1),
            "endpoint_bound": value.endpoint_bound,
            #: WHICH end, because "wanted to charge more than it may" and "wanted to charge less
            #: than it may" are opposite findings and this record used to report them as one.
            "endpoint_side": value.endpoint_side,
            #: WHICH LAWFUL CEILING THIS ANSWER WAS DECIDED UNDER, or none -- read off the
            #: arguments actually passed rather than described in a comment. This call site
            #: passes no `max_offered_rate_gbp_per_mwh`, so `ceiling_bound` below is
            #: structurally False for every account here and `endpoint_side == "ceiling"` can
            #: only mean the top of the candidate grid under the churn model's support bound.
            #: The sibling artefact (`docs/observability/value_cycle_ab.json`) prices under the
            #: Ofgem domestic cap and publishes counts with the SAME NAMES, and the two were
            #: read side by side as contradicting each other. Recorded per account so the day a
            #: ceiling is threaded through here this becomes true by itself instead of leaving
            #: a comment to rot.
            "lawful_ceiling_gbp_per_mwh": common.get("max_offered_rate_gbp_per_mwh"),
            "ceiling_bound": value.ceiling_bound,
            "extrapolation_bound": value.extrapolation_bound,
            #: How many candidates the bounds took off the grid, separately from whether that
            #: changed the answer. The two used to be the same field and the count was being read
            #: as the cause.
            "candidates_removed": value.candidates_removed,
            "withheld_reason": value.withheld_reason,
            "credit_risk": CREDIT_RISK_BY_CUSTOMER.get(cid, DEFAULT_CREDIT_RISK),
            "expected_cost_gbp_per_year": round(value.costs.total_gbp, 2) if value.costs else None,
            "bad_debt_gbp_per_year": round(value.costs.bad_debt_gbp, 2) if value.costs else None,
            "unsourced_cost_terms": list(value.costs.unsourced) if value.costs else [],
            # WHAT AN AVERAGE PLAYER WOULD HAVE EARNED on this same customer, from Ofgem's
            # published EBIT allowance. Read `company/pricing/regulated_average_margin.py` for
            # why a single-fuel answer is a RANGE. This is a COMPARATOR and never a target: the
            # value arm is not scored against it and no decision reads it.
            "average_player_gbp_per_mwh": _average_player(
                annual_revenue_gbp=float(leg.get("revenue_gbp") or 0.0) / years, eac_kwh=eac),
            "belief_vs_truth": belief_versus_truth(
                offered_rate=common["base_rate_gbp_per_mwh"] + value.margin_gbp_per_mwh,
                current_rate=avg_rate, tenure_years=years, eac_kwh=eac,
                segment=common["segment"], term_start=f"{as_of_year}-01-01"),
        })

    chosen = collections.Counter(r["value_margin_gbp_per_mwh"] for r in per_account)
    n = len(per_account)
    # The verdict READS the gap rather than restating a cause beside it -- see `_belief_clause`.
    belief = _belief_summary(per_account)
    return {
        "as_of_year": as_of_year,
        "accounts_priced": n,
        "accounts_skipped": dict(skipped),
        #: WHAT THE COUNTS BELOW ARE OVER, AND UNDER WHICH BOUNDS. See `_population`: this
        #: artefact and the realised A/B publish `endpoint_at_ceiling` under one name over two
        #: different populations under two different ceilings, and on 2026-08-26 the two were
        #: read as contradicting each other ("interior on 255 of 263" against "at the ceiling on
        #: 20 of 42"). Both were true. Neither could say so in its own words.
        "population": _population(per_account, as_of_year),
        "control": {
            "arm": FLAT_RULES,
            "margin_gbp_per_mwh": TARGET_MARGIN_GBP_PER_MWH,
            "what_it_is": (
                "what this company does today: one margin for every account, whoever they are. "
                "Imported from saas/tariff_pricing.py rather than restated, so the control "
                "cannot drift from the supplier it describes."
            ),
        },
        "average_player": _average_player_summary(per_account),
        "model_support_bound_pct": round(max_supported_rate_increase_pct(), 1),
        "differs_from_control": sum(
            1 for r in per_account if r["value_margin_gbp_per_mwh"] != TARGET_MARGIN_GBP_PER_MWH),
        "endpoint_bound": sum(1 for r in per_account if r["endpoint_bound"]),
        "endpoint_at_ceiling": sum(1 for r in per_account if r["endpoint_side"] == "ceiling"),
        "endpoint_at_floor": sum(1 for r in per_account if r["endpoint_side"] == "floor"),
        "extrapolation_bound": sum(1 for r in per_account if r["extrapolation_bound"]),
        "grid_trimmed": sum(1 for r in per_account if r["candidates_removed"]),
        #: THE SHARE OF THE BOOK ON ONE MARGIN, which is how a quantised search confesses. On
        #: 2026-08-25 this was 0.407 -- 107 of 263 accounts on exactly GBP 130/MWh, a rung of the
        #: candidate grid -- while every one of those accounts had a distinct interior optimum
        #: within a pound of a different number. A record of per-customer decisions in which two
        #: thirds of the book share two values is reporting the grid.
        "chosen_margin_concentration": round(
            max(chosen.values()) / n, 3) if n else None,
        "withheld_on_vulnerability": sum(1 for r in per_account if r["withheld_reason"]),
        "chosen_margins": {str(k): v for k, v in sorted(chosen.items())},
        "segmented_credit_risk": sum(1 for r in per_account if r["customer_id"] in CREDIT_RISK_BY_CUSTOMER),
        "median_implied_bill_change_pct": (
            sorted(r["implied_bill_change_pct"] for r in per_account)[n // 2] if n else None),
        "belief_vs_truth": belief,
        "verdict": _verdict(per_account, belief, _average_player_summary(per_account)),
        "accounts": per_account,
    }


def _population(rows: list[dict], as_of_year: int) -> dict:
    """WHICH decisions these counts are over, so they cannot be compared by name alone.

    THE DEFECT THIS DISCHARGES is a reconciliation, not an arithmetic error. This artefact and
    `docs/observability/value_cycle_ab.json` both publish `endpoint_bound`, `endpoint_at_ceiling`
    and `ceiling_bound`, computed by the same `decide_margin` — and they disagree, because they
    ask it different questions:

      * here — ONE decision per account, taken at a single moment (`as_of_year`), off a finished
        run's own record, with NO lawful ceiling passed;
      * there — one decision per RENEWAL EVENT a ten-year run actually reached, at that term's
        own rate under that term's own Ofgem cap window.

    So `endpoint_at_ceiling` does not mean the same thing in the two files, and until this block
    existed nothing in either said so. `what_endpoint_at_ceiling_means` is COMPUTED from whether
    a ceiling was in fact passed, not asserted, so it changes by itself if that ever changes.
    """
    under_ceiling = sum(1 for r in rows if r.get("lawful_ceiling_gbp_per_mwh") is not None)
    return {
        "unit": "one renewal decision per ACCOUNT, taken at a single moment",
        "as_of_year": as_of_year,
        "decisions": len(rows),
        "distinct_accounts": len({r["customer_id"] for r in rows}),
        "priced_under_a_lawful_ceiling": under_ceiling,
        "lawful_ceiling_passed": bool(under_ceiling),
        "what_endpoint_at_ceiling_means": (
            "the top of the candidate grid under the churn model's own support bound, and NOT "
            "the Ofgem price cap: this call site passes no `max_offered_rate_gbp_per_mwh`, so "
            "`ceiling_bound` is structurally False for every account here and its count is not "
            "a measurement of anything. A run that DOES price under the cap will report a far "
            "larger ceiling count on the same book and the same module, and that is not a "
            "contradiction."
            if not under_ceiling else
            "the highest margin this account could lawfully be offered -- a real ceiling was "
            "passed for {} of {} decisions, so `ceiling_bound` here is a measurement and can be "
            "compared with the realised A/B's.".format(under_ceiling, len(rows))
        ),
        "sibling_artefact": "docs/observability/value_cycle_ab.json",
    }


def _belief_summary(rows: list[dict]) -> dict:
    """How wrong the company would be, at the price its own arm chooses.

    UNDER-ESTIMATES ARE COUNTED SEPARATELY because the sign is the whole story: a company that
    believes fewer customers will leave than actually will is a company that will over-price and
    be punished for it, and that is the failure mode this arm has.
    """
    scored = [r["belief_vs_truth"] for r in rows if r.get("belief_vs_truth")]
    if not scored:
        return {"available": False, "why": "no account could be scored against the world"}
    errors = sorted(s["belief_error_pp"] for s in scored)
    n = len(errors)
    beyond = sum(1 for s in scored if s.get("world_curve_beyond_calibration"))
    differentials = sorted(s["price_differential_vs_svt"] for s in scored
                           if s.get("price_differential_vs_svt") is not None)
    provenance = shared_calibration_holds()
    return {
        "available": True,
        "accounts_scored": n,
        "median_belief_error_pp": errors[n // 2],
        "mean_belief_error_pp": round(sum(errors) / n, 1),
        "underestimating_departures": sum(1 for e in errors if e < -1.0),
        "median_price_differential_vs_svt": (
            round(differentials[len(differentials) // 2], 4) if differentials else None),
        "scored_beyond_the_world_calibration": beyond,
        "share_beyond_the_world_calibration": round(beyond / n, 3),
        # THE REFUSAL, AND IT IS THE POINT OF THIS BLOCK. The number above is a real
        # measurement of a real disagreement; what it is NOT is evidence that the company
        # inferred anything. Published without this, a median of a couple of percentage points
        # reads as "the company nearly knows the world" -- which is exactly what two calibrations
        # of one series look like, and exactly what a reader will quote it as.
        "publishable_as_evidence_of_inference": not provenance["co_calibrated"],
        "shared_calibration": provenance,
        "refusal": (
            "NOT EVIDENCE OF THE COMPANY'S INFERENCE. The two sides share a calibration source "
            "({}), and {} of {} scored accounts were compared at a differential where the world "
            "EXTRAPOLATES rather than observes. Quote this as a measured disagreement between two "
            "fits of one series; do not quote it as the company predicting the world. See "
            "`shared_calibration.what_would_discharge_it`."
        ).format(provenance["series"], beyond, n) if provenance["co_calibrated"] else "",
        "what_it_means": (
            "Positive means the company expects MORE departures than the world would deliver; "
            "negative means it expects FEWER -- it will over-price and be punished. This is the "
            "shape the thesis says the advantage must come from -- but only once the two sides "
            "stop sharing a source; until then see `refusal`."
        ),
    }


def _belief_clause(belief: dict) -> str:
    """Which of the two candidate causes the belief-vs-truth gap actually supports, READ OFF
    THE GAP rather than asserted beside it.

    The two are not the same problem and they need opposite work. If the company UNDER-estimates
    departures at its own chosen price it will over-price and be punished, and the belief is
    still wrong. If the gap is small or conservative, the belief is carrying the decision and
    what remains is whether the FLAT CONTROL is a credible average player -- because an arm that
    beats a control nobody would run measures the control, not the inference.
    """
    if not belief.get("available"):
        return ("The belief-vs-truth gap could not be scored, so which of the two causes this is "
                "cannot be read off this run.")
    median = belief["median_belief_error_pp"]
    under = belief["underestimating_departures"]
    scored = belief["accounts_scored"]
    if median < -1.0:
        return ("The belief is still the cause: the company under-estimates departures at its "
                "own chosen price on {} of {} accounts (median {:+.1f}pp), so it would "
                "over-price and be punished for it.").format(under, scored, median)
    return ("The belief is no longer the obvious cause -- the median account is scored {:+.1f}pp "
            "against the world, on the conservative side, with {} of {} under-estimating "
            "departures.").format(median, under, scored)


def _co_calibration_clause(belief: dict) -> str:
    """WHAT THE GAP ABOVE IS NOT, said in the same paragraph that quotes it.

    A caveat that lives in a nested key is a caveat nobody reads: the verdict paragraph is what
    gets pasted into a digest, so the refusal has to travel with the number rather than beside it.
    Derived from the same record the refusal is derived from, so it cannot say "co-calibrated"
    while the record says otherwise.
    """
    if not belief.get("available"):
        return ""
    if belief.get("publishable_as_evidence_of_inference"):
        return ("The two sides no longer share a calibration source, so that gap now speaks to "
                "the company's own inference.")
    beyond = belief.get("scored_beyond_the_world_calibration") or 0
    scored = belief.get("accounts_scored") or 0
    return ("Either way it is NOT evidence of the company's inference: the company's estimator "
            "and the world's price response descend from the same {}, and {} of {} accounts were "
            "scored where the world extrapolates the last informed slope rather than observing "
            "anything. A figure that cannot distinguish inference from shared arithmetic is not "
            "quotable as either -- what would discharge it is recorded beside it.").format(
        belief.get("shared_calibration", {}).get("series", "public switching series"),
        beyond, scored)


def _control_clause(average: dict, rows: list[dict]) -> str:
    """WHETHER THE CONTROL IS A CREDIBLE AVERAGE PLAYER, answered with an external figure instead
    of left open.

    This clause used to end "what that leaves open is whether the flat control is a credible
    average player" and stop there, which is a question a reader cannot answer either. Ofgem's
    published EBIT allowance answers it, and the answer is not the convenient one: the control IS
    under-priced, and nowhere near enough to explain the arm.
    """
    if not average.get("available"):
        return ("Whether the flat control is a credible average player could not be scored on "
                "this run, so that cause stays open.")
    low = average["median_gbp_per_mwh_low"]
    high = average["median_gbp_per_mwh_high"]
    flat = average["this_companys_flat_rule_gbp_per_mwh"]
    chosen = sorted(r["value_margin_gbp_per_mwh"] for r in rows)[len(rows) // 2] if rows else 0.0
    ratio_low = chosen / high if high else 0.0
    return ("The flat control IS under-priced -- GBP {:.2f}/MWh against a regulated average of "
            "GBP {:.2f}-{:.2f} for an efficient supplier -- but not nearly enough to be the "
            "cause: the value arm's median choice of GBP {:.0f}/MWh is still {:.0f}x the TOP of "
            "that range. Repricing the control to average behaviour would move it by a factor of "
            "two to four and leave the arm's answer an order of magnitude away, so the arm is "
            "not beating a straw man -- it is asking to charge many times what a regulated "
            "efficient supplier earns.").format(flat, low, high, chosen, ratio_low)


def _verdict(rows: list[dict], belief: dict, average: dict) -> dict:
    """The one paragraph a reader needs, DERIVED, so it cannot go stale beside the numbers.

    A comparison that leaves the reader to work out whether the arm is usable will be quoted as
    though it were, and this one is not usable — see the reason it names.
    """
    if not rows:
        return {"fit_to_run": False, "why": "no account could be priced, so nothing was compared"}
    at_ceiling = sum(1 for r in rows if r.get("endpoint_side") == "ceiling")
    at_floor = sum(1 for r in rows if r.get("endpoint_side") == "floor")
    at_edge = sum(1 for r in rows if r["endpoint_bound"])
    median_change = sorted(r["implied_bill_change_pct"] for r in rows)[len(rows) // 2]
    fit = at_edge == 0 and median_change < 25.0
    if fit:
        why = ("The value arm found interior optima and moves the median bill "
               "by {:+.0f}%. ").format(median_change) + _co_calibration_clause(belief)
    else:
        # THE DIAGNOSIS IS DERIVED, NOT WRITTEN DOWN, and this paragraph is the reason that
        # rule earned itself. Until 2026-08-25 it asserted a fixed cause -- the churn model's
        # 0.95 ceiling and its floor of captive customers -- which was true when it was
        # written and became FALSE the moment the ceiling was fixed, while the verdict stayed
        # correctly False for an entirely different reason. A stale cause beside a live number
        # is worse than no cause: a reader trusts it and stops looking.
        parts = []
        # THE TWO EDGES ARE OPPOSITE FINDINGS AND THIS SENTENCE USED TO CONFLATE THEM. Until
        # 2026-08-25 any endpoint read as "chose the highest margin available", which on the
        # book that then existed happened to be true. It is not true of the floor: the accounts
        # sitting there are 190-340 kWh/year meters whose 98.55 GBP standing charge IS the
        # relationship, and whose profit-maximising COMMODITY margin is NEGATIVE -- the arm wants
        # to sell them electricity below cost to keep the standing charge, and cannot, because
        # the lowest candidate on the grid is 0.50. A reader told that as "chose the highest
        # margin available" concludes the exact opposite of what the arm found.
        if at_ceiling:
            parts.append(
                "chose the highest margin available to it on {} of {} accounts, which is a "
                "ceiling reporting itself as a decision".format(at_ceiling, len(rows)))
        if at_floor:
            parts.append(
                "wanted to price BELOW the lowest margin it may offer on {} of {} accounts -- "
                "micro-consumption meters whose standing charge is the whole relationship, where "
                "the profit-maximising commodity margin is negative and the grid's floor is what "
                "decided".format(at_floor, len(rows)))
        if median_change >= 25.0:
            parts.append(
                "would move the median bill by {:+.0f}%, far outside anything this company has "
                "ever charged or observed a customer respond to".format(median_change))
        why = ("The value arm " + " and ".join(parts) + ". Not fit to wire to the renewal desk. "
               + _belief_clause(belief) + " " + _co_calibration_clause(belief) + " "
               + _control_clause(average, rows))
    return {
        "fit_to_run": fit,
        "belief_gap_publishable_as_inference": bool(
            belief.get("publishable_as_evidence_of_inference")),
        "at_grid_edge": at_edge,
        "at_grid_edge_ceiling": at_ceiling,
        "at_grid_edge_floor": at_floor,
        "median_implied_bill_change_pct": median_change,
        "why": why,
    }


#: The coupled pair this tool measures. The WORLD owns how a household responds to its own
#: supplier's price position (`simulation/market_switching_propensity.churn_position_multiplier`,
#: reached through `customer_events`); the COMPANY owns its estimate of the same thing
#: (`company/crm/enriched_churn_estimate`). Named as atom ids because that is what the ledger and
#: the coupled-triad gate read.
WORLD_ATOM_ID = "B10_competitor_switching_response"
TWIN_ATOM_ID = "B4_competitor_field"


def coupling_is_declared() -> tuple[bool, str]:
    """Does the MAP declare this world/twin pair, or would writing the ledger invent one?

    THE LEDGER IS READ AS THE MAP'S OWN RECORD, and `tools/couple_clv.py` records what happens
    when a row's key and its actual subject come apart: a control keyed `EP1_clv_three_horizon`
    that graded a different module's belief entirely, and stayed bit-identical when its named
    subject's whole output was deleted. It called that shape MIS-SUBJECTED. A row keyed on a pair
    the map does not declare is the same defect one step earlier -- the pair itself would be this
    tool's invention, and a reader would take it for the map's.

    So the write REFUSES rather than asserting a coupling nobody declared, and says what would
    make it legal: `B10_competitor_switching_response` currently has no twin on the map, and
    naming one there is a map edit with its own owner.
    """
    try:
        from background.coupled_triad import build_coupling

        atoms = map_store.load_atoms(PROJECT / "docs" / "design" / "maturity_map.yaml")
        coupling = build_coupling(atoms)
    except Exception as exc:
        return False, f"the map's coupling could not be read ({exc!r}), so the pair is unverified"
    declared = coupling.get(WORLD_ATOM_ID)
    if declared == TWIN_ATOM_ID:
        return True, "the map declares {} -> {}".format(WORLD_ATOM_ID, TWIN_ATOM_ID)
    return False, (
        "the map does not declare {} -> {} (it says {!r}). Writing the row would invent a "
        "coupling and publish it as the map's. Declare the twin on the map first."
    ).format(WORLD_ATOM_ID, TWIN_ATOM_ID, declared)


def _git_head() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT),
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip()[:12] if out.returncode == 0 else None
    except Exception:
        return None


def price_belief_gap(rows: list[dict]):
    """The company's price-response belief against the world's, normalised by NO SKILL.

    THE GAP IS THE SCORE (COUPLED_TRIAD_DESIGN). The belief-vs-truth summary beside this reports
    a median error in percentage points, which says how BIASED the company is and nothing about
    whether its belief carries any information. This says the second thing, and it is the one the
    thesis is about: the no-skill baseline is a supplier that predicts the SAME departure
    probability for every account -- the population mean -- which is exactly "a supplier applying
    flat rules with no per-customer view".

    A gap above 1.0 means the company's per-customer belief is WORSE than that flat rule. That is
    a result worth publishing, not a bug: an advantage that must come from inference cannot be
    claimed by a model carrying less information than the mean.
    """
    scored = [r["belief_vs_truth"] for r in rows if r.get("belief_vs_truth")]
    if len(scored) < 2:
        return None
    believed = [s["company_believes_p_leave"] for s in scored]
    actual = [s["world_would_p_leave"] for s in scored]
    mean_actual = sum(actual) / len(actual)
    raw = sum(abs(b - a) for b, a in zip(believed, actual)) / len(actual)
    g0 = sum(abs(mean_actual - a) for a in actual) / len(actual)
    provenance = shared_calibration_holds()
    beyond = sum(1 for s in scored if s.get("world_curve_beyond_calibration"))
    return _normalise(
        raw, g0,
        "a supplier that predicts the population-mean departure probability for every account "
        "-- flat rules, no per-customer view",
        "belief",
        {"accounts_scored": len(scored),
         "company_mean_abs_error": round(raw, 4),
         "no_skill_mean_abs_error": round(g0, 4),
         "world_mean_p_leave": round(mean_actual, 4),
         # CARRIED INTO THE COMPONENTS, not only into the prose, because the ledger row is what
         # a later reader consults and a note is the first thing an aggregator drops.
         "publishable_as_evidence_of_inference": not provenance["co_calibrated"],
         "co_calibrated_from": provenance["series"],
         "accounts_beyond_the_world_calibration": beyond},
        note=("Measured at the price the company's OWN value arm chooses, which is where it "
              "would actually be wrong. Below 1.0 the per-customer belief beats the flat rule; "
              "above 1.0 it is worse than predicting the mean."
              + ("" if not provenance["co_calibrated"] else
                 " NOT PUBLISHABLE AS EVIDENCE OF THE COMPANY'S INFERENCE: both sides descend "
                 "from {}, and {} of {} accounts were scored where the world extrapolates rather "
                 "than observes.".format(provenance["series"], beyond, len(scored)))),
    )


def generate(out_path: Path | None = None) -> dict:
    run = json.loads(latest_run_output().read_text(encoding="utf-8"))
    book = json.loads(BOOK_PATH.read_text(encoding="utf-8"))
    data = compare(run, book)
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    _ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    _ap.add_argument("--write-ledger", action="store_true",
                     help="persist the measured price-belief gap into coupled_gap_ledger.json")
    _args = _ap.parse_args()
    d = generate()
    print("priced {} account(s); {} differ from the control; {} at a grid edge".format(
        d["accounts_priced"], d["differs_from_control"], d["endpoint_bound"]))
    print("fit to run: {} -- {}".format(d["verdict"]["fit_to_run"], d["verdict"]["why"]))
    _gap = price_belief_gap(d["accounts"])
    if _gap is None:
        print("price-belief gap: NOT MEASURABLE -- fewer than two accounts could be scored "
              "against the world")
    else:
        print("price-belief gap: {} (company {} vs no-skill {})".format(
            _gap.gap, _gap.raw_gap, _gap.g0))
        if _gap.gap is not None and _gap.gap > 1.0:
            print("  -> WORSE THAN THE FLAT RULE: the per-customer belief carries less "
                  "information than predicting the population mean, so no inference advantage "
                  "can be claimed from it.")
        _declared, _why = coupling_is_declared()
        _provenance = shared_calibration_holds()
        if _provenance["co_calibrated"]:
            print("  NOT EVIDENCE OF INFERENCE: both sides descend from {}. {}".format(
                _provenance["series"], _provenance["what_would_discharge_it"]))
        if _args.write_ledger and _provenance["co_calibrated"]:
            # THE REFUSAL WITH TEETH. The ledger is where this pair is read as the company's
            # inference against the world's truth; writing a co-calibrated pair there publishes
            # shared arithmetic under that heading, and no caveat further down the file survives
            # the quoting. Refuses BEFORE the undeclared-coupling check because it is the wider
            # objection: declaring the twin on the map would not make the two sides independent.
            print("  ledger NOT written: the pair is co-calibrated, so the gap cannot be "
                  "published as evidence of the company's inference")
        elif _args.write_ledger and not _declared:
            print("  ledger NOT written: {}".format(_why))
        elif _args.write_ledger:
            _ledger = write_gap_entry(
                WORLD_ATOM_ID, TWIN_ATOM_ID, _gap,
                measured_at=datetime.now(timezone.utc).isoformat(),
                run_git_commit=_git_head(),
            )
            print("  ledger written: {} -> gap={}".format(
                WORLD_ATOM_ID, _ledger[WORLD_ATOM_ID]["gap"]))
