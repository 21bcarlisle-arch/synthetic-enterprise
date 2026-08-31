"""The company may only be put beside the ceiling when the comparison is legal.

THE DEFECT THIS EXISTS TO CATCH. `docs/design/LADDER_APPLIED_TO_CHURN_2026-08-31.md` measured the
world's oracle AUC at 0.6760 and then explicitly REFUSED to put it beside the company's published
0.4653, because the two came from different populations and different runs -- "two true numbers
whose legs are different populations do not have a difference". That refusal was correct and it was
prose. Prose does not survive the next reader, and the difference (0.21, or "the company captures
69% of the ceiling") is exactly the shape someone quotes six weeks later with the sentence gone.

So the legality is in code now, and this is the control on it. Every assertion below names a
specific way the comparison goes wrong, and each one is written so that REMOVING the guard reds it
-- not so that today's numbers stay put. A control pinned to 0.6815 would go red when the world
becomes more honest and stay green when the claim rots.

MUTATIONS PROVEN (2026-08-31), all seven, each against a GREEN unmutated baseline and each firing
on an ASSERTION rather than on any exception -- the first harness reported 7/7 while every "failure"
was an `AttributeError` in the harness itself, which is the same fail-open shape as the defect:
  1. drop `same_population` from `ceiling_vs_belief`     -> test_a_ratio_is_refused_when_the_legs_count_different_populations
  2. drop `independent`                                  -> test_a_ratio_is_refused_when_the_belief_seeds_the_worlds_roll
  3. drop `clears`                                       -> test_a_ratio_is_refused_when_the_belief_is_inside_its_null
  4. return `[]` for a beliefless route                  -> test_a_route_with_no_company_belief_says_so_rather_than_returning_nothing
  5. return 0.5 for a beliefless route                   -> (same test: `available` must be False, not an AUC)
  6. score the belief with a POOLED auc instead of the
     stratified one                                      -> test_the_belief_is_scored_by_the_same_estimator_as_the_ceiling
  7. drop the realised-hazard check from the join        -> test_the_join_refuses_a_run_that_is_not_the_capture

TWO OF THOSE SURVIVED FIRST TIME AND BOTH FAILURES ARE WORTH THE SPACE, because each is a shape
this file exists to catch, found in this file:

  * **6 survived because the FIXTURE could not tell the estimators apart.** The first draft gave
    departed households hazards of 0.6+ and stayed ones 0.1+, which separates perfectly, so pooled
    and stratified readings were both 1.0 and the identity held for every estimator. An identity
    test on a population where the identity is unconditional is a control that cannot fail. The
    fixture now carries a between-year offset and overlapping classes, and the test asserts up
    front that pooled and stratified DISAGREE on it before trusting anything else.
  * **3 survived because the test took the subject's word for the thing under test.** It skipped
    comparison entries whose `clears_its_null` was true -- the exact field the mutation hard-wires
    -- so a mutation that claimed every belief cleared made the loop skip every belief and pass.
    Which beliefs are uninformative is now read from `belief_readings`, not from the comparison.
"""
from __future__ import annotations

import json

import pytest

from tools.measure_churn_heterogeneity import (
    COMPANY_BELIEFS,
    ROUTES_WITH_A_COMPANY_BELIEF,
    Unreadable,
    _label,
    attach_company_beliefs,
    auc,
    belief_readings,
    ceiling_vs_belief,
    within_strata_auc,
)

#: Enough rows, spread over two years, for a within-stratum AUC and a null to exist on both
#: classes. Small on purpose: this is a control on the MECHANISM, so it must not depend on a
#: captured artefact being present, current, or the size it was yesterday.
#:
#: THE TWO YEARS ARE DELIBERATELY UNEQUAL AND THE SEPARATION IS DELIBERATELY IMPERFECT, and an
#: earlier draft of this fixture got both wrong. With departed households on 0.6+ and stayed on
#: 0.1+ the score separates perfectly, every estimator scores 1.0, and swapping the stratified AUC
#: for a pooled one changed nothing -- the mutation survived because the fixture could not tell the
#: two apart. So: 2017 carries a large hazard offset for EVERYONE and most of the departures, which
#: is what makes a pooled reading score the year term and diverge from the within-year one; and the
#: classes overlap inside each year, so the within-year reading sits strictly between chance and
#: certainty where a real one does.
_YEAR_OFFSET = {2016: 0.00, 2017: 0.55}


def _rows(n: int = 40, *, route: str = "renewal", belief_key: str | None = "churn_probability"):
    rows = []
    for i in range(n):
        year = 2016 if i < n // 2 else 2017
        # Departures concentrate in 2017 -- the year with the higher hazard for everyone. This is
        # the between-stratum structure a pooled estimator would score as household signal.
        departed = (i % 5 == 0) if year == 2016 else (i % 2 == 0)
        # Within a year the classes OVERLAP: a departed household is only usually above a stayed
        # one, so the within-year AUC lands short of 1.0 and a change of estimator is visible.
        within = 0.18 if departed else 0.10
        row = {
            "customer_id": f"C{i}",
            "event_date": f"{year}-06-30",
            "market_year": year,
            "route": route,
            "event_type": "churned" if departed else "renewed",
            # The world's hazard genuinely orders the outcome within a year, so the ceiling clears
            # its null and the "ratio is legal" branch is REACHABLE. A fixture on which nothing
            # clears would make every refusal below pass for the wrong reason (R15: unreachable
            # PASS branch reports a constant verdict).
            "realized_churn_probability": _YEAR_OFFSET[year] + within + 0.004 * (i % 9),
            "sim_segment_days": 1 + i % 30,
            "sim_svt_inertia": 0.001 * (i + 1),
            "sim_action_propensity": 1.0 + 0.01 * (i % 5),
        }
        if belief_key is not None:
            # EVERY declared belief gets the field, not just the first. A fixture that populated
            # one would make the other unavailable, and the "different populations" refusal would
            # then pass for the wrong reason -- reporting a missing column rather than the guard
            # under test.
            for spec in COMPANY_BELIEFS:
                row[spec["field"]] = row["realized_churn_probability"]
        rows.append(row)
    return rows


def _entry(rows, readings):
    return {
        "route": rows[0]["route"],
        "decisions": len(rows),
        "oracle_auc": within_strata_auc(rows, lambda r: r["realized_churn_probability"])[0],
        "company_belief": readings,
    }


def test_the_belief_is_scored_by_the_same_estimator_as_the_ceiling():
    """A belief EQUAL to the world's hazard must reproduce the ceiling exactly.

    This is the check that the two legs share one estimator and one stratification. If the company
    leg were ever computed pooled, or on a different stratum key, or over a different row set, this
    identity breaks -- and it breaks by more than rounding, because pooling the routes moves the
    whole-book reading 0.6760 -> 0.7445 on the real capture.

    It is an identity rather than a threshold on purpose: it holds whatever the world does next.
    """
    rows = _rows()
    readings = belief_readings(rows, "renewal", permutations=200)
    graded = [r for r in readings if r.get("available")]
    assert graded, "no belief was graded on a route that has one"
    ceiling = within_strata_auc(rows, lambda r: r["realized_churn_probability"])[0]

    # THE FIXTURE MUST BE ABLE TO TELL THE TWO ESTIMATORS APART, and it silently could not in the
    # first draft: with perfectly separated classes both read 1.0 and swapping the stratified AUC
    # for a pooled one changed no assertion. An identity test on a population where the identity
    # holds for every estimator is a control that cannot fail.
    pooled, _ = auc([(r["realized_churn_probability"], _label(r)) for r in rows])
    assert abs(pooled - ceiling) > 0.02, (
        f"pooled ({pooled:.4f}) and within-stratum ({ceiling:.4f}) readings agree on this fixture, "
        "so it cannot detect a leg computed with the wrong estimator. Give the strata different "
        "score levels before trusting anything below."
    )
    for reading in graded:
        assert reading["belief_auc"] == pytest.approx(ceiling, abs=1e-12), (
            f"{reading['field']} was handed the world's own hazard as its belief and scored "
            f"{reading['belief_auc']} where the ceiling is {ceiling}. The company leg is not being "
            "computed by the same estimator on the same strata, so no reading from it may be put "
            "beside the ceiling."
        )
        assert reading["decisions"] == len(rows)


def test_a_belief_not_defined_on_a_route_says_so_rather_than_returning_nothing():
    """"No belief exists here" and "the belief scored at chance" are opposite findings.

    RE-KEYED 2026-08-31, and the reason is this file's own opening standard. It used to assert
    `"svt_segment" not in ROUTES_WITH_A_COMPANY_BELIEF` -- that is today's answer, not the
    property. When `company.crm.churn_desk.estimate_svt_drift` gave the company its first belief
    about the SVT route the control went red, having caught nothing: the world had become MORE
    honest and the guard reported a regression. The header two hundred lines above says a control
    pinned to a current value "would go red when the world becomes more honest and stay green when
    the claim rots", and this was that control.

    The durable property is per BELIEF, not per route: a belief that is not formed on the route
    being read must say so, with its cause, rather than being omitted or scored. That survives any
    number of routes gaining or losing beliefs, including the SVT route gaining one.
    """
    route = "svt_segment"
    not_defined = [b for b in COMPANY_BELIEFS if route not in b.get("routes", ("renewal",))]
    assert not_defined, (
        f"every declared belief is now defined on {route}, so this control has no subject. That "
        "is a real change and it needs a route where one is absent, not a deleted assertion."
    )
    readings = {r["field"]: r for r in belief_readings(_rows(route=route), route, permutations=200)}
    assert len(readings) == len(COMPANY_BELIEFS), (
        "a route returned fewer readings than there are beliefs: an absence has to be stated per "
        "belief, not omitted"
    )
    for spec in not_defined:
        reading = readings[spec["field"]]
        assert reading["available"] is False
        assert reading.get("belief_auc") is None, (
            "an undefined belief reported an AUC. A number here is indistinguishable from a belief "
            "that was graded and came out uninformative."
        )
        assert spec["field"] in reading["reason"] and route in reading["reason"], (
            "the refusal does not name the belief and the route it is absent on, so a reader "
            "cannot tell which channel is missing"
        )
        assert "NOT a missing column" in reading["reason"], (
            "the refusal does not distinguish absent-by-construction from merely-uncaptured, "
            "which is the whole finding: this gap cannot be closed by adding a column"
        )


def test_a_ratio_is_refused_when_the_legs_count_different_populations():
    """A capture fraction whose numerator and denominator count different decisions is refused."""
    rows = _rows()
    readings = belief_readings(rows, "renewal", permutations=200)
    entry = _entry(rows, readings)
    entry["decisions"] = len(rows) + 1  # the ceiling now counts a population the belief does not
    graded = {r["field"] for r in readings if r.get("available")}
    assert graded, "no belief was graded on this route, so the population guard was never reached"
    for reading in ceiling_vs_belief(entry)["readings"]:
        assert reading["excess_over_chance_captured"] is None, (
            "a fraction of the ceiling was published across two populations -- the exact move the "
            "ladder page refused in prose"
        )
        # Only a belief that was actually GRADED can be refused for counting the wrong population.
        # One that is not formed on this route at all is refused earlier and for a better reason,
        # and demanding this phrase of it would assert the wrong cause -- the shape where a refusal
        # names a cause the checker never observed.
        if reading["field"] in graded:
            assert "not one population" in reading["refused_because"]


def test_a_ratio_is_refused_when_the_belief_seeds_the_worlds_roll():
    """A belief the world rolls against cannot be normalised onto the ceiling.

    `roll_lifecycle_event` seeds `effective_p_retain` from `build_churn_risk`, so that belief
    scoring well against the outcome is the world reading back its own input. A "fraction captured"
    computed from it would publish a tautology as a measure of company skill.
    """
    seeding = [b for b in COMPANY_BELIEFS if b["seeds_the_world_roll"]]
    assert seeding, "no belief is marked as seeding the roll; the tautology guard has no subject"
    rows = _rows()
    readings = belief_readings(rows, "renewal", permutations=200)
    entry = _entry(rows, readings)
    by_field = {r["field"]: r for r in ceiling_vs_belief(entry)["readings"]}
    for spec in seeding:
        matched = by_field[spec["field"]]
        assert matched["belief_auc"] is not None, (
            f"{spec['field']} was not graded, so the tautology guard was never reached"
        )
        assert matched["excess_over_chance_captured"] is None, (
            f"{spec['field']} seeds the world's roll and a captured fraction was still published"
        )
        assert "seeds the world's own roll" in matched["refused_because"]

    # AND THE PASS BRANCH IS REACHABLE: an independent belief on the same population that clears
    # its null DOES get a ratio. Without this the four refusals above are equally consistent with
    # `excess_over_chance_captured` being hard-wired to None (R15: a control whose PASS branch is
    # unreachable reports a constant verdict).
    #
    # PROVEN ON A CONSTRUCTED BELIEF, NOT ON THE LIVE SPEC SET -- corrected 2026-08-31. It used to
    # scan `COMPANY_BELIEFS` for a real belief that got a ratio, and on 2026-08-31 the last one
    # stopped: `company_churn_estimate` reads inside its null, `build_churn_risk` seeds the roll,
    # and `estimate_svt_drift` clears only before its route's exposure offset. All three refusals
    # are CORRECT, and the reachability check went red anyway -- because whether the live book
    # happens to contain a null-clearing independent belief is a fact about the world, not about
    # this guard. Reachability is a property of the CODE and is proven against a belief built to
    # satisfy every condition.
    reachable = ceiling_vs_belief({
        "route": "renewal", "decisions": 144, "oracle_auc": 0.7400,
        "company_belief": [{
            "belief": "a constructed belief that satisfies every condition",
            "field": "constructed", "available": True,
            "seeds_the_world_roll": False, "independent_of_the_outcome": True,
            "decisions": 144, "belief_auc": 0.65,
            "null": {"low": 0.40, "high": 0.60, "median": 0.5, "permutations": 200},
            "clears_the_null": True,
        }],
    })["readings"][0]
    assert reachable["excess_over_chance_captured"] is not None, (
        "a belief that is independent, counts one population, clears its null and carries no "
        "exposure offset was still refused a ratio: the guard cannot be told apart from a "
        "function that always refuses"
    )


def test_a_ratio_is_refused_when_the_belief_is_inside_its_null():
    """A reading inside its null is `we cannot tell`, and a percentage of the ceiling made from one
    reads as a finding.

    Measured on the real book: `company_churn_estimate` scores 0.4988 inside [0.3829, 0.6241] and
    the ratio it yields is -0.5%. A number with the authority of a measurement and the content of
    noise. It must be refused rather than rounded to zero.
    """
    rows = _rows(belief_key=None)
    # A belief that carries no information: constant-ish, uncorrelated with who left.
    for i, row in enumerate(rows):
        row["company_churn_estimate"] = 0.2 + 0.0001 * (i % 7)
    readings = belief_readings(rows, "renewal", permutations=400)
    graded = [r for r in readings if r.get("available")]
    assert graded, "the uninformative belief was not graded at all"
    inside = [r for r in graded if not r["clears_the_null"]]
    assert inside, (
        "a belief built to carry no signal cleared its null -- the fixture cannot exercise this "
        "guard, so the guard is untested rather than passing"
    )
    # WHICH BELIEFS ARE UNINFORMATIVE IS DECIDED FROM `belief_readings`, NOT FROM THE COMPARISON'S
    # OWN `clears_its_null`. Keying the skip to the field under test let a mutation that hard-wires
    # `clears = True` slip through: the comparison claimed the belief cleared, the loop skipped it,
    # and the test passed while publishing a ratio built on noise. A control must not take the
    # subject's word for the thing it is checking.
    uninformative = {r["field"] for r in graded if not r["clears_the_null"]}
    assert uninformative, "no belief came out inside its null; the guard has no subject here"
    entry = _entry(rows, readings)
    checked = 0
    for reading in ceiling_vs_belief(entry)["readings"]:
        if reading["field"] not in uninformative:
            continue
        checked += 1
        assert reading["excess_over_chance_captured"] is None, (
            f"{reading['field']} reads inside its null and a fraction of the ceiling "
            f"({reading['excess_over_chance_captured']}) was published from it anyway"
        )
        assert "INSIDE its null" in reading["refused_because"]
    assert checked == len(uninformative), (
        "an uninformative belief produced no comparison entry, so the refusal was never exercised"
    )


def test_the_join_refuses_a_run_that_is_not_the_capture(tmp_path):
    """The independent belief may only be joined from the run that produced the capture.

    Captures taken before 2026-08-31 do not carry `company_churn_estimate`, so it is joined from
    the published run output -- and joining two artefacts is how this project has published a
    figure whose legs came from different runs. The join verifies every row's realised hazard
    rather than trusting the file name.
    """
    rows = _rows(belief_key=None)
    events = [
        {
            "customer_id": r["customer_id"],
            "event_date": r["event_date"],
            "realized_churn_probability": r["realized_churn_probability"],
            "company_churn_estimate": 0.3,
        }
        for r in rows
    ]
    same = tmp_path / "same_run.json"
    same.write_text(json.dumps({"customer_events": events}))
    joined, provenance = attach_company_beliefs(rows, same)
    assert provenance["joined"] is True
    assert all(r["company_churn_estimate"] == 0.3 for r in joined)

    # One household's hazard differs by more than the tolerance: a different run of the world.
    events[3]["realized_churn_probability"] += 1e-6
    other = tmp_path / "other_run.json"
    other.write_text(json.dumps({"customer_events": events}))
    with pytest.raises(Unreadable, match="not the same run"):
        attach_company_beliefs(rows, other)

    # A household missing from the log entirely is the same class of defect.
    missing = tmp_path / "short_run.json"
    missing.write_text(json.dumps({"customer_events": events[:-1]}))
    with pytest.raises(Unreadable, match="not the same run"):
        attach_company_beliefs(rows, missing)


def test_the_join_is_skipped_once_the_capture_carries_the_field(tmp_path):
    """`capture_departure_factors` records the field from 2026-08-31, and the join must then go
    quiet rather than persisting as a second code path that can disagree with the first."""
    rows = _rows(belief_key=None)
    for row in rows:
        row["company_churn_estimate"] = 0.11
    unusable = tmp_path / "nonexistent.json"
    joined, provenance = attach_company_beliefs(rows, unusable)
    assert provenance["joined"] is False
    assert joined == rows, "the join altered rows it should not have touched"
