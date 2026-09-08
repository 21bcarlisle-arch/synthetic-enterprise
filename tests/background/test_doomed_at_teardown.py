"""Controls for `background/doomed_at_teardown.py` — each naming the defect it would catch.

THE DEFECT CLASS THIS WHOLE FILE GUARDS. The subject reports processes that are about to be
SIGKILLed. Its two failure directions are not symmetric and both are fatal in this repo:

  * FAIL-SILENT — it reports nothing, ever, and reads exactly like a clean bounded unit. This is
    the shape that cost four launches, and it is what `test_all_three_verdicts_are_reachable`
    exists for: a detector that refuses everything passes every "does it decline correctly" test.
  * FAIL-NOISY — it fires on the ordinary path, gets silenced within a day, and is then
    fail-silent with extra steps. `test_a_lone_process_in_its_own_cgroup_reports_nothing` and the
    zombie leg are the controls for that.

Every test here drives the subject through injected `proc_root`/`cgroup_root` trees rather than the
live machine: a control keyed to what happens to be running is keyed to today's answer.
"""
from __future__ import annotations

import ast
from pathlib import Path

from background import doomed_at_teardown as dat

_REPO = Path(__file__).resolve().parents[2]


def _fake_tree(tmp_path, *, cgroup_rel="/user.slice/bounded.service", procs=(), states=None,
               cmdlines=None):
    """Build a `/proc` + `/sys/fs/cgroup` pair the subject can be pointed at.

    `procs` is what `cgroup.procs` lists; `states` maps pid -> the `State:` letter (default `R`).
    A pid absent from `states` but present in `procs` still gets a `/proc/<pid>` directory, so
    "listed and alive" and "listed and gone" are distinguishable rather than collapsed.
    """
    states = dict(states or {})
    cmdlines = dict(cmdlines or {})
    proc_root = tmp_path / "proc"
    (proc_root / "self").mkdir(parents=True)
    (proc_root / "self" / "cgroup").write_text("0::{}\n".format(cgroup_rel))
    cgroup_root = tmp_path / "cgroup"
    cg = cgroup_root / cgroup_rel.lstrip("/")
    cg.mkdir(parents=True)
    (cg / "cgroup.procs").write_text("".join("{}\n".format(p) for p in procs))
    for pid in procs:
        d = proc_root / str(pid)
        d.mkdir(exist_ok=True)
        (d / "status").write_text("Name:\tx\nState:\t{} (x)\n".format(states.get(pid, "R")))
        (d / "cmdline").write_bytes(cmdlines.get(pid, "job-{}".format(pid)).encode() + b"\0")
        (d / "comm").write_text("job\n")
    return proc_root, cgroup_root


def _doomed(tmp_path, *, me, **kw):
    proc_root, cgroup_root = _fake_tree(tmp_path, **kw)
    return dat.doomed(me=me, proc_root=proc_root, cgroup_root=cgroup_root,
                      settle_s=0, sleep=lambda _s: None)


# ---------------------------------------------------------------- the three verdicts

def test_all_three_verdicts_are_reachable(tmp_path):
    """THE CONTROL OVER THE WHOLE PARTITION, not a leg apiece.

    A detector that returns "nothing doomed" unconditionally passes every individual clean-path
    test in this file, and that is precisely the failure the module exists to prevent. Asserting
    the three outcomes are ALL reachable from one partition is the only shape that catches it --
    the same lesson `tools/launch_shape_census.py` records paying for three times in an afternoon.
    """
    clean, clean_reason = _doomed(tmp_path / "a", me=100, procs=[100])
    found, found_reason = _doomed(tmp_path / "b", me=100, procs=[100, 200])
    blind, blind_reason = dat.doomed(me=100, proc_root=tmp_path / "nonexistent",
                                     cgroup_root=tmp_path / "nope",
                                     settle_s=0, sleep=lambda _s: None)

    assert (clean, clean_reason) == ([], None)
    assert [f["pid"] for f in found] == [200] and found_reason is None
    assert blind == [] and blind_reason  # "we did not look" is a THIRD verdict, not a clean one


def test_a_lone_process_in_its_own_cgroup_reports_nothing(tmp_path):
    """THE ORDINARY PATH. A tick that waited on its child and is now returning alone must be
    silent, or the control is noise and gets turned off."""
    found, reason = _doomed(tmp_path, me=100, procs=[100])
    assert found == [] and reason is None
    assert dat.report_line(found, reason) is None


def test_a_stray_long_job_is_named_with_its_command_line(tmp_path):
    """DEFECT: a report naming only a pid is useless an hour later, because the process it names is
    gone by definition. The four deaths were each diagnosed by a person reconstructing WHAT had
    been launched."""
    found, reason = _doomed(tmp_path, me=100, procs=[100, 777],
                            cmdlines={777: "/bin/bash /var/tmp/replay_decade.sh"})
    assert reason is None
    assert found == [{"pid": 777, "cmdline": "/bin/bash /var/tmp/replay_decade.sh"}]
    line = dat.report_line(found, reason)
    assert "777" in line and "/var/tmp/replay_decade.sh" in line
    assert "launch_long_job" in line  # the report names the remedy, not just the symptom


def test_a_zombie_is_not_reported(tmp_path):
    """DEFECT: a child that has exited but not yet been reaped is already dead, so reporting it is
    a false positive on the ordinary path -- the FAIL-NOISY direction. This is the leg that keeps
    the control worth listening to."""
    found, reason = _doomed(tmp_path, me=100, procs=[100, 201], states={201: "Z"})
    assert found == [] and reason is None


def test_a_process_that_leaves_between_the_two_samples_is_not_reported(tmp_path):
    """DEFECT: the settle window's whole job. A single read cannot tell a long job from a child
    mid-exit; the INTERSECTION of two reads can. Failure mode is missing something that vanished
    on its own, which was never a loss."""
    proc_root, cgroup_root = _fake_tree(tmp_path, procs=[100, 202])
    procs_file = cgroup_root / "user.slice/bounded.service/cgroup.procs"

    def _departs(_s):
        procs_file.write_text("100\n")  # 202 exits during the settle

    found, reason = dat.doomed(me=100, proc_root=proc_root, cgroup_root=cgroup_root,
                               settle_s=0, sleep=_departs)
    assert found == [] and reason is None


def test_unreadable_is_reported_as_not_checked_and_never_as_clean(tmp_path):
    """DEFECT: "we did not look" rendered as "nothing found" is the fail-open. CLAUDE.md: fail
    closed, and say so on the SURFACE -- so the reported line must be unmistakable, not empty."""
    found, reason = dat.doomed(me=100, proc_root=tmp_path / "gone", cgroup_root=tmp_path / "gone",
                               settle_s=0, sleep=lambda _s: None)
    line = dat.report_line(found, reason)
    assert line is not None and "NOT CHECKED" in line
    assert dat.report_line([], None) is None  # and it is DIFFERENT from the genuinely-clean line


def test_check_and_log_never_raises_into_its_caller(tmp_path, monkeypatch):
    """DEFECT: this runs in the `finally` of the two processes that do all the unattended work,
    including the path taken when they are ALREADY failing. A diagnostic that can take down its
    caller is worse than the silence it replaces."""
    monkeypatch.setattr(dat, "doomed", lambda **kw: (_ for _ in ()).throw(RuntimeError("boom")))
    seen = []
    line = dat.check_and_log(seen.append)
    assert "NOT CHECKED" in line and "boom" in line
    assert seen == [line]


def test_a_logger_that_itself_raises_does_not_escape(tmp_path, monkeypatch):
    """Same defect, one layer out: the tick's `_log` writes to a file that can be full or gone."""
    monkeypatch.setattr(dat, "doomed", lambda **kw: ([{"pid": 9, "cmdline": "x"}], None))

    def _broken(_line):
        raise OSError("disk full")

    assert dat.check_and_log(_broken) is not None  # returned, not raised


# ---------------------------------------------------------------- the wiring

def _calls_check_and_log(tree) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "check_and_log":
            return True
    return False


def _function_named(path: Path, name: str):
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError("{} has no {}()".format(path, name))


def test_the_worker_tick_calls_it_on_every_exit_path():
    """DEFECT THIS EXISTS FOR, and it is the one `launch_shape_census` records catching in itself
    just before shipping: WIRED, or it is a control that never runs. Asserting the call sits in
    `run_tick`'s `finally` -- not merely somewhere in the module -- is what makes it fire on the
    rested and errored ticks too, which are exit paths a stray outlives just as well."""
    fn = _function_named(_REPO / "background" / "worker_tick.py", "run_tick")
    finallys = [n for n in ast.walk(fn) if isinstance(n, ast.Try) and n.finalbody]
    assert finallys, "run_tick no longer has a finally to hang the teardown check on"
    assert any(_calls_check_and_log(ast.Module(body=f.finalbody, type_ignores=[]))
               for f in finallys)


def test_the_seat_executor_calls_it_on_the_once_path():
    """Same wiring defect on the other bounded oneshot. `main()` is the operator surface and is
    pragma-no-cover, so a static assertion is the only control available -- and an absent one is
    how the seat-executor half would quietly never run."""
    fn = _function_named(_REPO / "background" / "seat_executor.py", "main")
    assert _calls_check_and_log(fn)


def test_both_wired_units_are_oneshot_control_group_killers():
    """KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. The check is only meaningful for a unit whose
    teardown kills the cgroup. If either unit stops being `Type=oneshot`, the premise is gone and
    this control must go red -- rather than the module quietly becoming decoration."""
    for unit in ("worker-tick.service", "seat-executor.service"):
        text = (_REPO / "background" / unit).read_text() if (
            _REPO / "background" / unit).exists() else None
        if text is None:
            continue  # seat-executor.service lives outside the tree on this machine
        assert "Type=oneshot" in text, "{} is no longer a oneshot".format(unit)
        # KillMode is unset, i.e. the default control-group. An explicit relaxation must be seen.
        assert "KillMode=" not in text or "KillMode=control-group" in text
