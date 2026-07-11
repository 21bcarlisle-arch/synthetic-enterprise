"""AcquisitionFunnelPort -- structural interface + versioned messages for the
acquisition-funnel stage-transition flow crossing the SIM/company seam (quote ->
application -> credit_check -> onboarding -> cooling_off, the real supplier-switch
process an industry Switching Programme message set would carry).

Second reference-flow conversion of the WALLED_INTERFACES programme
(docs/design/WALLED_INTERFACES_SKETCH.md step 3 "generalize the pattern",
maturity_map atom W4_1_typed_adapters). Same adapter pattern as
tools/meter_read_port.py::MeterReadPort (the first reference flow),
tools/market_data_port.py::MarketDataPort (Phase PV) and
tools/credit_bureau_port.py::CreditBureauPort: a `runtime_checkable` Protocol
adapters satisfy without inheritance, plus frozen, schema-versioned message
dataclasses. Going live becomes swapping the sim adapter for a real Switching
Programme / CSS (Central Switching Service) feed behind this unchanged Protocol,
not a rewrite.

This is a SHAPE change to already-correct data, not new business logic. Like
meter reads, the funnel result does NOT cross the wall as a live Python
dataclass: simulation/run_phase2b.py runs simulation.acquisition_funnel.
run_acquisition_funnel() (which returns an AcquisitionFunnelResult), then
immediately serialises a projection of it into the plain-dict list
`acquisition_funnel_log` written to sim_data.json. That dict list is what
actually crosses into saas/company/tools code (saas/reporting/annual_report.py,
tools/generate_dashboard_data.py, tools/generate_shadow_html.py,
tools/population_anchor.py). These messages type exactly that crossing dict,
losslessly, plus a `schema_version`. `from_log_entry` / `to_log_entry` round-trip
is the identity on the existing dict, so every current downstream consumer of
`acquisition_funnel_log` is unaffected.

Note the seam is deliberately NARROWER than the internal dataclass: the crossing
dict carries per-stage `{stage, passed, stage_date}` but NOT the internal
`FunnelStageEvent.cost_increment_gbp` (no consumer reads per-stage cost; the
crossing's cost field is the aggregate `total_cost_gbp`), and it ADDS
`billing_account` from run_phase2b's loop context (not a field of the result
object). These messages mirror the crossing, not the internal object -- the seam
is what saas/company are allowed to see, which is the whole point.

Epistemic boundary (CLAUDE.md Architectural Law #2 -- the company cannot see
inside the SIM): the OBSERVABLE credit signal a supplier's acquisition decision
consumes is `credit_bureau_passed` / `credit_bureau_score_band` -- the imperfect,
purchased bureau read, identical treatment to
tools.credit_bureau_port.CreditCheckResult.passed/score_band.
AcquisitionFunnelMessage also carries `credit_bureau_true_creditworthy`, the
SIM's ground-truth creditworthiness, for evidence/divergence-analytics use ONLY
(false-decline / false-accept reporting on the Sim evidence surface) -- identical
treatment to CreditCheckResult.true_creditworthy and MeterReadMessage.
true_consumption_kwh. company/** decision code must NEVER read
`credit_bureau_true_creditworthy`: a real supplier does not know an applicant's
true creditworthiness. Use the observable bureau fields for anything the company
is allowed to see. `bureau_divergence` below is an evidence-surface accessor
(analytics, not a company decision) that reads ground truth deliberately.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Protocol, runtime_checkable

# Bump on any breaking change to the message field set / semantics. New readers
# should tolerate an unfamiliar version rather than assume 1.0's exact shape.
SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class FunnelStageMessage:
    """One funnel stage transition as a versioned typed message.

    Field set mirrors the per-stage dict simulation/run_phase2b.py emits into
    each `acquisition_funnel_log` entry's `stages` list exactly -- {stage,
    passed, stage_date} -- so the crossing is a transport-shape change only.
    `cost_increment_gbp` (present on the internal FunnelStageEvent dataclass) is
    intentionally NOT carried: it is not part of the seam, no consumer reads it,
    and the aggregate cost crosses as AcquisitionFunnelMessage.total_cost_gbp.
    """

    stage: str  # one of simulation.acquisition_funnel.FUNNEL_STAGES
    passed: bool
    stage_date: str  # ISO date -- real calendar spacing from quote (Phase 3 item 5)

    @classmethod
    def from_log_entry(cls, entry: dict) -> "FunnelStageMessage":
        return cls(
            stage=entry["stage"],
            passed=entry["passed"],
            stage_date=entry["stage_date"],
        )

    def to_log_entry(self) -> dict:
        """Serialise back to the plain dict shape existing consumers expect
        (lossless identity round-trip on the pre-conversion stage dict)."""
        return {
            "stage": self.stage,
            "passed": self.passed,
            "stage_date": self.stage_date,
        }


@dataclass(frozen=True)
class AcquisitionFunnelMessage:
    """One acquisition attempt's funnel outcome as a versioned typed message.

    Field set mirrors the `acquisition_funnel_log` entry simulation/run_phase2b.py
    emits exactly, so the crossing is a transport-shape change only.
    `credit_bureau_true_creditworthy` is SIM-internal ground truth -- see the
    module docstring's epistemic note; company decision code reads the observable
    `credit_bureau_passed` / `credit_bureau_score_band` instead.
    """

    billing_account: str
    segment: str
    term_start: str  # ISO date string (the quote-issued date, entry-point semantics)
    won: bool  # True iff survived cooling_off
    stage_reached: str  # last stage attempted, whether passed or failed
    total_cost_gbp: float
    credit_bureau_score_band: Optional[str] = None  # None if credit_check never reached
    credit_bureau_passed: Optional[bool] = None  # None if credit_check never reached
    credit_bureau_true_creditworthy: Optional[bool] = None  # SIM ground truth; analytics only
    stages: tuple[FunnelStageMessage, ...] = field(default_factory=tuple)
    schema_version: str = SCHEMA_VERSION

    @property
    def bureau_divergence(self) -> Optional[bool]:
        """Evidence-surface accessor: did the observable bureau decision diverge
        from the SIM's ground truth (a false-decline / false-accept)? None when
        credit_check was never reached or the bureau exposes no ground truth.

        This DELIBERATELY reads ground truth -- it is for the Sim divergence
        evidence surface only (matches tools/generate_shadow_html.py's existing
        `credit_bureau_passed != credit_bureau_true_creditworthy` computation),
        NOT a company decision. company/** must never call this to drive an
        accept/reject; use `credit_bureau_passed` for that.
        """
        if self.credit_bureau_passed is None or self.credit_bureau_true_creditworthy is None:
            return None
        return self.credit_bureau_passed != self.credit_bureau_true_creditworthy

    @classmethod
    def from_log_entry(cls, entry: dict) -> "AcquisitionFunnelMessage":
        """Build a message from an existing acquisition_funnel_log dict.

        Absent `schema_version` (all pre-conversion data) defaults to
        SCHEMA_VERSION, so historical run outputs load unchanged.
        """
        return cls(
            billing_account=entry["billing_account"],
            segment=entry["segment"],
            term_start=entry["term_start"],
            won=entry["won"],
            stage_reached=entry["stage_reached"],
            total_cost_gbp=entry["total_cost_gbp"],
            credit_bureau_score_band=entry.get("credit_bureau_score_band"),
            credit_bureau_passed=entry.get("credit_bureau_passed"),
            credit_bureau_true_creditworthy=entry.get("credit_bureau_true_creditworthy"),
            stages=tuple(
                FunnelStageMessage.from_log_entry(s) for s in entry.get("stages", [])
            ),
            schema_version=entry.get("schema_version", SCHEMA_VERSION),
        )

    def to_log_entry(self, include_schema_version: bool = False) -> dict:
        """Serialise back to the plain JSON-serialisable dict shape existing
        consumers expect. `include_schema_version` is opt-in so the default
        output is byte-for-byte the pre-conversion `acquisition_funnel_log` entry
        (lossless identity round-trip); callers migrating to the versioned wire
        can set it True.
        """
        entry = {
            "billing_account": self.billing_account,
            "segment": self.segment,
            "term_start": self.term_start,
            "won": self.won,
            "stage_reached": self.stage_reached,
            "total_cost_gbp": self.total_cost_gbp,
            "credit_bureau_score_band": self.credit_bureau_score_band,
            "credit_bureau_passed": self.credit_bureau_passed,
            "credit_bureau_true_creditworthy": self.credit_bureau_true_creditworthy,
            "stages": [s.to_log_entry() for s in self.stages],
        }
        if include_schema_version:
            entry["schema_version"] = self.schema_version
        return entry


@runtime_checkable
class AcquisitionFunnelPort(Protocol):
    """Structural interface for an acquisition-funnel outcome source. The sim
    adapter wraps the `acquisition_funnel_log` simulation/run_phase2b.py produces
    via simulation.acquisition_funnel.run_acquisition_funnel; a real deployment
    slots a Switching Programme / CSS feed adapter in behind this same signature
    with zero consumer-layer changes.
    """

    def get_acquisition_funnel(self) -> list[AcquisitionFunnelMessage]: ...
