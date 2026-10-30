#!/usr/bin/env python3
"""An area's pain-point table is its knowledge stage, and no row on it may be blank.

docs/design/THE_IMPROVEMENT_LOOP.md defines stage 0 of an area as a K8 page carrying the area's
pain-point table, where "each pain point has reaction evidence OR a GAP with a labelled range,
plus the area's scorecard vector", and its check as "every pain-point row has evidence or a
range. No row is blank". This file is that check, over the record the pages actually render.

Why a range and not a missing value: K2. A reaction nobody sized, left out, ships at 0, and 0 is
the one value we know is wrong. So a GAP must carry low <= central <= high and say what kind of
basis the range has -- published bound, derived, or a labelled assumption -- so a reader can tell
a bound from a belief.

The pages carrying a table are SCANNED from the record, never listed, with a floor so the scan
cannot pass by finding nothing. The door leg drives each page's own JavaScript against the real
feed: a row in the record that never reaches the reader is not knowledge.

R15: `test_the_check_can_refuse` feeds the validator a blank row, an inverted range and a row
whose range has no basis, and asserts each is refused. A check that accepts everything passes
every other test here.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
LIVE_HARNESS = SITE / "_live_harness.mjs"
RECORD = SITE / "data" / "knowledge_topics.json"
GRAPH = SITE / "data" / "knowledge_wholesale.json"

BASIS_KINDS = {"published bound", "derived", "assumption", "published bound + assumption"}
M3_AXES = ("money", "time", "carbon")


def _pages() -> dict:
    return json.loads(RECORD.read_text())["pages"]


def _tables() -> list[str]:
    return sorted(slug for slug, page in _pages().items() if page.get("pain_points"))


def row_defects(row: dict) -> list[str]:
    """What makes one pain-point row fail stage 0. Empty means it passes."""
    out = []
    for field in ("id", "pain_point", "how_met", "signal"):
        if not str(row.get(field) or "").strip():
            out.append(f"no {field}")
    evidence = [e for e in row.get("evidence") or [] if str(e).strip()]
    gap = row.get("gap")
    if not evidence and not gap:
        out.append("blank: neither reaction evidence nor a GAP")
    if gap:
        nums = [gap.get(k) for k in ("low", "central", "high")]
        if not all(isinstance(n, (int, float)) for n in nums):
            out.append(f"GAP range is not three numbers: {nums}")
        elif not nums[0] <= nums[1] <= nums[2]:
            out.append(f"GAP range is not ordered low <= central <= high: {nums}")
        if gap.get("basis_kind") not in BASIS_KINDS:
            out.append(f"GAP basis_kind {gap.get('basis_kind')!r} is not one of {sorted(BASIS_KINDS)}")
        for field in ("quantity", "unit", "basis"):
            if not str(gap.get(field) or "").strip():
                out.append(f"GAP has no {field}")
    return out


def _js(n) -> str:
    """A number as the page's JavaScript prints it: 1.0 renders as 1."""
    return str(int(n)) if float(n).is_integer() else repr(n)


def test_the_scan_has_not_emptied():
    """Three pages carried a table when this was written (2026-10-30). Raise, never lower."""
    assert len(_tables()) >= 3, _tables()


def test_the_check_can_refuse():
    good = {"id": "X1", "pain_point": "p", "how_met": "h", "signal": "s", "evidence": ["e"],
            "gap": {"quantity": "q", "low": 0.1, "central": 0.2, "high": 0.3, "unit": "u",
                    "basis_kind": "assumption", "basis": "b"}}
    assert row_defects(good) == []
    blank = dict(good, evidence=[], gap=None)
    inverted = dict(good, gap=dict(good["gap"], low=0.4))
    unbased = dict(good, gap=dict(good["gap"], basis=""))
    unkinded = dict(good, gap=dict(good["gap"], basis_kind="picked"))
    for bad in (blank, inverted, unbased, unkinded):
        assert row_defects(bad), bad


@pytest.mark.parametrize("slug", _tables())
def test_no_row_is_blank_and_every_range_is_labelled(slug: str):
    rows = _pages()[slug]["pain_points"].get("rows") or []
    assert rows, f"{slug} carries a pain-point table with no rows"
    bad = {r.get("id"): row_defects(r) for r in rows if row_defects(r)}
    assert not bad, f"{slug}: {bad}"


@pytest.mark.parametrize("slug", _tables())
def test_the_scorecard_is_a_vector_over_money_time_and_carbon(slug: str):
    axes = _pages()[slug]["pain_points"].get("scorecard") or []
    names = " ".join(a.get("axis", "") for a in axes).lower()
    missing = [a for a in M3_AXES if a not in names]
    assert not missing, f"{slug}: scorecard lacks the M3 axes {missing}"
    assert all(str(a.get("measures") or "").strip() for a in axes), f"{slug}: an axis measures nothing"


def test_a_pain_point_has_one_home():
    seen: dict[str, str] = {}
    for slug in _tables():
        for row in _pages()[slug]["pain_points"]["rows"]:
            assert row["id"] not in seen, f"{row['id']} is on both {seen[row['id']]} and {slug}"
            seen[row["id"]] = slug


@pytest.mark.parametrize("slug", _tables())
def test_the_page_renders_every_row_and_every_range(slug: str):
    door = HERE / slug / "index.html"
    html = door.read_text()
    for element_id in ("h-pain", "r-pain"):
        assert re.search(rf'id="{element_id}"', html), f"{slug} has no element {element_id}"
    feeds = {
        "../../data/knowledge_topics.json": json.loads(RECORD.read_text()),
        "../../data/knowledge_wholesale.json": json.loads(GRAPH.read_text()),
    }
    proc = subprocess.run(["node", str(LIVE_HARNESS), str(door)], input=json.dumps(feeds),
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[:600]
    rendered = json.loads(proc.stdout).get("r-pain", {}).get("innerHTML", "")
    for row in _pages()[slug]["pain_points"]["rows"]:
        assert f'data-pain-point="{row["id"]}"' in rendered, f"{slug}: row {row['id']} not rendered"
        gap = row.get("gap")
        if gap:
            assert (f"Low {_js(gap['low'])}, central {_js(gap['central'])}, "
                    f"high {_js(gap['high'])}") in rendered, (
                f"{slug}: {row['id']}'s range does not reach the reader")
