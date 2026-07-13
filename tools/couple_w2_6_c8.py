"""COUPLED-TRIAD runner for the W2_6 <-> C8 pair (SME / I&C credit risk).

This is HARNESS code. It sits OUTSIDE the epistemic wall by design and is the
ONLY layer permitted to hold the hidden SIM truth (theta -- a business's hidden
distress/culture state) and the company's observable-only belief (b) side by
side to compute the belief-vs-truth GAP (COUPLED_TRIAD_DESIGN.md 1.3; identical
role to background/gap_metric.py). It lives in tools/ -- NOT under company/ or
saas/ -- so it is not scanned by the epistemic verifier and may legitimately
import ``simulation.*``.

THE COUPLED LOOP (3 loops, COUPLED_TRIAD):

  1. SIM adds depth   -- simulation.sme_distress (W2_6) holds each business's
                         HIDDEN distress/culture state. Its ONE sanctioned
                         observable is ``is_paying_late(as_of)`` -- IDENTICAL for
                         a habitual-late-payer (CULTURE) and a genuinely
                         DISTRESSED business. ``late_payment_cause(as_of)`` is the
                         ANSWER KEY, read here (harness) and NEVER by the company.
  2. COMPANY copes    -- the company NEVER sees the cause. This harness turns the
                         single observable (is_paying_late, per month, with
                         realistic admin noise) into the payment RECORDS a real
                         supplier holds, plus the sector/tenure/consumption it
                         already holds. saas.sme_credit_risk (C8) reads only those
                         and ATTRIBUTES each late payment to distress-vs-culture.
  3. HARNESS measures -- TWO lenses on the same pair:
                         (a) classification_gap: cost-weighted 2x2 ability x
                             willingness misclassification, normalised to the
                             no-skill majority-class baseline. The CONFOUND is the
                             ability axis (CULTURE=can, DISTRESS/INSOLVENCY=cannot),
                             so mistaking real distress for habit is the expensive
                             8:1 error. This is the pair's headline ledger gap.
                         (b) attribution_gap: |naive - true| / |naive| -- the
                             fraction of the late-payment the company WRONGLY
                             attributes to distress-vs-culture. Reported alongside.

R15 INDEPENDENCE. The observable channel (a noisy monthly realisation of the
single sanctioned is_paying_late) and the assessor's thresholds are set
independently: the SIM decides who is late; the assessor encodes the supplier's
own reading of "what distress looks like" (persistence vs onset, sector, tenure,
consumption), blind to the SIM's hidden distress-onset / culture-incidence /
sector-hazard parameters. The gap is therefore a real measurement, not a
tautology, and is NOT tuned toward any target (R12 / R13).

DETERMINISM (C-S2). Every RNG is seeded from a stable sha256 of its context. No
unseeded randomness, no wall-clock inside the metric. ``measured_at`` /
``run_git_commit`` for the ledger are gathered by this harness (not by
gap_metric, which never calls a clock).
"""

from __future__ import annotations

import argparse
import hashlib
import random
import subprocess
from datetime import date, datetime, timezone

from simulation.sme_distress import (
    BUSINESS_SEGMENTS,
    LatePaymentCause,
    generate_business_distress,
)

from saas.sme_credit_risk import (
    BusinessObservationWindow,
    CreditRiskCause,
    SmeCreditRiskAssessor,
    cause_to_quadrant,
)

from background.gap_metric import (
    attribution_gap,
    classification_gap,
    write_gap_entry,
)

WORLD_ATOM_ID = "W2_6_sme_distress_twin"
TWIN_ATOM_ID = "C8_sme_credit_risk"

# Nominal steady-state monthly consumption (kWh) for a trading business; a ceased
# (insolvent) business consumes almost nothing -- a real observable (the meter
# stops turning). CURRICULUM-neutral harness scaffolding, not fitted.
_NOMINAL_MONTHLY_KWH = 1000.0
_INSOLVENT_KWH_FRACTION = 0.08

# Realistic monthly payment-observation noise on the single sanctioned observable
# (is_paying_late). A late-state month is usually -- not always -- observed late;
# a healthy month occasionally slips for benign admin reasons. Principled, frozen,
# NOT tuned toward a gap (R12/R13). Keeps the confound genuinely hard.
_P_LATE_WHEN_LATE_STATE = 0.85
_P_LATE_WHEN_HEALTHY = 0.05


def _rng(*parts) -> random.Random:
    """Deterministic RNG from a stable sha256 of the given parts (C-S2)."""
    key = ":".join(str(p) for p in parts)
    seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")
    return random.Random(seed)


def _monthly_payments(profile, cid: str, year: int, period: str) -> list[dict]:
    """12 observable monthly payment records for a period, realised from the SIM's
    single sanctioned observable ``is_paying_late`` (never from the hidden cause).
    ``period`` ('base'/'recent') keeps the two windows on independent noise seeds
    so recent noise never mirrors baseline noise."""
    r = _rng("pay", cid, year, period)
    recs: list[dict] = []
    for month in range(1, 13):
        as_of = date(year, month, 15).isoformat()
        late_state = profile.is_paying_late(as_of)  # the ONE observable
        p_late = _P_LATE_WHEN_LATE_STATE if late_state else _P_LATE_WHEN_HEALTHY
        if r.random() < p_late:
            # A bad month: mostly a late payment, occasionally a DD failure.
            result = "DD_FAILED" if r.random() < 0.25 else "LATE"
            days_late = r.randint(5, 45)
            recs.append({"result": result, "days_late": days_late})
        else:
            recs.append({"result": "ON_TIME", "days_late": 0})
    return recs


def _consumption(profile, year: int) -> float:
    """Recent-year observable consumption. A ceased (insolvent) business's meter
    stops -- derived harness-side from theta into a real observable, exactly as
    the payment records are. Trading/distressed businesses consume normally (the
    distress-vs-culture confound stays a PURELY payment-pattern problem, which is
    the hard part; consumption only helps separate the ceased case)."""
    state = profile.distress_state_at(date(year, 12, 31).isoformat())
    annual = _NOMINAL_MONTHLY_KWH * 12
    if state.value == "insolvent":
        return annual * _INSOLVENT_KWH_FRACTION
    return annual


# The SIM answer-key cause maps onto the SAME company label space by string value
# (both use none/culture/distress/insolvency). Kept explicit so a future SIM enum
# drift is caught rather than silently mis-scored.
_SIM_CAUSE_STR = {
    LatePaymentCause.NONE: "none",
    LatePaymentCause.CULTURE: "culture",
    LatePaymentCause.DISTRESS: "distress",
    LatePaymentCause.INSOLVENCY: "insolvency",
}


def build_scenario(n_customers: int, start_year: int, end_year: int):
    """Run the coupled loop and return (truth_q, belief_q, extras).

    Each (customer, year) with year in [start_year+1, end_year] is one instance
    (start_year is reserved as the first baseline). truth_q[i] / belief_q[i] are
    the (ability, willingness) quadrants of the SIM truth and the company belief.
    ``extras`` carries the attribution inputs and human-readable stats.
    """
    assessor = SmeCreditRiskAssessor()
    truth_q: list = []
    belief_q: list = []

    # Attribution accounting over LATE instances.
    true_late = true_late_distress = 0        # SIM truth
    belief_late = belief_late_distress = 0    # company belief
    # Confusion over the distress-vs-culture call, restricted to truly-late.
    n_instances = 0
    distress_missed_as_culture = 0            # the expensive cannot->can error
    culture_over_called_distress = 0          # the cheaper can->cannot error

    for i in range(n_customers):
        segment = BUSINESS_SEGMENTS[i % len(BUSINESS_SEGMENTS)]
        cid = f"BIZ{i:05d}"
        profile = generate_business_distress(
            customer_id=cid, segment=segment,
            sim_start_year=start_year, sim_end_year=end_year,
        )
        tenure0 = _rng("tenure", cid).uniform(0.5, 8.0)

        for year in range(start_year + 1, end_year + 1):
            n_instances += 1
            as_of = date(year, 12, 31).isoformat()

            true_cause = profile.late_payment_cause(as_of)      # ANSWER KEY
            t_quad = cause_to_quadrant(_SIM_CAUSE_STR[true_cause])

            window = BusinessObservationWindow(
                customer_id=cid,
                segment=segment,
                sector=profile.sector,           # sector is observable (on file)
                tenure_years=tenure0 + (year - start_year),
                baseline_payments=_monthly_payments(profile, cid, year - 1, "base"),
                recent_payments=_monthly_payments(profile, cid, year, "recent"),
                baseline_consumption_kwh=_NOMINAL_MONTHLY_KWH * 12,
                recent_consumption_kwh=_consumption(profile, year),
            )
            belief = assessor.assess(window)
            b_quad = belief.quadrant

            truth_q.append(t_quad)
            belief_q.append(b_quad)

            true_is_late = true_cause != LatePaymentCause.NONE
            true_is_distress = true_cause in (
                LatePaymentCause.DISTRESS, LatePaymentCause.INSOLVENCY
            )
            belief_is_late = belief.inferred_cause != CreditRiskCause.NONE
            belief_is_distress = belief.inferred_cause in (
                CreditRiskCause.DISTRESS, CreditRiskCause.INSOLVENCY
            )

            if true_is_late:
                true_late += 1
                if true_is_distress:
                    true_late_distress += 1
            if belief_is_late:
                belief_late += 1
                if belief_is_distress:
                    belief_late_distress += 1

            # Directional confound errors (only meaningful where truly late).
            if true_is_late and true_is_distress and not belief_is_distress:
                distress_missed_as_culture += 1
            if (true_cause == LatePaymentCause.CULTURE) and belief_is_distress:
                culture_over_called_distress += 1

    # Attribution: distress SHARE of late payment, company (naive) vs truth.
    delta_true = (true_late_distress / true_late) if true_late else 0.0
    delta_naive = (belief_late_distress / belief_late) if belief_late else 0.0

    extras = {
        "n_customers": n_customers,
        "n_instances": n_instances,
        "true_late": true_late,
        "true_late_distress": true_late_distress,
        "belief_late": belief_late,
        "belief_late_distress": belief_late_distress,
        "distress_missed_as_culture": distress_missed_as_culture,
        "culture_over_called_distress": culture_over_called_distress,
        "delta_true_distress_share": delta_true,
        "delta_naive_distress_share": delta_naive,
    }
    return truth_q, belief_q, extras


def measure(n_customers: int = 3000, start_year: int = 2016, end_year: int = 2025):
    truth_q, belief_q, extras = build_scenario(n_customers, start_year, end_year)

    cls = classification_gap(truth_q, belief_q)
    attr = attribution_gap(extras["delta_naive_distress_share"],
                           extras["delta_true_distress_share"])

    # The headline pair gap is the cost-weighted misclassification (normalised to
    # the no-skill baseline). The attribution lens is attached in components so
    # both numbers travel together and neither is hidden (design 1.4a+b).
    cls.components.update({
        "attribution_gap": attr.gap,
        "attribution_raw": attr.raw_gap,
        "attribution_delta_naive": attr.components["delta_naive"],
        "attribution_delta_true": attr.components["delta_true"],
        "distress_missed_as_culture": extras["distress_missed_as_culture"],
        "culture_over_called_distress": extras["culture_over_called_distress"],
        "true_late": extras["true_late"],
        "belief_late": extras["belief_late"],
    })
    cls.note = (
        "cost-weighted distress-vs-culture misclassification (W2_6 hidden "
        "distress/culture -> identical observable is_paying_late -> C8 attribution); "
        "ability axis = the can-pay/cannot-pay confound, 8:1 harm on reading real "
        "distress as mere habit. attribution_gap (fraction of late-payment wrongly "
        "attributed to distress) attached in components."
    )
    return cls, attr, extras


def _git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--customers", type=int, default=3000)
    ap.add_argument("--start-year", type=int, default=2016)
    ap.add_argument("--end-year", type=int, default=2025)
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gap into coupled_gap_ledger.json")
    args = ap.parse_args()

    cls, attr, extras = measure(args.customers, args.start_year, args.end_year)

    print("W2_6 <-> C8 coupled SME credit-risk scenario")
    print(f"  customers                 : {extras['n_customers']}")
    print(f"  instances (customer-years): {extras['n_instances']}")
    print(f"  truly late                : {extras['true_late']}"
          f"  (of which distress/insolvency: {extras['true_late_distress']})")
    print(f"  company flagged late      : {extras['belief_late']}"
          f"  (of which distress/insolvency: {extras['belief_late_distress']})")
    print(f"  distress MISSED as culture: {extras['distress_missed_as_culture']}"
          "   (the expensive cannot->can error)")
    print(f"  culture OVER-called distress: {extras['culture_over_called_distress']}")
    print(f"  fn_ability (distress read as can-pay): {cls.components['fn_ability']}")
    print(f"  fn_willingness (late read as on-time): {cls.components['fn_willingness']}")
    print(f"  classification GAP        : {cls.gap}")
    print(f"    baseline (g0)           : {cls.baseline}")
    print(f"  attribution GAP           : {attr.gap}"
          f"   (naive distress share {extras['delta_naive_distress_share']:.4f}"
          f" vs true {extras['delta_true_distress_share']:.4f})")

    if args.write_ledger:
        measured_at = datetime.now(timezone.utc).isoformat()
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, cls,
            measured_at=measured_at, run_git_commit=_git_head(),
        )
        print(f"  ledger written: {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
