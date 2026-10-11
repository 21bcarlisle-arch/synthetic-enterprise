"""The household's answer to a move-with-us offer made on its move-out notice.

REUSE: simulation/move_with_us_answer.py
CLASS: CUSTOM
INDEX: searched "save offer", "take up", "move with us". `simulation/save_on_loss_notice.py` is the
       template (curriculum switch, a scaled response on the household's own renewal roll); its
       scale is applied to a price CUT's effect on P(stay), and a move-with-us offer cuts no price,
       so the scale here is applied to P(stay) itself. Its own module because its activation and
       its population (movers, not switchers) are the director's separately.

WHO DECIDES. The world. No take-up rate of a move-with-us offer is published (home_moves.md s.8.5
G8.4), so none is invented. The household answers on the roll of its NEXT decision with us, against
the world's own P(stay) at the tariff it would carry (home_moves.md s.8.6, choice 2):
  * ON A FIXED TERM: the roll of its next renewal (`customer_events.churn_roll_for_renewal`) against
    the P(stay) the world rolled its renewal ONTO that tariff against (`effective_retention_
    probability` on the renewal event of the term in force).
  * ON THE DEFAULT TARIFF (2026-10-11): the roll of its next default-tariff segment (the run's
    `svt_inertia_<household>_<date>` seed) against the current segment's stay, annualised over the
    segment's own days, `(1 - p) ** (365.25 / days)` (`p_stay_on_default_tariff`). Annualised so a
    quarter's stay is not read as a year's. From the seat-executor's preserved build
    (`/var/tmp/mwu/patch/`), whose "origin's twin" destination is not taken.

`k` (`take_up_scale`) scales that P(stay): k = 0 nobody moves with us, k = 1 a mover stays as often
as a renewing household at that price. It is a labelled sensitivity, never a calibration.

WHO CAN ANSWER. A household whose term in force was entered through a rolled renewal, or whose
current default-tariff segment the world decided. A household still in its first fixed term has no
such P(stay); it is logged as unanswerable with that reason and does not move with us. That can only
understate take-up, and it is counted.
"""
from __future__ import annotations

import json
from pathlib import Path

ACTIVATION_PATH = (Path(__file__).resolve().parents[1]
                   / "docs" / "design" / "curriculum" / "move_with_us_activation.json")

NOT_ANSWERABLE = ("the term in force was not entered through a rolled renewal or a decided "
                  "default-tariff segment, so the world holds no P(stay) at the carried tariff")


def p_stay_on_default_tariff(p_depart_over_segment: float, segment_days: int) -> float:
    """The annual stay a default-tariff segment's decision implies."""
    if not 0.0 <= p_depart_over_segment <= 1.0:
        raise ValueError(f"a departure probability must lie in [0, 1], got {p_depart_over_segment}")
    if segment_days <= 0:
        raise ValueError(f"a segment needs at least one day, got {segment_days}")
    return (1.0 - p_depart_over_segment) ** (365.25 / segment_days)


def default_tariff_roll(household: str, next_segment_start: str) -> float:
    """The roll of the household's next default-tariff segment, on the run's own seed form."""
    import random

    return random.Random(f"svt_inertia_{household}_{next_segment_start}").random()


def _activation(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def move_with_us_active(path: Path = ACTIVATION_PATH) -> bool:
    """Whether households in this run answer a move-with-us offer. A non-bool raises."""
    value = _activation(path)["activated"]["value"]
    if not isinstance(value, bool):
        raise ValueError(f"{path}: activated.value must be true or false, got {value!r}")
    return value


def take_up_scale(path: Path = ACTIVATION_PATH) -> float:
    """k, the sensitivity on P(stay) a mover answers with (see the module note)."""
    value = _activation(path)["take_up_scale"]["value"]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{path}: take_up_scale.value must be a number in [0, 1], got {value!r}")
    return float(value)


def household_moves_with_us(next_renewal_roll: float, p_stay_at_carried: float, k: float) -> bool:
    """Whether the household takes the offer: its next renewal's roll against k * P(stay)."""
    if not 0.0 <= k <= 1.0:
        raise ValueError(f"k must lie in [0, 1], got {k!r}")
    # `k > 0` first, so k = 0 is nobody even on a roll of exactly 0.0.
    return k > 0.0 and next_renewal_roll <= k * p_stay_at_carried
