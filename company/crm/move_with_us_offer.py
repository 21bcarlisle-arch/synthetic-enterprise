"""What the company offers our household when it tells us it is moving out: to move with us.

REUSE: company/crm/move_with_us_offer.py
CLASS: CUSTOM
INDEX: searched "move with us", "home mover", "retention", "save offer" under company/. The save
       (`company/crm/save_offer.py`) answers a switch AWAY by cutting the renewal price; a move-out is
       not a switch, the household is leaving its home, not us, and the offer is not a price cut but
       supply at its new home on the tariff it already holds. `saas/home_move_win_rate.py` values
       winning the NEXT occupant of the premises vacated, a different household.

WHAT THE OFFER IS (home_moves.md s.8.3): supply at the new premises on the tariff in force, carried
across, with the exit fee that ending the old contract would trigger waived. SLC 24.3 gives a mover no
exemption from a fixed-term exit fee, so the waiver is the supplier's lever, not an entitlement. THIS
WORLD CHARGES NO EXIT FEE ON A MOVE, so the waiver is carried on the offer as its term and costs
nothing here; that understates what a real waiver costs and is named rather than priced.

WHAT IT READS, AND ONLY THIS: the notice (`company/crm/move_out_register.py`), the tariff in force
(its unit rate and type), the cost the company struck that rate against (its own forward price
belief) and its own annual consumption estimate for the household. From those it forms its forward
value belief of carrying the household: the margin per year it expects on the carried tariff. It does
not know the destination premise's consumption (the notice does not carry the destination), so the
household's own consumption at its old home is the company's estimate, and is labelled as such.

THE RULE: offer when the company's own estimate says carrying the household earns a positive margin.
A positive margin per year is exactly when its forward value (`next_best_action.forward_value`, any
departure hazard below one) is positive, so the sign is all the rule needs; no horizon or hazard is
chosen. A default-tariff household is not offered: "carrying" a default tariff is supply at our
default tariff, which the incumbent at the new home already gives it on a deemed contract, and the
world's renewal roll that answers the offer is rolled only at a fixed term's end (named simplification).

THE DIRECTOR'S RULES, held in code below:
  * An offer may vary by acquisition route or time on the default tariff, never the renewal price.
    This offer varies by neither: it carries the price the household already pays.
  * Never paid for by raising stayers' prices: a run-level property, measured by
    `tools/move_with_us_arms.py`.
  * A known-vulnerable household is never offered less than its twin: `vulnerable` may only ever
    widen the offer. Today it changes nothing, so the twin is offered exactly the same.
"""
from __future__ import annotations

from dataclasses import dataclass

#: Why no offer was made, one spelling each, so the run's log can be counted by reason.
NO_POLICY = "the policy makes no move-with-us offer"
NOT_FIXED = "not on a fixed tariff: a default tariff is what the new home's incumbent already supplies"
NO_RATE = "no struck rate in force to carry"
NO_MARGIN = "on the company's own estimate, carrying the household earns no margin"


@dataclass(frozen=True)
class MoveWithUsOffer:
    supply_point_id: str
    move_out_date: str
    carried_unit_rate: float  # GBP/MWh, the tariff in force
    tariff_type: str
    exit_fee_waived: bool = True


def expected_margin_gbp_per_year(unit_rate_gbp_per_mwh: float, cost_gbp_per_mwh: float,
                                 annual_kwh: float) -> float:
    """The company's own estimate of the margin a year of supply on the carried tariff earns."""
    return (unit_rate_gbp_per_mwh - cost_gbp_per_mwh) * annual_kwh / 1000.0


def decide_move_with_us(notice, *, offers_on: bool, tariff_type: str,
                        unit_rate_per_mwh: float | None, cost_per_mwh: float | None,
                        annual_kwh: float | None, vulnerable: bool = False,
                        ) -> tuple[MoveWithUsOffer | None, str | None]:
    """(the offer, or None; the reason for None). `notice` is a filed `MoveOutNotice`."""
    if not offers_on:
        return None, NO_POLICY
    if tariff_type != "fixed":
        return None, NOT_FIXED
    if unit_rate_per_mwh is None or cost_per_mwh is None or annual_kwh is None:
        return None, NO_RATE
    margin = expected_margin_gbp_per_year(unit_rate_per_mwh, cost_per_mwh, annual_kwh)
    # `vulnerable` may only widen the offer. It does not today: the rule is the household's
    # position alone, so a known-vulnerable household is offered exactly what its twin is.
    del vulnerable
    if margin <= 0.0:
        return None, NO_MARGIN
    return MoveWithUsOffer(supply_point_id=notice.supply_point_id,
                           move_out_date=notice.move_out_date.isoformat(),
                           carried_unit_rate=unit_rate_per_mwh,
                           tariff_type=tariff_type), None
