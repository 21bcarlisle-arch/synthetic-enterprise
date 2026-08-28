"""The ladder's three readers: the null check, the slope population, and the reference join.

WHY THIS FILE EXISTS
--------------------
`tools/run_price_ladder.py` turns six multi-minute simulation runs into three numbers. The runs
are the expensive part and the arithmetic on top of them is where a wrong answer would be
cheapest to produce and hardest to see, so the arithmetic is tested on hand-built rungs here
rather than left to be inspected in a published artefact.

Every test below names the mutation it fails against (R15). The three defects being held off are
this project's own catalogued shapes:

  * FAIL-OPEN -- a null check that passes when the rosters differ, so the ladder reports a curve
    it measured off its own plumbing.
  * COMPOSITION -- a slope taken over each rung's own survivors. Higher rungs churn accounts
    earlier, which deletes their later renewals, so the population at the top of the ladder is a
    survivor set selected BY THE TREATMENT. A slope over that is a measurement of attrition.
  * TAUTOLOGY -- a world-reference column computed by the harness and never checked against the
    world's own logged position, so a join that scored the wrong price would read as agreement.
"""
from __future__ import annotations

import pytest

from tools.run_price_ladder import (
    _ols_slope,
    household_saving_curve,
    household_side,
    null_control_check,
    reference_divergence,
    slopes,
    unmatched_diagnosis,
    world_curve_vs_belief,
)


def _events(*rows):
    """A minimal `phase2b.customer_events` log: (account, term, churned?)."""
    return {"phase2b": {"customer_events": [
        {"customer_id": a, "event_date": t,
         "event_type": "churned" if left else "renewed",
         "effective_retention_probability": 0.9, "random_roll": 0.5,
         "price_differential_vs_svt": 0.10, "churn_position_multiplier": 2.0}
        for a, t, left in rows
    ]}, "phase4c": {}}


def _decision(account, term, *, uplift, believed_leave, left, rate_inc=20.0, svt=10.0,
              rolled=True, world_leave=0.1):
    return {
        "account": account, "term_start": term,
        "margin_gbp_per_mwh": 2.0 + uplift, "uplift_gbp_per_mwh": uplift,
        "unit_rate_gbp_per_mwh": 150.0 + uplift,
        "rate_increase_pct": rate_inc, "rate_vs_svt_pct": svt,
        "believed_p_retain": 1.0 - believed_leave, "believed_p_leave": believed_leave,
        "ladder_ceiling_clamped": False, "ladder_above_support_bound": False,
        "world_rolled": rolled, "left": left if rolled else None,
        "world_effective_p_retain": 1.0 - world_leave, "world_roll": 0.5,
        "world_realized_p_leave": world_leave if rolled else None,
        "world_price_differential_vs_svt": svt / 100.0 if rolled else None,
        "world_churn_position_multiplier": 2.0 if rolled else None,
    }


def _rung(k, decisions):
    return {"multiplier": k, "priced": len(decisions),
            "rolled_by_the_world": sum(1 for d in decisions if d["world_rolled"]),
            "unrolled": sum(1 for d in decisions if not d["world_rolled"]),
            "ceiling_clamped": 0, "above_support_bound": 0, "decisions": decisions}


# ── the null check ────────────────────────────────────────────────────────────────────────────

def test_the_null_check_passes_when_rung_zero_reproduces_the_control():
    same = _events(("A", "2017-04-01", False), ("B", "2017-04-01", True))
    same["phase4c"]["total_net_margin_gbp"] = 1000.0
    check = null_control_check(same, same)
    assert check["churn_roster_matches"] is True
    assert check["net_margin_matches"] is True
    assert "reproduces the flat-rules control exactly" in check["verdict"]


def test_the_null_check_FAILS_when_the_roster_differs():
    """THE MUTATION IS THE FINDING. A ladder whose rung zero churns somebody the control did not
    is measuring the multiplier's plumbing; this check exists to refuse to publish that, so it
    has to be able to fire."""
    zero = _events(("A", "2017-04-01", True), ("B", "2017-04-01", True))
    zero["phase4c"]["total_net_margin_gbp"] = 1000.0
    control = _events(("A", "2017-04-01", False), ("B", "2017-04-01", True))
    control["phase4c"]["total_net_margin_gbp"] = 1000.0
    check = null_control_check(zero, control)
    assert check["churn_roster_matches"] is False
    assert check["only_in_rung_zero"] == ["A@2017-04-01"]
    assert "no slope below may be read" in check["verdict"]


def test_the_null_check_FAILS_on_the_money_even_when_the_roster_agrees():
    """Two arms can lose the same customers and still charge them differently. A roster-only check
    would pass on a rung zero that priced every survivor wrong."""
    roster = (("A", "2017-04-01", False), ("B", "2017-04-01", True))
    zero, control = _events(*roster), _events(*roster)
    zero["phase4c"]["total_net_margin_gbp"] = 1000.0
    control["phase4c"]["total_net_margin_gbp"] = 1750.0
    check = null_control_check(zero, control)
    assert check["churn_roster_matches"] is True
    assert check["net_margin_matches"] is False
    assert "no slope below may be read" in check["verdict"]


# ── the slope population ──────────────────────────────────────────────────────────────────────

def test_the_slope_population_is_the_INTERSECTION_across_rungs():
    """THE COMPOSITION DEFECT, stated as a test.

    `B` survives to be priced at rung 0 but a higher rung churned it at an earlier renewal, so it
    is absent from rung 2. Including it at rung 0 and not at rung 2 would compare two different
    books and call the difference a price response.

    MUTATION: take each rung's own decisions instead of the intersection. `n` at rung 0 becomes 2
    and this reds.
    """
    survivors = [_decision(a, "2017-04-01", uplift=0.0, believed_leave=0.10, left=False)
                 for a in ("A1", "A2")]
    rungs = [
        _rung(0.0, survivors + [
            _decision("B", "2018-04-01", uplift=0.0, believed_leave=0.10, left=False)]),
        _rung(2.0, [_decision(a, "2017-04-01", uplift=100.0, believed_leave=0.60, left=True)
                    for a in ("A1", "A2")]),
    ]
    out = slopes(rungs)
    assert out["available"] is True
    assert out["common_population"] == 2
    assert [p["n"] for p in out["points"]] == [2, 2]
    # B's own rung-0 outcome must not reach the rung-0 point at all.
    assert out["points"][0]["realised_non_renewals"] == 0


def test_an_unrolled_decision_is_excluded_from_the_population_at_every_rung():
    """"The world rolled no decision" is not "they stayed". Counting it as a retention would
    flatter the arm at every rung equally, which reads as a well-calibrated flat belief."""
    def _at(uplift, leave, left):
        return [_decision(a, "2017-04-01", uplift=uplift, believed_leave=leave, left=left)
                for a in ("A1", "A2")] + [
            _decision("C", "2017-04-01", uplift=uplift, believed_leave=leave, left=None,
                      rolled=False)]

    out = slopes([_rung(0.0, _at(0.0, 0.1, False)), _rung(1.0, _at(50.0, 0.4, True))])
    assert out["common_population"] == 2
    assert [p["n"] for p in out["points"]] == [2, 2]


def test_the_two_slopes_are_computed_against_the_same_x_and_their_ratio_is_reported():
    """A world that punishes price twice as hard as the company believes must come back as
    `realised_over_believed` = 2, on the axis the artefact's headline is read off."""
    rungs = [
        _rung(0.0, [_decision(f"A{i}", "2017-04-01", uplift=0.0, believed_leave=0.0, left=False)
                    for i in range(10)]),
        _rung(1.0, [_decision(f"A{i}", "2017-04-01", uplift=10.0, believed_leave=0.2,
                              left=(i < 4)) for i in range(10)]),
    ]
    pair = slopes(rungs)["against_delivered_uplift"]
    assert pair["realised"]["slope"] == 0.04       # 0.4 over 10 GBP/MWh
    assert pair["believed"]["slope"] == 0.02       # 0.2 over 10 GBP/MWh
    assert pair["realised_over_believed"] == 2.0


def test_a_single_rung_yields_no_slope_rather_than_a_zero():
    """FAIL-OPEN. A slope through one point is not zero, it is absent, and an artefact that
    published 0.0 there would read as "the world does not respond to price"."""
    rungs = [_rung(1.0, [_decision("A", "2017-04-01", uplift=5.0, believed_leave=0.2, left=False),
                         _decision("B", "2017-04-01", uplift=5.0, believed_leave=0.2, left=True)])]
    pair = slopes(rungs)["against_delivered_uplift"]
    assert pair["realised"]["available"] is False
    assert pair["realised_over_believed"] is None


def test_the_continuous_leg_SEES_a_move_the_binary_leg_CANNOT():
    """THE DEFECT THIS EXISTS FOR: a world change smaller than one account reads as zero.

    The realised leg is a count of flips over n, so it moves in steps of 1/n and nothing
    smaller than that quantum can appear in it at all. This is the shape that made the
    2026-08-28 chase-on/chase-off ladder unreadable: three of four rungs reported an
    identical 0.0000 delta, which was taken for "no effect" when it was "below resolution".

    Two worlds, ten decisions, IDENTICAL ROLLS -- so the binary leg is bit-identical by
    construction -- and a world probability 3 points higher in the second. The continuous leg
    must report that; if it is deleted, or wired to the flips, or averaged off the same
    counter, this test reds.
    """
    def world(p_leave):
        return [
            _rung(0.0, [_decision(f"A{i}", "2017-04-01", uplift=0.0, believed_leave=0.2,
                                  left=(i < 2), world_leave=p_leave) for i in range(10)]),
            _rung(1.0, [_decision(f"A{i}", "2017-04-01", uplift=10.0, believed_leave=0.4,
                                  left=(i < 5), world_leave=p_leave + 0.1) for i in range(10)]),
        ]
    soft, hard = slopes(world(0.10)), slopes(world(0.13))

    # The binary leg cannot tell these two worlds apart. That is the premise, not a bug.
    assert [p["realised_non_renewal_rate"] for p in soft["points"]] == \
           [p["realised_non_renewal_rate"] for p in hard["points"]] == [0.2, 0.5]

    # The continuous leg can, and by exactly the amount the world moved.
    assert [p["world_p_leave_mean"] for p in soft["points"]] == pytest.approx([0.10, 0.20])
    assert [p["world_p_leave_mean"] for p in hard["points"]] == pytest.approx([0.13, 0.23])

    # A level shift leaves the slope alone -- which is the reading that separated the defending
    # market's LEVEL effect from a SELECTION effect on the real book.
    for fit in (soft, hard):
        pair = fit["against_delivered_uplift"]
        assert pair["world_p_leave"]["slope"] == pytest.approx(0.01)
        # ...and it is reported against the belief, on the axis the headline is read off.
        assert pair["world_p_leave_over_believed"] == pytest.approx(0.5)


def test_a_rung_missing_the_world_probability_REFUSES_a_mean_rather_than_averaging_the_rest():
    """FAIL-OPEN, and the arithmetic version of "say what each number counts".

    If one decision in the common population carries no world probability, averaging the other
    nine publishes a mean over nine decisions beside a realised rate over ten. The difference
    between those two populations would then read as a price effect. The mutation this fails
    against is `statistics.fmean(world_p)` with the completeness guard removed: that returns a
    plausible 0.10 here instead of refusing.
    """
    rows = [_decision(f"A{i}", "2017-04-01", uplift=0.0, believed_leave=0.2, left=False,
                      world_leave=0.10) for i in range(10)]
    rows[3]["world_realized_p_leave"] = None      # rolled, but the world logged no probability
    rungs = [_rung(0.0, rows),
             _rung(1.0, [_decision(f"A{i}", "2017-04-01", uplift=10.0, believed_leave=0.4,
                                   left=(i < 5), world_leave=0.20) for i in range(10)])]
    fit = slopes(rungs)
    bad, good = fit["points"][0], fit["points"][1]

    assert bad["world_p_leave_mean"] is None
    assert bad["world_p_leave_carried"] == 9
    assert "9 of 10" in bad["world_p_leave_why_not"]
    # The rung that IS complete still reports, and the population is still all ten.
    assert good["world_p_leave_mean"] == pytest.approx(0.20)
    assert bad["n"] == good["n"] == 10
    # One readable rung is one point, and a slope through one point is absent, not zero.
    assert fit["against_delivered_uplift"]["world_p_leave"]["available"] is False
    assert fit["against_delivered_uplift"]["world_p_leave_over_believed"] is None


def test_ols_refuses_a_degenerate_x_axis():
    assert _ols_slope([1.0, 1.0, 1.0], [0.1, 0.2, 0.3])["available"] is False
    fit = _ols_slope([0.0, 1.0, 2.0], [0.0, 1.0, 2.0])
    assert fit["slope"] == 1.0 and fit["r_squared"] == 1.0


# ── the world's curve against the belief ──────────────────────────────────────────────────────

def test_the_paired_curve_comparison_recovers_a_known_ratio():
    """A world that moves half as fast as the company believes must come back at 0.5, and the
    direction of the finding -- OVER-predicting -- must be counted, not left to the sign.

    MUTATION: invert the `ratio < 1.0` test and the over/under counts swap, which flips the
    artefact's verdict from "leaving money on the table" to the hollow case.
    """
    rungs = [
        _rung(0.0, [_decision("A", "2017-04-01", uplift=0.0, believed_leave=0.20, left=False,
                              world_leave=0.10)]),
        _rung(1.0, [_decision("A", "2017-04-01", uplift=10.0, believed_leave=0.40, left=False,
                              world_leave=0.20)]),
    ]
    out = world_curve_vs_belief(rungs)
    assert out["available"] is True
    assert out["decisions"] == 1 and out["observations"] == 2
    row = out["per_decision"][0]
    assert row["believed_p_leave_slope_per_gbp_per_mwh"] == pytest.approx(0.02)
    assert row["world_p_leave_slope_per_gbp_per_mwh"] == pytest.approx(0.01)
    assert out["median_world_over_believed"] == pytest.approx(0.5)
    assert out["decisions_where_the_company_over_predicts_the_response"] == 1
    assert out["decisions_where_the_company_under_predicts_the_response"] == 0


def test_the_paired_comparison_uses_the_PRE_OFFER_world_probability():
    """`roll_lifecycle_event`'s own docstring: `realized_churn_probability` is captured before the
    retention-offer adjustment and is "the correct ground truth to compare a company churn
    estimate against", because the estimate is formed before the offer decision. Scoring against
    the post-offer `effective_retention_probability` would charge the company's forecast with the
    effect of its own later retention offer.

    MUTATION: read `1 - world_effective_p_retain` instead and this reds, because the row below
    carries a post-offer number that disagrees with the pre-offer one.
    """
    rows = []
    for k, uplift, world_leave in ((0.0, 0.0, 0.10), (1.0, 10.0, 0.20)):
        d = _decision("A", "2017-04-01", uplift=uplift, believed_leave=0.2 + uplift * 0.02,
                      left=False, world_leave=world_leave)
        d["world_effective_p_retain"] = 0.5      # a retention offer moved it; not our subject
        rows.append(_rung(k, [d]))
    row = world_curve_vs_belief(rows)["per_decision"][0]
    assert row["world_p_leave_at_lowest_rung"] == 0.10
    assert row["world_p_leave_at_highest_rung"] == 0.20


def test_the_paired_comparison_is_taken_per_decision_not_pooled():
    """POOLING IS THE DEFECT THE MEDIAN EXISTS TO AVOID. `WIDE` is priced over ten times the range
    of `NARROW`, so a pooled slope is almost entirely `WIDE`'s. They disagree by 4x here, and the
    median must report the middle of the two rather than the loud one.
    """
    def at(k, uplift_wide, uplift_narrow, bw, bn, ww, wn):
        return _rung(k, [
            _decision("WIDE", "2017-04-01", uplift=uplift_wide, believed_leave=bw, left=False,
                      world_leave=ww),
            _decision("NARROW", "2017-04-01", uplift=uplift_narrow, believed_leave=bn, left=False,
                      world_leave=wn),
        ])
    out = world_curve_vs_belief([
        at(0.0, 0.0, 0.0, 0.10, 0.10, 0.10, 0.10),
        at(1.0, 100.0, 10.0, 0.60, 0.20, 0.35, 0.20),
    ])
    ratios = sorted(r["world_over_believed"] for r in out["per_decision"])
    assert ratios == pytest.approx([0.5, 1.0])
    assert out["median_world_over_believed"] == pytest.approx(0.75)
    # And the pooled figure is published anyway, with its caveat, so the two can be compared.
    assert out["pooled"]["world_over_believed"] is not None
    assert "distrust this one" in out["pooled"]["caveat"]


def test_a_decision_the_world_never_rolled_carries_no_curve():
    """FAIL-OPEN. An unrolled decision has no world probability; treating a missing one as zero
    would manufacture a flat world curve and a ratio of 0.0 -- the hollow case's mirror image,
    invented out of an absence."""
    out = world_curve_vs_belief([
        _rung(0.0, [_decision("A", "2017-04-01", uplift=0.0, believed_leave=0.1, left=None,
                              rolled=False)]),
        _rung(1.0, [_decision("A", "2017-04-01", uplift=9.0, believed_leave=0.4, left=None,
                              rolled=False)]),
    ])
    assert out["available"] is False


# ── the reference join ────────────────────────────────────────────────────────────────────────

def test_the_harness_svt_column_is_reconciled_against_the_worlds_own(monkeypatch):
    """TAUTOLOGY GUARD. The harness computes `rate_vs_svt_pct` itself so it can report it for the
    decisions the world rolled nothing for. Where the world DID roll, it logged its own position,
    and the two must agree -- otherwise the harness is scoring a different price from the one the
    customer was charged.

    MUTATION: the second rung below carries a world position that disagrees with the harness
    column, and the reconciliation must call it.
    """
    good = [_rung(1.0, [_decision("A", "2017-04-01", uplift=50.0, believed_leave=0.3, left=True,
                                 svt=30.0)])]
    assert reference_divergence(good)["svt_reconciliation"]["agrees"] is True

    bad_row = _decision("A", "2017-04-01", uplift=50.0, believed_leave=0.3, left=True, svt=30.0)
    bad_row["world_price_differential_vs_svt"] = 0.05   # the world charged a different price
    recon = reference_divergence([_rung(1.0, [bad_row])])["svt_reconciliation"]
    assert recon["agrees"] is False
    assert recon["largest_absolute_gap_pct_points"] == 25.0


def test_the_two_references_disagreeing_in_sign_is_counted_not_inferred():
    """Finding 4's inversion, as a count. A supplier that was cheap and moves to average reads as
    a large RISE in the company's frame and as BELOW SVT in the world's."""
    rows = [
        _decision("cheap-to-average", "2017-04-01", uplift=30.0, believed_leave=0.6, left=False,
                  rate_inc=+35.0, svt=-5.0),
        _decision("dear-and-flat", "2017-04-01", uplift=1.0, believed_leave=0.1, left=True,
                  rate_inc=+2.0, svt=+30.0),
    ]
    out = reference_divergence([_rung(1.0, rows)])
    assert out["sign_disagreements"] == 1
    assert out["company_says_rise_world_says_below_svt"] == 1
    assert out["company_says_flat_world_says_30pct_dear"] == 1


# ── the unmatched diagnosis ───────────────────────────────────────────────────────────────────

def test_the_unmatched_diagnosis_separates_a_missing_account_from_a_missing_month():
    """The direction asked for a per-account reason, not a count. The two reasons are different
    facts about the world's roster and they point at different repairs."""
    rung = _rung(1.0, [
        _decision("SCHEDULE", "2017-04-01", uplift=5.0, believed_leave=0.2, left=None,
                  rolled=False),
        _decision("ABSENT", "2017-04-01", uplift=5.0, believed_leave=0.2, left=None,
                  rolled=False),
    ])
    result = _events(("SCHEDULE", "2017-07-01", False))
    out = unmatched_diagnosis(rung, result)
    assert out["unmatched_decisions"] == 2
    assert out["unmatched_accounts"] == 2
    assert out["accounts_the_world_never_rolled_at_all_in_window"] == 1
    assert out["accounts_the_world_never_rolled_at_all_in_window_named"] == ["ABSENT"]
    assert out["accounts_whose_world_schedule_names_other_months"] == 1
    reasons = {r["account"]: r["why_no_decision_was_rolled"] for r in out["per_decision"]}
    assert "at ANY renewal INSIDE THIS WINDOW" in reasons["ABSENT"]
    assert "2017-07-01" in reasons["SCHEDULE"]


def test_the_unmatched_count_separates_decisions_from_accounts():
    """Six accounts renewing three times each is eighteen unmatched DECISIONS and six absences to
    explain. A reader shown only the decision count reads eighteen separate defects.

    MUTATION: report `len(rows)` as the account count and this reds at 3 != 1.
    """
    rung = _rung(1.0, [
        _decision("SAME", t, uplift=5.0, believed_leave=0.2, left=None, rolled=False)
        for t in ("2017-04-01", "2018-04-01", "2019-04-01")])
    out = unmatched_diagnosis(rung, _events())
    assert out["unmatched_decisions"] == 3
    assert out["unmatched_accounts"] == 1
    assert out["accounts_the_world_never_rolled_at_all_in_window"] == 1


# ── the household side (atom A47) ─────────────────────────────────────────────────────────────

def test_the_household_side_is_absent_rather_than_zero_when_a_run_carried_no_records():
    """FAIL-OPEN killer. A run with no settlement records must not report £0 saved -- that
    is the shape that makes an empty book look like a fair one.

    MUTATION: return the portfolio of an empty view and this reds on `available`.
    """
    out = household_side({"phase2b": {"all_records": []}})
    assert out["available"] is False
    assert "no settlement records" in out["reason"]


def test_a_rung_priced_at_the_cap_shows_the_household_keeping_nothing():
    """The director's 2026-08-28 sentence, on the ladder: charging the cap transfers value
    rather than creating it, so the household side of that rung is exactly zero."""
    import datetime as dt

    from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date

    # Priced at THAT DAY'S cap, not at one day's cap held flat: the real cap moved
    # quarterly through 2022 (+54% on 1 April alone), so a flat rate across the window
    # is a price ABOVE the cap in the early quarter and below it later -- which the first
    # draft of this test discovered as a -£50 "saving" that was really a window mismatch.
    daily_kwh = 2700.0 / 365.0
    records = []
    for i in range(180):
        d = dt.date(2022, 1, 1) + dt.timedelta(days=i)
        cap = get_cap_unit_rate_for_date("electricity", d)
        records.append({
            "customer_id": "C1", "settlement_date": d.isoformat(),
            "consumption_kwh": daily_kwh,
            "revenue_gbp": daily_kwh / 1000.0 * cap,
            "wholesale_cost_gbp": daily_kwh / 1000.0 * 180.0,
            "margin_gbp": daily_kwh / 1000.0 * (cap - 180.0),
        })
    out = household_side({"phase2b": {"all_records": records}})
    assert out["available"] is True
    assert out["household_saving_gbp"] == pytest.approx(0.0, abs=1e-6)
    assert out["household_share_of_the_split_pct"] == pytest.approx(0.0, abs=1e-6)
    # The surplus is not zero -- it all went to us. Without this the test would pass on a
    # module that returned zeros for everything.
    assert out["our_gross_margin_gbp"] > 0.0


def test_the_household_curve_needs_two_rungs_and_says_so_rather_than_drawing_a_line():
    """POPULATION FLOOR. One point is not a curve, and a one-point OLS through the origin
    is a slope with no evidence behind it."""
    out = household_saving_curve([
        {"multiplier": 0.0,
         "household_side": {"available": True, "household_saving_gbp": 10.0},
         "decisions": [{"uplift_gbp_per_mwh": 1.0}]},
    ])
    assert out["available"] is False
    assert out["rungs_with_a_household_side"] == 1


def test_the_household_curve_falls_as_the_ladder_rises():
    """THE CONTINUOUS SURFACE the 17-decision churn leg could not supply. A higher rung takes
    more from the household, so the slope of saving against uplift is negative.

    MUTATION: sign-flip the saving and this reds -- a ladder that made households better off
    as it charged them more would be the arithmetic saying so, not a subtlety.
    """
    rungs = [
        {"multiplier": 0.0,
         "household_side": {"available": True, "household_saving_gbp": 300.0},
         "decisions": [{"uplift_gbp_per_mwh": 0.0}]},
        {"multiplier": 1.0,
         "household_side": {"available": True, "household_saving_gbp": 100.0},
         "decisions": [{"uplift_gbp_per_mwh": 10.0}]},
        {"multiplier": 2.0,
         "household_side": {"available": True, "household_saving_gbp": -100.0},
         "decisions": [{"uplift_gbp_per_mwh": 20.0}]},
    ]
    out = household_saving_curve(rungs)
    assert out["available"] is True
    assert len(out["rungs"]) == 3
    assert out["gbp_saved_per_gbp_per_mwh_of_uplift"]["slope"] == pytest.approx(-20.0, rel=1e-6)


def test_a_rung_whose_household_side_is_unknown_is_dropped_not_zeroed():
    """"We cannot say" must not enter the regression as £0 saved -- the fail-open that would
    drag the curve toward a flattering slope."""
    rungs = [
        {"multiplier": 0.0,
         "household_side": {"available": True, "household_saving_gbp": 300.0},
         "decisions": [{"uplift_gbp_per_mwh": 0.0}]},
        {"multiplier": 0.5,
         "household_side": {"available": True, "household_saving_gbp": None},
         "decisions": [{"uplift_gbp_per_mwh": 5.0}]},
        {"multiplier": 1.0,
         "household_side": {"available": True, "household_saving_gbp": 100.0},
         "decisions": [{"uplift_gbp_per_mwh": 10.0}]},
    ]
    out = household_saving_curve(rungs)
    assert [r["multiplier"] for r in out["rungs"]] == [0.0, 1.0]
    assert out["gbp_saved_per_gbp_per_mwh_of_uplift"]["slope"] == pytest.approx(-20.0, rel=1e-6)
