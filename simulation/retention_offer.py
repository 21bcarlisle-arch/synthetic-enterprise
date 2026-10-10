"""The household's answer to a retention offer: the world re-asked at the OFFERED RATE, on its own roll.

REUSE: simulation/retention_offer.py
CLASS: CUSTOM
INDEX: searched "retention offer", "offered rate", "same roll". `simulation.save_on_loss_notice.
       household_takes_save` is the rule (a household leaving at one price stays at a lower one iff
       its own roll sits at or below P(stay | lower price), the price effect optionally scaled) and
       is REUSED here, not paralleled. What it lacks is the run's retention offer itself: the
       offered rate from the company's discount tier, and the event the run keeps when the offer
       is answered.

WHAT THIS REPLACED (director, 2026-10-09: "a factual correction, not a choice"). The run handed
the world `min(0.95, RETENTION_EFFECTIVENESS * framing)` with `RETENTION_EFFECTIVENESS = 0.20`,
unsourced, as a cut to the price-position hazard. The discount's SIZE never reached the world: a
3% and an 8% offer retained identically and differed only in cost. Measured
(`docs/staging/WORKER_FINDING_THE_RUNS_RETENTION_OFFER_REACHES_THE_WORLD_AS_A_FLAT_TWENTY_PERCENT_
WHATEVER_ITS_SIZE_2026-10-09.md`): the flat 0.20 gave +0.028 P(stay) at every tier, where the
world's own price response gives +0.018 / +0.029 / +0.042 at 3% / 5% / 8%.

WHO DECIDES. The world. `roll_lifecycle_event` is a pure function of the household's renewal roll
(`customer_events.churn_roll_for_renewal`, one per account per renewal) and the offered rate, so
re-asking it at the discounted rate with every other argument unchanged is the same household on
the same day answering a cheaper price. No retention probability is added.

FRAMING (Nudge Physics Layer 1) IS KEPT, ONLY AS WHAT IS SOURCED. `framing_effectiveness_multiplier`
is a "relative uplift in acceptance probability", 10-35% on a matched framing
(`docs/market_research/NUDGE_PHYSICS_BENCHMARKS.md`: Levin, Schneider & Gaeth 1998). The household
that ACCEPTS a retention offer is the one leaving at the full rate and staying at the offered one,
so the uplift scales exactly that mass, `P(stay | offered) - P(stay | full)`, on the same roll --
the `scale` of `household_takes_save`. A multiplier of 1 (neutral, or unmatched framing) is the
world's own answer at the offered rate, unscaled. The 0.20 it used to multiply is gone.
"""
from __future__ import annotations

from simulation.customer_events import churn_roll_for_renewal
from simulation.save_on_loss_notice import household_takes_save


def offered_rate(unit_rate: float, discount_pct: float) -> float:
    """The rate a retention offer at `discount_pct` puts in front of the household."""
    if not 0.0 <= discount_pct < 1.0:
        raise ValueError(f"a retention discount must be in [0, 1), got {discount_pct!r}")
    return unit_rate * (1.0 - discount_pct)


def stays_at_offer(roll: float, p_stay_full: float, p_stay_offered: float,
                   framing_multiplier: float = 1.0) -> bool:
    """Whether the household stays, on ITS OWN renewal roll: a stayer at the full rate stays, and a
    leaver stays iff the offered rate (its effect scaled by the sourced framing uplift) holds it."""
    return roll <= p_stay_full or household_takes_save(
        roll, p_stay_full, p_stay_offered, framing_multiplier)


def ask_world_at_offer(roll_fn, customer_id: str, term_start: str, commodity: str,
                       roll_kwargs: dict, full_event: dict | None, *, discount_pct: float,
                       framing_multiplier: float = 1.0) -> dict | None:
    """Re-ask the world's renewal decision at the offered rate, every other argument unchanged, and
    return the event the run keeps. `None` where the world rolled nothing at the full rate."""
    if full_event is None:
        return None
    offered = roll_fn(customer_id, term_start, commodity, **{
        **roll_kwargs, "new_rate_gbp_per_mwh": offered_rate(
            roll_kwargs["new_rate_gbp_per_mwh"], discount_pct)})
    return answer_retention_offer(full_event, offered, discount_pct=discount_pct,
                                  framing_multiplier=framing_multiplier)


def answer_retention_offer(full_event: dict, offered_event: dict, *,
                           discount_pct: float, framing_multiplier: float = 1.0) -> dict:
    """The renewal event the run keeps when a retention offer was made.

    `full_event` is the world asked at the undiscounted rate, `offered_event` the SAME call re-asked
    at `offered_rate(...)`. Both drew the household's one renewal roll, which is read again here
    from its source rather than from the rounded copy on the event. The pre-offer
    ground truth (`realized_churn_probability`, and the company's estimate error against it) is the
    full-rate event's: comparing the company's pre-offer belief against a probability that already
    holds its own discount would make it look wrong exactly when the offer worked (Phase QA).
    """
    roll = churn_roll_for_renewal(full_event["customer_id"], full_event["event_date"])
    p_full = full_event["effective_retention_probability"]
    p_offered = offered_event["effective_retention_probability"]
    stays = stays_at_offer(roll, p_full, p_offered, framing_multiplier)
    if stays and offered_event["event_type"] == "renewed":
        event = dict(offered_event)
    elif stays:
        # Held by the framing uplift alone: the unscaled world at the offered rate would have let it go.
        event = {**offered_event, "event_type": "renewed", "departure_cause": None}
    elif offered_event["event_type"] == "churned":
        event = dict(offered_event)
    else:
        event = dict(full_event)
    p_effective = min(1.0, p_full + framing_multiplier * (p_offered - p_full))
    event.update(
        effective_retention_probability=round(max(p_full, p_effective), 4),
        realized_churn_probability=full_event["realized_churn_probability"],
        company_churn_estimate=full_event["company_churn_estimate"],
        churn_estimate_error_pct=full_event["churn_estimate_error_pct"],
        retention_offered=True,
        retention_discount_pct=discount_pct,
        p_stay_without_offer=p_full,
        p_stay_at_offered_rate=p_offered,
    )
    return event
