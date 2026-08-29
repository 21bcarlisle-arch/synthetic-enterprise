"""The growth curve must say WHICH constraint gave it its shape.

Director, 2026-08-24 console: *"if our own code binds growth rather than the simulated economics,
say so on the site and fix it if it's cheap. A growth curve that's an artefact of our engine is an
inconsistency, not a result."*

WHAT IS UNDER TEST is the DISCRIMINATION, not the numbers. A flat year has four possible causes --
the supplier could not afford to quote, the supplier chose not to grow, almost nobody was
switching, or our settlement engine refused to settle the wins -- and exactly one of those is a
defect in us rather than a fact about the company. A file that rendered the curve without that
distinction would be worse than no file: it would publish our own machine limit as a commercial
result.

R15: every control below is paired with the mutation that injects the defect it guards.
"""
from __future__ import annotations

import json

import pytest

from tools import generate_book_growth_data as gb


def _campaign(*bindings, **kw):
    """A campaign record whose years carry the given binding reasons, in order."""
    return {
        "by_year": [
            {"year": 2016 + i, "quotes_issued": 10 * (i + 1), "wins": 3, "funnel_wins": 3,
             "wins_refused_by_settlement_budget": 0, "accounts_after": 20 + i,
             "book_after": 20 + i,
             "spend_gbp": 100.0, "binding": b, "homes_in_market": 400,
             "switching_multiplier": 1.0, "believed_win_rate": 0.2,
             "realised_win_rate_used": None, "planning_on": "belief"}
            for i, b in enumerate(bindings)
        ],
        "notes": kw.get("notes", []),
        "quotes": 100, "wins": 9, "spend_gbp": 1000.0,
        "customer_years_committed": 590.0, "customer_year_budget": 600.0,
        "settlement_sample_rate": kw.get("sample_rate", 1.0),
    }


def test_a_year_our_engine_stopped_is_flagged_as_OUR_artefact():
    """THE ASSERTION THAT CARRIES THE FILE. settlement_engine is the one binding reason that is a
    fact about us rather than about the company.

    STILL TESTED THOUGH THE SHIPPED CAMPAIGN NO LONGER PRODUCES IT (2026-08-29): the ceiling now
    samples the campaign instead of stopping a year, so `binding` stays commercial. The label and
    the flag are kept because a future ceiling that DOES stop a year must not render as
    'unrecognised', and a classifier deleted the day its input went quiet is a classifier that
    has to be rediscovered the day it comes back."""
    out = gb.build(_campaign("settlement_engine"))
    year = out["years"][0]

    assert year["binding_is_our_artefact"] is True
    assert year["binding_label"] == "Our settlement engine"
    assert out["engine_bound_years"] == [2016]


@pytest.mark.parametrize("binding", ["capital", "growth_rate", "market", "mandate"])
def test_MUTATION_every_COMMERCIAL_reason_is_NOT_flagged_as_our_artefact(binding):
    """R15 null control. If everything were flagged, the flag would carry no information and the
    test above would pass on a file that simply always said 'artefact'. A thin market in 2022 is a
    real feature of GB retail and must NOT be published as a defect in us."""
    out = gb.build(_campaign(binding))

    assert out["years"][0]["binding_is_our_artefact"] is False
    assert out["engine_bound_years"] == []


# ── the HEADLINE, which is keyed to the sample rate and not to a binding label ───────────────
#
# THE FAILURE THIS REPLACES, because it is the reason the tests below look the way they do.
# Until 2026-08-29 the headline was built from `engine_bound_years`, which is the set of years
# carrying `binding == settlement_engine`. That was right while the ceiling STOPPED a year dead.
# The ceiling now takes a uniform sample of the whole campaign instead, so no year is stopped,
# `engine_bound_years` is honestly empty -- and the old headline would have published "no year
# was bound by our settlement engine" on a run where four wins in five were refused. The control
# did not go red. It went QUIET, which is the direction that gets published.
#
# So the headline is keyed to how much of what the company won reached the book, which is the
# question a reader actually has and which has an answer under either mechanism.

def test_the_headline_states_the_share_of_its_own_wins_the_machine_could_settle():
    """THE ASSERTION THAT CARRIES THE FILE now. A book that is a sample must say the rate, and
    say it in a form the reader can undo."""
    out = gb.build(_campaign("growth_rate", "capital", sample_rate=0.2))
    # 3 booked and 3 funnel wins per year in the fixture; the rate is what the record declares.
    assert out["settlement_sample_rate"] == 0.2
    assert "20.0% sample" in out["engine_bound_statement"]
    assert "Divide a booked count by 0.200" in out["engine_bound_statement"]


def test_MUTATION_a_run_that_settled_EVERY_win_does_not_claim_a_sample():
    """R15 null control. If the sampled headline rendered whatever the rate, it would tell a
    reader to divide by 1.0 and would carry no information."""
    out = gb.build(_campaign("growth_rate", sample_rate=1.0))

    assert "sample" in out["engine_bound_statement"]
    assert "settled every account the company won" in out["engine_bound_statement"]
    assert "Divide" not in out["engine_bound_statement"]


def test_a_record_with_NO_sample_rate_says_it_cannot_tell_and_never_the_clean_branch():
    """FAIL CLOSED (R15). A record written before the rate existed carries no evidence that
    nothing was refused, and the flattering branch is a claim. 'We cannot tell' is the result and
    it belongs on the page."""
    record = _campaign("growth_rate")
    del record["settlement_sample_rate"]
    out = gb.build(record)

    assert out["settlement_sample_rate"] is None
    assert "CANNOT BE READ FROM IT" in out["engine_bound_statement"]
    assert "settled every account" not in out["engine_bound_statement"]


def test_the_headline_counts_the_wins_the_MACHINE_refused_not_the_ones_the_market_did():
    """The two are different populations and the page publishes one of them. A year that quoted
    and lost is commercial; a year that won and could not be settled is ours."""
    record = _campaign("growth_rate", "capital", sample_rate=0.5)
    for row in record["by_year"]:
        row["funnel_wins"] = 6
        row["wins"] = 3
        row["wins_refused_by_settlement_budget"] = 3
    out = gb.build(record)

    assert out["settlement_funnel_wins"] == 12
    assert out["settlement_wins_refused"] == 6
    assert "won 12 accounts" in out["engine_bound_statement"]
    assert "settle 6 of them" in out["engine_bound_statement"]


def test_our_prospect_pool_and_the_REAL_market_are_told_apart_on_the_page():
    """THE SECOND ARTEFACT, added 2026-08-29, and the pair is only worth having if it splits.

    A year capped because the company could afford more quotes than we minted prospects for is
    OURS and should be raised. A year capped because 2022 was a crisis in which almost nobody
    switched supplier is the GB market, and raising anything would falsify it. One shared
    "capped" label would hand a reader the wrong instruction on whichever year it got wrong.
    """
    out = gb.build(_campaign("prospect_ceiling", "market", "capital"))
    ours, theirs, commercial = out["years"]

    assert ours["binding_is_our_artefact"] is True
    assert ours["binding_label"] == "Our prospect pool"
    assert "NOT the GB switching market" in ours["binding_meaning"]

    assert theirs["binding_is_our_artefact"] is False, (
        "the real switching market rendered as a defect in us -- a reader told to raise the "
        "pool on a crisis year would be falsifying the record"
    )
    assert commercial["binding_is_our_artefact"] is False

    assert out["prospect_ceiling_years"] == [2016]
    assert out["artefact_bound_years"] == [2016]
    assert "PROSPECTS_PER_YEAR" in out["prospect_ceiling_statement"]


def test_the_ENGINE_bound_list_does_not_quietly_absorb_the_other_artefact():
    """Two artefacts, two names, and neither may answer for the other.

    `engine_bound_years` means years the SETTLEMENT engine stopped. When the prospect pool
    became a second artefact it would have joined that list for free, and a name that no
    longer means what it says is unfalsifiable -- the failure this file spent 2026-08-29
    repairing three times over.
    """
    out = gb.build(_campaign("prospect_ceiling", "settlement_engine"))

    assert out["engine_bound_years"] == [2017], "the prospect pool is not the settlement engine"
    assert out["prospect_ceiling_years"] == [2016]
    assert out["artefact_bound_years"] == [2016, 2017], "the wider list must hold both"


def test_MUTATION_a_run_our_prospect_pool_never_capped_claims_no_such_year():
    """R15 null control. A statement rendered whatever the data would carry no information."""
    out = gb.build(_campaign("capital", "market", "growth_rate"))

    assert out["prospect_ceiling_years"] == []
    assert "No year was capped by our prospect pool" in out["prospect_ceiling_statement"]
    assert out["artefact_bound_years"] == []


def test_an_unrecognised_binding_is_shown_VERBATIM_and_never_guessed():
    """A binding reason this file has not been taught is a gap in this file, not a licence to
    classify. It must not silently become 'not our artefact' with a confident label."""
    out = gb.build(_campaign("some_new_reason"))
    year = out["years"][0]

    assert year["binding"] == "some_new_reason"
    assert year["binding_label"] == "some_new_reason"
    assert "Unrecognised" in year["binding_meaning"]


def test_a_missing_record_publishes_UNAVAILABLE_and_never_a_curve_of_zeroes():
    """FAIL-OPEN GUARD (R15). A zeroed curve is a CLAIM -- that the supplier won nothing -- and it
    is indistinguishable on a chart from a real collapse. Absence of a record is not evidence of
    absence of growth."""
    for empty in (None, {}, {"by_year": []}):
        out = gb.build(empty)
        assert out["available"] is False
        assert out["years"] == []
        assert "no campaign record" in out["reason"]
        assert "engine_bound_statement" not in out, (
            "an absent record must not produce a headline about what bound the book"
        )


# ── the SECOND artefact: the conversion rate the company plans the next campaign on ──────────
#
# The curve is not the only thing our engine can shape. `dcba2f2e2` gave the company a win-rate
# learning loop, and if the number it learns from is the count of wins THIS MACHINE settled
# rather than the count its funnel converted, then our ceiling is inside its commercial belief:
# the rate falls with no commercial mechanism suppressing it, the quote budget is derived from
# that rate, and the acquisition spend a reader judges growth by is derived from the budget.
# That really happened (WORKER_FINDING_THE_COMPANY_NOW_LEARNS_A_WIN_RATE_FROM_YEARS_AN_
# ENGINEERING_CAP_DECIDED) and was fixed company-side on 2026-08-28.
#
# WHAT IS TESTED HERE IS THE PROPERTY, NOT A LIST OF YEARS, and the rewrite of 2026-08-29 is
# the reason. The old flag was positional -- find the years binding on `settlement_engine`, latch
# every later rate -- and it broke twice in four days without going red once:
#
#   * the 2026-08-28 company-side fix made the rate clean at source, and this flag went on
#     caveating it; the published statement still said the series "decays 0.169 -> 0.051" when
#     the record had been flat at ~0.175 for a day.
#   * the 2026-08-29 sampling change removed `settlement_engine` from `binding` entirely, and
#     the same flag would have flipped to "none of them is an artefact of our engine".
#
# One flag, two opposite failures, both from asking WHICH YEAR. The question the reader has is
# whether the number the company planned on equals what its own funnel converted over the
# earlier years -- checkable on every row, true or false for a reason, and red the moment
# anyone re-wires the planner back onto booked wins.
#
# MUTATION SENSITIVITY (R15):
#   * plan on BOOKED wins -> `test_MUTATION_a_rate_computed_from_the_BOOKED_wins_is_flagged` red.
#   * treat an uncheckable record as clean ->
#     `test_a_record_without_the_funnels_own_win_count_is_UNCHECKED_never_clean` red.
#   * flag every year -> `test_MUTATION_a_rate_that_matches_the_funnel_is_NOT_flagged` red.
#   * caveat a year that planned on belief ->
#     `test_a_year_that_planned_on_BELIEF_has_no_learned_rate_to_caveat` red.

def _learning_campaign(*specs, funnel=None):
    """Years of (binding, planning_on, realised_win_rate_used).

    `quotes_issued` is 10, 20, 30... and `funnel_wins` defaults to 2 per year, so the rate a
    year should have planned on is the cumulative funnel wins over the cumulative quotes of
    every STRICTLY EARLIER year. `funnel` overrides the per-year funnel win counts.
    """
    rows = []
    for i, (b, plan, rate) in enumerate(specs):
        rows.append(
            {"year": 2016 + i, "quotes_issued": 10 * (i + 1), "wins": 3,
             "funnel_wins": 2 if funnel is None else funnel[i],
             "wins_refused_by_settlement_budget": 0, "accounts_after": 20 + i,
             "book_after": 20 + i,
             "spend_gbp": 100.0, "binding": b, "homes_in_market": 400,
             "switching_multiplier": 1.0, "believed_win_rate": 0.2,
             "realised_win_rate_used": rate, "planning_on": plan})
    return {
        "by_year": rows,
        "notes": [], "quotes": 100, "wins": 9, "spend_gbp": 1000.0,
        "customer_years_committed": 590.0, "customer_year_budget": 600.0,
        "settlement_sample_rate": 1.0,
    }


def _funnel_rate(rows, upto):
    """What year index `upto` should have planned on: the funnel's cumulative rate before it."""
    q = sum(r["quotes_issued"] for r in rows[:upto])
    w = sum(r["funnel_wins"] for r in rows[:upto])
    return w / q


def test_MUTATION_a_rate_that_matches_the_funnel_is_NOT_flagged():
    """R15 null control, and the branch the shipped run takes. If every rate were flagged the
    caveat would carry no information and a reader would learn to ignore it."""
    rows = _learning_campaign(
        ("growth_rate", "belief", None),
        ("growth_rate", "realised", None),
        ("capital", "realised", None),
    )["by_year"]
    for i in (1, 2):
        rows[i]["realised_win_rate_used"] = _funnel_rate(rows, i)
    out = gb.build({"by_year": rows, "notes": [], "quotes": 100, "wins": 9,
                    "spend_gbp": 1000.0, "customer_years_committed": 590.0,
                    "customer_year_budget": 600.0, "settlement_sample_rate": 1.0})

    assert out["learned_win_rate_contaminated_years"] == []
    assert "CHECKED against what its own funnel converted" in out["win_rate_statement"]
    assert "commercial outcomes only" in out["years"][1]["learned_win_rate_caveat"]


def test_MUTATION_a_rate_computed_from_the_BOOKED_wins_is_flagged():
    """THE DEFECT THIS EXISTS TO CATCH, injected. A planner wired to the wins our machine
    SETTLED rather than to the wins its funnel converted plans on our ceiling. With a sample rate
    near a fifth the two numbers differ by a factor of five, so a supplier converting 18% reads
    as converting 3% and buys quotes accordingly."""
    rows = _learning_campaign(
        ("growth_rate", "belief", None),
        ("growth_rate", "realised", None),
        ("capital", "realised", None),
        funnel=[10, 10, 10],
    )["by_year"]
    for r in rows:
        r["wins"] = 2  # the machine settled 2 of the 10 the funnel won
    for i in (1, 2):
        q = sum(x["quotes_issued"] for x in rows[:i])
        rows[i]["realised_win_rate_used"] = sum(x["wins"] for x in rows[:i]) / q
    out = gb.build({"by_year": rows, "notes": [], "quotes": 100, "wins": 9,
                    "spend_gbp": 1000.0, "customer_years_committed": 590.0,
                    "customer_year_budget": 600.0, "settlement_sample_rate": 0.2})

    assert out["learned_win_rate_contaminated_years"] == [2017, 2018]
    assert "From 2017 onward" in out["win_rate_statement"]
    assert "does not match what its own funnel converted" in out["win_rate_statement"]
    assert out["years"][1]["learned_win_rate_is_contaminated"] is True


def test_a_record_without_the_funnels_own_win_count_is_UNCHECKED_never_clean():
    """FAIL CLOSED (R15). A record written before `funnel_wins` existed cannot be checked, and
    'unchecked' rendering as 'checked and clean' is a reassurance nobody verified. The published
    caveat has to be able to say the third thing."""
    rows = _learning_campaign(
        ("growth_rate", "belief", None),
        ("growth_rate", "realised", 0.2),
    )["by_year"]
    for r in rows:
        del r["funnel_wins"]
    out = gb.build({"by_year": rows, "notes": [], "quotes": 100, "wins": 9,
                    "spend_gbp": 1000.0, "customer_years_committed": 590.0,
                    "customer_year_budget": 600.0})

    assert out["years"][1]["learned_win_rate_is_contaminated"] is True
    assert "CANNOT BE CHECKED" in out["years"][1]["learned_win_rate_caveat"]
    assert "Read it as unverified, not as clean" in out["years"][1]["learned_win_rate_caveat"]


def test_a_year_that_planned_on_BELIEF_has_no_learned_rate_to_caveat():
    """The company's opening years plan on a mandate figure, not on their own books. Attaching a
    contamination warning there would warn about a number the company never computed."""
    out = gb.build(_learning_campaign(
        ("settlement_engine", "realised", 0.17),
        ("growth_rate", "belief", None),
    ))

    assert out["years"][1]["learned_win_rate_is_contaminated"] is False
    assert out["years"][1]["learned_win_rate_caveat"] == ""
    assert 2017 not in out["learned_win_rate_contaminated_years"]


def test_the_statement_names_the_spend_a_reader_would_judge_growth_by():
    """The quote budget is derived from the learned rate, and the acquisition spend from the quote
    budget. A caveat that stopped at the percentage would leave the money figure uncaveated."""
    out = gb.build(_learning_campaign(
        ("settlement_engine", "realised", 0.17), ("settlement_engine", "realised", 0.12),
    ))

    assert "acquisition spend" in out["win_rate_statement"]


def test_every_published_money_figure_carries_its_clock():
    """R14: no financial figure without its basis."""
    out = gb.build(_campaign("capital", "settlement_engine"))

    assert out["totals"]["clock"] == "settled"
    for year in out["years"]:
        assert year["spend_gbp"] is not None
        assert year["clock"] == "settled"


def test_the_generator_writes_the_file_and_survives_an_unreadable_record(tmp_path):
    """End-to-end, including the branch that matters operationally: a corrupt or absent source
    must still produce a readable file rather than leaving the previous run's curve live under a
    fresh timestamp."""
    out_path = tmp_path / "book_growth.json"

    src = tmp_path / "campaign.json"
    src.write_text(json.dumps(_campaign("settlement_engine")), encoding="utf-8")
    gb.generate(out_path=out_path, campaign_path=src)
    assert json.loads(out_path.read_text())["engine_bound_years"] == [2016]

    src.write_text("{not json", encoding="utf-8")
    gb.generate(out_path=out_path, campaign_path=src)
    written = json.loads(out_path.read_text())
    assert written["available"] is False, "a corrupt record must not leave a stale curve claiming to be current"


def test_the_generator_is_WIRED_into_the_publish_cycle():
    """The class this project keeps finding: a generator with no caller. The campaign record it
    reads was itself written every run for a reader that did not exist, which is the whole reason
    this file was needed -- so assert the caller, not just the callee."""
    from pathlib import Path

    src = Path(gb.__file__).resolve().parent.parent / "background" / "process_run_complete.py"
    text = src.read_text(encoding="utf-8")
    assert "from tools.generate_book_growth_data import generate" in text
    assert "gen_growth()" in text


# ── the REFUSAL must name its own cause ──────────────────────────────────────────────────────────
#
# The unavailable branch is reached three ways and they carry three different instructions: the
# record is a RUN OUTPUT that a fresh checkout simply does not have (run the simulation); or it is
# on disk and will not parse (a defect in the writer); or a run wrote it with no years (a defect in
# the run). Until 2026-08-29 all three published ONE sentence -- "no run has assembled a book since
# this generator was wired" -- and `generate()` caught OSError and ValueError together, so the
# distinction was destroyed at the only site that could see it. That sentence asserts a fact about
# HISTORY this generator cannot observe, and it is false in the commonest of the three: the page
# reader is sent to check the wiring when what they need to do is run the simulation.


def test_the_three_absence_causes_do_not_publish_one_reason(tmp_path):
    """R15 MIXED SUBJECT: a refusal spanning three causes that prints one string reports the OR, so
    the two causes it does not describe read to the reader as the one it does.

    MUTATION: give any two keys of `gb.ABSENCE_REASON` the same text, or drop the second argument
    at the `build(campaign, absence)` call site in `generate()` so every cause falls back to the
    unknown reason. Either collapses the distinct-reason count below and reds this test.
    """
    out_path = tmp_path / "book_growth.json"
    src = tmp_path / "campaign.json"
    seen = {}

    # MISSING -- the file is not there at all. This is exactly what a fresh checkout of main is.
    assert not src.exists()
    seen["missing"] = gb.generate(out_path=out_path, campaign_path=src)

    # UNREADABLE -- on disk, does not parse.
    src.write_text("{not json", encoding="utf-8")
    seen["unreadable"] = gb.generate(out_path=out_path, campaign_path=src)

    # EMPTY -- parses, carries no campaign.
    src.write_text(json.dumps({"by_year": []}), encoding="utf-8")
    seen["empty"] = gb.generate(out_path=out_path, campaign_path=src)

    for cause, data in seen.items():
        assert data["available"] is False, cause
        assert data["absence"] == cause, (
            "the {} case was classified as {!r}".format(cause, data["absence"]))

    texts = {cause: data["reason"] for cause, data in seen.items()}
    assert len(set(texts.values())) == 3, (
        "three causes published {} distinct reason(s): {}".format(len(set(texts.values())), texts))


def test_every_absence_reason_names_what_a_reader_can_check_and_refuses_the_zero_reading():
    """Keyed to the PROPERTY, not to today's wording. A refusal that names a cause the generator
    did not observe is worse than one that names none, so the three CLASSIFIED reasons must point
    at the record a reader can go and look at, and every reason -- including the unclassified
    fallback -- must say out loud that this is an absent record rather than a supplier that won
    nothing. That second half is the fail-open guard: `available: false` on a growth page is one
    click from being read as a flat curve.

    MUTATION: drop `{path}` from any entry of `gb.ABSENCE_REASON`, or delete the CANNOT/NOT
    disclaimer from any reason, and this reds.
    """
    rel = gb.CAMPAIGN_PATH.relative_to(gb.PROJECT).as_posix()

    for cause, template in gb.ABSENCE_REASON.items():
        assert "{path}" in template, (
            "the {} reason does not tell the reader which file to look at".format(cause))
        assert rel in template.format(path=rel)

    for label, text in list(gb.ABSENCE_REASON.items()) + [("unknown", gb.UNKNOWN_ABSENCE_REASON)]:
        low = text.lower()
        assert ("won nothing" in low) or ("never assembled" in low) or ("does not mean" in low), (
            "the {} reason lets `available: false` be read as a supplier that won nothing".format(
                label))
        # The observability limit that produced the original false sentence: this generator sees
        # one file at one instant. It can never speak about whether a run happened.
        assert "no run has" not in low, (
            "the {} reason asserts a fact about run history the generator cannot observe".format(
                label))


def test_an_unrecognised_absence_class_claims_no_cause_at_all(tmp_path):
    """FAIL-CLOSED on the lookup itself. If a caller passes a class this file has not been taught,
    the safe answer is 'we were not told why', never the first plausible cause -- silently
    reporting the wrong one is the defect this whole block repairs.

    MUTATION: make the fallback in `build` pick any entry of `ABSENCE_REASON` instead of
    `UNKNOWN_ABSENCE_REASON` and this reds.
    """
    out = gb.build(None, "some_cause_this_file_has_never_heard_of")

    assert out["available"] is False
    assert out["absence"] is None, "an untaught class must not be published as if it were read"
    assert out["reason"] == gb.UNKNOWN_ABSENCE_REASON
    assert out["years"] == []
