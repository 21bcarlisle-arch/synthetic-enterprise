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
from tools.run_value_cycle_ab import sems_to_state_a_sign

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

    `summarise` used to restate one line of `run_value_cycle_ab.noise_floor` (`abs(mean) > 2 * sem`)
    and import the rest. A second implementation of one rule is this project's most expensive
    recurring shape -- the VAT rule had five, and a defect fixed in one of them in July was still
    live in another in August. This is the control that makes the two copies unable to drift
    silently: the fold's arithmetic, run over the real artefact's real rows, must return the
    figures that artefact already publishes.

    THE RESTATEMENT IS GONE SINCE 2026-09-18 and this control did not become redundant with it.
    Both homes now call `sems_to_state_a_sign`, so the BAR cannot drift -- but `summarise` still
    computes the mean, the standard error and the comparison itself, and every one of those is a
    place the two can part company. What changed is that one class of drift is now impossible by
    construction instead of being caught here after the fact.

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


def test_the_folds_bar_is_the_one_the_family_size_earns_and_is_published_beside_the_verdict():
    """THE DEFECT: a verdict graded at a bar nobody can re-derive from the artefact.

    Fires on: re-freezing this fold's bar to any constant -- 2, 1.96, anything. A constant returns
    the same value at every family size, so the assertion below that the published bar IS
    `sems_to_state_a_sign(n)` is exactly the property a literal cannot have.

    WHY IT IS ASSERTED HERE AND NOT ONLY THROUGH THE VERDICT. Re-freezing the bar to 2.0 is an
    EQUIVALENCE on every floor artefact currently on disk: all twelve were re-graded under both
    rules on 2026-09-18 and not one verdict flips, so a control that only watched the boolean
    would stay green through the exact mutation this change exists to prevent. Establishing which
    of "missing test" and "equivalence" a silent mutation is, is this repository's rule; this is
    the missing test, and it is keyed to the bar rather than to the answer for that reason.

    ONE BAR FOR EVERY LEG, which is the other half. The contrast between the level leg's verdict
    and the selection leg's is only a claim about the legs if both were asked the same question.
    """
    rows = _eighteen()["seeds"]
    got = summarise(rows)
    n = got["selection_gbp_spread"]["n"]
    earned = sems_to_state_a_sign(n)
    assert earned is not None, "the family on disk has no degrees of freedom to spend"
    assert got["selection_sems_needed_to_state_a_sign"] == earned, (
        "the fold published a bar that is not the one its own {} draws earn, so the verdict "
        "beside it was graded by a rule a reader holding the artefact cannot re-derive".format(n))
    bars = {leg: got[leg]["sems_needed_to_state_a_sign"]
            for leg in ("selection_leg", "level_leg", "value_leg")}
    assert set(bars.values()) == {earned}, (
        "the three legs were graded at different bars, so the contrast between their verdicts is "
        "an artefact of the rule rather than of the data: " + str(bars))
    # AND IT MOVES WITH THE FAMILY. A constant survives every assertion above at one n.
    half = summarise(rows[:len(rows) // 2])
    assert half["selection_sems_needed_to_state_a_sign"] != earned, (
        "the bar did not move when the family halved, so it is a written-down number wearing a "
        "derivation's name")
    assert half["selection_sems_needed_to_state_a_sign"] > earned, (
        "a smaller family was given a LOOSER bar, which is backwards: fewer draws buy less "
        "certainty about the standard error, so the tail is wider")


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
    # a one-variable test of the second member's absence. It is the PRODUCER's shape and not an
    # invented one: this fixture used to write `{"digest": "abc123"}`, a key no producer of a
    # floor book block has ever emitted, and a control whose fixture is unreachable in the field
    # cannot tell a live defect from a live pass. See the reachability control below.
    first = json.loads(sources[0].read_text(encoding="utf-8"))
    first["book_identity"] = _A_DECLARED_BOOK
    sources[0].write_text(json.dumps(first), encoding="utf-8")

    folded = fold(sources)
    assert folded["book_identity"]["digest"] is None
    assert "do not all name their book" in folded["book_identity"]["unavailable_because"]


#: The producer's own shape for a floor that DID observe its book, as `floor_book_identity` writes
#: it. Kept beside the controls that use it so a reader can see there is no `digest` in it.
_A_DECLARED_BOOK = {
    "declared": {
        "served_segments": ["resi", "SME"],
        "served_segments_resolved_from": "curriculum",
        "served_segments_override_env": None,
    },
    "seeds_reconciled": 9,
    "seeds_that_recorded_no_book": 0,
    "unavailable_because": None,
    "realised_across_seeds": {"billing_accounts_settled_in_window": {"min": 164, "max": 164,
                                                                     "n": 9}},
}


def test_a_family_whose_members_all_declare_one_book_NAMES_it(tmp_path):
    """THE DEFECT, and it was live on the published page: the fold took its agreement over
    `book_identity.digest`, which `run_value_cycle_ab.floor_book_identity` -- the only thing that
    writes a floor's book block -- has never emitted. So the success branch could not be reached
    by any real pair. Both members of the served 18-seed family declare `['resi', 'SME']` from the
    curriculum, and the fold published `the folded runs name 1 different books (None)` and dropped
    `declared`, which is the ONLY key `generate_value_arms_data._floor_book_admission` reads. The
    page then admitted its own error bar on a date-ordering stamp proxy while the book sat agreed
    in both members.

    THIS IS THE PARTITION CONTROL FOR THE BOOK BRANCHES, in the shape CLAUDE.md asks for: a guard
    that answers `unknown` to EVERYTHING passes both refusal tests around it, and until this
    assertion existed that is exactly what it did."""
    sources = _two_sources(tmp_path)
    for path in sources:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["book_identity"] = copy.deepcopy(_A_DECLARED_BOOK)
        path.write_text(json.dumps(data), encoding="utf-8")

    book = fold(sources)["book_identity"]

    assert book["unavailable_because"] is None
    assert book["declared"] == _A_DECLARED_BOOK["declared"], (
        "the folded family must carry the declared book forward -- it is what the consumer pairs "
        "on, and a family that drops it is admitted on a proxy instead")
    assert book["folded_over_members"] == 2
    # The seed counts are SUMMED, not inherited from the first member: a family of 18 that says it
    # reconciled 9 is a count over a third of its own rows.
    assert book["seeds_reconciled"] == 2 * _A_DECLARED_BOOK["seeds_reconciled"]
    # ...and the realised half is NOT carried, because each member measured it over its own seeds.
    assert "realised_across_seeds" not in book
    assert book["realised_across_seeds_unavailable_because"]


def test_two_declared_books_are_never_folded_into_one(tmp_path):
    """THE DEFECT: rows drawn over a resi-only book pooled with rows drawn over resi+SME, and the
    family naming one of the two. The spread of two populations is not an error bar on either."""
    sources = _two_sources(tmp_path)
    for path, segments in zip(sources, (["resi", "SME"], ["resi"])):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["book_identity"] = copy.deepcopy(_A_DECLARED_BOOK)
        data["book_identity"]["declared"]["served_segments"] = segments
        path.write_text(json.dumps(data), encoding="utf-8")

    book = fold(sources)["book_identity"]

    assert book["digest"] is None
    assert "2 different books" in book["unavailable_because"]


def test_a_book_block_that_declares_nothing_is_an_unknown_and_not_an_agreement(tmp_path):
    """THE DEFECT: `floor_book_identity` fails closed to `declared: None` when a seed inside the
    run recorded no book. That block is truthy, so a `not (data.get("book_identity") or {})` test
    sails past it -- and a set of one `None` is a set of size one, which reads as agreement. The
    two unknowns must not collapse into the flattering branch."""
    sources = _two_sources(tmp_path)
    for path in sources:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["book_identity"] = copy.deepcopy(_A_DECLARED_BOOK)
        path.write_text(json.dumps(data), encoding="utf-8")
    second = json.loads(sources[1].read_text(encoding="utf-8"))
    second["book_identity"]["declared"] = None
    second["book_identity"]["unavailable_because"] = "3 of 9 seeds recorded no book"
    sources[1].write_text(json.dumps(second), encoding="utf-8")

    book = fold(sources)["book_identity"]

    assert book["digest"] is None
    assert "declaring no population" in book["unavailable_because"]
    assert "floor_b.json" in book["unavailable_because"], (
        "an unknown that does not name the member responsible cannot be acted on")


def test_writing_the_fold_over_one_of_its_own_sources_is_refused(tmp_path):
    """THE DEFECT: `--out` pointed at a member. The fold succeeds, the file is well-formed, and
    `folded_from` then points at a path that no longer holds the rows it names -- so the join
    stops being reversible by reading."""
    sources = _two_sources(tmp_path)
    rc = main([str(sources[0]), str(sources[1]), "--out", str(sources[0])])
    assert rc == 2
    # And the source is untouched: a refusal that had already written is not a refusal.
    assert json.loads(sources[0].read_text(encoding="utf-8"))["seeds"] == _live()["seeds"]


# ---------------------------------------------------------------------------
# THE LEVEL LEG -- the half of the split nothing summarised until 2026-09-17
# ---------------------------------------------------------------------------
#
# THE DEFECT THESE EXIST TO CATCH, and it is not a missing feature. `level_advantage_gbp` has been
# in every seed row of every floor ever written, and `summarise` read `selection_gbp` alone. So the
# surface published "the level-versus-selection split cannot be read" while one of its two legs had
# a determined sign sitting in the rows. A leg nobody summarises is indistinguishable, from every
# consumer's side, from a leg with nothing in it -- and the reading it was hiding is the
# UNFLATTERING one, which is the direction an omission is least likely to be noticed in.

#: The two nine-seed floors with DISJOINT seed values. The pair matters: `_20260910.json` re-runs
#: `_20260909b.json`'s own seeds under a different tree, so folding those two is one family counted
#: twice and the fold refuses it. See `test_the_two_floors_that_share_seed_values_are_refused`.
_FLOOR_A = _REPO / "docs" / "observability" / "value_cycle_ab_s1_noise_floor_20260909b.json"
_FLOOR_B = _REPO / "docs" / "observability" / "value_cycle_ab_s1_noise_floor_20260910b.json"
_SAME_SEEDS_AS_A = _REPO / "docs" / "observability" / "value_cycle_ab_s1_noise_floor_20260910.json"


def _eighteen() -> dict:
    for path in (_FLOOR_A, _FLOOR_B):
        if not path.exists():
            pytest.skip("no floor artefact on disk at {}".format(path))
    return fold([_FLOOR_A, _FLOOR_B])


def test_both_legs_are_summarised_and_neither_verdict_is_hardcoded():
    """THE DEFECT: a summary that reports one leg and silently drops the other.

    KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Nothing here asserts that the level leg is
    positive or that the selection leg is not -- those are results, and pinning them would make
    this control go red on the day the book changes and the page becomes MORE honest. What is
    asserted is that both legs are asked, that each carries the fields a reader needs to re-judge
    it, and that the two were judged by the same rule.
    """
    got = summarise(_eighteen()["seeds"])

    for leg in ("selection_leg", "level_leg", "value_leg"):
        block = got[leg]
        assert block["spread"]["n"] == 18, leg
        assert block["distinguishable_from_zero"] in (True, False), leg
        assert block["sem_gbp"] is not None and block["sem_gbp"] > 0, leg
        # The distribution-free count must partition the family, so a reader can check the
        # estimator's verdict against a reading that assumes nothing about the distribution.
        assert (block["positive_seeds"] + block["negative_or_zero_seeds"]
                == block["seeds_with_a_figure"] == 18), leg
        assert block["distance_to_a_sign"]["available"] is True, leg

    # THE ARITHMETIC TIE BETWEEN THE THREE LEGS, which is what makes them one decomposition rather
    # than three separate measurements: selection is value minus level, seed by seed.
    for row in _eighteen()["seeds"]:
        assert row["selection_gbp"] == pytest.approx(
            row["value_advantage_gbp"] - row["level_advantage_gbp"], abs=1e-6)


def test_the_two_legs_are_judged_at_the_same_bar_so_a_split_verdict_is_about_the_data():
    """THE DEFECT: the level leg judged at a looser bar than the selection leg.

    The whole use of these two legs is the CONTRAST between their verdicts. If the bars differ,
    "one leg's sign is stateable and the other's is not" is a property of the RULE and not of the
    book -- and it would read on the surface exactly like a finding. Mutation: give `_leg` a
    leg-specific bar and this fires.
    """
    rows = copy.deepcopy(_eighteen()["seeds"])
    # Put both legs at the SAME numbers, so any difference in verdict can only come from the rule.
    for row in rows:
        row["level_advantage_gbp"] = row["selection_gbp"]
        row["value_advantage_gbp"] = row["selection_gbp"] * 2
    got = summarise(rows)
    assert (got["level_leg"]["distinguishable_from_zero"]
            == got["selection_leg"]["distinguishable_from_zero"])
    assert got["level_leg"]["sem_gbp"] == pytest.approx(got["selection_leg"]["sem_gbp"])


def test_the_level_legs_verdict_can_go_both_ways_on_this_summariser():
    """THE POISON ROUND, and the R15 trap this repo has walked into three times in one afternoon.

    Every assertion above is satisfied by a `distinguishable_from_zero` that is hardcoded, or by
    one that can only ever return one answer. A verdict function whose every branch returns the
    same value passes every per-branch test written against it. So the partition is asserted
    REACHABLE here, over the real summariser, before any test is allowed to mean anything by it.
    """
    rows = copy.deepcopy(_eighteen()["seeds"])
    determined = summarise(rows)["level_leg"]["distinguishable_from_zero"]

    # Drive the same leg to the other verdict by centring it on zero and spreading it wide.
    for i, row in enumerate(rows):
        row["level_advantage_gbp"] = 50_000.0 if i % 2 else -50_000.0
    undetermined = summarise(rows)["level_leg"]["distinguishable_from_zero"]

    assert {determined, undetermined} == {True, False}, (
        "the level leg's verdict returned {!r} and {!r} on a family centred away from zero and one "
        "centred on it -- the partition is not reachable, so no test of this verdict means "
        "anything".format(determined, undetermined))


def test_a_family_whose_seeds_carry_no_auc_states_an_unknown_and_never_a_spread():
    """THE DEFECT: an AUC spread computed over whichever rows happened to answer.

    Every floor on disk as of 2026-09-17 predates the producer recording the AUC, so this is the
    LIVE case and not a hypothetical. The flattering move is a spread over the subset that has a
    reading -- which bounds a different family from the one whose advantage is published beside it.
    """
    got = summarise(_eighteen()["seeds"])
    auc = got["discrimination_auc_across_seeds"]
    assert auc["available"] is False
    assert "spread" not in auc
    assert auc["seeds_carrying_an_auc"] == 0
    assert auc["seeds_in_family"] == 18
    assert "no discrimination reading beside them" in auc["unavailable_because"]


def test_one_seed_missing_an_auc_is_enough_to_withhold_the_whole_families_bound():
    """THE DEFECT: a partial family bounded as if it were whole -- the fail-open twin of the above.

    Mutation: relax the producer's `len(present) != len(rows)` to `not present` and this fires,
    because eighteen-minus-one rows would then publish a spread under the family's own name.
    """
    rows = copy.deepcopy(_eighteen()["seeds"])
    for i, row in enumerate(rows):
        row["discrimination_auc"] = 0.62
        row["auc_population"] = {"retained": 85, "left": 39}
    whole = summarise(rows)["discrimination_auc_across_seeds"]
    assert whole["available"] is True
    assert whole["spread"]["n"] == 18
    # 0.5 is the no-information point, so the reading is the distance from it and not from zero.
    assert whole["distance_from_no_information"]["mean"] == pytest.approx(0.12)

    rows[7].pop("discrimination_auc")
    holed = summarise(rows)["discrimination_auc_across_seeds"]
    assert holed["available"] is False
    assert holed["seeds_carrying_an_auc"] == 17
    assert holed["seeds_in_family"] == 18


def test_an_unmeasured_auc_is_never_written_as_the_no_information_value():
    """THE DEFECT: `None` coerced to 0.5. That is a REAL reading -- it means the belief carries no
    information about who stays -- so a run that was never scored would be published as a run that
    was scored and found to know nothing. Those license opposite decisions about the thesis."""
    rows = copy.deepcopy(_eighteen()["seeds"])
    for row in rows:
        row["discrimination_auc"] = None
    auc = summarise(rows)["discrimination_auc_across_seeds"]
    assert auc["available"] is False
    assert auc["seeds_carrying_an_auc"] == 0


def test_the_two_floors_that_share_seed_values_are_refused():
    """THE DEFECT, AND IT IS THE ONE THIS SESSION WALKED INTO. Three nine-seed floors sit in
    `docs/observability/`, and 27 rows look like 27 draws. Two of them re-run the SAME nine seed
    values under different trees, so the honest family is 18 and not 27. This pins that the refusal
    covers the real pair on disk and not only a synthetic one."""
    for path in (_FLOOR_A, _SAME_SEEDS_AS_A):
        if not path.exists():
            pytest.skip("no floor artefact on disk at {}".format(path))
    with pytest.raises(FoldRefused) as refusal:
        fold([_FLOOR_A, _SAME_SEEDS_AS_A])
    assert "appears in both" in str(refusal.value)
    # And the pair that does NOT share seeds folds, so the refusal above is about the seeds and
    # not about these two files being unfoldable for some other reason.
    assert len(fold([_FLOOR_A, _FLOOR_B])["seeds"]) == 18


def test_the_value_arm_pairing_separates_two_instruments_from_two_commits():
    """THE DEFECT (measured 2026-09-17): the published eighteen pools two PRICING arms and
    publishes the step between them as redraw noise.

    `_FLOOR_A` was drawn on `c066c114`, `_FLOOR_B` on `9f0ab066`, and those two trees differ in
    `company/pricing/value_based_renewal.py`. Re-running A's OWN nine seeds on B's value arm
    (`_SAME_SEEDS_AS_A`) moves `selection_gbp` by a paired -671.31 on all nine, 20.4 sems from
    zero. Pooled the family reads 1.80 sems and states no sign; on one arm it reads 2.50 and states
    a negative one. Nothing caught it because the refusal that stopped the AUC fold keys on
    `level_gbp_per_mwh`, which agrees to GBP4.27 across this pair.

    KEYED TO THE PROPERTY, NOT TO COMMIT IDENTITY, AND THAT IS THE WHOLE CONTROL. Both folds below
    have TWO distinct producing commits, so `producing_commit`'s "2 distinct code tree(s)" cannot
    tell them apart -- and the coarse implementation, comparing commits, passes the first
    assertion and FAILS the second. `_SAME_SEEDS_AS_A` and `_FLOOR_B` are three minutes apart with
    byte-identical value arms and are correctly poolable.
    """
    for path in (_FLOOR_A, _FLOOR_B, _SAME_SEEDS_AS_A):
        if not path.exists():
            pytest.skip("no floor artefact on disk at {}".format(path))

    mixed = fold([_FLOOR_A, _FLOOR_B])["value_arm_pairing"]
    single = fold([_SAME_SEEDS_AS_A, _FLOOR_B])["value_arm_pairing"]

    if mixed["unavailable_because"] or single["unavailable_because"]:
        # A clean `git archive` extract has no `.git`, so the diff cannot be taken there. That is
        # the fail-closed branch and it is asserted by its own control below -- skipping here keeps
        # THIS control about the distinction, rather than passing for the wrong reason.
        pytest.skip("value-arm provenance not checkable here: {}".format(
            mixed["unavailable_because"] or single["unavailable_because"]))

    # BOTH have two commits. The coarse implementation cannot reach this pair of verdicts.
    assert len(mixed["member_commits"]) == 2 and len(single["member_commits"]) == 2

    assert mixed["same_value_arm"] is False, (
        "the fold that pools c066c114 with 9f0ab066 must say so; those trees price the value arm "
        "differently by GBP671.31 paired on nine identical seeds")
    assert "company/pricing/value_based_renewal.py" in mixed["differing_paths"], (
        "the caveat must NAME the code that moved, or a reader cannot judge whether it could reach "
        "a seed row: got {}".format(mixed["differing_paths"]))
    assert mixed["caveat"] and "POOLS" in mixed["caveat"]

    assert single["same_value_arm"] is True, (
        "two commits with byte-identical value arms are one instrument and must NOT be flagged; "
        "flagging them is the commit-identity implementation this control exists to refuse")
    assert single["differing_paths"] == [] and single["caveat"] is None

    # STATED ON BOTH BRANCHES: silence must mean "asked and matched", never "never asked".
    assert mixed["why_this_rule"] and single["why_this_rule"]


def test_the_value_arm_pairing_fails_closed_and_every_branch_is_reachable():
    """THE DEFECT: a provenance check that cannot ask its question returning the FLATTERING answer.

    An unstamped member was drawn by a tree nobody wrote down. That is an unknown, and a `True`
    here would license pooling on no evidence -- the same error `_floor_tree_pairing` was written
    to stop making one field earlier. Both a missing stamp and a commit this repository does not
    have must land on `None` with a named reason.

    ONE CONTROL OVER THE WHOLE PARTITION. A guard that refuses everything passes every per-branch
    test, so this asserts all three verdicts are REACHABLE rather than checking each in isolation.
    """
    for path in (_FLOOR_A, _FLOOR_B, _SAME_SEEDS_AS_A):
        if not path.exists():
            pytest.skip("no floor artefact on disk at {}".format(path))

    from tools.fold_noise_floor_family import _value_arm_pairing

    def _src(path, commit="keep"):
        data = copy.deepcopy(json.loads(Path(path).read_text(encoding="utf-8")))
        if commit != "keep":
            data.setdefault("producing_commit", {})["commit"] = commit
            data["producing_commit"]["resolved_at"] = None
        return (path, data)

    unstamped = _value_arm_pairing([_src(_FLOOR_A, None), _src(_FLOOR_B)])
    assert unstamped["same_value_arm"] is None, "a missing stamp must not read as agreement"
    assert unstamped["members_without_a_commit"] == 1
    assert "never evidence the arms agree" in unstamped["unavailable_because"]
    assert unstamped["caveat"], "an unknown provenance owes the reader a caveat"

    # A syntactically valid commit this repository does not contain. Not a fabricated probe: the
    # branch it exercises is literally "a member's commit is not present here".
    absent = _value_arm_pairing(
        [_src(_FLOOR_A, "0" * 40), _src(_FLOOR_B, "1" * 40)])
    assert absent["same_value_arm"] is None
    assert absent["unavailable_because"] and "NOT assumed to agree" in absent["unavailable_because"]

    # One commit named by every member: one arm by construction, no diff to take.
    one = _value_arm_pairing([_src(_FLOOR_A, "abc1234"), _src(_FLOOR_B, "abc1234")])
    assert one["same_value_arm"] is True and one["differing_paths"] == []

    mixed = fold([_FLOOR_A, _FLOOR_B])["value_arm_pairing"]
    single = fold([_SAME_SEEDS_AS_A, _FLOOR_B])["value_arm_pairing"]
    if mixed["unavailable_because"] or single["unavailable_because"]:
        pytest.skip("value-arm provenance not checkable in this tree")

    # THE PARTITION: every verdict this predicate can return is reached by some real input, so it
    # is not a guard that only ever says one thing.
    assert {mixed["same_value_arm"], single["same_value_arm"], unstamped["same_value_arm"]} == {
        False, True, None}


# --- the duplicate-seed refusal names the cause it established -------------------------------
#
# THE DEFECT (2026-09-19). The refusal above fires on any repeated seed id and used to explain
# itself the same way every time: "folding it would count one draw twice". That is one specific
# cause, and the remedy it implies -- drop a copy -- is right only when both rows came off the
# same pricing code. Seeds 3100001-3100012 have now been drawn twice, at `a178b56d6` and at
# `18327d977`, on trees that differ on `company/pricing/value_based_renewal.py`. There the rows
# are two instruments, de-duplicating discards an entire family, and the refusal was recommending
# it. A refusal that names a cause it has not established is how a correct refusal produces the
# wrong repair.

# Derived from `_REPO` rather than from the module-level floor-directory constant on purpose:
# another lane is reworking that constant in this same file, and these controls must land on
# HEAD-plus-these-hunks without carrying it.
_NEXT12 = (_REPO / "docs" / "observability"
           / "value_cycle_ab_s1_noise_floor_next12_20260917.json")


def _twelve_twice(tmp_path, commit_a, commit_b):
    """The same twelve rows twice, stamped with the two commits under test."""
    if not _NEXT12.exists():
        pytest.skip("no twelve-seed floor on disk at {}".format(_NEXT12))
    src = json.loads(_NEXT12.read_text(encoding="utf-8"))
    out = []
    for tag, commit in (("a", commit_a), ("b", commit_b)):
        data = copy.deepcopy(src)
        data.setdefault("producing_commit", {})["commit"] = commit
        path = tmp_path / "twelve_{}.json".format(tag)
        path.write_text(json.dumps(data), encoding="utf-8")
        out.append(path)
    return out


def _refusal(tmp_path, commit_a, commit_b):
    tmp_path.mkdir(parents=True, exist_ok=True)
    with pytest.raises(FoldRefused) as caught:
        fold(_twelve_twice(tmp_path, commit_a, commit_b))
    return str(caught.value)


def _cause_only(text):
    """The refusal with its "seed N appears in both `x` and `y`." preamble removed.

    WHY THE PARTITION CONTROL CANNOT READ THE WHOLE STRING. It did, and it was a tautology:
    the preamble carries the two file paths, which differ between cases because the fixtures are
    written to different directories. So the four messages were distinct no matter what the
    explanation said, and the control stayed GREEN under the mutation that collapsed all four
    causes to one sentence -- the exact defect it was written for. Caught by mutation, 2026-09-19.
    """
    head, sep, rest = text.partition("`. ")
    assert sep, "the refusal no longer opens with the two source paths: {}".format(text[:120])
    return rest


def _head_of(rev):
    import subprocess
    done = subprocess.run(["git", "-C", str(_REPO), "rev-parse", rev],
                          capture_output=True, text=True)
    if done.returncode != 0:
        pytest.skip("{} is not in this repository".format(rev))
    return done.stdout.strip()


def test_every_branch_of_the_duplicate_refusal_is_reachable(tmp_path):
    """THE DEFECT THIS SHAPE CATCHES: a guard that refuses EVERYTHING passes every per-branch
    test written for it, and a branch reached through no door is pinned by nothing. So this is one
    control over the whole partition -- it asserts each of the four cases produces a DISTINCT
    explanation before any other test asserts what those explanations say.

    Learned here the expensive way: the old refusal had exactly one sentence for all four."""
    same = _head_of("a178b56d6")
    other = _head_of("18327d977")
    seen = {
        "same_commit": _refusal(tmp_path / "s", same, same),
        "different_arm": _refusal(tmp_path / "d", same, other),
        "unstamped": _refusal(tmp_path / "u", same, None),
        "unresolvable": _refusal(tmp_path / "x", same, "0" * 40),
    }
    for name, text in seen.items():
        assert "appears in both" in text, "{} stopped refusing altogether".format(name)
    causes = {k: _cause_only(v) for k, v in seen.items()}
    assert len(set(causes.values())) == 4, (
        "two of the four duplicate causes explain themselves identically, so at least one is "
        "unreachable or unnamed: {}".format({k: v[:80] for k, v in causes.items()}))


def test_two_instruments_drawing_one_seed_are_not_called_one_draw_twice(tmp_path):
    """THE DEFECT: the refusal tells the reader to de-duplicate when the two rows are different
    measurements. Dropping either discards a whole instrument's family and publishes the survivor
    as though no choice had been made. Pinned against the REAL pair of trees the twelve ran on."""
    text = _refusal(tmp_path, _head_of("a178b56d6"), _head_of("18327d977"))
    assert "DIFFERENT PRICING CODE" in text
    assert "company/pricing/value_based_renewal.py" in text
    assert "Do NOT de-duplicate" in text
    # The cause it must NOT claim here, and the repair it must not recommend.
    assert "one draw recorded twice" not in text
    assert "Drop one copy" not in text


def test_the_same_tree_twice_still_earns_the_original_sentence(tmp_path):
    """THE MIRROR, and it is why the test above is not satisfied by deleting the old sentence: when
    both rows DO come off one commit, de-duplication is the right repair and must still be said."""
    same = _head_of("a178b56d6")
    text = _refusal(tmp_path, same, same)
    assert "one draw recorded twice" in text
    assert "Drop one copy" in text
    assert "DIFFERENT PRICING CODE" not in text


def test_a_duplicate_it_cannot_resolve_recommends_neither_repair(tmp_path):
    """THE DEFECT: fail-open. An unstamped member and an unresolvable commit both leave the
    question unasked, and the two candidate causes need OPPOSITE repairs -- so naming either is a
    coin flip wearing a finding's clothes. `_value_arm_diff` returns an empty path set on failure
    and an empty path set on agreement; a caller that reads the set before the failure flag lands
    on 'same arm, drop a copy', which is the flattering branch."""
    for label, other in (("unstamped", None), ("unresolvable", "0" * 40)):
        text = _refusal(tmp_path / label, _head_of("a178b56d6"), other)
        assert "Drop one copy" not in text, "{} took the flattering branch".format(label)
        assert "opposite remedies" in text
        assert "neither is applied here" in text
