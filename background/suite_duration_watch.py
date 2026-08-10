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
"""
from __future__ import annotations

import datetime
import json
import math
from pathlib import Path

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


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read_series(path: Path | None = None, limit: int | None = None) -> list[dict]:
    """Read the duration series oldest-first. Corrupt lines are skipped, never fatal — this is a
    shared append-only surface with concurrent writers (CLAUDE.md), so one bad line must not blind
    the measure. Missing file → empty list, which upstream renders RED rather than green."""
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
            rows.append(rec)
    return rows[-limit:] if limit else rows


def record(duration_seconds, ceiling_seconds, git_hash: str, outcome: str,
           path: Path | None = None) -> dict:
    """Append one gate run to the series and return the record.

    Stores the raw duration AND the raw ceiling alongside the derived ratio, so the ratio can be
    re-derived by an independent reader and a ceiling change stays visible in the history.
    """
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
        "outcome": outcome,
    }
    p = path or SERIES_PATH
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
    if not rows:
        return ("🔴 RED — suite headroom unmeasured: no publish-gate duration recorded yet "
                "(fail-closed, not a green — R15). One appears after the next gate run.")
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
            "R12: a DIAGNOSTIC — no test may be deselected or tiered to move it.")


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


def record_gate_run(duration_seconds, ceiling_seconds, git_hash: str, outcome: str,
                    path: Path | None = None):
    """The publish path's single entry point: record, then alarm on a transition.

    NEVER RAISES. An observer that can red the gate it observes is itself a defect, so every
    failure here degrades to "no measurement this cycle" and the publish continues."""
    try:
        prev_rows = read_series(path)
        rec = record(duration_seconds, ceiling_seconds, git_hash, outcome, path)
        alarm(rec, prev_rows[-1] if prev_rows else None)
        return rec
    except Exception:  # noqa: BLE001 — see docstring; never raise into the publish path
        return None


def main() -> int:
    """`python3 -m background.suite_duration_watch` — print the reported line."""
    print(note_line())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
