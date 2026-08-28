"""SLC 22B, the Ban on Acquisition-only Tariffs, as a time-indexed licence condition.

Roadmap R4 of WORKER_FINDING_THE_SOURCED_ACQUISITION_MODEL_IS_UNWIRED_AND_THE_INVENTED_ONE_IS_LIVE
(2026-08-28). The condition commenced 2022-04-01 and our world spans the discontinuity with one
set of acquisition physics; these are the controls that make the book answerable to it.

R13 note, because this is a world change: it is BASELINE. The commencement date and the rule are
Ofgem's, read from the published condition, and registering them was decided blind to what it
does to our results. Nothing here is a difficulty dial.
"""
from datetime import date

import pytest

from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    NO_ACQUISITION_ONLY_TARIFF,
    acquisition_only_tariff_breaches,
    check_no_acquisition_only_tariff,
)

BEFORE = date(2022, 3, 31)
COMMENCEMENT = date(2022, 4, 1)
AFTER = date(2023, 6, 1)


def _offer(klass, rate, segment="resi", commodity="electricity"):
    return {
        "customer_class": klass,
        "unit_rate_gbp_per_mwh": rate,
        "segment": segment,
        "commodity": commodity,
    }


class TestTheConditionIsRegistered:
    def test_it_is_in_the_register(self):
        assert NO_ACQUISITION_ONLY_TARIFF in ALL_INVARIANTS

    def test_it_carries_its_real_commencement_date(self):
        assert NO_ACQUISITION_ONLY_TARIFF.effective_from == date(2022, 4, 1)

    def test_it_has_no_fabricated_end_date(self):
        """The ban is PROPOSED to run to 2027-03-31 and has been extended before. A date nobody
        has legislated is a fabricated one, and the regulation-commons doctrine forbids it."""
        assert NO_ACQUISITION_ONLY_TARIFF.effective_to is None

    def test_it_cites_the_condition_and_the_derogation(self):
        source = NO_ACQUISITION_ONLY_TARIFF.source
        assert "22B" in source
        assert "Derogation" in source


class TestTheLawIsTimeIndexed:
    """The whole point of R4: the same conduct is lawful before commencement and not after."""

    ACQUISITION_ONLY = [_offer("new", 200.0), _offer("existing", 260.0)]

    def test_lawful_the_day_before_commencement(self):
        assert check_no_acquisition_only_tariff(self.ACQUISITION_ONLY, BEFORE) is True

    def test_a_breach_on_the_day_it_commences(self):
        assert check_no_acquisition_only_tariff(self.ACQUISITION_ONLY, COMMENCEMENT) is False

    def test_still_a_breach_a_year_later(self):
        assert check_no_acquisition_only_tariff(self.ACQUISITION_ONLY, AFTER) is False

    def test_the_pre_2022_market_is_not_retrospectively_criminalised(self):
        """2016-2021 acquisition-only pricing is what the GB market WAS. A control that called
        every one of those years a breach would be asserting a fact about history that is false,
        and Historical Ground Truth is a wall."""
        for year in range(2016, 2022):
            assert check_no_acquisition_only_tariff(
                self.ACQUISITION_ONLY, date(year, 6, 1)) is True


class TestTheAsymmetryIsOneDirectional:
    def test_a_retention_only_deal_is_lawful(self):
        """The Market-wide Derogation, in terms: a cheaper price only existing customers can get
        is expressly permitted. A control that fired on this would forbid retention entirely."""
        offers = [_offer("existing", 200.0), _offer("new", 260.0)]
        assert check_no_acquisition_only_tariff(offers, AFTER) is True

    def test_matching_prices_are_lawful(self):
        offers = [_offer("new", 240.0), _offer("existing", 240.0)]
        assert check_no_acquisition_only_tariff(offers, AFTER) is True

    def test_a_new_price_matched_by_any_existing_offer_is_lawful(self):
        """It has to be AVAILABLE to existing customers, not taken by all of them. One existing
        offer at or below the new price satisfies the condition."""
        offers = [_offer("new", 240.0), _offer("existing", 240.0), _offer("existing", 300.0)]
        assert check_no_acquisition_only_tariff(offers, AFTER) is True


class TestScope:
    def test_non_domestic_is_out_of_scope(self):
        """SLC 22B is a domestic condition. An SME acquisition deal is not a breach of it, and
        claiming otherwise would be inventing coverage the law does not have."""
        offers = [_offer("new", 200.0, segment="SME"), _offer("existing", 260.0, segment="SME")]
        assert check_no_acquisition_only_tariff(offers, AFTER) is True

    def test_fuels_are_compared_within_themselves(self):
        """MUTATION: were the groups collapsed, a cheap new-customer gas price would be excused
        by an existing-customer ELECTRICITY price, which is not a comparison of anything."""
        offers = [
            _offer("new", 60.0, commodity="gas"),
            _offer("existing", 40.0, commodity="electricity"),
        ]
        result = acquisition_only_tariff_breaches(offers, AFTER)
        assert len(result["breaches"]) == 1
        assert result["breaches"][0]["best_rate_available_to_existing"] is None

    def test_a_new_offer_with_no_existing_offer_at_all_is_acquisition_only(self):
        offers = [_offer("new", 200.0)]
        assert check_no_acquisition_only_tariff(offers, AFTER) is False


class TestUnreadableIsNotUnlawful:
    """The distinction this control exists to keep: a claim about our conduct versus a claim
    about the artefact. Three controls were found on 2026-08-27 that refused on input they could
    not read, which is a blast radius far wider than the defect."""

    def test_an_unreadable_offer_is_counted_not_charged(self):
        offers = [_offer("new", 240.0), _offer("existing", 240.0), {"nonsense": True}]
        result = acquisition_only_tariff_breaches(offers, AFTER)
        assert result["breaches"] == []
        assert result["offers_that_could_not_be_read"] == 1

    def test_a_readable_majority_is_still_judged(self):
        offers = [_offer("new", 200.0), _offer("existing", 260.0), {"nonsense": True}]
        result = acquisition_only_tariff_breaches(offers, AFTER)
        assert len(result["breaches"]) == 1
        assert result["offers_that_could_not_be_read"] == 1

    def test_a_population_it_can_read_NONE_of_is_a_failed_check_not_a_pass(self):
        """FAIL-SILENT, the R15 killer. Handed offers and able to read none of them, this control
        has no evidence — and no evidence is a failure, not a clean bill of health."""
        assert check_no_acquisition_only_tariff([{"nonsense": True}, {"junk": 1}], AFTER) is False

    def test_an_empty_book_is_not_a_breach(self):
        """A supplier that made no offers has broken nothing. Distinct from the case above:
        there is no population, rather than a population nobody could read."""
        assert check_no_acquisition_only_tariff([], AFTER) is True

    @pytest.mark.parametrize("bad", [
        {"customer_class": "new", "unit_rate_gbp_per_mwh": None},
        {"customer_class": "new", "unit_rate_gbp_per_mwh": "cheap"},
        {"customer_class": "prospect", "unit_rate_gbp_per_mwh": 200.0},
        {"customer_class": "new", "unit_rate_gbp_per_mwh": 0.0},
        {"customer_class": "new", "unit_rate_gbp_per_mwh": -5.0},
    ])
    def test_malformed_shapes_land_in_the_unreadable_count(self, bad):
        result = acquisition_only_tariff_breaches([bad], AFTER)
        assert result["offers_that_could_not_be_read"] == 1
        assert result["breaches"] == []


class TestMutations:
    """R15: each proves the control fires on its own named defect."""

    def test_it_fires_on_a_penny(self):
        """Not a threshold: any new-customer price below the best existing one is the condition
        breached. A tolerance here would be a licence to shave."""
        offers = [_offer("new", 239.99), _offer("existing", 240.0)]
        assert check_no_acquisition_only_tariff(offers, AFTER) is False

    def test_float_noise_alone_does_not_fire(self):
        offers = [_offer("new", 240.0), _offer("existing", 240.0 + 1e-12)]
        assert check_no_acquisition_only_tariff(offers, AFTER) is True

    def test_the_breach_names_both_rates(self):
        """A refusal that says why. Without both legs the reader cannot check the claim."""
        offers = [_offer("new", 200.0), _offer("existing", 260.0)]
        breach = acquisition_only_tariff_breaches(offers, AFTER)["breaches"][0]
        assert breach["new_customer_rate_gbp_per_mwh"] == 200.0
        assert breach["best_rate_available_to_existing"] == 260.0

    def test_the_in_scope_count_is_the_population_floor(self):
        """A control that judged zero offers passes everything. `in_scope` is what a caller
        checks to know the verdict was about something."""
        result = acquisition_only_tariff_breaches(
            [_offer("new", 240.0), _offer("existing", 240.0)], AFTER)
        assert result["in_scope"] == 1
