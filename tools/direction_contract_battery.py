#!/usr/bin/env python3
"""R15 mutation battery for `background/direction.py`, scored PER CALLER SUITE.

The SUBJECT of this file is the spec below -- the four caller suites, the eight
contracts and the reachability anchor. The procedure that runs it lives in
`tools/contract_battery.py`, extracted there when the sweep reached its third
subject: a battery copied per subject is exactly the converged-code defect this
sweep exists to find, committed by the instrument that finds it. What the engine
guarantees, and why each guarantee is there, is documented on the engine.

Pre-registration and the eight predictions:
`docs/staging/SEAT_PREREG_WHICH_CALLER_SUITE_IS_EACH_DIRECTION_CONTRACT_STANDING_ON_2026-09-05.md`
Results, including the fourth column and the poison round that voided it:
`docs/staging/SEAT_RESULT_THE_FOURTH_COLUMN_SURVIVED_ENTIRE_AND_THE_BATTERY_PROVING_IT_HAD_NO_REACHABILITY_FLOOR_2026-09-05.md`

Usage:
    python3 -m tools.direction_contract_battery --out /var/tmp/battery.json
    python3 -m tools.direction_contract_battery --only M5 M6   # resume/subset
"""
from __future__ import annotations

from tools.contract_battery import BatterySpec, run

#: The four caller suites. `tools/generate_delivery_page.py` is the fourth
#: first-party caller and has no suite that imports it AND direction, so the
#: fourth row here is the self-audit suite -- the closest thing the module has
#: to one of its own.
SUITES = (
    "tests/background/test_supervisor.py",
    "tests/background/test_delivery_lane.py",
    "tests/background/test_delivery_seat.py",
    "tests/background/test_the_self_audit_declared_a_correction_and_nothing_carried_it.py",
)

#: The module's OWN suite, written as the repair once the four columns above showed the contracts
#: standing on borrowed suites. Deliberately NOT a member of `SUITES`: `survived_all` answers "did
#: any caller prove this", and folding the repair into that population would make the pre-registered
#: question unanswerable the moment the repair landed. It is scored as its own column.
REPAIR_SUITE = "tests/background/test_direction_contracts.py"
SELECTABLE = SUITES + (REPAIR_SUITE,)

#: (id, the contract as the module states it, old, new). Each is ONE edit to a
#: named function; each `old` must appear exactly once in the subject.
MUTATIONS = (
    (
        "M1",
        "focus_multiplier is ALWAYS >= 1.0 -- direction may only ADD attention, never filter",
        "    if not atom_id or atom_id not in focus:\n        return 1.0",
        "    if not atom_id or atom_id not in focus:\n        return 0.5",
    ),
    (
        "M2",
        "focus_weights returns weights untouched when the two lists disagree in length",
        "        if not focus or len(candidates) != len(original):",
        "        if not focus:",
    ),
    (
        "M3",
        "forbidden target-shaped keys are refused at any depth",
        "            _forbidden_keys_in(value, seen)",
        "            pass",
    ),
    (
        "M4",
        "an empty not_now is refused -- the rejections are what makes it reviewable",
        "    if not isinstance(not_now, list) or not not_now:",
        "    if not isinstance(not_now, list):",
    ),
    (
        "M5",
        "wrong[i].corrected must be a BOOLEAN, not merely present",
        '            elif not isinstance(item.get("corrected"), bool):',
        '            elif "corrected" not in item:',
    ),
    (
        "M6",
        "read_direction NEVER RAISES -- missing, unreadable and malformed are one answer",
        "    except Exception:\n        # BREADTH IS THE POINT",
        "    except FileNotFoundError:\n        # BREADTH IS THE POINT",
    ),
    (
        "M7",
        "is_live is bounded BELOW as well as above -- a future-dated record must not steer",
        "        return 0.0 <= self.age_hours(now) <= FOCUS_MAX_AGE_HOURS",
        "        return self.age_hours(now) <= FOCUS_MAX_AGE_HOURS",
    ),
    (
        "M8",
        "a legacy wrong row's correction state is None, NOT False -- different claims",
        '            out.append({"what": item.strip(), "corrected": None})',
        '            out.append({"what": item.strip(), "corrected": False})',
    ),
)

#: THE REACHABILITY FLOOR, and the reason it runs BEFORE the mutations rather than after. An
#: import-time raise: any suite that imports the subject, directly or transitively, MUST go red
#: under it. A suite that stays green here never reaches the module at all, and every "survived"
#: it goes on to report means UNREACHABLE, not UNPROVED.
#:
#: Those two readings are the same observation, and the flattering one is the one that gets
#: written down. This battery's own fourth column is the evidence: all eight mutations survived
#: `test_supervisor.py`, and the suite reaches `direction` only through a fixture that monkeypatches
#: `DIRECTION_PATH` to a file nothing writes -- so `focus_weights` short-circuits and
#: `focus_multiplier` is never called. Eight green cells, none of them at risk. Without this round
#: the column reads as eight contracts holding up.
POISON_OLD = "\ndef append_decision("
POISON_NEW = ('\nraise RuntimeError("POISON: direction.py reachability floor")'
              "\n\n\ndef append_decision(")


SPEC = BatterySpec(
    name="direction",
    subject="background/direction.py",
    suites=SUITES,
    repair_suite=REPAIR_SUITE,
    mutations=MUTATIONS,
    poison_old=POISON_OLD,
    poison_new=POISON_NEW,
)


def main(argv: list[str] | None = None) -> int:
    return run(SPEC, argv)


if __name__ == "__main__":
    raise SystemExit(main())
