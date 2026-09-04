"""THE DEFECT, observed live at 2026-09-04 15:48Z in `sim_runner` -- the path that actually
publishes in the steady state:

    publish-gate outcome recording failed (non-fatal): cannot import name
    'recorded_instant_seconds' from 'background.episode_monotonic'

The name was present at line 145 in HEAD and in the shared tree, and that file's mtime was 15:48Z.
Not a broken landing: a TORN READ of a source file under a live daemon, in a tree three lanes write
concurrently. The bare `except` did what it was built to do -- the loop survived -- and the outcome
was gone.

"Non-fatal" was true of the loop and false of the measurement. The outcome being routed is usually
a FAILURE, so one that never arrives makes the episode read one failure SHORT of what happened --
the under-reporting `episode_monotonic` exists to prevent, arriving by the one route that guard
cannot see because it is downstream of the import that failed.

AND THERE WERE TWO OF THESE WRAPPERS. `background_worker` carried a byte-for-byte twin. The first
draft of this repair went into the worker, which was NOT where the loss was observed -- one
requirement, two implementations, fixed in one and live in the other. Hence
`background/publish_outcome_route.py`, and hence the wiring controls at the bottom of this file.
"""
from __future__ import annotations

import builtins
import inspect

import pytest

from background import background_worker, publish_outcome_route, sim_runner


def _flaky_import(monkeypatch, fail_times, exc):
    """Make the first `fail_times` imports of `process_run_complete` raise, and count every one.

    Patched at `builtins.__import__` rather than at the target function, deliberately: the defect
    is that the IMPORT is torn, and a control that stubbed the function would pass just as happily
    with the import hoisted out of the retry -- which is the state that loses the outcome again.
    """
    real = builtins.__import__
    seen = []

    def flaky(name, glo=None, loc=None, fromlist=(), level=0):
        if "process_run_complete" in (fromlist or ()):
            seen.append(name)
            if len(seen) <= fail_times:
                raise exc
        return real(name, glo, loc, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", flaky)
    return seen


@pytest.fixture
def detector(monkeypatch):
    """Records what reached `record_publish_gate_outcome`, and nothing else runs."""
    from background import process_run_complete as prc

    got = []
    monkeypatch.setattr(prc, "record_publish_gate_outcome",
                        lambda m, rc, kind=None: got.append((m, rc, kind)))
    return got


# ── the whole partition in one control ──────────────────────────────────────────────────────
def test_the_route_takes_all_three_of_its_verdicts_and_not_one_of_them_always(monkeypatch,
                                                                              detector):
    """A route that retried everything, or one that retried nothing, passes most of the leg-by-leg
    tests below. So the partition is asserted together first: recorded-first-try, recorded-on-
    retry, and lost must all be REACHABLE from the same function.
    """
    slept = []
    kw = {"log": lambda _m: None, "sleep": lambda s: slept.append(s)}

    with monkeypatch.context() as m:
        _flaky_import(m, 0, ImportError("never raised"))
        clean = publish_outcome_route.route("mk", 0, **kw)
    with monkeypatch.context() as m:
        _flaky_import(m, 1, ImportError("torn once"))
        retried = publish_outcome_route.route("mk", 1, **kw)
    with monkeypatch.context() as m:
        _flaky_import(m, 99, ImportError("still being written"))
        lost = publish_outcome_route.route("mk", 1, **kw)

    assert clean and retried and not lost, \
        "clean={} retried={} lost={}".format(clean, retried, lost)
    assert len(detector) == 2, "the lost one must NOT have reached the detector"
    # TWO waits, not one: the LOST case also pays for its second look before giving up. The clean
    # case pays for none, which is the property worth pinning here -- a route that slept on the
    # healthy path would put a second on every publish in the steady state.
    assert slept == [publish_outcome_route.IMPORT_RETRY_SECONDS] * 2, \
        "the clean route must not wait, and each torn one waits exactly once"


# ── what each verdict does ──────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("exc", [
    ImportError("cannot import name 'recorded_instant_seconds' from 'background.episode_monotonic'"),
    SyntaxError("unexpected EOF while parsing"),
])
def test_a_torn_import_is_retried_so_the_outcome_still_reaches_the_detector(monkeypatch, detector,
                                                                            exc):
    """Both shapes a half-written module takes: a truncated parse (SyntaxError), and a file that
    parses fine but does not hold the name yet (ImportError).

    MUTATION: hoist the import above the loop, or set ATTEMPTS to 1, and the outcome is lost.
    """
    seen = _flaky_import(monkeypatch, 1, exc)
    said = []

    assert publish_outcome_route.route("mk", 1, kind=None, log=said.append,
                                       sleep=lambda _s: None) is True
    assert len(seen) == 2, "the import must be re-attempted, not reused from a failed first read"
    assert detector == [("mk", 1, None)]
    assert any("torn" in m for m in said), "the recovery must be visible: {}".format(said)


def test_a_persistently_torn_import_is_reported_as_LOST_and_not_as_a_skip(monkeypatch, detector):
    """It still may not break the loop -- a monitoring failure that takes the pipeline down is a
    worse outage than the one it watches. What changes is the WORD. "skipped" and "non-fatal" both
    read benign, and what happened is that the detector never saw a cycle it should have.

    MUTATION: restore either benign word and this fails.
    """
    seen = _flaky_import(monkeypatch, 99, ImportError("still being written"))
    said = []

    assert publish_outcome_route.route("mk", 1, log=said.append, sleep=lambda _s: None) is False
    assert len(seen) == publish_outcome_route.ATTEMPTS, \
        "bounded -- a retry loop inside a monitoring path is a wedge of its own"
    assert detector == []
    assert any("LOST" in m and "one outcome short" in m for m in said), said
    assert not any("skip" in m.lower() and "not a skip" not in m for m in said)


def test_a_failure_that_is_NOT_a_torn_read_is_never_retried(monkeypatch):
    """The retry is keyed to the transient class and nothing else. A detector that raises on real
    state will raise again a second later, and re-running its side effects is how one bad cycle
    becomes two. This is the leg that proves the retry is not just "try everything twice"."""
    from background import process_run_complete as prc

    attempts = []

    def _boom(m, rc, kind=None):
        attempts.append(rc)
        raise ValueError("the state file says something impossible")

    monkeypatch.setattr(prc, "record_publish_gate_outcome", _boom)
    slept = []

    assert publish_outcome_route.route("mk", 1, log=lambda _m: None,
                                       sleep=lambda s: slept.append(s)) is False
    assert attempts == [1], "a non-transient failure must be attempted exactly once"
    assert slept == [], "and must not pay the retry wait"


def test_a_clean_route_says_nothing_at_all(monkeypatch, detector):
    """Noise on the healthy path is how the LOST line stops being read."""
    _flaky_import(monkeypatch, 0, ImportError("never raised"))
    said = []

    assert publish_outcome_route.route("mk", 0, log=said.append) is True
    assert said == []


def test_it_never_raises_into_the_run_loop(monkeypatch):
    """The loops this reports from must survive anything it does, including a logger that throws."""
    from background import process_run_complete as prc

    monkeypatch.setattr(prc, "record_publish_gate_outcome",
                        lambda m, rc, kind=None: (_ for _ in ()).throw(RuntimeError("boom")))
    assert publish_outcome_route.route("mk", 1, log=None) is False


def test_the_route_is_a_leaf_so_reaching_it_cannot_be_torn_by_the_reporting_stack():
    """The whole point of the retry is that the deep import chain is what gets written. If this
    module grew a module-scope import of the reporting stack, reaching it would be torn by the same
    writes, and the retry would sit behind the failure it exists to survive.

    MUTATION: add `from background import process_run_complete` at module scope and this fails.
    """
    import ast

    src = inspect.getsource(publish_outcome_route)
    top = [n for n in ast.parse(src).body if isinstance(n, (ast.Import, ast.ImportFrom))]
    names = [n.module or "" for n in top if isinstance(n, ast.ImportFrom)]
    names += [a.name for n in top if isinstance(n, ast.Import) for a in n.names]
    assert set(names) <= {"__future__", "time"}, "module-scope imports: {}".format(names)


# ── and BOTH callers go through it, which is the half the first draft got wrong ─────────────
@pytest.mark.parametrize("wrapper", [
    background_worker._record_publish_gate_outcome,
    sim_runner._record_publish_gate_outcome,
])
def test_both_publishers_route_through_the_one_implementation(wrapper):
    """THE DEFECT INSIDE THE REPAIR. These two wrappers were byte-for-byte twins, and the first
    draft of this fix went into the worker -- which is NOT where the loss was observed. One
    requirement with two implementations is this project's most expensive recurring shape.

    MUTATION: restore a local `from background import process_run_complete` in either wrapper and
    that one fails while the other still passes -- which is precisely the state being forbidden.
    """
    src = inspect.getsource(wrapper)
    assert "publish_outcome_route" in src and "route(" in src
    body = src.split('"""')[2]
    assert "process_run_complete" not in body, \
        "the wrapper must not re-open the torn import chain itself"


@pytest.mark.parametrize("wrapper", [
    background_worker._record_publish_gate_outcome,
    sim_runner._record_publish_gate_outcome,
])
def test_neither_wrapper_can_raise_into_its_daemon(wrapper, monkeypatch, tmp_path):
    """The route is a leaf, but it is still an import, and the caller's own guard is the last
    resort for the vanishing case where the ROUTE is the file being written."""
    real = builtins.__import__

    def flaky(name, glo=None, loc=None, fromlist=(), level=0):
        # `from background.publish_outcome_route import route` puts the module in the NAME and
        # `route` in the fromlist -- the opposite way round from the helper above, which is why
        # this is spelled out rather than shared.
        if "publish_outcome_route" in name or "publish_outcome_route" in (fromlist or ()):
            raise ImportError("the route itself is mid-write")
        return real(name, glo, loc, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", flaky)
    said = []
    monkeypatch.setattr(background_worker, "log", said.append)
    monkeypatch.setattr(sim_runner, "log", said.append)

    marker = tmp_path / "run_complete_20260904T154800Z.md"
    marker.write_text("x")
    wrapper(marker, 1)  # must not raise

    assert any("LOST" in m for m in said), said
