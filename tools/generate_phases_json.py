#!/usr/bin/env python3
"""Generate site/data/phases.json from docs/PROJECT_OVERVIEW.md Section 4.

Replaces the previously hand-curated site/data/phases.json (last hand-edited
2026-07-03, frozen at latest_phase OL while the real build had moved
dozens of phases on) -- a direct R-A violation (nothing hand-written on
these surfaces, if a fact cannot be generated it does not appear,
PROJECT_TAB_OVERHAUL.md) flagged as remaining scope by Phase QW.

Every Phase header in Section 4 is one build-history entry (new entries
are always prepended at the top, per the phase-close checklist, so file
order is newest-first). Entries with no parseable date (the earliest,
pre-QW-era headers) still count toward total_phases but are honestly
excluded from the date-indexed series -- fabricating a date would violate
the same rule this generator exists to uphold. A header naming a phase
range or a split phase counts once, not per sub-phase -- a known
simplification, not an attempt at precise historical phase numbering.
"""
import re
import subprocess
import sys
import json
from pathlib import Path as _P

PROJECT = _P(__file__).resolve().parent.parent
PROJECT_OVERVIEW = PROJECT / "docs" / "PROJECT_OVERVIEW.md"
OUT_PATH = PROJECT / "site" / "data" / "phases.json"


def _total_commits():
    try:
        out = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=str(PROJECT), capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0:
            return int(out.stdout.strip())
    except Exception:
        pass
    return None


_LOG_DATE_RE = re.compile(r"^\d\d\d\d-\d\d-\d\d$")


def cumulative_commits_by_day(log_lines):
    """[date, cumulative_count] pairs from `git log --format=%ad --date=short`
    output (one date per line, newest-first) -- a genuinely cumulative
    metric (2026-07-10, director page comment: "I want to pick metrics, such
    as cumulative ones that show the growth we creating" -- a 4th repeat of
    the "these graphs look flat/decelerating" complaint). Unlike test-SUITE
    SIZE, which necessarily looks like deceleration once a large total makes
    each new addition a smaller relative share, real commit activity has
    stayed high and roughly constant across this project's whole history
    (60-400+ commits/day, every day) -- a running total of it climbs
    steadily with no flat stretches, because it counts ongoing WORK, not a
    saturating total.

    Only well-formed YYYY-MM-DD lines are counted (2026-07-29 G1 HARDEN): any
    other token reaching this function becomes its own bucket in `counts`,
    where it sorts as a string alongside real dates and publishes a garbage
    x-axis point on a chart whose entire claim is a clean cumulative curve.
    A non-date contributes nothing rather than a fabricated date, exactly as
    a malformed record is skipped in the sibling half
    (test_execution_metric.cumulative_tests_executed).
    """
    from collections import Counter
    counts = Counter(
        line.strip() for line in log_lines if _LOG_DATE_RE.match(line.strip())
    )
    running = 0
    result = []
    for date in sorted(counts):
        running += counts[date]
        result.append([date, running])
    return result


def _valid_commit_total(value):
    """A published commit total is usable only if it is a real non-negative
    int. `bool` is an int subclass and `json.loads` accepts a bare `NaN`
    literal into a float -- both would sail through a naive `is not None`
    check and then lose every `<` comparison below (NaN comparisons are all
    False), turning the monotonic guard into a no-op (R15 fail-open)."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _series_last_value(series):
    """Final cumulative value of a [[date, count], ...] series, or None if the
    series is absent/empty/malformed. Shape is validated rather than assumed:
    the previous series is read back off disk, where anything could be."""
    if not isinstance(series, list) or not series:
        return None
    last = series[-1]
    if not isinstance(last, (list, tuple)) or len(last) != 2:
        return None
    return last[1] if _valid_commit_total(last[1]) else None


def _previously_published(path=None):
    """The last successfully published phases.json, or {} if there isn't one
    (first ever run) or it cannot be parsed."""
    target = path or OUT_PATH
    try:
        prev = json.loads(target.read_text())
    except Exception:
        return {}
    return prev if isinstance(prev, dict) else {}


_COUNT, _SERIES, _ROWS = "count", "series", "rows"

# Every MONOTONIC growth metric published in phases.json, and how to measure
# its size. This registry is the class-level closure of the retention rule
# below (R10: an absurdity-class defect may not be closed with an instance
# fix). A metric added to `generate()`'s payload without an entry here is
# simply unguarded -- so the registry is asserted against the real published
# keyset by test_every_published_growth_metric_is_registered, which fails when
# a future metric is added and left out.
#
# `companions` are non-metric fields derived from the SAME source read: when
# the metric is retained they must be retained with it, or the payload
# self-contradicts (e.g. total_phases held at 519 next to start_date: null).
_GROWTH_METRICS = (
    ("total_phases", _COUNT, ("start_date",)),
    ("cumulative_tests_executed", _COUNT, ("cumulative_tests_executed_since",)),
    ("test_progression", _SERIES, ()),
    ("phase_dates", _SERIES, ()),
    ("timeline", _ROWS, ()),
)


def _growth_magnitude(value, kind):
    """Comparable size of a published growth metric, or None if it is absent,
    malformed or empty. One definition of "how big is this metric" shared by
    the commits pair and the payload-wide sweep, so a metric cannot be guarded
    by one and missed by the other."""
    if kind == _COUNT:
        # Zero is treated as unmeasurable, not as a measurement of nothing --
        # consistent with the empty list below, and true of every metric in
        # the registry: the generator only runs at all once the project has
        # phases, commits and executed tests, so a published 0 is always the
        # collapsed-source failure mode, never a real state. Without this a
        # first-ever-run collapse publishes 0 labelled "measured" (fail-silent).
        return value if _valid_commit_total(value) and value > 0 else None
    if kind == _SERIES:
        return _series_last_value(value)
    if not isinstance(value, list) or not value:
        return None
    return len(value)


# What to publish when a metric is unmeasurable AND there is no prior to
# retain: honest emptiness, never the raw malformed measurement.
_EMPTY = {_COUNT: None, _SERIES: [], _ROWS: []}


def _retained_value(measured, previous, kind):
    """(value, retained) -- hold `previous` when the fresh measurement is
    missing/malformed or has gone BACKWARDS. The single retention primitive
    for this file's monotonic metrics."""
    measured_size = _growth_magnitude(measured, kind)
    previous_size = _growth_magnitude(previous, kind)
    if measured_size is None or (previous_size is not None and measured_size < previous_size):
        if previous_size is not None:
            return previous, True
        return (measured if measured_size is not None else _EMPTY[kind]), True
    return measured, False


def _retain_growth_metrics(data, previous):
    """Apply the retention rule to EVERY registered growth metric in a freshly
    built payload, returning {key: 'measured'|'retained_previous'|'unavailable'}.

    R15 hardening (2026-07-29, G1 HARDEN -- the CLASS audit of the guard added
    to the commits pair earlier the same day). That guard was correct and
    tested, but it was keyed to two of the six monotonic metrics `generate()`
    publishes. `generate()` swallows the PROJECT_OVERVIEW.md read exception and
    falls back to `text = ""` -- so one unreadable or mid-write-truncated
    source file (CLAUDE.md documents concurrent writers on this tree) publishes
    total_phases 519 -> 0, test_progression 17,214 -> [], phase_dates 468 -> 0
    and timeline -> [], while `commits_source` still reads "measured" and the
    publish reports success. Observed directly, not inferred: driving the real
    generate() with a non-existent PROJECT_OVERVIEW produced exactly that
    payload.

    That is the SAME two killer patterns the commits half was hardened for --
    FAIL-SILENT (an unavailable source reported as a clean publish) and
    FAIL-OPEN (empty passing straight through metrics whose entire declared
    property is monotonic growth) -- reached through a different source, on
    four MORE metrics, one of which (test_progression) is the very series whose
    16,358 -> 221 collapse the director reported. Guarding the class rather
    than the next instance is what makes this closure rather than a treadmill.
    """
    sources = {}
    for key, kind, companions in _GROWTH_METRICS:
        value, retained = _retained_value(data.get(key), previous.get(key), kind)
        data[key] = value
        if not retained:
            sources[key] = "measured"
            continue
        # Retained-with-nothing-to-retain is an unavailable metric, not a
        # successful publish of zero -- label it so no surface can read it
        # as fresh (the honesty half of the same rule).
        sources[key] = (
            "retained_previous" if _growth_magnitude(value, kind) is not None else "unavailable"
        )
        for companion in companions:
            if companion in previous:
                data[companion] = previous[companion]
    return sources


def _retained_commit_metrics(measured_total, measured_series, previous):
    """Hold the cumulative-commits metrics at their last published value when
    a fresh measurement is missing or has gone BACKWARDS. Returns
    (total, series, source) where source is 'measured', 'retained_previous'
    or 'unavailable'.

    R15 hardening (2026-07-29, G1 HARDEN -- the commits half of this atom's
    own guarantee, never previously red-teamed; the two test-count halves
    were hardened 2026-07-27). `_total_commits()` and
    `_commits_per_day_lines()` both swallow EVERY exception and fall back to
    None/[] -- a git timeout (10s/15s caps on a repo with thousands of
    commits, on a tree CLAUDE.md documents as having concurrent writers), a
    non-zero return code, or a detached/rewritten HEAD therefore publishes
    `total_commits: null` and `commits_by_day: []`. `generate()` runs inside
    the publish path (background/process_run_complete.py), so that lands on
    the live Project page, where `renderBuildStats()` gates on `if(commits)`
    and the "N commits" figure simply DISAPPEARS.

    That is both R15 killer patterns at once on the atom's named property:
    FAIL-SILENT (the source being unavailable is reported as a successful
    publish of nothing, not as a failure) and FAIL-OPEN (empty/None passes
    straight through the monotonic metric to the surface). It is the same
    single-day-collapse class the director reported on the test-count series
    (16,358 -> 221), except the collapse is all the way to zero.

    Retaining the previous PUBLISHED figure is not fabrication -- it is the
    most recent real measurement, and `commits_source` labels it as retained
    so no surface can present it as fresh. With no previous publish to fall
    back on we report 'unavailable' and publish nothing, rather than invent
    a number.

    2026-07-29 (class audit): the per-key comparison is now the shared
    `_retained_value` primitive, so the commits pair and every other monotonic
    metric in the payload are guarded by ONE mechanism rather than two that can
    drift apart. This function survives only to carry the commits pair's own
    three-state `commits_source` label, which predates the sweep and is read by
    the site.
    """
    total, total_retained = _retained_value(
        measured_total, previous.get("total_commits"), _COUNT)
    series, series_retained = _retained_value(
        measured_series, previous.get("commits_by_day"), _SERIES)

    if not (total_retained or series_retained):
        return total, series, "measured"
    if total is None and _series_last_value(series) is None:
        return total, series, "unavailable"
    return total, series, "retained_previous"


def _commits_per_day_lines():
    try:
        out = subprocess.run(
            ["git", "log", "--format=%ad", "--date=short"],
            cwd=str(PROJECT), capture_output=True, text=True, timeout=15,
        )
        if out.returncode == 0:
            return out.stdout.splitlines()
    except Exception:
        pass
    return []

sys.path.insert(0, str(PROJECT))
from tools.generate_project_state import _parse_phase_and_tests  # noqa: E402

# 2026-07-10: broadened after discovering (director page comment: Home
# chart "still looks decelerated") that this had silently stopped matching
# 38 of 496 real Section 4 entries -- every one written since the header
# convention drifted from "### Phase XY -- Title (date...)" to bare
# descriptive titles ("### Tenure archetype -- Layer 2 dimension 3
# (date...)") somewhere around 2026-07-08/09. Every entry this entire
# session (payment-method-mix, fuel-poverty, tenure, occupancy, the
# build-stamp fix, etc.) was invisible to phases.json's date-indexed
# series -- the chart wasn't lying about deceleration, it was reading
# stale data. Now matches ANY "### " header; the optional "Phase XY" code
# is still extracted when present (for the old convention and the
# timeline's "Phase " + phase_id fallback label), but is no longer
# required for an entry to count.
_HEADER_RE = re.compile(r"^### (.+)$")
_PHASE_CODE_RE = re.compile(r"^Phase\s+(\S+)\b")
_DATE_RE = re.compile(r"(\d\d\d\d-\d\d-\d\d)")
_TITLE_RE = re.compile(r"^### (?:Phase\s+\S+(?:\s*\([^)]*\))?\s*--\s*)?(.+)$")
_FINDING_RE = re.compile(r"KEY FINDING\b[^\n]*")

_TEST_COUNT_RES = [
    re.compile(r"\*\*Total:\*\*\s*(\d[\d,]*)\s*tests"),
    # 2026-07-10: broadened -- this session's own entries phrase it "N tests
    # collected" (the word "tests" between the number and "collected"),
    # which the original digit-then-"collected" pattern never matched,
    # silently contributing to the same stale-chart symptom as the header
    # and phase-code regex fixes above.
    re.compile(r"(\d[\d,]*)\s*tests?\s*collected"),
    re.compile(r"(\d[\d,]*)\s*collected"),
    re.compile(r"(\d[\d,]*)\s*tests?\s+passing"),
    re.compile(r"\((\d[\d,]*)\+?\s*total\)"),
]


def _extract_test_count(body):
    for rgx in _TEST_COUNT_RES:
        m = rgx.search(body)
        if m:
            return int(m.group(1).replace(",", ""))
    return None


def _extract_title(header):
    """Pull the human title out of a '### Phase X -- Title (date, ...)' header.

    The trailing '(...)' metadata block (date/tier/notes) is stripped only when
    it contains a date -- titles that legitimately contain their own
    parentheticals (e.g. '... (WEBSITE_AS_SHOWCASE.md Part 0 CLOSED) + ...')
    are left intact.
    """
    m = _TITLE_RE.match(header)
    if not m:
        return None
    rest = m.group(1)
    idx = rest.rfind("(")
    if idx != -1 and _DATE_RE.search(rest[idx:]):
        rest = rest[:idx]
    rest = rest.strip()
    return rest or None


def _extract_findings(body):
    """Return the free-text tail of every 'KEY FINDING ...' line in a phase body."""
    findings = []
    for m in _FINDING_RE.finditer(body):
        text = m.group(0)[len("KEY FINDING"):].lstrip()
        if text.startswith(":"):
            text = text[1:].lstrip()
        text = text.strip()
        if text:
            findings.append(text)
    return findings


def _iter_phase_entries(text):
    """Yield (phase_id, date, test_count, title, body) for every Section-4 header, file order."""
    lines = text.split("\n")
    header_idxs = []
    for i, line in enumerate(lines):
        if _HEADER_RE.match(line):
            header_idxs.append(i)
    for n, idx in enumerate(header_idxs):
        header = lines[idx]
        header_text = _HEADER_RE.match(header).group(1)
        code_m = _PHASE_CODE_RE.match(header_text)
        # Fall back to a synthetic, unique-by-position id ("H<n>") for
        # headers that don't carry an explicit "Phase XY" code -- still
        # counts toward total_phases/phase_dates, just has no short letter
        # tag (the timeline label falls back to the extracted title in
        # that case anyway, never to "Phase H37").
        phase_id = code_m.group(1) if code_m else "H%d" % n
        date_m = _DATE_RE.search(header)
        date = date_m.group(1) if date_m else None
        if n + 1 < len(header_idxs):
            end = header_idxs[n + 1]
        else:
            end = len(lines)
        body = "\n".join(lines[idx:end])
        yield phase_id, date, _extract_test_count(body), _extract_title(header), body


def _parse_build_history(text):
    return [(pid, date, tc) for pid, date, tc, _title, _body in _iter_phase_entries(text)]


def _monotonic_test_progression(chronological):
    """Build [date, test_count] pairs, refusing any candidate below the running
    max seen so far -- enforced in DATE order so the published series is
    monotonic no matter what order the caller passes entries in.

    Not every phase entry restates the true running full-suite total -- some
    (this session's own segmented-financials entry, e.g.) report a partial,
    test-file-scoped count ("221 tests passing across the two touched test
    files") with no full-suite figure anywhere in that entry's own body.
    _extract_test_count() has no way to know a matched number is scoped
    rather than authoritative, so it was accepted verbatim (2026-07-10) --
    producing a nonsensical single-day crash from 16,358 to 221 on the live
    Home page chart, a real director-reported regression. The real suite only
    grows over a project's history; refusing any candidate below the running
    max (rather than trying to solve "which phrasing is authoritative") fixes
    this class of bug directly, matching the same cumulative-running-max
    principle already applied to phase_dates on the client side.

    R15 hardening (2026-07-27, G1 HARDEN sibling-half red-team): the running
    max used to be applied in the CALLER'S iteration order (`chronological` =
    reversed file order of PROJECT_OVERVIEW.md), and the result then re-sorted
    by date for publishing. That made the monotonic-BY-DATE guarantee depend
    on an unenforced precondition -- that the hand-maintained, concurrently
    edited PROJECT_OVERVIEW.md Section 4 is in strict newest-first order. A
    single out-of-order entry (an inserted or restated phase) let an earlier
    date retain a HIGHER value than a later date, so the date-sorted output
    DECREASED between adjacent dates -- FAIL-OPEN (R15 killer pattern 2),
    silently re-opening the very single-day-drop regression this function
    exists to block. We now collapse each date to its highest reported count
    and apply the running max strictly in date order, so monotonicity is a
    property of the output itself, not of how the caller happened to order
    its input.
    """
    # Highest count reported for any given date (a later scoped/partial count
    # for a date never lowers an authoritative full-suite figure for it).
    max_by_date = {}
    for _phase_id, date, tc, _title, _body in chronological:
        if tc is None:
            continue
        # A dateless Section-4 header (no date parenthetical -> date is None)
        # can still carry a test count in its body, so _iter_phase_entries
        # yields (None, tc). It cannot be placed on a date-ordered timeline,
        # and left in `max_by_date` it makes `sorted(max_by_date)` below raise
        # TypeError ('<' not supported between NoneType and str), propagating
        # up through generate() and wedging the whole site publish -- the same
        # FAIL-CRASH-on-malformed-record class the sibling half
        # (cumulative_tests_executed) was hardened against. Skip it, exactly
        # as a None test_count is skipped above.
        if date is None:
            continue
        if date not in max_by_date or tc > max_by_date[date]:
            max_by_date[date] = tc
    progression = []
    running_max_tc = 0
    for date in sorted(max_by_date):
        tc = max_by_date[date]
        if tc >= running_max_tc:
            progression.append([date, tc])
            running_max_tc = tc
    return progression


_EPOCH_RE = re.compile(r"[Ee]poch[\s-]?(\d+)")


def _epoch_for(text):
    """Best-effort epoch tag from a phase's own title+body text (e.g. "Epoch-2
    bounded start"). Not authoritative -- docs/design/maturity_map.yaml's own
    atoms are the epoch source of truth for capability atoms, but there is no
    existing join key between a git-log-derived Section-4 phase and a
    maturity-map atom, so this is a lightweight, honestly-partial heuristic
    (director page comment 2026-07-12: "/project/ ... No link to epochs
    etc."), not a fabricated mapping for phases that never mention one."""
    m = _EPOCH_RE.search(text)
    return int(m.group(1)) if m else None


def _body_summary(body):
    """First substantive paragraph of a phase's body (after its own header
    line), for the timeline's expandable detail -- previously `detail` was
    just "Phase X -- N tests", i.e. no real content behind a phase row at
    all (same director comment: "No details behind")."""
    _header, _, rest = body.partition("\n")
    paras = [p.strip() for p in rest.split("\n\n") if p.strip()]
    if not paras:
        return ""
    first = paras[0].replace("**", "")
    return first[:500] + ("..." if len(first) > 500 else "")


def _build_timeline(chronological):
    """Build the Project-tab timeline (phase + discovery rows) from oldest-first entries.

    Replaces the hand-curated PROJ array in site/project/index.html (PROJECT_TAB_OVERHAUL.md
    item 2, R-A: nothing hand-written, everything derives or dies) -- every row is generated
    from PROJECT_OVERVIEW.md Section 4, never hand-appended.

    Additive fields (director page comment 2026-07-12, /project/ timeline: "just a long
    list... no filters or sort. No details behind. No link to epochs"): `epoch` (best-effort,
    see _epoch_for) and `summary` (the real first paragraph, see _body_summary) alongside the
    existing `detail` (kept unchanged for back-compat with anything else reading this field).
    """
    timeline = []
    for phase_id, date, test_count, title, body in chronological:
        label = title or ("Phase " + phase_id)
        detail = "Phase " + phase_id + (" -- {:,} tests".format(test_count) if test_count else "")
        epoch = _epoch_for(label) or _epoch_for(body)
        timeline.append(dict(
            date=date, type="phase", phase_id=phase_id, label=label[:160], detail=detail,
            epoch=epoch, summary=_body_summary(body),
        ))
        for finding in _extract_findings(body):
            capped = finding[:320] + ("..." if len(finding) > 320 else "")
            timeline.append(dict(
                date=date, type="discovery", phase_id=phase_id,
                label="Key Finding (Phase " + phase_id + ")", detail=capped,
                epoch=epoch, summary=capped,
            ))
    timeline.sort(key=lambda e: e["date"])

    # Epoch-transition markers: the first dated entry that mentions a given
    # epoch number >= 2 is an honest (if approximate) "this is roughly where
    # Epoch N's work starts" anchor -- per-phase epoch tagging above is
    # sparse (only phases whose own text mentions an epoch), so this is the
    # more useful answer to "no link to epochs" without fabricating a false
    # per-phase precision the source material doesn't have. Epoch 1 is
    # deliberately NOT marked this way: it is the project's own foundational
    # period, and the first phase to literally say "Epoch 1" (a later,
    # retrospective reference) lands long after the project's real start --
    # marking it "Epoch 1 begins" there would be more misleading than no
    # marker at all. Epoch 1 is simply everything before the Epoch-2 marker.
    seen_epochs = set()
    markers = []
    for entry in timeline:
        if entry["type"] != "phase" or entry["epoch"] is None or entry["epoch"] < 2:
            continue
        if entry["epoch"] in seen_epochs:
            continue
        seen_epochs.add(entry["epoch"])
        markers.append(dict(
            date=entry["date"], type="epoch_marker", phase_id=None,
            label="Epoch " + str(entry["epoch"]) + " begins (approx.)",
            detail="First phase mentioning Epoch " + str(entry["epoch"])
                   + " by name: \"" + entry["label"] + "\"",
            epoch=entry["epoch"], summary="",
        ))
    timeline.extend(markers)
    timeline.sort(key=lambda e: e["date"])
    return timeline


def generate():
    try:
        text = PROJECT_OVERVIEW.read_text()
    except Exception:
        text = ""

    entries = list(_iter_phase_entries(text))
    seen_ids = set()
    for phase_id, _date, _tc, _title, _body in entries:
        seen_ids.add(phase_id)
    total_phases = len(seen_ids)

    dated = []
    for e in entries:
        if e[1]:
            dated.append(e)
    chronological = list(reversed(dated))
    start_date = chronological[0][1] if chronological else None

    phase_dates = []
    for i, (_phase_id, date, _tc, _title, _body) in enumerate(chronological):
        phase_dates.append([date, i])

    test_progression = _monotonic_test_progression(chronological)

    latest_phase, _test_count = _parse_phase_and_tests()
    timeline = _build_timeline(chronological)

    from tools.test_execution_metric import cumulative_tests_executed
    test_executions = cumulative_tests_executed()

    # Read the previous publish BEFORE overwriting it -- neither a git failure
    # nor an unreadable PROJECT_OVERVIEW.md may collapse these cumulative
    # metrics to null/[]/0 on the live Project page (see _retain_growth_metrics).
    previous = _previously_published()
    total_commits, commits_by_day, commits_source = _retained_commit_metrics(
        _total_commits(),
        cumulative_commits_by_day(_commits_per_day_lines()),
        previous,
    )

    data = dict(
        total_phases=total_phases,
        latest_phase=latest_phase,
        start_date=start_date,
        test_progression=test_progression,
        phase_dates=phase_dates,
        total_commits=total_commits,
        commits_by_day=commits_by_day,
        commits_source=commits_source,
        timeline=timeline,
        cumulative_tests_executed=test_executions["cumulative_total"],
        cumulative_tests_executed_since=test_executions["since"],
    )
    # Class guard: hold every registered monotonic metric at its last published
    # value rather than publish a collapse, and label what is fresh vs retained.
    metrics_source = _retain_growth_metrics(data, previous)
    metrics_source["total_commits"] = commits_source
    metrics_source["commits_by_day"] = commits_source
    data["metrics_source"] = metrics_source

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: %s (total_phases=%s, latest_phase=%s, dated_entries=%s, timeline_rows=%s)" % (
        OUT_PATH, total_phases, latest_phase, len(chronological), len(timeline)))
    return True


if __name__ == "__main__":
    generate()
