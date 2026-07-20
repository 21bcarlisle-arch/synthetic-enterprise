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


def realised_revenue_from_settlement(lines: Optional[List[FlexSettlementLine]]) -> float:
    """Sum the company's OWN observable settlement lines -- its realised
    utilisation revenue as read off its statement (observation, not truth).
    Tolerant of an empty / one-at-a-time / out-of-order feed (C-S1): each line
    is independently additive, no batch-completeness assumption."""
    if not lines:
        return 0.0
    return float(sum(line.utilisation_payment_gbp for line in lines))
