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


def _parse_build_history(text):
    lines = text.split("\n")
    header_idxs = []
    for i, line in enumerate(lines):
        if _HEADER_RE.match(line):
            header_idxs.append(i)
    entries = []
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
        entries.append((phase_id, date, _extract_test_count(body)))
    return entries


def generate():
    try:
        text = PROJECT_OVERVIEW.read_text()
    except Exception:
        text = ""

    entries = _parse_build_history(text)
    seen_ids = set()
    for phase_id, _date, _tc in entries:
        seen_ids.add(phase_id)
    total_phases = len(seen_ids)

    dated = []
    for e in entries:
        if e[1]:
            dated.append(e)
    chronological = list(reversed(dated))
    start_date = chronological[0][1] if chronological else None

    phase_dates = []
    for i, (_phase_id, date, _tc) in enumerate(chronological):
        phase_dates.append([date, i])

    tp_by_date = {}
    for _phase_id, date, tc in chronological:
        if tc is not None:
            tp_by_date[date] = tc
    test_progression = []
    for d in sorted(tp_by_date):
        test_progression.append([d, tp_by_date[d]])

    latest_phase, _test_count = _parse_phase_and_tests()

    data = dict(
        total_phases=total_phases,
        latest_phase=latest_phase,
        start_date=start_date,
        test_progression=test_progression,
        phase_dates=phase_dates,
        total_commits=_total_commits(),
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: %s (total_phases=%s, latest_phase=%s, dated_entries=%s)" % (
        OUT_PATH, total_phases, latest_phase, len(chronological)))
    return True


if __name__ == "__main__":
    generate()
