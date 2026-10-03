"""B8: the company discovers how its own customers respond to price, from its own renewals.

REUSE: company/pricing/discovered_price_sensitivity.py
CLASS: CUSTOM
INDEX: the atom names this file (`B8_discovered_price_sensitivity_holdout`, file_scope). Searched
       "price sensitivity", "slope", "learn", "posterior", "calibrat". The nearest is PB7's
       `company/crm/competitive_pressure.py`, which learns two LEVEL scalers (market pressure,
       payment-method engagement) from the company's own closed renewals; it is REUSED here, not
       paralleled -- the observations ride its ledger, scope and arming, and its precision weight
       sets the update. `tools/grade_renewal_churn_belief.py` grades the belief and moves nothing.
       No existing mechanism learns the PRICE RESPONSE: `churn_model.RATE_SENSITIVITY = 0.8` is a
       fixed literal for every household.

WHY (2026-10-03). The per-decision probe found the value rule's choosing loses 2,146-3,046 against
a flat price at its own median on four reference paths, and that the loss is the churn belief
(`SEAT_PREREG_WHICH_BELIEF_THE_CHOOSING_LOSES_ON_2026-10-03.md`). The company believes +10% price
costs 0.08 of P(stay) for everyone; the world's median is 0.036, and it differs by how a household
pays (prepayment 0.118, direct debit 0.038, standard credit 0.014). Most of the per-household spread
is unlearnable by construction (R1), but the part that runs with an observable is not.

WHAT IS LEARNED. Not the constant: a CORRECTION to the final belief's price response, per payment
method and fuel. The company believes P(leave) = (its existing estimate) + delta x own_move, where
own_move is the offer's gap to the published default -- the move a household can compare against
a cheaper alternative. Delta starts at 0 (the company's existing belief, unchanged) and is
estimated from realised-minus-believed departures across the company's own closed renewals:
delta_hat = cov(left - believed, own_move) / var(own_move). It is then shrunk towards 0 by PB7's
precision rule, so a thin book barely moves the belief. Learning a correction on the FINAL belief,
rather than re-deriving the constant, is deliberate: the rate term is multiplied downstream by
market pressure and engagement, and a learned raw constant would have to divide those back out.

NO LOOK-AHEAD. A renewal enters the estimate only for years strictly before the one being priced,
exactly as PB7's windows do. A departure is attributed to the renewal it ended through the company's
own account id: the company knows its own customers.

THE PRIOR'S SPREAD IS A BELIEF, NOT A SOURCED FIGURE, and is labelled so. Nothing published states
how uncertain a supplier should be about its own price slope. `PRIOR_DELTA_SD` says the company holds
its correction to within the size of its own slope: one standard deviation equal to RATE_SENSITIVITY.
The B8 pre-registration grades the result, and its sensitivity to this choice is reported, not hidden.
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass

from company.crm.churn_model import RATE_SENSITIVITY

#: BELIEF (B8, graded by SEAT_PREREG_B8_..._2026-10-03.md): the company's prior uncertainty about
#: its own price-response correction, one standard deviation, in P(leave) per unit own move. Equal
#: to its own resi slope -- "I could be wrong by as much as the whole slope". Not a published figure.
PRIOR_DELTA_SD = RATE_SENSITIVITY

#: The fuels whose price response is learned. I&C is priced by brokers on a different model and
#: is out of B8's scope; a method or fuel outside these gets no correction (delta 0).
LEARNED_FUELS = ("electricity", "gas")


def own_move(new_rate_gbp_per_mwh: float, old_rate_gbp_per_mwh: float | None, fuel: str,
             renewal_year: int | None, segment: str = "resi", on_date: str | dt.date | None = None,
             published_default_rate_gbp_per_mwh: float | None = None) -> float | None:
    """THE company's own price move at a renewal: the one definition learning and pricing share.

    A household with a published default to compare against (the cap, from 2019): the offer's gap
    to it, ex VAT, which is what the pricing chain prices against. Everything else -- every renewal
    before 2019, and every business account at any date, which the chain hands no default: the
    household's own price change net of the market's move as the company reads it, the same
    fallback `churn_model.estimate_churn_probability` uses. Until 2026-10-03 the desk measured every
    account against the domestic cap and pricing measured a business account by the fallback, so
    the learner was taught on one quantity and priced on another (B8 step 2).
    """
    if segment == "resi":
        default = published_default_rate_gbp_per_mwh
        if default is None and on_date is not None:
            gap = own_move_against_default(new_rate_gbp_per_mwh, fuel, on_date)
            if gap is not None:
                return gap
        elif default:
            return (float(new_rate_gbp_per_mwh) - float(default)) / float(default)
    if not old_rate_gbp_per_mwh or not new_rate_gbp_per_mwh or renewal_year is None:
        return None
    from company.crm.market_conditions import market_rate_move_pct
    return ((float(new_rate_gbp_per_mwh) - float(old_rate_gbp_per_mwh))
            / float(old_rate_gbp_per_mwh) - float(market_rate_move_pct(renewal_year, fuel=fuel)))


def own_move_against_default(new_rate_gbp_per_mwh: float, fuel: str, on_date: str | dt.date
                             ) -> float | None:
    """The offer's gap to the published default tariff for this fuel on this day, ex VAT --
    the same reference the pricing chain prices against. None where no cap applied (before 2019)
    or no rate: no move is asserted where the company has no published reference to compare."""
    from company.pricing.renewal_rate_chain import cap_ceiling_ex_vat
    day = on_date if isinstance(on_date, dt.date) else dt.date.fromisoformat(str(on_date)[:10])
    try:
        default = cap_ceiling_ex_vat(fuel, day, multi_register=False)
    except Exception:
        return None
    if not default or not new_rate_gbp_per_mwh:
        return None
    return (float(new_rate_gbp_per_mwh) - float(default)) / float(default)


@dataclass(frozen=True)
class SlopeReading:
    """What the company has learned about one channel's price response, and how much it trusts it."""

    payment_method: str
    fuel: str
    renewals: int
    departures: int
    raw_delta: float | None
    weight: float
    delta: float

    @property
    def moved_from_prior(self) -> bool:
        return self.weight > 0.0 and self.delta != 0.0


def slope_reading(sums: dict | None, payment_method: str, fuel: str) -> SlopeReading:
    """The posterior correction from closed-window sums: n, sum x, sum x^2, sum believed, sum
    believed*x, departures, sum x over departures. Delta 0 and weight 0 for any window that cannot
    support a slope (fewer than three renewals, or no spread in own move)."""
    s = sums or {}
    n = int(s.get("n", 0))
    if n < 3:
        return SlopeReading(payment_method, fuel, n, int(s.get("losses", 0)), None, 0.0, 0.0)
    mean_x = s["sx"] / n
    sxx_c = s["sxx"] - n * mean_x * mean_x
    if not math.isfinite(sxx_c) or sxx_c <= 1e-9:
        return SlopeReading(payment_method, fuel, n, int(s.get("losses", 0)), None, 0.0, 0.0)
    resid_cov = (s["loss_x"] - s["spx"]) - mean_x * (s["losses"] - s["sp"])
    raw = resid_cov / sxx_c
    p_bar = min(max(s["sp"] / n, 1e-3), 1 - 1e-3)
    v_evidence = p_bar * (1.0 - p_bar) / sxx_c
    v_prior = PRIOR_DELTA_SD ** 2
    weight = v_prior / (v_prior + v_evidence)
    return SlopeReading(payment_method, fuel, n, int(s["losses"]), raw, weight, weight * raw)


def learned_correction(payment_method: str | None, fuel: str | None,
                       renewal_year: int | None) -> float:
    """The correction to apply to this renewal's belief, per unit own move: 0 unless the active
    policy asks for it, a run ledger is in scope, and the channel and fuel are learnable."""
    from company.crm.competitive_pressure import active_pressure_ledger
    from company.policy.decision_policy import active_policy
    if not active_policy().learn_price_response:
        return 0.0
    ledger = active_pressure_ledger()
    if ledger is None or not payment_method or fuel not in LEARNED_FUELS or renewal_year is None:
        return 0.0
    sums = ledger.closed_slope_sums(str(payment_method), str(fuel), int(renewal_year))
    return slope_reading(sums, str(payment_method), str(fuel)).delta
