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


# ---------------------------------------------------------------------------------------------
# H47: the header's stated FIGURES, not only its date. Graded against the live repository on
# purpose -- the whole claim is that this sentence agrees with THIS project's sources, and a
# tmp_path repo would make every test below a statement about a fixture.
# ---------------------------------------------------------------------------------------------

def _live_header() -> str:
    return (saf.OVERVIEW).read_text(encoding="utf-8")


def test_the_startup_headers_figures_agree_with_the_sources_it_names():
    """THE CONTROL. The date sentence was gated and the four quantities beside it were not -- and
    in the incident that produced this module the date was 8 days out while the figures were out by
    3.7x, 15x and 2,905 tests. A session orienting on a hand-typed header was told it was working
    on a project a fifteenth of this one's size.

    Keyed to the property (each figure lies inside the range its own named source took over the
    window the date declares), never to today's number: it stays green as the repo grows and reds
    the moment a figure stops being computed.
    """
    rows = saf.figure_verdicts()

    assert {r["figure"] for r in rows} == set(saf.FIGURE_SOURCES), "a figure stopped being graded"
    assert saf.figure_refusals(rows) == [], (
        "the startup header states a figure its own source never carried: "
        + "; ".join(f"{r['figure']}={r['stated']:,} vs {r['band_low']:,}-{r['band_high']:,}"
                    for r in saf.figure_refusals(rows)))


def test_a_hand_typed_figure_is_refused_IN_EITHER_DIRECTION():
    """A control that only caught understatement would pass a header claiming 90,000 commits, and
    the failure that produced this module could have landed either way round -- the incident's own
    sentence was low on three figures and the same edit could as easily have been high.

    ONE assertion over the whole partition rather than a leg per direction: a refusal that refuses
    everything passes a per-direction test, and a control that can only reach one branch passes the
    other. Both verdicts must be REACHABLE from real mutations of the real header.
    """
    header = _live_header()
    low = header.replace("9,385 commits", "2,500 commits")
    high = header.replace("9,385 commits", "94,385 commits")
    assert low != header and high != header, "the mutation did not apply -- the header was reworded"

    verdicts = {r["figure"]: r["verdict"] for r in saf.figure_verdicts(low)}
    verdicts_high = {r["figure"]: r["verdict"] for r in saf.figure_verdicts(high)}

    assert verdicts["commits"] == "UNDERSTATES" and verdicts_high["commits"] == "OVERSTATES", (
        "both halves of the partition must be reachable")
    assert verdicts["tests"] == "AGREES", "only the mutated figure may move"


def test_deleting_a_figure_refuses_rather_than_leaving_nothing_to_disagree_with():
    """FAIL-CLOSED, and the cheapest possible silencing of this half of the check: a check that
    compares a stated number to its source is silenced by deleting the number, and an absent figure
    would otherwise read as a clean pass -- the same shape `MIN_ANCHORS` exists to stop."""
    stripped = _live_header().replace("9,385 commits. ", "")

    with pytest.raises(saf.AnchorRefusal) as exc:
        saf.stated_figures(stripped)
    assert "commits" in str(exc.value)


def test_a_figure_with_no_as_of_date_is_refused_because_it_cannot_be_falsified():
    """A quantity with no date is not a claim about anything: there is no window to compute the
    source over, so every value is as good as every other. Refuse rather than invent a window."""
    undated = _live_header().replace("*Last updated: 2026-09-05.", "*")

    with pytest.raises(saf.AnchorRefusal):
        saf.figure_verdicts(undated)


def test_the_band_is_COMPUTED_from_history_and_not_pinned_to_todays_repository():
    """The trap this project has entered repeatedly: a control pinned to the current answer goes
    red when the code becomes more honest and green when the claim rots. The band must MOVE with
    the date the header declares, or it is a hard-coded pair of numbers wearing a computation's
    clothes."""
    import datetime as _dt

    early = saf.figure_band(_dt.date(2026, 8, 1))
    late = saf.figure_band(_dt.date(2026, 9, 5))

    assert early["commits"][1] < late["commits"][0], "an earlier date must give an earlier band"
    assert early["modules"][1] < late["modules"][1], "the band tracks the repository, not a literal"


def test_a_figure_whose_source_did_not_exist_yet_is_UNGRADED_and_says_so():
    """Not every source is as old as the header. CLAUDE.md's Build line -- where the test count
    comes from -- exists only since the 2026-08-28 rewrite, so a window reaching further back has
    NO source for that figure rather than a wrong one.

    Refusing there would wedge on a document that is merely old and honest, which is precisely what
    the age half of this module refuses to do. Passing it silently would be worse: a reader would
    be told the figure was checked. So it is reported, and the route an author could abuse it by --
    back-dating the header past the source -- is closed by the LIES check, not by this leg.
    """
    import datetime as _dt

    header = _live_header().replace("*Last updated: 2026-09-05.", "*Last updated: 2026-08-01.")
    assert saf.figure_band(_dt.date(2026, 8, 1))["tests"] == (None, None)

    rows = {r["figure"]: r["verdict"] for r in saf.figure_verdicts(header)}
    table = saf._render_figures(saf.figure_verdicts(header))

    assert rows["tests"] == "UNGRADED"
    assert rows["commits"] != "UNGRADED", "git is as old as the repo -- those legs still grade"
    assert "no source existed over this window" in "\n".join(table)


def test_the_published_table_reports_the_figures_and_says_when_it_could_not():
    """Fail closed AND SAY SO ON THE SURFACE. A reader orienting on the header is entitled to the
    same reading the gate gets -- including the reading "this was not checked"."""
    rows = saf.assess()

    with_figures = saf.render(rows, figure_rows=saf.figure_verdicts())
    without = saf.render(rows, figure_rows=None)

    assert "The header's stated figures" in with_figures
    assert "AGREES" in with_figures and "could have said" in with_figures
    assert "treat them as hand-typed" in without, "an unchecked header must say it is unchecked"


def test_a_wrong_figure_actually_REFUSES_and_a_right_one_does_not(tmp_path):
    """MUTATION-FOUND GAP, 2026-09-16: every test above graded VERDICTS, and stubbing
    `figure_refusals` to return `[]` left all of them green -- the classification stayed perfect
    while the gate stopped refusing anything. A control that computes the right answer and does not
    act on it is a fail-open, and it is invisible to any test that stops at the verdict.

    Both halves in one assertion, over the same live tree: a clean copy must exit 0 and a copy with
    one hand-typed figure must exit 1. Asserting only the refusal would be satisfied by a check that
    refuses everything, and this pair cannot be.
    """
    clean = tmp_path / "clean.md"
    clean.write_text(_live_header())
    wrong = tmp_path / "wrong.md"
    wrong.write_text(_live_header().replace("9,385 commits", "2,500 commits"))

    verdicts = (saf.main(["--check", "--overview", str(clean)]),
                saf.main(["--check", "--overview", str(wrong)]))

    assert verdicts == (0, 1), (
        "the header's own figures must decide the exit code: (clean, hand-typed) was "
        f"{verdicts}. A 0 on the right is a gate that computes a refusal and drops it; a 1 on the "
        "left means the live tree is refusing for some other reason -- read the stderr above.")
