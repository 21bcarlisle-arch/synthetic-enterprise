"""R15 proof for PW3_suite_duration_watch — the publish gate's suite-duration headroom.

The named defect is the one observed on 2026-08-09: the suite grew to 612.94s against a 600s
wall, and nothing saw it coming. So this measure has to FAIL on that shape, must not be
satisfiable from the ceiling alone (the atom's own R15 clause), must render RED rather than green
when it cannot measure, must alarm only on a TRANSITION (R5), and must never be able to red the
publish path it observes.

R12 is live on this atom specifically: the cheapest way to make headroom green is to run fewer
tests. Nothing here scores the number, and `test_the_measure_has_no_test_count_input` pins that
the measure cannot even see suite size.
"""
from __future__ import annotations

import inspect
import json

import pytest

from background import suite_duration_watch as sdw


# ── the measure reads the MEASURED duration, not the ceiling (the atom's named mutation) ──────
def test_headroom_reads_the_measured_duration_not_the_ceiling_alone():
    """MUTATION (the one the atom names): report headroom from the ceiling alone — e.g.
    `return 1 - 600.0 / ceiling` — and this test dies. Under ONE fixed ceiling, two different
    measured durations must produce two different headrooms, ordered the right way."""
    fast = sdw.headroom(300.0, 1800)
    slow = sdw.headroom(1500.0, 1800)
    assert fast != slow, "headroom that ignores the duration is a ceiling report, not a measure"
    assert fast > slow, "more time spent must mean less headroom"
    assert sdw.headroom(900.0, 1800) == pytest.approx(0.5)


def test_headroom_is_comparable_across_a_changed_ceiling():
    """The reason the figure is a RATIO: the ceiling moved 600 -> 1800s. The same fraction of the
    wall must read the same on both sides of that move, which a raw second count cannot do.

    MUTATION: return the raw remaining seconds and this fails."""
    assert sdw.headroom(300.0, 600) == pytest.approx(sdw.headroom(900.0, 1800))


def test_the_wedge_shape_reports_negative_headroom():
    """The observed defect: 612.94s against a 600s wall. Past the wall must read as past it, not
    clamp to zero — how far past is the diagnostic.

    MUTATION: clamp with max(0.0, ...) and this fails."""
    h = sdw.headroom(612.94, 600)
    assert h < 0
    assert sdw.band(h) == "tight"


# ── fail-closed, not fail-open (R15 killer pattern 2) ────────────────────────────────────────
@pytest.mark.parametrize("duration,ceiling", [
    (None, 1800), ("", 1800), ("abc", 1800), (float("nan"), 1800), (float("inf"), 1800),
    (-1.0, 1800), (600.0, 0), (600.0, -1), (600.0, None),
])
def test_unmeasurable_inputs_are_none_never_a_number(duration, ceiling):
    """An unavailable measurement is a FAILED measurement. MUTATION: return 1.0 (or 0.0) on any
    of these and this fails — a missing duration would then read as full headroom."""
    assert sdw.headroom(duration, ceiling) is None
    assert sdw.band(sdw.headroom(duration, ceiling)) == "unknown"


def test_a_missing_series_renders_red_not_green(tmp_path):
    """MUTATION: return an OK line when there is nothing to read and this fails. A measure with no
    data must say so — a green line from an empty series is the fail-open shape."""
    line = sdw.note_line(tmp_path / "absent.jsonl")
    assert "RED" in line
    assert "✅" not in line


def test_a_recorded_run_with_no_usable_duration_renders_red(tmp_path):
    p = tmp_path / "series.jsonl"
    p.write_text(json.dumps({"timestamp": "t", "git_hash": "deadbeefcafe",
                             "duration_seconds": None, "ceiling_seconds": 1800,
                             "headroom_ratio": None, "band": "unknown",
                             "outcome": "timeout"}) + "\n")
    line = sdw.note_line(p)
    assert "RED" in line and "unmeasurable, not zero" in line


def test_a_corrupt_line_does_not_blind_the_measure(tmp_path):
    """Shared append-only surface, concurrent writers: one bad line must not take the series out.

    MUTATION: drop the JSONDecodeError guard and this raises instead of reading."""
    p = tmp_path / "series.jsonl"
    p.write_text("{not json\n" + json.dumps(
        {"git_hash": "abc123def", "duration_seconds": 900.0, "ceiling_seconds": 1800,
         "headroom_ratio": 0.5, "band": "ok", "outcome": "pass"}) + "\n")
    assert len(sdw.read_series(p)) == 1
    assert "50%" in sdw.note_line(p)


# ── the reported surface ─────────────────────────────────────────────────────────────────────
def _row(h, sha="abc123def0", ceiling=1800, band="ok"):
    return {"timestamp": "t", "git_hash": sha, "duration_seconds": round((1 - h) * ceiling, 2),
            "ceiling_seconds": ceiling, "headroom_ratio": h, "band": band, "outcome": "pass"}


def test_the_reported_line_is_a_ratio_with_its_subject(tmp_path):
    """EXIT (1)+(2): the figure reported is a RATIO, and it carries the SHA it was measured on."""
    p = tmp_path / "series.jsonl"
    p.write_text(json.dumps(_row(0.60, sha="feedface12")) + "\n")
    line = sdw.note_line(p)
    assert "60%" in line
    assert "feedface1" in line
    assert "R12" in line, "the anti-Goodhart clause must travel with the number"


def test_the_line_reports_the_trend_not_just_the_level(tmp_path):
    """The atom's whole point is the APPROACH, not the arrival. MUTATION: drop the trend fragment
    and this fails."""
    p = tmp_path / "series.jsonl"
    p.write_text("".join(json.dumps(_row(h)) + "\n" for h in (0.66, 0.64, 0.65, 0.50)))
    line = sdw.note_line(p)
    assert "shrinking" in line and "prior" in line


def test_the_measure_has_no_test_count_input():
    """R12, mechanised rather than exhorted: headroom cannot be a function of suite size, because
    suite size is not one of its inputs. MUTATION: add a test-count parameter and this fails."""
    params = set(inspect.signature(sdw.headroom).parameters)
    assert params == {"duration_seconds", "ceiling_seconds"}


# ── R5: the alarm is a transition, both ways, once each ───────────────────────────────────────
class _Spy:
    def __init__(self):
        self.sent = []

    def __call__(self, message, **kw):
        self.sent.append((message, kw))
        return "sent"


def test_crossing_into_tight_fires_once():
    spy = _Spy()
    cur = dict(_row(0.20, band="tight"))
    assert sdw.alarm(cur, _row(0.60, band="ok"), notify_fn=spy) is not None
    assert len(spy.sent) == 1
    msg, kw = spy.sent[0]
    assert "SUITE HEADROOM" in msg and "20%" in msg
    assert kw["kind"] == "real_alarm" and kw["state"] == "tight"
    assert "deselect" in msg, "R5: the alarm carries its diagnostic and its forbidden fix"


def test_an_unchanged_tight_status_never_repeats():
    """R5 outright: a standing tight headroom must not page every publish cycle.

    MUTATION: drop the `cur_band == prev_band` short-circuit and this fails."""
    spy = _Spy()
    assert sdw.alarm(dict(_row(0.20, band="tight")), _row(0.22, band="tight"), notify_fn=spy) is None
    assert spy.sent == []


def test_recovery_fires_once_and_only_out_of_tight():
    spy = _Spy()
    assert sdw.alarm(dict(_row(0.60, band="ok")), _row(0.20, band="tight"), notify_fn=spy)
    assert "Recovered" in spy.sent[0][0]
    # ...and an ok run following an ok run is silent
    assert sdw.alarm(dict(_row(0.60, band="ok")), _row(0.55, band="ok"), notify_fn=spy) is None
    assert len(spy.sent) == 1


def test_a_first_ever_observation_does_not_page():
    """No previous run means nothing has been CROSSED. MUTATION: send on prev=None and the series'
    first healthy run pages for no reason."""
    spy = _Spy()
    assert sdw.alarm(dict(_row(0.60, band="ok")), None, notify_fn=spy) is None
    assert spy.sent == []


def test_a_first_ever_observation_that_is_already_tight_does_page():
    spy = _Spy()
    assert sdw.alarm(dict(_row(0.10, band="tight")), None, notify_fn=spy) is not None


def test_the_hysteresis_gap_holds_the_previous_band():
    """A run between the two thresholds is neither a crossing nor a recovery.

    MUTATION: collapse RECOVERED_HEADROOM onto TIGHT_HEADROOM and this fails — a suite sitting on
    the boundary would then alternate tight/ok and page on every cycle."""
    mid = (sdw.TIGHT_HEADROOM + sdw.RECOVERED_HEADROOM) / 2
    assert sdw.band(mid, previous="tight") == "tight"
    assert sdw.band(mid, previous="ok") == "ok"
    assert sdw.TIGHT_HEADROOM < sdw.RECOVERED_HEADROOM


# ── recording, and never raising into the publish path ────────────────────────────────────────
def test_record_stores_the_raw_inputs_so_the_ratio_is_rederivable(tmp_path):
    """Independence (R15 killer pattern 1): a reader must be able to re-derive the ratio from the
    stored duration and ceiling rather than trust the stored ratio.

    MUTATION: store only headroom_ratio and this fails."""
    p = tmp_path / "series.jsonl"
    rec = sdw.record(612.94, 600, "cafebabe1234", "timeout", p)
    on_disk = json.loads(p.read_text().strip())
    assert on_disk == rec
    assert on_disk["duration_seconds"] == 612.94 and on_disk["ceiling_seconds"] == 600
    assert sdw.headroom(on_disk["duration_seconds"],
                        on_disk["ceiling_seconds"]) == pytest.approx(on_disk["headroom_ratio"],
                                                                     abs=1e-4)
    assert on_disk["git_hash"] == "cafebabe1234" and on_disk["outcome"] == "timeout"


def test_record_gate_run_never_raises(monkeypatch, tmp_path):
    """The observer must not be able to red the publish path. MUTATION: remove the try/except in
    record_gate_run and this fails."""
    def boom(*a, **kw):
        raise RuntimeError("series unavailable")
    monkeypatch.setattr(sdw, "record", boom)
    assert sdw.record_gate_run(600.0, 1800, "abc", "pass", tmp_path / "s.jsonl") is None


def test_record_gate_run_appends_and_alarms(monkeypatch, tmp_path):
    """End to end on the real series path: an ok run, then a tight run, pages exactly once.

    Patches the notify CONTRACT (which `alarm` resolves at call time), not this module's own
    alarm — so the wiring between record_gate_run, the band it derives, and the page it sends is
    the thing under test rather than a stub of it."""
    spy = _Spy()
    monkeypatch.setattr("background.notify.notify", spy)
    p = tmp_path / "series.jsonl"
    # THE CEILING IS SCALED OFF THE CADENCE (2026-08-26) so this fixture measures what it says.
    # It used to read 600s/1800s and 1500s/1800s, chosen when the cadence was 330s: both runs
    # were then over the cadence, which is what makes the absolute alarm page once and go quiet.
    # Re-measuring the cadence to 1500s left the 600s run UNDER it, so the second figure never
    # fired and the test reddened on an arrangement it had only ever assumed. Anchored to the
    # constant, the intent survives any future re-measurement.
    over = sdw.PUBLISH_CADENCE_SECONDS * 2.0        # over the cadence, roomy on headroom -> ok
    tight = sdw.PUBLISH_CADENCE_SECONDS * 5.0       # over the cadence AND short of headroom
    ceiling = sdw.PUBLISH_CADENCE_SECONDS * 6.0
    sdw.record_gate_run(over, ceiling, "sha_ok_0001", "pass", p)      # headroom 0.67 -> ok
    sdw.record_gate_run(tight, ceiling, "sha_tight_01", "pass", p)    # headroom 0.17 -> tight
    rows = sdw.read_series(p)
    assert [r["band"] for r in rows] == ["ok", "tight"]
    headroom_pages = [m for m, kw in spy.sent
                      if kw.get("transition_key") == "suite_duration_headroom"]
    assert len(headroom_pages) == 1 and "sha_tight" in headroom_pages[0]
    # SECOND FIGURE, SEPARATE KEY (2026-08-21). Both runs here are over the cadence, so the
    # absolute alarm pages once on the FIRST one and stays silent on the second — a different
    # question from headroom, crossing at a different moment, and deliberately not folded in:
    # the first run is `ok` on headroom and already 2x its own cadence.
    absolute_pages = [m for m, kw in spy.sent
                      if kw.get("transition_key") == "publish_gate_absolute_duration"]
    assert len(absolute_pages) == 1 and "sha_ok_00" in absolute_pages[0]
    assert len(spy.sent) == 2


# ── the wiring: the gate measures, and the note reports ───────────────────────────────────────
def test_the_publish_gate_measures_its_own_run():
    """EXIT (1): the duration is recorded BY the gate, per run, with its SHA — including on the
    timeout, which is the most informative point in the series.

    MUTATION: unwire _record_gate_duration from _run_gate_in and this fails."""
    from background import process_run_complete as prc
    src = inspect.getsource(prc._run_gate_in)
    assert "_record_gate_duration" in src
    assert "time.monotonic()" in src
    assert '"timeout"' in src, "the run that hits the wall must not be the one missing from the series"
    assert "GATE_SUITE_TIMEOUT_SECONDS" in inspect.getsource(prc._record_gate_duration)


def test_the_daily_self_note_reports_the_headroom():
    """EXIT (2): reported on a surface that is READ. MUTATION: remove the block from render_note
    and this fails."""
    from background import daily_self_note as sm1
    note = sm1.render_note("2026-08-10T06:00:00+00:00", _runner=lambda *a: (None, "unavailable"))
    assert "Suite headroom" in note
    assert "publish-gate duration against its own ceiling" in note


# ── a test process may not write the live series ──────────────────────────────────────────────
# BLOCKING finding WORKER_FINDING_THE_HEADROOM_SURFACE_PUBLISHES_A_TEST_FIXTURE_AS_THE_GATES_
# DURATION_2026-08-20: 3,434 of 5,527 live rows were written by pytest through the production
# writer, and the daily self-note published one of them as the gate's duration.
def test_a_test_process_cannot_append_to_the_live_series():
    """THE SOURCE. This IS a test process, so a path-less `record()` — the exact call
    `_record_gate_duration` makes in production — must be refused, and the live file must not
    grow by one byte.

    MUTATION: drop the `guard_live_ledger_write` call from `record()` and this fails on the
    raises; drop it and the size assertion catches the write even if some other refusal is
    substituted for it. The size is read from the real `SERIES_PATH` deliberately — a control
    that checked a fixture path could not tell whether the live file was safe."""
    from background.live_ledger_guard import LiveLedgerWriteUnderTest

    before = sdw.SERIES_PATH.stat().st_size if sdw.SERIES_PATH.exists() else -1
    with pytest.raises(LiveLedgerWriteUnderTest) as exc:
        sdw.record(0.0, 4500, "abc1234", "pass")
    after = sdw.SERIES_PATH.stat().st_size if sdw.SERIES_PATH.exists() else -1
    assert before == after, "the live series grew during a test"
    # Assert the REASON, not merely that something raised: two stacked refusals are otherwise
    # indistinguishable and the weaker one could be the only survivor.
    assert "suite_duration_watch.record" in str(exc.value)


def test_record_gate_run_swallows_the_refusal_and_writes_nothing():
    """`record_gate_run` never raises, by contract — so the refusal must arrive as "no measurement
    this cycle", not as a swallowed exception that wrote anyway.

    MUTATION: make `record_gate_run` re-raise, or make the guard fail open, and this fails."""
    before = sdw.SERIES_PATH.stat().st_size if sdw.SERIES_PATH.exists() else -1
    assert sdw.record_gate_run(0.0, 4500, "abc1234", "pass") is None
    after = sdw.SERIES_PATH.stat().st_size if sdw.SERIES_PATH.exists() else -1
    assert before == after


def test_a_scratch_path_is_still_writable_under_test(tmp_path):
    """The refusal must be about the LIVE record, not about being a test. If this fails the guard
    has been widened into "tests cannot record", which would take the module's own R15 proofs with
    it — a control that cannot be exercised is the fail-silent pattern."""
    p = tmp_path / "series.jsonl"
    rec = sdw.record(600.0, 1800, "sha_scratch", "pass", p)
    assert rec["duration_seconds"] == 600.0
    assert len(sdw.read_series(p)) == 1


def test_the_production_writer_still_reaches_the_live_series_outside_a_test(monkeypatch):
    """The other direction of the same control, and the one a naive guard breaks: outside a test
    process the write must proceed. Asserted through `in_test_process()` — the single predicate
    the guard branches on — with pytest's own two signals removed.

    MUTATION: make `guard_live_ledger_write` refuse unconditionally and this fails, catching a
    repair that "fixed" the contamination by ending the measurement."""
    from background import live_ledger_guard as llg

    assert llg.is_live_record_path(sdw.SERIES_PATH), \
        "the live series must be inside the guarded directory, or the guard never sees it"
    monkeypatch.setattr(llg, "in_test_process", lambda: False)
    # Same call production makes; returns the path unchanged rather than raising.
    assert llg.guard_live_ledger_write(
        sdw.SERIES_PATH, writer="suite_duration_watch.record") == sdw.SERIES_PATH


# ── the rows already written are excluded, not deleted ────────────────────────────────────────
def test_a_zero_second_row_is_not_a_measurement(tmp_path):
    """THE RECORD. A 0.0s gate run is unreachable for a real run of ~26k tests and is what every
    fixture writes. MUTATION: stop excluding in `read_series` and this fails."""
    p = tmp_path / "series.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in (
        _row(0.72, sha="a892df011"),
        {"timestamp": "t", "git_hash": "abc1234", "duration_seconds": 0.0,
         "ceiling_seconds": 4500, "headroom_ratio": 1.0, "band": "ok", "outcome": "pass"},
    )))
    assert [r["git_hash"] for r in sdw.read_series(p)] == ["a892df011"]
    # Not deleted: the file is untracked and a truncation is unrecoverable if wrong.
    assert len(sdw.read_series(p, include_fixture_rows=True)) == 2


def test_the_line_reports_the_measurement_the_fixture_displaced(tmp_path):
    """The live symptom, reproduced: the fixture row is last, so `rows[-1]` published `100%` at
    `0.0s` while the real run measured 72%. MUTATION: stop excluding and this reports 100%."""
    p = tmp_path / "series.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in (
        _row(0.72, sha="a892df011", ceiling=4500),
        {"timestamp": "t", "git_hash": "abc1234", "duration_seconds": 0.0,
         "ceiling_seconds": 4500, "headroom_ratio": 1.0, "band": "ok", "outcome": "pass"},
    )))
    line = sdw.note_line(p)
    assert "72%" in line and "100%" not in line
    assert "a892df011" in line and "abc1234" not in line


def test_the_line_says_what_it_excluded(tmp_path):
    """A surface that silently drops two thirds of its input is the mirror of the defect it
    repairs. MUTATION: drop `_exclusion_fragment` from `note_line` and this fails."""
    p = tmp_path / "series.jsonl"
    fixture = {"timestamp": "t", "git_hash": "deadbeef", "duration_seconds": 0.0,
               "ceiling_seconds": 4500, "headroom_ratio": 1.0, "band": "ok", "outcome": "pass"}
    p.write_text("".join(json.dumps(r) + "\n" for r in (
        _row(0.72, sha="a892df011", ceiling=4500), fixture, fixture)))
    line = sdw.note_line(p)
    assert "2 sub-second row(s) excluded" in line
    # Silent when there is nothing to say — no permanent footnote about a fixed problem.
    clean = tmp_path / "clean.jsonl"
    clean.write_text(json.dumps(_row(0.72, sha="a892df011", ceiling=4500)) + "\n")
    assert "excluded" not in sdw.note_line(clean)


def test_a_fixture_that_writes_a_token_duration_is_still_a_fixture(tmp_path):
    """THE FAIL-OPEN THE LIVE FILE PROVED (2026-08-21). `is_fixture_row` tested `== 0.0`, on the
    stated grounds that zero is "reached by every test one". It is not: of the 2,126 rows the old
    rule admitted as measurements, 1,579 were test writes carrying 0.01/0.02/0.11s — a full 74%
    of what every downstream reader saw. Only the two NAMED fixture shas write a literal zero; a
    fixture that passes any small non-zero number sailed through.

    MUTATION: restore `d == 0.0` in `is_fixture_row` and this fails on both legs — the 0.02s row
    is admitted as a measurement and the reported line publishes 100% headroom at 0.02s.
    """
    token = {"timestamp": "t", "git_hash": "9735ae10f4fd497e1e5c8cb1b58ddcae3dc4bc64",
             "duration_seconds": 0.02, "ceiling_seconds": 4500, "headroom_ratio": 1.0,
             "band": "ok", "outcome": "pass"}
    assert sdw.is_fixture_row(token), "a 0.02s gate run is not a measurement"
    assert sdw.is_fixture_row(dict(token, duration_seconds=0.11))
    assert sdw.is_fixture_row(dict(token, duration_seconds=0.0)), "the old subject still holds"

    # THE FLOOR MUST NOT EAT A REAL RUN. 3.46s is the fastest run the publisher has ever
    # recorded across 374 rows; the fail-fast reds of 2026-08-21 measured ~23s. Both are
    # measurements and must survive, or the repair fails CLOSED and hides the live numbers.
    assert not sdw.is_fixture_row(dict(token, duration_seconds=3.46))
    assert not sdw.is_fixture_row(dict(token, duration_seconds=23.44))
    assert not sdw.is_fixture_row(dict(token, duration_seconds=1.0)), "the floor is exclusive"

    # The live symptom, end to end: the token row is LAST, so an admitted one publishes itself.
    p = tmp_path / "series.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in (
        _row(0.72, sha="a892df011", ceiling=4500), token)))
    line = sdw.note_line(p)
    assert "72%" in line and "100%" not in line
    assert "a892df011" in line and "9735ae10f" not in line
    assert "1 sub-second row(s) excluded" in line


def test_a_fixture_row_cannot_page_a_false_recovery(tmp_path):
    """§3 of the finding, turned into a control: a genuinely tight run followed by ONE test write
    paged `[SUITE HEADROOM] Recovered` — a recovery that did not happen, on the director's
    channel, sourced from a fixture (R5: transitions in the world, not in the file).

    It has never fired only because no real run has ever been tight; it arms itself exactly when
    the instrument starts to matter. MUTATION: remove the `is_fixture_row(current)` early return
    from `alarm()` and this fails with `alarms sent: 1`."""
    spy = _Spy()
    monkeypatch_free_tight = {"timestamp": "t", "git_hash": "realtight1",
                              "duration_seconds": 4200.0, "ceiling_seconds": 4500,
                              "headroom_ratio": 0.0667, "band": "tight", "outcome": "pass"}
    fixture = {"timestamp": "t", "git_hash": "abc1234", "duration_seconds": 0.0,
               "ceiling_seconds": 4500, "headroom_ratio": 1.0, "band": "ok", "outcome": "pass"}
    assert sdw.alarm(fixture, monkeypatch_free_tight, notify_fn=spy) is None
    assert spy.sent == []
    # The other leg: a fixture must not become the baseline a REAL crossing is measured against,
    # or the next genuine tight run reads as ok->tight from the wrong previous.
    real_tight = dict(monkeypatch_free_tight)
    assert sdw.alarm(real_tight, fixture, notify_fn=spy) is not None
    assert len(spy.sent) == 1 and "realtight" in spy.sent[0][0]  # sha rendered at [:9]


# ── THE ABSOLUTE NUMBER, WHICH NO CEILING CAN BUY SILENCE ON ──────────────────────────────────
#
# Director, 2026-08-21 console: *"Nothing watches the absolute number — only headroom against a
# budget that grew to fit."* The named defect is six ceiling raises (600 → 4500), after each of
# which the SAME runtime read as more headroom. Every test below exists to make that move
# unavailable to the second figure, and the first one is the mutation that matters: point
# `absolute_band` at the ceiling in any way and it dies.
def test_the_absolute_band_is_unmoved_by_a_ceiling_that_grew_to_fit():
    """THE named mutation. Re-derive the verdict against the ceiling — `d / ceiling > 1`, or any
    ratio band — and this test dies, because the whole ceiling history is applied to ONE fixed
    runtime here and the verdict may not move.

    1250s is today's real gate run. Under every ceiling this project has shipped it is still four
    times the cadence, and the instrument must say so at 4500 exactly as loudly as at 600."""
    # RELATIVE TO THE CADENCE, NOT A LITERAL (2026-08-26). These durations were chosen
    # when `PUBLISH_CADENCE_SECONDS` was 330; re-measuring it to 1500 (runs got ~7.7x
    # slower as the book grew) turned them from 'comfortably over' into 'under', and the
    # tests reddened on a constant they were never about. A fixture that pins an absolute
    # number against a MEASURED quantity is the same defect this module exists to watch.
    over = sdw.PUBLISH_CADENCE_SECONDS * 2.0
    verdicts = {sdw.absolute_band(over) for _ in (600, 1800, 2600, 2900, 3400, 3600, 4500)}
    assert verdicts == {"over_cadence"}, "a verdict that moved with the ceiling is the old figure"
    # And the headroom ratio over the same runtime DOES move — which is why a second figure had
    # to exist. This is the contrast the finding rests on, asserted rather than described.
    assert sdw.headroom(over, 600) != sdw.headroom(over, 4500)
    assert sdw.band(sdw.headroom(1250.0, 4500)) == "ok"  # "healthy" at 21 minutes


def test_the_absolute_band_cannot_be_told_the_ceiling():
    """Structural, not conventional: the silencing move is unavailable rather than discouraged.
    MUTATION: add a `ceiling_seconds` parameter — even an unused, defaulted one — and this fails
    before anyone gets as far as using it."""
    params = set(inspect.signature(sdw.absolute_band).parameters)
    assert params == {"duration_seconds"}


def test_a_genuinely_fast_gate_reads_within_the_cadence():
    """THE NULL CONTROL. Without it, `return "over_cadence"` — a constant that can never be
    satisfied — passes every other test in this class, and an alarm that is always on is an
    alarm nobody reads. The gate measured 39s scoped and ~10 minutes two weeks ago; the first
    must read within and the second must not."""
    assert sdw.absolute_band(39.0) == "within_cadence"
    assert sdw.absolute_band(sdw.PUBLISH_CADENCE_SECONDS - 1) == "within_cadence"
    assert sdw.absolute_band(sdw.PUBLISH_CADENCE_SECONDS + 1) == "over_cadence"


def test_the_absolute_band_fails_closed_on_what_it_cannot_measure():
    """R15 killer pattern 2 (FAIL-OPEN on missing/zero/malformed): an unmeasurable duration is
    "unknown", which sends nothing — never "within_cadence", which would read as a green.
    MUTATION: `except: return "within_cadence"` and this dies.

    A numeric STRING is deliberately absent from this list: `headroom()` coerces one too, and a
    second rule for the same input would make the two figures disagree about whether a row is
    measurable at all."""
    for bad in (None, "", "not-a-number", float("nan"), float("inf"), -1.0, {}):
        assert sdw.absolute_band(bad) == "unknown", bad


def test_the_cadence_alarm_fires_once_on_the_crossing_and_once_on_recovery():
    """R5, and the first-observation asymmetry this alarm needs: it is crossed TODAY, so a
    first-ever `over_cadence` must page (the bad direction being the initial state is the case
    it was built in), while a first-ever `within_cadence` has crossed nothing.

    MUTATION: make the unchanged-band case send, and `alarms sent: 1` becomes 2."""
    spy = _Spy()
    slow = {"timestamp": "t", "git_hash": "2c0ba712b", "duration_seconds": 1250.0,
            "ceiling_seconds": 4500, "headroom_ratio": 0.72, "band": "ok",
            "cadence_band": "over_cadence", "cadence_seconds": 330, "outcome": "pass"}
    fast = {"timestamp": "t", "git_hash": "fast00001", "duration_seconds": 39.0,
            "ceiling_seconds": 4500, "headroom_ratio": 0.99, "band": "ok",
            "cadence_band": "within_cadence", "cadence_seconds": 330, "outcome": "pass"}

    assert sdw.absolute_alarm(fast, None, notify_fn=spy) is None      # first-ever good: silent
    assert sdw.absolute_alarm(slow, None, notify_fn=spy) is not None  # first-ever bad: pages
    assert sdw.absolute_alarm(slow, slow, notify_fn=spy) is None      # unchanged: silent
    assert sdw.absolute_alarm(fast, slow, notify_fn=spy) is not None  # recovery: pages once
    assert len(spy.sent) == 2
    assert "1250.0s" in spy.sent[0][0] and "3.8x" in spy.sent[0][0]
    assert spy.sent[0][1]["transition_key"] == "publish_gate_absolute_duration"
    assert "Recovered" in spy.sent[1][0]


def test_the_cadence_alarm_is_not_suppressed_by_a_comfortable_headroom_band():
    """The two figures must be able to DISAGREE, or the second one is decoration. The run below
    is `band: ok` — 72% headroom, the shape that read healthy for six ceiling raises — and the
    cadence alarm must page on it anyway.

    MUTATION: gate `absolute_alarm` on the headroom band (`if current["band"] == "ok": return`)
    and this dies. That mutation is exactly the fold-into-one-alarm design this rejects."""
    spy = _Spy()
    comfortable_but_slow = {"timestamp": "t", "git_hash": "a892df011",
                            "duration_seconds": 1247.73, "ceiling_seconds": 4500,
                            "headroom_ratio": 0.72, "band": "ok",
                            "cadence_band": "over_cadence", "cadence_seconds": 330,
                            "outcome": "pass"}
    assert sdw.alarm(comfortable_but_slow, None, notify_fn=spy) is None  # headroom: nothing to say
    assert sdw.absolute_alarm(comfortable_but_slow, None, notify_fn=spy) is not None
    assert len(spy.sent) == 1 and "raising the ceiling cannot clear it" in spy.sent[0][0]


def test_a_fixture_row_cannot_page_the_cadence_alarm(tmp_path):
    """The same defect as `test_a_fixture_row_cannot_page_a_false_recovery`, which this alarm
    would otherwise re-open: a 0.0s test write is `within_cadence` by arithmetic, so without the
    guard one fixture row pages `[GATE ABSOLUTE] Recovered` after a real slow run.

    MUTATION: drop either `is_fixture_row` branch from `absolute_alarm` and this fails."""
    spy = _Spy()
    slow = {"timestamp": "t", "git_hash": "2c0ba712b", "duration_seconds": 1250.0,
            "ceiling_seconds": 4500, "headroom_ratio": 0.72, "band": "ok",
            "cadence_band": "over_cadence", "cadence_seconds": 330, "outcome": "pass"}
    fixture = {"timestamp": "t", "git_hash": "abc1234", "duration_seconds": 0.0,
               "ceiling_seconds": 4500, "headroom_ratio": 1.0, "band": "ok",
               "cadence_band": "within_cadence", "cadence_seconds": 330, "outcome": "pass"}
    assert sdw.absolute_alarm(fixture, slow, notify_fn=spy) is None
    assert spy.sent == []
    # ...and a fixture may not become the baseline a real crossing is measured against.
    assert sdw.absolute_alarm(slow, fixture, notify_fn=spy) is not None


def test_the_record_stores_the_absolute_verdict_and_the_cadence_it_used(tmp_path):
    """5,570 historical rows can only be re-asked this question if the answer is ON the row, and
    the cadence rides along so a future re-derivation cannot silently change what old rows meant.
    MUTATION: drop either key from `record()` and this fails."""
    p = tmp_path / "series.jsonl"
    # Relative to the cadence: a literal chosen against the old 330s reads within the new 1500s.
    rec = sdw.record(sdw.PUBLISH_CADENCE_SECONDS * 2.0, 4500, "2c0ba712b", "pass", p)
    assert rec["cadence_band"] == "over_cadence"
    assert rec["cadence_seconds"] == sdw.PUBLISH_CADENCE_SECONDS
    assert json.loads(p.read_text().splitlines()[-1])["cadence_band"] == "over_cadence"


def test_the_read_surface_states_the_absolute_number_beside_the_ratio(tmp_path):
    """The 75-minute gate was invisible because the only surface reported a RATIO. MUTATION: drop
    `_absolute_fragment` from `note_line` and this fails — the line goes back to reporting 72%
    headroom on a run four times slower than its own cadence, with no second opinion."""
    p = tmp_path / "series.jsonl"
    p.write_text(json.dumps({"timestamp": "t", "git_hash": "a892df011",
                             "duration_seconds": 1247.73, "ceiling_seconds": 4500,
                             "headroom_ratio": 0.72, "band": "ok",
                             "cadence_band": "over_cadence", "cadence_seconds": 330,
                             "outcome": "pass"}) + "\n")
    line = sdw.note_line(p)
    assert "72%" in line                      # the ratio still reads healthy...
    assert "1247.73s is 3.8x the 330s cadence" in line   # ...and the absolute number says so
    assert "never reads it" in line


def test_the_cadence_is_read_from_a_measurement_not_an_aspiration():
    """The 300s cap that wedged publishing twice this morning was an ASPIRATION (the target
    cadence) used as a production bound. This constant is instead the MEASURED median marker
    inter-arrival (334s over the last 200 markers), so it describes the world rather than a wish.

    MUTATION: set it to a round aspirational 300 or 60 and this fails.

    MEASURED HERE, NOT PINNED (2026-08-26). This used to assert `320 <= C <= 440` — the p10-p90
    band of the 2026-08-21 measurement. That guarded the right property against the wrong thing:
    it pinned the constant to a MOMENT, so when runs slowed ~7.7x (the book grew about sixfold)
    the world left the band and the test reddened on a number that had become correct. A control
    that goes stale the moment its subject changes is the defect this whole module watches for,
    one level up.

    So the bound is recomputed from the markers on disk. It still fails on an aspiration — a
    round 60 or 300 is far below any real inter-arrival — and it now also fails if the constant
    drifts ABOVE the world, which is the silencing direction and the one that matters most.
    """
    measured = sdw.measure_publish_cadence_seconds()
    if measured is None:
        pytest.skip("fewer than three usable marker gaps on disk; nothing to measure against")
    assert sdw.PUBLISH_CADENCE_SECONDS <= measured, (
        f"cadence {sdw.PUBLISH_CADENCE_SECONDS}s is SOFTER than the measured "
        f"{measured:.0f}s — the bound must never be looser than the observation")
    assert sdw.PUBLISH_CADENCE_SECONDS >= measured * 0.5, (
        f"cadence {sdw.PUBLISH_CADENCE_SECONDS}s is far below the measured {measured:.0f}s — "
        "an aspiration used as a bound is what wedged publishing twice on 2026-08-21")


def test_a_killed_run_is_not_certified_as_inside_the_cadence():
    """FOUND BY THE LIVE SURFACE, not by design: rendering `note_line()` against the real series
    the day this landed produced *"Absolute: 304.05s, inside the 330s publish cadence"* — from the
    row `304.05s ceiling=300 outcome=timeout`, a gate that was KILLED and never answered. A
    censored run reported as comfortably healthy is R15 killer pattern 2 in the surface built to
    watch for exactly that.

    A timeout's duration is a LOWER BOUND. Above the cadence it still decides (≥ over is over);
    below it, the run was stopped before it could say, and that is `unknown` — never a green.

    MUTATION: drop the `outcome == "timeout"` branch from `row_cadence_band` and the first
    assertion fails with `within_cadence`."""
    killed_early = {"duration_seconds": 304.05, "ceiling_seconds": 300, "outcome": "timeout"}
    assert sdw.row_cadence_band(killed_early) == "unknown"
    killed_late = {"duration_seconds": 4503.7, "ceiling_seconds": 4500, "outcome": "timeout"}
    assert sdw.row_cadence_band(killed_late) == "over_cadence"
    # NULL CONTROL: the censoring rule must key on the OUTCOME, not on the duration being small.
    # A run that genuinely COMPLETED in 304s is a measurement and must read as one.
    finished = {"duration_seconds": 304.05, "ceiling_seconds": 3400, "outcome": "pass"}
    assert sdw.row_cadence_band(finished) == "within_cadence"


def test_a_censored_run_cannot_page_a_false_cadence_recovery():
    """The consequence on the channel, not just in the classifier: without the censoring rule a
    slow gate followed by a run KILLED at 304s pages `[GATE ABSOLUTE] Recovered` — a recovery
    that did not happen, sourced from a run that never finished. Same shape as the fixture-row
    false recovery of 2026-08-20, arriving through a different door."""
    spy = _Spy()
    slow = {"timestamp": "t", "git_hash": "2c0ba712b", "duration_seconds": 1250.0,
            "ceiling_seconds": 4500, "headroom_ratio": 0.72, "band": "ok",
            "outcome": "pass"}
    killed = {"timestamp": "t", "git_hash": "f983f074c", "duration_seconds": 304.05,
              "ceiling_seconds": 300, "headroom_ratio": -0.0135, "band": "tight",
              "outcome": "timeout"}
    assert sdw.absolute_alarm(killed, slow, notify_fn=spy) is None
    assert spy.sent == []


def test_the_record_marks_a_timeout_row_censored_at_write_time():
    """The verdict is stored, so it must be the censoring-aware one at the moment of writing —
    otherwise every future reader of the 5,570-row history re-derives a green for a killed run.
    MUTATION: have `record()` call `absolute_band(duration_seconds)` directly and this fails."""
    import tempfile
    from pathlib import Path as _P
    with tempfile.TemporaryDirectory() as d:
        p = _P(d) / "series.jsonl"
        rec = sdw.record(304.05, 300, "f983f074c", "timeout", p)
        assert rec["cadence_band"] == "unknown"
        assert sdw.record(304.05, 3400, "f983f074c", "pass", p)["cadence_band"] == "within_cadence"


def test_the_surface_says_the_absolute_number_is_UNMEASURED_rather_than_going_quiet(tmp_path):
    """A first draft returned "" for the censored case, so the absolute figure disappeared from
    the read surface precisely on the runs that were KILLED — silent at the moment of failure,
    which is the defect this whole figure exists to repair, one level down.

    MUTATION: `return ""` on the unknown branch and this fails."""
    p = tmp_path / "series.jsonl"
    p.write_text(json.dumps({"timestamp": "t", "git_hash": "f983f074c",
                             "duration_seconds": 304.05, "ceiling_seconds": 300,
                             "headroom_ratio": -0.0135, "band": "tight",
                             "outcome": "timeout"}) + "\n")
    line = sdw.note_line(p)
    assert "UNMEASURED" in line
    assert "killed at 304.05s" in line
    assert "not a fast one" in line
    assert "inside the" not in line, "a killed run may never render as inside the cadence"
