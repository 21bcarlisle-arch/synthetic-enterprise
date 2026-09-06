"""The defect: a mutation battery reported eight GREEN cells for `test_supervisor.py` and every
one of them was read as "the contract held". None was at risk -- the suite reaches
`background/direction.py` only through a fixture that points `DIRECTION_PATH` at a file nothing
writes, so `focus_weights` short-circuits and the mutated lines are never executed.

"the contract held" and "the suite never reached the line" are the SAME green. These tests are the
control on the round that tells them apart, and each names the way it can silently fail.

REPOINTED 2026-09-06. The engine was lifted out of `tools/direction_contract_battery.py` into
`tools/contract_battery.py` and every name these controls reach for went with it -- `SUBJECT`,
`POISON_OLD`, `_poison`, `_score` -- while the spec kept only its data. All six had been erroring
on `AttributeError: module has no attribute 'SUBJECT'` from the extraction until now, which is the
class this file exists to catch, committed against this file: a control whose subject moved is a
control that proves nothing, and it says so in a colour nobody was reading.
"""
from __future__ import annotations

import pytest

from tools import contract_battery as battery
from tools.direction_contract_battery import SPEC


@pytest.fixture()
def subject(tmp_path, monkeypatch):
    """A stand-in subject, so nothing here can write the real `background/direction.py`.

    `subject_path` is a property over the module-level `PROJECT`, so the redirection is done there
    rather than on the frozen spec -- and the stand-in is written at the SAME relative path, or
    the engine would resolve past it and mutate the real file."""
    path = tmp_path / SPEC.subject
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(SPEC.subject_path.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(battery, "PROJECT", tmp_path)
    monkeypatch.setattr(battery, "_clear_pycache", lambda: None)
    assert SPEC.subject_path == path, "the redirection must actually move the subject"
    return path


def _fake_runs(verdicts):
    """`_run_suite` replaced by a table of returncodes, keyed by suite."""
    def run(suite, deselect, stop_first):
        return {"suite": suite, "returncode": verdicts[suite], "failed": [],
                "seconds": 0.0, "tail": []}
    return run


def test_the_POISON_is_a_real_poison_and_not_a_string_edit_that_changes_nothing(tmp_path):
    """THE FAIL-OPEN. If `POISON_NEW` did not actually break the import, every suite would come
    back green, every one would be marked as never reaching the subject, and the round would
    condemn the whole battery instead of grading it.

    IMPORTED the way pytest would import it, not `exec`'d: the subject carries a `@dataclass`,
    and a bare `exec` fails on that for its own unrelated reason -- which would have passed this
    test for entirely the wrong reason."""
    src = SPEC.subject_path.read_text(encoding="utf-8")
    assert src.count(SPEC.poison_old) == 1, "the poison target must be present exactly once"
    poisoned = src.replace(SPEC.poison_old, SPEC.poison_new)
    assert poisoned != src

    # The unpoisoned source must import CLEANLY by this same route, or the RuntimeError below
    # could be anything at all.
    assert _import_source(src, tmp_path / "clean_direction.py") is None
    assert _import_source(poisoned, tmp_path / "poisoned_direction.py") == "POISON"


def _import_source(source: str, path):
    """Import `source` as a module. Returns None on a clean import, or the RuntimeError text."""
    import importlib.util
    import sys

    path.write_text(source, encoding="utf-8")
    name = path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
        return None
    except RuntimeError as exc:
        return str(exc).split(":")[0]
    finally:
        sys.modules.pop(name, None)


def test_a_suite_that_stays_GREEN_under_the_poison_is_recorded_as_NEVER_REACHING(subject, tmp_path):
    """The whole point: green under an import-time raise means the suite never imports the
    subject, so its later green cells are not evidence about any contract."""
    suites = ("tests/a_reaching_suite.py", "tests/a_blind_suite.py")
    results: dict = {}
    monkey = _fake_runs({suites[0]: 1, suites[1]: 0})
    import unittest.mock as mock
    with mock.patch.object(battery, "_run_suite", monkey):
        poison = battery._poison(SPEC, results, suites, tmp_path / "out.json",
                                 {s: () for s in suites})
    assert poison[suites[0]]["reaches_subject"] is True
    assert poison[suites[1]]["reaches_subject"] is False


def test_the_poison_round_RESTORES_the_subject_whatever_the_verdicts(subject, tmp_path):
    """A round that left the subject poisoned would redden every mutation after it, and the
    battery would read as every contract being proved everywhere."""
    before = subject.read_text(encoding="utf-8")
    suites = ("tests/a.py",)
    import unittest.mock as mock
    with mock.patch.object(battery, "_run_suite", _fake_runs({suites[0]: 1})):
        battery._poison(SPEC, {}, suites, tmp_path / "out.json", {suites[0]: ()})
    assert subject.read_text(encoding="utf-8") == before


def test_a_NON_UNIQUE_poison_target_reports_reachability_UNKNOWN_and_never_a_pass(subject,
                                                                                  tmp_path):
    """FAIL CLOSED. If the poison cannot be applied, the honest answer is that reachability is
    unknown. Recording an empty `poison` map that later reads as "every suite reaches the
    subject" is the fail-open shape this whole round exists to prevent."""
    subject.write_text(subject.read_text(encoding="utf-8") + "\ndef append_decision(x):\n    pass\n",
                       encoding="utf-8")
    results: dict = {}
    poison = battery._poison(SPEC, results, ("tests/a.py",), tmp_path / "out.json",
                             {"tests/a.py": ()})
    assert poison == {}
    assert "expected exactly 1" in results["poison_error"]


def test_a_survivor_is_stamped_UNREACHABLE_only_where_the_suite_is_BLIND(tmp_path):
    """THE PARTITION, not a leg per branch. A stamp that fired on every survivor would pass a
    test that only ever checked the blind suite, so both sides are asserted in one control:
    survived+blind is stamped, survived+reaching is NOT, and a death is never stamped at all."""
    reaching, blind = "tests/reaching.py", "tests/blind.py"
    row: dict = {"per_suite": {}}
    import unittest.mock as mock
    with mock.patch.object(battery, "_run_suite", _fake_runs({reaching: 0, blind: 0})):
        battery._score(SPEC, row, [reaching, blind], {reaching: (), blind: ()},
                       {reaching: True, blind: False}, {})
    assert row["per_suite"][reaching]["survived_but_unreachable"] is False
    assert row["per_suite"][blind]["survived_but_unreachable"] is True

    died: dict = {"per_suite": {}}
    with mock.patch.object(battery, "_run_suite", _fake_runs({blind: 1})):
        battery._score(SPEC, died, [blind], {blind: ()}, {blind: False}, {})
    assert died["per_suite"][blind]["died"] is True
    assert died["per_suite"][blind]["survived_but_unreachable"] is False


def test_an_UNMEASURED_suite_is_not_treated_as_reaching_the_subject(tmp_path):
    """`reaches` is absent, not False, when the poison round never ran for that suite -- and an
    absent reading must not be stamped as unreachable either. The cell is simply unqualified,
    which is what `--only` resume runs produce."""
    suite = "tests/never_poisoned.py"
    row: dict = {"per_suite": {}}
    import unittest.mock as mock
    with mock.patch.object(battery, "_run_suite", _fake_runs({suite: 0})):
        battery._score(SPEC, row, [suite], {suite: ()}, {}, {})
    assert row["per_suite"][suite]["survived_but_unreachable"] is False
