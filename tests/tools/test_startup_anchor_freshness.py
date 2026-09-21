"""The startup-anchor freshness check, each test named by the defect it exists to catch.

Driven against REAL git repositories built in tmp_path rather than mocks. The whole subject of
this module is the disagreement between what a file says and what git knows about it, so a mocked
git would make every test here a statement about the mock.
"""
from __future__ import annotations

import datetime as dt
import subprocess

import pytest

from tools import startup_anchor_freshness as saf

TODAY = dt.date(2026, 9, 5)

_BLOCK = """# Overview

*Last updated: {declared}.*

**GitHub Pages (live):**
- This document: {root}PROJECT_OVERVIEW.md
- Annual report: {root}reports/ANNUAL_REPORT.md
- Assumptions: {root}market_research/ASSUMPTIONS.md
- Status: {root}status/LATEST.md
"""


def _run(repo, *args):
    done = subprocess.run(("git", *args), cwd=str(repo), capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout


def _repo(tmp_path, monkeypatch, declared="2026-09-05", others=None, commit_date="2026-09-05"):
    """A real repo whose docs/ holds the four anchors, committed at `commit_date`."""
    repo = tmp_path / "r"
    (repo / "docs" / "reports").mkdir(parents=True)
    (repo / "docs" / "market_research").mkdir(parents=True)
    (repo / "docs" / "status").mkdir(parents=True)
    _run(repo.parent, "init", "-q", "-b", "main", str(repo))
    _run(repo, "config", "user.email", "t@t")
    _run(repo, "config", "user.name", "t")

    (repo / "docs" / "PROJECT_OVERVIEW.md").write_text(
        _BLOCK.format(declared=declared, root=saf.PAGES_ROOT))
    for rel, body in (others or {
        "docs/reports/ANNUAL_REPORT.md": "# Annual Report\n\nno date anywhere\n",
        "docs/market_research/ASSUMPTIONS.md": "# Assumptions\n\nLast seeded: 2026-09-05\n",
        "docs/status/LATEST.md": "## state\nLast updated: 2026-09-05T07:06:34Z\n",
    }).items():
        (repo / rel).write_text(body)

    _run(repo, "add", "-A")
    stamp = f"{commit_date}T12:00:00+00:00"
    subprocess.run(("git", "commit", "-q", "-m", "seed"), cwd=str(repo), check=True,
                   env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path),
                        "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp,
                        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})

    monkeypatch.setattr(saf, "PROJECT", repo)
    monkeypatch.setattr(saf, "OVERVIEW", repo / "docs" / "PROJECT_OVERVIEW.md")
    monkeypatch.setattr(saf, "OUT", repo / "docs" / "status" / "STARTUP_ANCHORS.md")
    return repo


def _verdict(rows, needle):
    return next(r["verdict"] for r in rows if needle in r["path"])


def test_a_document_whose_own_date_disagrees_with_its_real_age_is_refused():
    """THE DEFECT, exactly as it happened. PROJECT_OVERVIEW.md said "Last updated: 2026-08-09"
    while its last commit was 2026-08-17 and its figures were 3.7x out on commits and 15x on
    lines. A session started from it, orienting on a project a fifteenth of this one's size."""
    rows = [{"path": "docs/PROJECT_OVERVIEW.md", "verdict": "LIES",
             "declared": "2026-08-09", "true_last_change": "2026-08-17",
             "age_days": 19, "declared_drift_days": 8}]
    assert saf.refusals(rows) == rows


def test_a_genuinely_old_document_that_says_so_is_not_refused(tmp_path, monkeypatch):
    """THE DIRECTION THAT WOULD MAKE THIS CONTROL UNSATISFIABLE, and the real case that proves
    it matters: ASSUMPTIONS.md is 26 days old and says "Last seeded: 2026-08-10", which is true.

    A control keyed to AGE would go red on it for a reason nobody can act on -- nobody is going to
    re-seed an assumption library to silence a gate -- and an unsatisfiable control gets turned
    off. The property is honesty about age, not youth.
    """
    _repo(tmp_path, monkeypatch, commit_date="2026-08-10", declared="2026-08-10",
          others={"docs/reports/ANNUAL_REPORT.md": "# A\n",
                  "docs/market_research/ASSUMPTIONS.md": "# X\n\nLast seeded: 2026-08-10\n",
                  "docs/status/LATEST.md": "Last updated: 2026-08-10\n"})
    rows = saf.assess(today=TODAY)

    assert _verdict(rows, "ASSUMPTIONS") == "OLD"
    assert [r["age_days"] for r in rows if "ASSUMPTIONS" in r["path"]] == [26]
    assert saf.refusals(rows) == [], "an old-but-honest anchor must never refuse"


def test_an_undated_document_is_reported_and_not_refused(tmp_path, monkeypatch):
    """ANNUAL_REPORT.md carries no date of its own. It cannot be caught lying, so the published
    table is the only age a reader gets -- which is why the table exists and why this is not a
    refusal."""
    _repo(tmp_path, monkeypatch)
    rows = saf.assess(today=TODAY)

    assert _verdict(rows, "ANNUAL_REPORT") == "UNDATED"
    assert saf.refusals(rows) == []


def test_deleting_anchor_rows_refuses_rather_than_passing_an_empty_set(tmp_path, monkeypatch):
    """THE CHEAPEST WAY TO SILENCE ANY REGISTER-DRIVEN CONTROL: delete the rows it iterates.

    This module derives its subject from the anchor block precisely so the two cannot drift, and
    that derivation is what makes the silencing possible. The floor is the answer -- an empty or
    shrunken anchor set is a broken check, never a clean one.
    """
    repo = _repo(tmp_path, monkeypatch)
    (repo / "docs" / "PROJECT_OVERVIEW.md").write_text("# Overview\n\nno anchor block at all\n")

    with pytest.raises(saf.AnchorRefusal, match="floor"):
        saf.assess(today=TODAY)


def test_another_lanes_unstaged_edit_does_not_make_a_document_a_liar(tmp_path, monkeypatch):
    """THE DEFECT THE FIRST DRAFT SHIPPED WITH, found by running it against the real tree.

    It asked `git status --porcelain`, which counts unstaged edits. A concurrent lane was mid-
    append to ASSUMPTIONS.md, so the check called that file's honest date a lie and refused --
    naming a file that lane held dirty, which no other lane can correct without carrying their
    uncommitted work into its own commit.

    The subject is the tree THIS COMMIT creates. Unstaged is not that.
    """
    repo = _repo(tmp_path, monkeypatch, commit_date="2026-08-10", declared="2026-08-10",
                 others={"docs/reports/ANNUAL_REPORT.md": "# A\n",
                         "docs/market_research/ASSUMPTIONS.md": "# X\n\nLast seeded: 2026-08-10\n",
                         "docs/status/LATEST.md": "Last updated: 2026-08-10\n"})
    # Another lane, mid-append, nothing staged.
    p = repo / "docs" / "market_research" / "ASSUMPTIONS.md"
    p.write_text(p.read_text() + "\n## a new section this lane is still writing\n")

    assert saf.refusals(saf.assess(today=TODAY)) == []

    # ...and the moment that lane STAGES it, the date it has invalidated is its own to fix.
    _run(repo, "add", "docs/market_research/ASSUMPTIONS.md")
    assert _verdict(saf.assess(today=TODAY), "ASSUMPTIONS") == "LIES"


def test_a_git_failure_refuses_rather_than_reporting_everything_fresh(tmp_path, monkeypatch):
    """FAIL-CLOSED. An unmeasurable startup surface is the exact condition being guarded against,
    so unlike the next-step gate this has no fail-open branch. R15's FAIL-OPEN killer.

    Driven through the REAL `_git` against a real non-repository. The first version of this test
    monkeypatched `_git` to raise -- which made it a statement about the monkeypatch: mutation
    testing showed `_git`'s own `raise` could be replaced with `return ""` and this stayed green,
    the exact shape of a control that survives mutation of the thing it claims to guard.
    """
    _repo(tmp_path, monkeypatch)
    not_a_repo = tmp_path / "elsewhere"
    (not_a_repo / "docs" / "status").mkdir(parents=True)
    (not_a_repo / "docs" / "PROJECT_OVERVIEW.md").write_text(
        _BLOCK.format(declared="2026-09-05", root=saf.PAGES_ROOT))
    monkeypatch.setattr(saf, "PROJECT", not_a_repo)
    monkeypatch.setattr(saf, "OVERVIEW", not_a_repo / "docs" / "PROJECT_OVERVIEW.md")
    monkeypatch.setattr(saf, "OUT", not_a_repo / "docs" / "status" / "STARTUP_ANCHORS.md")

    with pytest.raises(saf.AnchorRefusal):
        saf.assess(today=TODAY)
    assert saf.main(["--check"]) == 1


def test_the_published_table_carries_every_declared_anchor_and_the_header_warning(
        tmp_path, monkeypatch):
    """A table that silently dropped an anchor would be worse than none: a reader would take the
    four rows as the whole surface.

    The `last-modified` warning is asserted because it is the actual trap and it is invisible: the
    Pages mirror uploads all of `docs/` as one artefact, so a publish restamps every file and a
    month-old document is served with today's date. A reader who checks the header is misled by
    the transport, not by the document.
    """
    _repo(tmp_path, monkeypatch)
    rows = saf.assess(today=TODAY)
    table = saf.render(rows, today=TODAY)

    for r in rows:
        assert r["path"] in table
    assert len(rows) >= saf.MIN_ANCHORS
    assert "last-modified" in table.lower()


def test_the_gate_does_not_refuse_a_lane_for_a_date_it_did_not_break(tmp_path, monkeypatch):
    """THE TRAP THIS PROJECT HAS ALREADY PAID FOR: a red that refuses your land was already at
    HEAD. If the gate judged every anchor, then from the moment ANY document's date sentence went
    wrong, every commit in the tree would be refused until someone unrelated fixed it -- and
    fixing it means editing a file another lane may hold dirty. `--gate` judges only what this
    commit stages.
    """
    repo = _repo(tmp_path, monkeypatch, commit_date="2026-08-10", declared="2026-08-10",
                 others={"docs/reports/ANNUAL_REPORT.md": "# A\n",
                         "docs/market_research/ASSUMPTIONS.md": "# X\n\nLast seeded: 2026-08-10\n",
                         "docs/status/LATEST.md": "Last updated: 2026-08-10\n"})
    # HEAD's overview is honest; now make it lie, but WITHOUT staging it (another lane's edit).
    (repo / "docs" / "PROJECT_OVERVIEW.md").write_text(
        _BLOCK.format(declared="2020-01-01", root=saf.PAGES_ROOT))
    (repo / "unrelated.txt").write_text("some other lane's actual commit\n")
    _run(repo, "add", "unrelated.txt")

    assert saf.main(["--gate"]) == 0, "an unrelated commit must not be refused"


def test_the_gate_refuses_the_lane_that_does_break_a_date(tmp_path, monkeypatch):
    """The other side, without which the test above is satisfied by a gate that never refuses."""
    repo = _repo(tmp_path, monkeypatch, commit_date="2026-08-10", declared="2026-08-10",
                 others={"docs/reports/ANNUAL_REPORT.md": "# A\n",
                         "docs/market_research/ASSUMPTIONS.md": "# X\n\nLast seeded: 2026-08-10\n",
                         "docs/status/LATEST.md": "Last updated: 2026-08-10\n"})
    p = repo / "docs" / "market_research" / "ASSUMPTIONS.md"
    p.write_text(p.read_text() + "\n## new content, header not updated\n")
    _run(repo, "add", str(p))

    assert saf.main(["--gate"]) == 1


def test_the_real_anchor_block_still_parses_at_or_above_the_floor():
    """REACHABILITY, against the live tree. Every test above builds its own repo, so all of them
    would stay green if the real PROJECT_OVERVIEW.md's block were reformatted past the regex --
    and the check would then refuse on the floor forever, which reads exactly like a wedge."""
    paths = saf.anchor_paths()

    assert len(paths) >= saf.MIN_ANCHORS
    assert "docs/PROJECT_OVERVIEW.md" in paths
    assert "docs/status/LATEST.md" in paths

def test_a_maintained_surface_the_anchors_DO_NOT_NAME_is_refused(monkeypatch, tmp_path):
    """THE CLASS, in the director's words: "every operating change we make is invisible to a fresh
    session until it trips over it."

    Measured 2026-09-06: the anchor block named PROJECT_OVERVIEW, LATEST and ASSUMPTIONS -- all of
    which predate the delivery seat, DIRECTION.yaml, the class registers and the stretch log. Two of
    the five named surfaces had ZERO commits in fourteen days while the five most actively
    maintained reasoning surfaces were named nowhere. A week of daily prose was written, rendered
    and published, and the advisor spent three tool calls hunting for it.
    """
    monkeypatch.setattr(saf, "discover_maintained_surfaces",
                        lambda *a, **k: {"docs/status/A_NEW_SURFACE.md": {"tools/thing.py"}})

    assert saf.unnamed_surfaces() == {"docs/status/A_NEW_SURFACE.md": {"tools/thing.py"}}
    assert saf.main(["--check"]) == 1


def test_a_surface_the_anchors_DO_name_is_not_flagged(monkeypatch):
    """The negative leg. Without it a check that flagged everything would satisfy the test above
    while making the anchor block impossible to satisfy."""
    named = saf.anchor_paths()[0]
    monkeypatch.setattr(saf, "discover_maintained_surfaces", lambda *a, **k: {named: {"x.py"}})

    assert saf.unnamed_surfaces() == {}


def test_discovery_finds_a_surface_by_ITS_MODULE_DECLARING_A_PATH_not_by_edit_frequency():
    """FREQUENCY WAS TRIED FIRST AND IS THE WRONG DISCRIMINATOR, which is why this is structural.

    Ranking `docs/` paths by commit count puts the RETIRED `docs/shadow/` mirror pages above
    `knowledge_map.md`, and it would never have caught the stretch log -- two commits old on the day
    it was missed. A surface the machine DECLARES A PATH TO is one a reader can be sent to, however
    new it is.
    """
    found = saf.discover_maintained_surfaces()

    assert "docs/status/SEAT_STRETCH_LOG.md" in found, "the surface that prompted this is not found"
    assert any("stretch_log" in m for m in found["docs/status/SEAT_STRETCH_LOG.md"])
    assert not any(p.startswith("docs/shadow/") for p in found), "the retired mirror is not a surface"
    assert not any(p.endswith(".json") for p in found), "a JSON feed is machinery output, not reading"


def _unfiltered_discovery(root):
    """`discover_maintained_surfaces` WITHOUT its line prefilter -- the reference implementation.

    Deliberately a transcription of the pre-2026-09-17 body rather than a call into the module:
    a reference that imports the thing it grades moves with it, and this one has to stay still.
    """
    import ast
    import re

    found = {}
    for tree in ("tools", "background"):
        for f in sorted((root / tree).glob("*.py")):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
                parsed = ast.parse(text)
            except (OSError, SyntaxError):
                continue
            for node in ast.walk(parsed):
                if not isinstance(node, ast.Assign):
                    continue
                src = ast.get_source_segment(text, node) or ""
                m = re.search(r'"docs"\s*/\s*(.+)', src, re.S)
                if not m:
                    continue
                segs = re.findall(r'"([^"]+)"', m.group(1))
                if not segs:
                    continue
                rel = "docs/" + "/".join(segs)
                if not saf._is_published(rel) or not rel.endswith(saf._READER_SUFFIXES):
                    continue
                found.setdefault(rel, set()).add(f"{tree}/{f.name}")
    return found


def test_the_prefilter_finds_exactly_what_the_unfiltered_walk_finds(tmp_path):
    """THE SPEED-UP MAY NOT NARROW THE CONTROL (2026-09-17).

    `discover_maintained_surfaces` called `ast.get_source_segment` once per `Assign`, and that
    function re-splits the whole file on every call: 42.2s over tools/ + background/ to return
    EIGHT surfaces, paid by every commit staging an anchor. It now skips a file with no literal
    `"docs"` and only segments nodes spanning a line that has one -- 2.0s, 18,947 calls down to
    450.

    A faster scan that finds LESS is the defect, not the repair, so this grades the two
    implementations against each other rather than against a list of today's answers. Keyed to
    the property: it stays true when a new surface is declared and goes red the moment the
    prefilter drops a node the regex would have matched.

    THE MUTATION IT EXISTS FOR, and the tempting wrong version: prefilter on `node.lineno` alone
    instead of the node's whole line span. `SPREAD_OVER_LINES` below is an `Assign` whose
    `"docs"` sits on its SECOND line, so the cheaper predicate loses it and this reds. The
    single-line and the false-friend cases are here so a prefilter that simply gives up and
    segments everything is not what makes it pass.
    """
    for tree in ("tools", "background"):
        (tmp_path / tree).mkdir()

    (tmp_path / "tools" / "single_line.py").write_text(
        'from pathlib import Path\n'
        'ROOT = Path(".")\n'
        'PLAIN = ROOT / "docs" / "status" / "PLAIN.md"\n',
        encoding="utf-8")

    # The node whose `"docs"` is NOT on its opening line -- the mutation's victim.
    (tmp_path / "tools" / "spread_over_lines.py").write_text(
        'from pathlib import Path\n'
        'ROOT = Path(".")\n'
        'SPREAD_OVER_LINES = (\n'
        '    ROOT\n'
        '    / "docs"\n'
        '    / "status"\n'
        '    / "SPREAD.md"\n'
        ')\n',
        encoding="utf-8")

    # A module with no `"docs"` at all -- the file-level skip must not change the answer.
    (tmp_path / "background" / "no_docs_here.py").write_text(
        'from pathlib import Path\n'
        'ELSEWHERE = Path(".") / "site" / "data" / "feed.json"\n',
        encoding="utf-8")

    # False friends: a JSON feed and an unpublished room are machinery, not reading, and both
    # implementations must agree on rejecting them for the SAME reason.
    (tmp_path / "background" / "false_friends.py").write_text(
        'from pathlib import Path\n'
        'ROOT = Path(".")\n'
        'FEED = ROOT / "docs" / "observability" / "feed.json"\n'
        'STAGED = ROOT / "docs" / "staging" / "THING.md"\n',
        encoding="utf-8")

    fast = saf.discover_maintained_surfaces(root=tmp_path)
    slow = _unfiltered_discovery(tmp_path)

    assert fast == slow, (
        "the prefiltered scan and the unfiltered walk disagree -- the speed-up narrowed the "
        f"control.\n  prefiltered: {fast}\n  unfiltered:  {slow}")

    # NOT A TAUTOLOGY: two empty dicts would satisfy the line above, and a scan that finds
    # nothing is this repo's recorded shape for a control that quietly stopped being one.
    assert "docs/status/PLAIN.md" in fast
    assert "docs/status/SPREAD.md" in fast, (
        "the multi-line declaration was lost -- the prefilter is keyed to the opening line "
        "instead of the node's whole span")
    assert not any(p.endswith(".json") for p in fast)


def test_the_prefilter_agrees_with_the_unfiltered_walk_ON_THE_REAL_TREE():
    """The synthetic tree above proves the shapes; this proves the TREE, which is the subject.

    IT COSTS THE 42s IT SAVED, and that is the right trade rather than an accident: it runs the
    slow reference implementation, and it is selected ONLY when `tools/startup_anchor_freshness.py`
    itself is staged, while the saving is paid back on every commit that stages any anchor. A
    prefilter's failure mode is "correct on every case I imagined", so the real tree -- 445
    modules nobody wrote a fixture for -- is the only thing that can grade it.
    """
    assert saf.discover_maintained_surfaces() == _unfiltered_discovery(saf.PROJECT)


def test_the_named_exemptions_are_still_undiscoverable():
    """`UNDISCOVERABLE` names surfaces the scan structurally cannot see -- a path assembled in two
    steps. The exemption must not outlive its reason: if one becomes discoverable it belongs in the
    ordinary set, and carrying it in both places would hide a real gap behind a hand-kept line."""
    found = saf.discover_maintained_surfaces()

    for rel in saf.UNDISCOVERABLE:
        assert rel not in found, f"{rel} is now discoverable -- drop its exemption"


def test_the_table_says_WHAT_EACH_ANCHOR_IS_FOR():
    """An age table orients nobody. The director asked for "whatever a new reader needs to orient
    today, in one place" -- so the rendered table carries the sentence beside each link, taken from
    the SAME line the path came from so the two cannot describe different anchors."""
    rows = saf.assess()
    table = saf.render(rows)

    assert "What it is for" in table
    assert "the reasoning behind a call" in table, "the stretch log's purpose must reach the reader"
    assert "orienting, read this table first" in table
