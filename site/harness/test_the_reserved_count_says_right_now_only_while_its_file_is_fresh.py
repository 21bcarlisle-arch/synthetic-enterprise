""""Right now nothing is waiting on him" may be said only while the count behind it is fresh.

THE DEFECT (2026-10-22). How it's built rendered "Right now nothing is waiting on him" from
`site/data/director_reserved.json`, last written on 18 Sep, while the director's list held open
rows. The page never read the file's own `generated_at`.

Runs the page's own `renderReserved` through the render harness. One partition over freshness and
count: a fresh count says "Right now", a stale one names its date and refuses "now", and an
unreadable stamp is stale. The fresh leg comes first so a render that refuses everything cannot
pass.

MUTATIONS, RUN 2026-10-22, all red:
  * `fresh` forced true -> the stale legs red.
  * `fresh` forced false -> the fresh leg reds.
  * the stamp's date dropped from the stale sentence -> the date leg reds.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent


def _render(feed: dict) -> str:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not available to run the page's own script")
    proc = subprocess.run(
        [node, str(_HERE / "_render_harness.mjs"), str(_HERE / "index.html"), "renderReserved",
         "reserved-now"],
        input=json.dumps(feed), capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr[:400]
    return json.loads(proc.stdout)["innerHTML"]


def _at(days_ago: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def test_right_now_only_while_the_count_is_fresh():
    fresh_none = _render({"generated_at": _at(1), "open_count": 0})
    fresh_two = _render({"generated_at": _at(1), "open_count": 2})
    stale = _render({"generated_at": "2026-09-18T23:17:47+00:00", "open_count": 0})
    unstamped = _render({"open_count": 0})

    assert fresh_none.startswith("Right now nothing is waiting")
    assert fresh_two.startswith("Right now <b>2</b> decision(s) are waiting")
    for html in (stale, unstamped):
        assert "Right now" not in html and "too old to say what is waiting now" in html
    assert "on 2026-09-18" in stale


def test_the_live_file_is_rendered_by_the_same_rule():
    """The real feed goes through the same function. Whatever its age, the sentence names
    either "Right now" or the day it was counted, never neither."""
    live = json.loads((_HERE.parent / "data" / "director_reserved.json").read_text())
    html = _render(live)
    assert html.startswith("Right now") or "When this was last counted, on " in html
