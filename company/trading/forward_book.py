"""Company Trading Desk — Forward Position Lifecycle (Phase 43a).

The company's trading book tracks electricity forward contracts opened at tariff
signing. This is the first full SIM/company separation for hedging: the SIM no
longer decides what hedge fraction to apply — the company's trading desk does,
and the SIM settles against the company's actual positions.

Epistemic constraint: every decision here uses only company-observable data
(company forward price, portfolio exposure, own P&L records, observable spot prices).
No simulation internals are accessed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NamedTuple


@dataclass(frozen=True)
class ForwardContract:
    """A single OTC forward contract opened at supply term signing.

    agreed_price_gbp_per_mwh: the company forward price at the time the tariff
        was priced (observable: from company's own tariff engine, which uses
        published forward market data only).
    notional_mwh: hedged volume — EAC × hedge_fraction / 1000.
    """

    customer_id: str
    term_start: str          # ISO date string
    term_end: str            # ISO date string
    notional_mwh: float
    agreed_price_gbp_per_mwh: float
    hedge_fraction: float


class HedgePnL(NamedTuple):
    hedged_mwh: float
    pnl_gbp: float           # positive = hedge won (forward > spot), negative = hedge lost


class TradingBook:
    """Tracks all open forward contracts and cumulative P&L.

    Used in run_phase2b.py: one TradingBook instance per full simulation run,
    shared across all customers and years.
    """

    def __init__(self) -> None:
        self._contracts: list[ForwardContract] = []
        self._total_pnl_gbp: float = 0.0
        self._total_hedged_mwh: float = 0.0

    def open_hedge(self, contract: ForwardContract) -> None:
        """Register a new forward contract when a supply term is signed."""
        self._contracts.append(contract)

    def settle_period(
        self,
        customer_id: str,
        term_start: str,
        consumed_kwh: float,
        actual_spot_gbp_per_mwh: float,
    ) -> HedgePnL:
        """Compute hedge P&L for one settlement period within an active term.

        For the matching contract: hedged_mwh = consumed × hedge_fraction / 1000.
        pnl = (agreed_price − actual_spot) × hedged_mwh.
        Positive when the forward price (what the company locked in) is above spot —
        i.e. the company paid over the odds on the hedge but covered its supply risk.

        Returns HedgePnL(0, 0) if no matching contract found (e.g. deemed/flex terms
        which have no locked forward price).
        """
        for c in self._contracts:
            if c.customer_id == customer_id and c.term_start == term_start:
                hedged_mwh = (consumed_kwh / 1000.0) * c.hedge_fraction
                pnl = (c.agreed_price_gbp_per_mwh - actual_spot_gbp_per_mwh) * hedged_mwh
                self._total_pnl_gbp += pnl
                self._total_hedged_mwh += hedged_mwh
                return HedgePnL(hedged_mwh=hedged_mwh, pnl_gbp=pnl)
        return HedgePnL(hedged_mwh=0.0, pnl_gbp=0.0)

    @property
    def total_pnl_gbp(self) -> float:
        return self._total_pnl_gbp

    @property
    def total_hedged_mwh(self) -> float:
        return self._total_hedged_mwh

    @property
    def contract_count(self) -> int:
        return len(self._contracts)

    def open_contracts(self) -> list[ForwardContract]:
        return list(self._contracts)

    def summary(self) -> dict:
        return {
            "contract_count": self.contract_count,
            "total_hedged_mwh": round(self._total_hedged_mwh, 3),
            "total_hedge_pnl_gbp": round(self._total_pnl_gbp, 2),
        }
