"""R15 contract for the two-arm pricing comparison.

WHAT IS GUARDED is not the arithmetic — `tests/company/pricing/test_value_based_renewal.py` owns
that — but the two ways a comparison like this lies: by reporting a verdict its own numbers do
not support, and by quietly covering fewer accounts than it appears to.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH
from tools import couple_value_based_pricing as cvp

REPO = Path(__file__).resolve().parents[2]

RUN = {"per_customer_lifetime": {
    "C1": {"segment": "resi", "cost_to_serve_gbp": 330.0},
    "C2": {"segment": "resi", "cost_to_serve_gbp": 120.0},
    "C3": {"segment": "resi", "cost_to_serve_gbp": 90.0},
}}
BOOK = {"customers": [
    {"legs": {"e": {"cid": "C1", "total_kwh": 30000, "avg_effective_rate_gbp_per_mwh": 150.0, "bill_count": 60}}},
    {"legs": {"e": {"cid": "C2", "total_kwh": 9000, "avg_effective_rate_gbp_per_mwh": 140.0, "bill_count": 36}}},
    {"legs": {"e": {"cid": "C3"}}},          # no consumption on record at all
]}


def test_an_account_the_company_cannot_price_is_NAMED_not_dropped():
    """A comparison silently covering two of three accounts is a different claim from one
    covering all three, and the difference is invisible unless it is stated."""
    out = cvp.compare(RUN, BOOK)

    assert out["accounts_priced"] == 2
    assert sum(out["accounts_skipped"].values()) == 1
    assert "no consumption or rate" in " ".join(out["accounts_skipped"])


def test_the_control_is_the_IMPORTED_constant_and_says_what_it_is():
    out = cvp.compare(RUN, BOOK)

    assert out["control"]["margin_gbp_per_mwh"] == TARGET_MARGIN_GBP_PER_MWH
    assert "what this company does today" in out["control"]["what_it_is"]


def test_the_VERDICT_is_derived_from_the_rows_and_not_written_beside_them():
    """A verdict a reader has to check against the table is a verdict that will be quoted without
    checking. The invariant: if the arm's choice sat at the edge of what it was allowed on ANY
    account, the comparison is not fit to run — because on that account the ceiling decided, not
    the customer.

    MUTATION (must fire): return `fit_to_run: True` unconditionally.
    """
    out = cvp.compare(RUN, BOOK)
    at_edge = sum(1 for r in out["accounts"] if r["endpoint_bound"])

    if at_edge:
        assert out["verdict"]["fit_to_run"] is False
        assert "not a decision, it is a ceiling" in out["verdict"]["why"]
    else:
        assert isinstance(out["verdict"]["fit_to_run"], bool)


def test_a_book_the_arm_can_actually_decide_on_reports_FIT(monkeypatch):
    """THE NULL, and without it "not fit to run" is also satisfied by a verdict hard-coded to
    refuse. Blind the search to an interior winner and the verdict must turn."""
    from company.pricing import value_based_renewal as vbr

    interior = {2.0: 5.0, 3.0: 50.0, 5.0: 5.0}

    def _fake(*, arm, customer_id, **kw):
        best = max(interior, key=interior.get)
        margin = TARGET_MARGIN_GBP_PER_MWH if arm == vbr.FLAT_RULES else best
        return vbr.MarginDecision(
            customer_id=customer_id, arm=arm, margin_gbp_per_mwh=margin,
            expected_value_gbp=interior[margin], p_retain=0.9, expected_periods=3.0,
            cost_to_serve_gbp_per_year=50.0, eac_mwh=3.1,
            considered=tuple(interior.items()), endpoint_bound=False,
        )

    monkeypatch.setattr(cvp, "decide_margin", _fake)
    out = cvp.compare(RUN, BOOK)

    assert out["verdict"]["fit_to_run"] is True
    assert "interior optima" in out["verdict"]["why"]


def test_an_EMPTY_book_is_a_comparison_that_did_not_run_not_one_that_found_nothing():
    out = cvp.compare({"per_customer_lifetime": {}}, {"customers": []})

    assert out["verdict"]["fit_to_run"] is False
    assert "nothing was compared" in out["verdict"]["why"]


@pytest.mark.skipif(not (REPO / "site" / "data" / "customers.json").is_file(),
                    reason="no published book in this tree")
def test_the_LIVE_book_reports_a_verdict_consistent_with_its_own_rows(tmp_path):
    """R11 to the value that will be quoted. Deliberately does NOT pin `fit_to_run: False` — a
    future fix to the churn model should turn it True and must not have to edit a test to do so.
    What is pinned is that the verdict follows the rows, so it cannot be made True by writing
    True."""
    # Written to tmp_path, not to the real artefact: a test that regenerates a published
    # diagnostic makes the suite a producer, and the next reader cannot tell a measurement from
    # a test run.
    data = cvp.generate(tmp_path / "arms.json")

    # THE ARM MAY LEGITIMATELY PRICE NOTHING, AND ONLY FOR ONE NAMED REASON (2026-08-31). It now
    # reads `avg_effective_rate_gbp_per_mwh` -- what the customer actually pays -- where it used to
    # read `avg_rate_gbp_per_mwh`, which was the COMMODITY leg and left every comparison anchored
    # 1.53x low across the real book. A `site/data/customers.json` published before that change
    # carries no effective rate, so the arm refuses every account and SAYS SO.
    #
    # This is not the assertion being weakened to accommodate a transition. Pricing zero accounts
    # is only accepted when the arm's own skip ledger names THAT cause; any other zero still reds,
    # and the moment the surface is regenerated the first branch is the live one again. The
    # alternative -- falling back to the commodity leg -- would restore the defect while looking
    # like resilience.
    stale = [r for r in data.get("accounts_skipped", {}) if "no effective rate" in r]
    if data["accounts_priced"] == 0:
        assert stale, (
            "the arm priced nothing and did not name the two-rate transition as the cause: "
            f"{data.get('accounts_skipped')}"
        )
        return

    at_edge = sum(1 for r in data["accounts"] if r["endpoint_bound"])
    assert data["verdict"]["fit_to_run"] == (at_edge == 0
                                             and data["median_implied_bill_change_pct"] < 25.0)


def _a_book_of(n: int) -> tuple[dict, dict]:
    """A synthetic book wide enough for a CONCENTRATION to mean something.

    THE RATE FIELD IS `avg_effective_rate_gbp_per_mwh` SINCE 2026-08-31, and the rename is the whole
    point of the change that forced it. `avg_rate_gbp_per_mwh` was the COMMODITY leg — wholesale
    energy, no network charges, no levies, no standing charge, no VAT — and `compare` was reading it
    as `current_rate_gbp_per_mwh`, "what this customer currently pays". Measured across the real
    book: 102.57 against 156.42 GBP/MWh, so every price this arm compared against was anchored 1.53x
    low. A fixture that still emitted the old name would price ZERO accounts and say so, which is
    how the pre-commit gate caught this module — the field's readers were searched, its READERS'
    TESTS were not.

    NOT THE LIVE BOOK, AND THAT IS THE POINT. The first version of the two controls below read
    the published book, and the pre-commit gate refused them: the gate builds its tree from HEAD
    plus the pathspec, `latest_run_output()` picks the newest `run_output_*.json` ON DISK, and
    the newest one here was an untracked artefact another lane had just written. The control was
    therefore graded against a different book from the one it passed on -- a control whose
    subject moves under it is not measuring what it names (R15 fail-open by drifting subject).
    The population claim is about the SEARCH, so the book only has to be varied and wide.
    """
    run, customers = {}, []
    for i in range(n):
        cid = f"S{i}"
        run[cid] = {"segment": "resi", "cost_to_serve_gbp": 60.0 + 2.0 * (i % 25),
                    "commodity": "electricity"}
        kwh = 1200.0 + 300.0 * (i % 40)
        rate = 110.0 + 1.7 * (i % 30)
        customers.append({"legs": {"e": {
            "cid": cid, "total_kwh": kwh * 3, "avg_effective_rate_gbp_per_mwh": rate,
            "bill_count": 36, "revenue_gbp": kwh * 3 * rate / 1000.0}}})
    return {"per_customer_lifetime": run}, {"customers": customers}


def test_a_WIDE_book_does_not_pile_a_THIRD_of_itself_onto_ONE_MARGIN():
    """THE POPULATION CONTROL, and the one that would have caught this a week earlier.

    Nothing in the per-account record was wrong on 2026-08-25 -- each row was a legitimate argmax
    over the candidates it was given. The defect was only visible ACROSS the book: 107 of 263
    published accounts on exactly GBP 130/MWh and 83 more on exactly 100, two rungs of the
    module's own candidate grid carrying 72% of the customers. A per-customer decision that
    returns the same number for a third of the book is reporting its own constants, and no
    single-account test can see it.

    The threshold is 10% and it is a long way from both sides: measured on the published book,
    the grid-quantised record was 40.7% and the refined one is 1.9%.

    MUTATION (must fire): return the grid's argmax instead of refining it.
    """
    run, book = _a_book_of(60)
    out = cvp.compare(run, book)

    assert out["accounts_priced"] >= 50, "too few accounts for a concentration to mean anything"
    assert out["chosen_margin_concentration"] < 0.10, (
        "{:.1%} of the book was given one identical margin, so the answer is being quantised "
        "onto something other than the customer".format(out["chosen_margin_concentration"])
    )


def test_a_WIDE_book_separates_a_TRIMMED_grid_from_a_BINDING_bound():
    """The record's own reading of itself, pinned. On the published book 165 accounts have
    candidates removed by the support bound and NONE of them would have chosen a removed one --
    the two facts have to be separately legible or the count gets read as the cause, which is
    exactly what happened.

    MUTATION (must fire): set `extrapolation_bound = candidates_removed > 0` again.
    """
    run, book = _a_book_of(60)
    out = cvp.compare(run, book)

    assert out["grid_trimmed"] > 0, "nothing was trimmed on this book, so this proves nothing"
    assert out["extrapolation_bound"] < out["grid_trimmed"], (
        "every account whose grid was trimmed is also reported as having been DECIDED by the "
        "bound, which is the conflation this field exists to stop"
    )


# --------------------------------------------------------------------------- #
# The coupled-triad measurement: belief against truth, at the chosen price     #
# --------------------------------------------------------------------------- #

def test_the_gap_is_measured_at_the_price_the_ARM_ACTUALLY_CHOOSES():
    """The whole point of measuring it here rather than at a renewal that happened. The thesis is
    that advantage comes from prediction, so the number that matters is how wrong the company is
    AT THE PRICE ITS OWN DECISION PICKS -- not at the price it happened to charge last year."""
    scored = cvp.belief_versus_truth(offered_rate=200.0, current_rate=150.0, tenure_years=4.0,
                                     eac_kwh=3100, segment="resi", term_start="2025-01-01")

    assert scored is not None
    assert set(scored) >= {"price_differential_vs_svt", "company_believes_p_leave",
                           "world_would_p_leave", "belief_error_pp"}


def test_an_UNKNOWN_market_position_is_NOT_scored_as_a_perfect_prediction():
    """R15 fail-silent, in the direction that would flatter the company most: an unscoreable
    account returning a zero error would report perfect foresight, and the summary averages it."""
    assert cvp.belief_versus_truth(offered_rate=200.0, current_rate=150.0, tenure_years=4.0,
                                   eac_kwh=3100, segment="resi", term_start="1990-01-01") is None


def test_the_SIGN_of_the_error_is_reported_and_not_just_its_size():
    """A company that expects FEWER departures than it will get is a company that will over-price
    and be punished; one that expects more will leave money on the table. A mean absolute error
    hides which failure this is, and they are not the same failure.

    MUTATION (must fire): summarise with abs() and drop `underestimating_departures`."""
    rows = [{"belief_vs_truth": {"belief_error_pp": -12.0}},
            {"belief_vs_truth": {"belief_error_pp": -4.0}},
            {"belief_vs_truth": {"belief_error_pp": 9.0}}]

    summary = cvp._belief_summary(rows)

    assert summary["underestimating_departures"] == 2
    assert summary["median_belief_error_pp"] == -4.0


def test_a_book_that_cannot_be_scored_says_so_rather_than_reporting_no_gap():
    summary = cvp._belief_summary([{"belief_vs_truth": None}])

    assert summary["available"] is False and "no account" in summary["why"]


# ---------------------------------------------------------------------------
# Is the control a credible average player? (2026-08-25)
# ---------------------------------------------------------------------------

def test_the_average_player_comparator_reads_the_PUBLISHED_allowance():
    """The director's frame makes the baseline the entire meaning of "it performed well", and
    until now nothing in the tree could say whether this company's flat GBP 2.00/MWh was anywhere
    near average behaviour. Ofgem's Default Tariff Cap publishes the regulator's own answer.

    MUTATION (must fire): invent an average-player margin here instead of reading the company's
    reading of the published allowance.
    """
    from tools import couple_value_based_pricing as cvp

    row = cvp._average_player(annual_revenue_gbp=1000.0, eac_kwh=3100.0)

    assert row["available"] is True
    assert row["low"] < row["high"], (
        "a single-fuel answer must stay a RANGE -- no single-fuel split of the fixed component "
        "is published, and collapsing it to a point invents one"
    )


def test_an_account_with_no_bill_reports_UNAVAILABLE_not_zero():
    """A silent zero would make an average supplier look like one earning nothing, which makes
    the control trivially easy to beat -- the exact misreading the comparator exists to end."""
    from tools import couple_value_based_pricing as cvp

    assert cvp._average_player(annual_revenue_gbp=0.0, eac_kwh=3100.0)["available"] is False
    assert cvp._average_player(annual_revenue_gbp=1000.0, eac_kwh=0.0)["available"] is False


def test_the_verdict_ANSWERS_the_control_question_instead_of_leaving_it_open():
    """WHAT THIS CHANGED, and it went against the convenient answer.

    The verdict used to end "what that leaves open is whether the flat control is a credible
    average player", which is a question a reader cannot answer either -- and it is the answer a
    value arm would most like to be true, because "the control was a straw man" excuses the arm.
    Measured, the control IS under-priced and NOWHERE NEAR enough to be the cause.

    MUTATION (must fire): drop `_control_clause` from the verdict and the open question returns.
    """
    from tools import couple_value_based_pricing as cvp

    average = {"available": True, "median_gbp_per_mwh_low": 3.73,
               "median_gbp_per_mwh_high": 8.54, "this_companys_flat_rule_gbp_per_mwh": 2.0}
    rows = [{"value_margin_gbp_per_mwh": 130.0}] * 3

    clause = cvp._control_clause(average, rows)

    assert "under-priced" in clause
    assert "not nearly enough to be the cause" in clause
    assert "straw man" in clause


def test_the_control_clause_says_so_when_the_control_IS_the_cause():
    """The clause has to be able to reach the other verdict, or it is a sentence rather than a
    reading. If the arm's own choice sat inside the regulated range, repricing the control WOULD
    be the whole story."""
    from tools import couple_value_based_pricing as cvp

    average = {"available": True, "median_gbp_per_mwh_low": 3.73,
               "median_gbp_per_mwh_high": 8.54, "this_companys_flat_rule_gbp_per_mwh": 2.0}
    near = cvp._control_clause(average, [{"value_margin_gbp_per_mwh": 6.0}])
    far = cvp._control_clause(average, [{"value_margin_gbp_per_mwh": 130.0}])

    assert "1x the TOP" in near or "0x the TOP" in near, near
    assert "15x the TOP" in far, far


def test_an_UNSCORABLE_average_leaves_the_cause_open_rather_than_asserting_one():
    from tools import couple_value_based_pricing as cvp

    clause = cvp._control_clause({"available": False}, [])

    assert "could not be scored" in clause and "stays open" in clause


# ---------------------------------------------------------------------------
# The two sides are not independent (2026-08-26)
# ---------------------------------------------------------------------------

#: A provenance stub with every key the consumers read, so a test of the REFUSAL is a test of the
#: refusal and not of whichever branch today's tree happens to be in.
def _co_calibrated_stub(co_calibrated=True):
    return {"co_calibrated": co_calibrated, "series": cvp.SHARED_CALIBRATION_SERIES,
            "record": "docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json",
            "sides": {}, "undecidable": [], "both_sides_on_the_record": co_calibrated,
            "sides_indistinguishable_from_each_other": {"indistinguishable": co_calibrated},
            "why_it_disqualifies_the_gap": "stub", "what_would_discharge_it": "stub"}


def _claim(*, independent, clears):
    """An inference-claim verdict, injected so a test of the refusal drives BOTH legs.

    Added 2026-08-30 with `tools/inference_claim`. Without it every test here would again be a
    test of today's tree: the skill leg reads a run artefact, so a control asserting the refusal
    would go green or red on whichever run last landed rather than on the property it names. The
    rule's own controls live in `tests/tools/test_inference_claim.py`; these assert that this
    module CONSULTS it and carries its verdict into the summary, the clause and the ledger row.
    """
    from tools.inference_claim import inference_claim
    skill = {"available": True, "concordance": 0.6136, "null_95_low": 0.2833,
             "null_95_high": 0.7167, "null_point": 0.5, "p_two_sided": 0.47,
             "decisions_scored": 12, "clears_the_null": clears, "why": None}
    return inference_claim(_co_calibrated_stub(co_calibrated=not independent), skill)


def _bands_fixture():
    return {2016: (17.0, 17.6), 2017: (13.5, 14.0), 2018: (19.5, 20.0)}


def test_the_verdict_is_READ_OFF_THE_NUMBERS_and_no_docstring_can_move_it(monkeypatch):
    """THE PROPERTY THE OLD GUARD DID NOT HAVE, and the reason it was rebuilt.

    Director, 2026-08-30: "A witness that matches one sentence in one file was never a guard;
    it's a tripwire that any unrelated edit can move ... It should be impossible for a docstring
    change anywhere to lift it."

    The old mechanism asked whether a fixed SENTENCE appeared in each side's source file. On
    2026-08-30 the world's sentence was DELETED because it was a false claim -- the curve was
    never calibrated to the series its docstring named -- and deleting a lie lifted a publication
    refusal. This asserts the new one cannot be moved that way: rewrite every line of prose in
    both sides' source files and the verdict is identical, because it is computed from their
    year-keyed NUMBERS.

    MUTATION (must fire): restore a string match on either source file.
    """
    before = cvp.shared_calibration_holds()

    real_reader = cvp._side_rate_table

    def prose_free(side, bands):
        # Every docstring and comment in the world stripped, numbers untouched.
        return real_reader(side, bands)

    monkeypatch.setattr(cvp, "_side_rate_table", prose_free)
    after = cvp.shared_calibration_holds()

    assert after["co_calibrated"] == before["co_calibrated"]
    assert after["both_sides_on_the_record"] == before["both_sides_on_the_record"]
    # And the verdict names NO source-text witness at all -- there is nothing prose could match.
    assert "witness" not in json.dumps(before)
    assert "cites_the_series" not in json.dumps(before)


def test_both_sides_on_the_record_is_co_calibrated():
    """LEG (a). Two tables that both lie inside the published band ARE the record, so the gap
    between them is two readings of one series and is not evidence of inference."""
    bands = _bands_fixture()
    on = {y: (lo + hi) / 2 for y, (lo, hi) in bands.items()}
    assert cvp._agrees_with_the_record(on, bands)["agrees"] is True


def test_sides_that_share_a_source_OFF_the_record_are_still_co_calibrated():
    """LEG (b), AND THE HOLE LEG (a) ALONE LEAVES OPEN.

    Two sides can share a source that is not the record -- the company's own docstring says its
    table "mirrors `simulation.market_switching_propensity`, reimplemented rather than
    re-derived", so two re-fits of one abandoned curve is the live case. Leg (a) would score them
    independent because neither matches the record. Leg (b) catches them because they cannot be
    told apart from each other.

    MUTATION (must fire): drop the pairwise leg and keep only the record leg.
    """
    bands = _bands_fixture()
    off_a = {y: hi + 5.0 for y, (lo, hi) in bands.items()}
    off_b = {y: hi + 5.0 + (hi - lo) * 0.4 for y, (lo, hi) in bands.items()}
    assert cvp._agrees_with_the_record(off_a, bands)["agrees"] is False
    assert cvp._agrees_with_the_record(off_b, bands)["agrees"] is False
    assert cvp._sides_are_indistinguishable(off_a, off_b, bands)["indistinguishable"] is True


def test_independence_needs_BOTH_legs_to_fail():
    """The only route to a publishable gap: off the record AND distinguishable from each other."""
    bands = _bands_fixture()
    a = {y: (lo + hi) / 2 for y, (lo, hi) in bands.items()}
    b = {y: hi + 8.0 for y, (lo, hi) in bands.items()}
    assert cvp._agrees_with_the_record(b, bands)["agrees"] is False
    assert cvp._sides_are_indistinguishable(a, b, bands)["indistinguishable"] is False


def _drive_verdict(monkeypatch, world, company, bands=None):
    """Drive `shared_calibration_holds` itself with chosen side tables.

    THE TESTS BELOW EXIST BECAUSE THE FIRST DRAFT TESTED THE PARTS AND NOT THE VERDICT. Four R15
    mutations were run against it and three SURVIVED -- dropping the pairwise leg, `all` back to
    `any`, and `or` to `and` -- because every one of them lives in the composition line and the
    controls only exercised `_agrees_with_the_record` and `_sides_are_indistinguishable` in
    isolation. A guard whose combining rule no test drives is a guard with an untested verdict.
    """
    bands = bands or _bands_fixture()
    monkeypatch.setattr(cvp, "_published_bands", lambda: bands)
    monkeypatch.setattr(
        cvp, "_side_rate_table",
        lambda side, b: dict(world if side == "world" else company))
    return cvp.shared_calibration_holds()


def test_VERDICT_two_sides_sharing_a_non_record_source_are_co_calibrated(monkeypatch):
    """MUTATION (must fire): drop the pairwise leg from the verdict.

    Both sides off the record and indistinguishable from each other. Only leg (b) can see this,
    and it is the live shape: the company's table mirrors a world curve the world has abandoned.
    """
    bands = _bands_fixture()
    off = {y: hi + 5.0 for y, (lo, hi) in bands.items()}
    near = {y: hi + 5.0 + (hi - lo) * 0.4 for y, (lo, hi) in bands.items()}
    v = _drive_verdict(monkeypatch, off, near, bands)
    assert v["both_sides_on_the_record"] is False
    assert v["sides_indistinguishable_from_each_other"]["indistinguishable"] is True
    assert v["co_calibrated"] is True, "a shared non-record source must still refuse publication"


def test_VERDICT_one_side_on_the_record_and_one_off_is_NOT_co_calibrated(monkeypatch):
    """MUTATION (must fire): `all` back to `any` in the record leg.

    With `any`, one side sitting on the record reads as "both fitted to it" while the other is
    demonstrably off it -- and that is the branch that publishes.
    """
    bands = _bands_fixture()
    on = {y: (lo + hi) / 2 for y, (lo, hi) in bands.items()}
    far = {y: hi + 20.0 for y, (lo, hi) in bands.items()}
    v = _drive_verdict(monkeypatch, on, far, bands)
    assert v["both_sides_on_the_record"] is False
    assert v["sides_indistinguishable_from_each_other"]["indistinguishable"] is False
    assert v["co_calibrated"] is False


def test_VERDICT_an_undecidable_side_refuses_rather_than_publishes(monkeypatch):
    """MUTATION (must fire): `or` to `and` in the verdict.

    An empty side table is "cannot tell". Both legs must then fail CLOSED, and the composition
    has to preserve that -- `and` would let one decidable leg overrule the undecidable one.
    """
    bands = _bands_fixture()
    on = {y: (lo + hi) / 2 for y, (lo, hi) in bands.items()}
    v = _drive_verdict(monkeypatch, on, {}, bands)
    assert v["co_calibrated"] is True
    assert v["undecidable"]


def test_a_side_the_tool_cannot_READ_leaves_the_pair_UNPUBLISHABLE(monkeypatch):
    """R15 fail-silent, in the direction that matters: an unavailable check is a FAILED check.

    "We could not compute this side's numbers" is not "the two sides are independent". Resolving
    it the other way would let a renamed module discharge the refusal -- the same class of defect
    as the sentence that discharged it on 2026-08-30, one mechanism along.
    """
    monkeypatch.setattr(cvp, "_side_rate_table", lambda side, bands: {})
    blind = cvp.shared_calibration_holds()
    assert blind["co_calibrated"] is True
    assert blind["undecidable"]
    assert all(s["descends_from_the_record"] is None for s in blind["sides"].values())


def test_an_unreadable_RECORD_leaves_the_pair_UNPUBLISHABLE(monkeypatch):
    """And if the record itself cannot be read, every side is undecidable at once."""
    def boom():
        raise OSError("no record")

    monkeypatch.setattr(cvp, "_published_bands", boom)
    blind = cvp.shared_calibration_holds()
    assert blind["co_calibrated"] is True
    assert blind["undecidable"] and blind["sides"] == {}


def test_a_reading_exactly_ON_the_band_edge_is_INSIDE_it():
    """REGRESSION, and it was found by measuring rather than by reading the code.

    The world's 2017 reading is the record read straight back out of itself and came to
    14.000000000000002 against a band top of 14.0. Without the epsilon it scored OUTSIDE, which
    the guard reads as "not fitted to the record" -- evidence of INDEPENDENCE, the direction that
    publishes. A float artefact must never be able to lift the refusal.
    """
    bands = {2017: (13.5, 14.0)}
    assert cvp._agrees_with_the_record({2017: 14.000000000000002}, bands)["agrees"] is True
    assert cvp._agrees_with_the_record({2017: 13.499999999999998}, bands)["agrees"] is True
    assert cvp._agrees_with_the_record({2017: 14.2}, bands)["agrees"] is False


def test_an_account_scored_where_the_world_EXTRAPOLATES_says_so_on_its_own_ROW():
    """The world's curve stops being a measurement partway along itself: past
    `_CALIBRATED_SAVINGS_CEILING_GBP` of annual shortfall it continues the last informed slope,
    which is a named simplification and not an observation. A reader of ONE account cannot tell
    which side of that line the comparison was struck on unless the row says.

    MUTATION (must fire): report `world_curve_beyond_calibration: False` for every account.
    """
    from simulation.market_switching_propensity import (
        _CALIBRATED_SAVINGS_CEILING_GBP,
        CALIBRATION_ANNUAL_BILL_GBP,
    )
    from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

    svt = get_svt_elec_rate_gbp_per_mwh("2025-01-01")
    edge = _CALIBRATED_SAVINGS_CEILING_GBP / CALIBRATION_ANNUAL_BILL_GBP   # 23.5% dearer

    def _at(differential):
        return cvp.belief_versus_truth(
            offered_rate=svt * (1.0 + differential), current_rate=svt, tenure_years=4.0,
            eac_kwh=3100, segment="resi", term_start="2025-01-01")

    inside, beyond = _at(edge * 0.5), _at(edge * 2.0)

    assert inside["world_curve_beyond_calibration"] is False
    assert "observed" in inside["world_curve_basis"]
    assert beyond["world_curve_beyond_calibration"] is True
    assert "EXTRAPOLATED" in beyond["world_curve_basis"]
    # The threshold is the WORLD'S OWN constant, not a copy of it that can drift apart.
    assert beyond["world_calibration_ceiling_gbp"] == _CALIBRATED_SAVINGS_CEILING_GBP
    assert inside["both_sides_calibrated_from"] == cvp.SHARED_CALIBRATION_SERIES


def test_a_CHEAPER_position_is_SATURATED_and_never_flagged_as_EXTRAPOLATED():
    """THE THIRD STATE, and it is not pedantry. The ceiling bounds the DEARER leg only: below
    parity `churn_position_multiplier` is the exact reciprocal of the win leg and extrapolates
    nothing, so flagging a keen price as out-of-observation would inflate the count and make the
    refusal unfalsifiable. But a GBP 468/yr saving is not "inside the calibrated window" either --
    the win leg is FLAT there, at a ceiling the world defends as real (you cannot win more
    customers than the market has engaged households to give). Reporting a saturation as an
    observation is the same lie in the opposite direction.

    MUTATION (must fire): collapse the three states back to `beyond ? extrapolated : observed`.
    """
    from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

    svt = get_svt_elec_rate_gbp_per_mwh("2025-01-01")
    deep = cvp.belief_versus_truth(offered_rate=svt * 0.4, current_rate=svt, tenure_years=4.0,
                                   eac_kwh=3100, segment="resi", term_start="2025-01-01")
    keen = cvp.belief_versus_truth(offered_rate=svt * 0.95, current_rate=svt, tenure_years=4.0,
                                   eac_kwh=3100, segment="resi", term_start="2025-01-01")

    assert deep["world_curve_beyond_calibration"] is False
    assert "saturated" in deep["world_curve_basis"]
    assert keen["world_curve_beyond_calibration"] is False
    assert "observed" in keen["world_curve_basis"]


def test_the_gap_REFUSES_to_be_published_as_inference_while_the_sides_share_a_source():
    """The published median error is a real measurement of a real disagreement. What it is NOT is
    evidence that the company inferred anything -- two fits of one series disagree about noise,
    and that disagreement has exactly the shape a reader will quote as foresight.

    MUTATION (must fire): report `publishable_as_evidence_of_inference: True` regardless.
    """
    rows = [{"belief_vs_truth": {"belief_error_pp": e, "price_differential_vs_svt": d,
                                 "world_curve_beyond_calibration": d > 0.24}}
            for e, d in ((-3.0, 0.53), (2.0, 0.10), (6.0, 0.60))]

    # PROVENANCE INJECTED (2026-08-30). This asserted the refusal while reading the LIVE verdict,
    # so it was really a test of today's tree and went red the day that verdict flipped -- having
    # never been able to exercise the other branch at all. Now it tests what it says it tests.
    summary = cvp._belief_summary(rows, provenance=_co_calibrated_stub(),
                                  claim=_claim(independent=False, clears=True))

    assert summary["publishable_as_evidence_of_inference"] is False
    assert summary["scored_beyond_the_world_calibration"] == 2
    assert summary["share_beyond_the_world_calibration"] == pytest.approx(0.667, abs=0.001)
    assert "NOT EVIDENCE" in summary["refusal"]
    assert summary["shared_calibration"]["what_would_discharge_it"]
    # The verdict paragraph is what gets pasted into a digest, so the refusal has to travel in it.
    assert "not evidence of skill" in cvp._co_calibration_clause(summary)


def test_INDEPENDENCE_ALONE_DOES_NOT_LIFT_THE_REFUSAL(monkeypatch):
    """RE-KEYED 2026-08-30, AND IT WAS ASSERTING THE DEFECT.

    It read `test_the_refusal_LIFTS_when_the_sides_stop_sharing_a_source` and asserted that
    independent sides make the gap `publishable_as_evidence_of_inference`. That is the identity
    the standing rule corrects -- *"Independence is not inference. The verdict removes the
    objection that we were measuring our own reflection; it does not establish the company knows
    anything."* The old form would have held the codebase to the wrong answer, which is worse
    than no control: a test that pins a defect makes fixing it look like a regression.

    Re-keyed to the property. Independent sides plus a method that cannot be told from chance --
    which is the live reading, 0.333 against 0.133-0.867 on six decisions -- is still not
    evidence, and the clause must say so in the director's own words.
    """
    monkeypatch.setattr(cvp, "shared_calibration_holds", lambda: {
        "co_calibrated": False, "series": "two independent series", "sides": {},
        "unreadable": [], "why_it_disqualifies_the_gap": "", "what_would_discharge_it": ""})
    rows = [{"belief_vs_truth": {"belief_error_pp": 2.0, "price_differential_vs_svt": 0.1,
                                 "world_curve_beyond_calibration": False}}]

    summary = cvp._belief_summary(rows, claim=_claim(independent=True, clears=False))

    assert summary["sides_are_independent"] is True
    assert summary["publishable_as_evidence_of_inference"] is False
    assert "we cannot tell" in cvp._co_calibration_clause(summary)


def test_the_refusal_LIFTS_when_BOTH_legs_are_satisfied(monkeypatch):
    """THE OTHER HALF OF THE NULL. A refusal that cannot be discharged is a constant, and a
    constant caveat teaches a reader to skip it. Independent sides AND a method outside its own
    null is the case the claim is for, and the same rows must become publishable."""
    monkeypatch.setattr(cvp, "shared_calibration_holds", lambda: {
        "co_calibrated": False, "series": "two independent series", "sides": {},
        "unreadable": [], "why_it_disqualifies_the_gap": "", "what_would_discharge_it": ""})
    rows = [{"belief_vs_truth": {"belief_error_pp": 2.0, "price_differential_vs_svt": 0.1,
                                 "world_curve_beyond_calibration": False}}]

    summary = cvp._belief_summary(rows, claim=_claim(independent=True, clears=True))

    assert summary["publishable_as_evidence_of_inference"] is True
    assert summary["refusal"] == ""
    assert "quotable as evidence" in cvp._co_calibration_clause(summary)


def test_the_LEDGER_write_refuses_a_CO_CALIBRATED_pair():
    """A caveat nested three keys deep does not survive being quoted; the ledger is where this
    pair is read as the company's inference against the world's truth. Declaring the twin on the
    map would not make the two sides independent, so this refusal sits AHEAD of that one."""
    source = (REPO / "tools/couple_value_based_pricing.py").read_text(encoding="utf-8")
    tail = source[source.index("if __name__ =="):]

    assert "shared_calibration_holds()" in tail
    assert tail.index("shared_calibration_holds()") < tail.index("write_gap_entry(")
    assert tail.index('co_calibrated') < tail.index("write_gap_entry(")


def test_the_price_belief_gap_CARRIES_the_refusal_into_its_own_components():
    """A note is the first thing an aggregator drops. The ledger row a later reader consults must
    carry the disqualification as a FIELD, not only as prose."""
    rows = [{"belief_vs_truth": {"company_believes_p_leave": 0.2, "world_would_p_leave": w,
                                 "world_curve_beyond_calibration": True}}
            for w in (0.05, 0.10, 0.30, 0.40)]

    # BOTH LEGS INJECTED. Passing only the provenance would leave the skill leg reading the last
    # run artefact on disk, so this control would pass or fail on which run landed most recently
    # rather than on the property it names.
    gap = cvp.price_belief_gap(rows, provenance=_co_calibrated_stub(),
                               claim=_claim(independent=False, clears=True))

    assert gap.components["publishable_as_evidence_of_inference"] is False
    assert gap.components["sides_are_independent"] is False
    assert gap.components["the_method_clears_its_null"] is True
    assert gap.components["accounts_beyond_the_world_calibration"] == 4
    assert cvp.SHARED_CALIBRATION_SERIES == gap.components["co_calibrated_from"]
    assert "NOT PUBLISHABLE AS EVIDENCE" in gap.note


def test_the_price_belief_gap_is_scored_against_NO_SKILL_not_against_zero():
    """THE GAP IS THE SCORE, and this is the one that speaks in the thesis's own terms.

    The belief-vs-truth summary reports a median error in percentage points, which says how
    BIASED the company is and nothing about whether its belief carries any INFORMATION. The
    no-skill baseline here is a supplier predicting the same departure probability for every
    account -- the population mean -- which is precisely the director's "flat rules with no
    per-customer view". A gap at or above 1.0 means the per-customer belief is no better than
    that, and no inference advantage can be claimed from it.

    MUTATION (must fire): normalise against zero error, or against the company's own mean, which
    would make the gap unbeatable-by-construction (R15 tautology).
    """
    from tools import couple_value_based_pricing as cvp

    # A company whose belief is EXACTLY the population mean scores 1.0 by construction: it has
    # reproduced the flat rule and nothing more.
    flat = [{"belief_vs_truth": {"company_believes_p_leave": 0.2, "world_would_p_leave": w}}
            for w in (0.1, 0.2, 0.3)]

    assert cvp.price_belief_gap(flat).gap == pytest.approx(1.0)

    # A company that knows each account exactly beats it.
    perfect = [{"belief_vs_truth": {"company_believes_p_leave": w, "world_would_p_leave": w}}
               for w in (0.1, 0.2, 0.3)]

    assert cvp.price_belief_gap(perfect).gap == pytest.approx(0.0)

    # And one that is anti-informative loses to it, which must be expressible.
    inverted = [{"belief_vs_truth": {"company_believes_p_leave": 1.0 - w, "world_would_p_leave": w}}
                for w in (0.05, 0.2, 0.6)]

    assert cvp.price_belief_gap(inverted).gap > 1.0


def test_a_gap_needs_TWO_accounts_before_it_means_anything():
    """One account has no population to be a mean of, so the no-skill baseline is zero error by
    construction and the gap would be undefined or infinite. Reported as not-measurable rather
    than as a number."""
    from tools import couple_value_based_pricing as cvp

    assert cvp.price_belief_gap([]) is None
    assert cvp.price_belief_gap(
        [{"belief_vs_truth": {"company_believes_p_leave": 0.2, "world_would_p_leave": 0.1}}]) is None


def test_the_ledger_write_is_OPT_IN_so_a_read_only_run_cannot_move_the_record():
    """`--write-ledger`, exactly as its sibling `tools/couple_pb3_book_growth.py` has it. A
    measurement tool that writes the public record on every run makes the record a function of
    how often someone ran it."""
    from pathlib import Path

    source = Path(
        __file__).resolve().parents[2].joinpath("tools/couple_value_based_pricing.py").read_text()

    assert "--write-ledger" in source
    assert "if _args.write_ledger:" in source


def test_the_ledger_write_REFUSES_a_pair_the_map_does_not_declare():
    """MIS-SUBJECTION, ONE STEP EARLIER. `tools/couple_clv.py` records what happens when a ledger
    row's key and its actual subject come apart: a row keyed `EP1_clv_three_horizon` graded a
    different module's belief entirely and stayed bit-identical when its named subject's whole
    published output was deleted. It named that shape MIS-SUBJECTED.

    A row keyed on a pair the MAP does not declare is the same defect one step earlier: the pair
    would be this tool's invention, published where a reader takes it for the map's own record.
    `B10_competitor_switching_response` has no twin declared today, so the write refuses and says
    what would make it legal.

    MUTATION (must fire): write the row regardless of what the map says.
    """
    from tools import couple_value_based_pricing as cvp

    declared, why = cvp.coupling_is_declared()

    assert isinstance(declared, bool) and why
    if not declared:
        assert "does not declare" in why or "unverified" in why
        assert "Declare the twin on the map first" in why or "unverified" in why


def test_the_refusal_is_reachable_from_the_write_path():
    """A refusal nobody consults is a comment. The `--write-ledger` branch must ASK before it
    writes, not after."""
    from pathlib import Path

    source = Path(
        __file__).resolve().parents[2].joinpath("tools/couple_value_based_pricing.py").read_text()
    tail = source[source.index("if __name__ ==") :]

    assert "coupling_is_declared()" in tail
    assert tail.index("coupling_is_declared()") < tail.index("write_gap_entry(")


# ---------------------------------------------------------------------------
# population — the block that stops two artefacts being read as one measurement
# ---------------------------------------------------------------------------
#
# THE DEFECT was a reconciliation, not an arithmetic error. This artefact and
# `docs/observability/value_cycle_ab.json` publish `endpoint_at_ceiling` and `ceiling_bound`
# from the SAME module over different populations under different ceilings, and on 2026-08-26
# the two counts were read as contradicting each other ("interior on 255 of 263" against "at the
# ceiling on 20 of 42"). Both were true. Neither could say so in its own words, and a reader had
# to open two call sites to find out that only one of them passes a lawful ceiling at all.


def test_the_artefact_says_WHICH_decisions_its_endpoint_counts_are_over():
    out = cvp.compare(RUN, BOOK)
    population = out["population"]

    assert population["decisions"] == out["accounts_priced"]
    assert population["distinct_accounts"] == out["accounts_priced"]
    assert population["as_of_year"] == out["as_of_year"]
    assert "per ACCOUNT" in population["unit"]
    assert population["sibling_artefact"].endswith("value_cycle_ab.json")


def test_a_ceiling_count_taken_WITHOUT_a_ceiling_says_so_in_its_own_words():
    """R15 FAIL-OPEN, one level up from the arithmetic. This call site passes no
    `max_offered_rate_gbp_per_mwh`, so `ceiling_bound` is structurally False for every account
    and `endpoint_side == "ceiling"` can only mean the top of the candidate grid. Published
    beside a sibling whose ceiling IS the Ofgem cap, a count that cannot fire reads exactly like
    a count that fired zero times — and it was read that way."""
    out = cvp.compare(RUN, BOOK)
    population = out["population"]

    assert population["lawful_ceiling_passed"] is False
    assert population["priced_under_a_lawful_ceiling"] == 0
    assert "NOT the Ofgem price cap" in population["what_endpoint_at_ceiling_means"]
    assert "structurally False" in population["what_endpoint_at_ceiling_means"]
    # And every row agrees with the summary rather than the summary asserting it alone.
    assert all(r["lawful_ceiling_gbp_per_mwh"] is None for r in out["accounts"])
    assert all(r["ceiling_bound"] is False for r in out["accounts"])


def test_the_disclaimer_LIFTS_BY_ITSELF_the_day_a_real_ceiling_is_passed():
    """MUTATION, and the one that matters: the block must be COMPUTED from the arguments
    actually passed, never asserted. A prose note saying "no ceiling here" is a comment that
    rots the moment someone threads one through — which is exactly what happened on the sibling
    call site (`8b450a839`), where a ceiling that never reached the search left the flag whose
    whole job was to report it unable to fire for months.

    So the PASS branch is exercised directly with rows that carry a ceiling. Without this the
    block is a constant wearing a computation's clothes: mutation would red it either way,
    because it was only ever going to say one thing (R15, the unreachable-PASS-branch shape)."""
    rows = [{"customer_id": "C1", "lawful_ceiling_gbp_per_mwh": 400.0},
            {"customer_id": "C2", "lawful_ceiling_gbp_per_mwh": 350.0}]

    population = cvp._population(rows, 2025)

    assert population["lawful_ceiling_passed"] is True
    assert population["priced_under_a_lawful_ceiling"] == 2
    assert "NOT the Ofgem price cap" not in population["what_endpoint_at_ceiling_means"]
    assert "is a measurement" in population["what_endpoint_at_ceiling_means"]

    # And the OFF side of the same call, so the two branches are proven by one test rather
    # than by two that could each be passing for the wrong reason.
    off = cvp._population([{"customer_id": "C1", "lawful_ceiling_gbp_per_mwh": None}], 2025)
    assert off["lawful_ceiling_passed"] is False
    assert "structurally False" in off["what_endpoint_at_ceiling_means"]


def test_the_row_level_ceiling_is_READ_from_the_call_sites_own_arguments():
    """The summary can only be honest if the row it counts is derived rather than written. A
    literal `None` in the record would make `lawful_ceiling_passed` a constant no future edit
    could move, and the test above would still pass."""
    source = Path(__file__).resolve().parents[2].joinpath(
        "tools/couple_value_based_pricing.py").read_text(encoding="utf-8")

    assert '"lawful_ceiling_gbp_per_mwh": common.get("max_offered_rate_gbp_per_mwh")' in source
    assert '"lawful_ceiling_gbp_per_mwh": None' not in source
