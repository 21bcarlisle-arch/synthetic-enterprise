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

sys.path.insert(0, str(PROJECT))
from tools.generate_project_state import _parse_phase_and_tests  # noqa: E402

_HEADER_RE = re.compile(r"^### Phase\s+(\S+)")
_DATE_RE = re.compile(r"(\d\d\d\d-\d\d-\d\d)")
_TITLE_RE = re.compile(r"^### Phase\s+\S+(?:\s*\([^)]*\))?\s*--\s*(.+)$")
_FINDING_RE = re.compile(r"KEY FINDING\b[^\n]*")

_TEST_COUNT_RES = [
    re.compile(r"\*\*Total:\*\*\s*([\d,]+)\s*tests"),
    re.compile(r"([\d,]+)\s*collected"),
    re.compile(r"([\d,]+)\s*tests?\s+passing"),
    re.compile(r"\(([\d,]+)\+?\s*total\)"),
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
        phase_id = _HEADER_RE.match(header).group(1)
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


def _build_timeline(chronological):
    """Build the Project-tab timeline (phase + discovery rows) from oldest-first entries.

    Replaces the hand-curated PROJ array in site/project/index.html (PROJECT_TAB_OVERHAUL.md
    item 2, R-A: nothing hand-written, everything derives or dies) -- every row is generated
    from PROJECT_OVERVIEW.md Section 4, never hand-appended.
    """
    timeline = []
    for phase_id, date, test_count, title, body in chronological:
        label = title or ("Phase " + phase_id)
        detail = "Phase " + phase_id + (" -- {:,} tests".format(test_count) if test_count else "")
        timeline.append(dict(date=date, type="phase", phase_id=phase_id, label=label[:160], detail=detail))
        for finding in _extract_findings(body):
            capped = finding[:320] + ("..." if len(finding) > 320 else "")
            timeline.append(dict(
                date=date, type="discovery", phase_id=phase_id,
                label="Key Finding (Phase " + phase_id + ")", detail=capped,
            ))
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

    tp_by_date = {}
    for _phase_id, date, tc, _title, _body in chronological:
        if tc is not None:
            tp_by_date[date] = tc
    test_progression = []
    for d in sorted(tp_by_date):
        test_progression.append([d, tp_by_date[d]])

    latest_phase, _test_count = _parse_phase_and_tests()
    timeline = _build_timeline(chronological)

    data = dict(
        total_phases=total_phases,
        latest_phase=latest_phase,
        start_date=start_date,
        test_progression=test_progression,
        phase_dates=phase_dates,
        total_commits=_total_commits(),
        timeline=timeline,
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: %s (total_phases=%s, latest_phase=%s, dated_entries=%s, timeline_rows=%s)" % (
        OUT_PATH, total_phases, latest_phase, len(chronological), len(timeline)))
    return True


if __name__ == "__main__":
    generate()
