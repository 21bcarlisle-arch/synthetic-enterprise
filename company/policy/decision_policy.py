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

from dataclasses import dataclass


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
)
