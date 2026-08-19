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

import math
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional, Tuple

SAVED = "saved"
SPENT = "spent"
_LEDGERS: Tuple[str, ...] = (SAVED, SPENT)

# Provenance enum, matching the fidelity ledger's vocabulary (DISCOVER §2).
_PROVENANCE_KINDS: Tuple[str, ...] = ("estimated_from_data", "assumed", "asserted")

# Row status vocabulary (E5 FRAME control C1 -- "absent feed must never read as 0.0").
OK = "ok"                    # the row rests on events on every side it needs
NO_SOURCE = "no_source"      # no events at all -- the row is an ABSENCE, not a measurement of zero
ONE_SIDED = "one_sided"      # NET only: one ledger is empty, so the net IS the other ledger


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
        # NON-FINITE FIRST (2026-07-29, E5 FRAME finding; same class already hardened on the
        # D5 billing ledger). A comparison guard is NaN-BLIND: `nan < 0` is False and `nan` IS
        # a float, so NaN and inf both walked straight through the check below. The consequence
        # was not local -- NaN propagates through saved()/spent() into net(), and `nan <= 0` is
        # ALSO False, so cost_per_tonne_abated's fail-loud door at :148 was BYPASSED and the
        # mission metric RETURNED nan instead of raising. That is precisely the "must never read
        # as free/great" fail-open this module's own docstring (c) forbids, reached through the
        # one comparison that cannot be written as a comparison. Reject non-finite BEFORE any
        # ordering test; bool is excluded because `isinstance(True, int)` is True and a boolean
        # tonnage is a malformed event, not 1 tCO2e.
        if isinstance(self.tco2e, bool) or not isinstance(self.tco2e, (int, float)):
            raise CarbonEventMalformed(
                f"tco2e must be a non-negative magnitude (sign lives in the ledger), got {self.tco2e!r}"
            )
        if not math.isfinite(self.tco2e):
            raise CarbonEventMalformed(
                f"tco2e must be FINITE -- a non-finite tonnage silently defeats every downstream "
                f"comparison guard (nan < 0 and nan <= 0 are both False), got {self.tco2e!r}"
            )
        if self.tco2e < 0:
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


@dataclass(frozen=True)
class LedgerRow:
    """One row of the three-ledger block: a tonnage that CANNOT be obtained without
    its labels (the R14 analogue for carbon — FRAME §2, the CLOCK x BASIS x
    PROVENANCE triple).

    WHY THIS TYPE EXISTS. `CarbonEvent.__post_init__` spends four separate
    fail-closed guards making `basis`, `provenance` and `as_of` MANDATORY on every
    event — and aggregation then threw all three away, because `three_ledger_view`
    returned three bare floats. The labels were never missing; they were DESTROYED
    at the one method whose output is the publishable headline. So a carbon figure
    could reach a reader with no accounting basis, no provenance mix and no as-of,
    while every event behind it was fully labelled. Returning the labels costs no
    new data collection at all — only the refusal to drop them.

    `bases` is a TUPLE, never a single string. Tonnes computed on a grid-marginal
    basis and tonnes computed on a grid-average basis are not the same unit, so a
    scalar basis label on a mixed aggregate would be a false claim about a real
    number. When `len(bases) > 1` the row is mixed and says so, rather than
    reporting whichever basis happened to arrive first.

    `provenance_mix` is weighted by TONNAGE, not by event count, because the
    question a reader has is "how much of this number is assumed?" — and one large
    `assumed` event among many small `estimated_from_data` ones is exactly the case
    an event-count weighting would hide."""

    tco2e: float
    status: str                          # ok | no_source | one_sided
    bases: Tuple[str, ...]
    provenance_mix: Mapping[str, float]  # provenance -> share of |tonnage|, tonnage-weighted
    as_of_earliest: Optional[str]
    as_of_latest: Optional[str]
    event_count: int

    @property
    def mixed_basis(self) -> bool:
        """True when the row aggregates more than one accounting basis — the reader
        needs this before comparing the number to anything."""
        return len(self.bases) > 1


def _provenance_mix(events: Tuple[CarbonEvent, ...]) -> Mapping[str, float]:
    """Tonnage-weighted share per provenance kind. Returns {} when total tonnage is
    zero: with nothing to attribute, ANY mix would be invented, and an invented
    '100% estimated_from_data' is precisely the flattering label this block exists
    to prevent."""
    total = float(sum(e.tco2e for e in events))
    if total <= 0:
        return {}
    mix: Dict[str, float] = {}
    for e in events:
        if e.tco2e:
            mix[e.provenance] = mix.get(e.provenance, 0.0) + e.tco2e / total
    return mix


def _row(tco2e: float, status: str, events: Tuple[CarbonEvent, ...]) -> LedgerRow:
    stamps = sorted(e.as_of for e in events)
    return LedgerRow(
        tco2e=float(tco2e),
        status=status,
        bases=tuple(sorted({e.basis for e in events})),
        provenance_mix=_provenance_mix(events),
        as_of_earliest=stamps[0] if stamps else None,
        as_of_latest=stamps[-1] if stamps else None,
        event_count=len(events),
    )


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

    def _events_in(self, ledger: str) -> Tuple[CarbonEvent, ...]:
        return tuple(e for e in self.events() if e.ledger == ledger)

    def net_status(self) -> str:
        """Whether NET rests on BOTH ledgers, one, or neither.

        THE FAIL-OPEN THIS NAMES (E5 FRAME, control C1). With no SPENT events,
        `net()` is `saved() - 0.0` == `saved()` — so the mission metric reports its
        BEST POSSIBLE value exactly WHEN the operational-carbon feed is missing.
        Nothing about that reads as broken: it is a plausible number, derived by
        correct arithmetic, from an absence. The FRAME found the SPENT feed is in
        fact unbuilt (there is no token sensor and no compute-kWh meter), so this
        is the live state of the ledger, not a hypothetical.

        Arithmetic cannot distinguish "we emitted nothing" from "we did not
        measure what we emitted", so the STATUS carries what the number cannot."""
        has = {lg: bool(self._events_in(lg)) for lg in _LEDGERS}
        if not any(has.values()):
            return NO_SOURCE
        if not all(has.values()):
            return ONE_SIDED
        return OK

    def cost_per_tonne_abated(self, cost_gbp: float) -> float:
        """£/tCO2e = cost / NET abated (the mission metric, a DIAGNOSTIC — R12).
        FAIL-LOUD: raises `CarbonAbatementUnavailable` when net <= 0, because
        there is no defensible cost-per-tonne when nothing (or negative) was
        abated — a 0 or inf would read as 'free'/'great', the fail-open the
        constraint forbids. This method is measurement ONLY; nothing in the
        machine may call it to steer a decision (CARBON_NOT_A_TARGET).

        ALSO fail-loud on a ONE-SIDED net (2026-08-19): a £/tCO2e whose net counts
        abatement but no operational emissions is not a conservative estimate, it
        is an unbounded one — and it is at its most flattering precisely when a
        feed is absent. "A claim that counts one side is not a claim" is the
        module's own rule; this is that rule reaching the metric it was written
        for. An absent SPENT ledger must read as UNAVAILABLE, never as cheap."""
        status = self.net_status()
        if status != OK:
            raise CarbonAbatementUnavailable(
                f"no defensible £/tCO2e: the carbon ledger is {status!r} -- a net computed "
                "with an empty SAVED or SPENT ledger reports its most flattering value BECAUSE "
                "a feed is missing. Report the absence; never price against half a ledger"
            )
        net = self.net()
        # Defence in depth (2026-07-29): the event guard should make a non-finite net
        # unreachable, but this door is the one the constraint actually rests on, so it does
        # not delegate its own safety to a guard in another class. `nan <= 0` is False, so
        # without this the fail-loud door opens for the single worst input.
        if not math.isfinite(net):
            raise CarbonAbatementUnavailable(
                f"no defensible £/tCO2e: net abatement is non-finite ({net!r}) -- a non-finite "
                "net defeats the <= 0 door below and would return nan/inf as if it were a rate"
            )
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

    def three_ledger_view(self) -> Mapping[str, LedgerRow]:
        """The honest headline block: all three rows, NET always present, each row
        carrying its own basis / provenance mix / as-of span and status.

        THERE IS DELIBERATELY NO UNLABELLED VARIANT of this method. R14's rule is
        that a figure cannot be obtained WITHOUT its clock — a second accessor
        returning bare floats would be the escape hatch a publisher reaches for,
        and the labels would be back to optional. The numbers are still on the row
        (`.tco2e`) for anyone who genuinely only needs arithmetic; what is gone is
        the ability to serialise the block without noticing the labels exist."""
        saved_events = self._events_in(SAVED)
        spent_events = self._events_in(SPENT)
        net_status = self.net_status()
        return {
            "saved_tco2e": _row(self.saved(), OK if saved_events else NO_SOURCE, saved_events),
            "spent_tco2e": _row(self.spent(), OK if spent_events else NO_SOURCE, spent_events),
            # NET's labels are the UNION of both sides -- it is a claim about both,
            # so it inherits every basis and the full provenance mix behind it.
            "net_tco2e": _row(self.net(), net_status, saved_events + spent_events),
        }
