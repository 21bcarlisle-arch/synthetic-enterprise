"""The company's SAVE-OFFER door: what it offers a household whose switch away it has been told of.

REUSE: company/interfaces/save_offer.py
CLASS: CUSTOM
INDEX: searched "save offer", "intervene", "retention tariff" under company/interfaces/. The
       renewal-offer door (`renewal_offer.py`) answers a renewal before the household decides; this
       answers a notice after it has decided to go, from the company's own change-of-supplier
       register, so it is a separate door as that module's note asks of every decision.

In: the company's own register (which holds the Invitation to Intervene the world sent it), the
supply point and effective date the world is asking about, and the rate the company itself struck
for the renewal being left. Out: one number, the Fixed Retention Tariff's unit rate, or None when
the company makes no offer. The decision is `company/crm/save_offer.py`.

THE PUBLISHED BEST-DEAL GAP is read through this door (`published_best_deal_gap_share`), from the
commons (`docs/domain_artefact_library/regulatory/gb_best_deal_gap_to_default.json`): published
market data, so the company's to read, and the save and the renewal cut read the one copy.

VULNERABILITY IS WHAT THE HOUSEHOLD DISCLOSED. The company's Priority Services Register holds a
record only for a household that told it (`interface/contracts/psr_registration_seam.py`), so a
household is offered as vulnerable iff its point is registered on or before the switch it is
answering. With no register (the hidden state off) every household is offered as one the company
does not know to be vulnerable. The desk's rule that a vulnerable household is never offered less
is held there and tested there; the run-level twin check is `tools/save_on_loss_notice_arms.py`.
"""
from __future__ import annotations

from company.crm.cos_process import CoSRegister
from company.crm.save_offer import (
    price_match_save_rate,
    published_best_deal_gap_share,
    save_offer_on_invitation,
)
from company.regulatory.priority_services_register import PriorityServicesRegister

__all__ = ["published_best_deal_gap_share", "request_save_offer"]


def request_save_offer(register: CoSRegister, supply_point_id: str, supply_effective_from: str,
                       renewal_unit_rate: float | None, cut_share: float | None,
                       psr_register: PriorityServicesRegister | None = None, *,
                       sizing: str | None = None,
                       published_default_rate: float | None = None,
                       published_best_deal_gap_share: float | None = None,
                       cost_floor: float | None = None,
                       ) -> tuple[float | None, bool]:
    """(the save's unit rate for this point's pending switch, or None; whether the company knew
    the household to be vulnerable when it answered). None where no Invitation is held, there is no
    fixed rate to cut from, or the policy names no save. `cut_share` and `sizing` are the run's
    policy's (`DecisionPolicy.save_offer_cut_share`, `.save_offer_sizing`), handed in by the run
    that holds it. Under `sizing == "price_match"` the three published or company-held values size
    the save (`company.crm.save_offer.price_match_save_rate`): plain values, as at the renewal door."""
    record = None if psr_register is None else psr_register.get_record(supply_point_id)
    vulnerable = (record is not None
                  and record.registration_date.isoformat() <= supply_effective_from)
    held = [n for n in register.pending_switches_notified()
            if n["supply_point_id"] == supply_point_id
            and n["supply_effective_from"] == supply_effective_from]
    if not held:
        return None, vulnerable
    match = (price_match_save_rate(renewal_unit_rate, published_default_rate,
                                   published_best_deal_gap_share, cost_floor)
             if sizing == "price_match" else None)
    offer = save_offer_on_invitation(held[-1], renewal_unit_rate,
                                     cut_share, vulnerable=vulnerable, price_match_rate=match)
    return (None if offer is None else offer.save_unit_rate), vulnerable
