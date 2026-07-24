"""VALUE_CHAIN BUILD ladder step 2 — the live feed transform.

Proves ``build_credit_register_from_exposure`` against the REAL producer
(``TradingBook.exposure_by_counterparty``), not a hand-built dict, so the transform is
tied to the actual live stream it will consume once the run-loop sample-point is wired.

R15 both-ways: each control asserts the feed is LOAD-BEARING (a fail-open mutation — empty
register / dropped exposure / removed CCP haircut — reds the test), and that the
attribution/wall behaviour (UNATTRIBUTED skipped, out-of-money → zero exposure) holds.
"""
from __future__ import annotations

from company.trading.forward_book import ForwardContract, TradingBook
from company.trading.wholesale_credit_exposure import (
    ClearingStatus,
    CounterpartyCreditRating,
    CounterpartyType,
    WholesaleCreditExposureRegister,
    _CCP_NO_PER_NAME_LIMIT_GBP,
    _CLEARED_EXPOSURE_HAIRCUT,
    build_credit_register_from_exposure,
)


def _book_with_two_counterparties() -> TradingBook:
    """A book with one bilateral bank contract and one CCP-cleared contract, both ITM."""
    book = TradingBook()
    # Bilateral bank, agreed £40, notional 1000 MWh -> at £100 spot, netted MtM = +£60,000.
    book.open_hedge(
        ForwardContract(
            customer_id="C-BANK",
            term_start="2022-01-01",
            term_end="2022-12-31",
            notional_mwh=1000.0,
            agreed_price_gbp_per_mwh=40.0,
            hedge_fraction=1.0,
            bid_ask_cost_gbp=0.0,
            counterparty_id="BANK-1",
            counterparty_type=CounterpartyType.MAJOR_BANK,
            clearing_status=ClearingStatus.BILATERAL_ISDA,
            counterparty_rating=CounterpartyCreditRating.AA,
        )
    )
    # CCP-cleared, agreed £50, notional 2000 MWh -> at £100 spot, netted MtM = +£100,000.
    book.open_hedge(
        ForwardContract(
            customer_id="C-CCP",
            term_start="2022-01-01",
            term_end="2022-12-31",
            notional_mwh=2000.0,
            agreed_price_gbp_per_mwh=50.0,
            hedge_fraction=1.0,
            bid_ask_cost_gbp=0.0,
            counterparty_id="ICE_CLEAR_EUROPE",
            counterparty_type=CounterpartyType.CLEARING_HOUSE,
            clearing_status=ClearingStatus.CLEARED_CCP,
            counterparty_rating=None,
        )
    )
    return book


_PRICES = {"C-BANK": 100.0, "C-CCP": 100.0}


def test_feed_populates_register_from_real_producer():
    book = _book_with_two_counterparties()
    exposure = book.exposure_by_counterparty(_PRICES)
    reg = build_credit_register_from_exposure(exposure)

    assert isinstance(reg, WholesaleCreditExposureRegister)
    # LOAD-BEARING: an empty-register fail-open mutation reds here.
    assert len(reg.all_records()) == 2
    bank = reg.get("BANK-1")
    ccp = reg.get("ICE_CLEAR_EUROPE")
    assert bank is not None and ccp is not None

    # Bilateral: gross MtM carried through, no collateral, rating-band limit (AA = £3.0M).
    assert bank.gross_mtm_gbp == 60_000.0
    assert bank.net_exposure_gbp == 60_000.0
    assert bank.credit_rating is CounterpartyCreditRating.AA
    assert bank.credit_limit_gbp == 3_000_000.0
    assert bank.is_limit_breached is False


def test_ccp_haircut_and_no_per_name_limit():
    reg = build_credit_register_from_exposure(
        _book_with_two_counterparties().exposure_by_counterparty(_PRICES)
    )
    ccp = reg.get("ICE_CLEAR_EUROPE")
    # LOAD-BEARING: removing _CLEARED_EXPOSURE_HAIRCUT in net_exposure_gbp reds this.
    assert ccp.gross_mtm_gbp == 100_000.0
    assert ccp.net_exposure_gbp == 100_000.0 * _CLEARED_EXPOSURE_HAIRCUT
    # No per-name limit for a CCP — never breaches, whatever the exposure.
    assert ccp.credit_limit_gbp == _CCP_NO_PER_NAME_LIMIT_GBP
    assert ccp.is_limit_breached is False


def test_bilateral_breach_is_detected_through_the_feed():
    """A bilateral net exposure above its rating band MUST flag — proves gross_mtm is fed,
    not zeroed (a fail-open feed that dropped exposure would leave this un-breached)."""
    book = TradingBook()
    # agreed £10, notional 100_000 MWh, spot £60 -> netted MtM = +£5,000,000 > AA £3.0M limit.
    book.open_hedge(
        ForwardContract(
            customer_id="C-BIG",
            term_start="2022-01-01",
            term_end="2022-12-31",
            notional_mwh=100_000.0,
            agreed_price_gbp_per_mwh=10.0,
            hedge_fraction=1.0,
            bid_ask_cost_gbp=0.0,
            counterparty_id="BANK-2",
            counterparty_type=CounterpartyType.MAJOR_BANK,
            clearing_status=ClearingStatus.BILATERAL_ISDA,
            counterparty_rating=CounterpartyCreditRating.AA,
        )
    )
    reg = build_credit_register_from_exposure(
        book.exposure_by_counterparty({"C-BIG": 60.0})
    )
    rec = reg.get("BANK-2")
    assert rec.gross_mtm_gbp == 5_000_000.0
    assert rec.is_limit_breached is True
    assert reg.limit_breaches() == [rec]


def test_out_of_money_position_is_zero_exposure():
    """A net out-of-the-money counterparty (company owes) is zero credit exposure, not negative."""
    book = TradingBook()
    # agreed £90, spot £40 -> netted MtM = -£50,000 (OTM). Feed -> gross_credit_exposure 0.
    book.open_hedge(
        ForwardContract(
            customer_id="C-OTM",
            term_start="2022-01-01",
            term_end="2022-12-31",
            notional_mwh=1000.0,
            agreed_price_gbp_per_mwh=90.0,
            hedge_fraction=1.0,
            bid_ask_cost_gbp=0.0,
            counterparty_id="TRADER-1",
            counterparty_type=CounterpartyType.ENERGY_TRADER,
            clearing_status=ClearingStatus.BILATERAL_ISDA,
            counterparty_rating=CounterpartyCreditRating.A,
        )
    )
    reg = build_credit_register_from_exposure(book.exposure_by_counterparty({"C-OTM": 40.0}))
    rec = reg.get("TRADER-1")
    assert rec.gross_mtm_gbp == 0.0
    assert rec.net_exposure_gbp == 0.0


def test_unattributed_bucket_is_skipped():
    """A contract opened with no counterparty forms no phantom credit record (wall/data-quality)."""
    book = TradingBook()
    book.open_hedge(
        ForwardContract(
            customer_id="C-NAKED",
            term_start="2022-01-01",
            term_end="2022-12-31",
            notional_mwh=1000.0,
            agreed_price_gbp_per_mwh=40.0,
            hedge_fraction=1.0,
            bid_ask_cost_gbp=0.0,
        )  # no counterparty attribution -> nets under "UNATTRIBUTED"
    )
    exposure = book.exposure_by_counterparty({"C-NAKED": 100.0})
    assert "UNATTRIBUTED" in exposure  # the producer surfaces it
    reg = build_credit_register_from_exposure(exposure)
    assert reg.all_records() == []  # the feed does not fabricate a record for it


def test_feed_is_deterministic_replay():
    """C-S2: same exposure input -> byte-identical register content on replay."""
    book = _book_with_two_counterparties()
    exposure = book.exposure_by_counterparty(_PRICES)
    reg_a = build_credit_register_from_exposure(exposure)
    reg_b = build_credit_register_from_exposure(exposure)
    key = lambda r: (
        r.counterparty_id,
        r.gross_mtm_gbp,
        r.net_exposure_gbp,
        r.credit_limit_gbp,
        r.is_limit_breached,
    )
    assert sorted(map(key, reg_a.all_records())) == sorted(map(key, reg_b.all_records()))
