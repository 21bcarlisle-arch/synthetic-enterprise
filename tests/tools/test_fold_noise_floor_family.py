"""Controls on the noise-floor fold, each naming the defect it exists to catch.

THE DEFECT CLASS. Every way this join goes wrong produces a WELL-FORMED artefact: the fields are
right, the arithmetic is self-consistent, and the family is not one population. Two worlds joined,
a seed counted twice, two clocks joined -- none of them raises anything downstream, and the bound
they publish is read as a measurement. So the controls here are about refusals, and the first one
is about whether the fold and the producer even agree what a mean is.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tools.fold_noise_floor_family import FoldRefused, fold, main, summarise

_REPO = Path(__file__).resolve().parent.parent.parent
#: The real nine-seed family the Lane 0 selection leg is published from. Read, never rebuilt: a
#: synthetic fixture here would be a fixture fitted to the conclusion, and the whole point of the
#: first control is that the fold agrees with a summary IT DID NOT COMPUTE.
_LIVE_FLOOR = _REPO / "docs" / "observability" / "value_cycle_ab_s1_noise_floor.json"


def _live() -> dict:
    if not _LIVE_FLOOR.exists():
        pytest.skip("no live floor artefact on disk at {}".format(_LIVE_FLOOR))
    return json.loads(_LIVE_FLOOR.read_text(encoding="utf-8"))


def test_the_fold_reproduces_the_producers_own_summary_on_the_family_already_on_disk():
    """THE DEFECT: the fold computes a mean the producer would not have computed.

    `summarise` restates one line of `run_value_cycle_ab.noise_floor` (`abs(mean) > 2 * sem`) and
    imports the rest. A second implementation of one rule is this project's most expensive
    recurring shape -- the VAT rule had five, and a defect fixed in one of them in July was still
    live in another in August. This is the control that makes the two copies unable to drift
    silently: the fold's arithmetic, run over the real artefact's real rows, must return the
    figures that artefact already publishes.

    IT IS KEYED TO THE PROPERTY AND NOT TO TODAY'S ANSWER: nothing here names -1078.17 or n=9, so
    the day the family grows this control still asks the same question of the bigger one.
    """
    live = _live()
    got = summarise(live["seeds"])

    assert got["selection_gbp_spread"] == live["selection_gbp_spread"]
    assert got["level_share_spread"] == live["level_share_spread"]
    assert got["selection_sem_gbp"] == live["selection_sem_gbp"]
    assert (got["selection_distinguishable_from_zero"]
            == live["selection_distinguishable_from_zero"])


def test_summarise_moves_at_all_so_the_agreement_above_is_not_an_artefact_of_a_dead_function():
    """THE POISON ROUND for the control above. Without it, "the fold agrees with the producer" and
    "`summarise` returns something constant" read identically -- and a `summarise` that ignored its
    argument would pass the previous test on any artefact whose figures happened to be baked in.

    Perturbing one row must move the mean, the sem, and `n`."""
    live = _live()
    rows = copy.deepcopy(live["seeds"])
    before = summarise(rows)
    rows.append({**copy.deepcopy(rows[0]), "seed": -1, "selection_gbp": 500_000.0})
    after = summarise(rows)

    assert after["selection_gbp_spread"]["n"] == before["selection_gbp_spread"]["n"] + 1
    assert after["selection_gbp_spread"]["mean"] != before["selection_gbp_spread"]["mean"]
    assert after["selection_sem_gbp"] != before["selection_sem_gbp"]


# ---------------------------------------------------------------------------
# The refusals. Each fixture is the live artefact with ONE field changed, so what is under test is
# the field and not a hand-built family that differs from a real one in ways nobody enumerated.
# ---------------------------------------------------------------------------

def _two_sources(tmp_path: Path, mutate=None, seed_offset: int = 100):
    """The live floor, plus a copy of it with fresh seed numbers -- a legitimate pair by default.

    `mutate` is applied to the SECOND member only, so every refusal below is a one-variable change
    against a pair that is otherwise foldable. A fixture that differed in two ways would not tell
    us which refusal fired.
    """
    live = _live()
    first = tmp_path / "floor_a.json"
    first.write_text(json.dumps(live), encoding="utf-8")

    second_data = copy.deepcopy(live)
    for row in second_data["seeds"]:
        row["seed"] = row["seed"] + seed_offset
    if mutate is not None:
        mutate(second_data)
    second = tmp_path / "floor_b.json"
    second.write_text(json.dumps(second_data), encoding="utf-8")
    return [first, second]


def test_the_control_pair_folds_so_every_refusal_below_is_reachable(tmp_path):
    """THE PARTITION CONTROL, and it comes first for the reason CLAUDE.md gives: a guard that
    refuses EVERYTHING passes every test that only asks whether it refuses. Before asserting what
    each refusal rejects, assert the un-mutated pair is ACCEPTED -- otherwise all six below are
    green against a `fold` that raises unconditionally."""
    folded = fold(_two_sources(tmp_path))

    assert folded["selection_gbp_spread"]["n"] == 2 * len(_live()["seeds"])
    assert len(folded["folded_from"]) == 2
    assert folded["folded"] is True


def test_two_worlds_are_never_folded(tmp_path):
    """THE DEFECT: a spread measured over one departure level published as the error bar on a
    figure measured over another. The rows are field-identical, so nothing downstream can tell."""
    sources = _two_sources(
        tmp_path, lambda d: d["world_identity"].update({"digest": "deadbeefdeadbeef"}))
    with pytest.raises(FoldRefused, match="world identity digest"):
        fold(sources)


def test_two_clocks_are_never_folded(tmp_path):
    """THE DEFECT: `noise_floor` refuses a mixed-clock spread outright because the bad-debt gap
    between this run's two clocks is larger than every contrast the spread bounds. A fold that did
    not ask the same question would publish that gap as seed noise."""
    sources = _two_sources(tmp_path, lambda d: d.update({"clock": "billed-nominal"}))
    with pytest.raises(FoldRefused, match="clock"):
        fold(sources)


def test_two_redraw_modes_are_never_folded(tmp_path):
    """THE DEFECT: `only` and `except` PARTITION the variance `all` measures; neither half bounds
    the whole. Joining a partition to its own superset double-counts one side and publishes a
    bound that is too narrow in the flattering direction."""
    sources = _two_sources(tmp_path, lambda d: d["redraw_scope"].update({"mode": "only"}))
    with pytest.raises(FoldRefused, match="redraw mode"):
        fold(sources)


def test_a_seed_shared_by_two_runs_is_refused(tmp_path):
    """THE DEFECT, and the one that would have been believed: the same draw twice raises `n` and
    shrinks the standard error by a factor that measures nothing. `run_arms_rerun.check_seeds`
    refuses a repeat WITHIN one run and is structurally blind ACROSS two, which is exactly where a
    second batch reusing the default seed list would land."""
    sources = _two_sources(tmp_path, seed_offset=0)
    with pytest.raises(FoldRefused, match="appears in both"):
        fold(sources)


def test_a_missing_field_is_an_unknown_and_never_an_agreement(tmp_path):
    """THE DEFECT: treating an absent world digest as "agrees with anything", which makes the
    OLDEST artefact in a family -- the one predating the field -- the one that folds with
    everything."""
    sources = _two_sources(tmp_path, lambda d: d["world_identity"].pop("digest"))
    with pytest.raises(FoldRefused, match="carries no world identity digest"):
        fold(sources)


def test_folding_one_run_is_refused_because_that_is_a_file_copy(tmp_path):
    """THE DEFECT: a one-source "fold" is promote-by-copy wearing a measurement's name, and this
    repo already carries a census for that class."""
    with pytest.raises(FoldRefused, match="at least two runs"):
        fold(_two_sources(tmp_path)[:1])


def test_the_same_path_twice_is_refused(tmp_path):
    """THE DEFECT: the duplicate-seed guard reads seeds, and passing one path twice is the one
    route to a doubled family that a per-seed check would catch only incidentally. Named
    separately because its message must name the PATH -- a reader told "seed 11111 appears in both
    floor_a.json and floor_a.json" has to work out what happened."""
    same = _two_sources(tmp_path)[0]
    with pytest.raises(FoldRefused, match="more than once"):
        fold([same, same])


# ---------------------------------------------------------------------------
# What the fold refuses to CLAIM
# ---------------------------------------------------------------------------

def test_a_folded_family_names_no_single_producing_commit(tmp_path):
    """THE DEFECT: writing the newest batch's commit into `producing_commit.commit` because the
    field wants a value. `generate_value_arms_data._floor_tree_pairing` reads exactly that field
    to tell a reader whether the bound and the figure it bounds were drawn by the same code, and
    it is explicit that a missing stamp "is not evidence the trees agree". A fold that names one
    tree for rows several trees drew turns that honest unknown into a false match."""
    folded = fold(_two_sources(tmp_path))

    assert folded["producing_commit"]["commit"] is None
    assert "FOLDED" in folded["producing_commit"]["unavailable_because"]
    # And what the summary field gave up is still on disk, per member.
    assert [m["path"] for m in folded["folded_from"]]
    assert all("producing_commit" in m for m in folded["folded_from"])


def test_a_member_without_a_book_identity_makes_the_whole_family_state_none(tmp_path):
    """THE DEFECT: claiming the newest member's book for rows drawn over an unstated one.
    `book_identity` arrived on floors on 2026-09-09, so any family spanning that date has members
    that predate it -- and the flattering move is to let the one that answers speak for all."""
    sources = _two_sources(tmp_path, lambda d: d.pop("book_identity", None))
    # The live artefact may itself predate the field; ensure the FIRST member has one so this is
    # a one-variable test of the second member's absence.
    first = json.loads(sources[0].read_text(encoding="utf-8"))
    first["book_identity"] = {"digest": "abc123"}
    sources[0].write_text(json.dumps(first), encoding="utf-8")

    folded = fold(sources)
    assert folded["book_identity"]["digest"] is None
    assert "do not all name their book" in folded["book_identity"]["unavailable_because"]


def test_writing_the_fold_over_one_of_its_own_sources_is_refused(tmp_path):
    """THE DEFECT: `--out` pointed at a member. The fold succeeds, the file is well-formed, and
    `folded_from` then points at a path that no longer holds the rows it names -- so the join
    stops being reversible by reading."""
    sources = _two_sources(tmp_path)
    rc = main([str(sources[0]), str(sources[1]), "--out", str(sources[0])])
    assert rc == 2
    # And the source is untouched: a refusal that had already written is not a refusal.
    assert json.loads(sources[0].read_text(encoding="utf-8"))["seeds"] == _live()["seeds"]
