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
# 15 isn't verifying the current state, it's reporting on the past."* So the reference is HOW
# OFTEN RUNS ACTUALLY ARRIVE, which is a fact about the world and not a budget anyone can raise.
#
# AND IT IS NOT THE PUBLISH CADENCE, WHICH IS A DIFFERENT QUANTITY WITH A DIFFERENT HOME
# ─────────────────────────────────────────────────────────────────────────────────────────
# RENAMED 2026-09-21, from `PUBLISH_CADENCE_SECONDS`, and the rename IS the repair.
#
# Until today this constant and `publish_freshness.PUBLISH_CADENCE_SECONDS` carried the same
# name, 112x apart — 5,400 here against 604,800 there — and stamped the same field name,
# `cadence_seconds`, into two different artefacts. That is the VAT-rule class CLAUDE.md names:
# one word, several implementations, and nothing able to notice. It went load-bearing rather
# than cosmetic when `tools/settlement_ceiling_probe` reached this number by a second route
# nobody re-asked, and priced the settlement ceiling on it.
#
# THE TWO QUANTITIES, said plainly, because the split is what the name was hiding:
#
#   THE DECLARED PUBLISH CADENCE — a DECISION. The director's, stated 2026-09-04: *"The site
#     publishes numbers and runs once a week."* It does not move when our runs get slower; it
#     moves when he changes his mind. Its single home is `publish_freshness`, which says so.
#   THE MEASURED RUN ARRIVAL INTERVAL — an OBSERVATION. This constant. Nobody chose 5,400s;
#     it is the median gap between `run_complete_*` markers, and it has moved 330 → 1500 → 5400
#     purely because the book grew and runs got slower.
#
# A DECISION AND AN OBSERVATION OF THE SAME SUBJECT ARE STILL TWO QUANTITIES, and this one is
# the one that is USELESS AS A BOUND ON ANYTHING THE RUN CONTROLS: run duration sets marker
# inter-arrival, so any ceiling argued "against the cadence" using THIS number grows when the
# ceiling grows. It is legitimate here, and only here, because this module asks the one question
# the circularity does not spoil — is the GATE slower than the runs it gates — where both sides
# are observations and neither is a budget.
#
# WHAT WAS DELIBERATELY NOT RENAMED, and why. `absolute_band()` still returns `over_cadence` /
# `within_cadence`, and `record()` still writes `cadence_band`. Those strings are STORED on
# 5,570 rows of history; renaming them would silently change what every historical row says,
# which is the opposite of the repair. The band vocabulary is this module's local word for its
# own comparison. The NUMBER is what a foreign reader picked up and mistook, so the number is
# what got an unmistakable name.
#
# MEASURED, not assumed. RE-MEASURED 2026-08-26, and the re-measurement is the point.
#
# The original figure: median inter-arrival of the last 200 `run_complete_*` markers = 334s
# (p10 324s, p90 435s) over 970 markers spanning 2026-08-09 → 2026-08-21, rounded DOWN to 330
# so the bound was never softer than the observation. That was correct for the world it was
# taken in.
#
# The world moved 7.7x and the constant did not. Measured over all 1,196 markers on disk:
#
#     2026-08-09 .. 08-21   n=1039   median   344s   <- the window 330 was taken from
#     2026-08-22 .. 08-24   n=  98   median 1,528s
#     2026-08-25 .. 08-26   n=  50   median 2,637s
#
# The book grew roughly sixfold over that period, so each run takes far longer and markers
# arrive far apart. Against a live gate median of 526s, `cadence_band` therefore returned
# `over_cadence` on 30 of the last 30 publish-gate runs — a control firing every single time,
# which carries exactly as much information as one that never fires.
#
# THIS RAISE IS THE MOVE THE PARAGRAPH ABOVE WARNS ABOUT, and it is being made anyway, so the
# distinction has to be stated rather than assumed. What that paragraph forbids is raising a
# BUDGET to fit the work: six ceiling raises made the same runtime read as more headroom, and
# `absolute_band()` cannot even be passed a ceiling so the move is structurally unavailable.
# This is not that. `MEASURED_RUN_ARRIVAL_SECONDS` is not a budget anyone chose; it is a measurement
# of how often runs actually arrive, and a measurement that no longer matches the world is
# simply wrong. Re-measuring it is the same act as re-freezing the ruff baseline after a real
# shrink — and like that ratchet, the move is DATED, its window is named, and the evidence is
# reproducible by `measure_run_arrival_seconds()` below rather than asserted here.
#
# THE DIRECTION IS THE UNCOMFORTABLE ONE and a reader should weigh it as such: this makes the
# alarm quieter. It is defensible only because the alarm was wrong 30 times out of 30, and a
# control at 100% false positives trains the reader to skim it — which is how the tree-divergence
# breach survived six days at 29x. An always-firing control and a never-firing one fail the same
# way. If runs get fast again, this number must come back DOWN, and the log line below is where
# that will be recorded.
#
# CADENCE LOG — every move, with its window and its direction.
#   2026-08-26  330 -> 1500  (re-measured; runs got slower as the book grew ~6x)
#     SAME METHOD AS THE ORIGINAL, deliberately: the median over the LAST 200 markers, which is
#     1,526s, rounded DOWN to 1500 so the bound is never softer than the observation.
#     A first attempt used 2400, taken from the 2026-08-25..08-26 slice alone (median 2,637s).
#     That slice is real but it is a different method from the one this constant was defined by,
#     and 2400 was SOFTER than the 200-marker observation — i.e. it broke the very rounding rule
#     it cited. Caught by `measure_run_arrival_seconds()` before it landed, which is the
#     argument for the helper existing at all.
#   2026-09-17  1500 -> 5400  (re-measured; runs slowed again, by a further ~3.6x)
#     SAME METHOD AGAIN: median over the LAST 200 markers = 5,445s (n=189 usable gaps, p10 784s,
#     p90 6,924s), window 2026-09-02T20:26 .. 2026-09-17T07:22, rounded DOWN to 5400 so the bound
#     is never softer than the observation. Sliced, the drift is monotone and not one bad day:
#       2026-08-26 .. 09-05  n=350  median 1,676s   <- the window 1500 was taken from
#       2026-09-05 .. 09-12  n= 83  median 6,676s
#       2026-09-12 .. 09-18  n= 25  median 6,827s
#     THE UNCOMFORTABLE DIRECTION, AGAIN, and the paragraph above applies unchanged: this makes
#     the alarm quieter for the second time. What makes it a re-measurement rather than a budget
#     raise is also unchanged -- the method was fixed before the answer was known, the window is
#     named, and `measure_run_arrival_seconds()` reproduces it. What a reader must NOT
#     conclude is that runs getting slower is FINE. This constant describes the world; a second
#     ~3.6x slowdown in three weeks is a finding ABOUT THE MACHINE, and moving the number records
#     it rather than answers it. It is written here because this is where it was noticed.
#     NOT TAKEN FROM THE SLICE. The last two slices alone would justify ~6,600s -- which is the
#     exact error the 2400 attempt made above: a different method from the one this constant is
#     defined by, and softer than the 200-marker observation.
MEASURED_RUN_ARRIVAL_SECONDS = 5400


def cadence_measurement_subject(markers_dir=None):
    """WHOSE marker set the cadence is measured from — `(roots, reason)`, exactly one non-None.

    THE SUBJECT HAS TO BE NAMED BECAUSE IT IS NOT ALWAYS THE MACHINE. `PROJECT_DIR` is the tree
    this module was imported FROM, and the publish gate imports it from a `git archive HEAD`
    throwaway checkout (`process_run_complete._head_checkout`, director ruling
    DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09). In that tree `docs/staging/done/` holds
    only the markers that happen to be COMMITTED — a lagging snapshot, not the live series.

    MEASURED 2026-09-03, the wedge this fixes. The working tree held 1,470 markers (newest
    21:28:50Z) and measured a 1,685.5s median; the gate's checkout of the same HEAD held 1,305
    (newest 17:55:42Z, ~3.5h stale) and measured 3,009s. `MEASURED_RUN_ARRIVAL_SECONDS` was
    re-measured on 2026-08-26 from the WORKING tree, so the gate was grading a constant
    calibrated on one population against a different one, and failed it by 4.5 seconds:
    `1500 >= 3009 * 0.5` is `1500 >= 1504.5`. Four consecutive publish-gate failures, all
    publishing blocked, on a control whose two sides were never the same series.

    So this is the `process_run_complete._machine_data_dir()` doctrine — "the MAIN worktree,
    never the importing tree" — applied to the one data set that helper does not cover. Where
    the tree belongs to this repository, a linked worktree resolves to the main tree and the
    measurement is the machine's. Where it does not, the answer is a REFUSAL WITH A NAMED REASON
    rather than a confident number taken off a stale snapshot.

    THERE ARE TWO THROWAWAY SHAPES AND THE FIRST FIX ONLY CAUGHT ONE — recorded because the
    second one refused the very commit that landed the first. `process_run_complete` builds its
    subject with `git archive HEAD`, which is not a git repository at all; `tools/surgical_land`
    builds its subject with `git archive` AND THEN `git init` (`_make_standalone_repo`, so that
    tests asking git a question get an answer), which IS one. A guard keying on "is this a git
    repo" therefore refuses the publish gate and sails straight into the landing gate — measured,
    on this change's own first landing attempt: `1500 >= 3009.0 * 0.5`, the identical failure.

    The property that actually separates them is OWNERSHIP, not repo-ness: a throwaway checkout
    is standalone and has no `origin`, while the live tree and every linked worktree share this
    repository's config and do. Verified on all four shapes on 2026-09-03 — main tree and both
    `/var/tmp/se-*` worktrees carry `origin` and resolve to `/home/rich/synthetic-enterprise`;
    the `git init` checkout carries none; the `git archive` extract is not a repo.

    An explicit `markers_dir` is always honoured: a caller naming its own subject has already
    answered the question this helper exists to ask.
    """
    import pathlib as _pathlib
    import subprocess as _subprocess

    if markers_dir:
        return [_pathlib.Path(markers_dir)], None

    def _git(*args):
        try:
            proc = _subprocess.run(["git", *args], cwd=str(PROJECT_DIR),
                                   capture_output=True, text=True, timeout=30)
        except (OSError, _subprocess.SubprocessError):
            return ""
        return (proc.stdout or "").strip() if proc.returncode == 0 else ""

    common = _git("rev-parse", "--path-format=absolute", "--git-common-dir")
    if not common:
        return None, (
            "{} is not a git repository, so it is a throwaway checkout whose `docs/staging/` is "
            "a committed snapshot rather than the machine's live marker series — the publish "
            "cadence is not observable from here".format(PROJECT_DIR))
    if not _git("config", "--get", "remote.origin.url"):
        return None, (
            "{} is a standalone git repository with no `origin`, so it is a throwaway gate "
            "checkout rather than a worktree of this repository, and its `docs/staging/` is a "
            "committed snapshot rather than the machine's live marker series".format(PROJECT_DIR))
    main_worktree = _pathlib.Path(common).parent
    if not main_worktree.is_dir():
        return None, "git named {} as the main worktree and it is not a directory".format(
            main_worktree)
    return [main_worktree / "docs" / "staging" / "done",
            main_worktree / "docs" / "staging"], None


def measure_run_arrival_seconds(markers_dir=None, window: int = 200):
    """Re-measure the RUN ARRIVAL INTERVAL from the `run_complete_*` markers on disk.

    THE EVIDENCE FOR `MEASURED_RUN_ARRIVAL_SECONDS`, callable rather than quoted. The constant above
    is a claim about the world, and a claim about the world that nobody can re-run is a claim
    that goes stale silently — which is exactly what happened between 2026-08-21 and today.

    Returns the median inter-arrival in seconds over the last `window` markers, or None when
    there are fewer than three usable gaps OR when the tree cannot see the machine's marker
    series at all (`cadence_measurement_subject` above carries that reason). Gaps above two
    hours are dropped as run outages rather than cadence, the same shape as the original
    measurement's own bounds.

    NOT wired into the constant on purpose. A cadence that recomputed itself every call would
    drift upward silently, which is the silencing move in a slower costume: the number has to
    MOVE IN A COMMIT, with a dated log line and a reader able to disagree.
    """
    import datetime as _dt
    import re as _re
    import statistics as _statistics

    roots, _reason = cadence_measurement_subject(markers_dir)
    if roots is None:
        return None
    stamps = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.glob("run_complete_*.md"):
            hit = _re.search(r"run_complete_(\d{8}T\d{6}Z)", path.name)
            if hit:
                stamps.append(_dt.datetime.strptime(hit.group(1), "%Y%m%dT%H%M%SZ"))
    stamps = sorted(set(stamps))[-window:]
    gaps = [(b - a).total_seconds() for a, b in zip(stamps, stamps[1:])
            if 0 < (b - a).total_seconds() < 7200]
    return _statistics.median(gaps) if len(gaps) >= 3 else None

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
    """Classify a raw runtime against the MEASURED RUN ARRIVAL INTERVAL: over_cadence /
    within_cadence / unknown. (The band names are this module's own vocabulary and are stored on
    5,570 historical rows; they are NOT a claim about the declared publish cadence.)

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
    return "over_cadence" if d > MEASURED_RUN_ARRIVAL_SECONDS else "within_cadence"


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


# A real gate run starts an interpreter, imports the suite and COLLECTS several thousand tests
# before it can time anything. The measured floor across all 374 rows the publisher has ever
# written is 3.46s. One second is therefore comfortably below any real run and comfortably above
# every fixture that writes a token duration — which is the property the rule needs, in both
# directions. Kept as a named constant so the number that defines "impossible" is auditable
# rather than buried in a comparison.
IMPOSSIBLE_GATE_SECONDS = 1.0


def is_fixture_row(rec) -> bool:
    """True for a row whose duration is impossible for a real gate run — i.e. not a measurement.

    `== 0.0` WAS FAIL-OPEN, AND THE FILE PROVES IT (2026-08-21). The previous rule tested for
    exactly zero, justified by "unreachable for any real run and reached by every test one". The
    first half is true; the second half was never true. Classifying the live series by the shape
    of the sha the writer passed:

        named fixtures (`deadbeef`/`abc1234`)   3,617 rows   — caught by `== 0.0`
        full 40-char shas                       1,579 rows   — median 0.02s, NOT caught
        short 9-char shas (the publisher)         374 rows   — min 3.46s, every one >= 1s

    So of the 2,126 rows the old rule ADMITTED as measurements, 1,579 — **74%** — were test
    writes that happened to pass a small non-zero duration (0.01s, 0.02s, 0.11s) instead of a
    literal zero. Every reader downstream (the reported line, the trend, the band the next record
    inherits, the alarm's `previous`) was looking at a series three quarters of which was
    fixtures, and `note_line` told the reader it had excluded 3,444 rows when the true
    contamination was 5,023. A control that under-reports its own blind spot by 1,579 rows is the
    R15 FAIL-OPEN pattern exactly: it passes on the malformed input it exists to catch.

    STILL NOT A git_hash DENYLIST, and now not a single magic value either. The subject remains
    the impossible VALUE — every present and future fixture that writes a token duration shares
    it — but the threshold is a floor rather than a point, because a point rule only ever catches
    fixtures that chose that exact point. Sha SHAPE was considered and rejected: it would read as
    "fixture" every real row the day the publisher switches to full hashes, which fails CLOSED on
    real measurements and would hide the very numbers this series exists to keep.

    HONEST LIMIT, STATED IN FULL because a control that rounds its own blind spot down is the
    defect above wearing a different hat. The rule excludes 5,100 of 5,570 rows and admits 470,
    of which **96 are still not measurements**: 13 full-sha rows carrying 1–162.64s, and 83
    `deadbeef`/`abc1234` rows carrying 2.42–3.3s. A duration that plausible is indistinguishable
    from a measurement BY VALUE, and raising the floor to swallow them would be fitting the
    threshold to today's sample at the cost of eating a genuinely fast run. They stay admitted
    and this rule does not claim them. The residue is bounded and CLOSED: `record()` has refused
    test-process writes since 2026-08-20, so 96 is a final count, not a running one. This rule is
    for the history already on disk, which is untracked and cannot be re-derived.

    `bool` is excluded explicitly because `True == 1.0` is False but `False == 0.0` is True in
    Python, and a `False` in this field is malformed data, not a zero measurement.
    """
    if not isinstance(rec, dict):
        return False
    d = rec.get("duration_seconds")
    return (isinstance(d, (int, float)) and not isinstance(d, bool)
            and 0.0 <= d < IMPOSSIBLE_GATE_SECONDS)


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
           path: Path | None = None, chains=None) -> dict:
    """Append one gate run to the series and return the record.

    Stores the raw duration AND the raw ceiling alongside the derived ratio, so the ratio can be
    re-derived by an independent reader and a ceiling change stays visible in the history.

    `chains` IS THE ROW'S UNIT, AND WITHOUT IT ON THE ROW NO READER CAN ASK (2026-09-17). The
    caller divides a multi-chain stopwatch down to a per-chain cost before it gets here — it is
    the only place that knows the count — and until now that count was DISCARDED at this call.
    So the repair that began dividing correctly could not be told apart, by any consumer, from
    the nine days of totals it replaced: every row in `commit_hook_duration.jsonl` reads
    identically whether its unit was stated or inferred, and 0 of 195 carry a count. A silent
    row is exactly the shape that wedged the shared tree — `666.95s`, two chains of ~333s read
    as one, refusing every commit including the liveness heartbeat. Stating the unit is the
    same discipline as the paragraph below: an answer the producer knew, written onto the row
    rather than dropped, so the question can be asked of history and not only of new rows.

    `None` means UNSTATED, not one. A caller that says nothing has not claimed its row is a
    single chain — the publisher's scoped-gate series, where a run is one run, simply never had
    a count to give. Reading an absent field as `1` is the inference that produced the wedge.

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
        # row. The arrival interval rides along for the same reason `ceiling_seconds` does — if it
        # is ever re-measured, the old rows must not silently change meaning.
        "cadence_band": row_cadence_band({"duration_seconds": duration_seconds,
                                          "outcome": outcome}),
        # RENAMED 2026-09-21 from `cadence_seconds`, and this key is the one that did the damage.
        # `publish_freshness.snapshot()` writes a field ALSO called `cadence_seconds`, carrying
        # the DECLARED weekly cadence — so two artefacts in this tree published one field name
        # over two quantities 112x apart. `settlement_ceiling_probe.publisher_context()` read
        # THIS one, out of `publish_gate_duration.jsonl`, and spent it as the publish interval
        # the settlement ceiling is priced against. Nothing was lying; the name was.
        "measured_arrival_seconds": MEASURED_RUN_ARRIVAL_SECONDS,
        "outcome": outcome,
        # The KEY is always present so a reader can tell "stated 1" from "said nothing"; the
        # VALUE is None unless the caller gave a positive int, because a bad count is an
        # unstated unit and not a claim of one chain.
        "chains": chains
        if isinstance(chains, int) and not isinstance(chains, bool) and chains > 0
        else None,
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


def row_arrival_seconds(row) -> float:
    """The arrival interval a STORED row was written against, new key first, legacy key second.

    THE LEGACY KEY IS DATA, NOT CODE, and that is the whole reason this fallback is honest where
    a fallback usually is not. 5,570 rows on disk were written before 2026-09-21 and carry
    `cadence_seconds`; they recorded the interval correctly under a name that turned out to be
    ambiguous. Rewriting history to fix a name would destroy the one property the key exists for
    — that a re-measurement must not silently change what an old row says.

    So the fallback has an END: no writer in this module emits `cadence_seconds` any more, so the
    legacy branch is reachable only by rows older than the rename and can never be reached by a
    row written from here again. It is not a compatibility shim for two live spellings.

    RETURNED AS STORED, not coerced. These values are interpolated straight into the alarm the
    director reads, so `float()` here turns "the 330s interval" into "the 330.0s interval" on
    every historical row — a cosmetic-looking change to a line whose whole job is to be read.
    """
    if not isinstance(row, dict):
        return MEASURED_RUN_ARRIVAL_SECONDS
    for key in ("measured_arrival_seconds", "cadence_seconds"):
        v = row.get(key)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0:
            return v
    return MEASURED_RUN_ARRIVAL_SECONDS


def _absolute_fragment(latest: dict) -> str:
    """The absolute number, on the same line as the ratio, because the ratio alone is what let a
    75-minute gate read as healthy. Silent only when unmeasurable — never silent on a green."""
    d = latest.get("duration_seconds")
    cadence = row_arrival_seconds(latest)
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
        return f" Absolute: {d}s, inside the {cadence}s measured run arrival interval."
    ratio = f"{d / cadence:.1f}x" if isinstance(d, (int, float)) and cadence else "?"
    return (f" 🔴 Absolute: {d}s is {ratio} the {cadence}s interval between the runs this "
            f"gate gates — a check "
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
    # "zero-second" NAMED THE OLD RULE, NOT THE ROWS (2026-08-21). While the filter tested
    # `== 0.0` the two agreed; the moment it became a sub-second FLOOR, a line still saying
    # "zero-second" would under-describe its own exclusions by the 1,579 rows that made the
    # floor necessary — the same under-reporting, one layer out. The fragment now describes
    # the rule that is actually running.
    return (f" ({excluded} sub-second row(s) excluded as test-process writes, not measurements — "
            f"under {IMPOSSIBLE_GATE_SECONDS:g}s is impossible for a real gate run; the source "
            "is refused at `record()` since 2026-08-20 — the rows already in the file are kept, "
            "not truncated.)")


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
    cadence = row_arrival_seconds(current)
    if cur == "over_cadence":
        ratio = (f"{d / cadence:.1f}x" if isinstance(d, (int, float)) and cadence else "?")
        msg = (f"[GATE ABSOLUTE] The publish gate took {d}s — {ratio} the {cadence}s interval "
               f"between the runs it gates — "
               f"gates, at {sha}. A check slower than the interval between the runs it checks is "
               "reporting on the past, not verifying the present. This figure does NOT read the "
               "ceiling, so raising the ceiling cannot clear it. R12/R15: it clears by deciding "
               "what genuinely must run before a publish — never by deselecting tests, and never "
               "by moving a bound.")
    else:
        msg = (f"[GATE ABSOLUTE] Recovered: the publish gate took {d}s, inside the {cadence}s "
               f"interval between the runs it gates, at {sha}.")

    send = notify_fn
    if send is None:
        from background.notify import notify as send
    send(msg, kind="real_alarm", transition_key="publish_gate_absolute_duration", state=cur)
    return msg


def record_gate_run(duration_seconds, ceiling_seconds, git_hash: str, outcome: str,
                    path: Path | None = None, chains=None):
    """The publish path's single entry point: record, then alarm on a transition.

    `chains` is forwarded verbatim to `record`, which documents why an absent count is UNSTATED
    rather than one. This entry point had no parameter for it, which is where the count the
    caller had already computed was being dropped.

    NEVER RAISES. An observer that can red the gate it observes is itself a defect, so every
    failure here degrades to "no measurement this cycle" and the publish continues."""
    try:
        prev_rows = read_series(path)
        rec = record(duration_seconds, ceiling_seconds, git_hash, outcome, path, chains=chains)
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
