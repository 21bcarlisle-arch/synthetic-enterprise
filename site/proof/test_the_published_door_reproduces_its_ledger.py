"""The door must serve the figure the ledger of record carries.

THE DEFECT, and it is this atom's own pair. H27 Expert Hour #33 (2026-08-17) measured
`site/data/proof.json` regenerating in the working tree with EXACTLY ONE of its fourteen
`coupled_gaps` pairs moving -- `W2_11_payment_behaviour_source`, gap 0.0834 -> 0.0311, the
whole book under it (universe_size 1600 -> 276, n_negatives 1451 -> 257, false_flag_rate
0.1668 -> 0.0623): a 2.68x UNDERSTATEMENT of the company's own payment belief-vs-truth gap,
one broad-pathspec commit away from the deployed payload.

WHY THIS PAIR AND NO OTHER -- a mechanism, not an incident. This pair's ledger entry is the
only one of the fourteen written as a SIDE EFFECT of running the simulation
(`simulation/run_phase2b.py` -> `LivePaymentTriad.measure_and_write`, `ledger_path`
defaulted to the real file), while every other pair is written by its own
`tools/couple_*.py --write-ledger` main that no test invokes -- and 67 test modules import
run_phase2b. `background/live_ledger_guard.py` now REFUSES that write under a test process
and Hour #34 verified it empirically (513 tests, live ledger md5 unchanged across the run).
This file is the OTHER half: the guard stops the poisoning, and this catches a door and a
ledger that have parted for any reason at all -- a stale record, a hand edit, a generator
run against a tree nobody committed.

WHY NOTHING WAS RED, and it is not that the checks were weak. Every control on this block
reads ONE side. The panel tests recompute the block from the working tree; the R11 door
tests read the published file; the site-lane control in
`test_the_committed_generator_reproduces_the_published_door.py` compares the artefact with
the GENERATOR and excludes the ledger as a subject on purpose. The defect lives only in the
RELATION: the door agrees with itself, the ledger agrees with itself, the generator did what
it was asked, and the scorer is not involved at all.

THE TWO SUBJECTS, and why neither is derived from the other. Subject A is the PUBLISHED DOOR
(`site/data/proof.json` on disk, which the deploy uploads verbatim). Subject B is the LEDGER
OF RECORD (`docs/observability/coupled_gap_ledger.json`). Both are read independently from
disk by `measure_published_door_against_the_ledger`; this file never regenerates either and
never compares one with itself.

WHY THIS FILE IS A CALLER AND NOT A SECOND IMPLEMENTATION. The comparison itself is
`tools.couple_w2_11_d5.check_published_door_reproduces_the_ledger`, built and mutation-proven
by Hour #33 (RED on the poisoned door as found -- 9 violations; GREEN once restored; four
source mutations proven to fire: unreadable-file-caught-into-{}, headline-only comparison,
no vacuity guard, absent-door-pair-as-skip). Re-deriving the comparison here would be a
SECOND implementation of the same wall, which is how one gets enforced while the other runs
free. What this file adds is the thing that check did not have: AN AUTOMATED CALLER. Hour
#32's finding 3 was that this module's `check_*` family had no caller on any run that
publishes; measured 2026-08-18, `check_published_door_reproduces_the_ledger` had ZERO callers
anywhere outside its own module.

R15 BOTH WAYS, PROVEN AGAINST REAL HISTORY RATHER THAN A FIXTURE:
  RED   at 079931c16 -- reading BOTH sides from that one ref gives 4 violations: door
        0.0833907649896623 vs ledger 0.0859375, universe_size 1600 vs 1557, n_negatives
        1451 vs 1408, false_flag_rate 0.166782 vs 0.171875. The door at that ref was
        current (generated 2026-08-18T00:52:34Z); the LEDGER was six days stale (measured
        2026-08-12T06:10:09Z). The published artefact had been committed and its source
        record had not.
  GREEN once the production ledger it was generated from is committed (Hour #34, e7a554d03)
        -- 0 violations, 10 of 10 declared components compared.
The state this control catches is one the repository was actually in, for six days, so the
mutation is history and not a mock. It is deliberately NOT in the same commit as the repair
that greens it.

THREE FURTHER MUTATIONS, each proven to fire (2026-08-18): the ledger ABSENT (fail-silent --
an unreadable subject is a violation, not an empty comparison); the ledger present with this
atom's ENTRY REMOVED (the door's figure derived from nothing on disk); and NINE OF TEN
components dropped, which is the one the tripwire alone does NOT catch and the second test
below exists for.

WHY THE SITE LANE. `tools/git-hooks/pre-commit`'s site-lane step triggers on site/**, on any
`generate_*_data` producer, and on a SITE-CONSUMED LEDGER -- so it fires on a change to
either of this file's two subjects, which is exactly when a substitution can land. The
tests/ publish gate selects by NAME STEM and would never run this.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent  # site/proof -> repo root


def _measured() -> dict:
    """The independent read of both subjects, from disk, at their real paths."""
    sys.path.insert(0, str(PROJECT))
    from tools.couple_w2_11_d5 import measure_published_door_against_the_ledger

    return measure_published_door_against_the_ledger()


def test_the_published_door_serves_the_figure_the_ledger_of_record_carries():
    """THE TRIPWIRE. Divergence is a violation whatever caused it.

    The check returns an `unavailable` violation -- never a clean pass -- when either
    artefact is missing, unreadable, or has stopped carrying this pair, so an absent
    subject fails this test rather than emptying it (R15 fail-silent).
    """
    sys.path.insert(0, str(PROJECT))
    from tools.couple_w2_11_d5 import check_published_door_reproduces_the_ledger

    m = _measured()
    violations = check_published_door_reproduces_the_ledger(m)
    assert not violations, (
        "the public Proof door and the ledger of record have parted:\n  - "
        + "\n  - ".join(violations)
        + f"\n(door generated {m.get('door_generated_at')!r}, ledger measured "
        f"{m.get('ledger_measured_at')!r}.) The repair depends on WHICH is stale: if the "
        "ledger is older, a real run has measured the door's figure and the record was "
        "never committed -- commit it. If the door is older, regenerate and commit the "
        "artefact, then re-fetch the live URL and quote the served value (R11). Never "
        "hand-edit either side to agree."
    )


def test_the_component_comparison_actually_compared_the_components():
    """THE VACUITY GUARD, and what it closes is PARTIAL erosion specifically.

    `measure_published_door_against_the_ledger` walks `_DOOR_LEDGER_COMPONENTS` and
    `continue`s on any name absent from EITHER side, so a component renamed or dropped
    silently leaves the comparison rather than becoming a violation. Hour #33 saw the
    endpoint of that and guarded it: `check_published_door_reproduces_the_ledger` already
    raises a violation when `compared` is EMPTY, so the all-gone case is covered and this
    test is not a second copy of it.

    What no control had was the approach to that endpoint. Measured 2026-08-18 by dropping
    nine of the ten components from the ledger entry and leaving `caught`: the existing
    check returns ZERO violations and the headline tripwire above PASSES, because a
    non-empty `compared` satisfies the emptiness guard while nine published figures sit
    outside the comparison entirely. Erosion only ever looks like vacuity on its last step,
    and by then the door has been unchecked for nine of them.

    So the population is asserted to be the DECLARED one, not merely non-empty. This is a
    deliberate ratchet, and the direction matters: it wedges when a component leaves the
    comparison, and the repair is to change `_DOOR_LEDGER_COMPONENTS` on purpose -- a
    considered edit with a reader, rather than a figure quietly ceasing to be checked.
    """
    sys.path.insert(0, str(PROJECT))
    from tools.couple_w2_11_d5 import _DOOR_LEDGER_COMPONENTS

    m = _measured()
    compared = set(m.get("compared") or [])
    declared = set(_DOOR_LEDGER_COMPONENTS)

    assert compared, (
        "the door/ledger comparison compared NO components at all -- both sides still "
        "carry a headline, so the tripwire above passes while every number under it is "
        "unchecked. This is the vacuous state, not a clean one"
    )
    missing = sorted(declared - compared)
    assert not missing, (
        f"{missing} are declared comparable but were skipped -- each is absent from the "
        "door, the ledger, or both, so it is silently outside the comparison rather than "
        f"agreeing with anything. Compared {sorted(compared)} of {len(declared)} declared. "
        "Either restore the component on the side that dropped it, or remove it from "
        "`_DOOR_LEDGER_COMPONENTS` deliberately"
    )
