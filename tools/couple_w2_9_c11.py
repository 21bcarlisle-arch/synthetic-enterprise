"""COUPLED-TRIAD runner for the W2_9 <-> C11 pair (segment debt T&C).

This is HARNESS code. It sits OUTSIDE the epistemic wall by design and is the
ONLY layer permitted to hold the hidden SIM truth (the customer's TRUE segment)
and the company's observable-only action (the T&C C11 applies from the OBSERVED
segment) side by side to compute the belief-vs-truth GAP
(COUPLED_TRIAD_DESIGN.md 1.3; same role as background/gap_metric.py and the
W2_5 runner). It lives in tools/ -- NOT under company/ or saas/ -- so it is not
scanned by the epistemic verifier.

THE COUPLED LOOP (3 loops):

  1. SIM adds depth   -- simulation.segment_debt_obligation (W2_9) holds the
                         CORRECT per-segment debt obligation (the answer key)
                         AND generates the OBSERVED segment recorded on the
                         company's book, which can be MISCLASSIFIED (a
                         microbusiness left on a domestic contract, etc).
  2. COMPANY copes    -- the company NEVER sees the true segment. It applies
                         C11 (company.compliance.segment_debt_policy.
                         select_debt_terms) to the OBSERVED segment it recorded.
  3. HARNESS measures -- misapplication_gap(truth_terms, applied_terms): the
                         fraction of accounts on the WRONG-segment T&C,
                         normalised to a no-skill (majority-class) applier.

R15 INDEPENDENCE. The world answer key derives the correct T&C from the TRUE
segment; C11 derives its applied T&C from the OBSERVED segment. Both read the
same real law (regulation-commons) but from a DIFFERENT segment source, so the
gap is a real compliance/fairness measurement, not a tautology. Not tuned to
any target (R12/R13): the misclassification rates are a frozen illustrative
curriculum, and the gap is whatever it is.

DETERMINISM (C-S2). The observed-segment channel and the true-segment mix are
both seeded from stable hashes (named substreams). No wall-clock, no global
RNG. `measured_at`/`run_git_commit` for the ledger are gathered by this
harness (not by gap_metric, which never calls a clock).
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
from datetime import date, datetime, timezone

from simulation.segment_debt_obligation import (
    BUSINESS_TERMS,
    DOMESTIC_TERMS,
    correct_obligation,
    observed_segment,
)

from company.compliance.segment_debt_policy import select_debt_terms

from background.gap_metric import misapplication_gap, write_gap_entry

WORLD_ATOM_ID = "W2_9_segment_debt_tnc"
TWIN_ATOM_ID = "C11_segment_debt_policy"

# The true-segment population mix. Real UK domestic-vs-non-domestic meter-point
# counts are ~28-29m domestic to ~2-3m non-domestic (BEIS/DESNZ sub-national
# consumption statistics) -> business is a ~7-8% minority of accounts. Split the
# business share between SME (the bulk of business meter points) and larger I&C.
# A frozen illustrative population shape (R13), not tuned to a gap number.
_TRUE_SEGMENT_MIX = [
    ("resi", 0.90),
    ("sme", 0.08),
    ("iandc", 0.02),
]

# The dates a debt case is assessed on -- one per LPCDCA half-year period across
# the anchored 2016-2025 rate history, so the scenario exercises the full
# statutory-rate span (the rate does not affect the wrong-segment gap, but keeps
# the scenario honest across the modelled window).
_ASSESSMENT_DATES = [date(y, m, 15) for y in range(2016, 2026) for m in (3, 9)]

# Arrears bands (GBP) a case can fall in -- varies the population, feeds the
# statutory-interest AMOUNT for business accounts. Does not change WHICH terms
# apply, so it does not bias the gap; included for scenario realism.
_ARREARS_BANDS = [85.0, 240.0, 620.0, 1850.0, 5400.0]


def _pick_true_segment(customer_id: str) -> str:
    """Deterministically assign a TRUE segment from the population mix, seeded
    per customer (C-S2, named substream)."""
    key = f"w2_9_true_segment:{customer_id}"
    draw = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big") / float(1 << 64)
    cum = 0.0
    for seg, share in _TRUE_SEGMENT_MIX:
        cum += share
        if draw < cum:
            return seg
    return _TRUE_SEGMENT_MIX[-1][0]


def _terms_class_of(debt_terms) -> str:
    """Reduce C11's applied DebtTerms to the obligation CLASS the world scores
    on: business-terms iff the company applied any business-only term (statutory
    interest OR a late charge), else domestic-terms."""
    if debt_terms.late_payment_interest_applies or debt_terms.late_payment_charges_permitted:
        return BUSINESS_TERMS
    return DOMESTIC_TERMS


def build_scenario(n_customers: int):
    """Run the coupled loop over a spread of (segment, date, arrears) cases and
    return (truth_labels, applied_labels, stats).

    Each (customer, date, arrears-band) is one case. Truth = the class the world
    says is correct for the customer's TRUE segment. Applied = the class C11
    applies from the OBSERVED (possibly misrecorded) segment.
    """
    truth_labels: list[str] = []
    applied_labels: list[str] = []
    n_misrecorded = 0
    n_true_business = 0
    n_observed_business = 0

    for i in range(n_customers):
        cid = f"W29C{i:06d}"
        true_seg = _pick_true_segment(cid)
        obs_seg = observed_segment(true_seg, cid)

        true_is_business = true_seg in ("sme", "iandc")
        obs_is_business = obs_seg in ("sme", "iandc")
        if true_is_business:
            n_true_business += 1
        if obs_is_business:
            n_observed_business += 1
        if true_is_business != obs_is_business:
            n_misrecorded += 1

        for as_of in _ASSESSMENT_DATES:
            # World answer key from the TRUE segment.
            correct = correct_obligation(true_seg, as_of)
            # Company applies C11 from the OBSERVED segment (the wall: it never
            # sees the true one). arrears varies the case but not the class.
            for _arrears in _ARREARS_BANDS:
                applied = select_debt_terms(obs_seg, as_of)
                truth_labels.append(correct.terms_class)
                applied_labels.append(_terms_class_of(applied))

    stats = {
        "n_customers": n_customers,
        "n_cases": len(truth_labels),
        "n_true_business": n_true_business,
        "n_observed_business": n_observed_business,
        "n_misrecorded_customers": n_misrecorded,
        "misrecord_rate": (n_misrecorded / n_customers) if n_customers else 0.0,
        "dates_per_customer": len(_ASSESSMENT_DATES),
        "arrears_bands": len(_ARREARS_BANDS),
    }
    return truth_labels, applied_labels, stats


def measure(n_customers: int = 5000):
    truth_labels, applied_labels, stats = build_scenario(n_customers)
    result = misapplication_gap(
        truth_labels, applied_labels, positive_class=BUSINESS_TERMS
    )
    result.note = (
        "fraction of arrears accounts on the WRONG-segment debt T&C (W2_9 true "
        "segment vs C11 applied-from-observed segment); a compliance/fairness "
        "gap driven by real onboarding segment misclassification, normalised to "
        "a blind majority-class applier."
    )
    return result, stats


def _git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--customers", type=int, default=5000)
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gap into coupled_gap_ledger.json")
    args = ap.parse_args()

    result, stats = measure(args.customers)

    print("W2_9 <-> C11 coupled segment-debt-T&C scenario")
    print(f"  customers                 : {stats['n_customers']}")
    print(f"  cases (cust x date x band): {stats['n_cases']}")
    print(f"  true business customers   : {stats['n_true_business']}")
    print(f"  observed business (C11)   : {stats['n_observed_business']}")
    print(f"  misrecorded customers     : {stats['n_misrecorded_customers']}"
          f"  (rate {stats['misrecord_rate']:.4f})")
    print(f"  wrong-T&C cases (raw)     : {result.components['n_wrong']}"
          f" / {result.components['n']}"
          f"  (error rate {result.components['error_rate']:.4f})")
    print(f"  wrongly applied business  : {result.components.get('wrongly_applied')}")
    print(f"  wrongly withheld business : {result.components.get('wrongly_withheld')}")
    print(f"  baseline (g0)             : {result.baseline}")
    print(f"  GAP (normalised)          : {result.gap}")

    if args.write_ledger:
        measured_at = datetime.now(timezone.utc).isoformat()
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, result,
            measured_at=measured_at, run_git_commit=_git_head(),
        )
        print(f"  ledger written: {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
