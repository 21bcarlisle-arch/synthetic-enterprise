"""COUPLED-TRIAD runner for the W2_7 <-> C9 pair -- the ARCHETYPE can't-pay /
won't-pay classification loop (COUPLED_TRIAD_DESIGN's highest-priority pair).

This is HARNESS code. It sits OUTSIDE the epistemic wall by design and is the ONLY
layer permitted to hold the hidden SIM truth (theta -- a household's hidden
ABILITY x WILLINGNESS quadrant) and the company's observable-only belief (b) side
by side to compute the belief-vs-truth GAP (COUPLED_TRIAD_DESIGN.md 1.3; identical
role to background/gap_metric.py). It lives in tools/ -- NOT under company/ or
saas/ -- so it is not scanned by the epistemic verifier and may legitimately import
``simulation.*``.

THE COUPLED LOOP (3 loops, COUPLED_TRIAD):

  1. SIM adds depth   -- simulation.willingness_classification (W2_7) holds each
                         customer's HIDDEN (ability, willingness) 2x2. Its ONE
                         sanctioned observable is ``is_in_arrears()`` -- IDENTICAL
                         for the three non-paying cells (CAN_WONT, CANNOT_WILL,
                         CANNOT_WONT). ``ability`` / ``willingness`` / ``quadrant``
                         are the ANSWER KEY, read HERE (harness) and NEVER by C9.
  2. COMPANY copes    -- the company NEVER sees the quadrant. This harness turns
                         the single observable (in arrears) plus the hidden truth
                         into the REAL records a supplier holds on an arrears
                         account -- part-payment behaviour, engagement, hardship
                         disclosure, metered consumption -- each with realistic
                         admin noise, then saas.arrears_classifier (C9) reads ONLY
                         those and classifies can't-pay vs won't-pay + gates
                         pursue/forbear.
  3. HARNESS measures -- classification_gap: cost-weighted 2x2 ability x
                         willingness misclassification, normalised to the no-skill
                         majority-class baseline. The CONFOUND is the ability axis
                         (CAN_WONT = can, CANNOT_* = cannot); mistaking a genuine
                         can't-pay for a strategic won't-pay is the expensive 8:1
                         error. Directional fn_ability/fn_willingness travel
                         alongside. The pursue/forbear gate outcomes + realised harm
                         are reported too.

R15 INDEPENDENCE. The observable-generation model here (how a hidden quadrant
shows up as engagement/part-payment/disclosure/consumption, with noise) and the
classifier's scoring weights are set INDEPENDENTLY: the harness decides how truth
leaks into behaviour; the classifier encodes the supplier's own reading of "what a
can't-pay looks like", blind to the SIM's hidden willingness-incidence / budget
parameters and to this harness's noise probabilities. The gap is therefore a real
measurement, not a tautology, and is NOT tuned toward any target (R12 / R13).

DETERMINISM (C-S2). Every RNG is seeded from a stable sha256 of its context. No
unseeded randomness, no wall-clock inside the metric. ``measured_at`` /
``run_git_commit`` for the ledger are gathered by this harness (not by gap_metric,
which never calls a clock).
"""

from __future__ import annotations

import argparse
import hashlib
import random
import subprocess
from datetime import datetime, timezone

from simulation.willingness_classification import (
    Ability as SimAbility,
    Willingness as SimWillingness,
    draw_willingness_profile,
)

from saas.arrears_classifier import (
    ArrearsObservationWindow,
    CantPayWontPayClassifier,
    Decision,
)

from background.gap_metric import (
    HARM_RATIO_R,
    classification_gap,
    write_gap_entry,
)

WORLD_ATOM_ID = "W2_7_willingness_classification"
TWIN_ATOM_ID = "C9_cantpay_wontpay_classifier"

# Nominal steady-state monthly consumption for a domestic account (kWh). Harness
# scaffolding, curriculum-neutral, not fitted.
_NOMINAL_MONTHLY_KWH = 300.0

# ---------------------------------------------------------------------------
# OBSERVABLE-GENERATION MODEL (R15: set INDEPENDENTLY of the classifier weights).
# How a hidden quadrant leaks into the four supplier-side observables, WITH noise
# so the confound is genuinely hard. These are principled and FROZEN -- never tuned
# toward a gap number (R12/R13). The point is that the leak is PARTIAL: a genuine
# can't-pay who is disengaged looks just like a strategic non-payer.
# ---------------------------------------------------------------------------
# P(engaged | willingness): willing customers respond, strategic non-payers avoid.
_P_ENGAGED_IF_WILL = 0.78
_P_ENGAGED_IF_WONT = 0.14
# P(made a part-payment | willingness): willing customers pay what they can.
_P_PARTPAY_IF_WILL = 0.60
_P_PARTPAY_IF_WONT = 0.05
# P(disclosed hardship | ability, willingness): genuine + willing customers
# disclose most; a genuine-but-unwilling household discloses less (chaos/shame); a
# strategic (can-pay) household rarely discloses (occasionally games it).
_P_DISCLOSE = {
    ("cannot", "will"): 0.68,
    ("cannot", "wont"): 0.28,
    ("can", "wont"): 0.07,
}
# Consumption rationing: a cannot-pay household cuts back (goes cold); a can-pay
# household lives normally. Realised as a kWh ratio with overlap (a small can-pay
# household can look low; a cannot-pay household on a cold-weather cap may not cut).
_RATION_RANGE_CANNOT = (0.45, 0.82)   # usually rationing, tail overlaps normal
_NORMAL_RANGE_CAN = (0.88, 1.12)      # lives normally
_P_CANNOT_DOES_NOT_RATION = 0.18      # noise: a cannot-pay who cannot cut further
_P_CAN_LOOKS_LOW = 0.12               # noise: a small can-pay household reads low


def _rng(*parts) -> random.Random:
    """Deterministic RNG from a stable sha256 of the given parts (C-S2)."""
    key = ":".join(str(p) for p in parts)
    seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")
    return random.Random(seed)


def _observe(cid: str, ability: str, willingness: str) -> ArrearsObservationWindow:
    """Realise the four supplier-side observables for one arrears account from its
    hidden (ability, willingness) truth, with independent admin noise (C-S2 seeded).
    The classifier sees ONLY the returned window; never the quadrant."""
    r = _rng("obs", cid)

    engaged = r.random() < (_P_ENGAGED_IF_WILL if willingness == "will" else _P_ENGAGED_IF_WONT)
    part_pay = r.random() < (_P_PARTPAY_IF_WILL if willingness == "will" else _P_PARTPAY_IF_WONT)
    disclosed = r.random() < _P_DISCLOSE.get((ability, willingness), 0.05)

    baseline = _NOMINAL_MONTHLY_KWH
    if ability == "cannot":
        if r.random() < _P_CANNOT_DOES_NOT_RATION:
            frac = r.uniform(*_NORMAL_RANGE_CAN)      # did not / could not cut back
        else:
            frac = r.uniform(*_RATION_RANGE_CANNOT)   # self-rationing
    else:  # can
        if r.random() < _P_CAN_LOOKS_LOW:
            frac = r.uniform(*_RATION_RANGE_CANNOT)   # a genuinely small household
        else:
            frac = r.uniform(*_NORMAL_RANGE_CAN)
    recent = baseline * frac

    return ArrearsObservationWindow(
        customer_id=cid,
        made_part_payment=part_pay,
        engaged=engaged,
        hardship_disclosed=disclosed,
        baseline_consumption_kwh=baseline,
        recent_consumption_kwh=recent,
    )


_SIM_ABILITY_STR = {SimAbility.CAN_PAY: "can", SimAbility.CANNOT_PAY: "cannot"}
_SIM_WILL_STR = {SimWillingness.WILL_PAY: "will", SimWillingness.WONT_PAY: "wont"}


def build_scenario(n_customers: int):
    """Run the coupled loop over ``n_customers`` drawn households, keeping only the
    ARREARS accounts (the classifier's population). Returns (truth_q, belief_q,
    extras)."""
    clf = CantPayWontPayClassifier()
    truth_q: list = []
    belief_q: list = []

    n_arrears = 0
    # Harm accounting over the pursue/forbear gate (realised, R13 cost matrix).
    pursued = forborne = 0
    pursued_cannot = 0          # the EXPENSIVE realised error: pursued a can't-pay
    forborne_strategic = 0      # the cheaper realised error: forbore a won't-pay
    # Directional classification confusion.
    cannot_read_as_can = 0      # ability FN: genuine can't-pay believed can-pay
    n_truth_cannot = 0
    n_truth_strategic = 0       # truth CAN_WONT

    for i in range(n_customers):
        cid = f"CUST{i:06d}"
        profile = draw_willingness_profile(cid)     # ANSWER KEY (harness only)
        if not profile.is_in_arrears():
            continue
        n_arrears += 1

        t_ability = _SIM_ABILITY_STR[profile.ability]
        t_will = _SIM_WILL_STR[profile.willingness]
        truth_q.append((t_ability, t_will))

        window = _observe(cid, t_ability, t_will)   # observables only
        belief = clf.assess(window)
        belief_q.append(belief.quadrant)

        truth_cannot = t_ability == "cannot"
        truth_strategic = (t_ability == "can" and t_will == "wont")
        if truth_cannot:
            n_truth_cannot += 1
            if belief.ability.value == "can":
                cannot_read_as_can += 1
        if truth_strategic:
            n_truth_strategic += 1

        if belief.decision == Decision.PURSUE:
            pursued += 1
            if truth_cannot:
                pursued_cannot += 1
        else:
            forborne += 1
            if truth_strategic:
                forborne_strategic += 1

    realised_harm = HARM_RATIO_R * pursued_cannot + 1.0 * forborne_strategic
    extras = {
        "n_customers": n_customers,
        "n_arrears": n_arrears,
        "n_truth_cannot": n_truth_cannot,
        "n_truth_strategic": n_truth_strategic,
        "cannot_read_as_can": cannot_read_as_can,
        "pursued": pursued,
        "forborne": forborne,
        "pursued_cannot_expensive_error": pursued_cannot,
        "forborne_strategic_loss": forborne_strategic,
        "realised_gate_harm": realised_harm,
    }
    return truth_q, belief_q, extras


def measure(n_customers: int = 60000):
    truth_q, belief_q, extras = build_scenario(n_customers)
    if not truth_q:
        raise SystemExit("no arrears accounts drawn -- increase --customers")

    cls = classification_gap(truth_q, belief_q)
    cls.components.update({
        "n_arrears": extras["n_arrears"],
        "pursued": extras["pursued"],
        "forborne": extras["forborne"],
        "pursued_cannot_expensive_error": extras["pursued_cannot_expensive_error"],
        "forborne_strategic_loss": extras["forborne_strategic_loss"],
        "realised_gate_harm": extras["realised_gate_harm"],
    })
    cls.note = (
        "cost-weighted can't-pay/won't-pay 2x2 misclassification (W2_7 hidden "
        "ability x willingness -> identical observable is_in_arrears -> C9 "
        "classification from engagement/part-payment/disclosure/consumption); "
        "ability axis = the can-pay/cannot-pay confound, 8:1 harm on reading a "
        "genuine can't-pay as a strategic won't-pay. fn_ability is the harm path "
        "(vulnerable read as able); pursue/forbear gate outcomes in components."
    )
    return cls, extras


def _git_head() -> "str | None":
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--customers", type=int, default=60000,
                    help="households to draw (only arrears accounts are scored)")
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gap into coupled_gap_ledger.json")
    args = ap.parse_args()

    cls, extras = measure(args.customers)

    print("W2_7 <-> C9 coupled can't-pay/won't-pay scenario")
    print(f"  households drawn          : {extras['n_customers']}")
    print(f"  arrears accounts (scored) : {extras['n_arrears']}")
    print(f"  truth cannot-pay          : {extras['n_truth_cannot']}"
          f"   strategic won't-pay: {extras['n_truth_strategic']}")
    print(f"  fn_ability (can't-pay read as can-pay): {cls.components['fn_ability']}")
    print(f"  fn_willingness (won't read as will)   : {cls.components['fn_willingness']}")
    print(f"  gate: pursued {extras['pursued']}  forborne {extras['forborne']}")
    print(f"    expensive error (pursued a can't-pay): "
          f"{extras['pursued_cannot_expensive_error']}")
    print(f"    loss (forbore a strategic won't-pay) : "
          f"{extras['forborne_strategic_loss']}")
    print(f"    realised gate harm (R=8:1 weighted)  : {extras['realised_gate_harm']}")
    print(f"  raw_gap (cost-weighted)   : {cls.raw_gap:.4f}")
    print(f"  g0 (no-skill baseline)    : {cls.g0:.4f}")
    print(f"  classification GAP        : {cls.gap}")
    print(f"    baseline                : {cls.baseline}")

    if args.write_ledger:
        measured_at = datetime.now(timezone.utc).isoformat()
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, cls,
            measured_at=measured_at, run_git_commit=_git_head(),
        )
        print(f"  ledger written: {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
