"""`tools/renewal_population_by_step` counts the book at each step of the renewal decision.

THE DEFECTS THIS NAMES. Two came up while the tool was being built against the single-levy run
(7379375f6), and each made a count that looked plausible:

- A spliced default stint repeats its `term_index`. With terms keyed by index, the later segment
  overwrote the earlier one, and a fixed term that ended onto the default was lost.
  `test_a_spliced_default_stint_is_ordered_by_date` fails if the sort becomes a dict on
  `term_index`.
- A household on the default that declines a fix at its anniversary is booked `declined_fix`, the
  same occasion as one declining at the end of a fixed term. Routed by occasion, 43 events matched
  no boundary. `test_a_declined_fix_on_the_default_is_the_default_route` fails if the route is
  read from the label.

- A considered household that got no offer must be split by the run's own reason, read from its
  event (a stayer) or `no_offer_churn_log` (a leaver), never inferred.
  `test_a_considered_household_with_no_offer_is_split_by_the_runs_own_reason` fails if either
  source is dropped, or if a missing reason is filled in rather than counted ``unrecorded``.

- The 10-10 gate is checked before the value test, so a gated household's value-test verdict is
  read from `retention_gate_value_test_log`. `test_a_gated_refusal_is_split_by_the_value_tests_verdict`
  fails if the two verdicts collapse into one, or if a run without the log reads as zero.

THE PARTITION IS ASSERTED REACHABLE before anything asserts what it holds. A counter that sends
everything to one route passes every per-route test.
"""
from __future__ import annotations

from tools.renewal_population_by_step import STEPS, population_by_step

FIRST_YEAR, LAST_YEAR = 2017, 2021


def _term(cid, start, end, tariff, idx, *, fuel="electricity", acct=None, rate=100.0):
    return {"customer_id": cid, "billing_account": acct or cid, "commodity": fuel,
            "term_start": start, "term_end": end, "term_index": idx, "tariff_type": tariff,
            "unit_rate_gbp_per_mwh": rate}


def _event(cid, when, estimate, *, occasion="renewal", fuel="electricity", left=False):
    return {"customer_id": cid, "event_date": when, "commodity": fuel,
            "event_type": "churned" if left else "renewed", "departure_occasion": occasion,
            "company_churn_estimate": estimate}


def _book():
    """One account per year whose fixed term ends that year, offered at a high estimate; one
    passive roller per year; one default-anniversary conversion per year."""
    states, events, offers = [], [], []
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        a, p, s = f"A{year}", f"P{year}", f"S{year}"
        states += [_term(a, f"{year - 1}-03-01", f"{year}-03-01", "fixed", 0),
                   _term(a, f"{year}-03-01", f"{year + 1}-03-01", "fixed", 1)]
        events.append(_event(a, f"{year}-03-01", 0.6))
        offers.append({"customer_id": a, "event_date": f"{year}-03-01"})
        # Passive roll: the fix ends onto the default and the world takes no decision.
        states += [_term(p, f"{year - 1}-05-01", f"{year}-05-01", "fixed", 0),
                   _term(p, f"{year}-05-01", f"{year}-07-01", "svt", 1)]
        # On the default, converting at its anniversary: a decision with no fixed term ending.
        states += [_term(s, f"{year - 1}-08-01", f"{year}-08-01", "svt", 0),
                   _term(s, f"{year}-08-01", f"{year + 1}-08-01", "fixed", 1)]
        events.append(_event(s, f"{year}-08-01", 0.4, occasion="svt_conversion"))
    return {"account_state_log": states, "customer_events": events, "retention_log": offers,
            "no_offer_churn_log": []}


def test_the_partition_is_reachable():
    run = _book()
    # An event at no boundary, and an offer at a decision below the threshold.
    run["customer_events"].append(_event("A2017", "2017-06-15", 0.9))
    run["account_state_log"] += [_term("L", "2018-01-01", "2019-01-01", "fixed", 0),
                                 _term("L", "2019-01-01", "2020-01-01", "fixed", 1)]
    run["customer_events"].append(_event("L", "2019-01-01", 0.1))
    run["retention_log"].append({"customer_id": "L", "event_date": "2019-01-01"})
    r = population_by_step(run)
    row = r["years"]["2019"]
    assert row["fixed_term"]["offered"] and row["default_anniversary"]["reached_decision"]
    assert row["fixed_to_default_with_no_decision"]
    assert row["fixed_term"]["reached_decision"] > row["fixed_term"]["considered"]
    assert r["unmatched"] == {"event_at_no_boundary": 1, "offer_at_no_considered_decision": 1}


def test_a_term_ending_in_each_year_is_counted_in_each_year():
    years = population_by_step(_book())["years"]
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        row = years[str(year)]
        assert row["fixed_term"] == {"term_ended": 2, "reached_decision": 1,
                                     "considered": 1, "offered": 1}, year
        assert row["fixed_to_default_with_no_decision"] == 1, year
        assert row["default_anniversary"] == {"reached_decision": 1, "considered": 1,
                                              "offered": 0}, year


def test_each_step_counts_no_more_than_the_step_before():
    run = _book()
    # Thin the later steps unevenly, so a step counted from the wrong log cannot tie.
    run["retention_log"] = [o for o in run["retention_log"] if o["event_date"][:4] != "2019"]
    for e in run["customer_events"]:
        if e["event_date"].startswith("2020"):
            e["company_churn_estimate"] = 0.2
    for year, row in population_by_step(run)["years"].items():
        f, d = row["fixed_term"], row["default_anniversary"]
        assert [f[s] for s in STEPS] == sorted((f[s] for s in STEPS), reverse=True), (year, f)
        assert d["reached_decision"] >= d["considered"] >= d["offered"], (year, d)


def test_the_threshold_is_strict():
    run = _book()
    from tools.renewal_population_by_step import RETENTION_THRESHOLD
    run["customer_events"][0]["company_churn_estimate"] = RETENTION_THRESHOLD
    row = population_by_step(run)["years"][str(FIRST_YEAR)]["fixed_term"]
    assert row["reached_decision"] == 1 and row["considered"] == 0


def test_a_spliced_default_stint_is_ordered_by_date():
    # The run writes a default stint's segments under ONE term_index, after the fix it follows.
    # The stint crosses a year end, so a boundary read off the wrong segment lands in 2018.
    states = [_term("X", "2016-11-17", "2017-11-17", "fixed", 0),
              _term("X", "2017-11-17", "2018-01-01", "svt", 1),
              _term("X", "2018-01-01", "2018-04-01", "svt", 1),
              _term("X", "2018-04-01", "2018-07-01", "svt", 1)]
    years = population_by_step({"account_state_log": states, "customer_events": []})["years"]
    assert years["2017"]["fixed_term"]["term_ended"] == 1
    assert years["2017"]["fixed_to_default_with_no_decision"] == 1
    assert years["2018"]["fixed_term"]["term_ended"] == 0


def test_a_declined_fix_on_the_default_is_the_default_route():
    states = [_term("Y", "2016-02-10", "2017-02-10", "svt", 4),
              _term("Y", "2017-02-10", "2017-04-01", "svt", 5)]
    events = [_event("Y", "2017-02-10", 0.5, occasion="declined_fix")]
    r = population_by_step({"account_state_log": states, "customer_events": events})
    assert r["unmatched"]["event_at_no_boundary"] == 0
    assert r["years"]["2017"]["default_anniversary"]["considered"] == 1
    assert r["years"]["2017"]["fixed_term"]["reached_decision"] == 0


def test_only_the_decision_leg_is_counted():
    # A dual-fuel household rolls on its electricity leg, so a boundary on its gas leg is not a
    # renewal (here the gas fix runs to 2018, where electricity has none). A gas-only household
    # rolls on gas.
    states = [_term("D", "2016-01-01", "2017-01-01", "fixed", 0),
              _term("D", "2017-01-01", "2019-01-01", "fixed", 1),
              _term("Dg", "2016-06-01", "2018-06-01", "fixed", 0, fuel="gas", acct="D"),
              _term("Dg", "2018-06-01", "2019-06-01", "fixed", 1, fuel="gas", acct="D"),
              _term("G", "2016-01-01", "2017-01-01", "fixed", 0, fuel="gas"),
              _term("G", "2017-01-01", "2018-01-01", "fixed", 1, fuel="gas")]
    events = [_event("D", "2017-01-01", 0.5), _event("G", "2017-01-01", 0.5, fuel="gas")]
    years = population_by_step({"account_state_log": states, "customer_events": events})["years"]
    assert years["2017"]["fixed_term"]["term_ended"] == 2
    assert years["2017"]["fixed_term"]["considered"] == 2
    assert "2018" not in years or years["2018"]["fixed_term"]["term_ended"] == 0


def test_a_declined_fix_at_a_fixed_end_is_a_decision_not_a_passive_roll():
    # Both move the household onto the default. Only the passive roll had no decision.
    states = [_term("Z", "2016-01-17", "2017-01-17", "fixed", 0),
              _term("Z", "2017-01-17", "2017-04-01", "svt", 1),
              _term("Q", "2016-03-01", "2017-03-01", "fixed", 0),
              _term("Q", "2017-03-01", "2017-04-01", "svt", 1)]
    events = [_event("Z", "2017-01-17", 0.44, occasion="declined_fix")]
    row = population_by_step({"account_state_log": states, "customer_events": events})["years"]["2017"]
    assert row["fixed_term"]["term_ended"] == 2 and row["fixed_term"]["reached_decision"] == 1
    assert row["fixed_to_default_with_no_decision"] == 1


def test_a_considered_household_with_no_offer_is_split_by_the_runs_own_reason():
    run = _book()
    # The book's conversions are considered (0.4) and never offered: give each year's a reason,
    # one from a stayer's event, one from a leaver's log row, one from neither.
    for e in run["customer_events"]:
        if e["customer_id"] == "S2017":
            e["retention_withheld_because"] = "the_discount_cannot_win_the_fix"
        if e["customer_id"] == "S2018":
            e["event_type"] = "churned"
    run["no_offer_churn_log"].append({"customer_id": "S2018", "event_date": "2018-08-01",
                                      "no_offer_reason": "uneconomical"})
    # An offered household carrying a stale reason is not a refusal.
    run["customer_events"][0]["retention_withheld_because"] = "uneconomical"
    years = population_by_step(run)["years"]
    split = {y: years[str(y)]["not_offered"]["default_anniversary"] for y in (2017, 2018, 2019)}
    assert all(split.values())
    assert split == {2017: {"the_discount_cannot_win_the_fix": 1}, 2018: {"uneconomical": 1},
                     2019: {"unrecorded": 1}}
    assert years["2017"]["not_offered"]["fixed_term"] == {}


def test_a_gated_refusal_is_split_by_the_value_tests_verdict():
    run = _book()
    run["retention_gate_value_test_log"] = [
        {"customer_id": "S2017", "event_date": "2017-08-01", "value_test_would_offer": True},
        {"customer_id": "S2018", "event_date": "2018-08-01", "value_test_would_offer": False},
        {"customer_id": "S2019", "event_date": "2019-08-01", "value_test_would_offer": False}]
    years = population_by_step(run)["years"]
    split = {y: years[str(y)]["gated_value_test"] for y in (2017, 2018, 2019, 2020)}
    assert split[2017]["would_offer"] and split[2018]["would_refuse"]
    assert split == {2017: {"would_offer": 1, "would_refuse": 0},
                     2018: {"would_offer": 0, "would_refuse": 1},
                     2019: {"would_offer": 0, "would_refuse": 1},
                     2020: {"would_offer": 0, "would_refuse": 0}}
    # A run that predates the log cannot say, and says so.
    assert population_by_step(_book())["years"]["2017"]["gated_value_test"] is None
