"""R15 controls for the run_complete marker sweep
(`background/background_worker.py::process_leftover_run_markers`), atom
OPS_run_marker_sweep_livelock.

THE DEFECT, measured on the live tree 2026-08-03 (observed-with-evidence, R9):
  - `ls docs/staging/run_complete_*.md | wc -l` = 406, spanning 2026-07-29..08-03.
  - docs/observability/background-worker-log.md: 1668 "Lock-skipped", 571
    "Failed to process", 300 "Processed"; 2239 lines ending "will retry next
    cycle".
  - The backlog was GROWING, not draining: "Found 382 leftover" at 2026-08-02
    23:48Z -> "Found 405" at 2026-08-03 04:12Z. sim_runner.py mints a marker
    every ~9 min; one publish costs ~8 min. A per-marker retry loop cannot win.

TWO defects, and the second is the one that hid the first:
  (1) NO PROGRESS. Attempting every marker oldest-first is unbounded work
      against an unbounded arrival rate. Worse, the 300 that DID "succeed"
      were the harmful ones: `process_run_complete._process()` regenerates
      ANNUAL_REPORT.md / LATEST.md / dashboard.json from the MARKER'S OWN
      json_path, so each one republished the live business surfaces from a run
      up to five days stale.
  (2) FAIL-SILENT (R15). A permanent, total, five-day failure was reported in
      the vocabulary of a transient retry -- "will retry next cycle" -- which
      in a log is indistinguishable from a healthy queue draining. Nothing
      measured whether the retrying ever worked.

Every control below is mutation-proven in the atom's report: neuter the drain
-> the DRAIN tests go red; neuter the alarm -> the ALARM tests go red.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from background import background_worker


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(background_worker, "STAGING_DIR", staging)
    monkeypatch.setattr(background_worker, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(background_worker, "SWEEP_STATE_FILE", tmp_path / ".sweep_state.json")
    import background.process_run_complete as prc
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "done")
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "prc_log.md")
    import background.notify as _notify
    monkeypatch.setattr(_notify, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    yield


@pytest.fixture
def sent(monkeypatch):
    """Capture pages at the TRANSPORT, so the real notify() contract layer --
    including its R5 transition-only suppression -- is genuinely exercised
    rather than mocked away."""
    box = []
    import background.ntfy_utils as ntfy_utils
    monkeypatch.setattr(ntfy_utils, "send_ntfy",
                        lambda message, headers=None, **kw: box.append(message) or "id-1")
    return box


def _sweep_pages(sent):
    """Only THIS control's pages. rc=1 is the live failure mode, and it also
    feeds the pre-existing H15 publish-gate wedge detector, which pages on the
    same transport -- a real and correct second alarm about a different thing.
    Filtering keeps these assertions about the sweep's own control rather than
    about H15's thresholds."""
    return [m for m in sent if "RUN-MARKER SWEEP" in m or "Run-marker sweep" in m]


def _mint(name_ts, staging=None):
    staging = staging or background_worker.STAGING_DIR
    p = staging / f"run_complete_{name_ts}.md"
    p.write_text(f"# Simulation Run Complete\n\nGit: abc123\nJSON: /tmp/{name_ts}.json\n")
    return p


def _rc(code):
    return lambda *a, **k: MagicMock(returncode=code)


def _staging_names():
    return sorted(p.name for p in background_worker.STAGING_DIR.glob("run_complete_*.md"))


def _done_names():
    import background.process_run_complete as prc
    return sorted(p.name for p in prc.DONE_DIR.glob("run_complete_*.md"))


# ══════════════════════════════════════════════════════════════════════════════
# HALF 1 — PROGRESS: the sweep must actually drain
# ══════════════════════════════════════════════════════════════════════════════

def test_a_backlog_drains_in_one_pass_even_while_every_publish_is_lock_skipped(monkeypatch):
    """THE livelock test, under the EXACT live condition. Every publish attempt
    returns EXIT_LOCK_SKIPPED (the producer holds the run lock while it
    publishes its own marker inline) -- 1668 of those in the live worker log.
    The old sweep drained nothing at all in that state. The new one must still
    reduce a 50-marker backlog to 1 in a single pass, because draining does not
    depend on the publish succeeding."""
    for i in range(50):
        _mint(f"2026080{1}T{i:02d}0000Z")
    monkeypatch.setattr(background_worker.subprocess, "run",
                        _rc(background_worker.EXIT_LOCK_SKIPPED))

    background_worker.process_leftover_run_markers()

    assert len(_staging_names()) == 1, (
        "a lock-skipped publish must not stop the backlog draining -- "
        "still in staging: {}".format(_staging_names()))
    assert len(_done_names()) == 49


def test_the_backlog_stays_bounded_across_cycles_while_markers_keep_arriving(monkeypatch):
    """The livelock invariant, not a one-shot: sim_runner mints a new marker
    every cycle and every publish is lock-skipped forever. The staging root
    must NEVER accumulate -- which is precisely what 406 markers over five days
    disproved for the old sweep."""
    monkeypatch.setattr(background_worker.subprocess, "run",
                        _rc(background_worker.EXIT_LOCK_SKIPPED))
    peak = 0
    for cycle in range(12):
        _mint(f"20260802T{cycle:02d}0000Z")          # a fresh marker each cycle
        background_worker.process_leftover_run_markers()
        peak = max(peak, len(_staging_names()))
    assert peak <= 1, "backlog grew to {} -- the livelock is back".format(peak)


def test_superseded_markers_are_archived_with_a_reason_never_deleted():
    """R10 WALL: closure by deleting the backlog is forbidden. Each superseded
    marker must survive in done/ carrying its ORIGINAL content plus an explicit
    superseded-by record."""
    old = _mint("20260801T010000Z")
    old_text = old.read_text()
    new = _mint("20260801T020000Z")
    import background.process_run_complete as prc

    archived = prc.supersede_run_markers([old], new, log_fn=lambda m: None)

    assert archived == [old.name]
    assert not old.exists()
    landed = prc.DONE_DIR / old.name
    assert landed.exists(), "a superseded marker must be ARCHIVED, never deleted"
    text = landed.read_text()
    assert text.startswith(old_text), "the original marker content must survive intact"
    assert prc.SUPERSEDED_BLOCK_HEADER in text
    assert "Superseded-by: {}".format(new.name) in text
    assert "Superseded-at:" in text
    assert "Reason:" in text and "STALE" in text


def test_a_marker_that_cannot_be_archived_is_left_in_staging(monkeypatch):
    """FAIL-CLOSED: if the archive cannot be CONFIRMED (nothing landed in
    done/), the marker stays in staging and is reported as not archived. A
    supersede that quietly loses a marker would be the deletion this atom's
    R10 wall forbids."""
    old = _mint("20260801T030000Z")
    new = _mint("20260801T040000Z")
    import background.process_run_complete as prc
    monkeypatch.setattr(prc, "_archive_marker", lambda m: False)

    archived = prc.supersede_run_markers([old], new, log_fn=lambda m: None)

    assert archived == []
    assert old.exists(), "an unconfirmed archive must leave the marker in place"


def test_an_unparseable_marker_name_is_never_superseded(monkeypatch):
    """FAIL-CLOSED on malformed input: supersession is only sound because the
    fixed-width `run_complete_YYYYMMDDTHHMMSSZ.md` name sorts chronologically.
    A name that does not match is NOT provably older than anything, so it must
    get its own publish attempt rather than a silent archive."""
    odd = background_worker.STAGING_DIR / "run_complete_manual_rerun.md"
    odd.write_text("# Simulation Run Complete\n")
    newest = _mint("20260801T050000Z")
    _mint("20260801T040000Z")

    attempted = []
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: attempted.append(Path(a[0][-1]).name) or MagicMock(returncode=0))

    background_worker.process_leftover_run_markers()

    assert odd.name in attempted, "an unrecognised marker must never be silently archived"
    assert newest.name in attempted
    assert odd.name not in _done_names()


def test_a_lone_marker_is_published_and_nothing_is_superseded(monkeypatch):
    """Both ways (R15): the drain must not fire when there is nothing to
    supersede. One marker = one publish attempt, zero archives -- otherwise
    the sweep would archive the very run it is supposed to publish."""
    only = _mint("20260801T060000Z")
    attempted = []
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: attempted.append(Path(a[0][-1]).name) or MagicMock(returncode=0))

    background_worker.process_leftover_run_markers()

    assert attempted == [only.name]
    assert _done_names() == []


def test_the_newest_marker_is_the_one_published(monkeypatch):
    """Publishing an OLDER marker is not merely wasted work: _process()
    regenerates the business surfaces from that marker's own json_path, so it
    overwrites the live figures with stale ones. 300 such republishes were
    logged as successes over five days."""
    for ts in ("20260801T070000Z", "20260801T090000Z", "20260801T080000Z"):
        _mint(ts)
    attempted = []
    monkeypatch.setattr(background_worker.subprocess, "run",
                        lambda *a, **k: attempted.append(Path(a[0][-1]).name) or MagicMock(returncode=0))

    background_worker.process_leftover_run_markers()

    assert attempted == ["run_complete_20260801T090000Z.md"]


def test_superseded_markers_do_not_feed_the_publish_gate_detector(monkeypatch):
    """A superseded-archive is NOT a publish -- it is evidence of nothing about
    the publish gate's health, exactly as a lock-skip is (the fail-open closed
    2026-07-29). Recording 405 archives as successes would re-arm and
    auto-resolve the H15 wedge alarm for runs nobody published."""
    for ts in ("20260801T100000Z", "20260801T110000Z", "20260801T120000Z"):
        _mint(ts)
    monkeypatch.setattr(background_worker.subprocess, "run", _rc(0))
    import background.process_run_complete as prc
    outcomes = []
    monkeypatch.setattr(prc, "record_publish_gate_success", lambda *a, **k: outcomes.append("success"))
    monkeypatch.setattr(prc, "record_publish_gate_failure", lambda *a, **k: outcomes.append("failure") or {"fired": False})

    background_worker.process_leftover_run_markers()

    assert outcomes == ["success"], (
        "exactly ONE publish happened, so exactly one outcome may be recorded; got {}".format(outcomes))


# ══════════════════════════════════════════════════════════════════════════════
# HALF 2 — R15 FAIL-SILENT: a retry loop that never succeeds must ALARM
# ══════════════════════════════════════════════════════════════════════════════

def _stuck_cycles(monkeypatch, n, rc=1):
    """Run n sweeps in which the single marker never leaves staging -- the live
    '571 x Failed to process ... will retry next cycle' condition."""
    monkeypatch.setattr(background_worker.subprocess, "run", _rc(rc))
    for _ in range(n):
        background_worker.process_leftover_run_markers()


def test_below_threshold_a_dead_retry_loop_does_not_page(monkeypatch, sent):
    """Both ways: transient contention must NOT page. Two dead cycles is
    ordinary lock contention, not a wedge."""
    _mint("20260802T010000Z")
    _stuck_cycles(monkeypatch, background_worker.ZERO_PROGRESS_ALARM_CYCLES - 1)
    assert _sweep_pages(sent) == []


def test_a_retry_loop_that_never_succeeds_raises_an_alarm(monkeypatch, sent):
    """THE control this atom exists for. N consecutive sweeps that drain ZERO
    markers while a backlog exists is a permanent failure, and must page --
    not log another 'will retry next cycle'."""
    _mint("20260802T020000Z")
    _stuck_cycles(monkeypatch, background_worker.ZERO_PROGRESS_ALARM_CYCLES)

    pages = _sweep_pages(sent)
    assert len(pages) == 1, "a never-succeeding retry loop must alarm exactly once"
    msg = pages[0]
    # R5: the page carries the diagnostic payload, not just a status word.
    assert "STUCK" in msg
    assert str(background_worker.ZERO_PROGRESS_ALARM_CYCLES) in msg
    assert "run_complete_20260802T020000Z.md" in msg, "the oldest marker must be named"
    assert "background-worker-log.md" in msg, "the page must say where to look"


def test_an_unchanged_stuck_status_does_not_repage(monkeypatch, sent):
    """R5: transition-only. Ten more dead cycles must not add ten more pages --
    that would just be 'will retry next cycle' on the director's phone."""
    _mint("20260802T030000Z")
    _stuck_cycles(monkeypatch, background_worker.ZERO_PROGRESS_ALARM_CYCLES + 10)
    assert len(_sweep_pages(sent)) == 1


def test_recovery_clears_the_alarm_and_is_itself_a_transition(monkeypatch, sent):
    """R11 no-orphan-transition: the alarm's RELEASE must have a defined,
    tested effect. It clears the armed state AND sends one recovery line."""
    _mint("20260802T040000Z")
    _stuck_cycles(monkeypatch, background_worker.ZERO_PROGRESS_ALARM_CYCLES)
    assert len(_sweep_pages(sent)) == 1

    # Now a real drain happens: a newer marker supersedes the stuck one.
    _mint("20260802T050000Z")
    monkeypatch.setattr(background_worker.subprocess, "run",
                        _rc(background_worker.EXIT_LOCK_SKIPPED))
    background_worker.process_leftover_run_markers()

    pages = _sweep_pages(sent)
    assert len(pages) == 2 and "RECOVERED" in pages[1]
    state = json.loads(background_worker.SWEEP_STATE_FILE.read_text())
    assert state["zero_progress_cycles"] == 0
    assert state["alarmed"] is False


def test_progress_is_measured_independently_of_the_publishers_own_verdict(monkeypatch, sent):
    """ANTI-TAUTOLOGY (R15 killer #1). The thing that lied was the sweep's own
    reporting, so the alarm may not be built on it. Here the publisher claims
    rc==0 ('Processed') every single cycle while the marker never actually
    leaves staging. A control that trusted the return code would see a
    perfectly healthy queue forever; the filesystem re-observation sees zero
    markers drained and pages."""
    _mint("20260802T060000Z")
    _stuck_cycles(monkeypatch, background_worker.ZERO_PROGRESS_ALARM_CYCLES, rc=0)
    pages = _sweep_pages(sent)
    assert len(pages) == 1 and "STUCK" in pages[0]


def test_an_empty_staging_dir_is_not_a_stuck_retry_loop(monkeypatch, sent):
    """FAIL-OPEN killer #2, the other direction: nothing to do is not
    zero-progress. A quiet machine must never page, or the alarm gets muted."""
    monkeypatch.setattr(background_worker.subprocess, "run", _rc(0))
    for _ in range(background_worker.ZERO_PROGRESS_ALARM_CYCLES + 5):
        background_worker.process_leftover_run_markers()
    assert _sweep_pages(sent) == []
    state = json.loads(background_worker.SWEEP_STATE_FILE.read_text())
    assert state["zero_progress_cycles"] == 0


@pytest.mark.parametrize("corrupt", ["", "not json", "{}", '{"zero_progress_cycles": null}',
                                     '{"zero_progress_cycles": "lots"}', '[]'])
def test_a_missing_or_corrupt_state_file_does_not_read_as_healthy(monkeypatch, sent, corrupt):
    """FAIL-OPEN killer: a control that passes on missing/empty/malformed input
    is not a control. Whatever garbage the state file holds, the counter must
    restart from zero and still reach the alarm -- never silently 'already
    fine'."""
    background_worker.SWEEP_STATE_FILE.write_text(corrupt)
    _mint("20260802T070000Z")
    _stuck_cycles(monkeypatch, background_worker.ZERO_PROGRESS_ALARM_CYCLES)
    assert len(_sweep_pages(sent)) == 1


def test_an_undeliverable_alarm_is_not_recorded_as_fired(monkeypatch):
    """FAIL-SILENT killer (R15 #3): an unavailable checker is a FAILED check.
    If the page cannot be delivered, the sweep must NOT mark itself alarmed and
    must NOT reset the counter -- otherwise a stuck sweep plus a dead notify
    channel equals total silence, which is the original defect wearing a
    different hat."""
    import background.ntfy_utils as ntfy_utils
    monkeypatch.setattr(ntfy_utils, "send_ntfy",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("ntfy down")))
    _mint("20260802T080000Z")
    _stuck_cycles(monkeypatch, background_worker.ZERO_PROGRESS_ALARM_CYCLES)

    state = json.loads(background_worker.SWEEP_STATE_FILE.read_text())
    assert state["alarmed"] is False, "an undelivered alarm has not fired"
    assert state["zero_progress_cycles"] >= background_worker.ZERO_PROGRESS_ALARM_CYCLES
    assert "alarm_delivery_failed_at" in state
    assert "COULD NOT BE DELIVERED" in background_worker.LOG_FILE.read_text()


def test_an_undeliverable_alarm_still_pages_once_the_channel_returns(monkeypatch, sent):
    """Both ways for the fail-silent guard: because the failed delivery was not
    recorded as fired, the very next cycle must try again and succeed."""
    import background.ntfy_utils as ntfy_utils
    monkeypatch.setattr(ntfy_utils, "send_ntfy",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("ntfy down")))
    _mint("20260802T090000Z")
    _stuck_cycles(monkeypatch, background_worker.ZERO_PROGRESS_ALARM_CYCLES)

    monkeypatch.setattr(ntfy_utils, "send_ntfy",
                        lambda message, headers=None, **kw: sent.append(message) or "id-2")
    _stuck_cycles(monkeypatch, 1)

    pages = _sweep_pages(sent)
    assert len(pages) == 1 and "STUCK" in pages[0]


def test_a_notify_outage_never_breaks_the_sweep(monkeypatch):
    """A monitoring failure must never break the pipeline it monitors -- the
    same guarantee _record_publish_gate_outcome already carries."""
    import background.ntfy_utils as ntfy_utils
    monkeypatch.setattr(ntfy_utils, "send_ntfy",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    for ts in ("20260802T100000Z", "20260802T110000Z"):
        _mint(ts)
    _stuck_cycles(monkeypatch, background_worker.ZERO_PROGRESS_ALARM_CYCLES + 1)
    # No exception escaped, and the drain still happened.
    assert len(_done_names()) == 1


def test_the_alarm_uses_the_one_notification_contract():
    """OPERATIONAL_COHERENCE / no accretion: the page must go through
    background.notify (kind + transition-only dedup already owned there), not a
    hand-rolled send_ntfy with its own _last_ts. tests/background/
    test_notify_contract.py enforces this globally with a SHRINKING allowlist;
    this pins it for the sweep specifically."""
    src = Path(background_worker.__file__).read_text()
    assert "from background.notify import notify" in src
    assert "send_ntfy" not in src, (
        "the sweep must page via notify(), not the low-level transport")


def test_a_superseding_drain_counts_as_progress(monkeypatch, sent):
    """Both ways: the alarm must stay quiet while the sweep IS draining. Twenty
    cycles, a new marker each time, publishes always lock-skipped -- the
    backlog never grows and nothing pages."""
    monkeypatch.setattr(background_worker.subprocess, "run",
                        _rc(background_worker.EXIT_LOCK_SKIPPED))
    for cycle in range(20):
        _mint(f"20260803T{cycle:02d}0000Z")
        background_worker.process_leftover_run_markers()
    assert _sweep_pages(sent) == [], "a draining sweep must not page"


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (the marker sweep's lifecycle + its own alarm),
# never a published business surface -- so it must never wedge the live publish.
# The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
pytestmark = pytest.mark.operational
