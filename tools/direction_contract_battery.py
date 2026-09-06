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

#: The four caller suites.
#:
#: CORRECTED 2026-09-06. This comment used to read: *"`tools/generate_delivery_page.py` is the
#: fourth first-party caller and has no suite that imports it AND direction, so the fourth row
#: here is the self-audit suite -- the closest thing the module has to one of its own."* Wrong,
#: and wrong in the way that mattered. The self-audit suite DOES exercise `generate_delivery_page`
#: as a caller, at `test_the_published_panel_SPLITS_open_from_corrected_from_not_recorded`, and on
#: a caller-only population that test is the source of the ONLY genuine caller kill in the whole
#: battery (M8). The column written off here as a near-own-suite is the one carrying real evidence.
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

#: THE SUBJECT'S OWN TESTS, LIVING IN FILES NAMED FOR ITS CALLERS. Deselected from the caller
#: columns; see `BatterySpec.direct_nodes` for the mechanism.
#:
#: `direction` is the spec that forced the node grain. `b3938b313`'s census asked the file
#: question -- is this file the subject's own suite -- and found it has no honest answer here:
#: all four columns import `background.direction` at module level AND all four are the dedicated
#: suite of a module that calls it, so the obvious gate would have condemned a correct spec. No
#: gate on that discriminator was shipped, and the question was left open as Lane 0 work.
#:
#: Asked per TEST it is decidable. Census by AST over the four files, 2026-09-06: a test is the
#: subject's own if its assertions run against `direction`'s API and it never touches the module
#: its file is named for. `test_delivery_lane.py` is why this cannot be done at the file grain --
#: it holds one of each, and the caller test (`test_EXPIRED_direction_offers_NOTHING`, which calls
#: `dl.`) is deliberately NOT here. `test_supervisor.py` contributes nothing: its only reference to
#: the module is the fixture's `monkeypatch.setattr(DIRECTION_PATH, ...)`, which is what the poison
#: round already proved it reaches the subject without ever proving anything about it.
DIRECT_NODES = (
    "tests/background/test_delivery_lane.py::test_a_MISSING_or_BROKEN_record_offers_nothing",
    "tests/background/test_delivery_seat.py::test_direction_can_NEVER_make_an_atom_harder_to_draw",
    "tests/background/test_delivery_seat.py::test_direction_cannot_shorten_the_candidate_list",
    "tests/background/test_delivery_seat.py::test_a_named_atom_actually_becomes_more_likely_and_the_steer_BITES",
    "tests/background/test_delivery_seat.py::test_focus_that_was_never_DRAWN_is_reported_rather_than_assumed",
    "tests/background/test_delivery_seat.py::test_the_verdict_is_SPLIT_so_one_dead_channel_cannot_hide_behind_the_other",
    "tests/background/test_delivery_seat.py::test_a_BROKEN_direction_record_leaves_the_draw_byte_identical",
    "tests/background/test_delivery_seat.py::test_a_MISSING_record_is_not_an_error",
    "tests/background/test_delivery_seat.py::test_direction_EXPIRES_so_stale_advice_stops_steering_on_its_own",
    "tests/background/test_delivery_seat.py::test_a_record_carrying_a_TARGET_is_refused_whatever_it_is_called",
    "tests/background/test_delivery_seat.py::test_the_refusal_reaches_ARBITRARY_depth",
    "tests/background/test_delivery_seat.py::test_a_measurement_quoted_in_a_WHY_is_not_a_target",
    "tests/background/test_delivery_seat.py::test_a_direction_that_REJECTED_NOTHING_is_refused",
    "tests/background/test_delivery_seat.py::test_a_direction_that_NAMES_NO_WORK_is_refused",
    "tests/background/test_delivery_seat.py::test_the_refusal_says_WHY_rather_than_returning_a_boolean",
    "tests/background/test_delivery_seat.py::test_the_write_scope_is_CLOSED_and_holds_no_code_path",
    "tests/background/test_delivery_seat.py::test_the_decision_log_is_APPEND_ONLY",
    "tests/background/test_delivery_seat.py::test_a_CORRUPT_line_does_not_blank_the_record",
    "tests/background/test_the_self_audit_declared_a_correction_and_nothing_carried_it.py::test_an_EMPTY_self_audit_row_is_refused_whatever_kind_of_empty_it_is",
    "tests/background/test_the_self_audit_declared_a_correction_and_nothing_carried_it.py::test_an_error_with_NO_CORRECTION_STATE_is_refused",
    "tests/background/test_the_self_audit_declared_a_correction_and_nothing_carried_it.py::test_a_POPULATED_self_audit_passes_and_an_ABSENT_one_is_not_an_error",
    "tests/background/test_the_self_audit_declared_a_correction_and_nothing_carried_it.py::test_the_refusal_NAMES_the_row_so_the_seat_can_fix_the_one_that_is_wrong",
    "tests/background/test_the_self_audit_declared_a_correction_and_nothing_carried_it.py::test_the_recorded_audit_reads_in_BOTH_shapes_and_never_invents_a_verdict",
)

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


#: SUBJECT AND CALLER IN ONE BODY -- kept in the run, flagged on the row, never counted as proof.
#: `test_EXPIRED_direction_offers_NOTHING` asserts `d.unreachable_focus(...) == []` AND
#: `dl.next_item(...) is None` two lines apart. Calling it a caller test understates it; putting it
#: in `DIRECT_NODES` would discard real caller evidence. It is neither, and the row it kills gets
#: `killed_by_a_mixed_test` instead of a verdict.
#: ONE member, and the census had TWO until the merge that produced this file corrected it.
#: `test_the_decision_log_is_APPEND_ONLY` reads as mixed to a taint pass that follows only return
#: values -- it asserts on a file `d.append_decision` wrote through an ARGUMENT -- and the other
#: lane's hand-built list had it right. It is in `DIRECT_NODES`, where it belongs. Two independent
#: censuses disagreeing on exactly one row is how that was found.
MIXED_NODES = (
    "tests/background/test_delivery_lane.py::test_EXPIRED_direction_offers_NOTHING",
)


SPEC = BatterySpec(
    name="direction",
    subject="background/direction.py",
    suites=SUITES,
    direct_nodes=DIRECT_NODES,
    mixed_nodes=MIXED_NODES,
    repair_suite=REPAIR_SUITE,
    mutations=MUTATIONS,
    poison_old=POISON_OLD,
    poison_new=POISON_NEW,
)


def main(argv: list[str] | None = None) -> int:
    return run(SPEC, argv)


if __name__ == "__main__":
    raise SystemExit(main())
