"""R4's product ceiling — and every control names the defect it exists to catch.

A49's requirement is the CEILING-or-FLOOR verdict per product, so the controls are over exactly
that: the verdicts must follow the CENSUS rather than a hard-coded opinion, the refusals to sum and
to invent must bite, and the arms that hold no data must return `None` rather than a zero.

NOTHING HERE READS A RUN OUTPUT FOR ITS ASSERTIONS. Run outputs are gitignored, so in a linked
worktree they are absent and a suite that depends on them passes VACUOUSLY. Every figure asserted
below is built in the test.
"""
from __future__ import annotations

import json

import pytest

from tools import r4_product_ceiling as r4
from tools.r3_carbon_score_ceiling import CeilingUnavailable


def _events(rows):
    return {"customer_events": rows}


def _pair(cid, rate, reference):
    return {"customer_id": cid, "unit_rate_gbp_per_mwh": rate,
            "market_reference_gbp_per_mwh": reference}


class TestTheTariffFitBoundIsAGapAndNotATrend:
    """DEFECT, and it is the one this instrument was actually caught by. The first draft collected
    rates from every log and references from the one log that carries them, then differenced the
    per-household MEANS. It returned £88.21 per household-year against a true £2.19 -- a 40x
    artefact, because the rate was averaged over every priced term and the reference only over
    renewal occasions, and GB prices move by a factor of three across 2016-2025. Differencing two
    averages taken over different windows is a price TREND wearing a price gap's name."""

    def test_a_rate_and_a_reference_on_DIFFERENT_rows_are_not_compared(self):
        payload = {
            "pricing": [{"customer_id": "C1", "unit_rate_gbp_per_mwh": 300.0}],
            "events": [{"customer_id": "C1", "market_reference_gbp_per_mwh": 100.0}],
        }
        assert r4.rate_against_reference(payload) == {}, (
            "a rate from one occasion and a reference from another are not a gap"
        )

    def test_a_rate_and_a_reference_on_the_SAME_row_ARE_compared(self):
        """The other leg. A reader that pairs nothing is as broken as one that pairs everything,
        and only both legs tell them apart."""
        got = r4.rate_against_reference(_events([_pair("C1", 150.0, 100.0)]))
        assert got["C1"]["rate_gbp_per_mwh"] == 150.0
        assert got["C1"]["reference_gbp_per_mwh"] == 100.0
        assert got["C1"]["occasions"] == 1

    def test_only_the_POSITIVE_side_counts(self):
        """DEFECT: netting a household already below the reference against one above it.

        A perfect method leaves the cheaper household alone; it does not harvest negative value
        from it. Summing signed gaps would understate the ceiling, which is the wrong direction
        for a bound.
        """
        # One household above the reference, 24 below it. Netting the signed gaps would drive the
        # ceiling negative; taking only the positive side leaves the one household's real headroom.
        rows = [_pair("C0", 150.0, 100.0)] + [_pair(f"C{i}", 50.0, 100.0) for i in range(1, 25)]
        eac = {f"C{i}": 1000.0 for i in range(25)}
        arm = r4.tariff_fit_ceiling(_events(rows), eac)
        assert arm["bound_kind"] == r4.CEILING, "the fixture is too thin to exercise the arm"
        assert arm["households_above_the_reference"] == 1
        assert arm["book_gbp_per_year"] == pytest.approx(50.0), (
            "£50/MWh over 1 MWh, from the one household above the reference and nowhere else"
        )
        assert arm["gbp_per_household_year"] > 0, "the households below the reference cancelled it"

    def test_the_arithmetic_is_the_gap_times_the_consumption(self):
        rows = [_pair(f"C{i}", 150.0, 100.0) for i in range(30)]
        eac = {f"C{i}": 2000.0 for i in range(30)}
        arm = r4.tariff_fit_ceiling(_events(rows), eac)
        # £50/MWh over 2 MWh = £100 for every household.
        assert arm["gbp_per_household_year"] == pytest.approx(100.0)


class TestTariffFitAbatesNothingByRule:
    """DEFECT: discounting counted as abatement — item 8 of the carbon scope brief's
    disqualification battery, and the canon's own charge that the company 'can make a household
    cheaper and never greener'."""

    def test_the_carbon_column_is_ZERO_and_says_it_is_by_RULE(self):
        rows = [_pair(f"C{i}", 150.0, 100.0) for i in range(30)]
        arm = r4.tariff_fit_ceiling(_events(rows), {f"C{i}": 2000.0 for i in range(30)})
        assert arm["kg_co2e_per_household_year"] == 0.0
        assert "not by measurement" in arm["carbon_is_zero_by_rule"], (
            "a zero that does not say it is a rule reads as a measurement that found nothing"
        )


class TestTheVerdictsFollowTheCensus:
    """DEFECT: a control pinned to today's answer. If the world starts writing a fabric parameter,
    the measure arms must stop being FLOORS on their own -- a verdict hard-coded here would stay
    red-hot wrong and green."""

    def test_the_census_FINDS_a_property_attribute_when_one_is_present(self):
        payload = {"homes": [{"customer_id": "C1", "loft_insulation_mm": 100}]}
        got = r4.property_attribute_census(payload)
        assert got["attributes_found"] == {"homes.loft_insulation_mm": 1}

    def test_the_census_finds_NOTHING_when_there_is_nothing(self):
        """Both legs of the partition. A census that reports a hit for every book is as useless
        as one that reports none."""
        got = r4.property_attribute_census(_events([_pair("C1", 150.0, 100.0)]))
        assert got["attributes_found"] == {} and got["logs_scanned"] == 1

    def test_a_measure_arm_is_a_FLOOR_and_says_a_negative_RETIRES_NOTHING(self):
        census = {"logs_scanned": 29, "attributes_found": {}}
        arm = r4.measure_arm("solar", census, {"available": False})
        assert arm["bound_kind"] == r4.FLOOR
        assert "RETIRE NOTHING" in arm["why_a_floor_and_not_a_ceiling"], (
            "the whole point of the floor verdict is what it licenses, and it must be stated"
        )
        assert arm["missing_data"], "a floor without its missing datum is a shrug, not a finding"

    def test_a_measure_arm_returns_None_and_NEVER_a_zero(self):
        """DEFECT: an honest gap published as 0.0. A zero will be read as established -- 'solar is
        worth nothing' -- and a `None` cannot be."""
        arm = r4.measure_arm("heat_pump", {"logs_scanned": 1, "attributes_found": {}}, {})
        assert arm["gbp_per_household_year"] is None
        assert arm["kg_co2e_per_household_year"] is None

    def test_every_measure_product_names_what_it_is_MISSING(self):
        for product in ("efficiency_fabric", "solar", "heat_pump"):
            assert product in r4.MISSING_FOR and len(r4.MISSING_FOR[product]) > 20


class TestItRefusesToTotalAndToDoubleCount:
    """DEFECT: a sum across non-disjoint products in two currencies. It is the number a reader
    would quote and it is not a quantity."""

    def test_advice_is_NOT_ADDITIVE_and_the_payload_says_so(self):
        arms = {"time_shifting": {"bound_kind": r4.CEILING},
                "tariff_fit": {"bound_kind": r4.CEILING}}
        arm = r4.advice_arm(arms)
        assert arm["not_additive"] is True
        assert arm["gbp_per_household_year"] is None, (
            "advice with its own pounds beside the arms it delivers counts them twice"
        )
        assert set(arm["delivers"]) == {"time_shifting", "tariff_fit"}

    def test_advice_delivers_NOTHING_when_no_arm_is_bounded(self):
        """The other leg: a channel with nothing to carry is unbounded, not a ceiling."""
        arm = r4.advice_arm({"time_shifting": {"bound_kind": r4.FLOOR}})
        assert arm["bound_kind"] == r4.UNBOUNDED and arm["delivers"] == []


class TestTimeShiftingIsReadAndNotRecomputed:
    """DEFECT: two implementations of one quantity, which is how a figure comes to have two values
    and no owner. This repository has paid for that once already with the VAT rule."""

    def test_it_REFUSES_when_R3s_artefact_is_absent(self, monkeypatch, tmp_path):
        monkeypatch.setattr(r4, "R3_ARTEFACT", tmp_path / "absent.json")
        with pytest.raises(CeilingUnavailable) as caught:
            r4.time_shifting_ceiling()
        assert "will NOT" in str(caught.value), (
            "a refusal that does not say it declines to recompute invites someone to recompute"
        )

    def test_it_READS_the_corrected_rung_and_keeps_the_currencies_apart(
            self, monkeypatch, tmp_path):
        artefact = tmp_path / "r3.json"
        artefact.write_text(json.dumps({
            "corrected_headline": {"gbp_per_household_year": 4.03,
                                   "kg_co2e_per_household_year": 91.7},
            "rungs": {"forecast_ceiling": {"gbp_per_household_year": 5.93,
                                           "kg_co2e_per_household_year": 134.8}},
        }))
        monkeypatch.setattr(r4, "R3_ARTEFACT", artefact)
        arm = r4.time_shifting_ceiling()
        assert arm["carbon_value_gbp_per_household_year"] == 4.03, "it took the uncorrected rung"
        assert arm["kg_co2e_per_household_year"] == 91.7
        assert arm["gbp_per_household_year"] is None, (
            "carbon valued at the traded price is NOT a bill saving, and putting it in the "
            "bill-saving column is what would let a reader add it to tariff fit's pounds"
        )


class TestItFailsClosed:
    """DEFECT: R15 fail-silent. 'R4 is worth nothing' retires the biggest unbuilt programme on the
    map, so an unavailable instrument must never be able to report it."""

    def test_a_thin_book_REFUSES_and_the_refusal_says_it_is_NOT_a_finding(self):
        rows = [_pair(f"C{i}", 150.0, 100.0) for i in range(3)]
        arm = r4.tariff_fit_ceiling(_events(rows), {f"C{i}": 2000.0 for i in range(3)})
        assert arm["bound_kind"] == r4.UNBOUNDED
        assert arm["gbp_per_household_year"] is None
        assert "NOT a finding" in arm["why"]

    def test_the_whole_instrument_REFUSES_on_a_book_with_no_EAC(self, tmp_path):
        path = tmp_path / "run_output_test.json"
        path.write_text(json.dumps(_events([_pair("C1", 150.0, 100.0)])))
        with pytest.raises(CeilingUnavailable) as caught:
            r4.measure(run_path=path)
        assert "NOT a finding that R4 is worthless" in str(caught.value)


class TestTheHeadlineSurvivesTheArmItRefuses:
    """DEFECT (2026-09-08): `headline` read `households_above_the_reference` unconditionally, and
    only ONE of `tariff_fit_ceiling`'s two returns carries it. On the data-availability refusal --
    fewer than MIN_HOUSEHOLDS carrying a rate, a reference and an EAC together -- `--save` died
    with a KeyError and wrote no artefact at all.

    THE COST WAS NOT THIS TOOL'S, WHICH IS WHY IT IS WORTH A CLASS. `site/data/delivery.json` has
    published *"re-run `python3 -m tools.r4_product_ceiling --save`"* as the remedy for its stale
    product table since 2026-09-07; three controls in `site/test_harness_delivery_record.py` are
    red at HEAD waiting for it; and the site lane gates EVERY lane's commit on those. A refusal
    branch that cannot write its own artefact leaves a command on a published surface that cannot
    be run, and every lane pays for it.

    BOTH SUBJECTS COME OUT OF `tariff_fit_ceiling` ITSELF, never hand-built: a control fed a
    hand-written dict would stay green through exactly the shape change that caused this.
    """

    def _result(self, arm):
        """The smallest `result` the headline reads, with the arm under test dropped in."""
        return {
            "arms": {"tariff_fit": arm,
                     "time_shifting": {"kg_co2e_per_household_year": 91.7,
                                       "carbon_value_gbp_per_household_year": 4.03}},
            "property_attribute_census": {"logs_scanned": 27, "attributes_found": []},
            "verdict": {"ceilings": ["tariff_fit", "time_shifting"], "floors": ["solar"]},
        }

    def _arm(self, n):
        rows = [_pair(f"C{i}", 150.0, 100.0) for i in range(n)]
        return r4.tariff_fit_ceiling(_events(rows), {f"C{i}": 2000.0 for i in range(n)})

    def test_a_REFUSED_arm_is_headlined_and_never_crashes_the_write(self):
        arm = self._arm(3)
        assert arm["bound_kind"] == r4.UNBOUNDED, "this subject is no longer the refusal branch"
        said = r4.headline(self._result(arm))
        assert "CANNOT BE SAID" in said, (
            "the refused arm's coverage is not stated as a refusal: " + said[-400:])
        assert arm["why"] in said, "the refusal reaches the headline without its reason"
        assert "BOTH BOUNDED ARMS ARE SMALL" not in said, (
            "an arm that was REFUSED is published as bounded and small, which is the flattering "
            "reading of a data-availability failure")

    def test_a_BOUNDED_arm_still_states_its_count_and_calls_both_arms_bounded(self):
        """The witness that makes the one above a judgement. A headline hard-wired to the refusal
        wording would pass every leg there and say nothing."""
        arm = self._arm(r4.MIN_HOUSEHOLDS + 5)
        assert arm["bound_kind"] == r4.CEILING, "this subject is no longer the bounded branch"
        said = r4.headline(self._result(arm))
        assert "BOTH BOUNDED ARMS ARE SMALL" in said
        assert "CANNOT BE SAID" not in said, (
            "a bounded arm is reported as unsayable, so the refusal wording is unconditional")
        assert "{} of {} households".format(
            arm["households_above_the_reference"], arm["households"]) in said, (
            "the bounded arm's own coverage count does not reach the headline")
