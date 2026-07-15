"""RecordedSimInterface — the typed mock at the OUTER sim/company seam.

ARCH1_internal_seams, highest-return slice (docs/design/ARCH1_FRAME.md). A
third `SimInterface` implementation alongside `StubSimInterface` and
`LiveSimInterface`. It REPLAYS a recorded EXOGENOUS observable trace
(market/weather/regulatory observables the company cannot see inside anyway)
so a company "life" runs at LOW memory footprint — the ~5.67 GB/life the
tournament reconstructs every run lives in that exogenous world, none of which
the company can read internals of. Recording it once and replaying it through
the seam collapses per-life RSS and unthrottles `tournament_runner`'s
memory-bound worker cap.

Lives in `company/interfaces/` — the one location EXEMPT from the epistemic
wall import check (`tools/epistemic_verifier.py` EXEMPT_PATHS). This IS the
seam, not a breach of it. The trace holds ONLY the return VALUES of
`SimInterface` methods (observables), never a sim internal, so nothing in it
could leak an internal even in principle.

WALLS preserved by construction (docs/design/ARCH1_FRAME.md §5):
  * Epistemic wall — mock is a seam impl; company still reaches the world only
    through the Protocol; trace is observables-only.
  * Point-in-Time Blindfold (WALL) — replay REFUSES any record whose
    `observed_at > as_of`: the future is unreachable through the mock exactly
    as through the real interface. FAIL-CLOSED: a missing/empty/malformed
    `observed_at` is treated as NOT-yet-knowable and NEVER leaks its payload.
    (R15 killer pattern FAIL-OPEN is forbidden; mutation-tested.)
  * Determinism (WALL, C-S2) — replay is a PURE function of
    (trace, request_key, as_of). It draws ZERO RNG; a subsystem that consumes
    no RNG can never shift another subsystem's draws (strictly safer than the
    live path).

Exogenous vs endogenous split (the load-bearing decision, §2): EXOGENOUS
observables (forward price / market curve / weather baseline / regulatory
publications) are pure replay — the company's own actions cannot move the
wholesale curve or the weather. ENDOGENOUS observables (customer status, churn
estimate, settlement volumes reflecting THIS variant's book, the notify_*
writes) run the LIVE fixed-world path against a cheap in-process delegate — they
are the company's own kilobytes of book state, not gigabytes. The fixed
exogenous world breaks the price->churn->volume feedback for endogenous
observables; that divergence is the MEASURED gap (COUPLED_TRIAD, §6,
`fitness_gap` below), a NAMED R10 simplification, licensed for inner-loop
ranking ONLY, never a published figure.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Optional

from company.crm.payment_behaviour_analytics import BehaviourScore
from company.interfaces.sim_interface import SimInterface, StubSimInterface


class ReplayStatus(str, Enum):
    """The recorded async-envelope status (C-S3). A recorded NOT_KNOWABLE_YET
    stays NOT_KNOWABLE_YET on replay — pending latency is representable, not
    collapsed to same-step resolution."""

    OK = "OK"
    NOT_KNOWABLE_YET = "NOT_KNOWABLE_YET"
    ERROR = "ERROR"


class NotKnowableYet(Exception):
    """Raised by a typed seam method when the queried observable was not yet
    knowable at the decision clock (blindfold WALL). It carries NO payload — the
    future value is unreachable, not merely withheld."""

    def __init__(self, request_key: str, as_of: dt.datetime):
        super().__init__(
            f"observable {request_key!r} is not knowable as of {as_of.isoformat()} "
            f"(Point-in-Time Blindfold WALL)"
        )
        self.request_key = request_key
        self.as_of = as_of


# --------------------------------------------------------------------------
# Canonical request key: hash of (request_type, args EXCLUDING the as_of clock).
# The as_of decision clock is NOT part of the key — it is the blindfold axis the
# replay filters on, not an identity axis. Two queries for the same observable
# at different decision clocks share one key and are resolved by observed_at.
# --------------------------------------------------------------------------
def canonical_request_key(request_type: str, *args: Any) -> str:
    raw = "|".join([request_type] + [str(a) for a in args])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _parse_dt(value: Any) -> Optional[dt.datetime]:
    """Parse a datetime, FAIL-CLOSED. A missing / empty / malformed value returns
    None — which the blindfold gate treats as NOT-yet-knowable, so a corrupt
    `observed_at` can never leak its payload (R15 FAIL-OPEN forbidden)."""
    if value is None or value == "":
        return None
    if isinstance(value, dt.datetime):
        return value
    try:
        return dt.datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def _parse_date(value: Any) -> Optional[dt.date]:
    if value is None or value == "":
        return None
    if isinstance(value, dt.date) and not isinstance(value, dt.datetime):
        return value
    try:
        return dt.date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


@dataclass(frozen=True)
class ObservableRecord:
    """One recorded exogenous seam response. Frozen — the trace is append-only
    and a record is never mutated. Envelope shape reused from the go-live
    contract (`GO_LIVE_SEAM_AND_INTERNAL_SEAMS_DESIGN.md §1.2`) — one envelope at
    two radii, ARCH1 invents no second one.

    `payload` is ONLY ever an observable value (a price float, a consumption
    baseline, a regulatory digest) — EXACTLY what the real interface returns.
    A record of a sim internal (e.g. a churn parameter) would be a wall breach;
    the capture tool records only the return values of `SimInterface` methods.
    """

    request_type: str
    request_key: str
    as_of: dt.datetime  # decision clock at capture (blindfold; WALL)
    observed_at: Optional[dt.datetime]  # when this answer became knowable (bitemporal)
    valid_time: Optional[dt.date]  # what period the answer is ABOUT
    status: ReplayStatus
    payload: Any

    def to_dict(self) -> dict:
        return {
            "request_type": self.request_type,
            "request_key": self.request_key,
            "as_of": self.as_of.isoformat() if self.as_of else None,
            "observed_at": self.observed_at.isoformat() if self.observed_at else None,
            "valid_time": self.valid_time.isoformat() if self.valid_time else None,
            "status": self.status.value,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ObservableRecord":
        try:
            status = ReplayStatus(d.get("status", "OK"))
        except ValueError:
            status = ReplayStatus.ERROR
        return cls(
            request_type=str(d.get("request_type", "unknown")),
            request_key=str(d.get("request_key", "")),
            as_of=_parse_dt(d.get("as_of")) or dt.datetime.min,
            observed_at=_parse_dt(d.get("observed_at")),  # None => fail-closed on replay
            valid_time=_parse_date(d.get("valid_time")),
            status=status,
            payload=d.get("payload"),
        )


class ObservableTrace:
    """Append-only recorded log of exogenous seam responses (C-S4: the
    append-only event-log abstraction; on-disk form JSONL now, swappable without
    touching replay logic — SIMPLICITY GUARD: a file, not a repository cathedral).

    `replay()` is the blindfold-gated read and the single most important WALL in
    ARCH1. It is a PURE function of (records, request_key, as_of): no RNG, no
    clock read, no I/O — same inputs, byte-identical record out (C-S2), for any
    arrival order (C-S1, keyed by request_key).
    """

    def __init__(self, records: Optional[Iterable[ObservableRecord]] = None) -> None:
        self._records: list[ObservableRecord] = list(records or [])

    def __len__(self) -> int:
        return len(self._records)

    def records(self) -> list[ObservableRecord]:
        return list(self._records)

    def append(self, record: ObservableRecord) -> None:
        """Append-only — never mutate or delete an existing record."""
        self._records.append(record)

    def replay(self, request_key: str, as_of: dt.datetime) -> ObservableRecord:
        """Serve the observable for `request_key` as it would have looked at the
        `as_of` decision clock — BLINDFOLD-GATED.

        The gate, in order (each line is load-bearing; removing any one is a WALL
        breach the mutation tests catch):
          1. FAIL-CLOSED on unknowable timing: a record whose `observed_at` is
             None (missing/empty/malformed at capture) is DROPPED — never served.
          2. BLINDFOLD: a record whose `observed_at > as_of` is DROPPED — the
             future is unreachable. (R15 FAIL-OPEN forbidden.)
          3. Of what remains, serve the LATEST-knowable record (by observed_at,
             insertion order as tie-break). A recorded non-OK status (a captured
             NOT_KNOWABLE_YET / ERROR, C-S3) is returned AS-IS.
          4. If nothing is knowable yet -> a synthesised NOT_KNOWABLE_YET record
             carrying NO payload (a real, honest answer, not a silent 0).
        """
        candidates = [r for r in self._records if r.request_key == request_key]
        knowable: list[tuple[int, ObservableRecord]] = []
        for idx, r in enumerate(candidates):
            oa = r.observed_at
            if oa is None:  # (1) FAIL-CLOSED: unknowable timing never leaks
                continue
            if oa > as_of:  # (2) BLINDFOLD WALL: future is unreachable
                continue
            knowable.append((idx, r))
        if not knowable:
            request_type = candidates[0].request_type if candidates else "unknown"
            return ObservableRecord(
                request_type=request_type,
                request_key=request_key,
                as_of=as_of,
                observed_at=None,
                valid_time=None,
                status=ReplayStatus.NOT_KNOWABLE_YET,
                payload=None,
            )
        # latest-knowable by (observed_at, insertion order)
        _, best = max(knowable, key=lambda pair: (pair[1].observed_at, pair[0]))
        return best

    # ---- persistence (C-S4: JSONL now, swappable) ------------------------
    def save(self, path: str | os.PathLike) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            for r in self._records:
                fh.write(json.dumps(r.to_dict(), sort_keys=True) + "\n")

    @classmethod
    def load(cls, path: str | os.PathLike) -> "ObservableTrace":
        recs: list[ObservableRecord] = []
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            recs.append(ObservableRecord.from_dict(json.loads(line)))
        return cls(recs)

    @staticmethod
    def append_record_to_file(path: str | os.PathLike, record: ObservableRecord) -> None:
        """Genuinely append-only on-disk write (C-S4) — used by the capture tool
        so a trace grows one line at a time and an existing line is never
        rewritten."""
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


# The exogenous seam methods the mock REPLAYS. Everything else is endogenous and
# runs the live fixed-world delegate (see class docstring / FRAME §2).
_EXOGENOUS_REQUEST_TYPES = {
    "get_forward_price": "forward_price.v1",
}


class RecordedSimInterface(SimInterface):
    """Third `SimInterface` impl: EXOGENOUS observables replayed from a recorded
    trace (blindfold-gated, zero RNG); ENDOGENOUS observables delegated to a
    cheap in-process live-path object (default `StubSimInterface`).

    The decision clock (`as_of`) is the blindfold axis. It is set by the caller
    (`set_as_of` / constructor). If it is NOT set, the mock FAILS CLOSED — it
    uses `datetime.min`, so every exogenous query returns NOT_KNOWABLE_YET rather
    than leaking a future-relative value. Wiring the real per-decision clock
    through the sim run path is the run-path's job (the tournament driver /
    `saas.reporting`), OUTSIDE this atom's `company/interfaces` scope.
    """

    def __init__(
        self,
        trace: ObservableTrace,
        *,
        as_of: Optional[dt.datetime] = None,
        endogenous: Optional[SimInterface] = None,
    ) -> None:
        self._trace = trace
        self._as_of = as_of
        self._endo = endogenous if endogenous is not None else StubSimInterface()

    @classmethod
    def from_path(
        cls,
        path: str | os.PathLike,
        *,
        as_of: Optional[dt.datetime] = None,
        endogenous: Optional[SimInterface] = None,
    ) -> "RecordedSimInterface":
        return cls(ObservableTrace.load(path), as_of=as_of, endogenous=endogenous)

    def set_as_of(self, as_of: dt.datetime) -> "RecordedSimInterface":
        """Set the point-in-time decision clock for subsequent exogenous replay."""
        self._as_of = as_of
        return self

    @property
    def endogenous_delegate(self) -> SimInterface:
        return self._endo

    def _resolve_as_of(self) -> dt.datetime:
        # FAIL-CLOSED: no decision clock -> datetime.min -> NOT_KNOWABLE_YET for
        # every exogenous query, never a leak.
        return self._as_of if self._as_of is not None else dt.datetime.min

    # ---- EXOGENOUS: pure replay (blindfold-gated) ------------------------
    def get_forward_price(self, fuel: str, delivery_date: str, term_months: int = 12) -> float:
        key = canonical_request_key(
            _EXOGENOUS_REQUEST_TYPES["get_forward_price"], fuel, delivery_date, term_months
        )
        as_of = self._resolve_as_of()
        rec = self._trace.replay(key, as_of)
        if rec.status is ReplayStatus.NOT_KNOWABLE_YET:
            raise NotKnowableYet(key, as_of)
        if rec.status is ReplayStatus.ERROR:
            raise RuntimeError(f"recorded ERROR for {key!r}: {rec.payload!r}")
        return float(rec.payload)

    # ---- ENDOGENOUS: live fixed-world delegate (company's own book) ------
    def get_settlement_data(self, mpan: str, period: str) -> dict[str, Any]:
        return self._endo.get_settlement_data(mpan, period)

    def get_customer_status(self, account_id: str) -> str:
        return self._endo.get_customer_status(account_id)

    def get_churn_estimate(
        self,
        account_id: str,
        old_rate_gbp_per_mwh: float,
        new_rate_gbp_per_mwh: float,
        tenure_years: float,
        annual_consumption_kwh: float = 0.0,
        *,
        bill_shock_count: int = 0,
        behaviour_score: Optional[BehaviourScore] = None,
        satisfaction_score: Optional[float] = None,
    ) -> float:
        return self._endo.get_churn_estimate(
            account_id,
            old_rate_gbp_per_mwh,
            new_rate_gbp_per_mwh,
            tenure_years,
            annual_consumption_kwh,
            bill_shock_count=bill_shock_count,
            behaviour_score=behaviour_score,
            satisfaction_score=satisfaction_score,
        )

    def notify_churn(self, account_id, event_date, *, reason="non-renewal",
                     sim_churn_probability=None, company_churn_estimate=None):
        return self._endo.notify_churn(
            account_id, event_date, reason=reason,
            sim_churn_probability=sim_churn_probability,
            company_churn_estimate=company_churn_estimate,
        )

    def notify_acquisition(self, account_id, event_date, *, channel="market-acquisition",
                           predecessor_id=None):
        return self._endo.notify_acquisition(
            account_id, event_date, channel=channel, predecessor_id=predecessor_id,
        )

    def notify_retention_attempt(self, account_id, event_date, company_churn_estimate,
                                 discount_pct, outcome="pending"):
        notify = getattr(self._endo, "notify_retention_attempt", None)
        if notify is not None:
            return notify(account_id, event_date, company_churn_estimate, discount_pct, outcome)
        return None


# --------------------------------------------------------------------------
# COUPLED_TRIAD gap-measurement point (the gap IS the score, §6). The mock's
# fixed exogenous world breaks the price->churn->volume feedback for endogenous
# observables; the divergence from a full LiveSimInterface run is the gap this
# atom must MEASURE, not paper over. This is the measurement primitive; the
# tournament driver supplies the two fitness dicts for the same variant.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class GapMeasurement:
    """|fitness(mock) - fitness(full)| for one variant on one fitness field —
    reported per COUPLED_TRIAD each digest. Use rule (fail-closed): the mock is
    licensed for inner-loop RANKING only; it is NEVER a published/headline
    figure. If the measured gap exceeds a declared tolerance for a variant class,
    that class falls back to a full run (L3)."""

    variant_id: str
    field: str
    mock_value: float
    full_value: float

    @property
    def gap(self) -> float:
        return abs(self.mock_value - self.full_value)

    @property
    def relative_gap(self) -> float:
        denom = abs(self.full_value)
        if denom:
            return self.gap / denom
        return 0.0 if self.gap == 0 else float("inf")


def fitness_gap(
    variant_id: str,
    mock_fitness: dict,
    full_fitness: dict,
    field: str = "total_net_gbp",
) -> GapMeasurement:
    """Compute the COUPLED_TRIAD gap for one variant. Pure; no side effects."""
    return GapMeasurement(
        variant_id=variant_id,
        field=field,
        mock_value=float(mock_fitness.get(field, 0.0) or 0.0),
        full_value=float(full_fitness.get(field, 0.0) or 0.0),
    )


# --------------------------------------------------------------------------
# Publish-refusal WALL (§4, R15 fail-closed): a recorded run is a DEVELOPMENT
# tool — it may NEVER publish, promote an atom, or feed the board pack. This is
# the in-scope assertion primitive; wiring it into `process_run_complete`
# (saas/background) is that layer's job. Mutation-tested.
# --------------------------------------------------------------------------
class RecordedRunPublishRefused(RuntimeError):
    """A recorded/mock run tried to reach a publish path. Fail closed."""


def refuse_publish_if_recorded(env: Optional[dict] = None) -> None:
    """Raise if a recorded run (SIM_RECORDED_TRACE set) reaches a publish path.
    Fail-closed: the mock's fixed-world approximation must never become a
    published figure (§6 use-rule)."""
    src = env if env is not None else os.environ
    if src.get("SIM_RECORDED_TRACE"):
        raise RecordedRunPublishRefused(
            "SIM_RECORDED_TRACE is set: a recorded/mock run may NEVER publish, "
            "promote an atom, or feed the board pack (ARCH1 FRAME §4, R15 fail-closed)."
        )
