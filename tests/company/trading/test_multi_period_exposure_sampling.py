"""R15 both-ways for VALUE_CHAIN multi-period credit-exposure sampling.

The single end-of-run open_contracts() mark sees a near-EMPTY book over a 2016-2025 run
(almost every term has delivered by effective_end), so the board-meaningful PEAK
counterparty exposure -- which occurs mid-run at maximum concurrent open position during a
price shock -- is invisible. `live_contracts_as_of` / `exposure_by_counterparty_as_of`
reconstruct the calendar-live positions as-of a past date from the retained book so a sample
loop captures that peak. Wall-clean: own book term windows + own observable forward marks.

R15 both-ways: each test names the mutation it reds. The teeth test (peak > end-of-run) is
the guard on the whole mechanism -- reverting `live_contracts_as_of` to end-of-run
`open_contracts()` (i.e. dropping the as-of reconstruction) collapses the peak to the
near-zero end value and reds it.
"""
from company.trading.forward_book import ForwardContract, TradingBook
from company.trading.wholesale_credit_exposure import (
    ClearingStatus,
    CounterpartyCreditRating,
    CounterpartyType,
    build_credit_register_from_exposure,
)


def _bilateral(cid, term_start, term_end, notional, agreed, cp_id="BANK_A"):
    """An in-the-money-when-marked-up bilateral position attributed to one counterparty."""
    return ForwardContract(
        customer_id=cid,
        term_start=term_start,
        term_end=term_end,
        notional_mwh=notional,
        agreed_price_gbp_per_mwh=agreed,
        hedge_fraction=1.0,
        counterparty_id=cp_id,
        counterparty_type=CounterpartyType.MAJOR_BANK,
        clearing_status=ClearingStatus.BILATERAL_ISDA,
        counterparty_rating=CounterpartyCreditRating.A,
    )


def _peak_net_exposure(book: TradingBook, sample_dates, mark_price):
    """Sample the book at each date at a flat mark and return the peak net exposure."""
    peak = 0.0
    for sd in sample_dates:
        prices = {c.customer_id: mark_price for c in book.live_contracts_as_of(sd)}
        reg = build_credit_register_from_exposure(
            book.exposure_by_counterparty_as_of(prices, sd)
        )
        peak = max(peak, reg.total_net_exposure_gbp())
    return peak


# ---------------------------------------------------------------------------
# live_contracts_as_of boundary correctness (reds an off-by-one on term windows)
# ---------------------------------------------------------------------------
def test_live_contracts_as_of_calendar_window_inclusive():
    book = TradingBook()
    book.open_hedge(_bilateral("C1", "2020-01-01", "2020-12-31", 100.0, 40.0))
    live_ids = lambda d: [c.customer_id for c in book.live_contracts_as_of(d)]
    assert live_ids("2020-06-30") == ["C1"]          # mid-window: live
    assert live_ids("2020-01-01") == ["C1"]          # start boundary inclusive
    assert live_ids("2020-12-31") == ["C1"]          # end boundary inclusive
    assert live_ids("2019-12-31") == []              # before start: not live
    assert live_ids("2021-01-01") == []              # after end: not live


# ---------------------------------------------------------------------------
# TEETH (the mechanism's reason to exist): peak mid-run exposure > end-of-run mark.
# A big 2020 position has delivered by 2025 -> end-of-run open_contracts() sees ~nothing,
# but the mid-run sample sees the real exposure. Reverting live_contracts_as_of to
# open_contracts() collapses the peak to the end value and reds this.
# ---------------------------------------------------------------------------
def test_peak_midrun_exposure_exceeds_end_of_run_snapshot():
    book = TradingBook()
    # A large early position, long delivered before the run end.
    book.open_hedge(_bilateral("C_2020", "2020-01-01", "2020-12-31", 10_000.0, 30.0))
    # A tiny position still live at run end.
    book.open_hedge(_bilateral("C_2025", "2025-01-01", "2025-12-31", 10.0, 30.0))

    mark = 60.0  # marked up -> both in-the-money (counterparty owes the company)
    end_of_run = "2025-06-30"

    # End-of-run single mark: only the tiny 2025 position is calendar-live.
    end_prices = {c.customer_id: mark for c in book.live_contracts_as_of(end_of_run)}
    end_reg = build_credit_register_from_exposure(
        book.exposure_by_counterparty_as_of(end_prices, end_of_run)
    )
    end_exposure = end_reg.total_net_exposure_gbp()

    # Multi-period peak across semi-annual samples.
    samples = ["2020-06-30", "2020-12-31", "2024-12-31", "2025-06-30"]
    peak_exposure = _peak_net_exposure(book, samples, mark)

    assert end_exposure < 1_000.0                     # end-of-run book is near-empty
    assert peak_exposure > 100_000.0                  # mid-run peak is real and large
    assert peak_exposure > end_exposure * 10          # the peak is what the single mark missed


# ---------------------------------------------------------------------------
# _as_of agrees with the end-of-run method when every contract is live-as-of that date
# (consistency: the refactor did not change the netting core).
# ---------------------------------------------------------------------------
def test_as_of_matches_open_when_all_live():
    book = TradingBook()
    book.open_hedge(_bilateral("C1", "2021-01-01", "2021-12-31", 500.0, 40.0, cp_id="BANK_A"))
    book.open_hedge(_bilateral("C2", "2021-01-01", "2021-12-31", 300.0, 40.0, cp_id="BANK_A"))
    d = "2021-06-30"
    prices = {"C1": 55.0, "C2": 55.0}
    as_of = book.exposure_by_counterparty_as_of(prices, d)
    openv = book.exposure_by_counterparty(prices)   # all still open (nothing settled)
    assert as_of == openv
    # Netting is real: both trades net under one counterparty.
    assert as_of["BANK_A"]["position_count"] == 2


# ---------------------------------------------------------------------------
# ISDA netting still bites through the as-of path (reds if netting were dropped):
# an offsetting position with the same counterparty must reduce net exposure.
# ---------------------------------------------------------------------------
def test_as_of_netting_offsets_within_counterparty():
    book = TradingBook()
    # In-the-money leg (agreed below mark) and out-of-the-money leg (agreed above mark),
    # same counterparty, both live on the sample date.
    book.open_hedge(_bilateral("C_itm", "2021-01-01", "2021-12-31", 1000.0, 30.0, cp_id="BANK_A"))
    book.open_hedge(_bilateral("C_otm", "2021-01-01", "2021-12-31", 1000.0, 90.0, cp_id="BANK_A"))
    d, mark = "2021-06-30", 60.0
    prices = {"C_itm": mark, "C_otm": mark}
    reg = build_credit_register_from_exposure(
        book.exposure_by_counterparty_as_of(prices, d)
    )
    # +30*1000 and -30*1000 net to zero -> no credit exposure (max(0, 0)).
    assert reg.total_net_exposure_gbp() == 0.0


# ---------------------------------------------------------------------------
# Determinism / replay (C-S2): identical books + sample dates -> identical peak.
# ---------------------------------------------------------------------------
def test_sampling_is_deterministic():
    def build():
        b = TradingBook()
        b.open_hedge(_bilateral("C1", "2020-01-01", "2020-12-31", 5000.0, 30.0))
        b.open_hedge(_bilateral("C2", "2021-01-01", "2021-12-31", 2000.0, 35.0, cp_id="TRADER_X"))
        return b

    samples = ["2020-06-30", "2020-12-31", "2021-06-30", "2021-12-31"]
    assert _peak_net_exposure(build(), samples, 70.0) == _peak_net_exposure(build(), samples, 70.0)
