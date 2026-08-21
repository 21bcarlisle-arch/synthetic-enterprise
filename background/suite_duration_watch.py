"""Suite duration watch — how much room the publish gate's suite has left before its wall.

PW3_suite_duration_watch, from DIRECTOR_STEER_SECOND_PUBLISH_WEDGE_2026-08-09 OBSERVATIONS:
*"The suite grew past a fixed wall. The new ceiling is sound and growth now fails loudly rather
than silently — but nothing watches suite duration, so the same shape recurs, just noisily."*

WHAT HAPPENED. The publish-gate suite reached 612.94s against a 600s timeout. The timeout branch
returned "passed", so the gate could not pass — it could only time out and publish unverified.
That fail-open is closed (1fd85cb27: a timeout now BLOCKS). What is still unmeasured is the
GROWTH that reached the wall: the suite crossed it silently over months, and the only event was
the crossing. This module makes the approach visible before the arrival.

WHY A NEW SERIES, having checked the existing one first (the atom's own EXIT prefers a series
that already exists). `docs/observability/test_execution_log.jsonl` cannot answer this:
  * it records `{timestamp, test_count}` and NO duration — the quantity in question is absent;
  * it carries no commit SHA, so a duration could not be attributed to a subject;
  * every partial/targeted pytest invocation appends to it undifferentiated (1,000+ lines/day of
    2-test runs), so the gate's own runs are not separable from them; and
  * the gate runs inside a throwaway HEAD checkout whose `docs/observability/` is discarded, so
    gate runs never reach that log at all.
Extending it in place would mean changing what every pytest session writes in order to observe
one specific caller. The cheap correct thing is one append per GATE run, written by the gate.

WHAT IS REPORTED, AND WHY AS A RATIO. Headroom = 1 − duration/ceiling: the fraction of the wall
still unused. A raw second count is not comparable across a changed ceiling — the ceiling moved
600 → 1800 the day this atom was minted, and every historical second-count silently changed
meaning at that moment. A ratio survives that move; the raw duration and ceiling are BOTH stored
so the ratio stays re-derivable and auditable.

R12 — DURATION IS A DIAGNOSTIC, NEVER A TARGET. The fastest way to make this number green is to
run fewer tests: deselect, mark slow, move to a tier. That is forbidden here, explicitly and by
name — CLAUDE.md's "DEPTH IS NOT THE PLACE TO SAVE" makes verification depth a wall and width the
dial. No test may be deselected, marked slow, or rehomed to a tier in order to move this figure.
A tight headroom is a signal to raise the ceiling (with the measurement behind it) or to make the
machine faster, never to make the suite smaller. Nothing here scores the number and there is no
lower bound; the alarm has one direction.

R5 — TREND TRANSITION, NOT A STATUS LINE. The alarm fires ONCE on crossing into a tight band and
ONCE on recovery, and never repeats an unchanged status. A hysteresis gap between the two
thresholds keeps a suite sitting on the boundary from paging on every cycle.

R15 — the measure must be able to FAIL, and cannot be satisfied by the ceiling alone: `headroom`
reads the MEASURED duration, so a mutation reporting headroom from the ceiling on its own kills
`test_headroom_reads_the_measured_duration_not_the_ceiling_alone`. Unmeasurable inputs return
None and render RED (an unavailable check is a failed check), never a fabricated green.

NEVER RAISES INTO THE PUBLISH PATH. `record_gate_run` swallows everything: an observer that can
red the gate it observes is itself a defect.

A TEST PROCESS MAY NOT WRITE THE LIVE SERIES (2026-08-20, BLOCKING finding
`WORKER_FINDING_THE_HEADROOM_SURFACE_PUBLISHES_A_TEST_FIXTURE_AS_THE_GATES_DURATION_2026-08-20`).
`process_run_complete._record_gate_duration` is the sole production caller and never passed the
`path` this module accepts, so every test that exercised the publish path appended a fabricated
row here through the front door. Measured on 2026-08-20: **3,434 of 5,527 live rows** were
fixtures (`deadbeef` 1,974, `abc1234` 1,460), and `note_line()` — which the daily self-note
publishes — was reporting `100% headroom, 0.0s, sha abc1234` while the real run it displaced
measured 1247.73s = 72%. Two halves, because the source and the record are separate problems:

  * THE SOURCE is closed at the choke point, not the instance (R10). `record()` routes its
    destination through `live_ledger_guard.guard_live_ledger_write`, the refusal built for the
    same class on 2026-08-17. Threading a `path` through `_record_gate_duration` — the instance
    fix — would close one caller and leave the shape open for the next one.
  * THE ROWS ALREADY WRITTEN cannot be un-written: this file is untracked and a quiet truncation
    is unrecoverable if wrong. So `read_series()` EXCLUDES them and `note_line()` SAYS how many
    it dropped — reversible and visible, where a deletion is neither.

A FIXTURE ROW MAY NOT PAGE (§3 of that finding). A 0.0s row carries `headroom_ratio: 1.0`, so a
genuinely tight run followed by one test write reads as a RECOVERY and pages the director on a
transition in the file rather than in the world. It has never fired only because no real run has
ever been tight; it arms itself exactly when the instrument starts to matter. `alarm()` therefore
treats an unmeasurable current record as `unknown`, which sends nothing.
"""
from __future__ import annotations

import datetime
import json
import math
from pathlib import Path

# Top level and no `try`, matching that module's own doctrine: if the guard cannot be imported,
# this module does not import either. An unavailable check is a FAILED check (R15), never a
# silently skipped one.
from background.live_ledger_guard import guard_live_ledger_write

PROJECT_DIR = Path(__file__).resolve().parent.parent
SERIES_PATH = PROJECT_DIR / "docs" / "observability" / "publish_gate_duration.jsonl"

# Headroom bands. TIGHT fires the alarm; RECOVERED clears it. The gap between them is deliberate
# hysteresis (R5): a suite oscillating around one threshold would otherwise page on every cycle,
# and a repeating alarm is an ignored alarm.
#
# 0.34 = the ceiling is less than ~1.5x the measured runtime. Chosen against the observed shape:
# the wedge suite ran 612.94s, and the ceiling was re-derived at 3x the measured runtime (0.66
# headroom). Half of that margin spent is the point at which the next re-derivation should be
# planned rather than discovered.
TIGHT_HEADROOM = 0.34
RECOVERED_HEADROOM = 0.45

# How many prior runs the reported trend looks back over.
TREND_WINDOW = 5

# ── THE ABSOLUTE NUMBER, WHICH NO CEILING CAN BUY SILENCE ON (2026-08-21, director console)
# ─────────────────────────────────────────────────────────────────────────────────────────
#
# *"A 75-minute gate is absurd on its face and neither of us said so. Two weeks ago it was ten
# minutes. Nothing watches the absolute number — only headroom against a budget that grew to
# fit."*
#
# He is describing THIS MODULE, and the diagnosis is exact. Everything above is a RATIO against
# `ceiling_seconds`, and `test_headroom_is_comparable_across_a_changed_ceiling` pins that
# property on purpose — a headroom figure has to survive a ceiling move to be a trend at all.
# But the ceiling moved 600 → 1800 → 2600 → 2900 → 3600 → 4500, and on the far side of each move
# the SAME runtime read as more headroom. The instrument reported recovery six times while the
# quantity it exists to watch got worse, and its own alarm text prescribes the mechanism:
# *"Raise the ceiling from a fresh measurement"*. A watch whose remedy is to move the thing it
# measures against cannot see growth. That is not a bug in the ratio; it is the ratio being the
# only figure.
#
# So this is the SECOND figure, and its entire design constraint is INDEPENDENCE FROM THE BUDGET:
# `absolute_band()` does not take `ceiling_seconds` and cannot be passed it. That is structural,
# not conventional — `test_the_absolute_band_cannot_be_told_the_ceiling` reads the signature, so
# the silencing move is unavailable rather than merely discouraged.
#
# WHAT IT MEASURES AGAINST, since not the ceiling. The gate's job is to answer "may THIS run
# publish". A check slower than the interval between runs is answering about a repo that has
# already moved on — the director again: *"A check that takes 75 minutes in a repo changing every
# 15 isn't verifying the current state, it's reporting on the past."* So the reference is the
# CADENCE the gate gates, which is a fact about the world and not a budget anyone can raise.
#
# MEASURED, not assumed: the median inter-arrival of the last 200 `run_complete_*` markers is
# 334s (p10 324s, p90 435s), over 970 markers spanning 2026-08-09 → 2026-08-21. 330 is that
# median, rounded down so the bound is never softer than the observation.
PUBLISH_CADENCE_SECONDS = 330

# THIS IS AN ALARM AND A SURFACE, NEVER A KILL, and that restraint is bought with evidence from
# this morning. The first attempt at the director's *"put a limit on the absolute duration that
# fails loudly when crossed"* made 300s a production TIMEOUT (`9dc57daee`, reverted): an
# aspirational cap on a measured quantity does not shrink the quantity, it just kills the work —
# publishing timed out twice at `304.05s ceiling=300`. The limit that survives is one that FAILS
# LOUDLY without failing the cycle, because the crossing is real information and the kill was not.
#
# Today's healthy gate runs ~1250s against this: it is crossed NOW, and says so ONCE (R5), not
# every cycle. It goes quiet when the scope work earns it, and it can never be quieted by a
# number anyone writes.


def headroom(duration_seconds, ceiling_seconds):
    """Fraction of the ceiling still unused: 1 − duration/ceiling. None when unmeasurable.

    Negative when the suite ran LONGER than its wall (the 612.94s/600s shape) — deliberately not
    clamped at zero, because how far past the wall a run went is the diagnostic.

    FAIL-CLOSED (R15 killer pattern 2): a missing, non-numeric, non-finite or negative duration,
    or a non-positive ceiling, returns None rather than a number. A None renders RED upstream.
    """
    try:
        d = float(duration_seconds)
        c = float(ceiling_seconds)
    except (TypeError, ValueError):
        return None
    if not (math.isfinite(d) and math.isfinite(c)):
        return None
    if d < 0 or c <= 0:
        return None
    return 1.0 - (d / c)


def band(h, previous: str | None = None) -> str:
    """Classify a headroom into tight / ok / unknown, holding `previous` inside the hysteresis gap.

    Inside [TIGHT_HEADROOM, RECOVERED_HEADROOM) the band is whatever it already was — a run in the
    gap is neither a new crossing nor a recovery. With no previous band, the gap reads `ok`: the
    alarm's job is to announce a CROSSING, and a first-ever observation has crossed nothing.
    """
    if h is None:
        return "unknown"
    if h < TIGHT_HEADROOM:
        return "tight"
    if h >= RECOVERED_HEADROOM:
        return "ok"
    return previous if previous in ("tight", "ok") else "ok"


def absolute_band(duration_seconds) -> str:
    """Classify a raw runtime against the publish CADENCE: over_cadence / within_cadence / unknown.

    Takes ONE argument and it is not the ceiling. Every silencing move this project has actually
    made — six ceiling raises — works by changing the denominator, and there is no denominator
    here to change. A gate slower than the interval between the runs it gates is reporting on a
    repo that has moved on, whatever budget it was given to do it in.

    NO HYSTERESIS, unlike `band()`. The gap there exists because a headroom ratio drifts across
    its threshold as a suite grows; this bound is 330s against a ~1250s reality, four times away
    from any oscillation. A hysteresis gap here would be margin nobody measured, which is the
    shape being repaired.

    FAIL-CLOSED (R15 killer pattern 2): missing, non-numeric, non-finite or negative returns
    "unknown", which sends nothing and renders as unmeasured — never as within.
    """
    try:
        d = float(duration_seconds)
    except (TypeError, ValueError):
        return "unknown"
    if not math.isfinite(d) or d < 0:
        return "unknown"
    return "over_cadence" if d > PUBLISH_CADENCE_SECONDS else "within_cadence"


def row_cadence_band(rec) -> str:
    """`absolute_band` for a whole ROW, with the one thing a bare duration cannot know: censoring.

    A `timeout` row's `duration_seconds` is where the run was KILLED, not how long it takes. It is
    a LOWER BOUND. That distinction is not academic here — the live series' latest row when this
    was written was `304.05s ceiling=300 outcome=timeout`, and the bare band called it
    "within_cadence", i.e. reported a gate that never finished as comfortably inside its cadence.
    A killed run certified as healthy is R15 killer pattern 2 (FAIL-OPEN) in the surface this
    module exists to be.

    So: censored ABOVE the cadence is still `over_cadence` (≥ a number already over it is over
    it), and censored BELOW is `unknown` — the run was stopped before it could answer, and an
    unavailable measurement is a failed one, never a green.

    This lives beside `absolute_band` rather than inside it on purpose: the primitive takes a
    duration and nothing else, which is what makes it impossible to tell it the ceiling.
    """
    if not isinstance(rec, dict):
        return "unknown"
    verdict = absolute_band(rec.get("duration_seconds"))
    if rec.get("outcome") == "timeout" and verdict == "within_cadence":
        return "unknown"
    return verdict


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def is_fixture_row(rec) -> bool:
    """True for a row that records a zero-second gate run — i.e. not a measurement.

    A gate run that compiles, collects and executes ~26k tests cannot take 0.00s; the duration is
    stored rounded to 2dp, so this is unreachable for any real run and reached by every test one.
    `bool` is excluded explicitly because `True == 1.0` is False but `False == 0.0` is True in
    Python, and a `False` in this field is malformed data, not a zero measurement.

    Deliberately NOT a git_hash denylist. `deadbeef`/`abc1234` are today's two fixture shas; a
    third fixture invents a third sha and a denylist of names would read it as a measurement. The
    subject is the impossible VALUE, which every present and future fixture shares.
    """
    if not isinstance(rec, dict):
        return False
    d = rec.get("duration_seconds")
    return isinstance(d, (int, float)) and not isinstance(d, bool) and d == 0.0


def read_series(path: Path | None = None, limit: int | None = None,
                include_fixture_rows: bool = False) -> list[dict]:
    """Read the duration series oldest-first. Corrupt lines are skipped, never fatal — this is a
    shared append-only surface with concurrent writers (CLAUDE.md), so one bad line must not blind
    the measure. Missing file → empty list, which upstream renders RED rather than green.

    Fixture rows (§`is_fixture_row`) are dropped by default, so every reader — the reported line,
    the trend, the band the next record inherits and the alarm's `previous` — sees measurements
    only. `include_fixture_rows=True` returns the file as written, which is how `note_line()`
    counts what it excluded and how a future audit can inspect the contamination without
    re-parsing the file itself.

    `limit` is applied AFTER the exclusion: "the last 5 runs" must mean five measured runs, not
    five lines two of which are fixtures.
    """
    p = path or SERIES_PATH
    rows: list[dict] = []
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return rows
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict):
            if not include_fixture_rows and is_fixture_row(rec):
                continue
            rows.append(rec)
    return rows[-limit:] if limit else rows


def record(duration_seconds, ceiling_seconds, git_hash: str, outcome: str,
           path: Path | None = None) -> dict:
    """Append one gate run to the series and return the record.

    Stores the raw duration AND the raw ceiling alongside the derived ratio, so the ratio can be
    re-derived by an independent reader and a ceiling change stays visible in the history.

    RAISES `LiveLedgerWriteUnderTest` when a test process aims this at the live series — BEFORE
    any work, so the refusal cannot be mistaken for a write that half-happened. A test that
    genuinely needs to exercise this passes `path=tmp_path / "series.jsonl"`, which every existing
    test in `test_suite_duration_watch.py` already does. `record_gate_run` swallows the refusal,
    per its own never-raise contract.
    """
    p = guard_live_ledger_write(path or SERIES_PATH, writer="suite_duration_watch.record")
    h = headroom(duration_seconds, ceiling_seconds)
    prev = read_series(path)
    prev_band = band(prev[-1].get("headroom_ratio"), None) if prev else None
    rec = {
        "timestamp": _now_iso(),
        "git_hash": git_hash,
        "duration_seconds": round(float(duration_seconds), 2)
        if isinstance(duration_seconds, (int, float)) and math.isfinite(float(duration_seconds))
        else None,
        "ceiling_seconds": ceiling_seconds,
        "headroom_ratio": round(h, 4) if h is not None else None,
        "band": band(h, prev_band),
        # The absolute verdict is STORED, not only alarmed: 5,570 rows of history exist and every
        # one of them can be asked this question retroactively, but only if the answer is on the
        # row. `cadence_seconds` rides along for the same reason `ceiling_seconds` does — if the
        # measured cadence is ever re-derived, the old rows must not silently change meaning.
        "cadence_band": row_cadence_band({"duration_seconds": duration_seconds,
                                          "outcome": outcome}),
        "cadence_seconds": PUBLISH_CADENCE_SECONDS,
        "outcome": outcome,
    }
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except OSError:
        pass
    return rec


def _pct(h) -> str:
    return "{:.0f}%".format(h * 100)


def note_line(path: Path | None = None) -> str:
    """One line for a surface that is read (the daily self-note).

    RED when the series is missing or the latest run is unmeasurable — an absent measurement is
    reported as absent, never as headroom."""
    rows = read_series(path)
    excluded = len(read_series(path, include_fixture_rows=True)) - len(rows)
    if not rows:
        return ("🔴 RED — suite headroom unmeasured: no publish-gate duration recorded yet "
                "(fail-closed, not a green — R15). One appears after the next gate run."
                + _exclusion_fragment(excluded))
    latest = rows[-1]
    h = latest.get("headroom_ratio")
    if h is None:
        return ("🔴 RED — latest publish-gate run recorded no usable duration "
                f"(sha {str(latest.get('git_hash'))[:9]}, outcome {latest.get('outcome')}); "
                "headroom is unmeasurable, not zero (R15).")
    ceiling = latest.get("ceiling_seconds")
    trend = _trend_fragment(rows)
    icon = "🔴" if h < TIGHT_HEADROOM else "✅"
    return (f"{icon} suite headroom: **{_pct(h)}** of the publish gate's ceiling unused "
            f"({latest.get('duration_seconds')}s against a {ceiling}s wall, "
            f"sha {str(latest.get('git_hash'))[:9]}){trend}. "
            "R12: a DIAGNOSTIC — no test may be deselected or tiered to move it."
            + _absolute_fragment(latest)
            + _exclusion_fragment(excluded))


def _absolute_fragment(latest: dict) -> str:
    """The absolute number, on the same line as the ratio, because the ratio alone is what let a
    75-minute gate read as healthy. Silent only when unmeasurable — never silent on a green."""
    d = latest.get("duration_seconds")
    cadence = latest.get("cadence_seconds") or PUBLISH_CADENCE_SECONDS
    cur = latest.get("cadence_band") or row_cadence_band(latest)
    if cur == "unknown":
        # SILENCE HERE WAS THE FIRST DRAFT AND IT WAS WRONG. The rows that classify as unknown
        # are overwhelmingly the KILLED ones, so an absolute figure that simply vanishes goes
        # quiet at exactly the moment the gate is failing — the same shape as the ratio reading
        # healthy through six ceiling raises, one level down. Say what is not known and why.
        if latest.get("outcome") == "timeout":
            return (f" Absolute: UNMEASURED — this run was killed at {d}s against its "
                    f"{latest.get('ceiling_seconds')}s ceiling, so its true duration is a lower "
                    "bound, not a measurement. A censored run is not a fast one.")
        return " Absolute: unmeasured (no usable duration on the latest run)."
    if cur == "within_cadence":
        return f" Absolute: {d}s, inside the {cadence}s publish cadence."
    ratio = f"{d / cadence:.1f}x" if isinstance(d, (int, float)) and cadence else "?"
    return (f" 🔴 Absolute: {d}s is {ratio} the {cadence}s cadence this gate gates — a check "
            "slower than its own subject changes is reporting on the past. Not clearable by "
            "raising the ceiling (this figure never reads it).")


def _exclusion_fragment(excluded: int) -> str:
    """Say what the line dropped, or say nothing.

    A surface that silently excludes two thirds of its own input is the mirror of the defect this
    exclusion repairs — the reader cannot tell a clean series from a filtered one. Silent at zero
    so a healthy series does not carry a permanent footnote about a fixed problem.
    """
    if excluded <= 0:
        return ""
    return (f" ({excluded} zero-second row(s) excluded as test-process writes, not measurements; "
            "the source is refused at `record()` since 2026-08-20 — the rows already in the "
            "file are kept, not truncated.)")


def _trend_fragment(rows: list[dict]) -> str:
    """Latest headroom against the median of the prior window, as a direction — the point of the
    atom is the approach, not the arrival. Silent when there is no prior window to compare to."""
    prior = [r.get("headroom_ratio") for r in rows[:-1][-TREND_WINDOW:]]
    prior = [x for x in prior if isinstance(x, (int, float))]
    if not prior:
        return ""
    prior.sort()
    mid = prior[len(prior) // 2] if len(prior) % 2 else (prior[len(prior) // 2 - 1]
                                                         + prior[len(prior) // 2]) / 2
    h = rows[-1].get("headroom_ratio")
    delta = h - mid
    if abs(delta) < 0.02:
        return f", flat against the prior {len(prior)} run(s)"
    arrow = "shrinking" if delta < 0 else "growing"
    return f", {arrow} {abs(delta) * 100:.0f}pp against the median of the prior {len(prior)} run(s)"


def alarm(current: dict, previous: dict | None = None, *, notify_fn=None):
    """Fire the TREND TRANSITION (R5), and only that.

    Sends on a crossing INTO tight, and once on recovery OUT of tight. An unchanged band sends
    nothing — no periodic "still fine", no repeated "still tight". Returns the message sent, or
    None. `notify_fn` is injected for tests; the real one is `background.notify.notify`.
    """
    # A fixture row is not a state of the world, so it cannot be a transition in one. Without
    # this, a genuinely tight run followed by one test write (headroom_ratio 1.0) pages
    # "[SUITE HEADROOM] Recovered" on the director's channel — a recovery that did not happen,
    # sourced from a test. Both sides are checked: as the current record it must not page, and as
    # the `previous` it must not become the band a real crossing is measured against.
    if is_fixture_row(current):
        return None
    if is_fixture_row(previous):
        previous = None

    prev_band = previous.get("band") if isinstance(previous, dict) else None
    if prev_band not in ("tight", "ok"):
        prev_band = band(previous.get("headroom_ratio"), None) if isinstance(previous, dict) else None
    cur_band = current.get("band") or band(current.get("headroom_ratio"), prev_band)

    if cur_band == prev_band or cur_band == "unknown":
        return None
    if cur_band == "ok" and prev_band != "tight":
        return None  # a first-ever observation, or unknown -> ok: nothing has been crossed

    h = current.get("headroom_ratio")
    sha = str(current.get("git_hash"))[:9]
    if cur_band == "tight":
        msg = (f"[SUITE HEADROOM] The publish gate's suite now uses "
               f"{_pct(1 - h) if h is not None else '?'} of its "
               f"{current.get('ceiling_seconds')}s wall — headroom down to {_pct(h)} at {sha}. "
               "Raise the ceiling from a fresh measurement, or make the machine faster. "
               "R12: do NOT deselect, mark slow, or re-tier tests to move this number.")
    else:
        msg = (f"[SUITE HEADROOM] Recovered: headroom back to {_pct(h)} of the "
               f"{current.get('ceiling_seconds')}s wall at {sha}.")

    send = notify_fn
    if send is None:
        from background.notify import notify as send
    send(msg, kind="real_alarm", transition_key="suite_duration_headroom", state=cur_band)
    return msg


def absolute_alarm(current: dict, previous: dict | None = None, *, notify_fn=None):
    """Fire on crossing the CADENCE, on its own transition key, independent of the headroom band.

    Two alarms rather than one branch inside `alarm()`, because they answer different questions
    and must be able to disagree: the run that reads "72% headroom, ok" is the SAME run that is
    four times slower than the cadence it gates. Folding this into the headroom transition would
    let a ceiling raise — which flips the headroom band to ok — suppress it, which is the exact
    silencing this figure exists to be immune to.

    R5, matching `alarm()`: once on the crossing, once on the recovery, nothing on an unchanged
    band. A first-ever `within_cadence` has crossed nothing and sends nothing; a first-ever
    `over_cadence` DOES send, because the bad direction being the initial state is the case this
    was built in — it is crossed today.
    """
    if is_fixture_row(current):
        return None
    if is_fixture_row(previous):
        previous = None

    cur = current.get("cadence_band") or row_cadence_band(current)
    prev = None
    if isinstance(previous, dict):
        prev = previous.get("cadence_band") or row_cadence_band(previous)
    if prev == "unknown":
        prev = None

    if cur == "unknown" or cur == prev:
        return None
    if cur == "within_cadence" and prev != "over_cadence":
        return None

    d = current.get("duration_seconds")
    sha = str(current.get("git_hash"))[:9]
    cadence = current.get("cadence_seconds") or PUBLISH_CADENCE_SECONDS
    if cur == "over_cadence":
        ratio = (f"{d / cadence:.1f}x" if isinstance(d, (int, float)) and cadence else "?")
        msg = (f"[GATE ABSOLUTE] The publish gate took {d}s — {ratio} the {cadence}s cadence it "
               f"gates, at {sha}. A check slower than the interval between the runs it checks is "
               "reporting on the past, not verifying the present. This figure does NOT read the "
               "ceiling, so raising the ceiling cannot clear it. R12/R15: it clears by deciding "
               "what genuinely must run before a publish — never by deselecting tests, and never "
               "by moving a bound.")
    else:
        msg = (f"[GATE ABSOLUTE] Recovered: the publish gate took {d}s, inside the {cadence}s "
               f"cadence it gates, at {sha}.")

    send = notify_fn
    if send is None:
        from background.notify import notify as send
    send(msg, kind="real_alarm", transition_key="publish_gate_absolute_duration", state=cur)
    return msg


def record_gate_run(duration_seconds, ceiling_seconds, git_hash: str, outcome: str,
                    path: Path | None = None):
    """The publish path's single entry point: record, then alarm on a transition.

    NEVER RAISES. An observer that can red the gate it observes is itself a defect, so every
    failure here degrades to "no measurement this cycle" and the publish continues."""
    try:
        prev_rows = read_series(path)
        rec = record(duration_seconds, ceiling_seconds, git_hash, outcome, path)
        prev = prev_rows[-1] if prev_rows else None
        alarm(rec, prev)
        absolute_alarm(rec, prev)
        return rec
    except Exception:  # noqa: BLE001 — see docstring; never raise into the publish path
        return None


def main() -> int:
    """`python3 -m background.suite_duration_watch` — print the reported line."""
    print(note_line())
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/suite_duration_watch.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("suite_duration_watch")
    raise SystemExit(main())
