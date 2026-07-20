"""E5 — the carbon three-ledger: the company's carbon P&L (SAVED / SPENT / NET).

PURPOSE (PURPOSE_PITCH_V4 §9). Carbon abatement through personalisation is the
mission, measured as £ per tonne of CO2e = (cost to serve + cost to persuade,
incl. compute) / carbon abated. A claim that counts one side is not a claim, so
carbon is a THREE-ledger P&L:

  SAVED  — CO2e a household would have emitted but did NOT, because of an
           intervention. A COUNTERFACTUAL, and the company's own ESTIMATE of it
           (a belief a real supplier forms from a methodology, never ground
           truth) — the belief-vs-truth gap against the in-sim counterfactual is
           a later, harness-side rung, not this module.
  SPENT  — CO2e emitted serving them: people, compute, tokens (ties the
           near-zero-marginal-cost claim + the token sensor).
  NET    — SAVED - SPENT, ALWAYS reported (the honest headline). Never hidden,
           even when negative (a company that spends more carbon than it saves
           shows a negative NET, it does not omit the row).

THE BINDING WALL (CARBON_NOT_A_TARGET_CONSTRAINT.md — the same law as R12/LAW A).
£/tCO2e and every metric derived from it is a DIAGNOSTIC: measured, reported,
inspected — NEVER optimised, never a reward/selection/ranking input. This module
is enforced read-only to decision surfaces THREE ways:
  (a) it exposes ONLY measurement/reporting — no reward hook, no "improve carbon"
      method, nothing a selection loop could call;
  (b) `tests/company/test_carbon_not_a_target.py` is a grep-guard: no decision
      surface (fitness function, atom draw, risk committee, pricing/
      personalisation reward) may import a carbon metric — mutation-tested;
  (c) FAIL-LOUD: an unavailable / zero / negative abatement can never read as
      "great" or "free" — `cost_per_tonne_abated` RAISES rather than return 0/inf.

DATA MODEL (DISCOVER §1, behind the append-only-event discipline). SAVED/SPENT/
NET and £/tCO2e are DERIVED VIEWS over an append-only `CarbonEvent` stream —
never stored scalars that can drift (same discipline as the R14 clocks and the
fidelity evidence ledger). Idempotent + replayable (C-S2: keyed by `event_id`,
adding an event twice is harmless, replaying a history reproduces identical
views); event-arrival tolerant (C-S1: events may arrive one at a time, late, or
out of order — the derived views never depend on arrival order).

SCOPE OF THIS RUNG. The data model + the diagnostic guard, on synthetic events —
factor-agnostic (tCO2e values are handed in; the emissions-factor set and the
counterfactual method are DIRECTOR VALUES-CALLS, surfaced by the DISCOVER doc,
not decided here). The live SAVED feed depends on the per-household cost-and-
carbon trajectory (unbuilt) and is a later rung.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Tuple

SAVED = "saved"
SPENT = "spent"
_LEDGERS: Tuple[str, ...] = (SAVED, SPENT)

# Provenance enum, matching the fidelity ledger's vocabulary (DISCOVER §2).
_PROVENANCE_KINDS: Tuple[str, ...] = ("estimated_from_data", "assumed", "asserted")


class CarbonEventMalformed(ValueError):
    """Fail-closed on a structurally invalid event (wrong ledger/sign/provenance/
    missing id) — an ill-formed carbon event is never silently absorbed."""


class CarbonAbatementUnavailable(Exception):
    """Raised by `cost_per_tonne_abated` when net abatement is <= 0. There is no
    defensible £/tCO2e when nothing (or negative) was abated; returning 0 or inf
    would read as 'free'/'great' — the exact fail-open the constraint forbids."""


@dataclass(frozen=True)
class CarbonEvent:
    """One entry in the carbon P&L. `tco2e` is a NON-NEGATIVE MAGNITUDE tagged by
    `ledger` (SAVED = avoided emissions; SPENT = incurred emissions) — the sign
    lives in the ledger, not the number, so a derived view can never accidentally
    add an abatement to an emission. `event_id` makes the stream idempotent."""

    event_id: str
    ledger: str            # SAVED | SPENT
    source: str            # household_id (SAVED/SPENT-to-serve) or operational source (SPENT)
    tco2e: float           # non-negative magnitude
    basis: str             # e.g. grid_marginal | grid_average | activity_based -- the accounting basis
    provenance: str        # estimated_from_data | assumed | asserted
    as_of: str             # PIT stamp

    def __post_init__(self) -> None:
        if not self.event_id:
            raise CarbonEventMalformed("event_id must be non-empty")
        if self.ledger not in _LEDGERS:
            raise CarbonEventMalformed(f"ledger must be one of {_LEDGERS}, got {self.ledger!r}")
        if not isinstance(self.tco2e, (int, float)) or self.tco2e < 0:
            raise CarbonEventMalformed(
                f"tco2e must be a non-negative magnitude (sign lives in the ledger), got {self.tco2e!r}"
            )
        if not self.basis:
            raise CarbonEventMalformed("basis must be non-empty (a carbon figure without its basis is a defect)")
        if self.provenance not in _PROVENANCE_KINDS:
            raise CarbonEventMalformed(
                f"provenance must be one of {_PROVENANCE_KINDS}, got {self.provenance!r}"
            )
        if not self.as_of:
            raise CarbonEventMalformed("as_of (PIT stamp) is required")


class CarbonLedger:
    """Append-only carbon-event stream with DERIVED SAVED/SPENT/NET/£-per-tonne
    views. Pure accounting — no sim/company-internal read, no decision hook.
    Idempotent (keyed by event_id) and arrival-order-independent."""

    def __init__(self) -> None:
        self._events: Dict[str, CarbonEvent] = {}

    # -- ingestion (idempotent, C-S2) --------------------------------------

    def add(self, event: CarbonEvent) -> None:
        """Record one event. Re-adding the same `event_id` is a harmless no-op
        (idempotent replay), NOT a double count."""
        self._events[event.event_id] = event

    def extend(self, events: Iterable[CarbonEvent]) -> None:
        for e in events:
            self.add(e)

    # -- derived views (never stored scalars) ------------------------------

    def _sum(self, ledger: str) -> float:
        return float(sum(e.tco2e for e in self._events.values() if e.ledger == ledger))

    def saved(self) -> float:
        """Total CO2e ABATED (avoided). Derived, order-independent."""
        return self._sum(SAVED)

    def spent(self) -> float:
        """Total CO2e EMITTED serving customers (people + compute + tokens)."""
        return self._sum(SPENT)

    def net(self) -> float:
        """SAVED - SPENT — ALWAYS reported, positive OR negative (the honest
        headline; a claim that counts one side is not a claim)."""
        return self.saved() - self.spent()

    def cost_per_tonne_abated(self, cost_gbp: float) -> float:
        """£/tCO2e = cost / NET abated (the mission metric, a DIAGNOSTIC — R12).
        FAIL-LOUD: raises `CarbonAbatementUnavailable` when net <= 0, because
        there is no defensible cost-per-tonne when nothing (or negative) was
        abated — a 0 or inf would read as 'free'/'great', the fail-open the
        constraint forbids. This method is measurement ONLY; nothing in the
        machine may call it to steer a decision (CARBON_NOT_A_TARGET)."""
        net = self.net()
        if net <= 0:
            raise CarbonAbatementUnavailable(
                f"no defensible £/tCO2e: net abatement is {net:.6g} tCO2e (<= 0) -- "
                "a zero/negative abatement has no cost-per-tonne and must NOT read as cheap/great"
            )
        return float(cost_gbp) / net

    # -- inspection --------------------------------------------------------

    def events(self) -> Tuple[CarbonEvent, ...]:
        """All events in stable (event_id-sorted) order — order-independent view."""
        return tuple(self._events[k] for k in sorted(self._events))

    def events_for(self, source: str) -> Tuple[CarbonEvent, ...]:
        return tuple(e for e in self.events() if e.source == source)

    def three_ledger_view(self) -> Mapping[str, float]:
        """The honest headline block: all three rows, NET always present."""
        return {"saved_tco2e": self.saved(), "spent_tco2e": self.spent(), "net_tco2e": self.net()}
