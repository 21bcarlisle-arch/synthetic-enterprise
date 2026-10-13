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

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

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


#: The published best-deal gap a price match is sized on. Published market data a real supplier
#: reads, so it lives in the commons beside the cap windows and is read here, on the company's side;
#: until 2026-10-12 it was a table in `simulation/save_on_loss_notice.py`, handed in by the run loop.
_BEST_DEAL_GAP_COMMONS = (
    Path(__file__).resolve().parents[2]
    / "docs" / "domain_artefact_library" / "regulatory" / "gb_best_deal_gap_to_default.json"
)
_ACCEPTED_PROVENANCE = ("primary", "secondary")


@lru_cache(maxsize=1)
def _published_best_deal_gaps() -> dict[str, float]:
    """`{"YYYY-Qn": gap share}` from the commons. A missing or malformed artefact, or an entry
    nobody fetched, raises: a quiet empty table would read as "no deal beat the default" and
    silently withdraw every price match."""
    raw = json.loads(_BEST_DEAL_GAP_COMMONS.read_text())
    out: dict[str, float] = {}
    for row in raw["quarters"]:
        if row.get("provenance") not in _ACCEPTED_PROVENANCE:
            raise ValueError(f"{_BEST_DEAL_GAP_COMMONS}: {row.get('quarter')} has provenance "
                             f"{row.get('provenance')!r}; an unfetched figure is not the record")
        gap = float(row["gap_share"])
        if not 0.0 <= gap < 1.0:
            raise ValueError(f"{_BEST_DEAL_GAP_COMMONS}: {row['quarter']} gap {gap} is not a share")
        out[row["quarter"]] = gap
    if not out:
        raise ValueError(f"{_BEST_DEAL_GAP_COMMONS} carries no quarters")
    return out


def published_best_deal_gap_share(date_str: str) -> float | None:
    """The published best-deal gap for the quarter holding `date_str`, or None if not established."""
    year, month = int(date_str[:4]), int(date_str[5:7])
    return _published_best_deal_gaps().get(f"{year}-Q{(month - 1) // 3 + 1}")


def published_default_rate_ex_vat(commodity: str, date_str: str) -> float | None:
    """The published default tariff for this fuel on this day, EX VAT and EPG-net -- the basis
    every rate the price match compares it with is on, and the one the churn belief reads
    (`renewal_rate_chain.cap_ceiling_ex_vat`, single-rate). None for a fuel with no cap.

    2026-10-13: the run handed the match `simulation.svt_rates`, which is INC VAT and the gross cap
    through the EPG, against an ex-VAT re-fix and floor. The market's best deal read 5% dear, so
    both desks under-offered: on 2024-Q3 a re-fix at the cap got no save at all (gap 3.7% < VAT)."""
    if commodity not in ("electricity", "gas"):
        return None
    from datetime import date

    from company.pricing.renewal_rate_chain import cap_ceiling_ex_vat
    return cap_ceiling_ex_vat(commodity, date.fromisoformat(date_str[:10]), multi_register=False)


def price_match_save_rate(renewal_unit_rate_gbp_per_mwh: float | None,
                          published_default_rate_gbp_per_mwh: float | None,
                          best_deal_gap_share: float | None,
                          cost_floor_gbp_per_mwh: float | None) -> float | None:
    """The save as a PRICE MATCH: the market's best published deal, never below our own cost.

    WHY THIS SHAPE (2026-10-10, director: "make the reactive save on the loss notice a live
    supplier capability"). A household on a loss notice is leaving for a cheaper deal, and a
    retention desk's save meets that deal where it can afford to. Every input is something a
    supplier holds: the published default tariff for the fuel, the published gap between the
    cheapest deal on the market and that default, and the cost floor of the rate it struck itself.

    CORRECTED 2026-10-11, beside the claim it replaces ("No size is chosen here"): the MATCH IS A
    DESIGN CHOICE WITH NO PUBLISHED BASIS. No rule or documented GB practice prices a save as a
    match to the market's best deal (SLC 22B's derogation leaves a retention tariff's depth
    unregulated; the nearest precedent, CMA 2016 §279, is a discount off the supplier's OWN default).
    The published gap sizes what is matched; it does not say matching is how a save is sized. The
    reasoning is a practitioner's -- a leaver is leaving for something cheaper, matching it is the
    least that answers the reason, the floor stops a guaranteed loss -- and is stated as such in
    docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md §7d, with the
    alternatives the evidence would allow.

    None -- no offer -- where any input is missing, where the market had nothing cheaper than the
    default (a gap at or below zero, as through 2022), or where the match would not beat the
    renewal it replaces. Position-free, so a household the company knows to be vulnerable is
    offered exactly what its twin is (the director's rule: never less)."""
    if None in (renewal_unit_rate_gbp_per_mwh, published_default_rate_gbp_per_mwh,
                best_deal_gap_share, cost_floor_gbp_per_mwh) or best_deal_gap_share <= 0.0:
        return None
    match = max(cost_floor_gbp_per_mwh, published_default_rate_gbp_per_mwh * (1.0 - best_deal_gap_share))
    return match if match < renewal_unit_rate_gbp_per_mwh else None


def save_offer_on_invitation(pending_notice: dict, renewal_unit_rate_gbp_per_mwh: float | None,
                             cut_share: float | None, *, acquisition_route: str | None = None,
                             months_on_default: int | None = None,
                             vulnerable: bool = False,
                             price_match_rate: float | None = None) -> SaveOffer | None:
    """The offer the company makes on one Invitation to Intervene it holds, or None.

    An experiment's explicit `cut_share` sizes the save when it names one; otherwise the standing
    price match (`price_match_save_rate`, computed by the door from what the company holds) does.
    None where neither gives a rate, or the company struck no fixed rate to cut from: a save is a
    fixed tariff priced off the offer it replaces."""
    if renewal_unit_rate_gbp_per_mwh is None:
        return None
    if cut_share is None:
        if price_match_rate is None:
            return None
        return SaveOffer(supply_point_id=pending_notice["supply_point_id"],
                         renewal_unit_rate=renewal_unit_rate_gbp_per_mwh,
                         save_unit_rate=price_match_rate)
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
