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
