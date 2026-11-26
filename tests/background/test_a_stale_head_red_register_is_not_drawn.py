"""A HEAD-red register the census has not re-observed is not drawn, and a killed census still observes.

THE DEFECT (2026-11-16). No census completed from 2026-11-04 to 2026-11-16: five nights hit the
17400s suite bound and four were deferred by the memory governor. Each UNPROVEN run recorded
nothing at all, so `HEAD_RED_REGISTER.md` kept reading "17 owed, observed 2026-11-04",
`drawable()` kept returning 17, and the worker tick drew it three times a day against a count
that no fix could move.

The property these hold: **the register is drawn only while its newest run is at least as new as
the census's newest attempt**, and **a run killed at its bound records what it reached, and
clears only what it reached.**
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from datetime import datetime, timedelta, timezone

import pytest

from background import head_red_register as reg
from tools import head_green_census as hgc

T0 = datetime(2026, 11, 4, 7, 54, tzinfo=timezone.utc)


def _store_with_one_red():
    return reg.record(["tests/a.py::red"], head_sha="aaa", passed=10, now=T0,
                      store={"runs": [], "tests": {}})


def _drawable_for(store, monkeypatch):
    monkeypatch.setattr(reg, "load_observed", lambda path=None: store)
    import background.head_red_baseline as hrb
    monkeypatch.setattr(hrb, "load_baseline", lambda *a, **k: set())
    return reg.drawable()


def test_the_register_is_drawn_when_current_and_not_when_an_attempt_is_newer(monkeypatch):
    """ONE control over the whole partition: both branches must be takeable.

    MUTATIONS (each fires here): drop the `stale_attempts` check from `drawable` (stale is drawn);
    make `stale_attempts` return every attempt regardless of age (current is not drawn after a
    run that FOLLOWS an attempt); compare `>=`/`<` the wrong way round.
    """
    store = _store_with_one_red()
    current = _drawable_for(store, monkeypatch)

    reg.record_attempt(store, reason="the suite did not finish inside 17400s",
                       now=T0 + timedelta(days=1))
    stale = _drawable_for(store, monkeypatch)

    reg.record(["tests/a.py::red"], head_sha="bbb", passed=10, store=store,
               now=T0 + timedelta(days=2))
    recovered = _drawable_for(store, monkeypatch)

    assert current and not stale and recovered, (
        "drawn when current, NOT drawn when the census has tried since and observed nothing, "
        "drawn again once a run lands: got current={} stale={} recovered={}".format(
            current, stale, recovered))


def test_an_attempt_touches_no_test_and_no_run():
    store = _store_with_one_red()
    before = (repr(store["tests"]), repr(store["runs"]))
    reg.record_attempt(store, reason="deferred", now=T0 + timedelta(days=1))
    assert (repr(store["tests"]), repr(store["runs"])) == before
    assert reg.owed(store, set()) == ["tests/a.py::red"], (
        "an attempt observed nothing, so it must neither fix nor forgive anything")


def test_the_stale_register_says_so_on_the_document_and_the_doorbell(monkeypatch):
    store = _store_with_one_red()
    reg.record_attempt(store, reason="DEFERRED by resource_headroom", now=T0 + timedelta(days=1))
    text = reg.render(store, set())
    assert "## STALE" in text and "DEFERRED by resource_headroom" in text
    assert "tests/a.py::red" in text, "stale is not empty: the owed set is still shown"
    clause = reg.doorbell_clause(reg.summary(store, set()))
    assert clause.startswith(reg.REGISTER_NAME + ": STALE"), clause


def test_a_partial_run_clears_only_what_it_reached():
    """MUTATION: ignore `reached` in `record` -- the unreached red is cleared and this fires."""
    store = reg.record(["tests/a.py::fixed", "tests/z.py::unreached"], head_sha="aaa",
                       passed=10, now=T0, store={"runs": [], "tests": {}})
    reg.record(["tests/a.py::still"], head_sha="bbb", passed=5, now=T0 + timedelta(days=1),
               store=store, reached=["tests/a.py::fixed", "tests/a.py::still"])
    assert reg.owed(store, set()) == ["tests/a.py::still", "tests/z.py::unreached"]
    assert store["tests"]["tests/z.py::unreached"]["runs_red"] == 1, (
        "a run that did not reach a test did not observe it red again")
    assert store["runs"][-1]["partial"] is True and store["runs"][-1]["reached"] == 2
    assert not reg.stale_attempts(store)


def test_progress_parsing_counts_a_setup_error_as_red():
    text = "\n".join([
        "call\tpassed\ttests/a.py::ok",
        "setup\tfailed\ttests/a.py::broken_fixture",
        "call\tfailed\ttests/a.py::assert",
        "teardown\tfailed\ttests/a.py::assert",
        "call\tskipped\ttests/a.py::skip",
        "garbage line",
    ])
    got = hgc.parse_progress(text)
    assert got["failures"] == ["tests/a.py::assert", "tests/a.py::broken_fixture"]
    assert got["passed"] == 1
    assert len(got["reached"]) == 4


def test_the_plugin_is_loaded_by_the_census_and_streams_every_test(tmp_path):
    """END TO END through a real pytest: `-p tools.head_census_progress` + the env var write the stream,
    and the FIRST list reorders modules. MUTATIONS: stream only the call phase -- the setup
    error vanishes; drop `-p tools.head_census_progress` from
    `pytest_argv` -- nothing is streamed; drop the sort -- `b` no longer runs first."""
    assert "tools.head_census_progress" in hgc.pytest_argv()
    (tmp_path / "test_a.py").write_text(
        "import pytest\n\n@pytest.fixture\ndef broken():\n    raise RuntimeError\n\n"
        "def test_one():\n    pass\n\ndef test_two():\n    assert 0\n\n"
        "def test_setup_error(broken):\n    pass\n")
    (tmp_path / "test_b.py").write_text("def test_three():\n    pass\n")
    progress = tmp_path / "progress.tsv"
    env = dict(os.environ, PYTHONPATH=str(hgc.PROJECT_DIR))
    env.update({hgc.PROGRESS_ENV: str(progress), hgc.FIRST_ENV: "test_b.py"})
    subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "tools.head_census_progress",
                    "-p", "no:cacheprovider", str(tmp_path)],
                   cwd=str(tmp_path), env=env, capture_output=True, text=True, timeout=120)
    got = hgc.parse_progress(progress.read_text())
    # A SETUP ERROR never reaches the call phase; streaming only `call` would read it as never
    # reached, so a fixture-dead module would sit in the register un-clearable and un-aged.
    assert got["failures"] == ["test_a.py::test_setup_error", "test_a.py::test_two"]
    assert got["passed"] == 2
    assert progress.read_text().splitlines()[0].endswith("test_b.py::test_three"), (
        "the register's own modules must run first so a bound cannot cut them off")


def test_a_test_that_patches_open_does_not_end_the_census(tmp_path):
    """The call-phase report fires before teardown, so a test that monkeypatches `builtins.open`
    is still patched when the stream is written. On 20 Nov that raised inside the hook and the
    INTERNALERROR ended the suite at test 6033. MUTATION: write with the builtin `open` in
    `pytest_runtest_logreport` -- the session dies and `test_after` is never reached."""
    (tmp_path / "test_a.py").write_text(
        "def test_patches_open(monkeypatch):\n"
        "    def _boom(*a, **kw):\n        raise OSError('no fd')\n"
        "    monkeypatch.setattr('builtins.open', _boom)\n\n"
        "def test_after():\n    pass\n")
    progress = tmp_path / "progress.tsv"
    env = dict(os.environ, PYTHONPATH=str(hgc.PROJECT_DIR))
    env.update({hgc.PROGRESS_ENV: str(progress)})
    env.pop(hgc.FIRST_ENV, None)
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "tools.head_census_progress",
                           "-p", "no:cacheprovider", str(tmp_path)],
                          cwd=str(tmp_path), env=env, capture_output=True, text=True, timeout=120)
    assert "INTERNALERROR" not in done.stdout + done.stderr
    assert hgc.parse_progress(progress.read_text())["reached"] == [
        "test_a.py::test_after", "test_a.py::test_patches_open"]


@pytest.mark.parametrize("ends", ["killed", "finishes", "exits_early"])
def test_a_killed_suite_reports_what_it_reached_and_a_finished_one_does_not(tmp_path, capsys,
                                                                            monkeypatch, ends):
    """MUTATION: restore the discard (return "" without filling `observed["partial"]`) -- the
    killed leg fires. The finished leg holds that partial is NOT taken from a run with a summary.

    The exits_early leg is the 17 Nov 2026 census: pytest exited after 1h21m with no summary
    line, and its output and progress stream were both discarded, so neither the cause nor the
    reds it re-observed survived. MUTATION: drop the no-summary branch -- this leg fires."""
    script = textwrap.dedent("""
        import os, sys, time
        with open(os.environ[{env!r}], "a") as fh:
            fh.write("call\\tpassed\\ttests/a.py::ok\\n")
            fh.write("call\\tfailed\\ttests/a.py::red\\n")
        if {ends!r} == "killed":
            time.sleep(30)
        if {ends!r} == "exits_early":
            print("INTERNALERROR> the cause of the early exit")
            sys.exit(3)
        print("1 failed, 1 passed in 0.1s")
    """).format(env=hgc.PROGRESS_ENV, ends=ends)
    monkeypatch.setattr(hgc, "pytest_argv", lambda: [sys.executable, "-c", script])
    monkeypatch.setattr(hgc, "first_modules", lambda: [])
    observed: dict = {}
    out = hgc._run_admitted_suite(tmp_path, {"TMPDIR": str(tmp_path), "PATH": "/usr/bin:/bin"},
                                  5, observed)
    if ends == "finishes":
        assert "1 passed" in out and "partial" not in observed and "exited_early" not in observed
    else:
        assert out == "" and hgc.evaluate(out)["status"] == "UNPROVEN"
        assert observed["partial"] == {"failures": ["tests/a.py::red"], "passed": 1,
                                       "reached": ["tests/a.py::ok", "tests/a.py::red"],
                                       "crash": {}}
    if ends == "exits_early":
        assert observed["exited_early"] == "pytest exited rc=3 with no summary line"
        assert "the cause of the early exit" in capsys.readouterr().err, \
            "the output's tail must reach the journal, or the next early exit is undiagnosable"
    assert not list(tmp_path.glob("head_census_progress_*")), "the stream must be cleaned up"


def test_an_unproven_census_records_its_attempt(monkeypatch):
    """MUTATION: return early on UNPROVEN as before -- no attempt reaches the store, the register
    never reads stale, and it is drawn for as long as the census keeps failing."""
    saved = {}

    class _Reg:
        load_observed = staticmethod(lambda: {"runs": [{"at": "2026-11-04T07:54:02+00:00"}],
                                              "tests": {}})
        record_attempt = staticmethod(reg.record_attempt)
        save_observed = staticmethod(lambda store: saved.update(store=store))
        write_register = staticmethod(lambda store, accepted: "register.md")

    import background
    monkeypatch.setattr(background, "head_red_register", _Reg, raising=False)
    monkeypatch.setitem(sys.modules, "background.head_red_register", _Reg)
    note = hgc._record_observation({"status": "UNPROVEN", "reason": "deferred: budget",
                                    "subject_head": "ccc"})
    assert "attempt recorded" in note, note
    assert saved["store"]["attempts"][-1]["reason"] == "deferred: budget"
    assert reg.stale_attempts(saved["store"])
