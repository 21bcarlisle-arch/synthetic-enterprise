"""A band verdict may only be read off a capture that ran under the anchors that are live.

THE DEFECT, 2026-09-03. `tools/measure_departure_level.py` reported the whole book **OUT OF BAND,
HIGH, in 8 of 8 years**, mean expected 22.35% against a published midpoint of 17.20% — "a world
that departs 1.3x harder than the GB record in every year the record covers". That reading reached
a direction file as its first-ranked item, whose instruction was to re-fit the anchor **downward**.

It was read off `docs/reports/c2_departure_factors.json`, and two things were true of that capture
that nothing in the tree could see:

  1. **Its two halves disagree with each other.** All 148 renewal rows match the live anchor block.
     Its 1221 SVT rows carry `sim_level_anchor` `3.053619` at 2022 against a live `1.0` — the
     reference year's anchor borrowed on the record's LOWEST year, which is the exact borrow
     `departure_level_anchor`'s own docstring says is wrong. A control that checked one half would
     have passed. That single stale year produced +8.53pp at 2022 and carried the whole of the
     apparent excess: strip it and c2's own remaining spread is +0.26 to +1.09pp.
  2. **Its SVT half was in no commit.** With the untracked sibling on disk the reading returns
     eight years; at a clean checkout of the same commit it returns a refusal. Same commit, same
     command, two answers — and the eight-year one is what was published into direction.

On the committed pair the world sits **below** the band in six of eight years and in band in one.
So the correcting move **raises** departures and the book gets **harder** to hold, which is the
opposite of what the drawn work assumed and the opposite tail from the one its trap detector was
about to be re-pointed at.

KEYED TO THE PROPERTY. Every test below drives synthesised rows or asks the live default whether it
passes. Not one names `c2`, `c4`, a year or an anchor value, because the sign of this error has
already flipped once and a control written against the sign we happened to have would have
certified the opposite one.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from simulation.departure_level_anchor import year_level_anchor
from tools import measure_departure_level as measure
from tools.departure_population import (
    stale_anchor_refusal,
    svt_sibling,
    untracked_capture_refusal,
)

LIVE_YEAR = 2020
LIVE = year_level_anchor(LIVE_YEAR)


def _row(anchor: float, year: int = LIVE_YEAR, **over) -> dict:
    row = {"customer_id": "acct-1", "event_date": f"{year}-06-01", "event_type": "renewal",
           "market_year": year, "sim_level_anchor": anchor}
    row.update(over)
    return row


# --------------------------------------------------------------------------- #
# The capture must have run under the world that is live now                   #
# --------------------------------------------------------------------------- #

def test_a_capture_that_MATCHES_the_live_anchors_is_not_refused():
    assert stale_anchor_refusal([_row(LIVE)], [_row(LIVE)]) is None


@pytest.mark.parametrize("recorded", [LIVE * 3.0, LIVE / 3.0])
def test_a_SUPERSEDED_anchor_is_refused_in_EITHER_direction(recorded):
    """The stale reading was HIGH and the committed one is LOW. A control keyed to the sign of the
    error we happened to have would have certified the opposite one, so it is keyed to
    disagreement.

    MUTATION (must fire): compare with `<` or `>` instead of `abs(...) >`.
    """
    refusal = stale_anchor_refusal([_row(recorded)], [_row(LIVE)])

    assert refusal is not None and "superseded level anchor" in refusal
    assert str(LIVE_YEAR) in refusal, "the refusal must name the year that disagrees"


def test_a_disagreement_in_the_SVT_HALF_ALONE_is_caught():
    """The c2 shape exactly: renewal rows all correct, SVT rows stale on one year. A reading of
    either half on its own passes. Both halves are checked because the pair is the subject.

    MUTATION (must fire): check `renewal_rows` only.
    """
    clean, stale = [_row(LIVE) for _ in range(148)], [_row(LIVE * 3.0) for _ in range(187)]

    assert stale_anchor_refusal(clean, []) is None
    assert stale_anchor_refusal(clean, stale) is not None
    assert "187 row(s)" in stale_anchor_refusal(clean, stale), (
        "the refusal states how much of the capture is affected, because one stale year out of "
        "ten is a different claim from all ten"
    )


def test_a_capture_that_CANNOT_SAY_which_world_it_ran_in_is_refused():
    """An absent column is not agreement. `sim_level_anchor` is what makes this checkable at all,
    and a capture without it certifies nothing.

    MUTATION (must fire): treat rows with no `sim_level_anchor` as matching.
    """
    bare = [{"customer_id": "a", "event_date": "2020-06-01", "market_year": 2020}]

    refusal = stale_anchor_refusal(bare, bare)

    assert refusal is not None and "no way" in refusal


def test_an_UNREADABLE_SVT_ROUTE_is_not_this_refusals_subject():
    """`account_denominator_refusal` already names that, with the warning the reader needs. A
    second refusal on the same cause sends whoever hits it looking for a stale anchor that is not
    there — the catalogued shape of a refusal naming a cause the checker never observed."""
    assert stale_anchor_refusal([_row(LIVE)], None) is None


def test_the_tolerance_is_a_FLOAT_REPRESENTATION_one_and_not_a_grace_band():
    """Captures record six decimals. A tolerance loose enough to absorb a real anchor change would
    be a band inside which staleness is tolerated, which is the thing this refuses."""
    from tools.departure_population import ANCHOR_AGREEMENT_TOLERANCE

    assert ANCHOR_AGREEMENT_TOLERANCE <= 1e-6
    assert stale_anchor_refusal([_row(LIVE + 1e-9)], [_row(LIVE)]) is None


# --------------------------------------------------------------------------- #
# The verdict must not depend on whose working tree it is read in              #
# --------------------------------------------------------------------------- #

def test_an_UNCOMMITTED_HALF_is_refused_and_the_missing_half_is_NAMED(tmp_path):
    """Same commit, same command, two answers. Both halves must be tracked, because either alone
    certifies nothing — on the capture that caused this the halves disagreed with each other.

    OUTSIDE THE REPOSITORY IS ITS OWN LEG, and the first draft of this got the right answer for
    the wrong reason: `git ls-files -- <path outside the worktree>` exits 128, so a capture in
    `/tmp` was refused with "git could not be asked". The control still FIRED, which is why
    nothing would ever have corrected the sentence — a refusal naming a cause the checker never
    observed, hidden behind a correct verdict.

    MUTATION (must fire): check the renewal table only.
    """
    loose = tmp_path / "not_in_the_repo.json"
    loose.write_text("[]", encoding="utf-8")

    refusal = untracked_capture_refusal(loose)

    assert refusal is not None and "in no commit" in refusal
    assert "outside the repository" in refusal, "the cause must be the one actually observed"
    assert str(loose) in refusal


def test_a_capture_INSIDE_the_repository_but_uncommitted_is_refused_by_GIT_and_named():
    """The ordinary case: a half git itself reports as untracked. Distinct from the leg above so
    that neither can pass on the other's reasoning — the outside-the-repo path never reaches git.

    NOTHING IS WRITTEN INTO THE TREE to test this. `git ls-files` answers about paths, not about
    files on disk, so an in-repo path that has never existed is exactly the shape being checked;
    a test that created a real file under `docs/reports/` could be swept into another lane's
    pathspec, which is the concurrency this project commits by pathspec to avoid.

    MUTATION (must fire): check the renewal table only.
    """
    from tools.departure_population import PROJECT

    base = PROJECT / "docs" / "reports" / "zz_capture_provenance_probe_never_written.json"

    refusal = untracked_capture_refusal(base)

    assert refusal is not None and "in no commit" in refusal
    assert "outside the repository" not in refusal, "this leg must go through git, not the path"
    assert svt_sibling(base).name in refusal, "the missing half is named, not just counted"


def test_UNRESOLVABLE_is_its_own_answer_and_is_not_silence(monkeypatch):
    """"I could not check whether this is reproducible" is not evidence that it is. The blast
    radius is bounded on purpose: it refuses one band verdict and leaves the renewal-route reading
    and its banner untouched.

    MUTATION (must fire): swallow the exception and return None.
    """
    import subprocess

    def _boom(*a, **k):
        raise OSError("git is not on the path")

    monkeypatch.setattr(subprocess, "run", _boom)

    refusal = untracked_capture_refusal(measure.DEFAULT_TABLE)

    assert refusal is not None and "could not be established" in refusal


# --------------------------------------------------------------------------- #
# Where it bites, and where it deliberately does not                           #
# --------------------------------------------------------------------------- #

def test_the_BAND_VERDICT_refuses_rather_than_reporting_a_number_off_a_stale_capture(tmp_path):
    """The whole point. `world_book_rate_pct` returned eight years off the stale capture and that
    is what reached a direction file. It now returns no years and a named cause.

    MUTATION (must fire): drop either refusal from `world_book_rate_pct`.
    """
    table = tmp_path / "stale_capture.json"
    rows = [_row(LIVE * 3.0, year=y, customer_id=f"a{i}", event_type="renewal")
            for i, y in enumerate(range(2017, 2025))]
    table.write_text(json.dumps(rows), encoding="utf-8")
    svt_sibling(table).write_text(json.dumps([]), encoding="utf-8")

    rates, refusal = measure.world_book_rate_pct(table)

    assert rates == {} and refusal is not None
    assert "superseded level anchor" in refusal


def test_the_LIVE_DEFAULT_passes_both_refusals_whatever_it_is_pointed_at():
    """THE ONE THAT KEEPS THIS HONEST, and it names no capture. A pointer can go stale again the
    moment the next capture lands; what stops that is that the default must satisfy the same two
    properties any other capture would have to.

    MUTATION (must fire): point `DEFAULT_TABLE` back at a capture with an untracked half or a
    superseded anchor.
    """
    path = Path(measure.DEFAULT_TABLE)
    rows = json.loads(path.read_text(encoding="utf-8"))
    from tools.departure_population import load_svt_decisions

    svt_rows, _ = load_svt_decisions(path)

    assert stale_anchor_refusal(rows, svt_rows) is None, (
        "the default capture did not run under the live anchor block"
    )
    assert untracked_capture_refusal(path) is None, (
        "the default capture is not fully committed, so its verdict is not reproducible"
    )
    rates, refusal = measure.world_book_rate_pct()
    assert refusal is None and rates, "the default capture yields no whole-book reading"


def test_the_FIT_is_not_gated_by_this_because_fitting_on_the_previous_anchors_is_what_a_fit_is():
    """`tools/fit_year_level_anchor.py` exists to read a capture taken under the PREVIOUS anchors
    and solve the next ones — the iteration `departure_level_anchor` states as capture -> fit ->
    capture. A refusal wired into the fit would forbid the only act that clears it, which is the
    catalogued shape of a wall with no door for a state it forbids.

    MUTATION (must fire): call either refusal from the fit tool.
    """
    import inspect

    from tools import fit_year_level_anchor as fit

    source = inspect.getsource(fit)

    assert "stale_anchor_refusal" not in source and "untracked_capture_refusal" not in source, (
        "the fit must be able to read a capture taken under the anchors it is replacing"
    )


# --------------------------------------------------------------------------- #
# The PAGE must refuse on the same grounds as the CONTROL                      #
# --------------------------------------------------------------------------- #


def test_the_printed_page_refuses_on_the_same_grounds_as_the_band_control(monkeypatch, capsys):
    """A refusal the control honours and the printed page ignores is not a refusal.

    THE DEFECT, 2026-09-03, and it is this file's own subject reproduced inside the repair for it.
    The three refusals above were added to `world_book_rate_pct` -- which the band control reads --
    and `main`, which is what a HUMAN reads, went on applying `account_denominator_refusal` alone.
    So when the re-fit landed the same day and made the default capture stale in 9 of its 10 years,
    the control correctly refused and the tool went on printing eight confident whole-book rows with
    `inside` at 2024 and no warning anywhere on the surface.

    THAT PRINTED TABLE IS WHERE THE ORIGINAL WRONG PREMISE CAME FROM. "The world departs 1.3x
    harder than the GB record in every year" was read off this page, not off the control, and it
    reached a direction file as a first-ranked item instructing a re-fit in the wrong direction.
    CLAUDE.md: "Fail closed, and say so on the surface. 'We cannot tell' is a result. It belongs on
    the page, not in a footnote."

    KEYED TO THE PROPERTY: names no capture, no year and no anchor value. It moves the LIVE block
    out from under whatever the default capture is, which is the one thing guaranteed to make any
    capture stale, in either direction of error.

    MUTATION (must fire): narrow `main`'s gate back to `account_denominator_refusal` alone, or drop
    `stale_anchor_refusal` from `book_reading_refusal`.
    """
    import simulation.departure_level_anchor as anchor_module

    real = anchor_module.year_level_anchor
    # Displace the live block from whatever produced the default capture. `stale_anchor_refusal`
    # imports the accessor INSIDE its body, so patching the module attribute reaches it.
    monkeypatch.setattr(anchor_module, "year_level_anchor", lambda year: real(year) + 1.0)

    rc = measure.main(["measure_departure_level.py", str(measure.DEFAULT_TABLE)])
    printed = capsys.readouterr().out

    assert rc == 0, "the instrument must still run and report, not crash, on a stale capture"
    assert "THE WHOLE BOOK" not in printed, (
        "the page printed a whole-book band verdict off a capture that did not run under the live "
        "anchor block -- the exact reading that reached a direction file with the sign inverted"
    )
    assert "superseded level anchor" in printed, (
        "the page dropped the whole-book table without saying why; a silent omission is how a "
        "reader concludes the section was never there rather than that it was refused"
    )


def test_the_page_and_the_control_take_their_verdict_from_one_gate():
    """The two must not be able to drift apart again, and on 2026-09-03 they had.

    The parity above is behavioural, but a future edit could satisfy it by copying the refusal trio
    into `main` -- which is how the two came apart in the first place, and is this repo's VAT shape:
    one requirement, several implementations, one of them repaired and the others left live.

    MUTATION (must fire): re-inline the refusal sequence in either caller.

    IT READS CALLS FROM THE AST AND NOT NAMES FROM THE TEXT, and the first draft of this test did
    the latter and was FAIL-OPEN on its own mutation: narrowing `main`'s gate back to
    `account_denominator_refusal` left the word `book_reading_refusal` sitting in the explanatory
    comment one line above, and a substring check counted that as the call. A control a comment can
    satisfy is the catalogued tautology.
    """
    import ast
    import inspect
    import textwrap

    def _calls(func) -> set[str]:
        tree = ast.parse(textwrap.dedent(inspect.getsource(func)))
        return {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }

    gate = _calls(measure.book_reading_refusal)
    for name in ("account_denominator_refusal", "stale_anchor_refusal", "untracked_capture_refusal"):
        assert name in gate, f"{name} is not CALLED by the shared gate, so one caller can miss it"

    for caller in (measure.main, measure.world_book_rate_pct):
        called = _calls(caller)
        assert "book_reading_refusal" in called, (
            f"{caller.__name__} does not CALL the shared gate"
        )
        assert not called & {"stale_anchor_refusal", "untracked_capture_refusal",
                            "account_denominator_refusal"}, (
            f"{caller.__name__} re-inlines a refusal instead of taking the shared gate, which is "
            f"how the page and the control came apart on 2026-09-03"
        )
