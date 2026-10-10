"""The company's MOVE-WITH-US door: what it offers our household that has told it it is moving out.

REUSE: company/interfaces/move_with_us.py
CLASS: CUSTOM
INDEX: searched "save offer", "move", "retention" under company/interfaces/. `save_offer.py` answers
       a CSS Invitation to Intervene from the change-of-supplier register; this answers a move-out
       notice from the move-out register, so it is its own door as that one's note asks of every
       decision.

In: the company's own move-out register (which holds the notice the household sent), the point and
move date the world is asking about, the tariff in force, the cost the company struck it against,
its own consumption estimate, and its Priority Services Register. Out: the offer or None, whether the
company knew the household to be vulnerable, and the reason for None. The decision is
`company/crm/move_with_us_offer.py`.

VULNERABILITY IS WHAT THE HOUSEHOLD DISCLOSED, as at the save's door: registered on or before the
notice, in the company's own register, or not known.
"""
from __future__ import annotations

from company.crm.move_out_register import MoveOutRegister
from company.crm.move_with_us_offer import MoveWithUsOffer, decide_move_with_us
from company.regulatory.priority_services_register import PriorityServicesRegister

__all__ = ["NO_NOTICE", "request_move_with_us_offer"]

NO_NOTICE = "no move-out notice held for this point and date"


def request_move_with_us_offer(
    register: MoveOutRegister, supply_point_id: str, move_out_date: str, *, offers_on: bool,
    tariff_type: str, unit_rate_per_mwh: float | None, cost_per_mwh: float | None,
    annual_kwh: float | None, psr_register: PriorityServicesRegister | None = None,
) -> tuple[MoveWithUsOffer | None, bool, str | None]:
    """(the offer or None; whether the company knew the household to be vulnerable; why None)."""
    notice = register.notice_for(supply_point_id, move_out_date)
    record = None if psr_register is None else psr_register.get_record(supply_point_id)
    vulnerable = (record is not None and notice is not None
                  and record.registration_date <= notice.notified_on)
    if notice is None:
        return None, vulnerable, NO_NOTICE
    offer, reason = decide_move_with_us(
        notice, offers_on=offers_on, tariff_type=tariff_type,
        unit_rate_per_mwh=unit_rate_per_mwh, cost_per_mwh=cost_per_mwh,
        annual_kwh=annual_kwh, vulnerable=vulnerable)
    return offer, vulnerable, reason
