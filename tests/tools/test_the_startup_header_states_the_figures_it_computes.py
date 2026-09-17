"""H47: the startup header states four FIGURES, and only its date was ever graded.

Each test named by the defect it exists to catch, and driven against the LIVE repository rather
than a fixture -- the whole claim is that this project's own orientation sentence agrees with this
project's own sources, and a tmp_path repo would make every test here a statement about a fixture.
That is the opposite convention from `test_startup_anchor_freshness.py` beside it, which builds
real repos in tmp_path because its subject is the disagreement between a file and git. Same module
under test, two different subjects, and the fixture follows the subject.

WHY A FILE OF ITS OWN and not eight more functions in that suite. The delivery grader dates a
control by the BIRTH of the file holding it (`level_zero_contradicted_by_its_own_controls
.controls_older_than_the_row`, `git log --follow`), so a control written for a row and appended to
a file older than that row is read as evidence about some earlier row -- all-or-nothing over the
whole file. Appending here was tried first and the grader said exactly that. The file granularity
is a known limitation with its own filed finding
(`WORKER_FINDING_THE_PREDATES_RULE_IS_ALL_OR_NOTHING_OVER_A_FILE...`); this file is not a way
around it but the shape it asks for, and it is this project's own convention anyway -- a `test_*`
named for the defect it catches.
"""
from __future__ import annotations

import datetime as dt

import pytest

from tools import startup_anchor_freshness as saf


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
        + "; ".join(f"{r['figure']}={r['stated']:,} vs "
                    + ("no band -- " + r["verdict"] if r["band_low"] is None
                       else f"{r['band_low']:,}-{r['band_high']:,}")
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
    early = saf.figure_band(dt.date(2026, 8, 1))
    late = saf.figure_band(dt.date(2026, 9, 5))

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
    header = _live_header().replace("*Last updated: 2026-09-05.", "*Last updated: 2026-08-01.")
    assert saf.figure_band(dt.date(2026, 8, 1))["tests"] == (None, None)

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


def test_a_HEDGED_figure_is_still_a_figure_and_is_still_graded():
    """EXPERT HOUR, 2026-09-17. The blind reviewer's hardest question was "would this have caught
    the last real error?", and replaying it answered NO for half the sentence. The header that cost
    a session its bearings said `2,500+ commits ... 360+ Python modules`, and a pattern that ended
    the number at `[\\d,]+` saw NO FIGURE THERE -- so the replay refused by the unstated-figure leg
    while the OVERSTATES/UNDERSTATES machinery, which is the whole substance of this module, was
    never reached by the only real instance of the defect it exists for.

    The trailing `+` is where this class LIVES: it is exactly how a person types a number they
    already know is going stale. `~` and `over` never had the problem because they sit to the LEFT
    of the digits, which is why the gap survived a reading of the patterns.

    BOTH HALVES IN ONE ASSERTION over the same hedge, because a pattern that accepted the hedge and
    then graded nothing would pass a test that only checked the true figure, and one that refused
    every hedge would pass a test that only checked the false one.
    """
    header = _live_header()
    honest = header.replace("9,385 commits", "9,000+ commits")
    stale = header.replace("9,385 commits", "2,500+ commits")
    assert honest != header and stale != header, "the mutation did not apply -- header reworded"

    seen = (saf.stated_figures(honest)["commits"], saf.stated_figures(stale)["commits"])
    graded = ({r["figure"]: r["verdict"] for r in saf.figure_verdicts(honest)}["commits"],
              {r["figure"]: r["verdict"] for r in saf.figure_verdicts(stale)}["commits"])

    assert seen == (9000, 2500), f"a hedged figure must still be READ as a figure, got {seen}"
    assert graded == ("AGREES", "UNDERSTATES"), (
        f"a hedged figure must still be GRADED, and the hedge cannot rescue a 3.7x miss: {graded}")


def test_a_source_TAKEN_AWAY_refuses_while_one_that_never_existed_stays_UNGRADED(tmp_path,
                                                                                monkeypatch):
    """EXPERT HOUR, 2026-09-17 -- the reviewer's named escape hatch, and it was open.

    `UNGRADED` was computed dynamically from "the band has no floor", and both causes of a floorless
    band landed on it: a source that did not exist that far back (honest, and the reader is owed the
    reading) and a source that WAS readable at the start of the window and is not readable now. The
    second is not the passage of time -- somebody changed something -- and it is reachable by one
    edit: the test figure's source is matched on a literal `**Build:**`, the pre-2026-08-28 spelling
    `Build:` returns None, and an audit has already deleted that line once before. One reword of one
    line in another document and this leg switched itself off, with a green gate and a published
    table telling the reader the figure merely could not be checked.

    The module's own note closed the BACK-DATING route to `UNGRADED` and pointed at the LIES check
    to do it. LIES grades the date of the header's own document and can see nothing about a source
    living in a different one, so it was never going to reach this.

    ONE ASSERTION OVER THE WHOLE PARTITION: taken-away refuses AND never-existed does not. A rule
    that refused every floorless band would pass the first half and fail the second, and that rule
    would wedge every commit on a document that is merely old and honest.
    """
    overview = tmp_path / "OVERVIEW.md"
    overview.write_text(_live_header(), encoding="utf-8")
    real_at = saf._figures_at
    # Patch the SOURCE side only. The header on disk is untouched and every other figure still
    # grades against real git, so a stub that broke the whole path would red the other three legs
    # rather than quietly satisfying this one.
    calls = {"n": 0}

    def _end(kill_high: bool, kill_low: bool):
        def fake(rev):
            out = dict(real_at(rev))
            calls["n"] += 1
            if (calls["n"] == 1 and kill_low) or (calls["n"] == 2 and kill_high):
                out["tests"] = None
            return out
        return fake

    def _verdict(*, kill_high: bool, kill_low: bool) -> tuple[str, int]:
        calls["n"] = 0
        monkeypatch.setattr(saf, "_figures_at", _end(kill_high, kill_low))
        # The REAL one, so it cannot perturb the call ordering the fake keys on. It only runs at
        # all when the window's late end IS head, and a `None` high survives the max() either way.
        monkeypatch.setattr(saf, "_figures_in_working_tree", lambda: dict(real_at("HEAD")))
        rows = saf.figure_verdicts(overview.read_text(encoding="utf-8"))
        calls["n"] = 0
        return ({r["figure"]: r["verdict"] for r in rows}["tests"],
                saf.main(["--check", "--overview", str(overview)]))

    taken_away = _verdict(kill_high=True, kill_low=False)
    never_existed = _verdict(kill_high=True, kill_low=True)

    assert taken_away == ("SOURCE_GONE", 1) and never_existed == ("UNGRADED", 0), (
        "a source readable at the start of the window and gone at the end must REFUSE, and one "
        f"that never existed must stay an honest unchecked reading: {taken_away} / "
        f"{never_existed}. Equal verdicts here mean the two causes were merged again.")
