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
    sdw.record_gate_run(600.0, 1800, "sha_ok_0001", "pass", p)      # headroom 0.67 -> ok
    sdw.record_gate_run(1500.0, 1800, "sha_tight_01", "pass", p)    # headroom 0.17 -> tight
    rows = sdw.read_series(p)
    assert [r["band"] for r in rows] == ["ok", "tight"]
    assert len(spy.sent) == 1 and "sha_tight" in spy.sent[0][0]


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
