"""The company's own belief about how hard the market is competing for its book.

WHAT THIS REPLACES, AND WHY IT IS NOT A REFINEMENT OF IT.
`company/crm/market_conditions.market_conditions_multiplier(renewal_year)` is a ten-entry table
keyed on the calendar year. It was, until this module, the ONLY competitive-pressure signal
reaching any company churn estimate (`enriched_churn_estimate` lines 104/139,
`churn_model.estimate_passive_churn_probability`). A year lookup is structurally incapable of
responding to anything a rival does inside a year, and that was measured rather than argued:
`docs/staging/WORKER_FINDING_THE_LADDER_RESOLVES_THE_DEFENDING_MARKET_AND_THE_COMPANY_CANNOT_SEE_IT`
ran a chase-on/chase-off pair over one tree with identical book and seeds, found the world's own
churn probability moved at every rung (+0.7 to +4.5pp) and the company's `believed_p_leave`
bit-identical between the two worlds -- `max |ON - OFF| = 0.0`, not approximately zero.

`docs/design/COMPETITOR_FIELD_FRAME.md` §5 says a large persistent gap between belief and truth
is not itself a defect -- it is the expected signature of a real epistemic limit -- but that
"a defect is a gap that never moves in response to new observations". A constant cannot move in
response to anything. This module is the observation channel that makes the gap movable.

WHAT THE COMPANY IS ALLOWED TO SEE, and it is the whole design constraint. It cannot see the
rival's price, the rival's chase parameter, or the world's churn probability. It CAN see its own
book: how many renewals it priced, what it believed about each of them, and how many of those
customers subsequently left it for somebody else. That is the entire input here. A supplier
inferring competitive intensity from the gap between its own predicted and realised losses is
not a modelling convenience -- it is what a retention analytics function does, and it is the only
competitive signal that exists on the company side of the wall.

THE PRIOR IS KEPT AND UPDATED, NOT DISCARDED. The published DESNZ/Ofgem switching series is real
evidence and the company should not throw it away because it has seen thirty of its own renewals.
So the year table becomes the PRIOR and the company's realised experience is the LIKELIHOOD, and
they combine by precision weighting in log space:

    posterior = prior x ratio ** w,   w = V_prior / (V_prior + V_evidence)

Ratios compose multiplicatively, so the blend is geometric (log space), not arithmetic -- the
same argument `enriched_churn_estimate._apply_market_conditions` makes for working the multiplier
in survival space. With no observations V_evidence is infinite, w is 0, and the posterior IS the
prior: this module's no-evidence behaviour is byte-identical to the table it replaces, which is
what makes it a fail-soft rather than a fail-open.

NEITHER VARIANCE IS A NUMBER SOMEBODY PICKED, which is the point. V_prior is the dispersion the
published series itself shows across the ten years it covers -- if the true multiplier for this
book moved that much year to year in the national record, that is the scale on which this year's
value could differ from the published estimate. V_evidence is the delta-method variance of the
log of a binomial proportion at the realised sample size. Both are computed here from data
already in the repository. THE WEIGHTING IS ALSO THE BOUND: no clamp is applied to `ratio`,
because a wild ratio only arises at small n, and small n drives V_evidence up and w down by the
same mechanism. A ratio of 20 observed on one decision moves the multiplier by 20**0.36.

NO LOOK-AHEAD. Evidence is drawn only from renewal years STRICTLY EARLIER than the one being
priced. A company pricing a 2019 renewal in 2019 has not yet seen how 2019 closed. This costs
real resolution -- the first year of any run gets the prior and nothing else -- and it is not
negotiable: an estimate informed by its own outcome is not an estimate.
"""
from __future__ import annotations

import math
import statistics
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional

from company.crm.market_conditions import (
    MARKET_SWITCHING_MULTIPLIER_BY_YEAR,
    market_conditions_multiplier,
)

#: Dispersion of the published multiplier series in log space, computed from the series itself
#: rather than asserted. This is the scale on which the company allows the truth for its OWN book
#: to differ from the national published figure for the year.
PRIOR_LOG_VARIANCE: float = statistics.pvariance(
    [math.log(m) for m in MARKET_SWITCHING_MULTIPLIER_BY_YEAR.values()]
)

#: Jeffreys/Anscombe continuity correction on the realised loss count. Without it a window in
#: which nobody left gives `log(0)` and a window in which everybody left gives zero variance --
#: both of which are FAIL-OPEN shapes (one refuses a real observation, the other believes an
#: unbelievable one with total confidence). 0.5/1.0 is the standard correction, not a tuning dial.
_CONTINUITY_SUCCESSES: float = 0.5
_CONTINUITY_TRIALS: float = 1.0


@dataclass(frozen=True)
class PressureReading:
    """What the company believes about competitive pressure, and everything behind it.

    Carried whole rather than returned as a bare float because a belief whose provenance is not
    inspectable cannot be graded, and grading belief against truth is the coupled triad's
    entire subject. `basis` names WHY the reading is what it is, including every refusal.
    """

    renewal_year: Optional[int]
    prior: float
    multiplier: float
    basis: str
    decisions: int = 0
    observed_losses: int = 0
    expected_losses: float = 0.0
    ratio: Optional[float] = None
    weight: float = 0.0

    @property
    def moved_from_prior(self) -> bool:
        """Whether the company's own experience changed what it believes.

        False is a legitimate and frequent answer -- no closed years yet, or a book whose
        realised losses landed exactly where it predicted -- and it is reported rather than
        inferred, because "the belief did not move" and "the belief cannot move" are the two
        facts this whole module exists to tell apart.
        """
        return self.ratio is not None and self.weight > 0.0


@dataclass
class CompetitivePressureLedger:
    """The company's closed renewal experience, by year.

    EXPLICIT STATE WITH A RUN SCOPE, never a bare module global -- the same rule
    `simulation.competitor_reference.CompanyPositionLedger` states for the world's side of this:
    a global would leak between runs and between tests and make a belief depend on the order
    tests happened to execute in.

    TWO COUNTERS PER YEAR AND NO PER-DECISION MATCHING. The ratio the company needs is
    realised losses over predicted losses across a population, and that is two aggregates. Asking
    for a per-account join would need an account key on both sides of a seam that does not carry
    one, and would buy nothing: the sum of the believed probabilities IS the predicted loss count.
    """

    decisions_by_year: dict[int, int] = field(default_factory=dict)
    expected_by_year: dict[int, float] = field(default_factory=dict)
    losses_by_year: dict[int, int] = field(default_factory=dict)
    #: Whether anything in this run has undertaken to REPORT departures to this ledger. See
    #: `arm_loss_reporting`. Until it has, the numerator is not zero -- it is absent.
    loss_reporting_armed: bool = False

    def arm_loss_reporting(self) -> None:
        """Declare that departures WILL be reported to this ledger for the rest of the run.

        THE DIFFERENCE BETWEEN "NOBODY LEFT" AND "NOBODY TOLD US", and this ledger got it wrong
        on its first live measurement (2026-08-28). `run_phase4c_on_phase2b.main` calls
        `run_phase2b()` without a `sim_interface`, so every `notify_churn` in the run loop is
        behind `if sim_interface is not None` and none of them fired. The ledger therefore
        accumulated a full denominator and an empty numerator, read `observed = 0` as evidence
        that the market had gone quiet, and COLLAPSED the company's churn belief across a run in
        which a sixth of the book actually left.

        That is the FAIL-OPEN shape in its purest form: the absence of an observation channel
        read as an observation of absence. It is also the flattering direction, which is how it
        nearly survived -- the belief moved a long way, the published over-prediction gap
        narrowed from 20.7-28.7pp to 1.1-14.9pp, and every one of those numbers was an artefact
        of a dead wire.

        So the numerator must be ARMED by the site that books into it, and an unarmed ledger
        refuses to update at all -- returning the published prior, which is exactly the behaviour
        that shipped before this module existed. Fail-soft, and it names its reason.
        """
        self.loss_reporting_armed = True

    def observe_renewal_decision(self, renewal_year: Optional[int], believed_p_leave: float) -> None:
        """Record that the company priced one renewal and what it believed about it.

        Called once per renewal from `churn_desk.estimate_renewal_churn` -- the company's single
        once-per-renewal belief site. NOT from `enriched_churn_estimate`, which the value arm's
        margin search calls dozens of times for one renewal while scoring candidate prices; a
        counter there would count the search, not the book.
        """
        if renewal_year is None:
            return
        year = int(renewal_year)
        p = float(believed_p_leave)
        if not math.isfinite(p):
            return
        self.decisions_by_year[year] = self.decisions_by_year.get(year, 0) + 1
        self.expected_by_year[year] = self.expected_by_year.get(year, 0.0) + max(0.0, min(1.0, p))

    def observe_competitive_loss(self, renewal_year: Optional[int]) -> None:
        """Record that one account left this supplier at a renewal, for a competitor.

        Only non-renewal departures reach here. A death or a house move is a loss of a customer
        and is NOT evidence about a rival, and counting it as one would make bereavement read as
        market pressure -- the caller (`SimInterface.notify_churn`) filters on its own `reason`.
        """
        if renewal_year is None:
            return
        year = int(renewal_year)
        self.losses_by_year[year] = self.losses_by_year.get(year, 0) + 1

    def _closed_window(self, renewal_year: int) -> tuple[int, float, int]:
        """Decisions, predicted losses and realised losses over years strictly before this one."""
        years = [y for y in self.decisions_by_year if y < renewal_year]
        n = sum(self.decisions_by_year[y] for y in years)
        expected = sum(self.expected_by_year.get(y, 0.0) for y in years)
        observed = sum(self.losses_by_year.get(y, 0) for y in years)
        return n, expected, observed

    def reading(self, renewal_year: Optional[int]) -> PressureReading:
        """The company's competitive-pressure multiplier for a renewal in `renewal_year`.

        Every branch that declines to update names its reason in `basis`. A refusal that says why
        is how the refusal itself gets found to be wrong.
        """
        prior = market_conditions_multiplier(renewal_year)
        if renewal_year is None:
            return PressureReading(None, prior, prior, "no renewal year: prior only")

        if not self.loss_reporting_armed:
            # An empty numerator that nobody undertook to fill is not a quiet market.
            return PressureReading(
                int(renewal_year), prior, prior,
                "departures are not being reported to this ledger: prior only")

        year = int(renewal_year)
        n, expected, observed = self._closed_window(year)
        if n <= 0:
            return PressureReading(
                year, prior, prior, "no closed renewal years yet: prior only")
        p_expected = expected / n
        if p_expected <= 0.0:
            # The company predicted that nobody would leave. There is no ratio to take against
            # zero, and inventing one would make any single departure infinite evidence.
            return PressureReading(
                year, prior, prior,
                f"predicted zero losses on {n} closed decisions: no ratio available",
                decisions=n, observed_losses=observed, expected_losses=expected)

        p_observed = (observed + _CONTINUITY_SUCCESSES) / (n + _CONTINUITY_TRIALS)
        ratio = p_observed / p_expected
        # THE VARIANCE IS EVALUATED UNDER THE NULL (at the PREDICTED rate), not at the realised
        # one, and this was found by printing the table rather than by thinking about it. The
        # Wald form -- `(1 - p_observed) / (n * p_observed)` -- makes the WEIGHT co-vary with the
        # ANSWER, and the result is NOT MONOTONE in the thing being observed: on 200 decisions
        # predicting 0.30, observing 30 losses gave a multiplier of 0.542 while observing ZERO
        # gave 0.594. A belief that reads more competitive pressure from fewer departures is not
        # a conservative belief, it is a broken one. Under the null the weight is a property of
        # the sample size and the prediction alone, so the posterior is strictly increasing in
        # realised losses -- which is the whole claim this channel makes. (This is the score-test
        # convention rather than the Wald one, and the reason is the textbook reason: the Wald
        # variance degenerates as the proportion approaches its bounds.)
        v_evidence = (1.0 - p_expected) / (n * p_expected)
        weight = PRIOR_LOG_VARIANCE / (PRIOR_LOG_VARIANCE + v_evidence)
        multiplier = prior * (ratio ** weight)
        return PressureReading(
            year, prior, multiplier,
            f"{observed} realised losses against {expected:.2f} predicted "
            f"on {n} closed decisions",
            decisions=n, observed_losses=observed, expected_losses=expected,
            ratio=ratio, weight=weight)


_ACTIVE_LEDGER: ContextVar[Optional[CompetitivePressureLedger]] = ContextVar(
    "active_competitive_pressure_ledger", default=None
)


def active_pressure_ledger() -> Optional[CompetitivePressureLedger]:
    """The ledger the CURRENT RUN is accumulating into, or None outside any run.

    None is the honest answer and it is load-bearing: a caller with no run scope has observed
    nothing, so it gets the published prior and exactly today's behaviour. Defaulting to a shared
    module-level ledger instead would let one test's book inform another test's belief.
    """
    return _ACTIVE_LEDGER.get()


@contextmanager
def pressure_ledger_scope(ledger: Optional[CompetitivePressureLedger] = None):
    """Run a block with a fresh (or supplied) competitive-pressure ledger active.

    Resets on exit including on exception, so a failed arm cannot contaminate the arm it is being
    compared against -- which on an A/B whose whole subject is a between-arm difference would not
    be a leak but a fabricated result.
    """
    ledger = ledger if ledger is not None else CompetitivePressureLedger()
    token = _ACTIVE_LEDGER.set(ledger)
    try:
        yield ledger
    finally:
        _ACTIVE_LEDGER.reset(token)


def derived_market_pressure_multiplier(renewal_year: Optional[int]) -> float:
    """The company's competitive-pressure multiplier -- the drop-in for the year table.

    This is what every churn estimate now scales by. Outside a run scope it returns the published
    year value unchanged, so nothing that does not opt in can observe a difference.
    """
    ledger = active_pressure_ledger()
    if ledger is None:
        return market_conditions_multiplier(renewal_year)
    return ledger.reading(renewal_year).multiplier
