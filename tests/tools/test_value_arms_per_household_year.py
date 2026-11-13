"""The value test's figures per household per year are computed from the run, not typed.

Director's addendum of 13 Nov: "£5k to £8k means nothing to me. Is this per customer or on a random
size sample?" `docs/design/THE_VALUE_TEST_REDESIGN.md` §3a computed these by hand; the defect this
names is a page that can only state them by typing them.
"""
from __future__ import annotations

import json
from pathlib import Path

from tools.generate_value_arms_data import (
    _error_bar_per_household_year,
    _per_household_year,
    _per_household_year_redraw_band,
    _run_per_household_year,
)

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "docs" / "observability" / "value_cycle_ab_s1_three_arm_20261008r.json"


def _run(nets_value, nets_control, nets_level, rows):
    def arm(n):
        return {"net_by_billing_account_gbp": n}
    return {"household_side": {"control_arm": {"customer_years": 10}},
            "book_identity": {"control_arm": {"billing_accounts_settled_in_window": 4}},
            "control_arm": arm(nets_control), "value_arm": arm(nets_value), "level_arm": arm(nets_level),
            "belief_against_control_outcomes": {"available": True, "scored_decisions": rows}}


def test_the_denominator_is_the_control_arms_household_years_and_an_absent_one_refuses():
    """MUTATION: divide by households, or by the value arm's own years -> the 3.0 assert reds;
    drop the refusal -> the last assert reds (it would divide by None)."""
    rows = [{"account": a, "believed_p_retain": p, "retained_under_the_control_arm": r}
            for a, p, r in (("A", 0.9, True), ("B", 0.2, False), ("C", 0.8, True), ("D", 0.3, False))]
    out = _per_household_year(_run({"A": 30.0, "B": 0.0}, {"A": 0.0, "B": 0.0, "C": 0.0, "D": 0.0},
                                   {"A": 0.0}, rows))
    assert out["available"] and out["household_years"] == 10 and out["households"] == 4
    assert out["whole_advantage"]["gbp_per_household_year"] == 3.0
    assert out["whole_advantage"]["households_spread"]["households"] == 4
    assert out["belief_skill"]["auc"] == 1.0 and out["belief_skill"]["interval_includes_a_coin"] is False
    assert _per_household_year({})["available"] is False


def test_the_published_run_reproduces_the_redesigns_hand_figures():
    """§3a, by hand on 13 Nov: 1,831 household-years, AUC 0.52, +£2.86 and +£6.20 per
    household-year at 0.6 and 2.0 standard errors across households. The input is the dated 8 Oct
    artefact the page publishes, which no later run overwrites."""
    out = _per_household_year(json.loads(RUN.read_text(encoding="utf-8")))
    assert out["household_years"] == 1831 and out["households"] == 272
    assert round(out["belief_skill"]["auc"], 2) == 0.52
    assert out["belief_skill"]["households_scored"] == 122 and out["belief_skill"]["interval_includes_a_coin"]
    assert out["whole_advantage"]["gbp_per_household_year"] == 2.86
    assert out["choosing"]["gbp_per_household_year"] == 6.2
    assert round(out["whole_advantage"]["households_spread"]["standard_errors_from_zero"], 1) == 0.6


def test_the_redraw_band_is_divided_by_the_same_household_years_and_an_unchecked_family_says_why():
    """The appendix's re-draw band in the published draw's units. MUTATION: divide the band by
    households instead of household-years -> the 2.0 assert reds; drop the `checked` branch -> the
    unchecked leg publishes a band and the `available is False` assert reds; skip a leg -> the
    partition assert reds, because both branches must be reachable from one input."""
    phy = {"available": True, "household_years": 10, "households": 4,
           "whole_advantage": {"available": True, "gbp_per_household_year": 3.0},
           "choosing": {"available": True, "gbp_per_household_year": 1.0},
           "price_level": {"available": True, "gbp_per_household_year": 2.0}}
    cw = {"per_household_year": phy,
          "verdict_stability": {"checked": True, "n": 2, "redraw_min_gbp": 20.0,
                                "redraw_mean_gbp": 25.0, "redraw_max_gbp": 30.0},
          "selection_leg": {"verdict_stability": {"checked": False, "why_not": "no floor"}},
          "level_leg": {}}
    out = _per_household_year_redraw_band(cw)
    bands = [out[k]["redraw_band"]["available"]
             for k in ("whole_advantage", "choosing", "price_level")]
    assert True in bands and False in bands
    assert out["whole_advantage"]["redraw_band"]["redraw_min_per_household_year"] == 2.0
    assert out["choosing"]["redraw_band"] == {"available": False, "why_not": "no floor"}
    assert "10" in out["redraw_denominator"]
    assert _per_household_year_redraw_band({"per_household_year": {"available": False}}) == {
        "available": False}


def test_the_headline_run_is_divided_by_its_own_household_years_and_states_sizes_not_signs():
    """MUTATION: keep the sign on the realised split -> the 2.0 size assert reds (it would be
    -2.0); divide by households -> 2.0 becomes 5.0; drop the refusal -> {} divides by None."""
    run = {"household_side": {"control_arm": {"customer_years": 10}},
           "book_identity": {"control_arm": {"billing_accounts_settled_in_window": 4}}}
    realised = {"split": {"available": True, "clock": "settled-realised",
                          "value_advantage_gbp": -20.0, "selection_gbp": 5.0,
                          "level_advantage_gbp": -25.0}}
    prov = {"available": True, "clock": "settled-provisioned", "selection_magnitude_gbp": 3.0,
            "arms": [{"key": "control", "net_gbp": 100.0, "advantage_gbp": None},
                     {"key": "value", "net_gbp": 110.0, "advantage_gbp": 10.0}]}
    out = _run_per_household_year(run, realised, prov)
    assert out["household_years"] == 10 and out["realised"]["value_advantage_size"] == 2.0
    assert out["provisioned"]["advantage_by_arm"] == {"control": None, "value": 1.0}
    assert _run_per_household_year({}, realised, prov)["available"] is False


def test_the_error_bar_family_names_its_own_book_in_the_absence():
    out = _error_bar_per_household_year({"seeds": [{"billing_accounts_settled_in_window": 164}]})
    assert out["available"] is False and "164 households" in out["why_not"]
