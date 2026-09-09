"""THE DEFECT: a census disposition closed on "same shape as `X`" instead of on its own carrier,
and it read as asked-and-answered, so nothing ever re-asked it.

The 2026-09-05 delivery-seat re-audit opened the eight rows that had closed that way. SEVEN were
wrong about their own carrier and NOT ONE was wrong about the verdict -- which is exactly why they
would never have been re-opened: a right verdict on a wrong reason looks identical to a graded row,
and the reason is the only part a later reader can check. The rule that came out of it went into
`_scope_of_resemblance` as prose, in the same file, beside the prose that had just cost 33 `loader`
annotations nine hours after they landed. Prose has no falsifier. This is the falsifier.

WHAT EACH TEST HERE WOULD CATCH IF `rows_graded_by_resemblance()` REGRESSED -- each names its own
defect rather than asserting the current answer:

  * dropping the citation half        -> a row citing a sibling and naming nothing of its own passes
  * dropping the own-carrier half     -> naming an INNER or SHARED helper counts as opening the row,
                                         which is precisely how `.atom_stall_tracker.json` hid a
                                         fourth reader that was NOT on the shared loader
  * checking the fields JOINTLY       -> a `why` that concludes on a sibling is rescued by a
                                         `loader` written a day later by a different pass
  * a `null` field                    -> `str(None)` is truthy, so the guard falls open
  * keying to a remembered row set    -> the rung goes red when the file becomes more honest
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))

from background import self_clearing_alarm_census as census  # noqa: E402


def _census(path: str, writers: list[str], readers: list[str]) -> dict:
    """A census with ONE hit, shaped exactly as `derive()` emits it."""
    return {
        "hits": [path],
        "state_paths": {
            path: {"writers": writers, "readers": readers, "hit": True},
            # A second path so there is something for a row to CITE. It is never the hit.
            "sibling_state.json": {"writers": ["background/other.py::_save_sibling"],
                                   "readers": ["background/other.py::_load_sibling"],
                                   "hit": False},
        },
    }


CENSUS = _census("carrier_state.json",
                 writers=["background/carrier.py::_save_carrier_state"],
                 readers=["background/carrier.py::_load_carrier_state"])


def test_a_row_that_cites_a_sibling_and_names_none_of_its_own_carriers_is_refused():
    """THE DEFECT: the shape of all eight re-audited rows -- a reason that DEFERS.

    Without this leg `undispositioned()` is satisfied ("same shape as X" is a non-empty reason)
    and the row joins the class looking settled."""
    rows = {"carrier_state.json": {
        "verdict": "benign",
        "why": "A latest-value watermark. Same shape as `sibling_state.json`.",
        "loader": "Asked via `_load_carrier_state`: absent and unreadable are told apart.",
    }}
    out = census.rows_graded_by_resemblance(CENSUS, rows)
    assert len(out) == 1, out
    assert "carrier_state.json [why]" in out[0]
    assert "sibling_state.json" in out[0]


def test_naming_the_shared_helper_instead_of_this_paths_own_carrier_does_not_satisfy_it():
    """THE DEFECT the rung was BUILT on, and the reason 'names a function' is not enough.

    `.atom_stall_tracker.json` closed on "already on `load_episode_prior`. Same as
    `.supervisor_stuck_state.json`" -- true of its three supervisor readers, FALSE of
    `generate_maturity_map_data._load_stall_state`, which hand-rolled the loader, failed open to
    `{}` on a corrupt read, and published `"stalled": false` for every atom. A check that accepted
    any plausible function name would have passed that row; only the DERIVED attribution catches
    it, because the shared helper is not a carrier of this path."""
    rows = {"carrier_state.json": {
        "verdict": "benign",
        "why": ("Already on `load_episode_prior`, so absent and unreadable are told apart. "
                "Same as `sibling_state.json`."),
    }}
    assert census.rows_graded_by_resemblance(CENSUS, rows), (
        "naming the shared helper -- which is not a carrier the census attributes to this path -- "
        "was accepted as opening the row")


def test_a_row_that_names_its_own_carrier_may_cite_a_sibling_to_corroborate():
    """THE CONTROL OVER THE WHOLE PARTITION: the rule permits corroboration, and a rung that
    refused EVERY citation would pass the leg above while forbidding the honest shape -- the
    'a guard that refuses everything passes all its tests' trap."""
    rows = {"carrier_state.json": {
        "verdict": "benign",
        "why": ("`_save_carrier_state` overwrites a latest-value stamp and `_load_carrier_state` "
                "reads it; no episode is stored. `sibling_state.json` agrees for the same reason."),
    }}
    assert census.rows_graded_by_resemblance(CENSUS, rows) == []


def test_a_row_citing_nothing_is_not_this_rungs_business():
    """The other half of the partition. Three of the eight rows the hand re-audit found wrong
    cited no sibling at all -- they made a false claim about their own carrier -- and this rung
    deliberately does not fire on them. Asserting that keeps the rung's scope honest instead of
    letting a later reader assume it covers the whole class."""
    rows = {"carrier_state.json": {"verdict": "benign", "why": "An append-only log."}}
    assert census.rows_graded_by_resemblance(CENSUS, rows) == []


def test_each_field_stands_on_its_own_carrier():
    """THE DEFECT: a `why` that concludes on a sibling, rescued by a `loader` a different pass
    wrote a day later. Checking the concatenation would pass this row -- and the `why` is what a
    later reader reads first."""
    rows = {"carrier_state.json": {
        "verdict": "benign",
        "why": "Same reasoning as `sibling_state.json`.",
        "loader": "`_load_carrier_state` tells absent from unreadable.",
    }}
    out = census.rows_graded_by_resemblance(CENSUS, rows)
    assert len(out) == 1 and "[why]" in out[0], out


def test_the_loader_field_is_held_to_the_same_bar_as_the_why():
    """Both fields, or the class walks out through the one that is not checked -- which is how the
    `loader` annotations were lost while every rung above stayed green."""
    rows = {"carrier_state.json": {
        "verdict": "benign",
        "why": "`_save_carrier_state` overwrites a stamp; no episode is stored.",
        "loader": "Same shape as `sibling_state.json`, and clean for the same reason.",
    }}
    out = census.rows_graded_by_resemblance(CENSUS, rows)
    assert len(out) == 1 and "[loader]" in out[0], out


def test_naming_the_SIBLINGS_carrier_is_not_naming_your_own():
    """THE DEFECT, and the one the fixture above cannot reach by accident: a row that DOES name a
    function -- the sibling's -- and none of its own.

    This is `.sanity_daemon_last_digest_date` verbatim. Its re-graded reason argued from
    `daily_self_note.already_ran_today` and `boot_announce.already_announced_this_boot`, both real
    readers of the SIBLING path, and never named `sanity_daemon._last_digest_date`. A rung that
    accepted a carrier of ANY census path would pass it, and the paragraph would keep arguing about
    somebody else's code."""
    cen = _census("carrier_state.json",
                  writers=["background/carrier.py::_save_carrier_state"],
                  readers=["background/carrier.py::_load_carrier_state"])
    rows = {"carrier_state.json": {
        "verdict": "benign",
        "why": ("`_load_sibling` in `sibling_state.json` reads its stamp under `except OSError`, "
                "and this one is the same."),
    }}
    assert census.rows_graded_by_resemblance(cen, rows), (
        "the row named the SIBLING's reader and none of its own, and was accepted")


def test_a_carrier_name_inside_a_longer_identifier_does_not_count_as_naming_it():
    """THE DEFECT, the mirror of the citation-boundary one and the fail-open direction of the pair:
    match the carrier name by substring and an UNRELATED identifier that happens to contain it lets
    a deferring row through. `hit_rate` is a real reader of `naive_organ_log.jsonl`; a row that
    mentions a `hit_rate_window` has named nothing at all."""
    cen = _census("carrier_state.json",
                  writers=["background/carrier.py::_save_carrier_state"],
                  readers=["background/carrier.py::hit_rate"])
    rows = {"carrier_state.json": {
        "verdict": "benign",
        "why": ("The `hit_rate_window` tuning is unrelated. Same shape as `sibling_state.json`."),
    }}
    assert census.rows_graded_by_resemblance(cen, rows), (
        "`hit_rate_window` was accepted as naming the carrier `hit_rate`")


@pytest.mark.parametrize("blank", [None, "", "   "])
def test_a_blank_field_is_the_loader_rungs_refusal_not_this_ones(blank):
    """Two rungs refusing the same absence is how a refusal gets fixed in one place and stays live
    in the other.

    AN EQUIVALENCE, ESTABLISHED BY MUTATION AND RECORDED RATHER THAN LEFT FLATTERING: removing the
    `or ""` before `str` -- the trap that made a mandatory reason fall open one rung above -- does
    NOT change this rung's answer, because "None" and "" both cite nothing, so the guard has
    nowhere to fall open TO. The `or ""` is kept for consistency with the two rungs above, where it
    IS load-bearing, and this leg pins the OUTCOME (a blank field is silent here) rather than
    pretending to falsify a line that cannot fail."""
    rows = {"carrier_state.json": {
        "verdict": "benign",
        "why": "`_save_carrier_state` overwrites a stamp; no episode is stored.",
        "loader": blank,
    }}
    assert census.rows_graded_by_resemblance(CENSUS, rows) == []


def test_a_path_name_inside_a_longer_token_is_not_a_citation():
    """THE DEFECT: `.lock` is a substring of `.lockfile`, `.locks/` and any longer path built on it.
    Match by substring and the rung fires on rows that cite nothing; it gets read as noise and
    switched off, which is how a control dies without anyone deciding to remove it."""
    cen = _census("carrier_state.json",
                  writers=["background/carrier.py::_save_carrier_state"],
                  readers=["background/carrier.py::_load_carrier_state"])
    cen["state_paths"][".lock"] = {"writers": [], "readers": [], "hit": False}
    rows = {"carrier_state.json": {
        "verdict": "benign",
        "why": "Each worker holds its own `.lockfile`; nothing here stores an episode.",
    }}
    assert census.rows_graded_by_resemblance(cen, rows) == [], (
        "`.lockfile` was read as a citation of the `.lock` row")


def test_a_hit_with_no_row_is_left_to_the_undispositioned_rung():
    """Two rungs refusing the same thing is how a refusal gets fixed in one place and stays live
    in the other -- this project's most expensive recurring shape."""
    assert census.rows_graded_by_resemblance(CENSUS, {}) == []


def test_the_rung_is_not_keyed_to_the_rows_it_first_found():
    """KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. A rung carrying the list of rows the hand
    re-audit happened to find would go GREEN on a brand-new row committing the same defect, and
    RED when a listed row was repaired -- exactly backwards. The subject here is any hit; a path
    the rung has never seen is judged by the same bar."""
    cen = _census("brand_new_state.json",
                  writers=["background/newcomer.py::_save_new_state"],
                  readers=["background/newcomer.py::_load_new_state"])
    rows = {"brand_new_state.json": {"verdict": "benign",
                                     "why": "Same shape as `sibling_state.json`."}}
    assert census.rows_graded_by_resemblance(cen, rows), (
        "a path the rung has never seen must be held to the same bar as the eight it was built on")


def test_the_live_dispositions_file_has_no_row_graded_by_resemblance():
    """THE LIVE LEG. Slow (it derives the census over the tree), and it is the one that would have
    caught the real defect: on its first run this refused four rows, one of which was publishing
    'no atom is stalled' off an unreadable tracker.

    THE VACUITY LEG FIRST, and it is not decoration: `rows_graded_by_resemblance()` returns [] over
    a census with no hits, so a derivation that goes blind turns this assertion GREEN. That is the
    fail-open shape the whole module is named after, reached through its own test."""
    cen = census.derive()
    assert census.census_is_vacuous(cen) is None, census.census_is_vacuous(cen)
    disp = census.load_dispositions()
    examined = [h for h in cen["hits"] if isinstance(disp.get(h), dict)]
    assert len(examined) > 20, (
        "only {} hits carry a row -- this leg would pass by examining almost nothing".format(
            len(examined)))
    assert census.rows_graded_by_resemblance(cen) == []


def test_the_prose_rule_points_at_this_enforcement():
    """A rule stated in prose beside its enforcement, with nothing linking them, is how the next
    author re-writes the file and deletes the annotations again. `_scope_of_resemblance` must name
    the function, so a reader arriving at the prose is told where the falsifier is."""
    data = json.loads((PROJECT / "docs" / "design"
                       / "self_clearing_alarm_dispositions.json").read_text())
    assert "rows_graded_by_resemblance" in data["_verdicts"]["_scope_of_resemblance"]
