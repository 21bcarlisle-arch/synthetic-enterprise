"""A run whose imported bytes were not its stamp's is refused as an arm of a one-variable grade.

Defect named by this file: a re-run at a published run's stamp is differenced against that run
when the run's code was another commit's. `run_output_2248e3baf_20261013T134447Z` was stamped
2248e3baf while its shared tree held 81c129fe8's `simulation/net_new_acquisition.py` and
`saas/growth_mandate.py`. A re-run at 2248e3baf drew a different book from 2016-02-13, so the
held-estimate grade became a two-commit difference and PROS-2017-0336 was left ungraded.

The first leg is that shape built for real: HEAD at X, and a disk copy of one simulation file from Y.
"""
import json
import subprocess
from datetime import datetime, timezone

import pytest

from background import code_closure
from tools import run_annual_report as rar

_SUBJECT = "simulation/net_new_acquisition.py"


def _header(reading, commit):
    """The producer's own header, so the key the arm check reads is the key the run writes."""
    return rar._run_identity_header(
        {"total_net_gbp": 1.0}, datetime(2026, 10, 15, tzinfo=timezone.utc), commit,
        {"digest": "w"}, {"risk_committee": "mock"}, from_launch=True,
        imports_off_commit=rar._imports_off_commit_record(reading, commit))


@pytest.fixture
def head_x_with_ys_file(tmp_path, monkeypatch):
    """HEAD at X; the working copy of `_SUBJECT` holds commit Y's bytes, and Y is not X's ancestor."""
    def git(*a):
        return subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True,
                              text=True).stdout.strip()
    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (tmp_path / "simulation").mkdir()
    (tmp_path / _SUBJECT).write_text("CAPITAL_TARGET_GBP = 130\n")
    git("add", "-A")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD")
    git("checkout", "-qb", "y")
    (tmp_path / _SUBJECT).write_text("CAPITAL_TARGET_GBP = 115\n")
    git("commit", "-qam", "Y: the capital target is 115")
    y = git("rev-parse", "--short", "HEAD")
    git("checkout", "-q", "--detach", base)
    (tmp_path / "simulation" / "unrelated.py").write_text("x = 1\n")
    git("add", "-A")
    git("commit", "-qm", "X: lands without Y")
    x = git("rev-parse", "--short", "HEAD")
    monkeypatch.setattr(code_closure, "import_closure", lambda entry, r=None: {_SUBJECT})
    return tmp_path, x, y, git


def test_an_arm_stamped_x_that_imported_ys_file_is_refused_naming_the_file(head_x_with_ys_file):
    """THE LOAD-BEARING LEG. MUTATION: make `one_variable_arm_refusal` return None for a non-empty
    `paths`, or drop the closure diff in `imports_off_commit`, and this fires."""
    root, x, y, git = head_x_with_ys_file
    clean = _header(code_closure.imports_off_commit(_SUBJECT, x, root), x)
    assert code_closure.one_variable_arm_refusal(clean) is None, (
        "a clean run at X must be admitted, or a refusal of everything passes the next assert")

    (root / _SUBJECT).write_text(git("show", f"{y}:{_SUBJECT}") + "\n")
    dirty = _header(code_closure.imports_off_commit(_SUBJECT, x, root), x)
    why = code_closure.one_variable_arm_refusal(dirty)
    assert why and _SUBJECT in why and x in why, (
        f"a run stamped {x} that imported {y}'s {_SUBJECT} was admitted as a one-variable arm: {why!r}")


def test_every_verdict_of_the_arm_check_is_reachable():
    """One control over the whole partition. MUTATION: let a header with no reading through (the
    publisher's rule, and the 2248e3baf case) and the `absent` leg fires."""
    verdicts = {
        "clean": code_closure.one_variable_arm_refusal(_header({"commit": "abc1234", "paths": []}, "abc1234")),
        "dirty": code_closure.one_variable_arm_refusal(
            _header({"commit": "abc1234", "paths": [_SUBJECT]}, "abc1234")),
        "unmeasured": code_closure.one_variable_arm_refusal(_header(None, "abc1234")),
        "absent": code_closure.one_variable_arm_refusal({"producing_commit": {"commit": "abc1234"}}),
        "no_commit": code_closure.one_variable_arm_refusal({"producing_commit": {"commit": None}}),
    }
    assert verdicts["clean"] is None
    assert all(verdicts[k] for k in ("dirty", "unmeasured", "absent", "no_commit")), verdicts
    assert "c701d8605" in verdicts["absent"] and _SUBJECT in verdicts["dirty"]


def test_the_loader_refuses_by_name(tmp_path):
    """MUTATION: have `load_one_variable_arm` skip the check and the raise goes missing."""
    run = tmp_path / "run_output_abc1234_x.json"
    run.write_text(json.dumps(_header({"commit": "abc1234", "paths": [_SUBJECT]}, "abc1234")))
    with pytest.raises(ValueError, match="not a one-variable arm"):
        code_closure.load_one_variable_arm(run)


def test_a_run_no_launcher_measured_takes_its_own_reading_at_start(monkeypatch, tmp_path):
    """A grader's arm or a hand run goes through `run_annual_report.main()` with no
    `--imports-off-commit`. It used to stamp `paths: None` (unmeasured). It now stamps the paths
    it read against the commit it captured before the run. MUTATION: drop the
    `_imports_off_commit_at_start` fallback and the stamped paths are None again."""
    monkeypatch.setattr(rar, "reconcile_published_run_output", lambda data: [])
    monkeypatch.setattr(rar, "world_level_identity", lambda: {"digest": "0" * 16})
    monkeypatch.setattr(rar, "_git_commit_hash", lambda: "aaaaaaaaa")
    asked = []

    def _reading(commit):
        asked.append(commit)
        return {"commit": commit, "paths": [_SUBJECT], "unavailable_because": None}

    monkeypatch.setattr(rar, "_imports_off_commit_at_start", _reading)
    monkeypatch.setattr(rar, "run_phase4c_on_phase2b", lambda report_end=None: {"raw": True})
    monkeypatch.setattr(rar, "extract_report_data", lambda raw: {"years": [{"year": 2025}]})
    monkeypatch.setattr(rar, "generate_annual_report", lambda data: "# report")
    save_json = tmp_path / "run_output.json"
    monkeypatch.setattr("sys.argv", ["run_annual_report", "--save-json", str(save_json),
                                     "--output", str(tmp_path / "r.md")])
    rar.main()

    data = json.loads(save_json.read_text())
    assert asked == ["aaaaaaaaa"]
    assert data["producing_commit"]["imports_off_commit"]["paths"] == [_SUBJECT]
    assert _SUBJECT in code_closure.one_variable_arm_refusal(data)
