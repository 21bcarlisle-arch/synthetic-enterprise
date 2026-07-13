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

2026-07-11 (M1 depth work, docs/design/M1_PRICE_HISTORY_PIPELINE_FINDING.md):
the obvious next migration (the historical backtest's own
estimate_price_volatility() call site) turned out to need a THIRD backing
source, not market_data_port -- that adapter is wired to a frozen 2025
snapshot built for the live-decision path, a completely different pipeline
from the historical simulation's own price records (elec_records/
gas_records in simulation/run_phase2b.py, sourced from a live Elexon API
fetch per run). `market_data_port` is therefore now OPTIONAL: a
PointInTimeView backing the historical replay is constructed with only a
bitemporal_log (populated from the sim's own records via
`build_price_bitemporal_log()` below), never touching market_data_port at
all -- the same fail-loud-if-missing pattern already used for
bitemporal_log extends naturally to this case.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

from company.interfaces.bitemporal_event_log import BitemporalEventLog, BitemporalRecord
from tools.market_data_port import MarketDataPort


def build_price_bitemporal_log(
    elec_records: list[dict], gas_records: list[dict],
) -> BitemporalEventLog:
    """Populate a BitemporalEventLog from the historical simulation's own
    raw settlement-price records -- the structural replacement for
    simulation/run_phase2b.py's `_price_history_as_of()` bisect-slice fix.

    One record per (commodity, date): entity_id=commodity, fact_type=
    "daily_mean_spot_price", valid_time=date, value=daily mean price.
    Aggregates to daily means at population time because
    company/trading/hedge_decision.py::estimate_price_volatility() already
    does this exact aggregation internally on whatever list it's handed --
    feeding it pre-aggregated daily records changes nothing about its
    output, just moves the aggregation earlier and lets the bitemporal log's
    one-record-per-valid_time model fit without losing information.

    transaction_time is set to START-OF-DAY on valid_time + 1 day, not
    valid_time's own midnight (2026-07-13 fix, closing the same-day-price
    boundary leak recorded in this atom's expert_hour finding,
    docs/design/maturity_map.yaml::W1_reveal_over_time). A hedge decision's
    decision_time is midnight(term_start=D); `history_as_known_at()` includes
    every record with transaction_time <= decision_time. With the old
    transaction_time == valid_time (midnight-of-D) encoding, a decision at
    midnight(D) could see date D's OWN daily-mean spot price -- not actually
    knowable at 00:00 on D. Setting transaction_time to midnight of D+1
    means that record only becomes visible to a decision at midnight(D+1) or
    later, so a decision at midnight(D) correctly excludes D's own price
    while still seeing D-1 and everything earlier -- matching the strictly-
    before window sim/risk_engine.py::calculate_sigma_recent() already uses
    (`end_date = ref_date - 1`). This dataset still does not model real
    Elexon settlement-run revisions (Initial/II/IF/SF) at the price level,
    so there is nothing to restate yet beyond this one-day reveal delay -- a
    real restatement would be `.record()`d with a LATER transaction_time for
    the same valid_time, which `history_as_known_at()` already handles
    correctly by construction (see bitemporal_event_log.py).
    """
    log = BitemporalEventLog()
    for commodity, records in (("electricity", elec_records), ("gas", gas_records)):
        daily: dict[str, list[float]] = {}
        for r in records:
            d = r.get("settlementDate", "")
            p = r.get("systemSellPrice", 0.0)
            if d and p and p > 0:
                daily.setdefault(d, []).append(p)
        for d in sorted(daily.keys()):
            mean_price = sum(daily[d]) / len(daily[d])
            valid_date = dt.date.fromisoformat(d)
            log.record(
                entity_id=commodity,
                fact_type="daily_mean_spot_price",
                valid_time=valid_date,
                transaction_time=dt.datetime.combine(
                    valid_date + dt.timedelta(days=1), dt.time.min,
                ),
                value=mean_price,
            )
    return log


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
        market_data_port: Optional[MarketDataPort] = None,
        bitemporal_log: Optional[BitemporalEventLog] = None,
    ) -> None:
        self.decision_time = decision_time
        self._market = market_data_port
        self._bitemporal_log = bitemporal_log

    @property
    def decision_date(self) -> dt.date:
        return self.decision_time.date()

    def _require_market(self) -> MarketDataPort:
        if self._market is None:
            raise RuntimeError(
                "PointInTimeView constructed without a market_data_port -- "
                "cannot answer this market-data read."
            )
        return self._market

    def get_spot_elec_gbp_per_mwh(self) -> float:
        return self._require_market().get_spot_elec_gbp_per_mwh(as_of=self.decision_date)

    def get_spot_gas_gbp_per_mwh(self) -> float:
        return self._require_market().get_spot_gas_gbp_per_mwh(as_of=self.decision_date)

    def get_forward_price(self, delivery_date: dt.date, commodity: str = "electricity") -> float:
        return self._require_market().get_forward_price(
            as_of=self.decision_date, delivery_date=delivery_date, commodity=commodity,
        )

    def get_market_summary(self) -> dict:
        return self._require_market().get_market_summary(as_of=self.decision_date)

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

    def get_price_history_as_of(self, commodity: str = "electricity") -> list[dict]:
        """Bounded daily-mean price history for volatility estimation --
        the real structural replacement for simulation/run_phase2b.py's
        `_price_history_as_of()` bisect-slice fix, backed by
        `build_price_bitemporal_log()`'s population of this view's
        bitemporal_log. Returns `[{settlementDate, systemSellPrice}, ...]`
        in chronological order, matching exactly the shape
        `company/trading/hedge_decision.py::estimate_price_volatility()`
        expects -- structurally bounded to `decision_time`, never anything
        the company couldn't yet know."""
        records = self.get_history_as_known(commodity, "daily_mean_spot_price")
        return [
            {"settlementDate": r.valid_time.isoformat(), "systemSellPrice": r.value}
            for r in records
        ]
