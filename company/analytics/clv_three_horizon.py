"""EP1 — what a customer is worth, on three horizons, from what the company can see.

WHAT THIS ANSWERS, AND WHAT IT DELIBERATELY DOES NOT. Three VALUATION BASES for the
same customer, measured forward:

  H1 ``contract_term``    — what the contract already sold is worth before it ends.
  H2 ``tenure_expected``  — what this customer is worth if they go on behaving the way
                            their MOST RECENT renewal suggests.
  H3 ``portfolio_cohort`` — what a customer like this is worth, when their own history
                            is too short to trust.

It is not `company/core/commitment_actual_forecast.py`, which answers a VARIANCE question
about one contract at three points in TIME (committed / actually earned / re-forecast).
That module carried this atom's name for eight passes and was renamed in the first commit
of this draw; the distinction is stated in both files so a reader never has to infer it.

EVERY NUMBER HERE IS A BELIEF. The inputs are the supplier's own observables — its
cost-to-serve arithmetic, its own churn estimate off its own bill-shock history, its own
customer roster. Nothing reads simulation internals, nothing asks the world who actually
churned. The estimate is allowed to be wrong; the GAP between it and realised value is
the score (COUPLED_TRIAD_DESIGN). R12 applies hard: CLV is a DIAGNOSTIC and never a
target — no tariff, retention offer or acquisition budget may be tuned to raise it.

=============================================================================
THE THREE CONSTRAINTS THIS MODULE IS BUILT TO, EACH BOUGHT BY AN EARLIER DEFECT
=============================================================================

1. A HORIZON DECLARES ITS TIME MODEL (pass 8). "Tenure-expected" is a family, not a
   horizon. The shipped estimator (`saas/clv_model.fit_theta_posterior_per_account`)
   updates a Beta prior with SOFT COUNTS, whose sufficient statistic is a SUM — so a
   customer whose bill shocks are all recent and one whose shocks are all ancient are
   bit-for-bit the same customer to it. That is a defensible assumption (a fixed
   per-account propensity) that nothing had ever stated. Here every horizon carries a
   `TimeModel` in the record it writes, and two of the three are order-AWARE BY
   CONSTRUCTION while the third is order-blind BY DESIGN and says why.

2. AN OUTPUT CARRIES ITS POPULATION, NOT ONLY ITS NUMBER (pass 6). Every aggregate this
   module publishes is a `HorizonValue`/`CohortValue` carrying a `Population`: how many
   were counted, how many excluded, and under which named reason. A bare float cannot
   leave this module.

3. A STRUCTURAL BLANK IS NOT THE NUMBER ZERO (pass 7, and `84ae6bbeb` one module away).
   "This customer has no margin we can observe" and "this customer is worth nothing" are
   different facts. `value_gbp` is `float | None`; `None` is excluded from aggregates
   with a reason rather than entering them as `0.0`. A cohort that does not exist returns
   `None`, not an all-zeros summary that a loss-making cohort is indistinguishable from.
   And `still_supplied` is a REQUIRED keyword with NO DEFAULT — the `66141b70c` shape,
   this repo's own proven answer to valuing accounts that had already left.

=============================================================================
THIS MODULE IS A RECONCILIATION, NOT A CONSTRUCTION
=============================================================================

Pass 8 found five shipped decision modules that had each brought their own CLV, on two
discount rates and three arithmetic shapes, none labelled with which horizon it was. An
AST census run for THIS pass over `company/` and `saas/` finds the seam is three times
that size: 18 modules bind a CLV-named symbol, not six. Adding a nineteenth beside them
is the accretion `OPERATIONAL_LAYER_DESIGN` forbids.

So the reconciliation is MECHANISED rather than exhorted. `CLV_SEAM_REGISTER` below names
every one of the 18 with a disposition and a reason, and `unregistered_clv_modules()`
re-runs the census against it. A nineteenth CLV cannot appear in this repository without
that test going red and forcing its author to say which horizon it is. That is the
difference between this pass and the three before it, each of which re-copied a
recommendation forward instead of leaving a mechanism.

Dispositions are recorded here and EXECUTED AT EACH MODULE'S NEXT TOUCH
(remediation-on-touch): all 18 are outside this atom's `file_scope`, and rewriting them
speculatively is the thing the standing design-lens rules forbid.
"""

from __future__ import annotations

import ast
import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable, Mapping, Sequence

__all__ = [
    "DISCOUNT_RATE",
    "Horizon",
    "TimeModel",
    "Exclusion",
    "Population",
    "HorizonValue",
    "RenewalPoint",
    "AccountObservables",
    "AccountCLV",
    "CohortValue",
    "BookCLV",
    "survival_discounted_value_gbp",
    "estimate_account",
    "estimate_book",
    "CLV_SEAM_REGISTER",
    "census_clv_modules",
    "unregistered_clv_modules",
]


# ONE discount rate for the whole seam. The census below found two live (0.10 in
# `channel_roi` and `saas/clv_model`, 0.08 in `switching_cba`) for one quantity. 0.10 is
# adopted because it is what the module that actually values the BOOK uses, so adopting
# it moves no published figure. It is a company parameter, not a world constant, and it
# is stated once here rather than five times in five callers.
DISCOUNT_RATE = 0.10

# A retention rate that exactly offsets the discount rate makes every period contribute
# the same present value; below this tolerance the closed form is replaced by its own
# algebraic limit rather than by a fallback branch.
_UNIT_RETENTION_EPSILON = 1e-12


class Horizon(str, Enum):
    """The three valuation bases. The value is the field name it publishes under."""

    CONTRACT_TERM = "contract_term"
    TENURE_EXPECTED = "tenure_expected"
    PORTFOLIO_COHORT = "portfolio_cohort"


class TimeModel(str, Enum):
    """How a horizon treats the customer's history in TIME — constraint 1.

    This is the field pass 8 said every horizon owes, and it exists so that the
    assumption is READABLE on the output rather than inferable from the arithmetic.
    """

    #: Hazard read from the account's most recent renewal and held constant over a term
    #: that is FIXED by the contract. Order-aware: reordering the history changes which
    #: renewal is most recent, and therefore the number.
    CONSTANT_HAZARD_FIXED_TERM = "constant_hazard_fixed_term"

    #: Hazard read from the account's most recent renewal; the term is the expected
    #: remaining tenure that hazard implies. Order-aware for the same reason.
    LATEST_RENEWAL_CONDITIONED = "latest_renewal_conditioned"

    #: Hazard and margin pooled over the account's cohort. Deliberately EXCHANGEABLE —
    #: reordering any member's history cannot move it, and that is the point: this
    #: horizon exists precisely for accounts whose own history is too short to condition
    #: on. Declared rather than discovered, which is the whole of constraint 1.
    POOLED_EXCHANGEABLE = "pooled_exchangeable"


class Exclusion(str, Enum):
    """Named reasons a subject is not counted. A `Population` carries these by count.

    An exclusion is never silent and never becomes a zero. Every reason here is a
    STRUCTURAL BLANK — a fact the company does not have — except `CEASED`, which is a
    fact it does have and which disqualifies the subject from a FORWARD valuation.
    """

    NO_MARGIN_OBSERVED = "no_margin_observed"
    NO_RENEWAL_OBSERVED = "no_renewal_observed"
    CEASED = "ceased"
    NO_COHORT_PEERS = "no_cohort_peers"


@dataclass(frozen=True)
class Population:
    """Who a published number is about — constraint 2.

    `counted` and `excluded` are independent counts, not a total and a remainder, so a
    reader can see the denominator that was used AND the one that was available.
    """

    counted: int
    excluded: int
    reasons: Mapping[str, int] = field(default_factory=dict)

    @property
    def available(self) -> int:
        return self.counted + self.excluded

    @property
    def is_empty(self) -> bool:
        """No subject was counted. Distinct from 'the counted subjects are worth zero'."""
        return self.counted == 0

    def describe(self) -> str:
        if not self.reasons:
            return str(self.counted) + " of " + str(self.available)
        why = ", ".join(
            k + "=" + str(v) for k, v in sorted(self.reasons.items())
        )
        return str(self.counted) + " of " + str(self.available) + " (" + why + ")"

    def as_published_dict(self) -> dict:
        """The population as JSON, with `available` MATERIALISED rather than derived.

        A reader of the published artefact has no properties, only keys. Leaving
        `available` to be re-added downstream is how a denominator gets recomputed
        differently in two places — so it is written once, here, by the object that
        owns the arithmetic.
        """
        return {
            "counted": self.counted,
            "excluded": self.excluded,
            "available": self.available,
            "reasons": dict(sorted(self.reasons.items())),
        }


@dataclass(frozen=True)
class HorizonValue:
    """One horizon's answer for one account, with its time model and its population.

    `value_gbp is None` means THE COMPANY CANNOT VALUE THIS ACCOUNT ON THIS HORIZON, and
    `population.reasons` says why. It never means zero. A caller that needs a float must
    decide what to do with the blank at a named place — which is exactly the decision
    `company/crm/clv_cohort_book.py` has no slot to record.
    """

    horizon: Horizon
    time_model: TimeModel
    value_gbp: float | None
    population: Population

    @property
    def is_estimable(self) -> bool:
        return self.value_gbp is not None

    def as_published_dict(self) -> dict:
        """This horizon's answer as JSON — the blank survives as `null`, never as 0.0.

        `horizon` and `time_model` are emitted as their `.value` strings explicitly.
        Both are `str` subclasses, so `json.dumps` would already produce the right
        characters; spelling `.value` means a later change to the enum's base class
        cannot silently change the shape of a published artefact.
        """
        return {
            "horizon": self.horizon.value,
            "time_model": self.time_model.value,
            "value_gbp": self.value_gbp,
            "population": self.population.as_published_dict(),
        }


@dataclass(frozen=True)
class RenewalPoint:
    """One annual renewal point as the company's own churn model produced it.

    Field-for-field the shape `saas.churn_model.build_churn_risk` already returns, so the
    company's existing belief feeds this without translation.
    """

    renewal_period: str
    churn_probability: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.churn_probability <= 1.0:
            raise ValueError(
                "churn_probability must be a probability, got "
                + repr(self.churn_probability)
            )


@dataclass(frozen=True)
class AccountObservables:
    """Everything the company can see about one account, and nothing it cannot.

    `still_supplied` is a REQUIRED keyword with NO DEFAULT, and `annual_margin_gbp` must
    be given explicitly as a float or explicitly as `None`. Both are constraint 3: this
    repo has already published a wrong figure once because valuing accounts that had
    left was the easy default, and once because a structural blank entered an aggregate
    as the number zero. Neither is reachable by forgetting an argument here.
    """

    account_id: str
    segment: str
    channel: str
    acquisition_year: int
    contract_term_years: float
    renewal_history: tuple[RenewalPoint, ...]
    annual_margin_gbp: float | None
    still_supplied: bool

    def __post_init__(self) -> None:
        # `still_supplied` is checked for its TYPE, not its truthiness: the failure this
        # guards is a caller passing a string, a `None`, or a count — each of which is
        # truthy or falsy by accident rather than by meaning.
        if not isinstance(self.still_supplied, bool):
            raise TypeError(
                "still_supplied must be an explicit bool for account "
                + str(self.account_id)
                + "; got "
                + type(self.still_supplied).__name__
                + ". Whether the company still supplies a customer is not a field that "
                "may be inferred from a default."
            )
        if self.annual_margin_gbp is not None and not isinstance(
            self.annual_margin_gbp, (int, float)
        ):
            raise TypeError(
                "annual_margin_gbp must be a number or an explicit None for account "
                + str(self.account_id)
                + "; got "
                + type(self.annual_margin_gbp).__name__
                + ". None means 'not observable' and is excluded from aggregates with a "
                "reason; it is not the number zero."
            )
        if self.contract_term_years < 0:
            raise ValueError(
                "contract_term_years cannot be negative for account "
                + str(self.account_id)
            )

    @property
    def latest_renewal(self) -> RenewalPoint | None:
        """The most recent renewal point, or None if the account has never renewed.

        Taken by POSITION, not by sorting on `renewal_period` — `build_churn_risk`
        returns its list chronologically and re-sorting here would silently repair a
        caller that handed over a scrambled history, which is the order-blindness this
        module exists to make visible.
        """
        return self.renewal_history[-1] if self.renewal_history else None


@dataclass(frozen=True)
class AccountCLV:
    """The three horizons for one account. Any of them may be unestimable."""

    account_id: str
    contract_term: HorizonValue
    tenure_expected: HorizonValue
    portfolio_cohort: HorizonValue

    def horizon(self, which: Horizon) -> HorizonValue:
        return {
            Horizon.CONTRACT_TERM: self.contract_term,
            Horizon.TENURE_EXPECTED: self.tenure_expected,
            Horizon.PORTFOLIO_COHORT: self.portfolio_cohort,
        }[which]


@dataclass(frozen=True)
class CohortValue:
    """A cohort's pooled view, carrying its population.

    `is_profitable` returns `None` for an empty cohort. That is the §5 repair: a cohort
    that DOES NOT EXIST and a cohort that LOSES MONEY must not publish the same boolean,
    and the sibling implementation one module away still does.
    """

    key: str
    time_model: TimeModel
    mean_value_gbp: float | None
    median_value_gbp: float | None
    total_value_gbp: float | None
    pooled_churn_probability: float | None
    population: Population

    @property
    def is_profitable(self) -> bool | None:
        if self.mean_value_gbp is None:
            return None
        return self.mean_value_gbp > 0

    def as_published_dict(self) -> dict:
        """The cohort as JSON, carrying the three-state `is_profitable` intact.

        `null` here is "this cohort has no counted member", NOT "it breaks even" —
        the §5 repair travels into the artefact rather than stopping at the object,
        because a publisher that re-derives the boolean from `mean_value_gbp` is
        exactly the sibling implementation that got it wrong.
        """
        return {
            "key": self.key,
            "time_model": self.time_model.value,
            "mean_value_gbp": self.mean_value_gbp,
            "median_value_gbp": self.median_value_gbp,
            "total_value_gbp": self.total_value_gbp,
            "pooled_churn_probability": self.pooled_churn_probability,
            "is_profitable": self.is_profitable,
            "population": self.population.as_published_dict(),
        }


@dataclass(frozen=True)
class BookCLV:
    """The whole book on all three horizons, each with its own population.

    The populations DIFFER between horizons on purpose: an account with no renewal
    history is unestimable on H1/H2 and perfectly estimable on H3, which is the reason
    there are three horizons rather than one.
    """

    accounts: tuple[AccountCLV, ...]
    cohorts: Mapping[str, CohortValue]
    portfolio: CohortValue
    #: WHICH of the three horizons the cohort and portfolio aggregates were built
    #: from, and at WHAT discount rate. Both are REQUIRED with no default, for the
    #: reason `still_supplied` is: this atom is being published, and a valuation
    #: figure without its basis is R14's defect in a different currency. Every
    #: account carries all three horizons, so `portfolio.mean_value_gbp` is
    #: uninterpretable — not merely under-documented — unless the book says which
    #: one it aggregated. `estimate_book` is the only construction site and it
    #: knows both, so neither can be supplied by a guess downstream.
    aggregate_horizon: Horizon
    discount_rate: float

    def cohort(self, key: str) -> CohortValue | None:
        """The cohort, or None if no such cohort exists in this book.

        `None` here means 'no such cohort'; a `CohortValue` whose population is empty
        cannot arise, because a cohort is only built from the members it has.
        """
        return self.cohorts.get(key)

    def account(self, account_id: str) -> AccountCLV | None:
        for a in self.accounts:
            if a.account_id == account_id:
                return a
        return None

    def as_published_dict(self) -> dict:
        """The whole book as a JSON-safe statement, basis first.

        THIS IS THE ONLY WAY THIS ATOM LEAVES THE PROCESS, and that is deliberate.
        `three_horizon_clv` has been computed on every run since pass 10 and read by
        nothing, which is the difference between built and dark; the fix is not a
        second estimator in the publisher but a single serialisation owned by the
        object that holds the numbers. A publisher that re-derives anything here —
        an aggregate, a denominator, a profitability flag — has forked the
        implementation, and this module's own reconciliation register exists because
        that has already happened six times on this one quantity.

        WHAT IS DELIBERATELY NOT HERE: no rounding, no `£` formatting, no
        "0.0 if None". Presentation is the renderer's job and a blank stays a blank
        all the way to the page, where `NOT_AVAILABLE` is printed for it under a
        named reason. Rounding at the seam would make the artefact and the object
        disagree at the fourth decimal, which is how a reconciliation becomes
        unfalsifiable.
        """
        return {
            "aggregate_horizon": self.aggregate_horizon.value,
            "discount_rate": self.discount_rate,
            "portfolio": self.portfolio.as_published_dict(),
            "cohorts": {
                key: cohort.as_published_dict()
                for key, cohort in sorted(self.cohorts.items())
            },
            "accounts": [
                {
                    "account_id": account.account_id,
                    Horizon.CONTRACT_TERM.value:
                        account.contract_term.as_published_dict(),
                    Horizon.TENURE_EXPECTED.value:
                        account.tenure_expected.as_published_dict(),
                    Horizon.PORTFOLIO_COHORT.value:
                        account.portfolio_cohort.as_published_dict(),
                }
                for account in sorted(self.accounts, key=lambda a: a.account_id)
            ],
        }


def survival_discounted_value_gbp(
    annual_margin_gbp: float,
    churn_rate: float,
    discount_rate: float,
    term_years: float,
) -> float:
    """Present value of an annual margin earned over a FINITE term, under a constant hazard.

        sum_{t=1..T} margin * retention^t / (1+d)^t
          = margin * retention * (1 - r^T) / (1 + d - retention),   r = retention / (1+d)

    THE SAME CLOSED FORM AS `company/core/commitment_actual_forecast._term_value_gbp`, and
    that duplication is deliberate and recorded rather than accidental. That symbol is
    private, lives in the module that answers the variance question, and is outside this
    atom's `file_scope`; importing a private name across a seam to save nine lines would
    couple the two questions this draw's first commit spent a whole pass separating. The
    register below names that module with an `ADOPT` disposition, so the duplication is
    visible to the census and has a stated end.

    The finite term matters: its `T -> infinity` limit is the perpetuity that overstated
    a one-year commitment by ~2.9x, which is what
    `WORKER_FINDING_THE_CONTRACT_TERM_HORIZON_PRICES_A_TERM_AS_A_PERPETUITY_2026-08-15`
    cost to find. Bounded above by `margin * term_years` wherever retention <= 1 + d.
    """
    if term_years <= 0:
        return 0.0
    retention = 1.0 - churn_rate
    if retention <= 0:
        # Certain churn: nothing survives to the first renewal.
        return 0.0
    factor = 1.0 + discount_rate
    if factor <= 0:
        # A rate at or below -100% is not a discount rate; price the term undiscounted
        # rather than producing a sign-flipped number nobody would question.
        factor = 1.0
    ratio = retention / factor
    denom = factor - retention
    if abs(denom) < _UNIT_RETENTION_EPSILON:
        # ratio == 1: every period contributes exactly `margin` in present value.
        return annual_margin_gbp * term_years
    return annual_margin_gbp * retention * (1.0 - ratio**term_years) / denom


def _blank(horizon: Horizon, time_model: TimeModel, reason: Exclusion) -> HorizonValue:
    """An unestimable horizon, carrying the named reason it is unestimable."""
    return HorizonValue(
        horizon=horizon,
        time_model=time_model,
        value_gbp=None,
        population=Population(counted=0, excluded=1, reasons={reason.value: 1}),
    )


def _counted(horizon: Horizon, time_model: TimeModel, value: float) -> HorizonValue:
    return HorizonValue(
        horizon=horizon,
        time_model=time_model,
        value_gbp=value,
        population=Population(counted=1, excluded=0, reasons={}),
    )


def estimate_account(
    obs: AccountObservables,
    *,
    cohort_margin_gbp: float | None = None,
    cohort_churn_probability: float | None = None,
    cohort_term_years: float | None = None,
    discount_rate: float = DISCOUNT_RATE,
) -> AccountCLV:
    """The three horizons for one account.

    The cohort arguments are the POOLED statistics this account's peers produced; when
    they are absent H3 is unestimable with reason `no_cohort_peers` rather than falling
    back to the account's own numbers — a cohort horizon that quietly becomes the tenure
    horizon for a lonely account is the same defect as a blank becoming a zero.
    """
    margin = obs.annual_margin_gbp
    latest = obs.latest_renewal

    # H1 — CONTRACT TERM. Constant hazard, term fixed by the contract.
    if margin is None:
        h1 = _blank(
            Horizon.CONTRACT_TERM,
            TimeModel.CONSTANT_HAZARD_FIXED_TERM,
            Exclusion.NO_MARGIN_OBSERVED,
        )
    elif latest is None:
        h1 = _blank(
            Horizon.CONTRACT_TERM,
            TimeModel.CONSTANT_HAZARD_FIXED_TERM,
            Exclusion.NO_RENEWAL_OBSERVED,
        )
    else:
        h1 = _counted(
            Horizon.CONTRACT_TERM,
            TimeModel.CONSTANT_HAZARD_FIXED_TERM,
            survival_discounted_value_gbp(
                margin, latest.churn_probability, discount_rate, obs.contract_term_years
            ),
        )

    # H2 — TENURE EXPECTED. Same hazard, but the term is the expected remaining tenure
    # that hazard implies (1/h renewals). Finite by construction: a hazard of zero would
    # imply an infinite tenure, which is the perpetuity this seam has already paid for
    # once, so it is refused rather than approximated.
    if margin is None:
        h2 = _blank(
            Horizon.TENURE_EXPECTED,
            TimeModel.LATEST_RENEWAL_CONDITIONED,
            Exclusion.NO_MARGIN_OBSERVED,
        )
    elif latest is None:
        h2 = _blank(
            Horizon.TENURE_EXPECTED,
            TimeModel.LATEST_RENEWAL_CONDITIONED,
            Exclusion.NO_RENEWAL_OBSERVED,
        )
    else:
        hazard = latest.churn_probability
        if hazard <= 0.0:
            # No observed propensity to leave is NOT evidence of an infinite tenure. The
            # company has no basis for a forward number here and says so.
            h2 = _blank(
                Horizon.TENURE_EXPECTED,
                TimeModel.LATEST_RENEWAL_CONDITIONED,
                Exclusion.NO_RENEWAL_OBSERVED,
            )
        else:
            h2 = _counted(
                Horizon.TENURE_EXPECTED,
                TimeModel.LATEST_RENEWAL_CONDITIONED,
                survival_discounted_value_gbp(
                    margin, hazard, discount_rate, 1.0 / hazard
                ),
            )

    # H3 — PORTFOLIO COHORT. Pooled margin and pooled hazard: what a customer LIKE this
    # one is worth. Uses none of this account's own numbers, which is why it survives an
    # account with no history of its own.
    if (
        cohort_margin_gbp is None
        or cohort_churn_probability is None
        or cohort_term_years is None
    ):
        h3 = _blank(
            Horizon.PORTFOLIO_COHORT,
            TimeModel.POOLED_EXCHANGEABLE,
            Exclusion.NO_COHORT_PEERS,
        )
    else:
        h3 = _counted(
            Horizon.PORTFOLIO_COHORT,
            TimeModel.POOLED_EXCHANGEABLE,
            survival_discounted_value_gbp(
                cohort_margin_gbp,
                cohort_churn_probability,
                discount_rate,
                cohort_term_years,
            ),
        )

    return AccountCLV(
        account_id=obs.account_id,
        contract_term=h1,
        tenure_expected=h2,
        portfolio_cohort=h3,
    )


def _pooled_cohort_inputs(
    members: Sequence[AccountObservables],
) -> tuple[float | None, float | None, float | None, Population]:
    """Pool a cohort's margin, hazard and term over the members that can supply them.

    The hazard is pooled over every RENEWAL POINT of every counted member, not over the
    members' latest points. That is what makes this horizon exchangeable, and it is a
    choice rather than an oversight: an account contributing nine renewals should weigh
    more in a peer-group prior than one contributing one.
    """
    margins: list[float] = []
    churns: list[float] = []
    terms: list[float] = []
    reasons: Counter[str] = Counter()
    counted = 0
    for m in members:
        if not m.still_supplied:
            reasons[Exclusion.CEASED.value] += 1
            continue
        if m.annual_margin_gbp is None:
            reasons[Exclusion.NO_MARGIN_OBSERVED.value] += 1
            continue
        if not m.renewal_history:
            reasons[Exclusion.NO_RENEWAL_OBSERVED.value] += 1
            continue
        counted += 1
        margins.append(float(m.annual_margin_gbp))
        terms.append(float(m.contract_term_years))
        churns.extend(r.churn_probability for r in m.renewal_history)

    population = Population(
        counted=counted, excluded=sum(reasons.values()), reasons=dict(reasons)
    )
    if counted == 0:
        return None, None, None, population
    return (
        sum(margins) / len(margins),
        sum(churns) / len(churns),
        sum(terms) / len(terms),
        population,
    )


def _median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2 == 0:
        return (ordered[mid - 1] + ordered[mid]) / 2
    return ordered[mid]


def _summarise(
    key: str,
    values: Sequence[float],
    pooled_churn: float | None,
    population: Population,
) -> CohortValue:
    if not values:
        return CohortValue(
            key=key,
            time_model=TimeModel.POOLED_EXCHANGEABLE,
            mean_value_gbp=None,
            median_value_gbp=None,
            total_value_gbp=None,
            pooled_churn_probability=pooled_churn,
            population=population,
        )
    return CohortValue(
        key=key,
        time_model=TimeModel.POOLED_EXCHANGEABLE,
        mean_value_gbp=sum(values) / len(values),
        median_value_gbp=_median(values),
        total_value_gbp=sum(values),
        pooled_churn_probability=pooled_churn,
        population=population,
    )


def estimate_book(
    observables: Iterable[AccountObservables],
    *,
    horizon: Horizon = Horizon.TENURE_EXPECTED,
    discount_rate: float = DISCOUNT_RATE,
) -> BookCLV:
    """Value a whole book, cohorting by segment.

    `horizon` selects which of the three the COHORT AGGREGATES are built from; all three
    are computed for every account regardless. Defaulting the aggregate to
    `TENURE_EXPECTED` is a stated choice, not a neutral one — it is the horizon a
    supplier's book value is conventionally quoted on — and a caller that wants the
    conservative read passes `Horizon.CONTRACT_TERM` and gets a smaller number for a
    reason it can name.

    A ceased account is VALUED (its three horizons are computed and returned) and
    EXCLUDED from every aggregate under `Exclusion.CEASED`. The distinction matters: the
    account-level number is a fact about a customer who left, and the aggregate is a
    forward claim about the book, and conflating them is what `66141b70c` had to repair.
    """
    members = list(observables)
    by_segment: dict[str, list[AccountObservables]] = {}
    for m in members:
        by_segment.setdefault(m.segment, []).append(m)

    pooled_by_segment = {
        seg: _pooled_cohort_inputs(group) for seg, group in by_segment.items()
    }

    accounts: list[AccountCLV] = []
    for m in members:
        c_margin, c_churn, c_term, _ = pooled_by_segment[m.segment]
        accounts.append(
            estimate_account(
                m,
                cohort_margin_gbp=c_margin,
                cohort_churn_probability=c_churn,
                cohort_term_years=c_term,
                discount_rate=discount_rate,
            )
        )
    by_id = {a.account_id: a for a in accounts}

    def _aggregate(key: str, group: Sequence[AccountObservables]) -> CohortValue:
        values: list[float] = []
        reasons: Counter[str] = Counter()
        for m in group:
            if not m.still_supplied:
                reasons[Exclusion.CEASED.value] += 1
                continue
            hv = by_id[m.account_id].horizon(horizon)
            if hv.value_gbp is None:
                for reason, n in hv.population.reasons.items():
                    reasons[reason] += n
                continue
            values.append(hv.value_gbp)
        _, pooled_churn, _, _ = _pooled_cohort_inputs(group)
        population = Population(
            counted=len(values), excluded=sum(reasons.values()), reasons=dict(reasons)
        )
        return _summarise(key, values, pooled_churn, population)

    cohorts = {seg: _aggregate(seg, group) for seg, group in by_segment.items()}
    portfolio = _aggregate("portfolio", members)
    return BookCLV(
        accounts=tuple(accounts),
        cohorts=cohorts,
        portfolio=portfolio,
        # The basis travels WITH the numbers rather than beside them. `horizon` and
        # `discount_rate` are this call's own arguments, so the book cannot disagree
        # with the aggregation that produced it — the alternative, letting a
        # publisher declare the basis it believes was used, is the TAUTOLOGY shape
        # inverted: a label that no longer checks anything because it is written by
        # whoever is reading.
        aggregate_horizon=horizon,
        discount_rate=discount_rate,
    )


# =========================================================================
# THE RECONCILIATION — see the module docstring. One entry per module the census finds.
# =========================================================================

#: ADOPT  — should call this module's horizons; its own arithmetic is superseded.
#: RETIRE — a duplicate with no distinct question; delete at next touch.
#: DIFFERS — genuinely answers something else, and the reason is stated.
CLV_SEAM_REGISTER: Mapping[str, tuple[str, str]] = {
    "company/core/commitment_actual_forecast.py": (
        "DIFFERS",
        "Three points in TIME on one sold contract (committed/actual/re-forecast), not "
        "three valuation bases. Its private `_term_value_gbp` is the same closed form as "
        "`survival_discounted_value_gbp` and should ADOPT this module's public one at its "
        "next touch, leaving the variance question where it belongs.",
    ),
    "company/crm/clv_calculator.py": (
        "RETIRE",
        "A general-purpose CLV with no horizon label; every question it answers is H1 or "
        "H2 here, on a rate it sets for itself.",
    ),
    "company/crm/clv_cohort_book.py": (
        "ADOPT",
        "The cohort horizon, built. Its record type has no slot for whether a customer is "
        "supplied and cannot hold a structural blank (2026-08-19 finding); `CohortValue` "
        "and `Population` are the shape it needs. Zero non-test importers, so adoption "
        "costs nothing.",
    ),
    "company/crm/clv_sensitivity_model.py": (
        "DIFFERS",
        "Sensitivity of a value to its inputs, not a value. Should take its point "
        "estimate from H2 rather than recomputing one, and its `clv_infinite_gbp` is the "
        "perpetuity this seam has already paid for once.",
    ),
    "company/crm/channel_roi.py": (
        "ADOPT",
        "An acquisition decision needs H1 (what the term I am buying is worth), not an "
        "annuity over 1/churn scaled by a channel factor. Its 0.10 rate is the one "
        "adopted here.",
    ),
    "company/crm/acquisition_cost.py": (
        "ADOPT",
        "`clv_vs_cac` multiplies margin by tenure UNDISCOUNTED — the only shape in the "
        "seam with no time value at all, so it reads high against every sibling.",
    ),
    "company/crm/acquisition_strategy_book.py": (
        "ADOPT",
        "Values a prospect off `_TYPICAL_TENURE_YEARS`, a constant table, and publishes a "
        "3x hurdle on it. One of four live residential accounts changes acquisition "
        "verdict between this and `channel_roi` (pass 8); one horizon removes the "
        "disagreement rather than adjudicating it.",
    ),
    "company/crm/acquisition_cohort.py": (
        "ADOPT",
        "Net-of-CAC cohort value. The cohorting is right and the underlying value should "
        "be H3, so the two cohort views cannot drift apart.",
    ),
    "company/crm/switching_cba.py": (
        "ADOPT",
        "The only 0.08 rate in the seam, and a single TERMINAL discount factor rather "
        "than an annuity — it discounts the whole stream as if earned on the last day.",
    ),
    "company/crm/customer_profitability_scorecard.py": (
        "ADOPT",
        "Scores a customer against a `_TARGET_CLV_GBP` of 500. R12: a target CLV is a "
        "scoring band, and must never become a thing any lever is tuned to reach.",
    ),
    "company/crm/porting_loss_register.py": (
        "ADOPT",
        "Values what a lost customer was worth. That is H1/H2 on a ceased account — "
        "exactly the case `still_supplied` forces the caller to be explicit about.",
    ),
    "company/crm/change_of_tenancy_register.py": (
        "ADOPT",
        "Values the incoming occupant. H3 is the correct horizon: a new occupant has no "
        "history of their own, which is the case the cohort horizon exists for.",
    ),
    "company/analytics/customer_value_view.py": (
        "ADOPT",
        "ADOPTED ALREADY, and it is here because the ratchet refused THIS COMMIT until "
        "it was. Wiring EP1 into the view bound a `three_horizon_clv` field, the census "
        "saw a nineteenth CLV producer, and the test went red on its own author before "
        "any of the eighteen were touched. A control whose first catch is the person who "
        "built it is the shape R15 asks for.",
    ),
    "company/finance/portfolio_dashboard.py": (
        "ADOPT",
        "Carrier, not producer: it renders an average. Named because pass 6 onward "
        "identified it as the propagator of the old horizon vocabulary, now removed.",
    ),
    "company/finance/segment_profitability.py": (
        "ADOPT",
        "Segment-level average with a `_CLV_POSITIVE_THRESHOLD_GBP`; the segment cohort "
        "is `BookCLV.cohorts` and should not be computed twice.",
    ),
    "saas/clv_model.py": (
        "ADOPT",
        "The shipped book estimator, and the one that reaches the live site. Its sBG "
        "posterior is exchangeable in a customer's own renewal order (pass 8), which is "
        "the defect `LATEST_RENEWAL_CONDITIONED` is defined against. Its uncommitted "
        "`CLV_MARGIN_BASIS` repair is a separate BUILD-lane draw and is untouched here.",
    ),
    "saas/clv_seed.py": (
        "ADOPT",
        "Seeds an opening value for an account with no history. That is H3 by "
        "definition; a second seeding rule is a second cohort prior.",
    ),
    "saas/home_move_win_rate.py": (
        "ADOPT",
        "Values the occupant it expects to win. Same case as the tenancy register, and "
        "the two should not hold different numbers for the same property.",
    ),
    "saas/reporting/annual_report.py": (
        "ADOPT",
        "Carrier, not producer: it renders snapshots and a trajectory. Its `_median` "
        "already carries the blank-is-not-zero reasoning (84ae6bbeb) that `Population` "
        "generalises.",
    ),
}

_CLV_SYMBOL = re.compile(r"(^|_)clv($|_)", re.IGNORECASE)

#: The census's own home. Excluded because a module cannot be a duplicate of itself, and
#: named as a constant so the exclusion is one auditable line rather than a `startswith`
#: buried in the walk.
_CENSUS_SELF = "company/analytics/clv_three_horizon.py"


def census_clv_modules(repo_root: Path | str) -> dict[str, list[str]]:
    """Every module under `company/` and `saas/` that BINDS a CLV-named symbol.

    Deliberately an AST walk over bindings, not a text scan: a docstring that mentions
    CLV is a module talking ABOUT the seam, and a function or field named `clv_gbp` is a
    module IN it. The same doctrine `background/process_run_complete.py` applies to
    comments, and it is what lets this run with no file excluded except its own home.

    Returns `{posix path: sorted symbol names}`, tests excluded by root.
    """
    root = Path(repo_root)
    found: dict[str, list[str]] = {}
    for package in ("company", "saas"):
        base = root / package
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            rel = path.relative_to(root).as_posix()
            if rel == _CENSUS_SELF:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                # An unparseable file is NOT silently clean. Recording it under a name
                # no register entry can match makes the census fail loudly rather than
                # shrinking, which is the fail-open shape R15 names.
                found[rel] = ["<unparseable>"]
                continue
            names: set[str] = set()
            for node in ast.walk(tree):
                targets: list[ast.expr] = []
                if isinstance(node, ast.Assign):
                    targets = list(node.targets)
                elif isinstance(node, ast.AnnAssign):
                    targets = [node.target]
                for target in targets:
                    if isinstance(target, ast.Name) and _CLV_SYMBOL.search(target.id):
                        names.add(target.id)
                    elif isinstance(target, ast.Attribute) and _CLV_SYMBOL.search(
                        target.attr
                    ):
                        names.add(target.attr)
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef)
                ) and _CLV_SYMBOL.search(node.name):
                    names.add(node.name)
            if names:
                found[rel] = sorted(names)
    return found


def unregistered_clv_modules(repo_root: Path | str) -> tuple[list[str], list[str]]:
    """`(unregistered, stale)` — the census against `CLV_SEAM_REGISTER`.

    `unregistered` is a nineteenth CLV that nobody gave a horizon to. `stale` is a
    register entry whose module no longer binds a CLV symbol — a disposition that has
    been EXECUTED, or a path that moved. Both directions are returned because a register
    that only grows cannot show its own progress, and a ratchet moving down is not
    coverage moving up.
    """
    census = census_clv_modules(repo_root)
    unregistered = sorted(set(census) - set(CLV_SEAM_REGISTER))
    stale = sorted(set(CLV_SEAM_REGISTER) - set(census))
    return unregistered, stale
