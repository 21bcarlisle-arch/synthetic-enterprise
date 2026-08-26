"""RUNG-1d PRODUCER STARVATION draw -- R15 both-ways proof (2026-08-17).

THE INCIDENT. Between 15:59Z and 17:17Z on 2026-08-17 the simulation runner failed
NINE consecutive times, every one of them `KeyError: 'net_margin_gbp'` at ~215s, and
the tick worked three other lanes throughout. Nothing was hidden: nine ntfys reached
the director's phone, nine tracebacks reached sim-runner-log.md, and `agent_status`
carried the anomaly the whole time. What did not exist was a DRAW -- the failure was
narrated to a human and to no mechanism, which is the consumed-not-absorbed class
R17/MAKE_IT_STICK forbids and the exact reason RUNG 1 was built for the publisher.

WHY THE EXISTING RUNGS COULD NOT SEE IT. Both blindnesses are structural, not
oversights, and both are pinned as tests below:
  * RUNG 1 (publish-gate wedge) keys on publish FAILURES. A run that dies never
    attempts a publish, so nine failed runs produced ZERO entries and `failures`
    stayed EMPTY -- indistinguishable from a healthy gate. Fail-open on empty.
  * RUNG 1b (operational-layer red) keys on `pytest -m operational`, the daemon-
    lifecycle/IaC suite. The daemon was ALIVE, so the signal read GREEN
    (consecutive_green=6, 16:54Z, with eight failures already behind it). It
    measures LIVENESS; the broken thing was the OUTPUT.
  * (Third watcher, not a rung: the content-freshness clocks key on commit/publish
    recency by ANY writer, and a concurrent SITE lane kept publishing -- so
    `published_age_seconds` read 1.9h against a real producer outage of 3.0h.)

R15 requires a control that can FAIL. These prove it both ways:
  * MUST FIRE: the recorded 2026-08-17 state (9 failures, 78 min, no newer artefact)
    -> a draw, returned by `_self_refill_draw` ABOVE the product lanes, and
    `_is_drained_and_gated` refuses rest. And the runner-is-DEAD case, where there is
    no counter at all and only the artefact age can speak.
  * MUST STAY SILENT: a healthy producer, a lone flake, a young streak, a director
    HOLD, an absent/malformed state file, and -- the anti-tautology limb -- a stale
    failure counter that a later successful run has superseded.
"""
import json
from pathlib import Path

import pytest

from background import supervisor as sv

HOUR = 3600.0
NOW = 1_786_000_000.0

#: The failure detail as `child_diagnostics.failure_detail` rendered it that day.
REAL_DETAIL = "KeyError: 'net_margin_gbp'"

#: Every OTHER rung `_is_drained_and_gated` consults, silenced so the producer rung is
#: the only thing that can refuse rest. Listed rather than derived: if a new rung is
#: added and not listed here, the isolation control below stops returning True and says
#: so, which is the right way for this list to go stale.
_EVERY_OTHER_REST_RUNG = (
    "_publish_gate_wedge_active",
    "_operational_red_persistent_draw",
    "_maturity_map_draw_concurrent",
    "_site_lane_draw_concurrent",
    "_idle_discover_frame_draw_concurrent",
    "_actionable_backlog_item",
    "_open_campaign_draw",
    "_declared_defect_backlog_draw",
    "_stale_gap_row_draw",
    "_propose_half_draw",
    "_forward_discovery_draw",
    "_planner_rung_draw",
    "_blocked_mints_open",
)


def _state(**overrides) -> dict:
    """The producer state as sim_runner would have written it at 17:17Z on
    2026-08-17: nine consecutive failures, the streak beginning at 15:59Z."""
    base = {
        "last_result": "failed",
        "consecutive_failures": 9,
        "first_failure_ts": NOW - 78 * 60,
        "last_failure_ts": NOW - 60,
        "last_success_ts": NOW - 3 * HOUR,
        "detail": REAL_DETAIL,
        "git": "4b36dc08a",
        "elapsed_s": 215,
    }
    base.update(overrides)
    return base


def _silence_the_live_log(monkeypatch):
    """`supervisor.log` appends to the REAL docs/observability/supervisor-log.md, and it is
    not injectable -- so any test that drives `_self_refill_draw` writes its synthetic verdict
    into the operational log an on-call reads. This test wrote ten "PRODUCER STARVATION (RUNG
    1d, PRIORITY ZERO): the simulation producer is down" lines into the live log while the
    producer was healthy, and they were briefly mistaken for a real false positive on the rung
    they describe -- which is the cost: a test's output that is indistinguishable from an
    incident. Same class as the conftest path sweep, but on a FUNCTION rather than a Path, so
    the sweep does not reach it.
    """
    monkeypatch.setattr(sv, "log", lambda *a, **k: None)


@pytest.fixture
def env(tmp_path):
    """A state file, a reports dir and a hold-flag path, none of which touch the
    real tree. `artefact(age)` stamps a run output at a chosen age."""
    state_path = tmp_path / ".sim_producer_state.json"
    reports = tmp_path / "reports"
    reports.mkdir()
    hold = tmp_path / ".sim_runner_hold"

    class Env:
        def write(self, state: dict | None):
            if state is not None:
                state_path.write_text(json.dumps(state))

        def artefact(self, age_seconds: float, name="run_output_abc_20260817T150000Z.json"):
            p = reports / name
            p.write_text("{}")
            import os
            os.utime(p, (NOW - age_seconds, NOW - age_seconds))
            return p

        def detect(self, now=NOW):
            return sv._producer_starved_active(
                now=now, state_path=state_path, reports_dir=reports, hold_flag=hold,
            )

        def hold_it(self):
            hold.write_text("director hold")

    return Env()


# ---------------------------------------------------------------------------
# MUST FIRE
# ---------------------------------------------------------------------------

class TestItFiresOnTheRealOutage:

    def test_the_recorded_2026_08_17_state_draws(self, env):
        env.write(_state())
        env.artefact(3 * HOUR)          # last success was 3h ago, before the streak
        draw = env.detect()
        assert draw, "the nine-failure outage did not produce a draw"
        assert "PRIORITY ZERO" in draw
        assert "9 consecutive" in draw

    def test_the_draw_carries_the_diagnostic_not_just_the_count(self, env):
        """R9: a draw that says 'the producer is down' without saying what it died
        of sends the next turn to re-derive what the runner already captured."""
        env.write(_state())
        env.artefact(3 * HOUR)
        draw = env.detect()
        assert REAL_DETAIL in draw
        assert "sim-runner-log.md" in draw, "the full traceback's location is not named"

    def test_a_dead_runner_that_wrote_no_counter_still_draws(self, env):
        """The failure mode a state-file-only detector is BLIND to, by construction:
        the runner is dead/wedged/never-started, so there is no counter to read. Only
        the artefact age can speak, and it must.

        This used to assert the draw said "not a run failing" -- i.e. that silence PROVED
        the runs were absent. It does not, and on 2026-08-24 it was wrong for four hours
        while every run was being OOM-killed mid-flight (`background/oom_watch.py`,
        `test_oom_watch.py`). What the draw owes the reader is that it fired and that the
        question is OPEN, so what is asserted here now is the firing, not the wrong half of
        a disjunction the two inputs cannot decide between."""
        env.artefact(4 * HOUR)          # no state file written at all
        draw = env.detect()
        assert draw, "a silent dead producer drew nothing"
        assert "PRODUCER SILENT" in draw
        assert "is not decided by either input above" in draw

    def test_self_refill_returns_it_above_the_product_lanes(self, env, monkeypatch):
        env.write(_state())
        env.artefact(3 * HOUR)
        drawn = env.detect()
        _silence_the_live_log(monkeypatch)
        monkeypatch.setattr(sv, "_publish_gate_wedge_active", lambda *a, **k: None)
        monkeypatch.setattr(sv, "_operational_red_persistent_draw", lambda *a, **k: None)
        monkeypatch.setattr(sv, "_producer_starved_active", lambda *a, **k: drawn)

        def _no_product_lane_should_be_reached(*a, **k):
            raise AssertionError(
                "the draw reached the product lanes with the producer down -- rung 1d "
                "is not above them"
            )

        monkeypatch.setattr(sv, "_maturity_map_draw_concurrent", _no_product_lane_should_be_reached)
        assert sv._self_refill_draw() == drawn

    def test_rest_is_refused_while_the_producer_is_down(self, env, monkeypatch):
        """The mirror. Without it, `_is_drained_and_gated` green-lights rest beside a
        pipeline producing nothing -- which is what 'the three lanes are empty' looked
        like for 70 minutes.

        EVERY OTHER RUNG IS SILENCED FIRST, on purpose. Written the obvious way (patch
        the producer rung, assert False) this test PASSED with the mirror deleted,
        because the real lanes had work and something further down returned False
        anyway -- a control passing for a reason unrelated to what it claims to check.
        With the rest of the ladder drained, the producer rung is the ONLY thing that
        can refuse rest, so deleting the mirror makes this fail."""
        env.write(_state())
        env.artefact(3 * HOUR)
        drawn = env.detect()
        _silence_the_live_log(monkeypatch)
        for name in _EVERY_OTHER_REST_RUNG:
            monkeypatch.setattr(sv, name, lambda *a, **k: None)
        monkeypatch.setattr(sv, "_blocking_lane_draw", lambda *a, **k: (None, frozenset()))
        monkeypatch.setattr(sv, "_producer_starved_active", lambda *a, **k: drawn)
        assert sv._is_drained_and_gated() is False

    def test_the_isolation_above_is_real_and_not_a_rigged_ladder(self, env, monkeypatch):
        """CONTROL ON THE CONTROL: the SAME drained ladder with a HEALTHY producer must
        reach a rest verdict of True. Without this, the test above would pass on a
        ladder rigged to refuse rest no matter what, and would prove nothing about the
        producer rung."""
        _silence_the_live_log(monkeypatch)
        for name in _EVERY_OTHER_REST_RUNG:
            monkeypatch.setattr(sv, name, lambda *a, **k: None)
        monkeypatch.setattr(sv, "_blocking_lane_draw", lambda *a, **k: (None, frozenset()))
        monkeypatch.setattr(sv, "_producer_starved_active", lambda *a, **k: None)
        # The final line of `_is_drained_and_gated` is `_rule0_harden_draw() is not None`
        # -- drained, with only the RULE-0 treadmill left, is the True case.
        monkeypatch.setattr(sv, "_rule0_harden_draw", lambda *a, **k: {"id": "HARDEN"})
        assert sv._is_drained_and_gated() is True


# ---------------------------------------------------------------------------
# MUST STAY SILENT
# ---------------------------------------------------------------------------

class TestItStaysSilentWhenItShould:

    def test_a_healthy_producer_draws_nothing(self, env):
        env.write({"last_result": "ok", "consecutive_failures": 0,
                   "first_failure_ts": None, "last_success_ts": NOW - 300})
        env.artefact(300)
        assert env.detect() is None

    def test_a_lone_flake_is_not_an_outage(self, env):
        """One failure, with the previous run's output still recent. Note the artefact
        must be recent for this to BE a lone flake -- a single recorded failure with no
        output for three hours is not a flake, it is an outage the runner stopped
        counting, and limb 2 fires on it (pinned in
        `test_a_single_failure_with_no_output_for_hours_is_still_starvation`)."""
        env.write(_state(consecutive_failures=1, first_failure_ts=NOW - 600,
                         last_failure_ts=NOW - 600))
        env.artefact(700)
        assert env.detect() is None

    def test_a_single_failure_with_no_output_for_hours_is_still_starvation(self, env):
        """The complement, and the reason limb 2 is not redundant with limb 1: the
        counter says 'one failure' and the filesystem says 'nothing for three hours'.
        The filesystem is the one that cannot be wrong about whether output happened."""
        env.write(_state(consecutive_failures=1, first_failure_ts=NOW - 600,
                         last_failure_ts=NOW - 600))
        env.artefact(4 * HOUR)
        draw = env.detect()
        assert draw and "PRODUCER SILENT" in draw

    def test_a_young_streak_is_not_yet_drawable(self, env):
        """Sustained, not immediate: three failures inside five minutes is a bad run,
        not a 70-minute outage."""
        env.write(_state(consecutive_failures=3, first_failure_ts=NOW - 300))
        env.artefact(400)
        assert env.detect() is None

    def test_a_director_hold_is_not_starvation(self, env):
        """A control that fires for as long as a deliberate hold stands is a phantom
        every tick, and a phantom that cannot drain gets deleted."""
        env.write(_state())
        env.artefact(6 * HOUR)          # both limbs would otherwise fire
        env.hold_it()
        assert env.detect() is None

    def test_an_absent_state_file_with_fresh_artefacts_draws_nothing(self, env):
        env.artefact(200)
        assert env.detect() is None

    def test_a_malformed_state_file_does_not_raise_into_the_draw_ladder(self, env):
        (Path(env.artefact(200)).parent.parent / ".sim_producer_state.json").write_text("{not json")
        assert env.detect() is None

    def test_an_empty_reports_dir_and_no_state_is_silent(self, env):
        """A fresh tree has produced nothing and has starved nothing. FAIL-SAFE: no
        phantom draw where there is no evidence either way."""
        assert env.detect() is None


class TestTheIndependenceLimb:
    """ANTI-TAUTOLOGY (R15): the streak comes from the runner's own bookkeeping, so
    the rung must not rest on that alone. A run ARTEFACT -- written by the child
    process, not by the runner -- is the independent cross-check."""

    def test_a_later_successful_run_supersedes_a_stale_counter(self, env):
        env.write(_state())             # says 9 failures, newest at NOW-60
        env.artefact(30)                # ...but a run output landed 30s ago
        assert env.detect() is None, (
            "the rung trusted its own counter over an artefact that proves a run "
            "has since succeeded -- it would keep drawing already-fixed work"
        )

    def test_an_artefact_older_than_the_failures_does_not_supersede_them(self, env):
        env.write(_state())
        env.artefact(3 * HOUR)
        assert env.detect(), "an artefact PREDATING the streak was treated as a pass"

    def test_the_artefact_age_helper_reads_the_newest_not_the_first(self, env):
        env.artefact(5 * HOUR, name="run_output_old_20260817T100000Z.json")
        env.artefact(600, name="run_output_new_20260817T170000Z.json")
        age = sv._newest_run_artefact_age_seconds(
            now=NOW, reports_dir=Path(env.artefact(600).parent),
        )
        assert age == pytest.approx(600, abs=5)


class TestTheBlindnessesThisRungExistsToCover:
    """These pin WHY rungs 1 and 1b were silent. If a future change makes either of
    them able to see a producer outage, these fail and rung 1d can be reconsidered --
    which is the point: the justification is testable, not asserted."""

    def test_rung_1_is_silent_on_an_empty_failure_list(self, tmp_path):
        """Nine dead runs attempt ZERO publishes, so the publish gate records nothing.
        An empty `failures` list is indistinguishable from a healthy gate."""
        state = tmp_path / ".publish_gate_state.json"
        state.write_text(json.dumps({"failures": []}))
        last_tested = tmp_path / ".last_tested_hash"
        last_tested.write_text("4b36dc08a")
        assert sv._publish_gate_wedge_active(
            now=NOW, head="4b36dc08a", state_path=state, last_tested_path=last_tested,
        ) is None

    def test_rung_1b_is_silent_while_the_daemon_is_merely_ALIVE(self, tmp_path):
        """The signal recorded at 16:54Z, with eight failures already behind it."""
        signal = tmp_path / ".operational_layer_signal.json"
        signal.write_text(json.dumps({
            "consecutive_green": 6, "consecutive_red": 0,
            "last_result": "green", "last_run_ts": NOW - 1800,
        }))
        assert sv._operational_red_persistent_draw(now=NOW, state_path=signal) is None


class TestTheRunnerSideBookkeeping:
    """The write half of the contract. A detector reading a counter nobody maintains
    correctly is the same fail-silent shape one level down."""

    def test_a_failure_starts_and_grows_the_streak(self, tmp_path):
        from background import sim_runner

        p = tmp_path / "state.json"
        first = sim_runner.record_run_outcome(False, detail="boom", state_path=p, now=NOW)
        assert first["consecutive_failures"] == 1
        second = sim_runner.record_run_outcome(False, detail="boom", state_path=p, now=NOW + 500)
        assert second["consecutive_failures"] == 2

    def test_the_streak_start_is_not_restamped_by_later_failures(self, tmp_path):
        """The defect that would make this whole rung unreachable: if every failure
        re-stamped `first_failure_ts`, the measured outage would never exceed one run
        cycle and the age threshold would never be crossed.

        NOTE ON WHAT THIS NOW PINS. Before the episode guard was wired, breaking the
        writer's own `first = previous.get(...) if streak else None` line failed this
        test. It no longer does: `guard_episode` is low-water on that field and absorbs
        the mutation. That is the guard doing its job -- two independent things now have
        to fail before an outage can shorten -- but it means this test pins the OBSERVABLE
        property and not that one line. The guard itself is pinned separately by
        `TestTheEpisodeGuardOnTheProducerState`."""
        from background import sim_runner

        p = tmp_path / "state.json"
        sim_runner.record_run_outcome(False, detail="boom", state_path=p, now=NOW)
        for i in range(1, 9):
            state = sim_runner.record_run_outcome(
                False, detail="boom", state_path=p, now=NOW + i * 520,
            )
        assert state["first_failure_ts"] == NOW, "the streak start moved with the streak"
        assert state["consecutive_failures"] == 9

    def test_a_success_clears_the_streak_so_the_rung_drains_itself(self, tmp_path):
        from background import sim_runner

        p = tmp_path / "state.json"
        sim_runner.record_run_outcome(False, detail="boom", state_path=p, now=NOW)
        sim_runner.record_run_outcome(False, detail="boom", state_path=p, now=NOW + 500)
        cleared = sim_runner.record_run_outcome(True, state_path=p, now=NOW + 1000)
        assert cleared["consecutive_failures"] == 0
        assert cleared["first_failure_ts"] is None
        assert cleared["last_result"] == "ok"

    def test_a_write_failure_is_never_fatal_to_the_runner(self, tmp_path, monkeypatch):
        """The runner's job is to run the simulation. Losing a counter is bad; dying
        because the counter could not be written is worse.

        `log` is patched because it is NOT injectable: it writes to the module-level
        real `sim-runner-log.md`, so an unpatched run of this test appends fake
        'producer-health state write failed' lines to the operational log an on-call
        reads during an outage. Caught by doing exactly that, three times."""
        from background import sim_runner

        monkeypatch.setattr(sim_runner, "log", lambda msg: None)
        unwritable = tmp_path / "nope" / "deeper"
        unwritable.mkdir(parents=True)
        unwritable.chmod(0o500)
        try:
            assert sim_runner.record_run_outcome(
                False, detail="boom", state_path=unwritable / "state.json",
            ) is None
        finally:
            unwritable.chmod(0o700)

    def test_every_terminal_path_in_the_runner_records_an_outcome(self):
        """R15 census, not a spot-check: the mechanism fails silently if ANY terminal
        path forgets to write. Counts the call sites against the four terminal
        outcomes -- timeout, non-zero exit, success, and an exception inside
        run_simulation (the one that skips the other three)."""
        import ast

        src = Path("background/sim_runner.py").read_text()
        calls = [
            n for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.Call)
            and getattr(n.func, "id", None) == "record_run_outcome"
        ]
        assert len(calls) == 4, (
            f"expected 4 terminal outcome recordings, found {len(calls)} -- a terminal "
            "path that does not record leaves the rung blind to exactly the outage it "
            "is meant to catch"
        )


class TestTheUndiagnosedLimbIsSizedAgainstRealCADENCE:
    """A PRIORITY-ZERO rung that fires on normal operation gets a kill flag, not a fix.

    The first draft used 45 minutes on the reasoning "a run cycle is ~6 min, so that is
    seven lost cycles". It sized against the RUN and the real cycle is run + PUBLISH.
    Measured over the 2,977 inter-completion gaps in the runner's own log: p50 9 min,
    p90 20, p95 32, p99 67 -- so 45 min would have fired on 2.79% of gaps, roughly 31
    phantom priority-zero draws a week on a healthy pipeline."""

    def test_the_threshold_clears_the_measured_p99_cadence(self):
        P99_GAP_MINUTES = 67          # measured 2026-08-17 over 2,977 gaps
        assert sv.PRODUCER_ARTEFACT_STALE_SECONDS > P99_GAP_MINUTES * 60 * 2, (
            "the undiagnosed limb fires inside normal operating cadence -- at this bar it "
            "draws priority-zero on healthy publish cycles, and a rung that cannot drain "
            "gets disabled rather than trusted"
        )

    def test_it_is_the_projects_existing_staleness_clock_not_a_new_number(self):
        """Both ends of the pipeline should agree on when the site has gone stale --
        that is the consequence this rung and `publish_freshness` both exist to prevent."""
        from background import publish_freshness

        assert sv.PRODUCER_ARTEFACT_STALE_SECONDS == publish_freshness.STALE_AFTER_SECONDS

    def test_a_normal_slow_publish_cycle_does_not_draw(self, env):
        """The concrete false positive the first threshold would have produced: a healthy
        run whose publish step ran long, with no failures recorded at all."""
        env.artefact(50 * 60)         # 50 min since the last run output, nothing failing
        assert env.detect() is None

    def test_a_genuine_multi_hour_silence_still_draws(self, env):
        """...and the backstop must still work. Today's real outage was 3.0h."""
        env.artefact(4 * HOUR)
        draw = env.detect()
        assert draw and "PRODUCER SILENT" in draw


class TestTheEpisodeGuardOnTheProducerState:
    """PW2 self-clearing-alarm census: this file carries an episode START and an episode
    COUNTER that a PRIORITY-ZERO rung reads for severity, so a write that has not shown
    the episode ended must not be able to shorten it. It landed RED on that census the
    day it was written -- the census working as intended, not a surprise.

    WHAT THE GUARD ACTUALLY BUYS, stated honestly rather than sold: the sequential
    single-writer path was ALREADY correct without it (`record_run_outcome` preserves the
    streak start while a streak is open), and a truly unreadable prior gives the guard
    nothing to compare against, so it cannot help there either. What it adds is defence in
    depth against the cases that path cannot cover -- an out-of-order or concurrent write
    landing a lower streak or a later start, and any future refactor of the writer's own
    arithmetic. Verified: with the guard wired, breaking the writer's streak-start line no
    longer changes behaviour, where before it did."""

    def test_a_failure_write_that_lost_its_prior_cannot_shorten_the_outage(self, tmp_path):
        """THE DEFECT THE GUARD EXISTS FOR, and the 2026-08-09 shape: a 10h26m publish
        outage paged as a fresh 14 minutes. Here a failure write arrives with no readable
        prior state -- concurrent writer, truncated read, hand edit -- and must NOT reset
        the streak to 1 or re-stamp the start at now, because doing so drops the rung
        back below its own 30-minute / 3-failure bars mid-outage."""
        from background import episode_monotonic, sim_runner

        open_episode = {
            "last_result": "failed",
            "consecutive_failures": 9,
            "first_failure_ts": NOW - 78 * 60,
        }
        # What an un-guarded writer would propose after losing the prior.
        naive = {"last_result": "failed", "consecutive_failures": 1, "first_failure_ts": NOW}
        guarded = episode_monotonic.guard_episode(
            open_episode, naive,
            since_fields=sim_runner.PRODUCER_SINCE_FIELDS,
            streak_fields=sim_runner.PRODUCER_STREAK_FIELDS,
            episode_closed=False,
        )
        assert guarded["consecutive_failures"] == 9, "the open streak was reset mid-episode"
        assert guarded["first_failure_ts"] == NOW - 78 * 60, "the outage start was re-stamped"

    def test_only_a_terminal_SUCCESS_closes_the_episode(self, tmp_path):
        """The close condition is the one way a start clears, and it is independent of
        this file: `ok` is set only after the child exited 0 AND wrote its run output."""
        from background import sim_runner

        p = tmp_path / "state.json"
        sim_runner.record_run_outcome(False, detail="boom", state_path=p, now=NOW)
        sim_runner.record_run_outcome(False, detail="boom", state_path=p, now=NOW + 600)
        still_open = sim_runner.record_run_outcome(False, detail="boom", state_path=p, now=NOW + 1200)
        assert still_open["first_failure_ts"] == NOW
        assert still_open["consecutive_failures"] == 3

        closed = sim_runner.record_run_outcome(True, state_path=p, now=NOW + 1800)
        assert closed["first_failure_ts"] is None, (
            "a terminal success must be able to close the episode -- a guard that cannot "
            "be cleared by real evidence wedges the rung on permanently"
        )
        assert closed["consecutive_failures"] == 0

    def test_the_guard_is_actually_wired_not_merely_imported(self):
        """'Wired this field in' vs a no-op that reviews as protection -- the distinction
        `guard_episode`'s own docstring draws. Both episode fields must be DECLARED, or
        the call silently protects nothing."""
        from background import sim_runner

        assert "first_failure_ts" in sim_runner.PRODUCER_SINCE_FIELDS
        assert "consecutive_failures" in sim_runner.PRODUCER_STREAK_FIELDS

        import inspect
        src = inspect.getsource(sim_runner.record_run_outcome)
        assert "guard_episode(" in src, "the state is written without passing through the guard"
        assert "episode_closed=ok" in src, (
            "the close condition is not the terminal-success evidence the disposition row "
            "names -- a guard closed on anything weaker is closed on the thing it guards"
        )
