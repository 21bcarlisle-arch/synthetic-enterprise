"""Writer 1's premium learns only from the book whose strike it moves: completed FIXED terms (B12,
2026-10-15).

The defect: the lookback took the last four completed terms of any tariff, about 10 in 11 of them
default terms earning the cap's headroom, and compared that with what a fixed strike priced for. So
fixed renewals took the full -5% in the years the cap sat above cost
(`docs/staging/SEAT_FINDING_THE_UNIT_RATE_MARGIN_STILL_READS_ABOVE_ITS_TARGET_ON_FIXED_TERMS_2026-10-14.md`).
"""
from company.pricing.renewal_rate_chain import PortfolioMarginBook


def _end(book, tariff_type, net_margin=10.0):
    book.term_ended(billing_account=tariff_type, commodity="electricity",
                    last_settled_day="2024-01-31", net_margin=net_margin, revenue=100.0,
                    standing_charge_revenue=0.0, volume_mwh=1.0, held_on_a_save=False,
                    tariff_type=tariff_type)


def test_a_fixed_term_teaches_the_premium_and_a_default_term_does_not():
    # The partition in one control: a book that admits nothing fails the first leg, and a book
    # that admits everything fails the second.
    book = PortfolioMarginBook()
    _end(book, "fixed", net_margin=2.0)
    _end(book, "svt", net_margin=30.0)
    book.as_of("2024-02-01")
    assert book.rates("electricity") == [0.02]
    assert len(book.priced_for("electricity")) == 1
