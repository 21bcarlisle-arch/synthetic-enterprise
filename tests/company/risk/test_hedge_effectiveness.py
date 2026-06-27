import datetime as dt
import pytest
from company.risk.hedge_effectiveness import (
    EffectivenessTest, EffectivenessOutcome, HedgeRelationshipType,
    HedgeEffectivenessBook,
)


def make_test(hedge_id="H1", item_change=-100.0, instrument_change=100.0,
              prospective=False, rel=HedgeRelationshipType.CASH_FLOW,
              date=None):
    return EffectivenessTest(
        hedge_id=hedge_id,
        test_date=date or dt.date(2022, 6, 30),
        relationship_type=rel,
        hedged_item_fair_value_change_gbp=item_change,
        hedging_instrument_fair_value_change_gbp=instrument_change,
        is_prospective=prospective,
    )


class TestEffectivenessTest:
    def test_perfect_effectiveness_ratio(self):
        t = make_test(item_change=-100.0, instrument_change=100.0)
        assert t.effectiveness_ratio_pct == 100.0

    def test_ratio_lower_bound(self):
        t = make_test(item_change=-100.0, instrument_change=80.0)
        assert t.effectiveness_ratio_pct == 80.0

    def test_ratio_upper_bound(self):
        t = make_test(item_change=-100.0, instrument_change=125.0)
        assert t.effectiveness_ratio_pct == 125.0

    def test_ratio_none_when_item_zero(self):
        t = make_test(item_change=0.0, instrument_change=50.0)
        assert t.effectiveness_ratio_pct is None

    def test_outcome_highly_effective(self):
        t = make_test(item_change=-100.0, instrument_change=100.0)
        assert t.outcome == EffectivenessOutcome.HIGHLY_EFFECTIVE

    def test_outcome_effective_at_lower_bound(self):
        t = make_test(item_change=-100.0, instrument_change=80.0)
        assert t.outcome == EffectivenessOutcome.HIGHLY_EFFECTIVE

    def test_outcome_effective_at_upper_bound(self):
        t = make_test(item_change=-100.0, instrument_change=125.0)
        assert t.outcome == EffectivenessOutcome.HIGHLY_EFFECTIVE

    def test_outcome_ineffective_below_bound(self):
        t = make_test(item_change=-100.0, instrument_change=70.0)
        assert t.outcome == EffectivenessOutcome.INEFFECTIVE

    def test_outcome_ineffective_above_bound(self):
        t = make_test(item_change=-100.0, instrument_change=130.0)
        assert t.outcome == EffectivenessOutcome.INEFFECTIVE

    def test_outcome_prospective_only(self):
        t = make_test(prospective=True)
        assert t.outcome == EffectivenessOutcome.PROSPECTIVE_ONLY

    def test_is_effective_true(self):
        t = make_test(item_change=-100.0, instrument_change=100.0)
        assert t.is_effective is True

    def test_is_effective_false(self):
        t = make_test(item_change=-100.0, instrument_change=60.0)
        assert t.is_effective is False

    def test_ineffectiveness_zero_when_perfect(self):
        t = make_test(item_change=-100.0, instrument_change=100.0)
        assert t.ineffectiveness_gbp == 0.0

    def test_ineffectiveness_when_effective_but_not_perfect(self):
        t = make_test(item_change=-100.0, instrument_change=90.0)
        assert t.ineffectiveness_gbp == -10.0

    def test_ineffectiveness_full_when_de_designated(self):
        t = make_test(item_change=-100.0, instrument_change=60.0)
        assert t.ineffectiveness_gbp == 60.0

    def test_ineffectiveness_zero_prospective(self):
        t = make_test(prospective=True)
        assert t.ineffectiveness_gbp == 0.0

    def test_frozen(self):
        t = make_test()
        with pytest.raises((AttributeError, TypeError)):
            t.hedge_id = "X"


class TestHedgeEffectivenessBook:
    def test_empty_book(self):
        book = HedgeEffectivenessBook()
        assert book.effective_tests() == []
        assert book.failed_tests() == []

    def test_record_and_retrieve(self):
        book = HedgeEffectivenessBook()
        t = make_test()
        book.record_test(t)
        assert t in book.tests_for_hedge("H1")

    def test_tests_for_hedge_filters(self):
        book = HedgeEffectivenessBook()
        book.record_test(make_test(hedge_id="H1"))
        book.record_test(make_test(hedge_id="H2"))
        assert len(book.tests_for_hedge("H1")) == 1

    def test_tests_for_period(self):
        book = HedgeEffectivenessBook()
        book.record_test(make_test(date=dt.date(2022, 3, 31)))
        book.record_test(make_test(date=dt.date(2022, 9, 30)))
        result = book.tests_for_period(dt.date(2022, 1, 1), dt.date(2022, 6, 30))
        assert len(result) == 1

    def test_failed_tests(self):
        book = HedgeEffectivenessBook()
        book.record_test(make_test(hedge_id="H1", item_change=-100.0, instrument_change=100.0))
        book.record_test(make_test(hedge_id="H2", item_change=-100.0, instrument_change=60.0))
        assert len(book.failed_tests()) == 1
        assert book.failed_tests()[0].hedge_id == "H2"

    def test_de_designated_hedges(self):
        book = HedgeEffectivenessBook()
        book.record_test(make_test(hedge_id="H1", item_change=-100.0, instrument_change=60.0))
        book.record_test(make_test(hedge_id="H1", item_change=-100.0, instrument_change=60.0))
        assert book.de_designated_hedges() == ["H1"]

    def test_de_designated_deduplicates(self):
        book = HedgeEffectivenessBook()
        book.record_test(make_test(hedge_id="H1", item_change=-100.0, instrument_change=60.0))
        book.record_test(make_test(hedge_id="H2", item_change=-100.0, instrument_change=60.0))
        assert len(book.de_designated_hedges()) == 2

    def test_total_ineffectiveness_all(self):
        book = HedgeEffectivenessBook()
        book.record_test(make_test(item_change=-100.0, instrument_change=90.0,
                                   date=dt.date(2022, 6, 30)))
        book.record_test(make_test(item_change=-100.0, instrument_change=90.0,
                                   date=dt.date(2023, 6, 30)))
        assert book.total_ineffectiveness_gbp() == -20.0

    def test_total_ineffectiveness_by_year(self):
        book = HedgeEffectivenessBook()
        book.record_test(make_test(item_change=-100.0, instrument_change=90.0,
                                   date=dt.date(2022, 6, 30)))
        book.record_test(make_test(item_change=-100.0, instrument_change=90.0,
                                   date=dt.date(2023, 6, 30)))
        assert book.total_ineffectiveness_gbp(year=2022) == -10.0

    def test_summary_keys(self):
        book = HedgeEffectivenessBook()
        book.record_test(make_test())
        s = book.effectiveness_summary()
        for k in ("total_tests", "effective", "ineffective", "pass_rate_pct",
                  "de_designated_hedge_count", "total_ineffectiveness_gbp"):
            assert k in s

    def test_summary_empty(self):
        book = HedgeEffectivenessBook()
        s = book.effectiveness_summary()
        assert s["total_tests"] == 0
        assert s["pass_rate_pct"] == 0.0

    def test_summary_pass_rate(self):
        book = HedgeEffectivenessBook()
        book.record_test(make_test(item_change=-100.0, instrument_change=100.0))
        book.record_test(make_test(item_change=-100.0, instrument_change=100.0))
        book.record_test(make_test(item_change=-100.0, instrument_change=60.0))
        s = book.effectiveness_summary()
        assert s["pass_rate_pct"] == pytest.approx(66.7)
