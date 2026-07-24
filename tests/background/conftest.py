"""Directory-scoped test isolation for the supervisor draw/rest ladder.

CLASS FIX (R10), 2026-07-24, WEDGE3_AND_RUNG1_MECHANISE: the RUNG-1 publish-gate-wedge
detector (`supervisor._publish_gate_wedge_active`, wired as the TOP rung of both
`_self_refill_draw` and `_is_drained_and_gated`) reads the REAL on-disk
`.publish_gate_state.json` + `.last_tested_hash`. Any test in this directory that exercises
the draw/rest ladder WITHOUT isolating those two files silently leaks the live gate state: when
the real gate is wedged AND HEAD != last_tested_hash, the rung fires and every "map empty -> rest"
/ "draws forward-discovery" assertion flips (12 such tests red-ed the publish gate the moment the
rung landed -- the fork's own full-suite run false-greened only because HEAD == last_tested_hash
at that instant kept the detector transiently silent).

This is the exact "new always-drawable rung needs fixture isolation" class the F-lane draw hit
before (see test_supervisor.py::_isolate). Rather than re-patch each file on touch, this autouse
fixture neutralises the leak for the WHOLE directory: it points both state files at a clean,
absent tmp path (an absent/empty state => detector returns None => no phantom wedge). The one
test that genuinely needs a wedged state (test_publish_gate_wedge_draw.py) writes it in the test
BODY via its own monkeypatch, which runs after this fixture's setup and therefore wins; the tests
that already isolate explicitly (test_supervisor.py::_isolate) merely point at a different clean
tmp -- also non-wedged, so correctness is unaffected either way.
"""
import pytest

from background import supervisor


@pytest.fixture(autouse=True)
def _isolate_publish_gate_wedge_state(tmp_path, monkeypatch):
    """Default every test in tests/background/ to a NON-wedged publish-gate state so the
    RUNG-1 wedge detector cannot leak the real gate state into unrelated draw/rest assertions.
    Tests that need a specific wedged state override these paths in their own body."""
    monkeypatch.setattr(
        supervisor, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json", raising=False
    )
    monkeypatch.setattr(
        supervisor, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash", raising=False
    )
    # RUNG-7 PLANNER (director ruling WORK_IS_THE_DEFAULT 2026-07-23): the planner reads the real
    # DIRECTOR_AXES.md, which is populated -> planner fires -> rest is never legitimate. That would
    # flip every "map empty -> rest" assertion in this dir (same fixture-isolation class as the wedge
    # state above). Default the axes path to an ABSENT tmp file so the planner does NOT fire by
    # default; the R15 planner tests point it at a populated file explicitly.
    monkeypatch.setattr(
        supervisor, "DIRECTOR_AXES_PATH", tmp_path / "DIRECTOR_AXES_absent.md", raising=False
    )
