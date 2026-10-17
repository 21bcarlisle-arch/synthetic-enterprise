"""Phase 3 (CORE_FIDELITY_PHASES.md item 1): meter-read arrival/estimation/
failure model.

Tests simulation/meter_reads.py: deterministic dispatch, smart-vs-traditional
delay/estimation behaviour, a feed that reports status and no figure to bill
(the estimate is the company's, D48 slice 4), and (W2_36) a read process whose absence persists and has no forced
read at 12 months.
"""
import pytest

import simulation.meter_reads as mr
from simulation.meter_reads import (
    NO_READ_12M_SHARE,
    READ_CUTOFF_DAYS_AFTER_PERIOD_END,
    generate_meter_read_log,
    is_hard_to_read,
    is_not_in_smart_mode,
    meter_type_for_customer,
    simulate_final_read,
    simulate_read,
    solve_easy_rate,
)


def test_meter_type_smart_via_smart_meter_flag():
    assert meter_type_for_customer({"smart_meter": True, "metering": "NHH"}) == "smart"


def test_meter_type_smart_via_hh_metering():
    assert meter_type_for_customer({"smart_meter": False, "metering": "HH"}) == "smart"


def test_meter_type_traditional_default():
    assert meter_type_for_customer({}) == "traditional"
    assert meter_type_for_customer({"smart_meter": False, "metering": "NHH"}) == "traditional"


def test_simulate_read_is_deterministic():
    r1 = simulate_read("C1", "2020-01-31", "smart", 300.0, 0)
    r2 = simulate_read("C1", "2020-01-31", "smart", 300.0, 0)
    assert r1 == r2


def test_simulate_read_varies_by_period():
    statuses = {
        simulate_read("C1", f"20{yr}-01-31", "traditional", 300.0, 0).status
        for yr in range(16, 26)
    }
    # Both outcomes should occur across enough periods -- otherwise the roll
    # isn't actually varying.
    assert len(statuses) > 1


def test_smart_meters_mostly_actual():
    # Smart, communicating meters should read "actual" the large majority of
    # the time (near-real-time WAN transmission, small delay).
    outcomes = [
        simulate_read("C1", f"20{yr:02d}-{mo:02d}-28", "smart", 300.0, 0).status
        for yr in range(16, 26) for mo in range(1, 13)
    ]
    actual_rate = outcomes.count("actual") / len(outcomes)
    assert actual_rate > 0.85


def test_traditional_meters_estimated_more_often_than_smart():
    # Over a population: one smart id may hold traditional mode for life and read like one.
    def actual(meter_type):
        return sum(
            simulate_read(f"C{meter_type}{i}", f"20{yr:02d}-{mo:02d}-28", meter_type, 300.0, 0)
            .status == "actual"
            for i in range(50) for yr in range(16, 26) for mo in range(1, 13))
    assert actual("traditional") < actual("smart")


def test_the_feed_reports_status_and_never_a_figure_to_bill():
    """Defect caught (D48 slice 4): the world making the supplier's estimate. It used to send a
    trailing mean, and for an opening period this period's TRUE use under an estimate's name.
    Both arms in one statement, so a feed that never estimates cannot pass vacuously."""
    events = [simulate_read("C4", f"20{yr}-06-30", "traditional", 999.0, 0) for yr in range(16, 60)]
    estimated = [e for e in events if e.status == "estimated"]
    assert estimated and len(estimated) < len(events), "both statuses must be reachable"
    assert all(e.estimated_consumption_kwh is None for e in events), estimated[:3]


def test_a_long_estimated_run_does_not_force_a_read():
    """Defect caught: the world enforcing SLC 21B's read DUTY (an effort) as a guaranteed read at
    12 months, which made the 12-month back-billing limit unreachable."""
    for yr in range(16, 26):
        args = ("C6", f"20{yr}-01-31", "traditional", 300.0)
        assert simulate_read(*args, 0).status == simulate_read(*args, 500).status
        assert simulate_read(*args, 500).forced_catch_up is False


def test_a_closing_read_is_actual_only_where_the_world_has_a_reason(monkeypatch):
    """Defect caught (2026-10-17): every closing read answered actual, so the estimate at a
    move-out or switch never reached a final bill. A smart meter in smart mode is read remotely
    on the day; a traditional meter, or a smart one out of smart mode, gets the period's ordinary
    read; a customer-given read fires only once its share is sourced. One partition, so a rule
    that answers actual always, or never, cannot pass."""
    smart_on = next(f"S{i}" for i in range(500) if not is_not_in_smart_mode(f"S{i}"))
    smart_off = next(f"S{i}" for i in range(500) if is_not_in_smart_mode(f"S{i}"))
    periods = [f"20{yr}-{m:02d}-28" for yr in range(16, 26) for m in (1, 7)]

    def closing(cid, meter, period):
        return simulate_final_read(cid, period, meter, 300.0, 3)

    assert all(closing(smart_on, "smart", p).status == "actual" for p in periods)
    late = next(f"2020-{m:02d}-{d:02d}" for m in range(1, 13) for d in range(1, 29)
                if simulate_read(smart_on, f"2020-{m:02d}-{d:02d}", "smart", 300.0, 3).status
                == "estimated")
    assert closing(smart_on, "smart", late).status == "actual", "a late remote read stays late"
    for cid, meter in (("T1", "traditional"), (smart_off, "smart")):
        events = [closing(cid, meter, p) for p in periods]
        assert events == [simulate_read(cid, p, meter, 300.0, 3) for p in periods]
        assert any(e.status == "estimated" for e in events), (cid, "no estimate reached")
        assert all(e.consecutive_estimated_count == 4 for e in events if e.status == "estimated")

    assert mr.CLOSING_READ_CUSTOMER_GIVEN_SHARE is None and mr.CLOSING_READ_CUSTOMER_GIVEN_GAP
    monkeypatch.setattr(mr, "CLOSING_READ_CUSTOMER_GIVEN_SHARE", 1.0)
    given = closing("T1", "traditional", periods[0])
    assert (given.status, given.delay_days, given.forced_catch_up) == ("actual", 0, True)


def _traditional_history(cid, months=60):
    statuses, consecutive = [], 0
    for m in range(months):
        event = simulate_read(cid, f"{2016 + m // 12}-{m % 12 + 1:02d}-28", "traditional",
                              300.0, consecutive)
        statuses.append(event.status == "actual")
        consecutive = event.consecutive_estimated_count
    return statuses


def test_the_read_process_reproduces_the_registered_12_month_no_read_share():
    """Defect caught: a read rate typed in the module rather than solved to the published moment
    (the old 1/6 a month, forced at 12, left 0.048 unread for a year, an artefact of the cap)."""
    windows = unread = 0
    for i in range(1500):
        history = _traditional_history(f"CAL{i}")
        for end in range(24, len(history)):
            windows += 1
            unread += not any(history[end - 12:end])
    assert abs(unread / windows - NO_READ_12M_SHARE) < 0.01


def test_both_read_classes_are_reached_and_the_hard_class_reads_less():
    """Partition control: the hard-to-read class must be reachable before its rate means anything,
    and a spell unread for two years must be possible (Ofgem's complaint median is 24 months)."""
    cids = [f"P{i}" for i in range(3000)]
    hard = [c for c in cids if is_hard_to_read(c)]
    easy = [c for c in cids if not is_hard_to_read(c)]
    assert hard and easy
    hard_rate = sum(sum(_traditional_history(c)) for c in hard) / (60 * len(hard))
    easy_rate = sum(sum(_traditional_history(c)) for c in easy[:300]) / (60 * 300)
    assert hard_rate < easy_rate / 3
    assert any(not any(_traditional_history(c)[:24]) for c in hard)


def test_the_easy_rate_solver_refuses_a_hard_class_that_alone_exceeds_the_target():
    with pytest.raises(ValueError, match="no easy-class rate"):
        solve_easy_rate(0.2, 0.07)
    assert 0.19 < solve_easy_rate(0.0, 0.07) < 0.21  # 0.8 ** 12 is about 0.07


def test_the_read_process_is_read_from_the_assumption_register():
    assert mr.PERSISTENT_UNREAD_SHARE == mr.assumption_toggle("q2_persistent_unread_share")
    assert mr.NO_READ_12M_SHARE == mr.assumption_toggle("q2_no_read_12m_share")
    assert mr.SMART_METER_NOT_COMMUNICATING_RATE == mr.assumption_toggle(
        "q6_smart_not_in_smart_mode_share")


def _year_unread(cid, meter_type):
    statuses = [simulate_read(cid, f"{2016 + m // 12}-{m % 12 + 1:02d}-28", meter_type, 300.0, 0)
                .status for m in range(60)]
    return any(all(s == "estimated" for s in statuses[k - 12:k]) for k in range(12, 60))


def test_a_smart_meter_out_of_smart_mode_stays_out_so_its_home_can_go_a_year_unread():
    """Defect caught: traditional mode drawn afresh each month (the register's Q6 row: it is a
    STATE). Drawn monthly at 0.10 no smart home ever went a year unread (measured 0.0000 of
    windows, against 0.0073 held). Partition first: both modes must be reachable."""
    cids = [f"SM{i}" for i in range(2000)]
    out = [c for c in cids if is_not_in_smart_mode(c)]
    in_mode = [c for c in cids if not is_not_in_smart_mode(c)]
    assert out and in_mode
    assert abs(len(out) / len(cids) - mr.SMART_METER_NOT_COMMUNICATING_RATE) < 0.02
    assert any(_year_unread(c, "smart") for c in out)
    assert not any(_year_unread(c, "smart") for c in in_mode[:300])


def test_delay_days_non_negative():
    for yr in range(16, 26):
        event = simulate_read("C7", f"20{yr}-01-31", "traditional", 300.0, 0)
        assert event.delay_days >= 0


def test_generate_meter_read_log_tracks_consecutive_estimates_per_customer():
    bills = [
        {"customer_id": "C8", "period_end": f"2020-{mo:02d}-28", "total_consumption_kwh": 300.0}
        for mo in range(1, 13)
    ]
    log = generate_meter_read_log(bills, {"C8": "traditional"})
    assert len(log) == 12
    assert all(entry["customer_id"] == "C8" for entry in log)
    # Running consecutive-estimate counter must reset to 0 immediately after
    # any actual read and increment across a genuine estimated streak.
    running = 0
    for entry in log:
        if entry["status"] == "actual":
            running = 0
            assert entry["consecutive_estimated_count"] == 0
        else:
            running += 1
            assert entry["consecutive_estimated_count"] == running


def test_generate_meter_read_log_multiple_customers_independent():
    bills = [
        {"customer_id": "C9", "period_end": "2020-01-31", "total_consumption_kwh": 300.0},
        {"customer_id": "C10", "period_end": "2020-01-31", "total_consumption_kwh": 400.0},
    ]
    log = generate_meter_read_log(bills, {"C9": "smart", "C10": "traditional"})
    by_cid = {entry["customer_id"]: entry for entry in log}
    assert by_cid["C9"]["meter_type"] == "smart"
    assert by_cid["C10"]["meter_type"] == "traditional"


def test_read_cutoff_constant_is_positive():
    assert READ_CUTOFF_DAYS_AFTER_PERIOD_END > 0


def _barred_and_long_share(monkeypatch, persistent_share, households=300, months=600):
    """Months more than 12 back at their catch-up read (what the 12-month back-billing limit bars),
    as a share of all months; and the share of those that sit in runs of 24 months or more."""
    monkeypatch.setattr(mr, "PERSISTENT_UNREAD_SHARE", persistent_share)
    monkeypatch.setattr(mr, "TRADITIONAL_ACTUAL_READ_PROBABILITY",
                        solve_easy_rate(persistent_share, NO_READ_12M_SHARE) / mr.on_time_share())
    barred = long_barred = 0
    for i in range(households):
        run = 0
        for m in range(months):
            event = simulate_read(f"SW{i}", f"{2016 + m // 12}-{m % 12 + 1:02d}-28", "traditional",
                                  300.0, run)
            if event.status == "actual":
                barred += max(0, run - 12)
                long_barred += max(0, run - 12) if run >= 24 else 0
            run = event.consecutive_estimated_count
    return barred / (households * months), long_barred / barred


def test_the_hard_to_read_share_moves_the_shape_of_back_bills_and_not_their_total(monkeypatch):
    """The register's Q2 verdict (DOESNT_MATTER for aggregates, MATTERS for the shape), measured.

    Defect caught: a hard-to-read share that changes how much energy the back-billing limit bars,
    which would make it decision-changing for pricing and the accrual. The second leg asserts the
    toggle moves SOMETHING, so an inert toggle cannot pass the invariance leg."""
    total_none, long_none = _barred_and_long_share(monkeypatch, 0.0)
    total_high, long_high = _barred_and_long_share(monkeypatch, 0.03)
    assert abs(total_high - total_none) < 0.008
    assert long_high > long_none + 0.1


# --- W2_36 theft at a premise (2026-10-16) ---------------------------------

def _theft_population(n=4000, months=120, **kw):
    return [mr.premise_theft_study(f"P{i}", [333.0] * months, **kw) for i in range(n)]


def test_a_premise_theft_starts_and_ends_and_the_stock_holds_at_the_registers_prevalence():
    # The rare branches first: a theft must be able to start mid-window and to end, or a chain
    # that never moves would hold the stock at its opening draw and pass the level check below.
    pop = _theft_population()
    starts = sum(1 for r in pop for a, b in zip(r["stealing"], r["stealing"][1:]) if not a and b)
    ends = sum(1 for r in pop for a, b in zip(r["stealing"], r["stealing"][1:]) if a and not b)
    assert starts and ends
    late = sum(r["stealing"][-1] for r in pop) / len(pop)
    mean = sum(sum(r["stealing"]) for r in pop) / (len(pop) * 120)
    se = (mr.THEFT_PREVALENCE * (1 - mr.THEFT_PREVALENCE) / len(pop)) ** 0.5
    assert abs(mean - mr.THEFT_PREVALENCE) < 3 * se
    assert abs(late - mr.THEFT_PREVALENCE) < 4 * se


def test_a_theft_month_registers_the_unhidden_share_and_any_other_month_registers_true_use():
    pop = _theft_population(n=2000, unregistered_share=0.4)
    theft = [(t, g) for r in pop for t, g, s in zip(r["true_kwh"], r["registered_kwh"], r["stealing"]) if s]
    honest = [(t, g) for r in pop for t, g, s in zip(r["true_kwh"], r["registered_kwh"], r["stealing"]) if not s]
    assert theft and honest
    assert all(g == pytest.approx(t * 0.6) for t, g in theft)
    assert all(g == t for t, g in honest)
    assert sum(r["stolen_kwh"] for r in pop) == pytest.approx(sum(t - g for t, g in theft))


def test_at_the_registers_default_a_theft_premise_registers_nothing_as_an_empty_home_does():
    # The IA's implied whole-use theft: the screen sees the same zero a B7 void shows.
    r = next(r for r in _theft_population(n=2000) if any(r["stealing"]))
    assert mr.THEFT_UNREGISTERED_SHARE == 1.0
    assert all(g == 0.0 for g, s in zip(r["registered_kwh"], r["stealing"]) if s)


def test_a_theft_that_hides_nothing_is_refused_by_name():
    with pytest.raises(ValueError, match="hides some use"):
        mr.premise_theft_study("P1", [333.0] * 12, unregistered_share=0.0)


def test_a_premises_theft_is_its_own_and_repeats():
    assert mr.premise_theft_months("P42", 60) == mr.premise_theft_months("P42", 60)
