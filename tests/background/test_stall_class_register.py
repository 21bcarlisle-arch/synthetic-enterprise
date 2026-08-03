"""R15 mutation tests for the stall-class register (HX2_stall_set_coverage_verdict).

This is a CONTROLS atom, so R15 is binding, not decorative: every detector added here
is proven to FIRE on its own named defect AND to stay quiet on the benign look-alike,
and each of the three killer patterns is ruled out explicitly.

  TAUTOLOGY   -> test_origin_freeze_never_reads_the_local_tracking_ref
                 (the freeze verdict must not be derived from the stale ref that IS
                  the failure)
  FAIL-OPEN   -> test_*_malformed_*, test_non_finite_*
  FAIL-SILENT -> test_registry_fails_loud_when_a_named_detector_vanishes,
                 test_git_unreadable_is_unavailable_not_clean,
                 test_origin_unreachable_is_unavailable_not_clean

ISOLATION: every test drives a FAKE git runner or a tmp_path state file. Nothing here
reads or writes real docs/observability/ state, and no stdlib symbol is patched
globally (a blanket Path patch once escaped into another module's test and ran the
real publish pipeline).
"""
from __future__ import annotations

import pytest

from background import stall_class_register as scr

HOUR = 3600.0
T0 = 1_785_000_000.0  # arbitrary fixed base; every assertion is RELATIVE to it, never pinned


# ── fake primary state ──────────────────────────────────────────────────────────
def make_runner(commits=None, inputs=None, *, log_rc=0, input_rc=0):
    """A fake `git`. `commits` is [(epoch, subject)]; `inputs` is
    [(epoch, subject, [paths])] as they would appear in a --diff-filter=A log."""
    commits = commits or []
    inputs = inputs or []
    calls: list[tuple[str, ...]] = []

    def run(*args: str) -> tuple[int, str]:
        calls.append(args)
        if args[:1] == ("log",) and "--diff-filter=A" in args:
            if input_rc != 0:
                return input_rc, ""
            out = []
            for ts, subject, paths in inputs:
                out.append(f"\x01{int(ts)}\x00{subject}")
                out.extend(paths)
            return 0, "\n".join(out)
        if args[:1] == ("log",):
            if log_rc != 0:
                return log_rc, ""
            return 0, "\n".join(f"{int(ts)}\x00{s}" for ts, s in commits)
        raise AssertionError(f"unexpected git call {args}")

    run.calls = calls  # type: ignore[attr-defined]
    return run


# ── G1/G2: the enumeration and its FAIL-SILENT guard ────────────────────────────
def test_every_named_detector_resolves():
    resolved = scr.resolve_detectors()
    named = [c.id for c in scr.STALL_CLASSES if c.detector]
    assert sorted(resolved) == sorted(named)
    assert all(callable(v) for v in resolved.values())


def test_registry_fails_loud_when_a_named_detector_vanishes(monkeypatch):
    """MUTATION (FAIL-SILENT): rename/delete a detector a class points at. The
    registry must RAISE, never quietly return a smaller set -- a silently shrunk
    stall set reads as 'no stalls of this class', which is how a counter certifies a
    span it never checked."""
    broken = scr.STALL_CLASSES[0].__class__(
        id="ghost",
        summary="x",
        detector="background.supervisor:_detector_that_was_deleted",
        evidence_kind="point",
        origin="mutation",
        verdict="already_detected",
    )
    monkeypatch.setattr(scr, "STALL_CLASSES", scr.STALL_CLASSES + (broken,))
    with pytest.raises(scr.StallRegistryError, match="no longer exists"):
        scr.resolve_detectors()
    assert "BROKEN" in scr.coverage_line()


def test_registry_fails_loud_when_a_detector_module_vanishes(monkeypatch):
    broken = scr.STALL_CLASSES[0].__class__(
        id="ghost",
        summary="x",
        detector="background.module_that_does_not_exist:f",
        evidence_kind="point",
        origin="mutation",
        verdict="already_detected",
    )
    monkeypatch.setattr(scr, "STALL_CLASSES", (broken,))
    with pytest.raises(scr.StallRegistryError, match="does not import"):
        scr.resolve_detectors()


def test_uncovered_classes_are_named_not_omitted():
    """G1: a class with no detector must be VISIBLE. An omitted class is invisible to
    HX1; an uncovered one is a named hole."""
    cov = scr.coverage()
    assert cov.total == len(scr.STALL_CLASSES)
    assert set(cov.uncovered) == {"harden_while_content_unminted", "act_later_ruled_reversible"}
    assert not cov.complete
    line = scr.coverage_line()
    assert "UNCOVERED" in line and "not *proof*" not in line
    assert "harden_while_content_unminted" in line


def test_coverage_reads_green_only_when_every_class_is_covered(monkeypatch):
    """Both-ways for the coverage surface itself: it is not hardcoded amber."""
    covered_only = tuple(c for c in scr.STALL_CLASSES if c.detector)
    monkeypatch.setattr(scr, "STALL_CLASSES", covered_only)
    assert scr.coverage().complete
    assert scr.coverage_line().startswith("🟢")


# ── E1/E4: the progress-gap / rescue detector ───────────────────────────────────
def test_fires_on_a_stall_ended_by_an_advisor_ruling():
    """FIRES (E4, the named defect): 30h of silence, an advisor ruling lands, work
    resumes 25 min later. Modelled on the real 2026-07-25/27 42h deadlock."""
    ruling_at = T0 + 30 * HOUR
    runner = make_runner(
        commits=[(T0, "feat: last real work before the silence"),
                 (ruling_at + 25 * 60, "EIGHTH CLASS fix: pending-batch deadlock")],
        inputs=[(ruling_at, "[DIRECTOR-RULING][ADVISOR-STAGED] EIGHTH CLASS",
                 ["docs/staging/DIRECTOR_RULING_EIGHTH_CLASS.md"])],
    )
    events = scr.detect_progress_gap_stalls(T0 - HOUR, T0 + 40 * HOUR, runner=runner)
    assert [e.class_id for e in events] == ["stall_ended_by_director_or_advisor_input"]
    assert events[0].channel == "advisor_bridge"
    assert not events[0].unavailable
    assert "25 min after advisor_bridge" in events[0].detail


def test_fires_on_an_ntfy_steer_using_the_filename_arrival_time():
    """The from_rich_* filename carries the true UTC ARRIVAL time; the commit that
    sweeps it in may be hours later. Attribution must use arrival, or a real rescue
    reads as arriving after the work it caused."""
    arrival = scr._parse_from_rich_stamp("20260729", "173731")
    assert arrival is not None
    runner = make_runner(
        commits=[(arrival - 20 * HOUR, "feat: work before"),
                 (arrival + 30 * 60, "feat: work resumed")],
        # committed a full day later, deliberately
        inputs=[(arrival + 24 * HOUR, "archive(staging): sweep",
                 ["docs/staging/done/from_rich_20260729_173731.md"])],
    )
    events = scr.detect_progress_gap_stalls(arrival - 30 * HOUR, arrival + 40 * HOUR, runner=runner)
    assert [e.class_id for e in events] == ["stall_ended_by_director_or_advisor_input"]
    assert events[0].channel == "ntfy"


def test_quiet_on_a_director_decision_during_healthy_progress():
    """DOES NOT FIRE (the benign look-alike R15 demands, and the ruling's own
    stall/decision split): the director touches the machine every bit as often, but
    work is flowing throughout. A DECISION-class touch is unrestricted and must
    produce NO event."""
    commits = [(T0 + i * 20 * 60, f"feat: steady work {i}") for i in range(12)]
    runner = make_runner(
        commits=commits,
        inputs=[(T0 + 2 * HOUR, "[DIRECTOR-RULING][ADVISOR-STAGED] curriculum call",
                 ["docs/staging/DIRECTOR_RULING_CURRICULUM.md"]),
                (T0 + 3 * HOUR, "sweep", ["docs/staging/done/from_rich_20260101_120000.md"])],
    )
    assert scr.detect_progress_gap_stalls(T0, T0 + 5 * HOUR, runner=runner) == []


def test_unattributed_gap_is_still_a_stall():
    """E1 fallback: a console rescue leaves NO trace in this repo (director_input_log
    writes to the private ops repo), so the gap it ended is all that is visible. It
    must still count -- under R17 a long silence is a stall whether or not anyone can
    say who ended it."""
    runner = make_runner(
        commits=[(T0, "feat: before"), (T0 + 4 * HOUR, "feat: after")], inputs=[]
    )
    events = scr.detect_progress_gap_stalls(T0 - HOUR, T0 + 6 * HOUR, runner=runner)
    assert [e.class_id for e in events] == ["meaningful_progress_gap"]
    assert events[0].channel == "n/a"


def test_input_long_before_resumption_is_not_credited_as_the_rescue():
    """The input lands early in the gap but work only resumes 3h later -- outside the
    attribution window. Counted as a stall, but NOT attributed: a coincidence must not
    be reported as causation."""
    runner = make_runner(
        commits=[(T0, "feat: before"), (T0 + 5 * HOUR, "feat: after")],
        inputs=[(T0 + 30 * 60, "[DIRECTOR-RULING][ADVISOR-STAGED] unrelated",
                 ["docs/staging/DIRECTOR_RULING_X.md"])],
    )
    events = scr.detect_progress_gap_stalls(T0 - HOUR, T0 + 6 * HOUR, runner=runner)
    assert [e.class_id for e in events] == ["meaningful_progress_gap"]


def test_a_staging_commit_is_input_not_progress():
    """REGRESSION, found by running this detector against real git history: the
    advisor's own `[ADVISOR-STAGED]` staging commit was being counted as the machine
    resuming work, which closed the gap at the doorbell and hid the rescue. If this
    ever regresses, a doorbelled stall becomes undetectable by construction."""
    ruling_at = T0 + 30 * HOUR
    runner = make_runner(
        commits=[(T0, "feat: before"),
                 (ruling_at, "[DIRECTOR-RULING][ADVISOR-STAGED] EIGHTH CLASS"),
                 (ruling_at + 25 * 60, "feat: machine actually resumes")],
        inputs=[(ruling_at, "[DIRECTOR-RULING][ADVISOR-STAGED] EIGHTH CLASS",
                 ["docs/staging/DIRECTOR_RULING_EIGHTH_CLASS.md"])],
    )
    assert scr.meaningful_commits(T0 - HOUR, T0 + 40 * HOUR, runner=runner) == [
        (T0, "feat: before"),
        (ruling_at + 25 * 60, "feat: machine actually resumes"),
    ]
    events = scr.detect_progress_gap_stalls(T0 - HOUR, T0 + 40 * HOUR, runner=runner)
    assert [e.class_id for e in events] == ["stall_ended_by_director_or_advisor_input"]


def test_non_progress_commits_do_not_refresh_the_clock():
    """FAIL-OPEN guard: auto-process/chore no-ops must not break a gap, or a machine
    that publishes every 15 minutes never looks stalled -- the exact fail-open the
    deadman was rebuilt to close. Definition shared with deadmans_switch."""
    runner = make_runner(
        commits=[(T0, "feat: before"),
                 (T0 + HOUR, "Auto-process run complete: report + LATEST.md"),
                 (T0 + 2 * HOUR, "chore(liveness): publish heartbeat"),
                 (T0 + 4 * HOUR, "feat: after")],
    )
    events = scr.detect_progress_gap_stalls(T0 - HOUR, T0 + 6 * HOUR, runner=runner)
    assert [e.class_id for e in events] == ["meaningful_progress_gap"]
    assert "240 min" in events[0].detail


def test_git_unreadable_is_unavailable_not_clean():
    """FAIL-SILENT: git unreadable must yield an `unavailable` event, never []. An
    empty list means 'this span was clean', which is a certification the check never
    performed."""
    events = scr.detect_progress_gap_stalls(T0, T0 + HOUR, runner=make_runner(log_rc=128))
    assert len(events) == 1 and events[0].unavailable
    assert scr.meaningful_commits(T0, T0 + HOUR, runner=make_runner(log_rc=128)) is None


def test_input_history_unreadable_is_flagged_even_when_commits_read():
    """Half-blind is not clean: if attribution could not run, say so, because an
    unattributed gap might in fact be a rescue."""
    runner = make_runner(
        commits=[(T0, "feat: before"), (T0 + 4 * HOUR, "feat: after")], input_rc=128
    )
    events = scr.detect_progress_gap_stalls(T0 - HOUR, T0 + 6 * HOUR, runner=runner)
    assert any(e.unavailable for e in events)


def test_malformed_commit_rows_are_dropped_not_crashed():
    """FAIL-OPEN: a malformed/non-finite timestamp must not become a commit at epoch
    zero (which would manufacture a 56-year 'gap')."""
    def run(*args):
        if "--diff-filter=A" in args:
            return 0, ""
        return 0, "not-a-number\x00feat: x\nNaN\x00feat: y\ngarbage-with-no-nul\n" + \
                  f"{int(T0)}\x00feat: real"
    assert scr.meaningful_commits(T0 - HOUR, T0 + HOUR, runner=run) == [(T0, "feat: real")]


# ── E2: the publish-gate wedge adapter ──────────────────────────────────────────
def _wedged_state(now, *, age_seconds, failures=4):
    """Build a wedged state RELATIVE to `now`. Never pin a generated/absolute value in
    a control -- a pinned date once wedged publishing for four days."""
    start = now - age_seconds
    return {
        "wedge_since": start,
        "alerted_at": start + 60,
        "failures": [
            {"ts": start + i * 600, "reason": "test_regression", "rc": 1, "git_hash": "deadbeef"}
            for i in range(failures)
        ],
    }


def test_wedge_adapter_fires_past_the_directors_one_hour_bar(tmp_path):
    """FIRES (E2): >1h wedge, no gate pass at HEAD."""
    import json
    import time

    now = time.time()
    state = tmp_path / ".publish_gate_state.json"
    state.write_text(json.dumps(_wedged_state(now, age_seconds=95 * 60)))
    last_tested = tmp_path / ".last_tested_hash"
    last_tested.write_text("0000000")
    ev = scr.detect_publish_gate_wedge(
        now=now, state_path=state, last_tested_path=last_tested, head="fffffff"
    )
    assert ev is not None and ev.class_id == "publish_gate_wedged_over_an_hour"
    assert "PUBLISH-GATE WEDGE" in ev.detail


def test_wedge_adapter_quiet_below_the_bar(tmp_path):
    """DOES NOT FIRE: the same failures, 20 minutes old. The director's bar is one
    hour and a short streak is a flake, not a wedge."""
    import json
    import time

    now = time.time()
    state = tmp_path / ".publish_gate_state.json"
    state.write_text(json.dumps(_wedged_state(now, age_seconds=20 * 60)))
    last_tested = tmp_path / ".last_tested_hash"
    last_tested.write_text("0000000")
    assert scr.detect_publish_gate_wedge(
        now=now, state_path=state, last_tested_path=last_tested, head="fffffff"
    ) is None


def test_wedge_adapter_quiet_when_the_gate_passed_at_head(tmp_path):
    """DOES NOT FIRE (the benign look-alike, and the anti-tautology cross-check): the
    failures are stale because the gate has since PASSED at HEAD. Note the known trap
    this preserves -- the wedge clears on a real publish/pass, not on a green code
    edit, because .last_tested_hash is written only by an actual gate pass."""
    import json
    import time

    now = time.time()
    state = tmp_path / ".publish_gate_state.json"
    state.write_text(json.dumps(_wedged_state(now, age_seconds=95 * 60)))
    last_tested = tmp_path / ".last_tested_hash"
    last_tested.write_text("fffffff")
    assert scr.detect_publish_gate_wedge(
        now=now, state_path=state, last_tested_path=last_tested, head="fffffff"
    ) is None


# ── E3: the origin-freeze detector ──────────────────────────────────────────────
def origin_runner(*, local_head="aaaa111", unpushed=None, rev_parse_rc=0, log_rc=0):
    unpushed = unpushed or []
    calls: list[tuple[str, ...]] = []

    def run(*args: str) -> tuple[int, str]:
        calls.append(args)
        if args[0] == "rev-parse":
            return rev_parse_rc, ("" if rev_parse_rc else local_head + "\n")
        if args[0] == "log":
            if log_rc:
                return log_rc, ""
            return 0, "\n".join(str(int(t)) for t in unpushed)
        raise AssertionError(f"unexpected git call {args}")

    run.calls = calls  # type: ignore[attr-defined]
    return run


def test_origin_freeze_fires_past_thirty_minutes():
    """FIRES (E3, the named defect): the phantom-push signature -- local commits that
    have not reached origin, oldest 3.5h old, exactly the 2026-07-24 freeze."""
    now = T0 + 10 * HOUR
    run = origin_runner(unpushed=[now - 3.5 * HOUR, now - 2 * HOUR, now - 10 * 60])
    ev = scr.detect_origin_freeze(now, runner=run, remote_head_fn=lambda: "bbbb222")
    assert ev is not None and ev.class_id == "origin_frozen_over_thirty_minutes"
    assert not ev.unavailable
    assert "3 local commit(s)" in ev.detail and "210 min" in ev.detail


def test_origin_freeze_quiet_when_origin_is_at_head():
    """DOES NOT FIRE: origin == HEAD is a healthy pipeline."""
    run = origin_runner(local_head="aaaa111")
    assert scr.detect_origin_freeze(T0, runner=run, remote_head_fn=lambda: "aaaa111") is None


def test_origin_freeze_quiet_inside_the_push_throttle():
    """DOES NOT FIRE (the benign look-alike that would otherwise fire constantly): the
    publisher batches pushes on a 30-minute throttle, so unpushed commits younger than
    the threshold are NORMAL. A detector that fired here would call every healthy
    cycle a stall."""
    now = T0 + 10 * HOUR
    run = origin_runner(unpushed=[now - 12 * 60, now - 60])
    assert scr.detect_origin_freeze(now, runner=run, remote_head_fn=lambda: "bbbb222") is None


def test_origin_unreachable_is_unavailable_not_clean():
    """FAIL-SILENT, and precisely the blind spot that caused the incident: if the
    machine cannot read origin it CANNOT know its pushes are landing. 'No freeze
    detected' would be the same false comfort the phantom rc=0 gave."""
    run = origin_runner()
    ev = scr.detect_origin_freeze(T0, runner=run, remote_head_fn=lambda: None)
    assert ev is not None and ev.unavailable
    assert "phantom-push blind spot" in ev.detail


def test_origin_freeze_unavailable_when_local_head_unreadable():
    run = origin_runner(rev_parse_rc=1)
    ev = scr.detect_origin_freeze(T0, runner=run, remote_head_fn=lambda: "bbbb222")
    assert ev is not None and ev.unavailable


def test_origin_freeze_unavailable_when_remote_commit_absent_locally():
    """A remote head we cannot resolve locally means the age is UNKNOWN, not zero."""
    run = origin_runner(log_rc=128)
    ev = scr.detect_origin_freeze(T0, runner=run, remote_head_fn=lambda: "bbbb222")
    assert ev is not None and ev.unavailable
    assert "not present locally" in ev.detail


def test_origin_freeze_rejects_a_non_finite_clock():
    """FAIL-OPEN / NaN-blindness: reject non-finite BEFORE any comparison. `nan >= x`
    is False, so an unguarded detector silently passes."""
    for bad in (float("nan"), float("inf"), None):
        ev = scr.detect_origin_freeze(bad, runner=origin_runner(), remote_head_fn=lambda: "b")
        assert ev is not None and ev.unavailable


def test_origin_freeze_ignores_malformed_commit_timestamps():
    def run(*args):
        if args[0] == "rev-parse":
            return 0, "aaaa111\n"
        return 0, "not-a-number\nnan\n"
    assert scr.detect_origin_freeze(T0, runner=run, remote_head_fn=lambda: "bbbb222") is None


def test_origin_freeze_never_reads_the_local_tracking_ref():
    """TAUTOLOGY guard: the remote-tracking ref `origin/main` is the very thing that
    goes stale in a phantom push. A detector that consulted it would be checking the
    phantom against the phantom. Ground truth is `ls-remote` -- as the existing push
    verifier already does."""
    now = T0 + 10 * HOUR
    run = origin_runner(unpushed=[now - 3 * HOUR])
    scr.detect_origin_freeze(now, runner=run, remote_head_fn=lambda: "bbbb222")
    flat = " ".join(" ".join(c) for c in run.calls)  # type: ignore[attr-defined]
    assert "origin/main" not in flat

    # ...and the DEFAULT remote-head reader is ls-remote, not a ref read.
    seen: list[tuple[str, ...]] = []

    def probe(*args):
        seen.append(args)
        return 1, ""

    scr._ls_remote_head(runner=probe)
    assert seen and seen[0][0] == "ls-remote"


def test_origin_freeze_writes_nothing(tmp_path, monkeypatch):
    """G3 + the 'a false positive must not jam the pipeline' trap: the detector
    returns a verdict and touches no state, so it can never wedge publishing."""
    import os

    before = set(os.listdir(scr.PROJECT_DIR / "docs" / "observability"))
    now = T0 + 10 * HOUR
    scr.detect_origin_freeze(
        now, runner=origin_runner(unpushed=[now - 3 * HOUR]), remote_head_fn=lambda: "b"
    )
    scr.detect_progress_gap_stalls(T0, T0 + HOUR, runner=make_runner())
    assert set(os.listdir(scr.PROJECT_DIR / "docs" / "observability")) == before
