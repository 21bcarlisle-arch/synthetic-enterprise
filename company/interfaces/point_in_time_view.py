"""PointInTimeView — the as-of snapshot object (Epoch-2 core, W1_reveal_over_
time / D2_three_clocks, director-approved bounded start 2026-07-10, per the
closed POINT_IN_TIME_SNAPSHOT_TIER1.md gate's Option A scope).

The structural fix the hedge-volatility bug (docs/review_gates/done/
HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md) needed but didn't get: instead of
patching one caller (`_price_history_as_of()` in simulation/run_phase2b.py)
to remember to bound its own data, a company decision constructs ONE
PointInTimeView(decision_time=...) object and reads everything through it.
The bound lives on the object, not in each caller's memory -- a future call
site literally cannot forget it, because there is no unbounded read path
left to accidentally use.

Two backing sources, matching the two real timing problems this spine
exists to solve:
- `market_data_port`: an existing MarketDataPort-Protocol adapter
  (tools/market_data_port.py) for prices/forwards -- single-axis as-of
  filtering, adequate for synthetic/frozen market data with no revision
  history.
- `bitemporal_log`: a BitemporalEventLog (company/interfaces/
  bitemporal_event_log.py) for anything with REAL settlement-run
  restatement behaviour (consumption, settlement-derived facts) -- answers
  "what did we know as of decision_time", not just "what was valid then".

Scope, matching the gate's own sizing ("1-2 files, a class + a handful of
methods, existing call sites migrated one at a time"): price/forward
observables via market_data_port now; weather/generation/demand left for a
later pass unless a similar caller-trusted gap is found there too (not yet
audited, per the gate's own honest scope limit).
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

from company.interfaces.bitemporal_event_log import BitemporalEventLog, BitemporalRecord
from tools.market_data_port import MarketDataPort


class PointInTimeView:
    """Constructed once per decision, bound to `decision_time`. No method
    here accepts an `as_of`/date parameter for the bounded quantities --
    that would just recreate the exact bug this object exists to prevent
    (a caller passing the wrong date, or a default that silently reads
    everything). The bound is fixed at construction and used for every
    subsequent read."""

    def __init__(
        self,
        decision_time: dt.datetime,
        market_data_port: MarketDataPort,
        bitemporal_log: Optional[BitemporalEventLog] = None,
    ) -> None:
        self.decision_time = decision_time
        self._market = market_data_port
        self._bitemporal_log = bitemporal_log

    @property
    def decision_date(self) -> dt.date:
        return self.decision_time.date()

    def get_spot_elec_gbp_per_mwh(self) -> float:
        return self._market.get_spot_elec_gbp_per_mwh(as_of=self.decision_date)

    def get_spot_gas_gbp_per_mwh(self) -> float:
        return self._market.get_spot_gas_gbp_per_mwh(as_of=self.decision_date)

    def get_forward_price(self, delivery_date: dt.date, commodity: str = "electricity") -> float:
        return self._market.get_forward_price(
            as_of=self.decision_date, delivery_date=delivery_date, commodity=commodity,
        )

    def get_market_summary(self) -> dict:
        return self._market.get_market_summary(as_of=self.decision_date)

    def get_fact_as_known(
        self, entity_id: str, fact_type: str, valid_time: Optional[dt.date] = None,
    ) -> Optional[BitemporalRecord]:
        """One bitemporal fact, exactly as it would have looked to this
        decision. Raises if this view was constructed without a
        bitemporal_log -- a clear, load-bearing error rather than silently
        returning None (which would be indistinguishable from "genuinely
        unknown yet")."""
        if self._bitemporal_log is None:
            raise RuntimeError(
                "PointInTimeView constructed without a bitemporal_log -- "
                "cannot answer get_fact_as_known()."
            )
        return self._bitemporal_log.as_known_at(
            self.decision_time, entity_id, fact_type, valid_time,
        )

    def get_history_as_known(self, entity_id: str, fact_type: str) -> list[BitemporalRecord]:
        """The bitemporal generalisation of `_price_history_as_of()`'s
        bisect-slice -- the full history of one entity/fact_type, bounded
        to exactly what this decision could have known, structurally rather
        than by a per-call-site patch."""
        if self._bitemporal_log is None:
            raise RuntimeError(
                "PointInTimeView constructed without a bitemporal_log -- "
                "cannot answer get_history_as_known()."
            )
        return self._bitemporal_log.history_as_known_at(
            self.decision_time, entity_id, fact_type,
        )
