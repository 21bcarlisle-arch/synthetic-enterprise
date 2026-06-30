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
