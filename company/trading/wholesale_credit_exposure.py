"""Wholesale Credit Exposure Register (Phase DY).

When an energy supplier buys forward contracts, it is exposed to counterparty
credit risk: if the counterparty (bank, generator, trader) defaults before
delivery, the supplier loses the mark-to-market value of those contracts.

Key concepts for UK wholesale energy markets:
- ISDA Master Agreement + CSA (Credit Support Annex): governs collateral
- Initial Margin: posted upfront, returned at contract close
- Variation Margin: marked-to-market daily; call if MtM goes against you
- Netting: ISDA netting means all trades with same counterparty netted before
  calculating credit exposure
- Credit Limit: board-approved maximum exposure per counterparty
- Mark-to-market (MtM): current replacement cost if counterparty defaults now

UK-specific: ICE Endex OTC clearing (cleared through LCH); bilateral OTC
trades have no CCP backing — higher credit risk. Clearing mandated under
EMIR for standardised contracts.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class CounterpartyType(str, Enum):
    MAJOR_BANK = "major_bank"
    ENERGY_TRADER = "energy_trader"
    GENERATOR = "generator"
    CLEARING_HOUSE = "clearing_house"
    AGGREGATOR = "aggregator"


class ClearingStatus(str, Enum):
    CLEARED_CCP = "cleared_ccp"        # CCP-cleared; lower credit risk
    BILATERAL_ISDA = "bilateral_isda"  # OTC bilateral
    UNCONFIRMED = "unconfirmed"


class CounterpartyCreditRating(str, Enum):
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB_OR_LOWER = "BB_or_lower"
    UNRATED = "unrated"


_CREDIT_LIMIT_BY_RATING: Dict[CounterpartyCreditRating, float] = {
    CounterpartyCreditRating.AAA: 5_000_000.0,
    CounterpartyCreditRating.AA: 3_000_000.0,
    CounterpartyCreditRating.A: 2_000_000.0,
    CounterpartyCreditRating.BBB: 1_000_000.0,
    CounterpartyCreditRating.BB_OR_LOWER: 250_000.0,
    CounterpartyCreditRating.UNRATED: 100_000.0,
}

_CLEARED_EXPOSURE_HAIRCUT = 0.10     # CCP-cleared: 10% of MtM counts (collateral covers most)


@dataclass(frozen=True)
class WholesaleCreditRecord:
    counterparty_id: str
    counterparty_type: CounterpartyType
    credit_rating: CounterpartyCreditRating
    clearing_status: ClearingStatus
    gross_mtm_gbp: float
    collateral_held_gbp: float
    credit_limit_override_gbp: Optional[float] = None

    @property
    def net_exposure_gbp(self) -> float:
        raw = self.gross_mtm_gbp - self.collateral_held_gbp
        if self.clearing_status == ClearingStatus.CLEARED_CCP:
            raw *= _CLEARED_EXPOSURE_HAIRCUT
        return max(0.0, raw)

    @property
    def credit_limit_gbp(self) -> float:
        if self.credit_limit_override_gbp is not None:
            return self.credit_limit_override_gbp
        return _CREDIT_LIMIT_BY_RATING[self.credit_rating]

    @property
    def utilisation_pct(self) -> float:
        if self.credit_limit_gbp <= 0:
            return 0.0
        return self.net_exposure_gbp / self.credit_limit_gbp * 100

    @property
    def is_limit_breached(self) -> bool:
        return self.net_exposure_gbp > self.credit_limit_gbp

    @property
    def headroom_gbp(self) -> float:
        return max(0.0, self.credit_limit_gbp - self.net_exposure_gbp)


class WholesaleCreditExposureRegister:
    """Board-level view of all wholesale counterparty credit exposures."""

    def __init__(self) -> None:
        self._records: Dict[str, WholesaleCreditRecord] = {}

    def register(self, record: WholesaleCreditRecord) -> WholesaleCreditRecord:
        self._records[record.counterparty_id] = record
        return record

    def get(self, counterparty_id: str) -> Optional[WholesaleCreditRecord]:
        return self._records.get(counterparty_id)

    def all_records(self) -> List[WholesaleCreditRecord]:
        return list(self._records.values())

    def limit_breaches(self) -> List[WholesaleCreditRecord]:
        return [r for r in self._records.values() if r.is_limit_breached]

    def cleared_records(self) -> List[WholesaleCreditRecord]:
        return [r for r in self._records.values()
                if r.clearing_status == ClearingStatus.CLEARED_CCP]

    def bilateral_records(self) -> List[WholesaleCreditRecord]:
        return [r for r in self._records.values()
                if r.clearing_status == ClearingStatus.BILATERAL_ISDA]

    def total_net_exposure_gbp(self) -> float:
        return sum(r.net_exposure_gbp for r in self._records.values())

    def total_collateral_held_gbp(self) -> float:
        return sum(r.collateral_held_gbp for r in self._records.values())

    def largest_exposure(self) -> Optional[WholesaleCreditRecord]:
        if not self._records:
            return None
        return max(self._records.values(), key=lambda r: r.net_exposure_gbp)

    def credit_exposure_summary(self) -> str:
        n = len(self._records)
        n_breach = len(self.limit_breaches())
        total = self.total_net_exposure_gbp()
        collateral = self.total_collateral_held_gbp()
        return (
            f"Wholesale Credit Exposure: {n} counterparties. "
            f"Total net exposure: £{total:,.0f}. "
            f"Collateral held: £{collateral:,.0f}. "
            f"Limit breaches: {n_breach}. "
            f"ISDA/CSA governs bilateral OTC; EMIR clearing mandate."
        )


# --- VALUE_CHAIN BUILD ladder step 2: the live feed (2026-07-24) ---
# A CCP-cleared position carries no per-name credit limit — the clearing house's default
# waterfall (initial margin + default fund + skin-in-the-game) absorbs a member default,
# so a supplier does not set a bilateral-style credit line against ICE Clear Europe / LCH.
# The register still counts CCP *net* exposure (haircut by _CLEARED_EXPOSURE_HAIRCUT) but it
# can never breach a per-name limit. Expressed as a large finite override (JSON-safe, unlike
# float('inf')) rather than a rating-band cap, which would false-breach a big cleared book.
_CCP_NO_PER_NAME_LIMIT_GBP = 1e15


def build_credit_register_from_exposure(
    exposure_by_counterparty: Dict[str, dict],
) -> "WholesaleCreditExposureRegister":
    """Populate a WholesaleCreditExposureRegister from the trading book's live feed.

    VALUE_CHAIN BUILD ladder step 2 — the feed transform. Input is the exact output of
    ``company.trading.forward_book.TradingBook.exposure_by_counterparty(prices)`` (ISDA-netted
    per-counterparty MtM credit exposure at a point-in-time forward-price snapshot). This is a
    PURE transform (no I/O, no clock, deterministic) so a replay of the same exposure reproduces
    an identical register (C-S2). It is wall-clean: every input field is the company's OWN book
    (netted MtM of its own positions) or a PUBLIC agency rating band — no simulation internal.

    Mapping decisions (each an R10-flagged modelling choice, not a sourced figure):
    - ``gross_credit_exposure_gbp`` (already ``max(0, netted)`` under ISDA netting) → the record's
      ``gross_mtm_gbp``. An out-of-the-money net position (company owes) is zero credit exposure.
    - ``collateral_held_gbp`` = 0.0 here — CSA collateral/variation-margin postings are modelled by
      the observation-window step (ladder step 3), not this feed. NAMED SIMPLIFICATION: this feed
      reports GROSS-of-collateral bilateral exposure; it is an upper bound on the true net line.
    - CCP-cleared rows (``counterparty_rating is None``) get ``_CCP_NO_PER_NAME_LIMIT_GBP`` as a
      limit override (no per-name limit — the default waterfall absorbs) and a nominal AAA rating
      slot only to satisfy the required field; the override, not the rating, governs the limit.
    - The ``"UNATTRIBUTED"`` bucket (contracts opened with no counterparty — a wiring regression the
      book's ``counterparty_distribution().unattributed_count`` self-check already surfaces) is
      SKIPPED: it has no counterparty identity/rating to form a credit record from.

    Returns a freshly-built register (does not mutate any shared state).
    """
    register = WholesaleCreditExposureRegister()
    for cp_id, entry in exposure_by_counterparty.items():
        if cp_id == "UNATTRIBUTED":
            continue
        type_val = entry.get("counterparty_type")
        clearing_val = entry.get("clearing_status")
        if type_val is None or clearing_val is None:
            # No counterparty identity → not a formable credit record (same class as UNATTRIBUTED).
            continue
        counterparty_type = CounterpartyType(type_val)
        clearing_status = ClearingStatus(clearing_val)
        rating_val = entry.get("counterparty_rating")
        if rating_val is None:
            # CCP-cleared: no per-name rating/limit.
            credit_rating = CounterpartyCreditRating.AAA
            limit_override: Optional[float] = _CCP_NO_PER_NAME_LIMIT_GBP
        else:
            credit_rating = CounterpartyCreditRating(rating_val)
            limit_override = None
        register.register(
            WholesaleCreditRecord(
                counterparty_id=cp_id,
                counterparty_type=counterparty_type,
                credit_rating=credit_rating,
                clearing_status=clearing_status,
                gross_mtm_gbp=float(entry.get("gross_credit_exposure_gbp", 0.0)),
                collateral_held_gbp=0.0,
                credit_limit_override_gbp=limit_override,
            )
        )
    return register
