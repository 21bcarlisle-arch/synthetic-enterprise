"""R11: "ten of eleven are stale" must be a READING on the page, not a discovery someone makes.

THE DEFECT THIS OWNS. On 2026-09-04 ten of eleven daemons were running code up to eleven days
behind the repository, one of them holding 146 changed modules it imports. The drift control had
been computing that correctly every five minutes for weeks and writing it to a log. Nobody read the
log. The director's instruction was to put "every daemon's loaded-code age against its running age,
in one place, so 'ten of eleven are stale' is a reading and not a discovery."

WHY THIS RUNS THE PAGE'S OWN JAVASCRIPT rather than grepping `index.html`. `renderDeployment`
composes its sentence at RUNTIME from the feed — the words a reader actually meets ("N of M
observed daemons are running code behind the repository") exist nowhere in the markup, so a grep of
the source is blind to whether the section says anything at all. Same lesson as
`test_door_render_functions_are_wired`: a panel can be defined, wired, and still render nothing.

The legs, and the defect each names:
  * the real feed renders every daemon with BOTH ages — the ordered figure actually arrives.
  * an absent feed block renders a NAMED refusal — the fail-closed direction. An empty table reads
    as "no daemon is stale", which is the one sentence this section must never say by accident.
  * a stale daemon and a current one render DIFFERENTLY — without this the section could print the
    same thing whatever the world does, which is a constant verdict wearing a table's clothes.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_PAGE = _HERE / "index.html"
_HARNESS = _HERE / "_render_harness.mjs"
_FEED = _HERE.parent / "data" / "proof.json"


def _render(feed: dict) -> dict:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not available to run the page's own script")
    proc = subprocess.run(
        [node, str(_HARNESS), str(_PAGE), "renderDeployment", "deployment"],
        input=json.dumps(feed), capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr[:400]}"
    out = json.loads(proc.stdout)
    assert out is not None, "the page rendered nothing into #deployment"
    return out


def _live_feed() -> dict:
    if not _FEED.is_file():
        pytest.fail("site/data/proof.json is missing — an unavailable check is a FAILED check")
    return json.loads(_FEED.read_text())


def test_the_live_feed_renders_every_daemon_with_both_ages():
    """MUTATION: drop `loaded_code_age_s` from the row, or the column from the table, and this
    fires. Both ages were the instruction; one of them is a different, weaker answer."""
    feed = _live_feed()
    dep = feed.get("deployment")
    assert dep and dep.get("available"), (
        "the harness feed carries no deployment reading, so the page cannot show one: {}".format(
            (dep or {}).get("unavailable_because"))
    )
    html = _render(feed)["innerHTML"]

    assert "running age" in html and "loaded-code age" in html, (
        "the rendered table does not offer both ages, which is the whole instruction"
    )
    for row in dep["daemons"]:
        assert row["session"] in html, f"{row['session']} is missing from the rendered table"
    assert "behind" in html


def test_the_headline_states_the_count_a_reader_would_quote():
    """The sentence that makes it a reading. MUTATION: delete the headline and the section becomes
    a table a reader has to count for themselves — which is the discovery, not the reading."""
    feed = _live_feed()
    dep = feed["deployment"]
    html = _render(feed)["innerHTML"]
    stale = int(dep["summary"].get("stale", 0))
    observed = int(dep["summary"].get("observed", 0))
    if stale:
        assert f"{stale} of {observed} observed daemons are running code behind" in html
    else:
        assert f"All {observed} observed daemons are running current code." in html


def test_an_absent_reading_renders_a_named_refusal_not_an_empty_table():
    """THE FAIL-CLOSED LEG, and the one worth the most. MUTATION: `if (!dep) return;` — an early
    return leaves the container empty, and an empty container under the heading "What code each
    daemon is actually running" reads as "nothing to report". Absence must be stated."""
    html = _render({"deployment": {"available": False,
                                   "unavailable_because": "the artefact could not be read"}})["innerHTML"]
    assert "cannot be established" in html
    assert "the artefact could not be read" in html
    assert "running current code" not in html, "a refusal rendered a reassurance"


def test_a_missing_block_entirely_is_also_refused():
    """The feed predates this section, or the generator failed. Same requirement."""
    html = _render({})["innerHTML"]
    assert "cannot be established" in html
    assert "running current code" not in html


def test_a_stale_daemon_and_a_current_one_do_not_render_the_same():
    """THE NULL CONTROL. Without it every leg above is satisfied by a section that prints one fixed
    thing regardless of the world — a constant verdict, which is this repo's most expensive control
    shape."""
    base = {"running_age_s": 600, "loaded_code_age_s": 900, "behind_s": 300,
            "session_hosting": False, "mid_work": False, "unresolved": None}
    stale = _render({"deployment": {"available": True, "summary": {"stale": 1, "observed": 1},
                                    "daemons": [dict(base, session="alpha", stale=True,
                                                     modules_behind=7)]}})["innerHTML"]
    current = _render({"deployment": {"available": True, "summary": {"stale": 0, "observed": 1},
                                      "daemons": [dict(base, session="alpha", stale=False,
                                                       modules_behind=0)]}})["innerHTML"]
    assert stale != current, "the section renders identically whether the daemon is stale or not"
    assert "7 changed module(s) it imports" in stale
    assert "current" in current and "changed module(s)" not in current


def test_a_daemon_that_cannot_be_judged_says_so_rather_than_reading_as_current():
    """An unresolved drift row must not render in the same colour as a clean one — unknown is not
    current, and this is the row where that distinction is cheapest to lose."""
    html = _render({"deployment": {"available": True, "summary": {"stale": 0, "observed": 1},
                                   "daemons": [{"session": "ghost", "running_age_s": 60,
                                                "loaded_code_age_s": 60, "behind_s": 0,
                                                "modules_behind": 0, "stale": False,
                                                "mid_work": False, "session_hosting": False,
                                                "unresolved": "unstamped"}]}})["innerHTML"]
    assert "cannot tell" in html and "unstamped" in html
