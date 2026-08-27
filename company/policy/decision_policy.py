"""Swappable decision-policy struct for simulation/run_phase2b.py::main().

FROZEN_POLICY_BASELINE_DESIGN.md option B: the retention and hedging decisions
that would need to vary between "last-generation" and "current" company policy
were, until this module existed, inlined as module-level constants and
if/else branches directly in run_phase2b.py. This dataclass makes that
decision surface explicit and swappable without changing any existing
caller's behaviour (CURRENT_POLICY reproduces today's constants exactly).

CURRENT_POLICY is the live policy: tiered retention discount (Phase 14a),
acquisition-cost-aware retention guard (Phase 15b), VaR-constrained hedge
decision on top of the backward-looking evolution (Phase 43b).

NAIVE_POLICY reconstructs the superseded "last-generation" policy at the
specific historical point each mechanic was introduced:
- Retention discount: flat 5%, no tiers (pre-Phase 14a).
- Retention guard: margin-only, no acquisition-cost-saved term (pre-Phase 15b,
  i.e. the Phase 12d state).
- Hedging: `company_evolve_hedge_fraction` alone; the VaR-forward
  `decide_hedge_fraction` layer (Phase 43b) never overrides it (pre-Phase 43b,
  i.e. the Phase 22b state).

Deferral pricing is deliberately NOT a policy field: `retention_deferral_economics.py`
(Phase QM) is observational only and does not feed back into the retention
guard on the live path, so "pre-deferral-pricing" is not a real fork in the
current code (see FROZEN_POLICY_BASELINE_DESIGN.md's honest-gap note).
"""

import hashlib
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class DecisionPolicy:
    name: str

    # Retention discount sizing.
    retention_discount_mode: str  # "tiered" or "flat"
    retention_tiers: tuple  # ((churn_estimate_threshold, discount_pct), ...), used when mode == "tiered"
    flat_discount_pct: float  # used when mode == "flat"

    # Retention economic guard: offer made only if the value protected exceeds
    # the cost of the offer. When False, acq_cost_saved is excluded (Phase 12d
    # margin-only state); when True, it is included (Phase 15b).
    include_acq_cost_saved_in_guard: bool

    # Hedging: when True, decide_hedge_fraction() (Phase 43b, VaR-forward) may
    # override the term's hedge fraction on top of the always-running
    # backward-looking evolve_hedge_fraction (Phase 22b). When False, the
    # evolved fraction is used as-is -- the pre-43b state.
    use_var_hedge_decision: bool

    # Nudge Physics Layer 1 (NUDGE_PHYSICS.md): offer comms framing.
    # "ab_test" runs a stable per-offer cohort split (loss_framed /
    # gain_framed, hashed on customer_id + event_date) so the company can
    # discover which framing lifts retention for which segment via
    # company/analytics/nudge_discovery.py -- without ever seeing the
    # SIM-side loss-aversion susceptibility that actually drives the
    # response. A fixed value (e.g. "gain_framed") reproduces the single
    # framing every pre-Nudge-Physics phase implicitly used.
    framing_mode: str = "gain_framed"

    # NUDGE_PHYSICS.md remaining mechanism: debt-collection letter tone
    # (2026-07-10). Same "ab_test" cohort-split convention as framing_mode
    # above -- the company discovers which tone lifts on-time payment for
    # which segment via company/analytics/nudge_discovery.py, without ever
    # seeing simulation/nudge_physics.py's hidden tone-susceptibility.
    tone_mode: str = "firm_toned"

    # THE VALUE CYCLE'S ONE VARIABLE (2026-08-26, docs/design/THE_VALUE_CYCLE_REALISED_AB.md).
    # Which rule sets the renewal MARGIN: `"flat_rules"` is the £2.00/MWh every account pays
    # today, `"value_based"` is company/pricing/value_based_renewal.py choosing per customer from
    # the company's own beliefs. It is a POLICY FIELD rather than a new switch because the honest
    # comparison between the two is realised rather than expected -- the same book, the same
    # world, run once per arm -- and this dataclass is already the thing a run's decision
    # identity is swapped by (`tools/run_frozen_baseline.py` does exactly that for the naive
    # arm). Reusing it also inherits `run_phase2b.main`'s refusal of a run whose `policy` and
    # whose `policy_scope` disagree, which is precisely the chimera an A/B on pricing would
    # otherwise be exposed to: one variable changed in one place, or the delta means nothing.
    #
    # The default is the CONTROL, so every existing caller is untouched and a run that does not
    # ask for the experiment is byte-identical to today's.
    renewal_margin_arm: str = "flat_rules"

    # THE PRICE LADDER'S RUNG (2026-08-27, docs/design/THE_VALUE_CYCLE_REALISED_AB.md, the
    # 2026-08-27 section's item 2: "measure the slope, not the level").
    #
    # How far along its OWN chosen uplift the value arm actually goes, as a multiple. The delivered
    # margin is `flat_rule + k x (chosen - flat_rule)`, so `k=1.0` is the arm as it stands and
    # `k=0.0` is the flat rule EXACTLY -- which is what makes rung zero a NULL CONTROL rather than
    # a nearby one, and `run_price_ladder` asserts rung zero reproduces the flat-rules arm's churn
    # roster and net margin before reading any slope off the rest of the ladder.
    #
    # WHY A COMMERCIAL DIAL AND NOT A HARNESS ONE. A supplier that computes an optimal renewal
    # price and then offers a fixed fraction of the increase is an ordinary commercial posture, so
    # this is a company decision a real supplier makes and the field belongs on the company's own
    # policy. Nothing about the world or the world's switching curve is read to set it. It is
    # resolved from `active_policy()` at the same site as `renewal_margin_arm` for the same reason
    # -- the rate chain is a wall door and must not gain a policy argument.
    #
    # THE DEFAULT IS 1.0, so every existing run -- including both arms of the standing realised
    # A/B -- is byte-identical to today's.
    renewal_margin_ladder_multiplier: float = 1.0

    # THE FLAT-AT-LEVEL ARM'S LEVEL (2026-08-27, director-directed).
    #
    # The uplift, in GBP/MWh, that `renewal_margin_arm="flat_at_level"` applies to EVERY renewal
    # it prices -- the same renewals the value arm prices, through the same guards and under the
    # same lawful ceiling.
    #
    # WHY THE ARM EXISTS. The value arm beat flat rules by GBP 7,066 with `discrimination_auc`
    # 0.4653 -- below a coin flip -- so the advantage cannot be attributed to inference. What it
    # demonstrably did was price HIGH: a median 44.50 GBP/MWh against the flat rule's 2.00. This
    # arm holds the LEVEL and removes the SELECTION, which is the only way to tell "chose well"
    # from "charged more".
    #
    # NOT THE LADDER. `renewal_margin_ladder_multiplier` delivers `flat + k x (chosen - flat)`, a
    # fraction of the arm's OWN per-customer answer, so it varies the SLOPE and never removes the
    # choosing. At k=0 it is the flat rule at 2.00, not at the arm's level. The two dials answer
    # different questions and neither substitutes for the other.
    #
    # A COMMERCIAL POSTURE, not only a measurement construct: a supplier that puts the same
    # increase on every renewing customer is doing an ordinary thing, and it is what most
    # suppliers actually did in 2022. That is why it belongs on the company's policy beside the
    # ladder rather than in the harness.
    #
    # `None` is the default and means the arm is not selected; selecting the arm without a level
    # is refused rather than defaulted, because a flat arm whose level was silently 0.0 would
    # reproduce the flat rule and be reported as a level comparison.
    renewal_margin_flat_level_gbp_per_mwh: float | None = None

    def retention_discount_for_risk(self, company_est: float) -> float:
        """Return the retention discount fraction for a given churn estimate."""
        if self.retention_discount_mode == "flat":
            return self.flat_discount_pct
        for threshold, discount in self.retention_tiers:
            if company_est >= threshold:
                return discount
        return 0.0


# Mirrors RETENTION_TIERS in simulation/run_phase2b.py exactly -- kept as a
# separate literal (not imported) so this module has no import-time
# dependency on the sim entry point.
CURRENT_POLICY = DecisionPolicy(
    name="current",
    retention_discount_mode="tiered",
    retention_tiers=(
        (0.75, 0.08),  # high risk (>=75%): 8% discount
        (0.50, 0.05),  # medium risk (50-75%): 5% discount
        (0.30, 0.03),  # low-risk-above-threshold (30-50%): 3% discount
    ),
    flat_discount_pct=0.05,  # unused in tiered mode; matches naive's flat rate for reference
    include_acq_cost_saved_in_guard=True,
    use_var_hedge_decision=True,
    framing_mode="ab_test",
    tone_mode="ab_test",
)

# Pre-Phase-14a/15b/43b state: naive flat-discount retention with a
# margin-only guard, and hedging left to the backward-looking evolution alone.
NAIVE_POLICY = DecisionPolicy(
    name="naive",
    retention_discount_mode="flat",
    retention_tiers=(),
    flat_discount_pct=0.05,
    include_acq_cost_saved_in_guard=False,
    use_var_hedge_decision=False,
    framing_mode="gain_framed",
)

# THE VALUE ARM, and NOTHING ELSE (2026-08-26). Built from CURRENT_POLICY by
# `dataclasses.replace` rather than typed out, because the whole worth of the
# comparison it is for is that exactly ONE field differs: a second hand-written
# literal would drift from `current` the first time a retention tier moved, and
# the realised delta would then carry an uncontrolled variable — the defect
# `WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10` recorded and the
# active-policy block below exists to close.
# `test_the_value_arm_policy_differs_from_current_in_exactly_one_field` pins it.
VALUE_ARM_POLICY = replace(
    CURRENT_POLICY, name="value_arm", renewal_margin_arm="value_based")


# ---- THE RUN'S POLICY, for consumers that are not handed one ----------------
#
# WHY THIS EXISTS (2026-08-12, WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10)
#
# Most consumers of a policy field receive the policy as an argument, so a
# counterfactual replay under NAIVE_POLICY gets the naive answer for free:
# `run_phase2b.main(policy=...)` reads `policy.retention_discount_for_risk`,
# `policy.include_acq_cost_saved_in_guard`, `policy.use_var_hedge_decision` and
# calls `framing_type_for(policy, ...)`.
#
# `tone_mode` was the exception, and it was a real defect rather than a rounding
# error. The dunning tone is resolved per bill from deep inside the settlement
# path (`simulation/arrears_engine.py::_tone_for_bill` ->
# `company/interfaces/collections_communication.py::collections_tone_for`), which
# has no policy argument and — by the B5 wall cut — must never be given one: the
# world may learn the TONE of the letter that arrived, never the policy object
# that chose it. So the seam pinned `CURRENT_POLICY`, and the frozen baseline's
# NAIVE arm ran naive retention, naive guard and naive hedging with the CURRENT
# A/B-split collections tone. It was not the naive company, and the resulting
# delta attributed one uncontrolled variable to the policy changes.
#
# Threading the policy down to that call site was the other option and was
# rejected: it would push a company decision object through four SIM consumers
# (`compute_emergent_bad_debt`, `compute_debt_recovery`, `dd_collection_book`,
# `tools/generate_billing_ledger`) — exactly the plumbing the wall pass removed.
#
# A run-scoped ACTIVE POLICY, read only on the company side of the seam, gets the
# identity right without moving a single byte across the wall: the SIM still asks
# for a string and cannot see, set or name the policy. `policy_scope` is a
# context manager rather than a bare setter so an arm cannot leak into whatever
# runs next, which is the failure mode a module-level global would have.
_ACTIVE_POLICY: ContextVar[DecisionPolicy] = ContextVar(
    "active_decision_policy", default=CURRENT_POLICY
)


def active_policy() -> DecisionPolicy:
    """The policy the CURRENT RUN is executing under.

    Defaults to CURRENT_POLICY, so every caller that never enters a
    `policy_scope` sees exactly today's behaviour. Consumers that cannot be
    handed a policy (the collections-communication seam) resolve their field
    here; consumers that ARE handed one keep using their argument, because an
    explicit argument is the stronger contract.
    """
    return _ACTIVE_POLICY.get()


@contextmanager
def policy_scope(policy: DecisionPolicy):
    """Run a block as though `policy` were the company's live policy.

    The counterfactual replay in `tools/run_frozen_baseline.py` wraps each arm
    in this, so the naive arm's collections tone is the naive tone. Resets on
    exit — including on exception — so a failed arm cannot contaminate the next
    one, or the test that runs after it.
    """
    token = _ACTIVE_POLICY.set(policy)
    try:
        yield policy
    finally:
        _ACTIVE_POLICY.reset(token)


def framing_type_for(policy: DecisionPolicy, customer_id: str, event_date: str) -> str:
    """Offer comms framing attribute for one retention offer.

    Company-observable by construction (the company chose it) -- this
    function never reads simulation/nudge_physics.py's hidden
    susceptibility. In ab_test mode the split is hashed on
    customer_id + event_date (not customer_id alone), so a single repeat
    customer can see both framings across their renewal history -- a real
    cohort-rotation practice, and what lets the Customer 360 timeline show
    one household two differently framed offers with different outcomes.
    """
    if policy.framing_mode != "ab_test":
        return policy.framing_mode
    seed = "framing_cohort_" + customer_id + "_" + event_date
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return "loss_framed" if int(digest, 16) % 2 == 0 else "gain_framed"


def tone_for(policy: DecisionPolicy, customer_id: str, period_end: str) -> str:
    """Debt-collection letter tone attribute for one bill's payment cycle
    (2026-07-10, NUDGE_PHYSICS.md remaining mechanism).

    Company-observable by construction (the company chose it) -- never
    reads simulation/nudge_physics.py's hidden tone-susceptibility. In
    ab_test mode the split is hashed on customer_id + period_end (same
    cohort-rotation convention as framing_type_for), so the company can
    discover which tone lifts on-time payment for which segment via
    company/analytics/nudge_discovery.py.
    """
    if policy.tone_mode != "ab_test":
        return policy.tone_mode
    seed = "tone_cohort_" + customer_id + "_" + period_end
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return "empathetic_toned" if int(digest, 16) % 2 == 0 else "firm_toned"
