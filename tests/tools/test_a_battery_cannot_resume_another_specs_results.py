"""A contract battery must not adopt a results file that a DIFFERENT spec wrote.

THE DEFECT THIS NAMES (delivery seat, 2026-09-06). `tools/contract_battery.py` defaulted `--out`
to `/var/tmp/<subject-name>_battery_results.json` and keyed its resume cache on the mutation ID
alone. Every spec in this family numbers its contracts `M1`..`M8`. Two lanes wrote eight DIFFERENT
`ops_repo` contracts to that one path within seven minutes; the second run found all eight ids
present, executed nothing but a single outstanding control suite, and printed
`SURVIVED ALL 3 CALLER SUITES: M1..M8` with the first lane's contract text on every row.

A battery that exists to establish that a kill came from RUNNING the code had published eight
survivals it never applied. That is the instrument committing the class it was built to find, so
the control belongs on the engine and not in a habit.

WHAT MAKES THIS ABLE TO FAIL. A refusal that refuses everything passes every test of a refusal,
and this project has entered that trap three times through three different doors. So the whole
partition is asserted over: `test_the_partition_is_real` proves the SAME spec still resumes --
delete the fingerprint comparison and make it unconditional, and that leg reds. The refusal leg
and the resume leg cannot both be satisfied by a constant.
"""
from __future__ import annotations

import json

import pytest

from tools.contract_battery import BatterySpec, fingerprint

_COMMON = dict(
    subject="background/ops_repo.py",
    suites=("tests/background/test_ntfy_mirror.py",),
    poison_old="\ndef commit_and_push(",
    poison_new='\nraise RuntimeError("POISON")\n\n\ndef commit_and_push(',
)


def _spec(mutations) -> BatterySpec:
    return BatterySpec(name="fixture_subject", mutations=mutations, **_COMMON)


#: Same id, same subject, same suites -- and a different edit. This is the shape that actually
#: collided: not a careless duplicate but two honest specs for one converged module.
SPEC_A = _spec((("M1", "the write refuses under a test process", "    if in_test_process():",
                 "    if False:"),))
SPEC_B = _spec((("M1", "the push actually happens", '        ["git", "push"], check=True,',
                 '        ["git", "status"], check=True,'),))


def test_two_specs_for_one_subject_do_not_share_a_fingerprint():
    """The ids match, the subject matches, the suites match. Only the EDIT differs, and that is
    the thing a cell is evidence about."""
    assert fingerprint(SPEC_A) != fingerprint(SPEC_B)


def test_the_default_results_path_carries_the_fingerprint(tmp_path, monkeypatch):
    """Collision prevented at source: neither run has to remember to pass `--out`."""
    import tools.contract_battery as cb

    seen = {}

    def _record(results, suites, out_path):
        seen["out"] = out_path
        return {s: {"failed": []} for s in suites}

    monkeypatch.setattr(cb, "_baseline", _record)
    monkeypatch.setattr(cb, "_poison", lambda *a, **k: {})
    monkeypatch.setattr(cb, "_null_round", lambda *a, **k: {})

    subject = cb.PROJECT / _COMMON["subject"]
    original = subject.read_text(encoding="utf-8")
    try:
        cb.run(SPEC_A, ["--pristine", str(tmp_path / "p.py"), "--only", "NOTHING"])
    finally:
        subject.write_text(original, encoding="utf-8")

    assert fingerprint(SPEC_A) in str(seen["out"]), (
        "the default --out must be spec-specific, or two specs for one subject collide before "
        "the refusal ever gets a chance to fire"
    )


def test_a_results_file_written_by_another_spec_is_refused(tmp_path):
    """The load-bearing leg. Before 2026-09-06 this returned 0 and reported SPEC_B's row as
    SPEC_A's."""
    out = tmp_path / "shared.json"
    out.write_text(json.dumps({
        "spec_fingerprint": fingerprint(SPEC_B),
        "subject": _COMMON["subject"],
        "baseline": {"tests/background/test_ntfy_mirror.py": {"failed": []}},
        "mutations": {"M1": {"contract": "the push actually happens", "per_suite": {
            "tests/background/test_ntfy_mirror.py": {"died": False}}}},
    }))

    rc = _run_a(out, tmp_path)
    assert rc == 2, "a run resuming another spec's file must refuse, not score"


def test_an_unfingerprinted_results_file_is_refused_just_as_hard(tmp_path):
    """Absent is not 'matches'. A file written before this check existed cannot say which spec
    scored it, and an unavailable check reports itself unavailable rather than reporting a pass."""
    out = tmp_path / "legacy.json"
    out.write_text(json.dumps({
        "subject": _COMMON["subject"],
        "mutations": {"M1": {"contract": "whatever the other lane meant", "per_suite": {}}},
    }))

    assert _run_a(out, tmp_path) == 2


def test_the_partition_is_real_and_its_own_spec_still_resumes(tmp_path):
    """WITHOUT THIS LEG the refusal above is satisfied by `return 2` unconditionally, and every
    battery in the family is dead while reading exactly like a battery that works."""
    out = tmp_path / "own.json"
    out.write_text(json.dumps({
        "spec_fingerprint": fingerprint(SPEC_A),
        "subject": _COMMON["subject"],
        "baseline": {"tests/background/test_ntfy_mirror.py": {"failed": []}},
        "poison": {},
        "mutations": {"M1": {"contract": "the write refuses under a test process",
                             "per_suite": {"tests/background/test_ntfy_mirror.py":
                                           {"died": True, "failed": []}}}},
    }))

    assert _run_a(out, tmp_path) == 0, (
        "a spec resuming ITS OWN results must proceed -- a refusal that refuses everything "
        "passes every test of a refusal"
    )


def _run_a(out, tmp_path) -> int:
    """SPEC_A against `out`, with every mutation deselected so nothing is patched on disk.

    `--only NOTHING` matches no id, so the subject is never written to. The fingerprint check runs
    before any mutation regardless -- that ordering is what the return code here reports on.
    """
    import tools.contract_battery as cb

    subject = cb.PROJECT / _COMMON["subject"]
    original = subject.read_text(encoding="utf-8")
    try:
        return cb.run(SPEC_A, ["--out", str(out), "--pristine", str(tmp_path / "pristine.py"),
                               "--only", "NOTHING", "--suites", "no_such_suite"])
    finally:
        if subject.read_text(encoding="utf-8") != original:
            subject.write_text(original, encoding="utf-8")


@pytest.mark.parametrize("spec", [SPEC_A, SPEC_B])
def test_a_fingerprint_is_stable_across_calls(spec):
    """A key that moved between the write and the read would refuse every resume, including its
    own -- the fail-closed direction, but still a dead instrument."""
    assert fingerprint(spec) == fingerprint(spec)
