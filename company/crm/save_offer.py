"""What the company offers a household whose switch away it has just been told of.

REUSE: company/crm/save_offer.py
CLASS: CUSTOM
INDEX: searched "save offer", "retention tariff", "intervene". `company/crm/cos_process.CoSRegister`
       files the CSS Invitation to Intervene and says no decision reads it; this is that decision.
       The renewal desk's retention offer (`DecisionPolicy.retention_discount_for_risk`) is a
       proactive discount sized on a churn BELIEF before the roll; a save answers a notice after
       the household has chosen to go, so it shares neither its trigger nor its sizing.

THE FORM IS A FIXED RETENTION TARIFF (SLC 22B market-wide derogation, in force with the ban on
acquisition-only tariffs to 31 March 2027; save-offer note s.1d and s.6): fixed term, open only to
existing customers, aimed at keeping them. A variable discount offered only to leavers has no
derogation.

THE SIZE IS THE COMPANY'S AND IS NOT ESTABLISHED. No published or practitioner figure prices a
save (toggle q4_save_offer_cost_share_of_annual_bill, GAP; asked of the director in DIRECTION.yaml
row the-save-offer-needs-two-practitioner-figures). So the policy field is None unless an
experiment names a cut, and None offers nothing.

THE DIRECTOR'S RULES (2026-10-08), each held by code below rather than by this sentence:
  * A save may vary by acquisition route or time on the default tariff (`SAVE_MAY_VARY_BY`).
  * A vulnerable household is never offered less than a household in the same position that is
    not (`save_offer_rate`; `tests/company/crm/test_save_offer.py`).
  * A save is never paid for by raising a stayer's price. That is a property of the whole run, not
    of this function, so it is measured there (`tools/save_on_loss_notice_arms.py`).
"""
from __future__ import annotations

from dataclasses import dataclass

#: The only positions a save offer may be varied by (director, 2026-10-08). A renewal price may
#: vary by neither.
SAVE_MAY_VARY_BY: tuple[str, ...] = ("acquisition_route", "months_on_default")


@dataclass(frozen=True)
class SaveOffer:
    supply_point_id: str
    renewal_unit_rate: float  # GBP/MWh, as the renewal offer it replaces
    save_unit_rate: float
    tariff: str = "fixed_retention_tariff"



def _cut_share_for(cut_share: float, acquisition_route: str | None,
                   months_on_default: int | None) -> float:
    """The cut for a position, as a share of the renewal unit rate. Flat today: the policy names
    one share and no evidence yet says how it should vary, so it does not. The two position
    arguments are the only ones it may read."""
    del acquisition_route, months_on_default
    return cut_share


def save_offer_rate(renewal_unit_rate_gbp_per_mwh: float, cut_share: float, *,
                    acquisition_route: str | None = None, months_on_default: int | None = None,
                    vulnerable: bool = False) -> float:
    """The Fixed Retention Tariff's unit rate for a household in this position.

    `vulnerable` may only ever buy a larger cut. Today it buys the same one: the cut is sized by
    position alone, so a vulnerable household gets exactly what its non-vulnerable twin does."""
    del vulnerable
    share = _cut_share_for(cut_share, acquisition_route, months_on_default)
    return renewal_unit_rate_gbp_per_mwh * (1.0 - share)


def save_offer_on_invitation(pending_notice: dict, renewal_unit_rate_gbp_per_mwh: float | None,
                             cut_share: float | None, *, acquisition_route: str | None = None,
                             months_on_default: int | None = None,
                             vulnerable: bool = False) -> SaveOffer | None:
    """The offer the company makes on one Invitation to Intervene it holds, or None.

    None where the policy names no cut (the size is a GAP, see the module note) or the company
    struck no fixed rate to cut from: a save is a fixed tariff priced off the offer it replaces."""
    if cut_share is None or renewal_unit_rate_gbp_per_mwh is None:
        return None
    if not 0.0 < cut_share < 1.0:
        raise ValueError(f"a save's cut share must lie in (0, 1), got {cut_share!r}: a zero cut is "
                         "never offering, which is the arm it is graded against")
    return SaveOffer(
        supply_point_id=pending_notice["supply_point_id"],
        renewal_unit_rate=renewal_unit_rate_gbp_per_mwh,
        save_unit_rate=save_offer_rate(
            renewal_unit_rate_gbp_per_mwh, cut_share, acquisition_route=acquisition_route,
            months_on_default=months_on_default, vulnerable=vulnerable),
    )
