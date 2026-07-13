"""COUPLED-TRIAD runner for the W2_4 <-> C6 pair (household budget / affordability).

This is HARNESS code. It sits OUTSIDE the epistemic wall by design and is the
ONLY layer permitted to hold the hidden SIM truth (theta -- the household budget)
and the company's observable-only belief (b -- the inferred affordability book)
side by side to compute the belief-vs-truth GAP (COUPLED_TRIAD_DESIGN.md 1.3;
identical role to background/gap_metric.py and tools/couple_w2_5_c7.py). It lives
in tools/ -- NOT under company/ or saas/ -- so it is not scanned by the epistemic
verifier and may legitimately import `simulation.*`.

THE COUPLED LOOP (3 loops, COUPLED_TRIAD):

  1. SIM adds depth   -- simulation.household_budget (W2_4) draws each household's
                         HIDDEN budget: income decile, essential-cost floor,
                         discretionary margin (which may be NEGATIVE), savings
                         buffer. The company NEVER reads any of it.
  2. COMPANY copes    -- the hidden budget, meeting a monthly energy bill,
                         produces an income-stress level (SIM physics, below),
                         which drives OBSERVABLE payment records via the
                         INDEPENDENT simulation.payment_timing model, plus an
                         observable arrears case and a noisy consumption read.
                         company.crm.affordability_inference (C6) infers each
                         customer's affordability band, and the book composition,
                         from those observables ALONE.
  3. HARNESS measures -- belief_gap(truth_dist, belief_dist, prior): the
                         total-variation distance between the TRUE book
                         composition (from the hidden budgets) and the company's
                         INFERRED composition, normalised to the blind national
                         prior (the no-book-info belief).

R15 INDEPENDENCE / R12-R13 NO-GOAL-SEEK. Three separately-authored pieces meet
here and none is fitted to the others:
  * the SIM budget distribution (household_budget.py, director curriculum);
  * the budget->income_stress physics (below) and payment_timing's stress->record
    physics (its own module);
  * the company's affordability thresholds (affordability_inference.py), set blind
    to all of the above.
The gap is therefore a real measurement. It is genuinely non-zero and NOT
recoverable to zero, because the observable channel is strictly coarser than the
truth: budget->income_stress is many-to-one (4 truth bands collapse into 3 stress
levels), stress->payment is stochastic, and a cannot-pay household sitting on
savings pays cleanly and is observationally a comfortable one. That information
loss is the wall holding, not a modelling defect -- see the honest interpretation
printed by main().

DETERMINISM (C-S2). Every RNG is seeded from a stable hash of its named inputs.
No unseeded randomness, no wall-clock. `measured_at`/`run_git_commit` for the
ledger are gathered by this harness (not by gap_metric, which never calls a clock).
"""

from __future__ import annotations

import argparse
import hashlib
import random
import subprocess
from datetime import date, datetime, timezone
from typing import Dict, List, Tuple

from simulation.household import IncomeStress
from simulation.household_budget import HouseholdBudget, draw_household_budget
from simulation.payment_timing import generate_payment_record

from company.crm.affordability_inference import (
    AffordabilityBand,
    AffordabilityInference,
    AffordabilityObservation,
    BAND_ORDER,
    composition_of,
    composition_vector,
)

from background.gap_metric import belief_gap, write_gap_entry

WORLD_ATOM_ID = "W2_4_household_budget"
TWIN_ATOM_ID = "C6_affordability_inference"

# ---------------------------------------------------------------------------
# National blind prior over affordability bands -- the belief the company would
# hold with ZERO book-specific information (the belief-gap normaliser g0). It is
# a plausible UK affordability shape (a fuel-poverty-shaped minority in real
# difficulty, most managing/comfortable); illustrative (R10), NOT a cited table,
# and NOT fitted to the gap. It exists only so the gap reads as "how much did
# knowing our own book beat knowing nothing".
_NATIONAL_PRIOR: Dict[AffordabilityBand, float] = {
    AffordabilityBand.NEGATIVE: 0.10,
    AffordabilityBand.STRETCHED: 0.25,
    AffordabilityBand.MANAGING: 0.40,
    AffordabilityBand.COMFORTABLE: 0.25,
}

# A nominal unit rate to turn a monthly bill into an annual consumption read
# (the observable). Illustrative.
_UNIT_RATE_GBP_PER_KWH = 0.28


def _rng(*parts) -> random.Random:
    """Deterministic RNG from a stable sha256 of the given parts (C-S2)."""
    key = ":".join(str(p) for p in parts)
    seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")
    return random.Random(seed)


# ---------------------------------------------------------------------------
# SIM PHYSICS (harness-side, holds theta). Both functions read the HIDDEN budget.
# They are the WORLD's ground truth, never visible to the company.
# ---------------------------------------------------------------------------

def _monthly_bill(budget: HouseholdBudget) -> float:
    """A household's monthly energy bill. It scales weakly with income decile
    (wealthier -> larger property/consumption) plus noise, so consumption is a
    GENUINE BUT WEAK observable proxy for affordability -- the only handle the
    company has to separate managing from comfortable. Deterministic."""
    r = _rng("bill", budget.customer_id)
    base = 70.0 + 7.0 * budget.income_decile
    return round(base + r.uniform(-15.0, 15.0), 2)


def true_affordability_band(budget: HouseholdBudget, monthly_bill: float) -> AffordabilityBand:
    """The GROUND-TRUTH affordability band from the hidden budget. Defined on the
    discretionary slack left AFTER the energy bill -- energy affordability is
    about how much room the bill leaves, not the bill in isolation. Cut-offs are
    affordability reasoning (R12: NOT tuned to move the gap)."""
    margin = budget.discretionary_margin_monthly
    residual = margin - monthly_bill
    if margin < 0:
        return AffordabilityBand.NEGATIVE
    if residual < 200.0:
        return AffordabilityBand.STRETCHED
    if residual < 800.0:
        return AffordabilityBand.MANAGING
    return AffordabilityBand.COMFORTABLE


def budget_to_income_stress(budget: HouseholdBudget, monthly_bill: float) -> IncomeStress:
    """Map the hidden budget to the income-stress level that drives OBSERVABLE
    payment behaviour (WORLD physics, independent of the company's thresholds).

    Savings act as a cushion: a negative-margin household with a deep buffer can
    still pay on time for a while (and so looks fine to the company). That cross
    -cutting cushion is the main reason the affordability band is NOT recoverable
    from payments alone -- the honest heart of the gap."""
    margin = budget.discretionary_margin_monthly
    residual = margin - monthly_bill
    savings_months = budget.savings_buffer / monthly_bill if monthly_bill > 0 else 1e9
    if margin < 0:
        return IncomeStress.HIGH if savings_months < 6 else IncomeStress.MODERATE
    if residual < 0:
        return IncomeStress.MODERATE if savings_months < 12 else IncomeStress.LOW
    if residual < 150.0:
        return IncomeStress.MODERATE if savings_months < 3 else IncomeStress.LOW
    return IncomeStress.LOW


# ---------------------------------------------------------------------------
# OBSERVABLE GENERATION -- what the company gets to see (derived from the hidden
# budget via the SIM physics above), then handed to the C6 twin.
# ---------------------------------------------------------------------------

def _observable_for(budget: HouseholdBudget, year: int) -> AffordabilityObservation:
    monthly_bill = _monthly_bill(budget)
    stress = budget_to_income_stress(budget, monthly_bill)

    # 12 monthly payment records, driven by the (hidden) income stress.
    r_pay = _rng("pay", budget.customer_id, year)
    recs = [
        generate_payment_record(
            budget.customer_id, date(year, m, 1), monthly_bill, stress, r_pay
        )
        for m in range(1, 13)
    ]

    # Observable arrears: an escalating case opens only under sustained
    # non-payment (>= 4 bad months in the year). Stage reflects severity. This is
    # the company's OWN collections record, not the budget.
    bad = sum(1 for x in recs if x["result"] in ("LATE", "DD_FAILED"))
    dd_fail = sum(1 for x in recs if x["result"] == "DD_FAILED")
    arrears_open = bad >= 4
    if dd_fail >= 6:
        stage = "default"
    elif dd_fail >= 3:
        stage = "second_notice"
    elif arrears_open:
        stage = "first_notice"
    else:
        stage = None

    annual_bill = round(monthly_bill * 12.0, 2)
    annual_kwh = round(annual_bill / _UNIT_RATE_GBP_PER_KWH, 1)

    return AffordabilityObservation(
        customer_id=budget.customer_id,
        segment="resi",
        recent_payments=recs,
        arrears_open=arrears_open,
        arrears_stage=stage,
        arrears_balance_gbp=round(dd_fail * monthly_bill, 2),
        annual_consumption_kwh=annual_kwh,
        annual_bill_gbp=annual_bill,
        tariff_unit_rate_gbp_per_mwh=_UNIT_RATE_GBP_PER_KWH * 1000.0,
        inbound_hardship_contacts=1 if (bad >= 6) else 0,
    )


def build_scenario(n_customers: int, year: int = 2022) -> Tuple[
    Dict[AffordabilityBand, float], Dict[AffordabilityBand, float], dict
]:
    """Run the coupled loop and return (truth_composition, belief_composition,
    stats). One customer = one household with a hidden budget; the truth band is
    read from the budget, the belief band is inferred from observables."""
    inference = AffordabilityInference()
    true_bands: List[AffordabilityBand] = []
    obs_list: List[AffordabilityObservation] = []
    confusion: Dict[Tuple[AffordabilityBand, AffordabilityBand], int] = {}

    for i in range(n_customers):
        cid = f"AFF{i:06d}"
        budget = draw_household_budget(cid)
        monthly_bill = _monthly_bill(budget)
        t_band = true_affordability_band(budget, monthly_bill)
        obs = _observable_for(budget, year)
        b_band = inference.infer_band(obs).band

        true_bands.append(t_band)
        obs_list.append(obs)
        confusion[(t_band, b_band)] = confusion.get((t_band, b_band), 0) + 1

    truth_dist = composition_of(true_bands)
    belief_dist = inference.book_composition(obs_list)

    correct = sum(v for (t, b), v in confusion.items() if t == b)
    # The harmful error: a truly can't-pay (NEGATIVE) household believed able to
    # pay (MANAGING/COMFORTABLE) -- the vulnerable-treated-as-fine miss.
    n_negative = sum(1 for t in true_bands if t == AffordabilityBand.NEGATIVE)
    missed_hardship = sum(
        v for (t, b), v in confusion.items()
        if t == AffordabilityBand.NEGATIVE
        and b in (AffordabilityBand.MANAGING, AffordabilityBand.COMFORTABLE)
    )
    stats = {
        "n_customers": n_customers,
        "year": year,
        "per_customer_accuracy": round(correct / n_customers, 4) if n_customers else 0.0,
        "n_true_negative": n_negative,
        "missed_hardship": missed_hardship,
        "missed_hardship_rate": round(missed_hardship / n_negative, 4) if n_negative else 0.0,
        "truth_dist": {b.value: round(truth_dist[b], 4) for b in BAND_ORDER},
        "belief_dist": {b.value: round(belief_dist[b], 4) for b in BAND_ORDER},
    }
    return truth_dist, belief_dist, stats


def measure(n_customers: int = 3000, year: int = 2022):
    """Compute the belief-family gap for the pair. Returns (GapResult, stats)."""
    truth_dist, belief_dist, stats = build_scenario(n_customers, year)
    truth_vec = composition_vector(truth_dist)
    belief_vec = composition_vector(belief_dist)
    prior_vec = composition_vector(_NATIONAL_PRIOR)

    result = belief_gap(truth_vec, belief_vec, prior=prior_vec)
    result.note = (
        "TV(company belief, hidden truth) over the affordability-band book "
        "composition (W2_4 hidden budgets -> observable payment/arrears/"
        "consumption -> C6 inference), normalised to the blind national prior. "
        "Non-zero and NOT recoverable to zero: the observable channel is strictly "
        "coarser than the hidden budget (can't-pay-on-savings pays cleanly; "
        "managing vs comfortable are indistinguishable from payments)."
    )
    result.components.update({
        "per_customer_accuracy": stats["per_customer_accuracy"],
        "missed_hardship_rate": stats["missed_hardship_rate"],
        "truth_dist": stats["truth_dist"],
        "belief_dist": stats["belief_dist"],
    })
    return result, stats


def _git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--customers", type=int, default=3000)
    ap.add_argument("--year", type=int, default=2022)
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gap into coupled_gap_ledger.json")
    args = ap.parse_args()

    result, stats = measure(args.customers, args.year)

    print("W2_4 <-> C6 coupled affordability-inference scenario")
    print(f"  customers                : {stats['n_customers']}  (year {stats['year']})")
    print(f"  TRUE book composition    : {stats['truth_dist']}")
    print(f"  BELIEVED book composition: {stats['belief_dist']}")
    print(f"  per-customer accuracy    : {stats['per_customer_accuracy']}")
    print(f"  true cannot-pay (NEG)    : {stats['n_true_negative']}")
    print(f"  missed-hardship rate     : {stats['missed_hardship_rate']}"
          f"  (NEG households believed able to pay)")
    print(f"  raw TV(belief, truth)    : {result.components.get('tv')}")
    print(f"  blind-prior TV (g0)      : {result.components.get('tv_prior')}")
    print(f"  GAP (normalised)         : {result.gap}")
    print(f"  baseline (g0)            : {result.baseline}")

    if args.write_ledger:
        measured_at = datetime.now(timezone.utc).isoformat()
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, result,
            measured_at=measured_at, run_git_commit=_git_head(),
        )
        print(f"  ledger written: {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
