"""The household's answer to a save offer made on the CSS Invitation to Intervene.

REUSE: simulation/save_on_loss_notice.py
CLASS: CUSTOM
INDEX: searched "save offer", "loss notice", "saved_on". `simulation.coin_drawn_decision_set.
       saved_on_loss_notice` is the rule (a leaver at the offer is saved iff its roll is at or below
       P(stay | save price)) and is REUSED here, not paralleled; `tools.grade_save_offer_shapes`
       owns the response scale this module applies to the settled run. What neither has is the
       curriculum switch and the settled run's own facts: which departures send the loser an
       Invitation at all, and the roll the run itself drew.

WHO DECIDES. The world. The renewal roll is `customer_events.churn_roll_for_renewal`, one draw per
account per renewal, and `roll_lifecycle_event` is a pure function of it and the offered rate. So
re-asking that function at the save price, with every other argument unchanged, is the same
household on the same day answering a cheaper price. No save probability is added: the published
save rate (q4_save_rate_on_loss_notice) is what the world's OUTPUT is checked against.

WHICH DEPARTURES CAN BE SAVED. Only a switch that sends the loser an Invitation to Intervene
(`registration_loss_seam.emits_pending_notice`: requests submitted from CSS go-live, 18 July 2022).
Before that the seam carries no notice in time to answer, so nothing is saved, though a real
pre-CSS loser was told of a switch in its objection window. That is a gap of the seam, named there
(`GAPS`), and it can only understate the save.

NAMED SIMPLIFICATIONS:
  * Departures from a FIXED term at its renewal point only. A household leaving the default tariff
    (C1b's inertia hazard, or a passive renewer rolled onto it) is not offered a save: whether a
    Fixed Retention Tariff offered to a default-tariff household sits inside the SLC 22B derogation
    is NOT ESTABLISHED (save-offer note s.1d).
  * The cut is on the departure decision leg's rate, the only price the world's roll weighs. A
    dual-fuel household's other leg keeps its offer; cutting it would buy nothing in this world.
"""
from __future__ import annotations

import json
from pathlib import Path

from simulation.coin_drawn_decision_set import saved_on_loss_notice

ACTIVATION_PATH = (Path(__file__).resolve().parents[1]
                   / "docs" / "design" / "curriculum" / "save_on_loss_notice_activation.json")


def _activation(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def save_offers_active(path: Path = ACTIVATION_PATH) -> bool:
    """Whether households in this run answer a save offer. A non-bool raises: on or off is the
    director's, and neither may be inferred from a file that does not say."""
    value = _activation(path)["activated"]["value"]
    if not isinstance(value, bool):
        raise ValueError(f"{path}: activated.value must be true or false, got {value!r}")
    return value


def world_save_response_scale(path: Path = ACTIVATION_PATH) -> float:
    """The sensitivity on the world's response to the save's price (1.0 is the world itself)."""
    value = _activation(path)["world_save_response_scale"]["value"]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{path}: world_save_response_scale.value must be a number >= 0, "
                         f"got {value!r}")
    return float(value)


def household_takes_save(roll: float, p_stay_at_offer: float, p_stay_at_save: float,
                         scale: float = 1.0) -> bool:
    """Whether a household leaving at the renewal offer stays at the save price, on its own roll.

    `scale` multiplies the save's effect on P(stay) (`world_save_response_scale`); at 1.0 this is
    exactly the world's own answer at the save price, and at 0 nobody is saved."""
    scaled = min(1.0, p_stay_at_offer + scale * (p_stay_at_save - p_stay_at_offer))
    return saved_on_loss_notice(roll, p_stay_at_offer, scaled)


def billed_rate_when_saved(renewal_unit_rate: float, save_unit_rate: float) -> float:
    """What a saved household is billed: the save's price. Named so the PLACEBO arm
    (`tools/save_on_loss_notice_arms.py`) can bill the same saves at the renewal price, which holds
    the book's composition fixed and leaves the save's price as the only difference."""
    del renewal_unit_rate
    return save_unit_rate


#: The gap between the cheapest deal on the market and the default tariff, as a share of the typical
#: default bill, by quarter ("YYYY-Qn"). PUBLISHED DATA a supplier can read (Ofgem retail market
#: indicators), handed to the company's save door as a plain value -- the observable a price-match
#: save is sized on (`company.crm.save_offer.price_match_save_rate`). Source: Ofgem RMI "Retail
#: price comparison by company and tariff type: Domestic (GB)", "cheapest tariff (all suppliers)"
#: against the default, read 2026-10-10 (`docs/market_research/
#: cheapest_fix_against_the_default_tariff_gb_2016_2025.md`). A quarter not listed is None, which
#: offers nothing. Each is the quarter's first-month reading; the default is the large-legacy SVT
#: average until 2018 and the cap level from 2019, as the series itself switches.
#:
#: The pre-CSS quarters (2026-10-11) are read by the RENEWAL desk's price match (B8 Q5,
#: `company.interfaces.growth_desk.retention_cut_share_at_price_match`). No save reads them: a
#: switch before 2022-07-18 sends no Invitation to Intervene, so no save is offered there at all.
PUBLISHED_BEST_DEAL_GAP_SHARE: dict[str, float] = {
    "2016-Q1": 0.303, "2016-Q2": 0.321, "2016-Q3": 0.289, "2016-Q4": 0.304,
    "2017-Q1": 0.214, "2017-Q2": 0.231, "2017-Q3": 0.261, "2017-Q4": 0.272,
    "2018-Q1": 0.287, "2018-Q2": 0.308, "2018-Q3": 0.302, "2018-Q4": 0.246,
    "2019-Q1": 0.172, "2019-Q2": 0.298, "2019-Q3": 0.325, "2019-Q4": 0.267,
    "2020-Q1": 0.310, "2020-Q2": 0.327, "2020-Q3": 0.301, "2020-Q4": 0.210,
    "2021-Q1": 0.176, "2021-Q2": 0.246,
    # July 2021's cheapest (GBP 858.59) is the penny figure of Jan-Apr; by August the gap was 9.3%
    # and the average fix already sat above the default. Kept at the method's reading, flagged.
    "2021-Q3": 0.246,
    # 2021 Q4 - 2022 Q2: 0.0, the same absence as the window below. The cheapest column is stale to
    # the penny from October 2021 and the average fix ran 64-54% above the default.
    "2021-Q4": 0.0, "2022-Q1": 0.0, "2022-Q2": 0.0,
    # 2022 Q3 - 2023 Q2: 0.0, ESTABLISHED as an absence, not missing. The series' "cheapest tariff"
    # repeats to the penny for six months at a time (stale, carried forward), while its "average
    # fixed tariff" -- everything on sale -- ran 54-133% ABOVE the default and no fix was quoted
    # at all Oct 2022 - May 2023. Nothing undercut the default, so no save is offered.
    "2022-Q3": 0.0, "2022-Q4": 0.0, "2023-Q1": 0.0, "2023-Q2": 0.0,
    # From 2023 Q3, quarterly cap cadence: the quarter's first-month reading, gap / default bill.
    "2023-Q3": 0.048, "2023-Q4": 0.039,
    "2024-Q1": 0.091, "2024-Q2": 0.089, "2024-Q3": 0.037, "2024-Q4": 0.088,
    "2025-Q1": 0.063, "2025-Q2": 0.140, "2025-Q3": 0.110, "2025-Q4": 0.150,
}


def published_best_deal_gap_share(date_str: str) -> float | None:
    """The published best-deal gap for the quarter holding `date_str`, or None if not established."""
    year, month = int(date_str[:4]), int(date_str[5:7])
    return PUBLISHED_BEST_DEAL_GAP_SHARE.get(f"{year}-Q{(month - 1) // 3 + 1}")
