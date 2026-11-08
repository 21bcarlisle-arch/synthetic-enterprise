"""Tests for company/finance/corporation_tax.py -- Phase 316."""
from __future__ import annotations

import pytest

from company.finance.corporation_tax import (
    CorporationTaxBook,
    TaxProvision,
    _ct_rate_for_year,
)


class TestCTRateForYear:
    def test_rate_2016_is_20pct(self):
        assert _ct_rate_for_year(2016) == 0.20

    def test_rate_2017_is_19pct(self):
        assert _ct_rate_for_year(2017) == 0.19

    def test_rate_2022_is_19pct(self):
        assert _ct_rate_for_year(2022) == 0.19

    def test_rate_2023_is_25pct(self):
        assert _ct_rate_for_year(2023) == 0.25

    def test_rate_2024_is_25pct(self):
        assert _ct_rate_for_year(2024) == 0.25

    def test_unknown_year_defaults_to_25pct(self):
        assert _ct_rate_for_year(2030) == 0.25


class TestTaxProvision:
    def test_taxable_profit_no_relief(self):
        p = TaxProvision(2022, 1_000_000.0, 0.19)
        assert p.taxable_profit_gbp == 1_000_000.0

    def test_taxable_profit_with_relief(self):
        p = TaxProvision(2022, 1_000_000.0, 0.19, loss_relief_gbp=200_000.0)
        assert p.taxable_profit_gbp == 800_000.0

    def test_current_tax_gbp(self):
        p = TaxProvision(2022, 1_000_000.0, 0.19)
        assert p.current_tax_gbp == 190_000.0

    def test_current_tax_zero_on_loss(self):
        p = TaxProvision(2022, -500_000.0, 0.19)
        assert p.current_tax_gbp == 0.0

    def test_profit_after_tax(self):
        p = TaxProvision(2022, 1_000_000.0, 0.19)
        assert p.profit_after_tax_gbp == 810_000.0

    def test_effective_rate_pct(self):
        p = TaxProvision(2022, 1_000_000.0, 0.19)
        assert p.effective_rate_pct == 19.0

    def test_effective_rate_zero_on_loss(self):
        p = TaxProvision(2022, -100_000.0, 0.19)
        assert p.effective_rate_pct == 0.0

    def test_is_loss_year_true(self):
        p = TaxProvision(2022, -50_000.0, 0.19)
        assert p.is_loss_year

    def test_is_loss_year_false(self):
        p = TaxProvision(2022, 100_000.0, 0.19)
        assert not p.is_loss_year


class TestCorporationTaxBook:
    def _book(self) -> CorporationTaxBook:
        return CorporationTaxBook()

    def test_provision_for_year_profitable(self):
        book = self._book()
        p = book.provision_for_year(2022, 1_000_000.0)
        assert p.current_tax_gbp == 190_000.0

    def test_provision_for_year_2023_higher_rate(self):
        book = self._book()
        p = book.provision_for_year(2023, 1_000_000.0)
        assert p.current_tax_gbp == 250_000.0

    def test_loss_year_accumulates_losses(self):
        book = self._book()
        book.provision_for_year(2020, -200_000.0)
        assert book.accumulated_losses_gbp() == 200_000.0

    def test_loss_relief_applied_next_year(self):
        book = self._book()
        book.provision_for_year(2020, -200_000.0)
        p = book.provision_for_year(2021, 500_000.0)
        # Relief: 200k used; taxable = 300k; tax = 300k * 19% = 57k
        assert p.loss_relief_gbp == 200_000.0
        assert p.current_tax_gbp == round(300_000.0 * 0.19, 2)

    def test_losses_cleared_after_relief(self):
        book = self._book()
        book.provision_for_year(2020, -200_000.0)
        book.provision_for_year(2021, 500_000.0)
        assert book.accumulated_losses_gbp() == 0.0

    def test_total_tax_paid_multi_year(self):
        book = self._book()
        book.provision_for_year(2021, 1_000_000.0)
        book.provision_for_year(2022, 1_000_000.0)
        expected = round(1_000_000 * 0.19 + 1_000_000 * 0.19, 2)
        assert book.total_tax_paid_gbp() == expected

    def test_loss_years_list(self):
        book = self._book()
        book.provision_for_year(2020, -100_000.0)
        book.provision_for_year(2021, 500_000.0)
        assert len(book.loss_years()) == 1

    def test_tax_summary_keys(self):
        book = self._book()
        book.provision_for_year(2022, 800_000.0)
        book.provision_for_year(2023, 1_200_000.0)
        s = book.tax_summary()
        assert "years_filed" in s
        assert "total_tax_paid_gbp" in s
        assert "accumulated_losses_gbp" in s
        assert "loss_years" in s
        assert "by_year" in s
        assert len(s["by_year"]) == 2

    def test_empty_book_summary(self):
        book = self._book()
        s = book.tax_summary()
        assert s["years_filed"] == 0
        assert s["total_tax_paid_gbp"] == 0.0
