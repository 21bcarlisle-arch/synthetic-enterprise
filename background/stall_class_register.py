"""THE stall-class register -- HX2's deliverable to HX1.

`docs/design/maturity_map.yaml`'s HX1 cell states its dependency plainly: "Depends on
HX2 (stall-set coverage) for its stall-class input completeness" and its own exit
criteria demand the counter be "a PURE FUNCTION of primary state... independence, R15
pattern TAUTOLOGY guard" that must "REJECT" on missing inputs (FAIL-OPEN guard). HX2's
own exit criteria (§3): "the stall-class set consumed by HX1 is the UNION of prior
detectors + these verdicts, enumerated in ONE place so HX1 cannot silently miss a class
(FAIL-SILENT guard)." This module is that one place.

HOW TO READ THIS: `evaluate_stall_class_register()` returns one `StallCheckResult` per
LIVE, directly-callable class (the four HX2 was minted to cover, plus the two prior
classes that already have a clean boolean primary-state predicate). Two prior classes
have NO simple boolean "active now" predicate to call (see `CITED_ONLY_CLASSES` below,
with the reason each is cited rather than wrapped) -- HX1 must account for those by
whatever mechanism it builds for cumulative/retrospective signals; they are enumerated
here so their omission is a decision, not an oversight.

STATUS VALUES (never collapse "unavailable" into "clear" -- R15 FAIL-SILENT doctrine):
  - "fired"       -- the detector ran and found the stall-class condition TRUE.
  - "clear"       -- the detector ran successfully and found nothing.
  - "unavailable" -- the detector could not run (a state file exists but is corrupt, a
                     git command failed, etc.) -- this must NEVER be read as "clear" by
                     a caller counting toward N=3 clean advances.

VERDICTS ON THE FOUR DIRECTOR-NAMED EVENTS (§3 of `DIRECTOR_RULING_HARNESS_EXIT_
CRITERION_RATIFIED_2026-07-27.md`), summarised -- full evidence in
`docs/design/HX2_STALL_SET_COVERAGE_VERDICT.md`:

  E1 console-rescue            -> ADDED   `background/console_rescue_detector.py`
  E2 publish-gate-wedge >1h    -> ALREADY DETECTED `supervisor._publish_gate_wedge_
                                   active()` (and, as of sibling-fork commit
                                   `869c8e57c` 2026-08-03, correctly CLEARS on a
                                   healthy publisher again -- see the design doc)
  E3 origin-freeze/push >30min -> ADDED   `background/origin_freeze_detector.py`
  E4 advisor-restart-ruling    -> ADDED   `background/advisor_restart_ruling_detector.py`
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

PROJECT_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class StallCheckResult:
    class_id: str
    status: str          # "fired" | "clear" | "unavailable"
    detail: str | None    # the detector's own message (fired) or the caught error (unavailable)
    verdict: str          # "already_detected" | "added" (HX2's disposition of this class)
    source: str            # module.function citation


def _safe_call(fn: Callable[[], str | None]) -> tuple[str, str | None]:
    """Run one detector, classifying its outcome per the FAIL-SILENT doctrine: an
    exception (the detector's own `*Unavailable` type, or anything else -- a detector
    that dies in an unexpected way is EVEN LESS available, not more clear) becomes
    status='unavailable', never 'clear'."""
    try:
        result = fn()
    except Exception as exc:  # noqa: BLE001 -- deliberately broad, see docstring
        return "unavailable", f"{type(exc).__name__}: {exc}"
    return ("fired" if result else "clear"), result


def evaluate_stall_class_register(now: float | None = None) -> dict[str, StallCheckResult]:
    """Evaluate every directly-callable stall class from PRIMARY STATE ONLY and return
    one `StallCheckResult` per class, keyed by class_id. Never raises -- each class's
    own failure is captured as that class's `unavailable` status, so one broken
    detector cannot hide the others (or silently pass as clear)."""
    now = time.time() if now is None else now

    from background.console_rescue_detector import console_rescue_active
    from background.origin_freeze_detector import origin_freeze_active
    from background.advisor_restart_ruling_detector import advisor_restart_ruling_active
    from background.supervisor import (
        _publish_gate_wedge_active,
        _load_map_exhausted_state,
        _unconsumed_director_ruling_or_steer,
    )

    def _map_exhausted_check() -> str | None:
        state = _load_map_exhausted_state()
        if state.get("exhausted"):
            return (
                "MAP EXHAUSTED (prior class, cited): the self-refill draw found no "
                "candidate atom at all -- see supervisor.check_map_exhausted_escalation."
            )
        return None

    def _harden_while_unminted_check() -> str | None:
        if _unconsumed_director_ruling_or_steer():
            return (
                "HARDEN-WHILE-UNMINTED precursor (prior class, cited): an unconsumed "
                "[DIRECTOR-RULING]/[STEER] sits in docs/staging/ root -- if a HARDEN "
                "re-verify draws anyway while this is True, THAT draw is the stall "
                "event (supervisor._unconsumed_director_ruling_or_steer names the "
                "precondition; the composite 'HARDEN drew anyway' event is a property "
                "of the draw log, out of HX2's scope -- flagged for HX1)."
            )
        return None

    checks: dict[str, tuple[Callable[[], str | None], str, str]] = {
        "console_rescue": (
            lambda: console_rescue_active(now=now),
            "added",
            "background.console_rescue_detector.console_rescue_active",
        ),
        "publish_gate_wedge": (
            lambda: _publish_gate_wedge_active(now=now),
            "already_detected",
            "background.supervisor._publish_gate_wedge_active",
        ),
        "origin_freeze": (
            lambda: origin_freeze_active(now=now),
            "added",
            "background.origin_freeze_detector.origin_freeze_active",
        ),
        "advisor_restart_ruling": (
            lambda: advisor_restart_ruling_active(),
            "added",
            "background.advisor_restart_ruling_detector.advisor_restart_ruling_active",
        ),
        "map_exhausted_draw_failure": (
            _map_exhausted_check,
            "already_detected",
            "background.supervisor._load_map_exhausted_state "
            "(+ check_map_exhausted_escalation)",
        ),
        "harden_while_content_unminted": (
            _harden_while_unminted_check,
            "already_detected",
            "background.supervisor._unconsumed_director_ruling_or_steer",
        ),
    }

    out: dict[str, StallCheckResult] = {}
    for class_id, (fn, verdict, source) in checks.items():
        status, detail = _safe_call(fn)
        out[class_id] = StallCheckResult(
            class_id=class_id, status=status, detail=detail, verdict=verdict, source=source,
        )
    return out


# Prior stall classes from the ratified proposal's original five (`docs/design/
# HARNESS_EXIT_CRITERION_PROPOSAL_2026-07-27.md` §2) that HX2 does NOT wrap as a
# directly-callable predicate here, with the reason -- enumerated so their absence
# above is a stated decision, not a silent gap (the exact FAIL-SILENT failure mode
# this whole register exists to prevent).
CITED_ONLY_CLASSES: dict[str, dict[str, str]] = {
    "idle_turn_with_atoms": {
        "reason": (
            "supervisor.IDLE_TURN_COUNTER_FILE / _record_idle_turn() track an "
            "ALL-TIME CUMULATIVE count of genuinely-idle cycles, not a queryable "
            "'is the loop idle-with-atoms-available RIGHT NOW' boolean -- there is no "
            "single primary-state read that answers the live predicate the way "
            "e.g. _load_map_exhausted_state() does. HX1 needs a WINDOWED delta "
            "(count-at-span-start vs count-at-span-end) to use this as a per-span "
            "signal; that windowing is HX1's counter-construction concern, not a "
            "missing detector."
        ),
        "source": "background.supervisor._record_idle_turn / IDLE_TURN_COUNTER_FILE",
    },
    "director_hand_types_next_atom": {
        "reason": (
            "The R3 incident this named (docs/staging/done/R3_WORK_GRANTING_"
            "REDESIGN.md, 2026-07-12) never produced its own machine-readable "
            "detector -- the FIX was the backlog-driven-draw redesign (R3) that "
            "makes the underlying idle state near-impossible, not a standing "
            "detector of the act of hand-typing. HX2's new console_rescue_active() "
            "SUBSUMES this: a console sanctified while a STUCK streak is already "
            "escalated covers 'the director had to intervene at the terminal' "
            "regardless of whether the intervention was typing an atom ID or "
            "something else -- see console_rescue_active's docstring. Kept as its "
            "own cited entry (not silently merged) because HX1 may still want the "
            "distinction if a future incident narrows it further."
        ),
        "source": "docs/staging/done/R3_WORK_GRANTING_REDESIGN.md "
                  "(subsumed by background.console_rescue_detector.console_rescue_active)",
    },
    "later_ruled_reversible_act": {
        "reason": (
            "By construction this class can only be evaluated IN HINDSIGHT -- an "
            "[ACT] escalation only becomes this stall class once the director rules "
            "it was reversible, which is a judgment recorded after the fact, not a "
            "primary-state condition a detector can observe at the time. "
            "docs/design/ESCALATION_REVERSIBILITY_AUDIT.md is the existing "
            "audit mechanism (MAKE_IT_STICK's anti-decay metric); "
            "background.decision_log.read_decision_log()/count_since() are the "
            "queryable primary-state log this audit reads. HX1 should treat a NEW "
            "audit-flagged reversible escalation within the span as this class's "
            "signal, not attempt a live predicate."
        ),
        "source": "docs/design/ESCALATION_REVERSIBILITY_AUDIT.md "
                  "+ background.decision_log.read_decision_log",
    },
}
