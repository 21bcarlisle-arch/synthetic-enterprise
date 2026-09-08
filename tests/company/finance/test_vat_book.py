"""Tests for company/finance/vat_book.py -- Phase 317."""
from __future__ import annotations

import datetime as dt
import importlib
import json
from pathlib import Path

import pytest

from company.finance.vat_book import (
    SME_ELEC_THRESHOLD_KWH_PER_DAY,
    SME_GAS_THRESHOLD_KWH_PER_DAY,
    VATBook,
    VATQuarterlyReturn,
    VATRateCategory,
    VATTransaction,
    classify_vat_category,
)


def _txn(
    account_id: str = "A001",
    date: dt.date = dt.date(2023, 1, 15),
    net: float = 100.0,
    category: VATRateCategory = VATRateCategory.DOMESTIC_REDUCED,
) -> VATTransaction:
    return VATTransaction(account_id, date, net, category)


class TestClassifyVATCategory:
    def test_residential_is_reduced(self):
        assert classify_vat_category(is_residential=True) == VATRateCategory.DOMESTIC_REDUCED

    def test_large_business_is_standard(self):
        assert classify_vat_category(is_residential=False, daily_consumption_kwh=500.0) == VATRateCategory.STANDARD

    def test_sme_below_threshold_is_reduced(self):
        assert classify_vat_category(is_residential=False, daily_consumption_kwh=30.0) == VATRateCategory.DOMESTIC_REDUCED


class TestTheDeMinimisIsPerFuelAndNotTheLargerOfTheTwo:
    """THE DEFECT: `classify_vat_category` took `max(elec_limit, gas_limit)` and applied it to
    every fuel, so a business ELECTRICITY supply anywhere in the 33-145 kWh/day band was
    reduced-rated where VAT Notice 701/19 s5.2 says standard. Over-charging or under-charging VAT
    is money, and this direction under-charges: the supplier owes HMRC the difference.

    The whole band is asserted, not one point in it, because a single point passes for a
    limit set anywhere below it.
    """

    #: Strictly inside the band where the two fuels take OPPOSITE rates: above electricity's
    #: 33 kWh/day, at or below gas's 145.
    BAND = [33.5, 50.0, 100.0, 144.9, 145.0]

    @pytest.mark.parametrize("kwh_per_day", BAND)
    def test_business_electricity_in_the_band_is_standard_rated(self, kwh_per_day):
        assert classify_vat_category(
            is_residential=False, daily_consumption_kwh=kwh_per_day, fuel="electricity"
        ) == VATRateCategory.STANDARD

    @pytest.mark.parametrize("kwh_per_day", BAND)
    def test_business_gas_in_the_same_band_is_reduced_rated(self, kwh_per_day):
        assert classify_vat_category(
            is_residential=False, daily_consumption_kwh=kwh_per_day, fuel="gas"
        ) == VATRateCategory.DOMESTIC_REDUCED

    def test_the_band_is_non_empty_so_the_two_tests_above_disagree(self):
        """Reachability. Both tests above pass vacuously if the two limits are ever equal --
        every case would be on the same side of both. Assert the partition can be entered."""
        assert SME_ELEC_THRESHOLD_KWH_PER_DAY < SME_GAS_THRESHOLD_KWH_PER_DAY
        assert any(
            SME_ELEC_THRESHOLD_KWH_PER_DAY < k <= SME_GAS_THRESHOLD_KWH_PER_DAY
            for k in self.BAND
        )

    def test_an_unnamed_fuel_inside_the_band_refuses_and_says_why(self):
        """Fail closed. Outside the band every fuel agrees, so the answer is honest without
        knowing the fuel; inside it there is no answer right for both."""
        with pytest.raises(ValueError, match="no fuel was named"):
            classify_vat_category(is_residential=False, daily_consumption_kwh=100.0)

    @pytest.mark.parametrize(
        "kwh_per_day,expected",
        [(30.0, VATRateCategory.DOMESTIC_REDUCED), (500.0, VATRateCategory.STANDARD)],
    )
    def test_an_unnamed_fuel_outside_the_band_still_answers(self, kwh_per_day, expected):
        assert classify_vat_category(
            is_residential=False, daily_consumption_kwh=kwh_per_day
        ) == expected

    def test_the_limits_are_the_published_ones_not_a_local_copy(self):
        """The point of the change: these are DERIVED from the regulation commons, so a
        correction to the artefact cannot leave this module behind. Compares against the
        published file directly rather than against the loader that produced them."""
        published = json.loads(
            (
                Path(__file__).resolve().parents[3]
                / "docs" / "domain_artefact_library" / "regulatory"
                / "vat_fuel_and_power_de_minimis.json"
            ).read_text()
        )["de_minimis_by_fuel"]
        assert SME_ELEC_THRESHOLD_KWH_PER_DAY == published["electricity"]["kwh_per_day"]
        assert SME_GAS_THRESHOLD_KWH_PER_DAY == published["gas"]["kwh_per_day"]

    def test_a_move_in_the_published_limit_carries_into_this_module(self):
        """THE PROPERTY IS PROVENANCE, AND A VALUE ASSERTION CANNOT REACH IT.

        Restoring the old literals `33.0`/`145.0` passes every other test in this class, because
        today the literals and the publication agree -- that is an EQUIVALENT mutation against a
        value check, and it is exactly the state the module was in for months while being wrong in
        principle. What distinguishes a copy from a derivation is only visible when the two
        disagree, so this moves the published limit and asserts the module follows it.
        """
        import company.billing.dual_fuel_bill as dfb
        import company.finance.vat_book as vb

        original = dict(dfb.SME_VAT_DE_MINIMIS_KWH_PER_DAY)
        try:
            dfb.SME_VAT_DE_MINIMIS_KWH_PER_DAY.clear()
            dfb.SME_VAT_DE_MINIMIS_KWH_PER_DAY.update({"electricity": 40.0, "gas": 160.0})
            importlib.reload(vb)
            assert vb.SME_ELEC_THRESHOLD_KWH_PER_DAY == 40.0
            assert vb.SME_GAS_THRESHOLD_KWH_PER_DAY == 160.0
            # and the READING moves with the limit, not just the constant: 35 kWh/day of
            # business electricity is standard-rated under the real 33 and reduced under 40.
            assert vb.classify_vat_category(
                is_residential=False, daily_consumption_kwh=35.0, fuel="electricity"
            ) == vb.VATRateCategory.DOMESTIC_REDUCED
        finally:
            dfb.SME_VAT_DE_MINIMIS_KWH_PER_DAY.clear()
            dfb.SME_VAT_DE_MINIMIS_KWH_PER_DAY.update(original)
            importlib.reload(vb)
        assert vb.SME_ELEC_THRESHOLD_KWH_PER_DAY == original["electricity"]

    def test_domestic_is_unconditional_even_above_every_limit(self):
        """The artefact's `domestic_is_unconditional`: a quantity test applied to a domestic
        account is not redundant, it is a different rule."""
        assert classify_vat_category(
            is_residential=True, daily_consumption_kwh=10_000.0, fuel="electricity"
        ) == VATRateCategory.DOMESTIC_REDUCED

    def test_an_unpublished_fuel_refuses_rather_than_inventing_a_limit(self):
        with pytest.raises(ValueError, match="no published de minimis limit"):
            classify_vat_category(
                is_residential=False, daily_consumption_kwh=50.0, fuel="heat_network"
            )


class TestVATTransaction:
    def test_domestic_vat_rate(self):
        t = _txn(category=VATRateCategory.DOMESTIC_REDUCED)
        assert t.vat_rate == 0.05

    def test_standard_vat_rate(self):
        t = _txn(category=VATRateCategory.STANDARD)
        assert t.vat_rate == 0.20

    def test_zero_vat_rate(self):
        t = _txn(category=VATRateCategory.ZERO)
        assert t.vat_rate == 0.0

    def test_vat_gbp_domestic(self):
        t = _txn(net=200.0, category=VATRateCategory.DOMESTIC_REDUCED)
        assert t.vat_gbp == 10.0  # 5% of 200

    def test_vat_gbp_standard(self):
        t = _txn(net=100.0, category=VATRateCategory.STANDARD)
        assert t.vat_gbp == 20.0  # 20% of 100

    def test_gross_amount(self):
        t = _txn(net=100.0, category=VATRateCategory.DOMESTIC_REDUCED)
        assert t.gross_amount_gbp == 105.0

    def test_zero_vat_gross_equals_net(self):
        t = _txn(net=50.0, category=VATRateCategory.ZERO)
        assert t.gross_amount_gbp == 50.0


class TestVATQuarterlyReturn:
    def test_net_vat_due(self):
        r = VATQuarterlyReturn(
            period_start=dt.date(2023, 1, 1),
            period_end=dt.date(2023, 3, 31),
            output_vat_gbp=10000.0,
            input_vat_gbp=800.0,
        )
        assert r.net_vat_due_gbp == 9200.0

    def test_is_repayment_false(self):
        r = VATQuarterlyReturn(dt.date(2023, 1, 1), dt.date(2023, 3, 31), 10000.0, 800.0)
        assert not r.is_repayment

    def test_is_repayment_true(self):
        r = VATQuarterlyReturn(dt.date(2023, 1, 1), dt.date(2023, 3, 31), 100.0, 500.0)
        assert r.is_repayment


class TestVATBook:
    def _book(self) -> VATBook:
        return VATBook()

    def test_record_transaction(self):
        book = self._book()
        book.record_transaction(_txn())
        assert len(book._transactions) == 1

    def test_transactions_for_period(self):
        book = self._book()
        book.record_transaction(_txn(date=dt.date(2023, 1, 15)))
        book.record_transaction(_txn(date=dt.date(2023, 4, 15)))
        result = book.transactions_for_period(dt.date(2023, 1, 1), dt.date(2023, 3, 31))
        assert len(result) == 1

    def test_quarterly_return_q1(self):
        book = self._book()
        book.record_transaction(_txn(date=dt.date(2023, 2, 1), net=1000.0))
        ret = book.quarterly_return(2023, 1)
        assert ret.output_vat_gbp == 50.0  # 5% of 1000
        assert ret.input_vat_gbp == round(50.0 * 0.08, 2)

    def test_total_output_vat_gbp(self):
        book = self._book()
        book.record_transaction(_txn(net=200.0, category=VATRateCategory.DOMESTIC_REDUCED))
        book.record_transaction(_txn(net=100.0, category=VATRateCategory.STANDARD))
        # 5% of 200 = 10; 20% of 100 = 20
        assert book.total_output_vat_gbp() == 30.0

    def test_total_output_vat_filtered_by_year(self):
        book = self._book()
        book.record_transaction(_txn(date=dt.date(2022, 6, 1), net=200.0))
        book.record_transaction(_txn(date=dt.date(2023, 6, 1), net=200.0))
        assert book.total_output_vat_gbp(year=2023) == 10.0

    def test_vat_summary_keys(self):
        book = self._book()
        book.record_transaction(_txn())
        s = book.vat_summary()
        assert "total_transactions" in s
        assert "total_output_vat_gbp" in s
        assert "by_category" in s

    def test_empty_book(self):
        book = self._book()
        s = book.vat_summary()
        assert s["total_transactions"] == 0
        assert s["total_output_vat_gbp"] == 0.0
