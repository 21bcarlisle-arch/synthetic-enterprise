"""observable_trace_capture — record an EXOGENOUS observable trace from ONE
seeded `SimInterface` run, for cheap deterministic replay via
`RecordedSimInterface` (ARCH1_internal_seams, docs/design/ARCH1_FRAME.md §3/§9).

WHAT IT RECORDS: only the RETURN VALUES of `SimInterface` EXOGENOUS methods
(currently `get_forward_price`) — a price float per (fuel, delivery_date,
term_months) queried as of a decision clock. It records NO sim internal: a
trace that captured, say, a churn parameter would be a wall breach, and there
is no path here to one — the capture only ever calls the seam and stores what
the seam returns (§5). This makes the wall structurally safe.

BLINDFOLD / R13 discipline: the capture clock (`as_of`) is recorded as the
record's `observed_at` — the moment that answer became knowable. Replay
(`ObservableTrace.replay`) then refuses to serve any record whose `observed_at`
is after the query's decision clock. Capture is blind to company P&L: it records
what the world DID at each clock, never adjusted because a variant's results
look wrong (R13 baseline discipline).

Lives in `tools/` (harness, EXEMPT from the epistemic import check). This is a
DISTINCT file from anything A8 touches (`tournament_runner.py` / `sim_runner.py`
/ `autonomous_runner.py`), so the two atoms stay logically disjoint even though
both nominally list `tools`.

Usage:
    python3 -m tools.observable_trace_capture --out trace.jsonl \\
        --fuels electricity gas \\
        --as-of 2018-01-01 2020-01-01 2022-01-01 \\
        --delivery 2018-07-01 2020-07-01 2022-07-01 \\
        --terms 12 24

The CLI wires a seeded `LiveSimInterface`; the core `capture_trace()` accepts
ANY `SimInterface`, so it is deterministically testable against a stub.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from company.interfaces.recorded_sim_interface import (
    ObservableRecord,
    ObservableTrace,
    ReplayStatus,
    _EXOGENOUS_REQUEST_TYPES,
    canonical_request_key,
)
from company.interfaces.sim_interface import SimInterface


@dataclass(frozen=True)
class ForwardPriceQuery:
    """One exogenous query to capture. `as_of` is the decision clock; `observed_at`
    on the recorded row is set to `as_of` (the answer became knowable at the
    decision clock). `valid_time` is the delivery date (what the answer is ABOUT)."""

    fuel: str
    delivery_date: str  # ISO date string, as the seam expects
    as_of: dt.datetime
    term_months: int = 12


def capture_forward_price(
    interface: SimInterface, query: ForwardPriceQuery
) -> ObservableRecord:
    """Capture ONE forward-price observable into a record. Records only the
    return value of `get_forward_price` (an observable price float)."""
    request_type = _EXOGENOUS_REQUEST_TYPES["get_forward_price"]
    key = canonical_request_key(
        request_type, query.fuel, query.delivery_date, query.term_months
    )
    try:
        price = interface.get_forward_price(
            query.fuel, query.delivery_date, term_months=query.term_months
        )
        status = ReplayStatus.OK
        payload: object = float(price)
    except Exception as exc:  # a genuine capture-time failure is recorded honestly
        status = ReplayStatus.ERROR
        payload = f"{type(exc).__name__}: {exc}"
    return ObservableRecord(
        request_type=request_type,
        request_key=key,
        as_of=query.as_of,
        observed_at=query.as_of,  # knowable at the decision clock (blindfold axis)
        valid_time=_safe_date(query.delivery_date),
        status=status,
        payload=payload,
    )


def _safe_date(iso: str) -> Optional[dt.date]:
    try:
        return dt.date.fromisoformat(iso)
    except (ValueError, TypeError):
        return None


def capture_trace(
    interface: SimInterface,
    queries: Iterable[ForwardPriceQuery],
    out_path: Optional[str] = None,
) -> ObservableTrace:
    """Capture every query into an ObservableTrace. If `out_path` is given, each
    record is ALSO written append-only to disk as it is produced (C-S4)."""
    if out_path is not None:
        Path(out_path).write_text("", encoding="utf-8")  # start a fresh trace file
    trace = ObservableTrace()
    for q in queries:
        rec = capture_forward_price(interface, q)
        trace.append(rec)
        if out_path is not None:
            ObservableTrace.append_record_to_file(out_path, rec)
    return trace


def build_queries(
    fuels: list[str],
    as_ofs: list[dt.datetime],
    deliveries: list[str],
    terms: list[int],
) -> list[ForwardPriceQuery]:
    """Deterministic query grid. Order is fixed (nested loops) so a re-capture
    with the same arguments produces a byte-identical trace (determinism WALL)."""
    queries: list[ForwardPriceQuery] = []
    for as_of in as_ofs:
        for fuel in fuels:
            for delivery in deliveries:
                for term in terms:
                    queries.append(
                        ForwardPriceQuery(
                            fuel=fuel,
                            delivery_date=delivery,
                            as_of=as_of,
                            term_months=term,
                        )
                    )
    return queries


def _parse_clock(s: str) -> dt.datetime:
    try:
        return dt.datetime.fromisoformat(s)
    except ValueError:
        return dt.datetime.combine(dt.date.fromisoformat(s), dt.time.min)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Capture an exogenous observable trace from a seeded SimInterface."
    )
    parser.add_argument("--out", required=True, help="output JSONL trace path")
    parser.add_argument("--fuels", nargs="+", default=["electricity", "gas"])
    parser.add_argument(
        "--as-of", dest="as_ofs", nargs="+", required=True,
        help="decision clocks (ISO date/datetime) to capture the curve as-of",
    )
    parser.add_argument(
        "--delivery", dest="deliveries", nargs="+", required=True,
        help="delivery dates (ISO) to price",
    )
    parser.add_argument("--terms", nargs="+", type=int, default=[12])
    parser.add_argument(
        "--stub", action="store_true",
        help="use StubSimInterface instead of LiveSimInterface (smoke/self-test)",
    )
    args = parser.parse_args(argv)

    if args.stub:
        from company.interfaces.sim_interface import StubSimInterface
        interface: SimInterface = StubSimInterface()
    else:
        # Seeded live capture (records real Elexon/NESO-derived observables).
        from company.interfaces.sim_interface import LiveSimInterface
        interface = LiveSimInterface()

    as_ofs = [_parse_clock(s) for s in args.as_ofs]
    queries = build_queries(args.fuels, as_ofs, args.deliveries, args.terms)
    trace = capture_trace(interface, queries, out_path=args.out)
    print(
        f"captured {len(trace)} exogenous observable record(s) to {args.out} "
        f"({len(queries)} queries)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
