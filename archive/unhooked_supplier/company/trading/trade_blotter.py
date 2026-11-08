"""Wholesale trading journal (trade blotter).

The company's trading desk records every wholesale transaction in a trade
blotter — a chronological log of all buy/sell actions. This is distinct from
the forward book (open positions aggregated by customer) and is the primary
record for:
  - P&L attribution by trader/desk
  - Counterparty credit exposure
  - Regulatory reporting (REMIT trade reporting obligation)

REMIT (Regulation on Energy Market Integrity and Transparency) requires
European energy market participants to report wholesale trades to ACER
within 1 working day.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


_REMIT_REPORTING_THRESHOLD_MWH = 0.01  # all trades above this are reportable


@dataclass
class TradeEntry:
    trade_id: str
    trade_date: str                             # ISO date
    trade_time: str                             # HH:MM UTC
    direction: Literal["buy", "sell"]
    commodity: Literal["electricity", "gas"]
    volume_mwh: float
    price_gbp_per_mwh: float
    counterparty: str
    delivery_period: str                        # e.g. "2024-Q1", "2024-M03"
    trader_id: str = ""
    desk: str = "front_office"                 # front_office / gas_desk / renewables
    reported_to_remit: bool = False
    notes: str = ""

    @property
    def notional_gbp(self) -> float:
        return round(self.volume_mwh * self.price_gbp_per_mwh, 2)

    @property
    def is_remit_reportable(self) -> bool:
        return self.volume_mwh >= _REMIT_REPORTING_THRESHOLD_MWH


class TradeBlotter:
    """Chronological trade journal for the wholesale desk."""

    def __init__(self):
        self._trades: list[TradeEntry] = []
        self._next_id = 1

    def record(self, entry: TradeEntry) -> TradeEntry:
        if not entry.trade_id:
            entry.trade_id = f"TRD-{self._next_id:06d}"
        self._trades.append(entry)
        self._next_id += 1
        return entry

    def get(self, trade_id: str) -> TradeEntry | None:
        return next((t for t in self._trades if t.trade_id == trade_id), None)

    def buys(self) -> list[TradeEntry]:
        return [t for t in self._trades if t.direction == "buy"]

    def sells(self) -> list[TradeEntry]:
        return [t for t in self._trades if t.direction == "sell"]

    def by_counterparty(self, counterparty: str) -> list[TradeEntry]:
        return [t for t in self._trades if t.counterparty == counterparty]

    def by_desk(self, desk: str) -> list[TradeEntry]:
        return [t for t in self._trades if t.desk == desk]

    def unreported_remit(self) -> list[TradeEntry]:
        return [t for t in self._trades if t.is_remit_reportable and not t.reported_to_remit]

    def mark_reported(self, trade_id: str) -> bool:
        t = self.get(trade_id)
        if t is None:
            return False
        t.reported_to_remit = True
        return True

    def net_position_mwh(self) -> float:
        return round(
            sum(t.volume_mwh for t in self.buys()) - sum(t.volume_mwh for t in self.sells()), 4
        )

    def total_notional_gbp(self) -> float:
        return round(sum(t.notional_gbp for t in self._trades), 2)

    def counterparty_exposure(self) -> dict[str, float]:
        exp: dict[str, float] = {}
        for t in self._trades:
            exp[t.counterparty] = round(exp.get(t.counterparty, 0.0) + t.notional_gbp, 2)
        return exp

    def summary(self) -> dict:
        return {
            "total_trades": len(self._trades),
            "buys": len(self.buys()),
            "sells": len(self.sells()),
            "net_position_mwh": self.net_position_mwh(),
            "total_notional_gbp": self.total_notional_gbp(),
            "unreported_remit": len(self.unreported_remit()),
            "counterparties": len(set(t.counterparty for t in self._trades)),
        }
