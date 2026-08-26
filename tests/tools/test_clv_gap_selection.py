"""R15 proofs for the three rows that say whether EP1's scale error belongs to
the estimator or to the population it was graded on.

Every control here is mutation-proven: each `test_*_fires_on_*` builds the defect
the control exists to catch and asserts the control notices, and each has a
partner asserting it stays quiet on a clean fixture. A control that cannot report
"no shift" is not a measurement, it is a slogan.

The three killer patterns, addressed by name:

  TAUTOLOGY   -- `recover_hazard` inverts the horizon ratio with its OWN copy of
                 the closed form, not by calling the company function it is
                 grading. `test_the_harness_annuity_matches_the_company_form`
                 is the agreement test between the two implementations, so the
                 duplication is checked rather than trusted.
  FAIL-OPEN   -- every input the run may not publish has a test asserting the
                 row comes back `available: False` with a NAMED reason. A missing
                 field must never read as "no selection shift".
  FAIL-SILENT -- `test_the_scale_attribution_is_never_published_alone` fails if
                 `couple_clv` ever emits `error_decomposition` without
                 `population_selection` beside it. That pairing is the whole
                 point: reading the attribution alone is what sent a stretch of
                 work at the lifetime term on 2026-08-26.
"""

import pytest

from company.analytics.clv_three_horizon import survival_discounted_value_gbp
from tools import clv_gap_selection as sel

# ---------------------------------------------------------------------------
# fixtures: the smallest run shapes that carry each defect
# ---------------------------------------------------------------------------

def _lifetime(value, segment="resi"):
    return {"segment": segment, "net_margin_after_cost_to_serve_gbp": value}


def _run_with_populations(graded, excluded, segment="resi"):
    """A run whose graded accounts realised `graded` and whose still-supplied
    accounts realised `excluded`, all in one segment."""
    lifetimes = {}
    for i, value in enumerate(graded):
        lifetimes[f"DEAD-{i}"] = _lifetime(value, segment)
    for i, value in enumerate(excluded):
        lifetimes[f"ALIVE-{i}"] = _lifetime(value, segment)
    counted = [{"account": f"DEAD-{i}", "belief_year": "2020"}
               for i in range(len(graded))]
    return {"per_customer_lifetime": lifetimes}, counted


def _events(believed_hazard, decisions, churns):
    """`decisions` renewal points at one believed hazard, of which `churns`
    ended in churn."""
    return [
        {"customer_id": f"C{i}", "event_type": "churned" if i < churns else "renewed",
         "churn_probability": believed_hazard}
        for i in range(decisions)
    ]


def _snapshot_run(hazards_by_account, discount_rate=0.10, margin=100.0):
    """A run publishing the two horizons EP1 publishes, built from the COMPANY's
    own closed form so the recovery is graded against the real producer."""
    accounts = {}
    for account_id, hazard in hazards_by_account.items():
        accounts[account_id] = {
            "contract_term": {"value_gbp": survival_discounted_value_gbp(
                margin, hazard, discount_rate, 1.0)},
            "tenure_expected": {"value_gbp": survival_discounted_value_gbp(
                margin, hazard, discount_rate, 1.0 / hazard)},
        }
    run = {"three_horizon_clv_snapshots": {
        "discount_rate": discount_rate,
        "years": {"2020": {"accounts": accounts}},
    }}
    counted = [{"account": a, "belief_year": "2020"} for a in hazards_by_account]
    return run, counted


# ---------------------------------------------------------------------------
# recover_hazard -- the inversion, and its independence from what it grades
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("hazard", [0.05, 0.08, 0.11, 0.2, 0.41, 0.6, 0.9])
def test_the_harness_annuity_matches_the_company_form(hazard):
    """The harness's re-derived closed form agrees with the company's, so the
    duplication the module's docstring declares is checked, not trusted."""
    for term in (1.0, 3.0, 1.0 / hazard):
        company = survival_discounted_value_gbp(1.0, hazard, 0.10, term)
        harness = sel._survival_annuity(hazard, term, 0.10)
        assert company == pytest.approx(harness, rel=1e-12)


@pytest.mark.parametrize("hazard", [0.05, 0.08, 0.11, 0.2, 0.41, 0.6, 0.9])
def test_the_hazard_round_trips_through_the_published_horizons(hazard):
    """Build both horizons with the COMPANY function at a known hazard, then
    recover it from the ratio alone. This is what licenses reading a hazard off
    a published artefact without re-running anything."""
    h1 = survival_discounted_value_gbp(137.0, hazard, 0.10, 1.0)
    h2 = survival_discounted_value_gbp(137.0, hazard, 0.10, 1.0 / hazard)
    assert sel.recover_hazard(h1, h2, 0.10) == pytest.approx(hazard, rel=1e-6)


def test_the_recovery_is_independent_of_the_margin():
    """Two accounts on the same hazard and wildly different margins must recover
    the same hazard -- the ratio cancels the margin, which is the property the
    whole inversion rests on."""
    for margin in (1.0, 1e6, -450.0):
        h1 = survival_discounted_value_gbp(margin, 0.23, 0.10, 1.0)
        h2 = survival_discounted_value_gbp(margin, 0.23, 0.10, 1.0 / 0.23)
        assert sel.recover_hazard(h1, h2, 0.10) == pytest.approx(0.23, rel=1e-6)


def test_an_uninvertible_ratio_returns_none_not_a_boundary_value():
    """FAIL-OPEN. A ratio outside the invertible range must not be pinned to the
    edge of the search, because 1e-5 recovered as a hazard reads as a 100,000
    year tenure and would be the most confident wrong number in the artefact."""
    assert sel.recover_hazard(0.0, 5.0) is None
    assert sel.recover_hazard(1.0, 1e9) is None      # ratio above the range
    assert sel.recover_hazard(1.0, 0.001) is None    # ratio below the range


def test_the_published_ratio_is_strictly_decreasing_in_the_hazard():
    """The monotonicity the bisection assumes, asserted rather than assumed."""
    ratios = [sel._published_ratio(h, 0.10)
              for h in (0.01, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 0.95)]
    assert all(a > b for a, b in zip(ratios, ratios[1:]))


# ---------------------------------------------------------------------------
# selection_profile
# ---------------------------------------------------------------------------

def test_selection_profile_fires_when_the_graded_population_is_the_losers():
    run, counted = _run_with_populations(graded=[100.0] * 5, excluded=[300.0] * 5)
    profile = sel.selection_profile(run, counted)
    assert profile["available"]
    assert profile["like_for_like_excluded_over_graded"] == pytest.approx(3.0)


def test_selection_profile_stays_quiet_when_the_populations_match():
    """The control must be able to say NO SHIFT, or it is not a measurement."""
    run, counted = _run_with_populations(graded=[200.0] * 5, excluded=[200.0] * 5)
    profile = sel.selection_profile(run, counted)
    assert profile["like_for_like_excluded_over_graded"] == pytest.approx(1.0)


def test_the_like_for_like_ratio_survives_a_segment_the_grading_never_touched():
    """The mistake this guard exists for, made on 2026-08-26 before the module
    was written: five I&C accounts, all still supplied and each worth ~500x a
    domestic one, turned a 3x selection shift into a reported 45x. The
    whole-book ratio moves; the like-for-like ratio must not."""
    lifetimes = {f"DEAD-{i}": _lifetime(100.0) for i in range(5)}
    lifetimes.update({f"ALIVE-{i}": _lifetime(300.0) for i in range(5)})
    counted = [{"account": f"DEAD-{i}", "belief_year": "2020"} for i in range(5)]
    clean = sel.selection_profile({"per_customer_lifetime": dict(lifetimes)}, counted)

    lifetimes["IC-1"] = _lifetime(200_000.0, segment="I&C")
    contaminated = sel.selection_profile(
        {"per_customer_lifetime": lifetimes}, counted)

    assert contaminated["like_for_like_excluded_over_graded"] == pytest.approx(
        clean["like_for_like_excluded_over_graded"])
    assert contaminated["whole_book_excluded_over_graded"] > 100
    assert contaminated["dominant_graded_segment"] == "resi"


def test_selection_profile_is_unavailable_with_a_named_reason_when_lifetimes_are_absent():
    """FAIL-OPEN. A run with no lifetimes must not report a clean 1.0."""
    for run in ({}, {"per_customer_lifetime": {}}, {"per_customer_lifetime": None}):
        profile = sel.selection_profile(run, [{"account": "X", "belief_year": "2020"}])
        assert profile["available"] is False
        assert profile["reason"]


def test_selection_profile_is_unavailable_on_an_empty_graded_population():
    run, _ = _run_with_populations(graded=[100.0], excluded=[300.0])
    profile = sel.selection_profile(run, [])
    assert profile["available"] is False
    assert profile["reason"] == sel.UNAVAILABLE_EMPTY


def test_selection_profile_declares_the_excluded_side_censored():
    """The direction of the remaining bias is stated on the row, not left for a
    reader to work out: the excluded accounts are still accruing, so the
    reported shift is a lower bound."""
    run, counted = _run_with_populations(graded=[100.0], excluded=[300.0])
    profile = sel.selection_profile(run, counted)
    assert profile["excluded_side_is_censored"] is True
    assert "LOWER BOUND" in profile["reading"]


# ---------------------------------------------------------------------------
# hazard_calibration
# ---------------------------------------------------------------------------

def test_hazard_calibration_fires_when_the_company_overstates_churn():
    """Believed 0.5, realised 0.1 -> the company thinks customers leave 5x more
    readily than they do, which makes its believed tenure too SHORT."""
    run = {"customer_events": _events(0.5, decisions=100, churns=10)}
    result = sel.hazard_calibration(run)
    assert result["available"]
    row = result["by_believed_hazard"][0]
    assert row["believed_over_realised"] == pytest.approx(5.0)
    assert result["mean_believed_tenure_years"] == pytest.approx(2.0)
    assert result["implied_realised_mean_tenure_years"] == pytest.approx(10.0)


def test_hazard_calibration_fires_when_the_company_understates_churn():
    """The opposite defect must be visible too, or the control only knows one
    direction and would read a too-long lifetime term as calibrated."""
    run = {"customer_events": _events(0.05, decisions=100, churns=25)}
    result = sel.hazard_calibration(run)
    assert result["by_believed_hazard"][0]["believed_over_realised"] == pytest.approx(0.2)


def test_hazard_calibration_stays_quiet_on_a_calibrated_model():
    run = {"customer_events": _events(0.2, decisions=100, churns=20)}
    result = sel.hazard_calibration(run)
    assert result["by_believed_hazard"][0]["believed_over_realised"] == pytest.approx(1.0)


def test_hazard_calibration_grades_the_belief_against_outcomes_not_another_probability():
    """R15 INDEPENDENCE. The realised side is a COUNT of `event_type`, so a run
    that publishes a contradictory second probability field cannot move it --
    which is the defect `simulation/customer_events.py` records having already
    paid for once (comparing the belief against a probability the dice roll
    never used produced a spurious ~-80% error pattern)."""
    events = _events(0.2, decisions=100, churns=20)
    for event in events:
        event["realized_churn_probability"] = 0.99
        event["company_churn_estimate"] = 0.99
    result = sel.hazard_calibration({"customer_events": events})
    assert result["by_believed_hazard"][0]["realised_rate"] == pytest.approx(0.2)


def test_hazard_calibration_buckets_separately_so_one_bucket_cannot_hide_another():
    run = {"customer_events": _events(0.05, 100, 5) + _events(0.4, 100, 10)}
    result = sel.hazard_calibration(run)
    by_hazard = {r["believed_hazard"]: r for r in result["by_believed_hazard"]}
    assert by_hazard[0.05]["believed_over_realised"] == pytest.approx(1.0)
    assert by_hazard[0.4]["believed_over_realised"] == pytest.approx(4.0)


def test_hazard_calibration_reports_a_zero_churn_bucket_as_none_not_infinity():
    run = {"customer_events": _events(0.3, decisions=20, churns=0)}
    row = sel.hazard_calibration(run)["by_believed_hazard"][0]
    assert row["realised_rate"] == 0.0
    assert row["believed_over_realised"] is None


def test_hazard_calibration_is_unavailable_with_a_named_reason_without_events():
    """FAIL-OPEN. No events must not read as a calibrated model."""
    for run in ({}, {"customer_events": []}, {"customer_events": [{"x": 1}]}):
        result = sel.hazard_calibration(run)
        assert result["available"] is False
        assert result["reason"] == sel.UNAVAILABLE_NO_EVENTS


# ---------------------------------------------------------------------------
# lifetime_level
# ---------------------------------------------------------------------------

def test_lifetime_level_fires_when_the_tenure_horizon_is_a_constant():
    """The defect found on 2026-08-26: all 33 graded accounts carried the same
    believed hazard, so the tenure horizon contributed no per-account variation
    and every ranking the CLV produced came from the margin term alone."""
    run, counted = _snapshot_run({f"A{i}": 0.05 for i in range(6)})
    result = sel.lifetime_level(run, counted)
    assert result["available"]
    assert result["hazard_is_constant_across_graded_population"] is True
    assert result["distinct_hazards"] == 1
    assert result["median_believed_tenure_years"] == pytest.approx(20.0, rel=1e-4)


def test_lifetime_level_stays_quiet_when_the_horizon_does_vary():
    """The partner. A control that always reports CONSTANT catches nothing."""
    run, counted = _snapshot_run({"A": 0.05, "B": 0.2, "C": 0.41})
    result = sel.lifetime_level(run, counted)
    assert result["hazard_is_constant_across_graded_population"] is False
    assert result["distinct_hazards"] == 3


def test_lifetime_level_recovers_the_hazard_the_company_actually_used():
    run, counted = _snapshot_run({"A": 0.05, "B": 0.38})
    recovered = {r["account"]: r["hazard"]
                 for r in sel.lifetime_level(run, counted)["per_account"]}
    assert recovered["A"] == pytest.approx(0.05, rel=1e-5)
    assert recovered["B"] == pytest.approx(0.38, rel=1e-5)


def test_lifetime_level_uses_the_runs_own_discount_rate_not_the_fallback():
    """A run published at a different discount rate must recover the same
    hazard; silently applying 0.10 to a 0.06 run would shift every hazard."""
    run, counted = _snapshot_run({"A": 0.25}, discount_rate=0.06)
    assert sel.lifetime_level(run, counted)["per_account"][0]["hazard"] == (
        pytest.approx(0.25, rel=1e-5))


def test_lifetime_level_names_the_accounts_it_could_not_recover():
    """A dropped row is a silent denominator change. Blanks are named."""
    run, counted = _snapshot_run({"A": 0.05})
    run["three_horizon_clv_snapshots"]["years"]["2020"]["accounts"]["B"] = {
        "contract_term": {"value_gbp": None},
        "tenure_expected": {"value_gbp": None},
    }
    counted.append({"account": "B", "belief_year": "2020"})
    counted.append({"account": "MISSING", "belief_year": "2020"})
    result = sel.lifetime_level(run, counted)
    assert result["recovered_accounts"] == 1
    assert result["unrecoverable_accounts"] == 2
    reasons = {r["account"]: r["reason"] for r in result["unrecoverable"]}
    assert reasons["B"] == "horizon blank"
    assert reasons["MISSING"] == "no snapshot row"


def test_lifetime_level_is_unavailable_with_a_named_reason_without_snapshots():
    """FAIL-OPEN. No snapshots must not read as a varying horizon."""
    for run in ({}, {"three_horizon_clv_snapshots": {}},
                {"three_horizon_clv_snapshots": {"years": {}}}):
        result = sel.lifetime_level(run, [{"account": "A", "belief_year": "2020"}])
        assert result["available"] is False
        assert result["reason"] == sel.UNAVAILABLE_NO_SNAPSHOTS


# ---------------------------------------------------------------------------
# the pairing rule -- the reason the module exists
# ---------------------------------------------------------------------------

def assert_attribution_is_paired(components: dict) -> None:
    """The rule, as one function so it can be proven on shapes that are not
    whichever artefact happens to be on disk.

    THE PRE-COMMIT GATE FOUND THIS, and the finding is worth keeping. The first
    draft demanded all three rows be `available`, and it passed in the working
    tree and RED in the gate -- because the gate runs against HEAD's artefact,
    which predates EP1's belief series and is graded through the LEGACY
    `clv_snapshots` field. That series publishes one number per account and no
    horizons, so `lifetime_level` has nothing to invert and is correctly blank.
    A control that fires on a run which is not defective gets loosened rather
    than fixed, so the rule is split by what each row actually depends on.
    """
    for key in ("population_selection", "hazard_calibration", "lifetime_level"):
        assert key in components, (
            f"{key} missing: the scale attribution cannot be read alone")

    # These two derive from fields EVERY run publishes -- the lifetime roster and
    # the event log. There is no honest reason for either to be blank, so a blank
    # one is a producer regression.
    for key in ("population_selection", "hazard_calibration"):
        assert components[key].get("available") is True, (
            f"{key} unavailable ({components[key].get('reason')}): the scale "
            "attribution would be published one-sided")

    # `lifetime_level` inverts the GRADED belief's own two horizons, so it exists
    # only where the graded series publishes them.
    if components["grades_atom_estimator"]:
        assert components["lifetime_level"].get("available") is True, (
            "lifetime_level unavailable "
            f"({components['lifetime_level'].get('reason')}) on a run that DOES "
            "grade EP1's estimator: its horizons are published and invertible, so "
            "a blank here is a regression, not a shape")
    else:
        assert components["lifetime_level"].get("reason"), (
            "lifetime_level is blank on a legacy-series run and does not say why "
            "-- a named reason is the difference between a shape and a silence")


def _paired(grades_ep1: bool, lifetime_level: dict) -> dict:
    return {
        "grades_atom_estimator": grades_ep1,
        "population_selection": {"available": True},
        "hazard_calibration": {"available": True},
        "lifetime_level": lifetime_level,
    }


def test_the_pairing_rule_accepts_both_shapes_it_is_meant_to_accept():
    assert_attribution_is_paired(_paired(True, {"available": True}))
    assert_attribution_is_paired(
        _paired(False, {"available": False, "reason": "run predates the series"}))


@pytest.mark.parametrize("components, defect", [
    (_paired(True, {"available": False, "reason": "whatever"}),
     "EP1-graded run whose horizons stopped inverting"),
    (_paired(False, {"available": False}),
     "legacy run whose blank carries no named reason"),
    (_paired(False, {"available": False, "reason": ""}),
     "legacy run whose reason is an empty string"),
])
def test_the_pairing_rule_rejects_each_shape_it_is_meant_to_reject(components, defect):
    """R15. The branch-aware rule must still be able to FAIL on both branches --
    a rule that only ever accepts is the loosening it was written to avoid."""
    with pytest.raises(AssertionError):
        assert_attribution_is_paired(components)


@pytest.mark.parametrize("missing",
                         ["population_selection", "hazard_calibration", "lifetime_level"])
def test_the_pairing_rule_rejects_a_dropped_row_on_either_branch(missing):
    for grades in (True, False):
        components = _paired(grades, {"available": True})
        del components[missing]
        with pytest.raises(AssertionError):
            assert_attribution_is_paired(components)


@pytest.mark.parametrize("blanked", ["population_selection", "hazard_calibration"])
def test_the_pairing_rule_rejects_an_always_derivable_row_going_blank(blanked):
    """These two never have a legitimate excuse, on either branch."""
    for grades in (True, False):
        components = _paired(grades, {"available": True})
        components[blanked] = {"available": False, "reason": "mutated"}
        with pytest.raises(AssertionError):
            assert_attribution_is_paired(components)


def test_the_scale_attribution_is_never_published_alone():
    """FAIL-SILENT guard, and the R10 class fix.

    `error_decomposition.best_single_scale` has two possible causes and the
    published entry used to name only one. This fails if a future edit emits the
    attribution without the three rows that distinguish them -- including if one
    of those rows is present but silently unavailable, which would leave a reader
    with the same one-sided story in a different shape.
    """
    from tools import couple_clv

    run = couple_clv.load_run_output()
    result, _ = couple_clv.measure(run)
    components = result.components
    if not (components.get("error_decomposition") or {}).get("available"):
        pytest.skip("no scale attribution in this run; nothing to pair with")

    assert_attribution_is_paired(components)


def test_the_published_note_declares_survivorship_not_only_the_truth_window():
    """A field a reader may not open is not a disclosure -- this module's own
    rule, applied to the bias it was missing. The note declared the truth-window
    bias at length while the larger selection effect went unnamed."""
    from tools import couple_clv

    run = couple_clv.load_run_output()
    result, _ = couple_clv.measure(run)
    assert "SURVIVORSHIP" in result.note
    assert "population_selection" in result.note
