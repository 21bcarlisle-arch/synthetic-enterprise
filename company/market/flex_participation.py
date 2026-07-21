"""W1_9_dsr_flex_markets (L1) -- the COMPANY side of the DSR/flexibility
coupled triad. The company copes THROUGH THE WALL and is allowed to be wrong.

WHAT A REAL UK FLEX PARTY KNOWS (the only inputs this module may read):
  * the OBSERVED wholesale price outturn (Elexon SSP) -- public market data,
  * its OWN enrolled capacity and offers (its own records),
  * its OWN past settlement lines (`FlexSettlementLine`, off its statement).
It does NOT know the SIM's true system need, the true residual margin, or the
merit-order internals -- so it cannot see WHY a scarcity call happens, only
the PRICE it can observe. It must INFER when flex is worth bidding, and how
much revenue to expect, from that price alone (FRAME §8 refinement: the honest
L1 trigger is a price-derived scarcity proxy, never a read of true residual).

THE BELIEF (L1). The company predicts it will be dispatched in the highest-
price periods (a rolling/whole-window price percentile is its scarcity proxy)
and expects to be paid utilisation at the observed price for those periods.
Its EXPECTED utilised revenue is what it would forecast ex-ante; the SIM's
TRUE utilised revenue is driven by residual demand (which the company cannot
see). The two dispatch sets differ -- the belief-vs-truth GAP is that
forecast error, scored by `background/flex_dispatch_triad.py`.

EPISTEMIC WALL. This module imports ONLY the typed observable seam
(`interface.contracts.flex_observable_seam`) and numpy. It imports NOTHING
from `sim`/`simulation` -- verified by `python3 -m tools.epistemic_verifier`
and by `tests/company/test_flex_participation.py::test_no_sim_import`. The
price series is handed in as market data (as a real supplier reads SSP); the
company never reaches into the SIM to fetch it.

L1 NAMED SIMPLIFICATIONS (R10): the proxy is a single whole-window price
percentile (the simplest honest scarcity inference); a point-in-time /
rolling estimate and a learned dispatch-frequency model are L2+. Participation
size is the company's own input, not a benchmark.

L2 (`form_participation_belief_l2`): the company no longer assumes PERFECT
delivery. It LEARNS a de-rating from its OWN past settlement observables
(metered delivery / instructed volume -- both on its own statement) and
applies it to future forecasts, and it estimates its counterfactual BASELINE
with a methodology that may be BIASED. Both are observables-only company
BELIEFS; the SIM's true per-event delivery ratio and true baseline stay behind
the wall, so the residual belief-vs-truth GAP (sampling error in the learned
ratio + baseline-methodology error exposure) is what the harness scores.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

import numpy as np

from interface.contracts.flex_observable_seam import FlexSettlementLine

# The company's OWN scarcity-proxy threshold: it expects dispatch in periods
# whose observed price is at/above this percentile. Its belief parameter (a
# guess), deliberately the SAME nominal percentile the SIM uses for residual
# so the ONLY thing separating truth from belief is residual-vs-price -- the
# real form inadequacy, not a threshold mismatch artefact.
DEFAULT_PRICE_SCARCITY_PERCENTILE: float = 95.0


@dataclass(frozen=True)
class FlexParticipationBelief:
    """The company's observables-only flex participation belief for one run.

    `expected_utilised_revenue` is the per-period revenue vector b the harness
    scores against the SIM truth; `predicted_dispatch_mask` is the company's
    price-proxy guess at which periods it will be called."""

    expected_utilised_revenue: np.ndarray   # per-period, GBP
    predicted_dispatch_mask: np.ndarray     # bool, company's price-proxy guess
    observed_price: np.ndarray              # GBP/MWh, the only signal used
    enrolled_mw: float
    period_hours: float
    price_percentile: float

    @property
    def total_expected_revenue_gbp(self) -> float:
        return float(self.expected_utilised_revenue.sum())

    @property
    def n_predicted_dispatch(self) -> int:
        return int(self.predicted_dispatch_mask.sum())


def form_participation_belief(
    observed_price: Sequence[float],
    *,
    enrolled_mw: float,
    period_hours: float,
    price_percentile: float = DEFAULT_PRICE_SCARCITY_PERCENTILE,
) -> FlexParticipationBelief:
    """Form the company's ex-ante flex participation belief from the OBSERVED
    price alone. It predicts dispatch in the top-`price_percentile` price
    periods (its scarcity proxy) and expects utilisation revenue there at the
    observed price. Reads NO SIM internal -- only the price a supplier sees."""
    price = np.asarray(list(observed_price), dtype=float)
    if price.size == 0:
        raise ValueError("form_participation_belief: empty observed price series")
    thr = float(np.percentile(price, price_percentile))
    predicted = price >= thr
    expected_mwh = np.where(predicted, enrolled_mw * period_hours, 0.0)
    expected_revenue = expected_mwh * price
    return FlexParticipationBelief(
        expected_utilised_revenue=expected_revenue,
        predicted_dispatch_mask=predicted,
        observed_price=price,
        enrolled_mw=enrolled_mw,
        period_hours=period_hours,
        price_percentile=price_percentile,
    )


# The company's baseline-estimation bias (L2). 0.0 = an unbiased counterfactual
# methodology; >0 over-states the baseline (claims more reduction than real,
# clawback exposure); <0 under-states. A COMPANY BELIEF parameter -- the SIM's
# true baseline is not readable across the wall.
DEFAULT_BASELINE_BIAS: float = 0.0


@dataclass(frozen=True)
class FlexParticipationBeliefL2:
    """The company's L2 flex participation belief: L1 price-proxy dispatch plus
    a LEARNED delivery de-rating and a (possibly biased) baseline estimate.

    `expected_utilised_revenue` is the de-rated per-period forecast the harness
    scores; `learned_delivery_ratio` is what the company inferred from its own
    settlement; `estimated_baseline_mwh` is its counterfactual estimate whose
    error vs the SIM truth is the company's baseline-methodology exposure."""

    expected_utilised_revenue: np.ndarray   # per-period, GBP (de-rated)
    predicted_dispatch_mask: np.ndarray     # bool, price-proxy guess (as L1)
    observed_price: np.ndarray
    learned_delivery_ratio: float           # inferred from own settlement
    estimated_baseline_mwh: float           # per-event counterfactual estimate
    baseline_bias: float
    enrolled_mw: float
    period_hours: float
    price_percentile: float

    @property
    def total_expected_revenue_gbp(self) -> float:
        return float(self.expected_utilised_revenue.sum())

    @property
    def n_predicted_dispatch(self) -> int:
        return int(self.predicted_dispatch_mask.sum())


def learn_delivery_ratio(
    observed_delivery_mwh: Optional[Sequence[float]],
    *,
    instructed_mwh: float,
) -> float:
    """Infer the portfolio's realised delivery ratio from the company's OWN
    past settlement observables: mean(metered delivery) / instructed volume.
    Both quantities are on the company's statement (metered delivery crosses
    the seam; instructed volume is its own enrolled capacity x window) -- no
    SIM internal is read. Cold start (no history) => 1.0, i.e. the company
    falls back to the L1 perfect-delivery assumption until it has evidence.
    FAIL-CLOSED on a non-positive instructed volume (a degenerate enrolment)."""
    if instructed_mwh <= 0.0:
        raise ValueError("learn_delivery_ratio: instructed_mwh must be > 0")
    if not observed_delivery_mwh:
        return 1.0
    arr = np.asarray(list(observed_delivery_mwh), dtype=float)
    if arr.size == 0:
        return 1.0
    return float(np.clip(arr.mean() / instructed_mwh, 0.0, 1.0))


def form_participation_belief_l2(
    observed_price: Sequence[float],
    *,
    enrolled_mw: float,
    period_hours: float,
    observed_delivery_mwh: Optional[Sequence[float]] = None,
    price_percentile: float = DEFAULT_PRICE_SCARCITY_PERCENTILE,
    baseline_bias: float = DEFAULT_BASELINE_BIAS,
) -> FlexParticipationBeliefL2:
    """Form the company's L2 flex participation belief. Dispatch prediction is
    the L1 price-proxy (top-percentile observed price). Two L2 refinements:

      * DELIVERY DE-RATING -- the expected delivered volume is de-rated by the
        ratio LEARNED from the company's own past settlement observables
        (`observed_delivery_mwh`), instead of the L1 perfect-delivery
        assumption. This is the company coping better with a portfolio that
        under-delivers, still wrong by the sampling error of a finite history.
      * BASELINE ESTIMATE -- the company estimates its per-event counterfactual
        baseline with a (possibly biased) methodology; `estimated_baseline_mwh`
        is exposed so the harness can score the baseline-methodology error
        against the SIM truth (the company cannot see that gap itself).

    Reads NO SIM internal -- only observed price + the company's own settlement
    history + its own enrolment."""
    price = np.asarray(list(observed_price), dtype=float)
    if price.size == 0:
        raise ValueError("form_participation_belief_l2: empty observed price series")
    instructed_mwh = enrolled_mw * period_hours
    thr = float(np.percentile(price, price_percentile))
    predicted = price >= thr
    learned_ratio = learn_delivery_ratio(observed_delivery_mwh, instructed_mwh=instructed_mwh)
    estimated_baseline = instructed_mwh * (1.0 + baseline_bias)
    # De-rated expected delivered volume in the predicted-dispatch periods.
    expected_mwh = np.where(predicted, instructed_mwh * learned_ratio, 0.0)
    expected_revenue = expected_mwh * price
    return FlexParticipationBeliefL2(
        expected_utilised_revenue=expected_revenue,
        predicted_dispatch_mask=predicted,
        observed_price=price,
        learned_delivery_ratio=learned_ratio,
        estimated_baseline_mwh=estimated_baseline,
        baseline_bias=baseline_bias,
        enrolled_mw=enrolled_mw,
        period_hours=period_hours,
        price_percentile=price_percentile,
    )


def realised_revenue_from_settlement(lines: Optional[List[FlexSettlementLine]]) -> float:
    """Sum the company's OWN observable settlement lines -- its realised
    utilisation revenue as read off its statement (observation, not truth).
    Tolerant of an empty / one-at-a-time / out-of-order feed (C-S1): each line
    is independently additive, no batch-completeness assumption."""
    if not lines:
        return 0.0
    return float(sum(line.utilisation_payment_gbp for line in lines))
