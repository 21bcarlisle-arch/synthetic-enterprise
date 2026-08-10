"""Controls for the OPS2 subject-cost measurement harness's CHECKPOINT contract.

The harness (`tools/measure_publish_gate_subject_cost.py`) is the evidence source for two
OPS2 exit criteria: the warm/in-tree ratio (≤ 1.3x) and the timeout floor derived from the
worst legitimate run. It is a ~50-minute, three-phase job on a box where the OOM killer is a
known visitor, so it is expected to be killed sometimes.

WHAT THESE CONTROLS ARE FOR (R15). The defect they fire on is OBSERVED, not hypothetical: the
2026-08-10 05:28 run died inside `_wait_for_quiet` and left NOTHING in the repo, so the next
tick could not distinguish "died in the wait" from "never launched" from "ran and found
nothing". The fix is a checkpoint written before the first phase and after each one — and a
checkpoint has exactly one way to be worse than useless, which is to look like a RESULT:

  1. FAIL-OPEN TO A READER KEYING ON EXISTENCE — a partial record whose `complete` flag is
     absent or true would let a reader fill in the design doc's table from phases that never
     ran. `complete` must be false until all three phases are present, and `phases_missing`
     must name the ones still owed.
  2. FAIL-LOUD ON ITS OWN WRITE — a checkpoint that raises would kill the live measurement it
     exists to protect. Losing the record must never cost the run.

MUTATION-PROVEN: setting `results["complete"] = True` unconditionally in `_checkpoint` reds
`test_a_partial_record_is_not_complete` and `test_an_aborted_record_is_not_complete`; deleting
the `except OSError` reds `test_an_unwritable_checkpoint_never_kills_the_run`.
"""
import json

import pytest

from tools import measure_publish_gate_subject_cost as measure


@pytest.fixture
def out(tmp_path):
    return str(tmp_path / "publish_gate_subject_cost.json")


def _read(path):
    with open(path) as fh:
        return json.load(fh)


def test_a_record_exists_before_the_first_phase_runs(out):
    """The 05:28 defect exactly: a run killed in the quiet-wait must still be evidenced.

    MUTATION: drop the pre-wait `_checkpoint` call in `main` and there is no file at all, which
    is indistinguishable from never having been launched."""
    measure._checkpoint({"phases": {}}, out, print)

    rec = _read(out)
    assert rec["complete"] is False
    assert rec["phases_missing"] == list(measure.PHASE_ORDER)


def test_a_partial_record_is_not_complete(out):
    """Two of three phases is not a result, and must not read as one."""
    results = {"phases": {"cold_checkout": {"seconds": 900.0},
                          "warm_checkout": {"seconds": 700.0}}}
    measure._checkpoint(results, out, print)

    rec = _read(out)
    assert rec["complete"] is False, (
        "a record missing the in-tree baseline cannot support the ratio criterion, so it must "
        "not be flagged complete"
    )
    assert rec["phases_missing"] == ["in_tree_baseline"]
    # And it must not be carrying the derived figures a reader would copy into the design doc.
    assert "ratio_warm_over_in_tree" not in rec
    assert "implied_timeout_floor_2x" not in rec


def test_a_full_record_is_complete_and_owes_nothing(out):
    """The other direction: a control that can only say "incomplete" is not a control."""
    results = {"phases": {p: {"seconds": 1.0} for p in measure.PHASE_ORDER}}
    measure._checkpoint(results, out, print)

    rec = _read(out)
    assert rec["complete"] is True
    assert rec["phases_missing"] == []


def test_an_aborted_record_is_not_complete(out):
    """An abort names its reason AND stays incomplete -- the reason is not a substitute."""
    results = {"phases": {}, "aborted": "another publisher held the reuse lock"}
    measure._checkpoint(results, out, print)

    rec = _read(out)
    assert rec["complete"] is False
    assert rec["aborted"] == "another publisher held the reuse lock"


def test_an_unwritable_checkpoint_never_kills_the_run(tmp_path):
    """Losing the record must cost the record, never the 50-minute measurement.

    MUTATION: remove the `except OSError` in `_checkpoint` and this raises."""
    logged = []
    unwritable = str(tmp_path / "no-such-dir" / "c.json")

    measure._checkpoint({"phases": {}}, unwritable, logged.append)

    assert logged, "a failed checkpoint must say so rather than fail silently"
    assert "could not checkpoint" in logged[0]


def test_every_phase_the_harness_times_is_named_in_the_phase_order():
    """PHASE_ORDER is what `phases_missing` is computed from, so a phase absent from it would
    be silently un-owed: the record would read complete with that phase never run.

    Independent oracle -- the phase KEYS are read out of `main`'s own source rather than from
    PHASE_ORDER itself, so the two cannot agree by construction (R15 TAUTOLOGY)."""
    import inspect
    import re

    src = inspect.getsource(measure.main)
    assigned = set(re.findall(r'results\["phases"\]\["(\w+)"\]', src))

    assert assigned, "could not find the phase assignments in main() -- this oracle has gone blind"
    assert assigned == set(measure.PHASE_ORDER), (
        f"main() times {sorted(assigned)} but PHASE_ORDER declares "
        f"{sorted(measure.PHASE_ORDER)}; a phase missing from PHASE_ORDER is never reported "
        "as owed"
    )
