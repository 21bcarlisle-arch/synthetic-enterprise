"""VALUE_CHAIN step 1 — counterparty attribution on ForwardContract.

Grounds: docs/market_research/uk_supplier_hedge_counterparty_distribution_2026-07-24.md.
Covers the attribution fields (backward-compat), the deterministic R10 default
distribution, the epistemic-wall placement of the rating band, and the ISDA-netted
per-counterparty exposure feed. Includes R15-style checks that FAIL on the named
defects (split collapse, netting removed, credit-exposure fail-open).
"""
from collections import Counter

import pytest

from company.trading.forward_book import (
    CounterpartyAttribution,
    ForwardContract,
    TradingBook,
    assign_default_counterparty,
)
from company.trading.wholesale_credit_exposure import (
    ClearingStatus,
    CounterpartyCreditRating,
    CounterpartyType,
)


class TestBackwardCompatibility:
    def test_positional_construction_still_valid(self):
        # 6-positional form used by existing tests must still build (new fields default).
        c = ForwardContract("C1", "2022-01-01", "2023-01-01", 10.0, 80.0, 0.9)
        assert c.counterparty_id is None
        assert c.counterparty_type is None
        assert c.clearing_status is None
        assert c.counterparty_rating is None
        assert c.broker_arranged is False

    def test_new_fields_stored(self):
        c = ForwardContract(
            customer_id="C1", term_start="2022-01-01", term_end="2023-01-01",
            notional_mwh=10.0, agreed_price_gbp_per_mwh=80.0, hedge_fraction=0.9,
            counterparty_id="BANK-2", counterparty_type=CounterpartyType.MAJOR_BANK,
            clearing_status=ClearingStatus.BILATERAL_ISDA,
            counterparty_rating=CounterpartyCreditRating.AA, broker_arranged=True,
        )
        assert c.counterparty_id == "BANK-2"
        assert c.is_bilateral and not c.is_cleared
        assert c.broker_arranged is True

    def test_cleared_flag(self):
        c = ForwardContract("C1", "2022-01-01", "2023-01-01", 10.0, 80.0, 0.9,
                            clearing_status=ClearingStatus.CLEARED_CCP)
        assert c.is_cleared and not c.is_bilateral


class TestDefaultAssignment:
    def test_deterministic_repeatable(self):
        # Same inputs -> identical attribution across calls (C-S2 deterministic replay).
        a = assign_default_counterparty("C1", "2022-01-01", 10.0)
        b = assign_default_counterparty("C1", "2022-01-01", 10.0)
        assert a == b

    def test_process_independent_golden(self):
        # Golden value pins the hashlib draw. If someone swaps to the salted builtin
        # hash(), this value changes per-process and the test fails -> proves determinism
        # does not rely on process-local salt.
        a = assign_default_counterparty("C1", "2022-01-01", 10.0)
        assert a == CounterpartyAttribution(
            counterparty_id="ICE_CLEAR_EUROPE",
            counterparty_type=CounterpartyType.CLEARING_HOUSE,
            clearing_status=ClearingStatus.CLEARED_CCP,
            counterparty_rating=None,
            broker_arranged=False,
        )

    def test_ccp_has_no_rating_wall_placement(self):
        # CCP-cleared: no per-name credit limit -> no rating band (RQ3). Bilateral MUST
        # carry a published rating band (wall-safe observable, RQ4).
        pop = [assign_default_counterparty(f"C{i}", "2022-01-01", 10.0 + (i % 5))
               for i in range(500)]
        for at in pop:
            if at.clearing_status == ClearingStatus.CLEARED_CCP:
                assert at.counterparty_rating is None
            else:
                assert at.counterparty_rating is not None

    def test_population_split_is_roughly_half_cleared(self):
        # R10 default: ~50/50 cleared/bilateral. R15 both ways: this FAILS if the split
        # collapses to a single channel (a static/degenerate assignment defect).
        n = 3000
        counts = Counter(
            assign_default_counterparty(f"CUST{i}", "2022-01-01", 10.0 + (i % 7)).clearing_status
            for i in range(n)
        )
        cleared = counts[ClearingStatus.CLEARED_CCP]
        bilateral = counts[ClearingStatus.BILATERAL_ISDA]
        assert cleared > 0 and bilateral > 0, "split collapsed to one channel"
        assert 0.42 <= cleared / n <= 0.58, f"cleared share {cleared / n:.3f} out of band"

    def test_bilateral_pool_is_concentrated(self):
        # Real ISDA-onboarding cost -> a small active bilateral pool per type (RQ2).
        ids = {
            assign_default_counterparty(f"CUST{i}", "2022-01-01", 10.0 + (i % 7)).counterparty_id
            for i in range(3000)
        }
        bilateral_ids = {i for i in ids if i != "ICE_CLEAR_EUROPE"}
        # 4 bank + 4 trader + 3 generator = 11 distinct names, not one per contract.
        assert len(bilateral_ids) <= 11


class TestExposureByCounterparty:
    def _book_with(self, contracts):
        book = TradingBook()
        for c in contracts:
            book.open_hedge(c)
        return book

    def test_isda_netting_across_a_counterparty(self):
        # Two contracts with the same counterparty net BEFORE exposure is taken.
        # One in-the-money (+), one out (-); net decides the exposure.
        c_long = ForwardContract("A", "2022-01-01", "2023-01-01", 100.0, 50.0, 1.0,
                                 counterparty_id="BANK-1",
                                 counterparty_type=CounterpartyType.MAJOR_BANK,
                                 clearing_status=ClearingStatus.BILATERAL_ISDA,
                                 counterparty_rating=CounterpartyCreditRating.AA)
        c_short = ForwardContract("B", "2022-01-01", "2023-01-01", 100.0, 90.0, 1.0,
                                  counterparty_id="BANK-1",
                                  counterparty_type=CounterpartyType.MAJOR_BANK,
                                  clearing_status=ClearingStatus.BILATERAL_ISDA,
                                  counterparty_rating=CounterpartyCreditRating.AA)
        book = self._book_with([c_long, c_short])
        # market 70: c_long MtM = (70-50)*100 = +2000 ; c_short MtM = (70-90)*100 = -2000
        agg = book.exposure_by_counterparty({"A": 70.0, "B": 70.0})
        entry = agg["BANK-1"]
        assert entry["netted_mtm_gbp"] == 0.0
        # netted to zero -> zero credit exposure (netting works; not 2000 gross-per-leg)
        assert entry["gross_credit_exposure_gbp"] == 0.0
        assert entry["position_count"] == 2

    def test_positive_net_creates_exposure(self):
        c = ForwardContract("A", "2022-01-01", "2023-01-01", 100.0, 50.0, 1.0,
                            counterparty_id="BANK-1",
                            counterparty_type=CounterpartyType.MAJOR_BANK,
                            clearing_status=ClearingStatus.BILATERAL_ISDA,
                            counterparty_rating=CounterpartyCreditRating.AA)
        book = self._book_with([c])
        agg = book.exposure_by_counterparty({"A": 70.0})
        assert agg["BANK-1"]["gross_credit_exposure_gbp"] == 2000.0

    def test_negative_net_is_zero_exposure_not_negative(self):
        # Out-of-the-money net: the company owes, so counterparty credit exposure is 0,
        # never negative (a negative would be a fail-open credit-exposure defect).
        c = ForwardContract("A", "2022-01-01", "2023-01-01", 100.0, 90.0, 1.0,
                            counterparty_id="BANK-1",
                            counterparty_type=CounterpartyType.MAJOR_BANK,
                            clearing_status=ClearingStatus.BILATERAL_ISDA,
                            counterparty_rating=CounterpartyCreditRating.AA)
        book = self._book_with([c])
        agg = book.exposure_by_counterparty({"A": 70.0})
        assert agg["BANK-1"]["netted_mtm_gbp"] == -2000.0
        assert agg["BANK-1"]["gross_credit_exposure_gbp"] == 0.0

    def test_unattributed_contracts_group_separately(self):
        c = ForwardContract("A", "2022-01-01", "2023-01-01", 100.0, 50.0, 1.0)
        book = self._book_with([c])
        agg = book.exposure_by_counterparty({"A": 70.0})
        assert "UNATTRIBUTED" in agg
        assert agg["UNATTRIBUTED"]["counterparty_type"] is None

    def test_closed_positions_excluded(self):
        c = ForwardContract("A", "2022-01-01", "2023-01-01", 100.0, 50.0, 1.0,
                            counterparty_id="BANK-1",
                            counterparty_type=CounterpartyType.MAJOR_BANK,
                            clearing_status=ClearingStatus.BILATERAL_ISDA)
        book = self._book_with([c])
        book.close_position("A", "2022-01-01", "2022-06-01", 70.0)
        agg = book.exposure_by_counterparty({"A": 70.0})
        assert agg == {}

    def test_broker_arranged_counted(self):
        c = ForwardContract("A", "2022-01-01", "2023-01-01", 100.0, 50.0, 1.0,
                            counterparty_id="TRADER-1",
                            counterparty_type=CounterpartyType.ENERGY_TRADER,
                            clearing_status=ClearingStatus.BILATERAL_ISDA,
                            broker_arranged=True)
        book = self._book_with([c])
        agg = book.exposure_by_counterparty({"A": 70.0})
        assert agg["TRADER-1"]["broker_arranged_count"] == 1


class TestFeedsRegisterShape:
    def test_exposure_maps_onto_credit_record_fields(self):
        # The aggregation output is the intended feed for WholesaleCreditRecord:
        # gross_credit_exposure_gbp -> gross_mtm_gbp, plus type/clearing/rating carried.
        from company.trading.wholesale_credit_exposure import WholesaleCreditRecord
        c = ForwardContract("A", "2022-01-01", "2023-01-01", 100.0, 50.0, 1.0,
                            counterparty_id="BANK-1",
                            counterparty_type=CounterpartyType.MAJOR_BANK,
                            clearing_status=ClearingStatus.BILATERAL_ISDA,
                            counterparty_rating=CounterpartyCreditRating.AA)
        book = TradingBook()
        book.open_hedge(c)
        entry = book.exposure_by_counterparty({"A": 70.0})["BANK-1"]
        record = WholesaleCreditRecord(
            counterparty_id=entry["counterparty_id"],
            counterparty_type=CounterpartyType(entry["counterparty_type"]),
            credit_rating=CounterpartyCreditRating(entry["counterparty_rating"]),
            clearing_status=ClearingStatus(entry["clearing_status"]),
            gross_mtm_gbp=entry["gross_credit_exposure_gbp"],
            collateral_held_gbp=0.0,
        )
        assert record.gross_mtm_gbp == 2000.0
        assert record.credit_limit_gbp == 3_000_000.0  # AA band from the register
        assert not record.is_limit_breached
