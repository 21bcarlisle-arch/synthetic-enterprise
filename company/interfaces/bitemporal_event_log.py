"""Bitemporal event log — the ordering-invariant foundation for the reveal-
over-time spine (Epoch-2 core, W1_reveal_over_time / D2_three_clocks, one
architecture per the closed POINT_IN_TIME_SNAPSHOT_TIER1.md gate).

Real UK settlement data is bitemporal by nature, not just "dated": a
half-hour's consumption/price goes through multiple Elexon settlement runs
(Initial, II, IF, SF at T+5wd/T+14mo/T+14mo respectively) that can RESTATE
an earlier figure. Two distinct time axes matter for any point-in-time-
honest read:

- valid_time: what real-world period the fact is ABOUT (e.g. the half-hour
  settlement period, or the calendar date a price applies to).
- transaction_time: when THIS PARTICULAR VALUE became knowable/recorded --
  i.e. which settlement run produced it, or more generally, when the
  company's own systems could first have observed it.

A naive single-timestamp "as of" filter (the existing MarketDataPort
pattern, tools/market_data_port.py) answers "what was true about date X" --
it does NOT answer "what did we actually know, as of decision time D,
about date X" if date X's own settlement figure was itself revised after D.
The bitemporal log answers the second, harder, more honest question --
named "bitemporal history" (Martin Fowler) / "point-in-time join" (Feast) in
the external literature already cited in W1's DISCOVER-stage finding
(docs/design/MARGIN_REALISM_W1_DISCOVER_FINDING.md).

Lives in company/interfaces/ (the one location explicitly exempt from the
epistemic-wall import check, tools/epistemic_verifier.py's EXEMPT_PATHS) --
this IS the seam, not a violation of it.
"""
from __future__ import annotations

import copy
import datetime as dt
from dataclasses import dataclass, field, replace
from typing import Any


@dataclass(frozen=True)
class BitemporalRecord:
    """One fact, dated on both axes. `record_id` is assigned by the log on
    insertion (monotonically increasing insertion order), not by the
    caller -- this is what lets `as_known_at()` give a deterministic
    "latest record whose transaction_time is visible" answer when multiple
    records share the same valid_time (e.g. Initial vs SF settlement runs
    for the same half-hour)."""
    record_id: int
    entity_id: str
    fact_type: str
    valid_time: dt.date
    transaction_time: dt.datetime
    value: Any
    superseded_by_run: str | None = None  # e.g. "SF" superseding "II" -- informational only


class BitemporalEventLog:
    """Append-only. Nothing is ever mutated or deleted -- a restatement is a
    NEW record with a later transaction_time for the same (entity_id,
    fact_type, valid_time), never an edit to the old one. This is what makes
    "what did we know as of decision_time D" a well-defined question no
    matter how many times reality has since been restated."""

    def __init__(self) -> None:
        self._records: list[BitemporalRecord] = []
        self._next_id = 1

    @staticmethod
    def _decouple(rec: BitemporalRecord) -> BitemporalRecord:
        """Return a record whose mutable payload is fully independent of
        `rec`'s. `BitemporalRecord` itself is `frozen`, but `value` is `Any`
        -- in practice a JSON-like dict, or a `DecisionEvent` whose own
        request/context/decision fields are dicts -- so a shared reference to
        `value` is a live alias through which a caller (on write) or a
        consumer (on read) can silently rewrite a 'past' record, breaching the
        append-only guarantee this class documents. Deep-copying the payload
        and rewrapping via `dataclasses.replace` (record_id and both time axes
        preserved) is what makes that impossible. Payloads are small; deepcopy
        is correct and adequate here (see class/module notes)."""
        return replace(rec, value=copy.deepcopy(rec.value))

    def record(
        self,
        entity_id: str,
        fact_type: str,
        valid_time: dt.date,
        transaction_time: dt.datetime,
        value: Any,
        superseded_by_run: str | None = None,
    ) -> BitemporalRecord:
        # COPY-ON-WRITE: store a payload decoupled from the caller's object,
        # so a caller that keeps and later mutates the dict it passed in
        # cannot rewrite the stored ('immutable') record.
        rec = BitemporalRecord(
            record_id=self._next_id,
            entity_id=entity_id,
            fact_type=fact_type,
            valid_time=valid_time,
            transaction_time=transaction_time,
            value=copy.deepcopy(value),
            superseded_by_run=superseded_by_run,
        )
        self._records.append(rec)
        self._next_id += 1
        # COPY-ON-READ (the return is a read): the caller must not receive a
        # live alias into the store either.
        return self._decouple(rec)

    def as_known_at(
        self,
        decision_time: dt.datetime,
        entity_id: str,
        fact_type: str,
        valid_time: dt.date | None = None,
    ) -> BitemporalRecord | None:
        """The single fact a company decision made AT decision_time would
        have seen -- the LATEST record (by transaction_time, tie-broken by
        insertion order) whose transaction_time <= decision_time, optionally
        filtered to one valid_time. Returns None if nothing was knowable yet
        -- a real, honest answer (not a KeyError, not a silent 0), matching
        this project's R12 discipline of never fabricating a value that
        doesn't exist."""
        candidates = [
            r for r in self._records
            if r.entity_id == entity_id
            and r.fact_type == fact_type
            and r.transaction_time <= decision_time
            and (valid_time is None or r.valid_time == valid_time)
        ]
        if not candidates:
            return None
        # COPY-ON-READ: a returned payload is decoupled from the stored record
        # AND from any other read, so mutating it can neither corrupt the store
        # nor alias a sibling event (e.g. resolve reading a pending request).
        return self._decouple(max(candidates, key=lambda r: (r.transaction_time, r.record_id)))

    def history_as_known_at(
        self,
        decision_time: dt.datetime,
        entity_id: str,
        fact_type: str,
    ) -> list[BitemporalRecord]:
        """Every valid_time's latest-known-as-of-decision_time record, for
        an entity/fact_type -- e.g. "the full price history for this
        commodity, exactly as it would have looked to a decision made at
        decision_time", the bitemporal generalisation of the existing
        `_price_history_as_of()` bisect-slice fix (simulation/
        run_phase2b.py) that this whole spine exists to replace with a
        structural guarantee instead of a per-call-site patch."""
        latest_by_valid_time: dict[dt.date, BitemporalRecord] = {}
        for r in self._records:
            if r.entity_id != entity_id or r.fact_type != fact_type:
                continue
            if r.transaction_time > decision_time:
                continue
            existing = latest_by_valid_time.get(r.valid_time)
            if existing is None or (r.transaction_time, r.record_id) > (existing.transaction_time, existing.record_id):
                latest_by_valid_time[r.valid_time] = r
        # COPY-ON-READ: each returned record is decoupled from the store.
        return [
            self._decouple(r)
            for r in sorted(latest_by_valid_time.values(), key=lambda r: r.valid_time)
        ]

    def all_records(self) -> list[BitemporalRecord]:
        """Full, unfiltered log -- for tooling/debugging only. Company
        decision code must never call this; it defeats the entire point.
        Named loudly, not `_all_records`, so a reviewer immediately sees
        any call site using it is suspect."""
        # COPY-ON-READ: decouple every payload, so even this debug/tooling
        # surface cannot be used to mutate the store through an alias.
        return [self._decouple(r) for r in self._records]
