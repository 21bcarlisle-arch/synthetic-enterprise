from datetime import date, datetime, time, timedelta

import pytest

from company.interfaces.point_in_time_view import PointInTimeView, build_price_bitemporal_log
from company.interfaces.sim_interface import StubSimInterface
from sim.weather_price_sensitivity import COLD_SPELL_PRICE_MULTIPLIER
from simulation.renewals import NOTICE_DAYS
from simulation.run_phase2b import (
    DEFAULT_PROPERTY,
    REPORT_END,
    _build_gas_renewal_schedule,
    _clamp_term_end,
    _weather_adjusted_shape_fn,
    main as _run_phase2b_main,
)


def _flat_base_shape(date_str):
    return [1.0] * 48


def test_weather_adjusted_shape_fn_falls_back_without_weather_data():
    shape_fn = _weather_adjusted_shape_fn(_flat_base_shape, {}, DEFAULT_PROPERTY)
    assert shape_fn("2016-01-01") == [1.0] * 48


def test_weather_adjusted_shape_fn_adds_heating_load_on_cold_day():
    weather_means = {"2016-01-01": -5.0}  # well below 15.5C heating base
    shape_fn = _weather_adjusted_shape_fn(_flat_base_shape, weather_means, DEFAULT_PROPERTY)

    cold_shape = shape_fn("2016-01-01")
    assert sum(cold_shape) > sum(_flat_base_shape("2016-01-01"))


def _flat_gas_price_records(start_date: str, end_date: str, price: float = 50.0) -> list[dict]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    records = []
    current = start
    while current <= end:
        records.append({"settlementDate": current.isoformat(), "systemSellPrice": price})
        current += timedelta(days=1)
    return records


def test_build_gas_renewal_schedule_cold_spell_does_not_affect_gas_price():
    # Phase 42: weather adjustment is electricity-only. Gas uses seasonal calibration instead.
    records = _flat_gas_price_records("2015-10-01", "2017-06-30")
    customer = {"aq_kwh": 12000, "acquisition_date": "2016-01-01"}

    no_weather = _build_gas_renewal_schedule(
        {**customer, "acquisition_date": "2016-01-01"}, records
    )

    def cold_lookback(term_start):
        return [0.0] * 90

    with_cold_weather = _build_gas_renewal_schedule(
        {**customer, "acquisition_date": "2016-01-01"}, records, lookback_temps_fn=cold_lookback
    )

    ratio = (
        with_cold_weather[0]["forward_price_gbp_per_mwh"]
        / no_weather[0]["forward_price_gbp_per_mwh"]
    )
    # Weather does not affect gas forward pricing — ratio must be 1.0
    assert ratio == 1.0


def test_clamp_term_end_uses_default_report_end():
    # With no end_date kwarg the default REPORT_END is used — verify it returns a date string
    result = _clamp_term_end("2016-01-01")
    assert isinstance(result, str) and len(result) == 10


def test_clamp_term_end_truncates_to_custom_end_date():
    short_end = "2018-06-30"
    result = _clamp_term_end("2018-01-01", end_date=short_end)
    # Contract is 365 days; term end = 2019-01-01, which is beyond 2018-06-30 — should clamp
    assert result == "2018-07-01"  # end_date + 1 day (exclusive upper bound convention)


def test_clamp_term_end_does_not_truncate_when_natural_end_is_within_window():
    long_end = "2025-12-31"
    result = _clamp_term_end("2016-01-01", end_date=long_end)
    # Natural end ~2017-01-01 is well inside the window — no truncation
    assert result < long_end


def test_build_gas_renewal_schedule_truncates_on_report_end():
    records = _flat_gas_price_records("2015-01-01", "2022-12-31")
    customer = {"aq_kwh": 12000, "acquisition_date": "2016-01-01"}

    short_end = "2017-06-30"
    schedule = _build_gas_renewal_schedule(customer, records, report_end=short_end)

    # All terms must start on or before short_end
    for term in schedule:
        assert term["acquisition_date"] <= short_end

    # Full-window schedule should have more terms
    full_schedule = _build_gas_renewal_schedule(customer, records)
    assert len(full_schedule) > len(schedule)


# Phase 34a: 42-day notice period for gas schedule


def test_gas_schedule_notice_date_present():
    records = _flat_gas_price_records("2015-10-01", "2017-06-30")
    customer = {"aq_kwh": 12000, "acquisition_date": "2016-01-01"}
    schedule = _build_gas_renewal_schedule(customer, records)
    assert "notice_date" in schedule[0]


def test_gas_schedule_notice_date_is_42_days_before_term_start():
    records = _flat_gas_price_records("2015-01-01", "2020-12-31")
    customer = {"aq_kwh": 12000, "acquisition_date": "2016-06-01"}
    schedule = _build_gas_renewal_schedule(customer, records)
    for term in schedule:
        term_start = date.fromisoformat(term["acquisition_date"])
        notice_date = date.fromisoformat(term["notice_date"])
        assert (term_start - notice_date).days == NOTICE_DAYS


# Phase 12e: _compute_company_divergence tests

def test_compute_company_divergence_groups_by_year():
    from simulation.run_phase2b import _compute_company_divergence
    basis_risk = [
        {"term_start": "2021-01-01", "tariff_error_pct": 0.20},
        {"term_start": "2021-07-01", "tariff_error_pct": -0.30},
        {"term_start": "2022-01-01", "tariff_error_pct": 0.50},
    ]
    churn_risk = [
        {"term_start": "2021-01-01", "churn_estimate_error_pct": 0.10},
        {"term_start": "2022-01-01", "churn_estimate_error_pct": -0.40},
    ]
    result = _compute_company_divergence(basis_risk, churn_risk)
    tariff = result["tariff_error_by_year"]
    churn = result["churn_error_by_year"]

    assert "2021" in tariff
    assert "2022" in tariff
    assert tariff["2021"]["n"] == 2
    # mean abs error for 2021: (0.20 + 0.30) / 2 = 0.25
    assert abs(tariff["2021"]["mean_abs_error_pct"] - 0.25) < 0.001
    assert tariff["2021"]["max_abs_error_pct"] == 0.30
    assert tariff["2022"]["n"] == 1
    assert tariff["2022"]["mean_abs_error_pct"] == 0.50

    assert "2021" in churn
    assert "2022" in churn
    assert churn["2021"]["n"] == 1
    assert abs(churn["2021"]["mean_abs_error_pct"] - 0.10) < 0.001


def test_compute_company_divergence_skips_none_churn_errors():
    from simulation.run_phase2b import _compute_company_divergence
    churn_risk = [
        {"term_start": "2020-01-01", "churn_estimate_error_pct": None},
        {"term_start": "2020-07-01", "churn_estimate_error_pct": 0.15},
    ]
    result = _compute_company_divergence([], churn_risk)
    churn = result["churn_error_by_year"]
    assert "2020" in churn
    assert churn["2020"]["n"] == 1  # None entry skipped


def test_compute_company_divergence_empty_inputs():
    from simulation.run_phase2b import _compute_company_divergence
    result = _compute_company_divergence([], [])
    assert result["tariff_error_by_year"] == {}
    assert result["churn_error_by_year"] == {}


# ── Acquisition-aware retention guard tests (Phase 15b) ──────────────────────

def test_retention_offer_made_when_margin_plus_acq_exceeds_ret_cost():
    """Offer made when margin < ret_cost but margin + acq_cost > ret_cost."""
    from saas.growth_mandate import COST_PER_ACQUISITION
    # Scenario: crisis year, margin £122, ret_cost £160 (8% on large SME contract)
    # Old guard: blocked. New guard with acq_cost=£400: £122+£400=£522 > £160 → offered.
    margin = 122.0
    ret_cost = 160.0
    acq_cost = COST_PER_ACQUISITION.get("SME", 400.0)
    assert margin < ret_cost   # old guard would have blocked
    assert margin + acq_cost > ret_cost   # new guard allows


def test_retention_blocked_when_even_acq_savings_dont_justify():
    """Offer still blocked when margin + acq_cost < ret_cost (truly uneconomical)."""
    from saas.growth_mandate import COST_PER_ACQUISITION
    # Scenario: very expensive retention offer vs tiny margin and resi acq cost
    margin = 5.0
    # 8% discount on very large contract = ret_cost = 400 * 0.08 * 20000/1000 = £640
    ret_cost = 640.0
    acq_cost = COST_PER_ACQUISITION.get("resi", 150.0)
    assert margin + acq_cost < ret_cost   # new guard also blocks


def test_acq_cost_resi_lower_than_sme():
    """Resi acquisition cost is lower than SME (harder SME market justifies more retention spend)."""
    from saas.growth_mandate import COST_PER_ACQUISITION
    assert COST_PER_ACQUISITION["resi"] < COST_PER_ACQUISITION["SME"]


# Test throughput fix (TEST_THROUGHPUT_MEASUREMENT_AND_PROPOSAL.md root cause #1):
# this test previously called main() with no report_end truncation, replaying
# the full 2016-2025 decade (~185s) just to check one dict key's presence on the
# first retention-log entry. Truncated to the same 2016-2017 window already
# proven by the sibling file tests/simulation/test_run_phase2b_event_log.py's
# module-scoped sim_result_2017 fixture -- verified directly (2026-07-19) that
# this truncated window still produces retention_log entries (2 entries, the
# first including acq_cost_saved_gbp), so the assertion's exposure is unchanged.
@pytest.fixture(scope="module")
def _phase2b_result_2017():
    return _run_phase2b_main(report_end="2017-12-31", sim_interface=StubSimInterface())


def test_retention_log_includes_acq_cost_saved(_phase2b_result_2017):
    """Retention log entries include acq_cost_saved_gbp for traceability (Phase 15b)."""
    # conftest autouse fixture already sets SIM_FAST_MODE=1 for all tests
    result = _phase2b_result_2017
    rl = result.get("retention_log", [])
    # The truncated window must still exercise retention logging -- an empty
    # retention_log would make this test vacuously pass (fail-open), which is
    # exactly the R15 pattern to avoid.
    assert rl, "expected at least one retention_log entry in the truncated 2016-2017 window"
    assert "acq_cost_saved_gbp" in rl[0], "retention_log entry should include acq_cost_saved_gbp"


# --- price history as-of (2026-07-10 HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md fix;
# 2026-07-11 M1 depth work retired the per-call-site _price_history_as_of() wrapper in
# favour of PointInTimeView.get_price_history_as_of(), backed by a BitemporalEventLog
# built once per run via build_price_bitemporal_log() -- see
# docs/design/M1_PRICE_HISTORY_PIPELINE_FINDING.md) ---

def _daily_records(start_date_str, n_days, price_start=50.0):
    start = date.fromisoformat(start_date_str)
    return [
        {"settlementDate": (start + timedelta(days=i)).isoformat(), "systemSellPrice": price_start + i}
        for i in range(n_days)
    ]


def _piv_at(decision_date_str, elec_records, gas_records=None):
    log = build_price_bitemporal_log(elec_records, gas_records or [])
    decision_time = datetime.combine(date.fromisoformat(decision_date_str), time.min)
    return PointInTimeView(decision_time=decision_time, bitemporal_log=log)


def test_price_history_as_of_excludes_future_records():
    """The core fix: no record with settlementDate after the decision date may
    ever be returned -- this is the exact point-in-time-blindfold violation
    that was previously live (the full run's price history, including
    dates far in the decision's future, was passed unsliced)."""
    records = _daily_records("2016-01-01", 3000)  # spans ~8yrs of daily records
    history = _piv_at("2018-06-15", records).get_price_history_as_of("electricity")
    assert all(r["settlementDate"] <= "2018-06-15" for r in history)


def test_price_history_as_of_early_decision_gets_only_early_data():
    """A decision near the start of the run must not see any later data --
    directly what was broken (a 2018 decision seeing 2025 crisis-era data)."""
    records = _daily_records("2016-01-01", 3000)
    history = _piv_at("2016-02-01", records).get_price_history_as_of("electricity")
    assert all(r["settlementDate"] <= "2016-02-01" for r in history)
    assert len(history) <= 32  # ~1 month of daily records, since the run only started 2016-01-01


def test_price_history_as_of_empty_records_returns_empty():
    assert _piv_at("2020-01-01", []).get_price_history_as_of("electricity") == []


def test_price_history_as_of_electricity_and_gas_independent():
    """Two different commodities built into the SAME shared log (as
    run_phase2b.py does once per run) must not leak into each other."""
    elec = _daily_records("2016-01-01", 50, price_start=50.0)
    gas = _daily_records("2020-01-01", 50, price_start=20.0)
    piv = _piv_at("2016-01-20", elec, gas)
    elec_hist = piv.get_price_history_as_of("electricity")
    assert all(r["settlementDate"].startswith("2016") for r in elec_hist)
    # gas history at this decision_time is empty -- gas prices only start 2020,
    # after this 2016 decision could have known them.
    gas_hist = piv.get_price_history_as_of("gas")
    assert gas_hist == []


# ── the treasury drawdown register (2026-08-24) ─────────────────────────────────────────────

def test_the_run_emits_a_treasury_drawdown_register(_phase2b_result_2017):
    """`treasury_cash_balance_gbp` is a PORTFOLIO running total, stamped on each record as the
    term loop produces it. The report used to rebuild its drawdown path by re-sorting the
    finished book into (date, period) order, which interleaves balances from different points in
    that loop and manufactured 6,747 drawdown events in a real 2017 that had none.

    The run now folds the path while that order is still the one it is being read in. This is the
    emitting half of the seam; `tests/saas/reporting/test_annual_report.py` holds the reading
    half. Both are needed: a rename on either side is silent, because the report's read is a
    `.get` that would quietly fall back to the book.

    WHAT THIS TEST ASSERTS AND WHAT IT NO LONGER TRIES TO (2026-08-28, repairing the red
    diagnosed in `docs/observability/RED_DISPOSITION_TWO_REDS_THAT_REFUSED_THE_COMPOSITE_LAND_2026-08-27.md`).
    This test used to end in a null control asserting that at least one year in the window
    distinguishes accumulation order from date order. That control was RIGHT and it was firing:
    measured on this fixture, the treasury runs 250,000 -> 254,242 and there is no peak-to-trough
    fall of `DRAWDOWN_THRESHOLD_PCT` (10%) anywhere in it, so the book has ZERO drawdown events
    under either ordering and the containment loop below iterates over nothing. The window was
    truncated from the full decade to 2016-2017 as a throughput fix, and that truncation removed
    every year in which the treasury actually draws down -- converting a real control into a
    vacuous one, which is exactly what the null control existed to announce.

    The legal repairs were: widen this window until it contains a drawdown (paying a multi-minute
    run in the hot path, and requiring a search over windows to find one), or move the
    ordering-discrimination property onto a book CONSTRUCTED to contain the drawdowns, driven
    through the same production seam. The second was taken:
    `test_the_register_sees_a_drawdown_the_daily_book_cannot` below holds the containment
    property, the strictly-more property and the null control, on a book where all three can
    fire, in milliseconds. What stays here is what this expensive fixture can still genuinely
    witness: that a REAL run emits the register at all, that it is strictly richer than a walk of
    its own retained book, and that the fold is wired. Lowering the 10% threshold, deleting the
    null control or excluding this file would each have weakened a control that was telling the
    truth.
    """
    from saas.reporting.annual_report import (
        _drawdown_events_by_year,
        _treasury_path_from_book,
    )

    result = _phase2b_result_2017
    register = result["treasury_drawdown_path"]
    assert register, "the run emitted no drawdown register at all"

    all_records = result["all_records"]

    # THE ORACLE CHANGED WHEN THE FOLD WAS WIRED (2026-08-24), and it had to. This used to
    # assert `register == TreasuryDrawdown().add(all_records).points()` -- a rebuild from the
    # retained book -- which was a sound oracle only while that book held every half-hour. It
    # now holds DAILY rows (simulation/settlement_daily.py), so a rebuild from it is a strictly
    # coarser path and can no longer reproduce a per-period register BY CONSTRUCTION. That is
    # not the register failing; it is the register's entire reason for existing: a drawdown that
    # opens and closes inside one day is invisible in daily closes.
    #
    # So the property asserted is the one that survives, and it is the one that matters:
    # THE REGISTER MAY SEE MORE THAN THE BOOK, NEVER LESS.
    book_path = _treasury_path_from_book(all_records)
    reg_events = _drawdown_events_by_year(register)
    book_events = _drawdown_events_by_year(book_path)
    # Vacuous on THIS window by measurement (see the docstring), and kept anyway: it costs
    # nothing and becomes live the moment anyone widens the fixture. The discriminating version
    # is the constructed-book test below, which is where a reader should look for the proof.
    for year, events in book_events.items():
        for event in events:
            assert _drawdown_identity(event) in [
                _drawdown_identity(e) for e in reg_events.get(year, [])
            ], (
                "the daily book finds a {} drawdown the per-period register missed -- the "
                "register is being fed somewhere other than the single point `all_records` is "
                "extended, or it is dropping turning points".format(year))
    assert len(register) > len(book_path), (
        "the register is no larger than a walk of the daily book, so it is not carrying the "
        "half-hourly detail it exists to carry")

    # The book really is daily now, or the assertions above are comparing a thing to itself.
    assert any(r.get("settlement_periods_folded", 1) > 1 for r in all_records), (
        "no record in the retained book is a fold of several periods -- the fold is not wired, "
        "and this test is no longer testing what it says it is")


def _drawdown_identity(event: dict) -> tuple:
    """A drawdown event's IDENTITY, which is not the whole dict.

    `_drawdown_events_by_year` stamps each event with `sequence`, its position in the ONE walk
    that produced it. That is a property of the walk, not of the swing: the register and the
    daily book are two different walks, and the containment property asserted above --
    "the register may see more than the book, never less" -- entails that the register's
    sequences shift whenever it sees an extra event the book cannot. Comparing whole dicts
    therefore contradicts the property it is written to check, and would red on a register that
    is behaving exactly as designed. The swing itself is (peak, trough, depth).
    """
    return (event["peak_gbp"], event["trough_gbp"], event["drawdown_pct"])


#: One term of a constructed portfolio: `(day, period, balance)` triples, half-hourly, in the
#: order the term loop produces them. Kept as data so a mutation can be aimed at one number.
_TERM_A = [
    ("2020-01-01", 1, 100_000.0), ("2020-01-01", 2, 100_000.0),
    ("2020-01-01", 3, 100_000.0), ("2020-01-01", 4, 100_000.0),
    # A 15% dip that opens AND closes inside 2020-01-02: the day's close is 100,500, so a reader
    # of daily rows cannot see it at all. This is the drawdown the register exists for.
    ("2020-01-02", 1, 100_000.0), ("2020-01-02", 2, 85_000.0),
    ("2020-01-02", 3, 88_000.0), ("2020-01-02", 4, 100_500.0),
    ("2020-01-03", 1, 100_500.0), ("2020-01-03", 2, 101_000.0),
    ("2020-01-03", 3, 101_500.0), ("2020-01-03", 4, 102_000.0),
]

#: The SECOND term, settled after the whole of the first, over the SAME three days -- which is
#: what makes date-order re-sorting interleave two customers' balances and is the defect the
#: register was built against. Carries a 16.7% drawdown that spans days, so the daily book can
#: see this one.
_TERM_B = [
    ("2020-01-01", 1, 102_000.0), ("2020-01-01", 2, 101_000.0),
    ("2020-01-01", 3, 95_000.0), ("2020-01-01", 4, 90_000.0),
    ("2020-01-02", 1, 88_000.0), ("2020-01-02", 2, 87_000.0),
    ("2020-01-02", 3, 86_000.0), ("2020-01-02", 4, 85_000.0),
    ("2020-01-03", 1, 90_000.0), ("2020-01-03", 2, 95_000.0),
    ("2020-01-03", 3, 105_000.0), ("2020-01-03", 4, 110_000.0),
]


def _constructed_term(customer_id: str, rows) -> list[dict]:
    return [
        {
            "customer_id": customer_id,
            "commodity": "electricity",
            "settlement_date": day,
            "settlement_period": period,
            "treasury_cash_balance_gbp": balance,
        }
        for day, period, balance in rows
    ]


def test_the_register_sees_a_drawdown_the_daily_book_cannot():
    """The discriminating half of the register's contract, on a book built to contain drawdowns.

    Driven through the PRODUCTION seam, not a re-implementation of it: `run_phase2b.main` feeds
    `treasury_drawdown.add(settled_this_term)` and `all_records.extend(fold_to_days(...))` from
    the same per-period list, once per term, and that is exactly what this does. What it does not
    pay for is a simulated year -- which is the whole reason the expensive fixture above could
    not host these assertions once its window was truncated past the last real drawdown.
    """
    from saas.reporting.annual_report import (
        _drawdown_events,
        _drawdown_events_by_year,
        _treasury_path_from_book,
    )
    from simulation.settlement_daily import TreasuryDrawdown, fold_to_days

    treasury_drawdown = TreasuryDrawdown()
    all_records: list[dict] = []
    for customer_id, rows in (("C_A", _TERM_A), ("C_B", _TERM_B)):
        term = _constructed_term(customer_id, rows)
        treasury_drawdown.add(term)
        all_records.extend(fold_to_days(term))

    register = treasury_drawdown.points()
    book_path = _treasury_path_from_book(all_records)
    reg_events = _drawdown_events_by_year(register)
    book_events = _drawdown_events_by_year(book_path)

    # The population is non-empty on BOTH sides, so every assertion below has something to bite
    # on. Asserted, not assumed: this is the exact condition the truncated fixture window failed.
    assert book_events.get("2020"), "the constructed book contains no drawdown to contain"
    assert reg_events.get("2020"), "the constructed register contains no drawdown at all"

    # THE REGISTER MAY SEE MORE THAN THE BOOK, NEVER LESS -- the containment half.
    reg_identities = [_drawdown_identity(e) for e in reg_events["2020"]]
    for event in book_events["2020"]:
        assert _drawdown_identity(event) in reg_identities, (
            "the daily book finds a drawdown the per-period register missed: {}".format(event))

    # ...and the MORE half, which containment alone cannot express: the 2020-01-02 dip opens and
    # closes inside one day, so it is present in the register and absent from the daily closes.
    intraday = (100_000.0, 85_000.0, 0.15)
    assert intraday in reg_identities, (
        "the register lost the intraday drawdown, which is the only thing it exists to carry")
    assert intraday not in [_drawdown_identity(e) for e in book_events["2020"]], (
        "the daily book can see the intraday dip, so this fixture is not testing the gap "
        "between the two and the assertion above proves nothing")
    assert len(register) > len(book_path)

    # The fold really happened, or the two paths are the same object under two names.
    assert any(r.get("settlement_periods_folded", 1) > 1 for r in all_records)

    # NULL CONTROL: on a book settled term-by-term the two orderings genuinely disagree, so the
    # containment above is a fact about the register rather than about a book whose order happens
    # not to matter. This is the assertion the 2016-2017 fixture could no longer make.
    accumulation = _drawdown_events([r["treasury_cash_balance_gbp"] for r in all_records])
    re_sorted = _drawdown_events([
        r["treasury_cash_balance_gbp"]
        for r in sorted(all_records, key=lambda r: (r["settlement_date"],
                                                    r.get("settlement_period") or 0))
    ])
    assert re_sorted != accumulation, (
        "accumulation order and date order agree on this book, so it cannot distinguish the "
        "register from the re-sorting defect it was built against")
