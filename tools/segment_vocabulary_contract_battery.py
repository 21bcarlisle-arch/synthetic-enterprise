#!/usr/bin/env python3
"""R15 mutation battery for `simulation/segment_vocabulary.py`, scored PER SUITE.

The third subject of the convergence-evidence sweep, and the top row of
`tools/converged_contract_screen.py` by caller count: 8 first-party callers, 3
test files that IMPORT it, 265 whose import closure reaches it.

This file is the SPEC -- the suites, the eight contracts and the reachability
anchor. The procedure lives in `tools/contract_battery.py`; what it guarantees
and why is documented there and deliberately not restated here.

Pre-registration, written and landed BEFORE this ran:
`docs/staging/SEAT_PREREG_WHICH_SUITE_HOLDS_THE_SEGMENT_VOCABULARY_2026-09-06.md`

WHY THIS SUBJECT IS WORTH A BATTERY. The module exists to be the single place a
segment is normalised, and the defect it closed was C5 and C6 -- the two
microbusiness accounts in the population, billed as households for the whole
history because two sim-side modules compared `segment == "sme"` against a
record spelled "SME". Nothing went red. If this module's contracts turn out to
stand on one borrowed suite, that defect is one refactor away from returning by
the same silent route.

Usage:
    python3 -m tools.segment_vocabulary_contract_battery
    python3 -m tools.segment_vocabulary_contract_battery --only M3 --suites w2_15
"""
from __future__ import annotations

from tools.contract_battery import BatterySpec, run

#: The three suites that IMPORT the module -- the only ones that can NAME a
#: contract -- followed by one dedicated suite per caller that has one.
#:
#: `grep -rl segment_vocabulary tests/` returns a FOURTH importer,
#: `tests/tools/test_segment_case_guard.py`. It is not one: it carries the
#: module's name in fixture source strings and assertion messages and imports
#: `tools.segment_case_guard` instead. It reaches the subject through that
#: caller's own module-level import, so it is scored here as a reaching suite
#: and never as a direct one -- the grep-is-an-upper-bound failure the screen's
#: finding names, live in this very suite list.
DIRECT_SUITES = (
    "tests/sim/test_w2_15_segment_vocabularies.py",
    "tests/simulation/test_segment_case_normalisation.py",
    "tests/simulation/test_served_segments_curriculum.py",
)

#: One per caller with a dedicated suite. `simulation/sme_payment_behaviour.py`
#: has none: its only test importer is `test_segment_case_normalisation.py`,
#: already above. 265 suites reach this module and ten is what gets graded --
#: stated as a BOUND on the answer, not hidden: a contract killed by none of
#: these ten is unproved by the suites a reader would look in, which is not the
#: same claim as unproved anywhere in the tree.
CALLER_SUITES = (
    "tests/simulation/test_arrears_engine.py",
    "tests/simulation/test_population_draw.py",
    "tests/simulation/test_live_population_seam.py",
    "tests/sim/test_w2_11_payment_behaviour_source.py",
    "tests/sim/test_segment_debt_obligation.py",
    "tests/sim/test_w2_6_sme_distress.py",
    "tests/tools/test_segment_case_guard.py",
)

SUITES = DIRECT_SUITES + CALLER_SUITES

#: Two suites with no import path to the subject. The poison round must leave
#: these GREEN. Without them, a floor that reddens every suite for a reason
#: unrelated to the subject -- a syntax error, a collection-time failure --
#: reads exactly like total reachability, and the reachability column would be
#: strongest precisely when it was broken.
CONTROL_SUITES = (
    "tests/background/test_delivery_lane.py",
    "tests/design/test_atom_notes_store.py",
)

#: (id, the contract as the module states it, old, new). Each `old` appears
#: exactly once in the subject and the engine refuses the row if it does not.
MUTATIONS = (
    (
        "M1",
        'an alias maps to its OWN canon -- "sme" is SME and never RESIDENTIAL',
        '    "sme": SME,',
        '    "sme": RESIDENTIAL,',
    ),
    (
        "M2",
        "lookup is case-INSENSITIVE by construction -- the defect the module exists to close",
        "    key = segment.strip().casefold()",
        "    key = segment.strip()",
    ),
    (
        "M3",
        "a CompanyBookLabel (V2) is refused whatever it spells -- belief is not truth",
        "    if isinstance(segment, CompanyBookLabel):",
        "    if False:",
    ),
    (
        "M4",
        "a PRESENT-but-unknown segment RAISES -- absent and wrong are different claims",
        "    try:\n        return _ALIASES[key]",
        "    if key not in _ALIASES:\n        return RESIDENTIAL\n    try:\n"
        "        return _ALIASES[key]",
    ),
    (
        "M5",
        "is_business is TRUE for SME and I&C and FALSE for a household",
        "    return normalise_segment(segment) in BUSINESS_SEGMENTS",
        "    return normalise_segment(segment) in CANONICAL_SEGMENTS",
    ),
    (
        "M6",
        "BUSINESS_SEGMENTS contains SME -- dropping it IS the C5/C6 defect",
        "BUSINESS_SEGMENTS = (SME, INDUSTRIAL_AND_COMMERCIAL)",
        "BUSINESS_SEGMENTS = (INDUSTRIAL_AND_COMMERCIAL,)",
    ),
    (
        "M7",
        "CANONICAL_SEGMENTS is all THREE segments",
        "CANONICAL_SEGMENTS = (RESIDENTIAL, SME, INDUSTRIAL_AND_COMMERCIAL)",
        "CANONICAL_SEGMENTS = (RESIDENTIAL, SME)",
    ),
    (
        "M8",
        "an ABSENT segment defaults to RESIDENTIAL",
        "def normalise_segment(segment, *, default: str | None = RESIDENTIAL) -> str:",
        "def normalise_segment(segment, *, default: str | None = SME) -> str:",
    ),
)

#: The reachability floor. Every one of the eight callers imports this module at
#: MODULE level, so unlike `direction.py` -- whose fourth column was eight green
#: cells behind a monkeypatched path, none ever at risk -- total reachability is
#: the expected answer here. It is still measured, because "expected" is exactly
#: the state in which a floor stops being run.
POISON_OLD = "\ndef normalise_segment("
POISON_NEW = ('\nraise RuntimeError("POISON: segment_vocabulary reachability floor")'
              "\n\n\ndef normalise_segment(")

#: THE NULL ROUND: a module-level no-op assignment. It changes the bytes and adds
#: an AST node, and it cannot change what any function does. A suite that reddens
#: under it is grading this file's TEXT rather than running it -- and one of the
#: ten is a plausible candidate, because `tools/segment_case_guard.py` AST-scans
#: `simulation/` for segment string literals. This marker deliberately contains no
#: string literal, so the guard SHOULD be indifferent to it; measuring that rather
#: than assuming it is the whole point.
NULL_OLD = "class UnknownSegmentError(ValueError):"
NULL_NEW = ("_NULL_ROUND_MARKER = None  # behaviour-preserving; tools/contract_battery.py\n"
            "\n\nclass UnknownSegmentError(ValueError):")

SPEC = BatterySpec(
    name="segment_vocabulary",
    subject="simulation/segment_vocabulary.py",
    suites=SUITES,
    mutations=MUTATIONS,
    poison_old=POISON_OLD,
    poison_new=POISON_NEW,
    control_suites=CONTROL_SUITES,
    null_old=NULL_OLD,
    null_new=NULL_NEW,
)


def main(argv: list[str] | None = None) -> int:
    return run(SPEC, argv)


if __name__ == "__main__":
    raise SystemExit(main())
