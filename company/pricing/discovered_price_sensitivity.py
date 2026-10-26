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
#: Asks `learned_correction` for the response pooled over every channel: what a price may rest on,
#: because a slope learned per channel prices a clean account by how it pays (see
#: `enriched_churn_estimate`'s `channel_blind`).
EVERY_CHANNEL = "*"


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
    if payment_method == EVERY_CHANNEL:
        sums: dict = {}
        for method in sorted({m for (m, f, _y) in ledger.slope_sums if f == fuel}):
            for k, v in ledger.closed_slope_sums(method, str(fuel), int(renewal_year)).items():
                sums[k] = sums.get(k, 0) + v
    else:
        sums = ledger.closed_slope_sums(str(payment_method), str(fuel), int(renewal_year))
    return slope_reading(sums, str(payment_method), str(fuel)).delta


# --- B8: the offer's effect, from the company's own coin-drawn holdout -------------------------
#
# The slope above is learned from renewals the company priced by its own rule, which is why it can
# never identify an OFFER's effect: on the settled book every renewal above the belief threshold is
# offered, so no comparison holds the belief fixed (`3811342db`). A holdout breaks that by
# construction. The company flips its own coin at each renewal and compares the arms. It sees only
# who stayed, so the estimate is a difference of two shares, and its interval is the whole claim.

#: The coverage of the interval the estimate is published with. Not a domain figure: the
#: convention the census in `3811342db` used, kept so the two read on one scale.
INTERVAL_COVERAGE = 0.95


@dataclass(frozen=True)
class OfferEffectEstimate:
    """What a holdout says an offer did to staying: treated stay share minus held-out stay share."""

    treated: int
    held_out: int
    stayed_treated: int
    stayed_held_out: int
    effect: float | None
    low: float | None
    high: float | None
    verdict: str
    reason: str


def _wilson(stayed: int, n: int, z: float) -> tuple[float, float, float]:
    p = stayed / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return p, centre - half, centre + half


def estimate_offer_effect(observations) -> OfferEffectEstimate:
    """The offer's effect on staying from the company's own holdout rows alone (each row: `arm`
    "treated" or "holdout", `stayed`). The interval is Newcombe's hybrid score interval for a
    difference of two proportions, the one the `3811342db` census used.

    THE VERDICT IS THE INTERVAL'S, NEVER THE POINT'S: "raises staying" only when the whole interval
    is above zero, "lowers staying" only when it is wholly below, and "undecided" otherwise -- an
    underpowered holdout is a result, not a failure. An arm with no rows is refused by name: a
    difference against nothing is not an estimate.
    """
    from statistics import NormalDist

    counts = {"treated": [0, 0], "holdout": [0, 0]}
    for row in observations:
        arm = counts.get(row["arm"])
        if arm is None:
            raise ValueError(f"a holdout row names no arm the company ran: {row['arm']!r}")
        arm[0] += 1
        arm[1] += bool(row["stayed"])
    (n1, s1), (n0, s0) = counts["treated"], counts["holdout"]
    if not n1 or not n0:
        empty = "treated" if not n1 else "holdout"
        return OfferEffectEstimate(n1, n0, s1, s0, None, None, None, "refused",
                                   f"the {empty} arm holds no decision, so nothing is compared")
    z = NormalDist().inv_cdf(0.5 + INTERVAL_COVERAGE / 2)
    p1, l1, u1 = _wilson(s1, n1, z)
    p0, l0, u0 = _wilson(s0, n0, z)
    d = p1 - p0
    low = d - math.sqrt((p1 - l1) ** 2 + (u0 - p0) ** 2)
    high = d + math.sqrt((u1 - p1) ** 2 + (p0 - l0) ** 2)
    if low > 0:
        verdict, reason = "raises_staying", "the whole interval is above zero"
    elif high < 0:
        verdict, reason = "lowers_staying", "the whole interval is below zero"
    else:
        verdict, reason = "undecided", "the interval spans zero at this many decisions"
    return OfferEffectEstimate(n1, n0, s1, s0, d, low, high, verdict, reason)


# --- B8 L2: the company USES the estimate. A retention cut is offered where it pays ----------------
#
# Two forward values, both the supplier's: without the cut the household stays with the held-out
# share and earns its margin; with it, it stays with that share plus the learned effect and earns its
# margin less the cut on every kWh it is billed. The household's side (the saving) is reported beside
# this by the grader and never enters it.

#: The power the per-channel read asks for before it trusts a channel's own estimate. Not a domain
#: figure: the convention `tools/grade_coin_drawn_holdout._power_n` sized the set with.
CHANNEL_READ_POWER = 0.80


def estimate_offer_effect_by_channel(observations) -> dict[str, OfferEffectEstimate]:
    """`estimate_offer_effect` per payment method, on the same rows."""
    by: dict[str, list] = {}
    for row in observations:
        by.setdefault(str(row["payment_method"]), []).append(row)
    return {m: estimate_offer_effect(rows) for m, rows in sorted(by.items())}


#: The positions a save offer may vary by (director, 2026-10-08), as the company's holdout rows
#: carry them. `company.crm.save_offer.SAVE_MAY_VARY_BY` names the two a save prices on; the third,
#: whether the account has ever renewed actively, is the company's own renewal record.
SAVE_POSITION_OBSERVABLES = ("acquisition_route", "days_on_default", "ever_actively_renewed")


def position_group(observation: dict, observable: str) -> str:
    """The group one decision falls in on `observable`. Days on the default are read in whole years
    (0, 1, 2+), the unit the renewal walk moves in; every other observable is its own value."""
    value = observation[observable]
    if observable == "days_on_default" and value is not None:
        years = int(value) // 365
        return f"{years}y" if years < 2 else "2y+"
    return str(value)


def estimate_offer_effect_by_position(observations, observable: str) -> dict[str, OfferEffectEstimate]:
    """`estimate_offer_effect` per group of `observable` (`position_group`), on the same rows."""
    by: dict[str, list] = {}
    for row in observations:
        by.setdefault(position_group(row, observable), []).append(row)
    return {g: estimate_offer_effect(rows) for g, rows in sorted(by.items())}


def decisions_needed_per_arm(estimate: OfferEffectEstimate) -> int | None:
    """Decisions per arm for a two-sided test at `INTERVAL_COVERAGE` to find `estimate`'s own effect
    with `CHANNEL_READ_POWER`, at its held-out stay share. None where there is no effect to find."""
    from statistics import NormalDist

    if not estimate.effect or not estimate.held_out:
        return None
    nd = NormalDist()
    z = nd.inv_cdf(0.5 + INTERVAL_COVERAGE / 2) + nd.inv_cdf(CHANNEL_READ_POWER)
    p = estimate.stayed_held_out / estimate.held_out
    return math.ceil(2 * z * z * p * (1 - p) / estimate.effect ** 2)


def _difference_and_variance(treated: int, held_out: int, stayed_treated: int,
                             stayed_held_out: int) -> tuple[float, float]:
    """Treated minus held-out stay share, and its Wald variance."""
    p1, p0 = stayed_treated / treated, stayed_held_out / held_out
    return p1 - p0, p1 * (1 - p1) / treated + p0 * (1 - p0) / held_out


def channel_gap(own: OfferEffectEstimate, pooled: OfferEffectEstimate) -> tuple[float, float] | None:
    """The channel's effect minus the effect on the rest of the book (pooled counts less the
    channel's), and the two-sided `INTERVAL_COVERAGE` bound on that gap. None where the rest has an
    empty arm: a channel that is the whole book has nothing to differ from."""
    from statistics import NormalDist

    rest = (pooled.treated - own.treated, pooled.held_out - own.held_out,
            pooled.stayed_treated - own.stayed_treated, pooled.stayed_held_out - own.stayed_held_out)
    if min(rest) < 0:
        raise ValueError("the channel holds more decisions than the pooled estimate: they were not "
                         "estimated on the same rows")
    if not rest[0] or not rest[1]:
        return None
    d_own, v_own = _difference_and_variance(own.treated, own.held_out, own.stayed_treated,
                                            own.stayed_held_out)
    d_rest, v_rest = _difference_and_variance(*rest)
    z = NormalDist().inv_cdf(0.5 + INTERVAL_COVERAGE / 2)
    return d_own - d_rest, z * math.sqrt(v_own + v_rest)


def effect_for_channel(payment_method: str, by_channel: dict[str, OfferEffectEstimate],
                       pooled: OfferEffectEstimate) -> tuple[OfferEffectEstimate, str]:
    """The channel's own estimate where its smaller arm reaches the decisions the POOLED effect needs
    AND its effect differs from the rest of the book's beyond the interval on that gap; otherwise
    the pooled one, and the reason says which gate refused.

    Power alone is not enough: it passes as the book grows whether or not the channels differ, and
    a channel read where they do not swaps the pooled estimate for a noisier subset of the same rows
    (2026-10-26: direct debit read on 12,096 of 16,788 decisions where the world's per-channel gap
    was 0.0001)."""
    need = decisions_needed_per_arm(pooled)
    own = by_channel.get(payment_method)
    if own is None or own.verdict == "refused":
        return pooled, f"pooled: no {payment_method} decision in the holdout"
    have = min(own.treated, own.held_out)
    if need is None:
        return pooled, f"pooled: {payment_method} has {have:,} per arm and the pooled effect is nil"
    if have < need:
        return pooled, f"pooled: {payment_method} has {have:,} per arm, short of the {need:,} needed"
    gap = channel_gap(own, pooled)
    if gap is None:
        return pooled, f"pooled: {payment_method} is the whole book, so there is no rest to differ from"
    diff, bound = gap
    if abs(diff) <= bound:
        return pooled, (f"pooled: {payment_method} is powered ({have:,} per arm) but its gap to the rest, "
                        f"{diff:+.4f}, is inside +/-{bound:.4f}")
    return own, (f"{payment_method}: {have:,} per arm reaches the {need:,} needed and its gap to the "
                 f"rest, {diff:+.4f}, is beyond +/-{bound:.4f}")


@dataclass(frozen=True)
class CutDecision:
    """One renewal's retention decision, both forward values, and why."""

    offer_cut: bool
    value_with_cut: float | None
    value_without_cut: float | None
    read: str
    reason: str


def retention_cut_decision(observation: dict, *, cut_gbp_per_mwh: float, margin_share: float,
                           by_channel: dict[str, OfferEffectEstimate],
                           pooled: OfferEffectEstimate,
                           observable: str = "payment_method") -> CutDecision:
    """Offer `cut_gbp_per_mwh` at this renewal only where the learned effect pays for it at
    `margin_share` of the household's own last year's bills, and only where the holdout says the
    offer raises staying at all.

    `margin_share` has no default on purpose: what share of a retained household's bill a supplier
    keeps is not established as one figure -- it lies between the cap's EBIT allowance and the
    sector's gross margin, and the caller names which it means.

    `observable` names what `by_channel` is grouped by: the payment method by default, or one of
    `SAVE_POSITION_OBSERVABLES` read through `estimate_offer_effect_by_position`.

    The years after this one are valued at the held-out stay share `s` the company observed, as
    `s / (1 - s)` further years: the same horizon for either option, so it scales the margin a stay
    is worth and never favours one side by construction.
    """
    est, read = effect_for_channel(position_group(observation, observable), by_channel, pooled)
    if est.verdict != "raises_staying":
        return CutDecision(False, None, None, read,
                           f"no cut: the holdout says {est.verdict.replace('_', ' ')} ({est.reason})")
    p0 = est.stayed_held_out / est.held_out
    if not 0.0 < p0 < 1.0:
        return CutDecision(False, None, None, read, f"no cut: a held-out stay share of {p0} values no future")
    return _cut_on_value(p0, est.effect, margin_share * sum(observation["monthly_bills"]),
                         cut_gbp_per_mwh * float(observation["billed_kwh"]) / 1000.0, read)


def _cut_on_value(p0: float, effect: float, margin: float, cut_cost: float, read: str) -> CutDecision:
    """The two forward values at stay share `p0` and `effect` of staying bought, and the decision."""
    lifetime = margin * (1.0 + p0 / (1.0 - p0))
    without = p0 * lifetime
    with_cut = min(1.0, p0 + effect) * (lifetime - cut_cost)
    if with_cut > without:
        return CutDecision(True, with_cut, without, read,
                           f"cut: +{effect:.4f} of staying is worth {with_cut - without:.2f} more than it costs")
    return CutDecision(False, with_cut, without, read,
                       f"no cut: +{effect:.4f} of staying is worth {without - with_cut:.2f} less than the cut")


# --- B8 Q8: the company's prior on what a cut buys, from published trials ---------------------------
#
# The director, 2026-10-12 (canon C8, decision 7): the company may learn what an offer does from
# published trials and from its own randomised holdout, never from the world's truth. The run's own
# holdout cannot separate the effect from zero at the founders' scale (~30 considered renewals a year
# against ~19,600 per arm), and a significance gate then keeps it passive for good (blind Expert Hour
# Q8). So the run decides on expected value under a belief the published gradients start and its
# own rows update. Knowledge page: how_households_respond_to_supplier_contact.md s.6.

#: PUBLISHED, two observational gradients of 30-day switching on the annual saving available, per GBP:
#: CMOL technical annex s.12 (0.0000522, whole sample) and CMOC s.3.42 fn.43 (+1.3% per GBP 100,
#: contacted only). Both overstate the causal effect (the saving runs with consumption, and with it
#: engagement; CMOC counts those who would have switched anyway), so a prior from them is generous
#: to the offer. No trial randomises a retention offer's size.
PUBLISHED_STAY_PER_GBP_OF_SAVING = (0.0000522, 0.00013)
PRIOR_STAY_PER_GBP_MEAN = sum(PUBLISHED_STAY_PER_GBP_OF_SAVING) / 2
#: BELIEF, not a published figure, and the module's one convention for a spread nothing publishes
#: (`PRIOR_DELTA_SD`): "I could be wrong by as much as the whole gradient". Half the two figures' span
#: was the first draft; printed, it let 800 rows showing +0.20 of staying move the belief by 0.1%,
#: a company deaf to its own holdout over two figures from a different decision (30-day switching
#: on default stock, not a renewal). Never sized from the world's response: that is its truth.
PRIOR_STAY_PER_GBP_SD = PRIOR_STAY_PER_GBP_MEAN


@dataclass(frozen=True)
class StayPerPound:
    """The company's belief in the staying a GBP of annual cut buys: the published prior, updated by
    precision with its own holdout where its rows carry a comparison."""

    mean: float
    sd: float
    own_rows: int
    reason: str


def stay_per_pound(rows) -> StayPerPound:
    """The belief after `rows` (closed holdout rows, each `arm`, `stayed`, and on the treated arm the
    `cut_gbp` it was offered). The own-book gradient is the pooled effect over the treated rows' mean
    annual cut, its variance the Newcombe half-width over z, squared, over that cut. With no
    comparison -- an empty arm, or no treated row carrying its cut -- the prior stands alone."""
    from statistics import NormalDist

    rows = list(rows)
    prior = StayPerPound(PRIOR_STAY_PER_GBP_MEAN, PRIOR_STAY_PER_GBP_SD, len(rows),
                         "published prior alone")
    pooled = estimate_offer_effect(rows)
    if pooled.verdict == "refused":
        return StayPerPound(prior.mean, prior.sd, len(rows), f"published prior alone: {pooled.reason}")
    cuts = [float(r["cut_gbp"]) for r in rows if r["arm"] == "treated" and r.get("cut_gbp")]
    if not cuts:
        return StayPerPound(prior.mean, prior.sd, len(rows),
                            "published prior alone: no treated row carries the cut it was offered")
    mean_cut = sum(cuts) / len(cuts)
    z = NormalDist().inv_cdf(0.5 + INTERVAL_COVERAGE / 2)
    own_sd = (pooled.high - pooled.low) / (2 * z) / mean_cut
    own = pooled.effect / mean_cut
    w_prior, w_own = PRIOR_STAY_PER_GBP_SD ** -2, own_sd ** -2
    mean = (w_prior * PRIOR_STAY_PER_GBP_MEAN + w_own * own) / (w_prior + w_own)
    return StayPerPound(mean, (w_prior + w_own) ** -0.5, len(rows),
                        f"published prior with {pooled.treated}+{pooled.held_out} own rows, "
                        f"own {own:.6f}/GBP at weight {w_own / (w_prior + w_own):.3f}")


def retention_cut_on_belief(belief: StayPerPound, *, stay_belief: float, term_margin_gbp: float,
                            cut_gbp: float) -> CutDecision:
    """Offer the cut where the staying it buys at `belief`'s mean, valued over the household's expected
    tenure, pays for it: expected value, never significance (Q8). `stay_belief` is the company's own
    for this renewal -- a held-out share from a handful of rows is no share at all."""
    read = f"{belief.reason}: {belief.mean:.6f} of staying per GBP"
    if not 0.0 < stay_belief < 1.0:
        return CutDecision(False, None, None, read, f"no cut: a stay belief of {stay_belief} values no future")
    return _cut_on_value(stay_belief, belief.mean * cut_gbp, term_margin_gbp, cut_gbp, read)


# --- B8 L3: the run's own retention holdout --------------------------------------------------------
#
# L2 decided on an estimate learned off a coin-drawn decision set the size of a national book. The
# run's company has only its own renewals, so it runs the holdout itself: at every renewal its guard
# would consider, it flips its own coin. The held-out half gets no offer. The other half gets the
# offer the company decides on expected value: the published prior, updated by its own closed rows
# (B8 Q8, `retention_cut_on_belief`). Until 2026-10-20 the standing guard decided while the
# interval was undecided, which at this scale was always.
# A row is written only where the company WOULD have offered, on either arm
# (`RetentionHoldout.would_offer`). The coin is flipped over every renewal the guard considers, but only the would-offer ones are the
# experiment: keeping a held-out renewal the guard would have declined, while dropping its treated
# twin, puts households nobody would offer into one arm only (blind Expert Hour, 2026-10-11, Q11).

#: Not a domain figure: the split that gives a difference of two shares its narrowest interval for a
#: given number of decisions, the one `simulation/coin_drawn_decision_set.py` flips.
HOLDOUT_SHARE = 0.5


def holdout_arm(account_id: str, event_date: str) -> str:
    """The company's own coin for this renewal: `"holdout"` or `"treated"`. Seeded on the account and
    the day, so a re-run flips the same coin, and on nothing the world drew."""
    import hashlib

    digest = hashlib.sha256(f"B8_run_holdout::{account_id}::{event_date}".encode()).digest()
    return "holdout" if int.from_bytes(digest[:8], "big") / 2 ** 64 < HOLDOUT_SHARE else "treated"


#: HOW LONG AFTER A RENEWAL A LOSS IS STILL THAT RENEWAL'S (blind Expert Hour, 2026-10-11, Q10). None
#: on purpose: no published source establishes a retention-measurement window for a GB domestic
#: renewal. SLC 22C fixes the notice (42-49 days before term end) and the fee-free exit window
#: before it, not how long after the decision a loss is attributed; a practitioner case study's
#: "six or twelve months" is advice, not evidence. While it is None no holdout row closes, so the
#: company learns nothing from its own holdout and the published prior decides alone. 0 is the old definition (stayed
#: at the decision itself), kept nameable so the bias it carries can be measured against a window.
#: Keep a window inside the term it attributes: at or past a re-fix's own term end it counts the
#: household's NEXT renewal departure against this one (2026-10-11: nine of ten later losses sat there).
RETENTION_OUTCOME_WINDOW_DAYS: int | None = None

#: The three ways a renewal decision ends, as the supplier holds them: the household left on the
#: decision, took the new fixed term, or stayed and refused it and sits on the default tariff. A
#: rollover onto the default is not a re-fix, and a held-out arm full of one is not the other's twin.
RENEWAL_KINDS = ("left_at_decision", "re_fixed", "declined_fix_on_default")


class RetentionHoldout:
    """The run's holdout rows, and the decision they support at a given day.

    A row's outcome is "still on supply `outcome_window_days` after the renewal", read from the
    company's own loss notices (`CoSRegister.losses_notified()`) on the account's supply points. A
    move-out is not a loss notice and does not count against the row: a household that moved home
    was not lost to a rival price."""

    def __init__(self, outcome_window_days: int | None = RETENTION_OUTCOME_WINDOW_DAYS) -> None:
        self.rows: list[dict] = []
        self.outcome_window_days = outcome_window_days

    def record(self, *, account_id: str, event_date: str, arm: str, stayed: bool,
               payment_method: str | None, saved_on_loss_notice: bool = False,
               renewal: str | None = None, supply_points: tuple[str, ...] = (),
               cut_gbp: float | None = None) -> None:
        """`stayed` is the decision's own stay-or-leave; the outcome is read later, at the window.
        `saved_on_loss_notice`: the household was leaving and the reactive save kept it. It
        stays `stayed` (the estimate is the renewal offer's effect with the save running, on both
        arms alike), but it is carried so a save reaching the held-out arm is counted, not hidden.
        `renewal` is one of `RENEWAL_KINDS`; `supply_points` are the account's own points, the key
        its loss notices arrive under. `cut_gbp` is the annual cut the renewal was (or, held out,
        would have been) offered: what the own-book gradient divides by."""
        kind = renewal or ("re_fixed" if stayed else "left_at_decision")
        if kind not in RENEWAL_KINDS or (kind == "left_at_decision") == bool(stayed):
            raise ValueError(f"a renewal that {'stayed' if stayed else 'left'} cannot end {kind!r}")
        self.rows.append({"account_id": account_id, "event_date": event_date, "arm": arm,
                          "stayed_at_decision": bool(stayed), "renewal": kind,
                          "payment_method": str(payment_method),
                          "saved_on_loss_notice": bool(saved_on_loss_notice),
                          "supply_points": tuple(supply_points) or (account_id,),
                          "cut_gbp": cut_gbp})

    @staticmethod
    def first_loss_after(row: dict, losses_notified) -> dict | None:
        """The earliest loss notice on the row's points effective AFTER its renewal, or None. A
        loss effective on the renewal day is the decision's own departure, already on the row."""
        later = [loss for loss in losses_notified or ()
                 if loss["supply_point_id"] in row["supply_points"]
                 and loss["supply_effective_from"] > row["event_date"]]
        return min(later, key=lambda loss: loss["supply_effective_from"], default=None)

    def closed_before(self, event_date: str, losses_notified=()) -> list[dict]:
        """Rows whose outcome the company knew before `event_date`, each with its `stayed` at the
        window. A row closes when the household left on the decision (known that day), when a loss
        notice inside the window had reached the company, or when the whole window had passed with
        none. With no window established, none closes."""
        window = self.outcome_window_days
        if window is None:
            return []
        closed = []
        for row in self.rows:
            if row["event_date"] >= event_date:
                continue
            if not row["stayed_at_decision"]:
                closed.append({**row, "stayed": False})
                continue
            end = (dt.date.fromisoformat(row["event_date"]) + dt.timedelta(days=window)).isoformat()
            loss = self.first_loss_after(row, losses_notified)
            if (loss is not None and loss["supply_effective_from"] <= end
                    and loss["notified_on"] < event_date):
                closed.append({**row, "stayed": False})
            elif end < event_date:
                closed.append({**row, "stayed": True})
        return closed

    def outcomes(self, losses_notified) -> list[dict]:
        """Every row with the days from its renewal to its first later loss (None: none notified),
        so the outcome at any window can be read off the run's artefact without re-running it."""
        result = []
        for row in self.rows:
            loss = self.first_loss_after(row, losses_notified) if row["stayed_at_decision"] else None
            result.append({**{k: v for k, v in row.items() if k != "supply_points"},
                           "days_to_later_loss": None if loss is None else (
                               dt.date.fromisoformat(loss["supply_effective_from"])
                               - dt.date.fromisoformat(row["event_date"])).days})
        return result

    def decide(self, *, account_id: str, event_date: str, payment_method: str | None,
               term_margin_gbp: float, term_billed_gbp: float, billed_kwh: float,
               cut_gbp_per_mwh: float, stay_belief: float | None,
               losses_notified=()) -> tuple[str, CutDecision | None]:
        """`(arm, decision)` for one renewal: `retention_cut_on_belief` on the published prior
        updated by the rows closed before today, at this term's own margin and the company's own
        stay belief. None -- the standing guard decides -- only where there is nothing to value (no
        billing, or no stay belief). It is read on BOTH arms, because whether a renewal belongs in
        the experiment (`would_offer`) must not depend on the coin."""
        arm = holdout_arm(account_id, event_date)
        if term_billed_gbp <= 0 or stay_belief is None:
            return arm, None
        belief = stay_per_pound(self.closed_before(event_date, losses_notified))
        return arm, retention_cut_on_belief(
            belief, stay_belief=stay_belief, term_margin_gbp=term_margin_gbp,
            cut_gbp=cut_gbp_per_mwh * billed_kwh / 1000.0)

    @staticmethod
    def would_offer(decision: CutDecision | None, standing_guard_offers: bool) -> bool:
        """Whether the company would offer at this renewal, read before its coin: the learned
        decision once there is one, else the standing guard. The held-out arm gets no offer and the
        treated arm gets it, but a row is due on either arm exactly when this is true."""
        return decision.offer_cut if decision is not None else bool(standing_guard_offers)
