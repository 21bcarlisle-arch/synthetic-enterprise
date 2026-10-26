"""THE DEFECT: the 07:40Z publish of run 4ae8da9b0f (2026-10-26) was refused by the stale-copy
guard as reverting 19 pages. On every one, the only distinctive line the last landing added was
the 19 Oct run's RUN-CLOCK or cast stamp -- a region the publish rewrites whole, by design. So the
first publish after any commit that last touched a page through its stamp could never land.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import generate_dashboard_data as gdd
from tools import stale_copy_refusal as scr

CLOCK = "{}\n<p class=\"lf-prov\">Published with the run of {} (run {})</p>\n{}\n"


def _page(run, body="<p>The body of the page.</p>"):
    return "<html>\n{}\n{}</html>\n".format(
        body, CLOCK.format(gdd.RUN_CLOCK_START, run, run + "_hash", gdd.RUN_CLOCK_END))


def _git(root, *a):
    return subprocess.run(["git", *a], cwd=str(root), capture_output=True, text=True,
                          check=True).stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "r"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")
    (root / "p.html").write_text(_page("12 Oct"))
    _git(root, "add", "p.html")
    _git(root, "commit", "-qm", "base")
    return root


def _land(root, text):
    (root / "p.html").write_text(text)
    _git(root, "add", "p.html")
    _git(root, "commit", "-qm", "landing")
    return _git(root, "rev-parse", "HEAD").strip()


def test_a_regenerated_stamp_is_not_a_revert_and_a_lost_body_line_still_is(repo):
    """BOTH SIDES IN ONE CONTROL, so a filter that drops everything cannot pass.

    MUTATION: delete the `written` filter and the first assertion reds (the stamp is evidence
    again); make `publish_written_lines` return every line and the second reds (no evidence).
    """
    stamp_only = _land(repo, _page("19 Oct"))
    assert scr.distinctive_lines(repo, "p.html", stamp_only) == ()
    assert scr.judge(repo, "p.html", _page("19 Oct"), _page("26 Oct")) is None

    body = _land(repo, _page("19 Oct", body="<p>A paragraph a landing added and a copy can lose.</p>"))
    assert "<p>A paragraph a landing added and a copy can lose.</p>" in \
        scr.distinctive_lines(repo, "p.html", body)


def test_the_cast_region_on_one_line_is_publish_written():
    line = '<div id="c"><!--cast:static--><p>Run of 26 Oct</p><!--/cast:static--></div>'
    assert scr.publish_written_lines("<p>x</p>\n" + line + "\n<p>y</p>") == frozenset({line})


def test_the_region_tokens_are_the_generators_own():
    """Keyed to the property: if a generator renames its marker, the exemption must red here,
    not silently stop applying."""
    start, end = scr.PUBLISH_WRITTEN_REGIONS[0]
    assert start in gdd.RUN_CLOCK_START and end in gdd.RUN_CLOCK_END
    cast = Path(__file__).resolve().parents[2] / "tools" / "generate_explore_cast.py"
    assert all(tok in cast.read_text() for tok in scr.PUBLISH_WRITTEN_REGIONS[1])
