"""The chase comparison's per-year loss census: where evidence was available, and where it was wasted.

THE DEFECT THIS EXISTS FOR, named. On 2026-08-28 the derived competitive-pressure channel moved
the company's belief at one rung in four, and the obvious reading of three silent rungs is "the
book is too thin for the departure count to cross". It was not that. The chase DID change the
count at those rungs -- in 2019, the final year of the window -- and
`CompetitivePressureLedger._closed_window` reads only years STRICTLY EARLIER than the renewal
being priced. A departure nothing is ever priced after is not weak evidence; it is no evidence.

Without this split the comparison prints a silent rung and the reader supplies the flattering
explanation. `_wasted` is the one line that makes "the count did not move" and "the count moved
where nothing could read it" different facts, so it is the thing pinned here.
"""
from __future__ import annotations

from tools.compare_chase_belief import (
    _by_year,
    _points,
    _wasted,
    per_rung_paired,
    tree_identity_verdict,
)


def _dec(account: str, term_start: str, believed: float, world: float = 0.3,
         rolled: bool = True) -> dict:
    return {"account": account, "term_start": term_start, "believed_p_leave": believed,
            "world_realized_p_leave": world, "world_rolled": rolled}


def _artefact(by_rung: dict[str, list[dict]]) -> dict:
    return {"decisions": by_rung,
            "slopes": {"common_population": 0, "points": []},
            "world_curve_vs_belief": {"per_decision": []}}


def _late_book(late_believed_on: float) -> tuple[dict, dict]:
    """A two-rung book where the TOP rung has churned everything after the first year.

    This is the real shape, not a contrived one: on the 2021-window founder-book pair the top
    rung priced nothing after 2019 while rung 0 priced into 2021, so the cross-rung intersection
    held only 2016-2018 decisions -- and 2016-2018 is exactly where the company's forward-
    accumulating loss ledger has least to read.
    """
    early_on = [_dec("A", "2016-01-01", 0.20)]
    early_off = [_dec("A", "2016-01-01", 0.20)]
    late_on = early_on + [_dec("B", "2021-01-01", late_believed_on)]
    late_off = early_off + [_dec("B", "2021-01-01", 0.40)]
    return (_artefact({"0.0": late_on, "2.0": early_on}),
            _artefact({"0.0": late_off, "2.0": early_off}))


def test_the_per_rung_join_SEES_a_late_window_move_the_cross_rung_intersection_CANNOT():
    # THE DEFECT, in one assertion. Account B renews in 2021 and its belief differs between the
    # arms. It is priced at rung 0 in both arms, so the between-arm question has a perfectly good
    # paired observation for it -- but B is absent from rung 2.0, so the cross-rung intersection
    # excludes it and reports the two worlds identical. Two published findings read "one rung in
    # four" off that set.
    on, off = _late_book(0.44)
    rows = {r["rung"]: r for r in per_rung_paired(on, off)}
    assert rows["0.0"]["decisions_moved"] == 1
    assert rows["0.0"]["moved_years"] == ["2021"]
    # ...and the intersection, computed the way the artefact's own `slopes` block would, holds
    # only the early decision, which is identical in both arms.
    intersection = set(d["account"] for d in on["decisions"]["0.0"]) & \
        set(d["account"] for d in on["decisions"]["2.0"])
    assert intersection == {"A"}


def test_a_rung_where_NOTHING_moved_is_reported_as_zero_rather_than_dropped():
    # A rung with a population and no move is a result. Dropping it would make the headline
    # "rungs that moved / rungs measured" a ratio over a denominator that quietly shrinks --
    # which reads as broader coverage the emptier the evidence gets.
    on, off = _late_book(0.40)
    rows = {r["rung"]: r for r in per_rung_paired(on, off)}
    assert rows["0.0"]["n"] == 2 and rows["0.0"]["decisions_moved"] == 0
    assert rows["2.0"]["n"] == 1 and rows["2.0"]["decisions_moved"] == 0


def test_a_belief_moving_DOWNWARD_is_counted_separately_and_not_absorbed_into_the_mean():
    # §5 component 2 is about DIRECTION, and it names a wrong sign as worse than a wrong
    # magnitude. One decision moving down inside a rung whose mean still rises would be invisible
    # if the direction were read off the mean.
    on, off = _late_book(0.44)
    on["decisions"]["0.0"].append(_dec("C", "2020-01-01", 0.10))
    off["decisions"]["0.0"].append(_dec("C", "2020-01-01", 0.30))
    row = {r["rung"]: r for r in per_rung_paired(on, off)}["0.0"]
    assert row["moved_up"] == 1 and row["moved_down"] == 1


def test_a_decision_the_world_never_ROLLED_is_excluded_from_the_pairing():
    # An unrolled decision has no realised world outcome to compare against, so including it
    # would put a belief difference beside a world difference that does not exist.
    on, off = _late_book(0.44)
    on["decisions"]["0.0"].append(_dec("D", "2020-01-01", 0.10, rolled=False))
    off["decisions"]["0.0"].append(_dec("D", "2020-01-01", 0.90, rolled=False))
    row = {r["rung"]: r for r in per_rung_paired(on, off)}["0.0"]
    assert row["n"] == 2 and row["decisions_moved"] == 1


def test_a_rung_with_NO_shared_decision_says_so_rather_than_reporting_a_zero_move():
    # FAIL-OPEN: an empty intersection between the arms averages to nothing, and "no move" is the
    # flattering reading of "no comparison was possible".
    on = _artefact({"0.0": [_dec("A", "2016-01-01", 0.2)]})
    off = _artefact({"0.0": [_dec("Z", "2016-01-01", 0.9)]})
    row = per_rung_paired(on, off)[0]
    assert row["n"] == 0 and "priced and rolled in both arms" in row["why_not"]


def test_the_points_reader_still_keys_rungs_the_way_the_artefact_writes_them():
    # `_points` and `per_rung_paired` key off different parts of the artefact (`slopes.points`
    # vs `decisions`); if they ever disagree about how a rung is named, the two tables in the
    # output silently describe different rungs.
    assert set(_points({"slopes": {"points": [{"multiplier": 0.0}, {"multiplier": 0.5}]}})) == {
        "0.0", "0.5"}


def _run(decisions: dict[int, int], losses: dict[int, int]) -> dict:
    """One census run as `_ladder_chase_arm` writes it -- JSON, so the years are STRINGS."""
    return {
        "armed": True,
        "decisions_by_year": {str(y): n for y, n in decisions.items()},
        "predicted_losses_by_year": {str(y): 1.0 for y in decisions},
        "realised_losses_by_year": {str(y): n for y, n in losses.items()},
    }


def test_a_departure_in_the_LAST_PRICED_YEAR_counts_as_wasted_not_as_evidence():
    # Four losses in 2019, and 2019 is the last year anything was priced in. Every one of them
    # is invisible to the channel. Relaxing `_wasted`'s comparison to `<=` reds this.
    usable, wasted = _wasted(_run({2017: 5, 2018: 5, 2019: 5}, {2019: 4}))
    assert (usable, wasted) == (0, 4)


def test_the_same_departures_one_year_EARLIER_are_evidence():
    # The only difference from the case above is the year the losses fell in. If this and the
    # test above did not disagree, the split would be reporting the window rather than the
    # evidence, and a silent rung would still have no explanation.
    usable, wasted = _wasted(_run({2017: 5, 2018: 5, 2019: 5}, {2018: 4}))
    assert (usable, wasted) == (4, 0)


def test_a_loss_in_a_year_BEYOND_the_last_priced_year_is_wasted_too():
    # A run can lose accounts after it stops pricing renewals -- those departures are booked and
    # can never be read either. Counting them as evidence would overstate what the company saw.
    usable, wasted = _wasted(_run({2017: 5, 2018: 5}, {2017: 1, 2020: 3}))
    assert (usable, wasted) == (1, 3)


def test_a_run_that_priced_NOTHING_reports_every_loss_as_wasted_rather_than_dividing_by_nothing():
    # FAIL-OPEN guard: with no priced years there is no "last priced year", and the tempting
    # default is to treat the losses as available. They are not -- nothing exists to read them.
    usable, wasted = _wasted(_run({}, {2018: 2}))
    assert (usable, wasted) == (0, 2)


def _cen(before: str, after: str | None = None, head: str = "abc123def", missing=()) -> dict:
    """One arm's census, carrying only what the tree-identity verdict reads."""
    return {
        "tree_before": {"head": head, "subject_sha256": before, "missing": list(missing)},
        "tree_after": {"head": head, "subject_sha256": after or before, "missing": list(missing)},
        "runs": [],
    }


def test_two_arms_on_DIFFERENT_trees_are_refused_rather_than_caveated():
    # The arms must run sequentially -- the ladder retains every rung's settlement records -- so
    # another lane can land work in the shared worktree between them. Both artefacts would still
    # report their own null rung reproducing their own control, because each arm is internally
    # consistent with whatever tree it ran on. Nothing else in the pair can see this.
    ok, why = tree_identity_verdict(_cen("aaaa"), _cen("bbbb"))
    assert not ok
    assert "DIFFERENT trees" in why


def test_a_tree_that_changed_DURING_one_arms_run_is_refused():
    # An arm takes tens of minutes. Fingerprinting only at the start would pass a pair whose
    # second half ran on someone else's commit.
    ok, why = tree_identity_verdict(_cen("aaaa"), _cen("aaaa", after="cccc"))
    assert not ok
    assert "DURING its run" in why


def test_an_UNFINGERPRINTED_pair_is_refused_rather_than_assumed_comparable():
    # FAIL-OPEN: artefacts written before the fingerprint existed carry no `tree_before`, and the
    # tempting default -- "no evidence of a difference" -- is the absence of an observation read
    # as an observation of absence.
    ok, why = tree_identity_verdict({"runs": []}, _cen("aaaa"))
    assert not ok
    assert "no tree fingerprint" in why


def test_a_fingerprint_over_a_MISSING_file_is_refused():
    # A hash that silently skips a file it could not read agrees with every other hash that
    # skipped the same file, so a deleted subject makes two trees look identical.
    ok, why = tree_identity_verdict(_cen("aaaa", missing=["simulation/run_phase2b.py"]),
                                    _cen("aaaa", missing=["simulation/run_phase2b.py"]))
    assert not ok
    assert "run_phase2b.py" in why


def test_the_matching_case_is_REACHABLE_so_the_verdict_is_not_a_constant_refusal():
    # R15's fourth shape: a control whose PASS branch cannot be reached reports a constant.
    ok, why = tree_identity_verdict(_cen("aaaa"), _cen("aaaa"))
    assert ok
    assert "aaaa" in why


def test_the_census_years_are_read_as_INTEGERS_so_the_ordering_is_numeric():
    # JSON stringifies integer keys, and string ordering would put "2019" before "202" and make
    # the strictly-earlier comparison nonsense the moment a year ran to four digits differently.
    # Pinning the coercion is cheaper than discovering it through a wrong table.
    assert _by_year(_run({2019: 1, 2020: 2}, {}), "decisions_by_year") == {2019: 1, 2020: 2}
