"""MeterReadPort -- structural interface + versioned message for the meter-read
arrival flow crossing the SIM/billing seam (D0010-style actual reads and the
supplier's own estimated-read fallback when no actual arrives in time).

First reference-flow conversion of the WALLED_INTERFACES programme
(docs/design/WALLED_INTERFACES_SKETCH.md step 2, maturity_map atom
W4_1_typed_adapters). Same adapter pattern as tools/market_data_port.py::
MarketDataPort (Phase PV) and tools/credit_bureau_port.py::CreditBureauPort:
a `runtime_checkable` Protocol that adapters satisfy without inheritance, plus
a frozen, schema-versioned message dataclass. Going live becomes swapping the
sim adapter for a real DTC/Elexon D0010 feed behind this unchanged Protocol,
not a rewrite.

This is a SHAPE change to already-correct data, not new business logic. The
message carries exactly the same fields simulation/meter_reads.py already
produces (see MeterReadEvent / generate_meter_read_log), losslessly, plus a
`schema_version`. `from_log_entry` / `to_log_entry` round-trip is the identity
on the existing dict, so every current downstream consumer of `meter_read_log`
is unaffected.

Epistemic boundary (CLAUDE.md Architectural Law #2 -- the company cannot see
inside the SIM): the OBSERVABLE value a supplier's billing engine consumes is
`billed_consumption_kwh` -- the actual read when one arrived, otherwise the
supplier's OWN estimate built from that customer's prior confirmed reads.
MeterReadMessage also carries `true_consumption_kwh`, the SIM's ground-truth
consumption for the period, for evidence/divergence-analytics use ONLY --
identical treatment to CreditCheckResult.true_creditworthy. company/** billing-
decision code must NEVER read `true_consumption_kwh` when status == "estimated":
that value is not knowable at bill time. Use `billed_consumption_kwh` (which
enforces this by construction) for anything the company is allowed to see.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable

# Bump on any breaking change to the message field set / semantics. New readers
# should tolerate an unfamiliar version rather than assume 1.0's exact shape.
SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class MeterReadMessage:
    """One customer-period meter-read event as a versioned typed message.

    Field set mirrors simulation.meter_reads.MeterReadEvent exactly (the dict
    generate_meter_read_log emits), so the crossing is a transport-shape change
    only. `true_consumption_kwh` is SIM-internal ground truth -- see the module
    docstring's epistemic note; read `billed_consumption_kwh` instead.
    """

    customer_id: str
    period_end: str
    meter_type: str  # "smart" | "traditional"
    delay_days: int
    status: str  # "actual" | "estimated"
    estimated_consumption_kwh: Optional[float] = None
    true_consumption_kwh: Optional[float] = None
    consecutive_estimated_count: int = 0
    forced_catch_up: bool = False
    schema_version: str = SCHEMA_VERSION

    @property
    def billed_consumption_kwh(self) -> Optional[float]:
        """The company-observable consumption billing may consume for this
        period: the actual read value when status == "actual", otherwise the
        supplier's own estimate. Never exposes ground truth for an estimated
        period -- this is the observable-only accessor the epistemic wall
        permits, matching what tools/generate_billing_ledger.py already does by
        branching on `status`.
        """
        if self.status == "actual":
            return self.true_consumption_kwh
        return self.estimated_consumption_kwh

    @classmethod
    def from_log_entry(cls, entry: dict) -> "MeterReadMessage":
        """Build a message from an existing generate_meter_read_log dict.

        Absent `schema_version` (all pre-conversion data) defaults to
        SCHEMA_VERSION, so historical run outputs load unchanged.
        """
        return cls(
            customer_id=entry["customer_id"],
            period_end=entry["period_end"],
            meter_type=entry["meter_type"],
            delay_days=entry["delay_days"],
            status=entry["status"],
            estimated_consumption_kwh=entry.get("estimated_consumption_kwh"),
            true_consumption_kwh=entry.get("true_consumption_kwh"),
            consecutive_estimated_count=entry.get("consecutive_estimated_count", 0),
            forced_catch_up=entry.get("forced_catch_up", False),
            schema_version=entry.get("schema_version", SCHEMA_VERSION),
        )

    def to_log_entry(self, include_schema_version: bool = False) -> dict:
        """Serialise back to the plain JSON-serialisable dict shape existing
        consumers expect. `include_schema_version` is opt-in so the default
        output is byte-for-byte the pre-conversion `meter_read_log` entry
        (lossless identity round-trip); callers migrating to the versioned
        wire can set it True.
        """
        entry = {
            "customer_id": self.customer_id,
            "period_end": self.period_end,
            "meter_type": self.meter_type,
            "delay_days": self.delay_days,
            "status": self.status,
            "estimated_consumption_kwh": self.estimated_consumption_kwh,
            "true_consumption_kwh": self.true_consumption_kwh,
            "consecutive_estimated_count": self.consecutive_estimated_count,
            "forced_catch_up": self.forced_catch_up,
        }
        if include_schema_version:
            entry["schema_version"] = self.schema_version
        return entry


@runtime_checkable
class MeterReadPort(Protocol):
    """Structural interface for a meter-read source. The sim adapter wraps
    simulation.meter_reads.generate_meter_read_log; a real deployment slots a
    DTC/Elexon D0010 feed adapter in behind this same signature with zero
    consumer-layer changes.
    """

    def get_meter_reads(self) -> list[MeterReadMessage]: ...
