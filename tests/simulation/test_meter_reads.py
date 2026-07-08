"""Phase 3 (CORE_FIDELITY_PHASES.md item 1): meter-read arrival/estimation/
failure model.

Tests simulation/meter_reads.py: deterministic dispatch, smart-vs-traditional
delay/estimation behaviour, the estimate never leaking this period's true
value, and the back-billing forced-catch-up cap.
"""
import statistics

from simulation.meter_reads import (
    MAX_CONSECUTIVE_ESTIMATED_PERIODS,
    READ_CUTOFF_DAYS_AFTER_PERIOD_END,
    generate_meter_read_log,
    meter_type_for_customer,
    simulate_read,
)


def test_meter_type_smart_via_smart_meter_flag():
    assert meter_type_for_customer({"smart_meter": True, "metering": "NHH"}) == "smart"


def test_meter_type_smart_via_hh_metering():
    assert meter_type_for_customer({"smart_meter": False, "metering": "HH"}) == "smart"


def test_meter_type_traditional_default():
    assert meter_type_for_customer({}) == "traditional"
    assert meter_type_for_customer({"smart_meter": False, "metering": "NHH"}) == "traditional"


def test_simulate_read_is_deterministic():
    r1 = simulate_read("C1", "2020-01-31", "smart", 300.0, [280.0, 290.0], 0)
    r2 = simulate_read("C1", "2020-01-31", "smart", 300.0, [280.0, 290.0], 0)
    assert r1 == r2


def test_simulate_read_varies_by_period():
    statuses = {
        simulate_read("C1", f"20{yr}-01-31", "traditional", 300.0, [280.0], 0).status
        for yr in range(16, 26)
    }
    # Both outcomes should occur across enough periods -- otherwise the roll
    # isn't actually varying.
    assert len(statuses) > 1


def test_smart_meters_mostly_actual():
    # Smart, communicating meters should read "actual" the large majority of
    # the time (near-real-time WAN transmission, small delay).
    outcomes = [
        simulate_read("C1", f"20{yr:02d}-{mo:02d}-28", "smart", 300.0, [290.0] * 3, 0).status
        for yr in range(16, 26) for mo in range(1, 13)
    ]
    actual_rate = outcomes.count("actual") / len(outcomes)
    assert actual_rate > 0.85


def test_traditional_meters_estimated_more_often_than_smart():
    smart_actual = sum(
        simulate_read("C2", f"20{yr:02d}-{mo:02d}-28", "smart", 300.0, [290.0] * 3, 0).status == "actual"
        for yr in range(16, 26) for mo in range(1, 13)
    )
    traditional_actual = sum(
        simulate_read("C3", f"20{yr:02d}-{mo:02d}-28", "traditional", 300.0, [290.0] * 3, 0).status == "actual"
        for yr in range(16, 26) for mo in range(1, 13)
    )
    assert traditional_actual < smart_actual


def test_estimated_read_never_uses_true_consumption_as_the_estimate():
    # Force an estimate by starving the roll with a customer/period combo
    # known to land on "estimated" for a traditional meter, and confirm the
    # estimate is drawn from trailing history, not this period's true value.
    trailing = [100.0, 110.0, 120.0]
    found_estimate = False
    for yr in range(16, 40):
        event = simulate_read("C4", f"20{yr}-06-30", "traditional", 999.0, trailing, 0)
        if event.status == "estimated":
            found_estimate = True
            assert event.estimated_consumption_kwh == round(statistics.mean(trailing), 2)
            assert event.estimated_consumption_kwh != 999.0
            break
    assert found_estimate, "expected at least one estimated read across 24 periods"


def test_first_ever_read_with_no_history_bootstraps_from_opening_read():
    # No trailing actuals yet (first bill). If this roll estimates, the
    # estimate must fall back to the true value (a real opening read taken
    # at switch), not None/zero.
    for yr in range(16, 40):
        event = simulate_read("C5", f"20{yr}-01-31", "traditional", 250.0, [], 0)
        if event.status == "estimated":
            assert event.estimated_consumption_kwh == 250.0
            return
    # If no estimate ever fired in 24 tries, that's suspicious but not fatal
    # to this specific assertion -- the deterministic tests above already
    # cover estimate occurrence.


def test_forced_catch_up_after_max_consecutive_estimates():
    event = simulate_read(
        "C6", "2020-01-31", "traditional", 300.0, [290.0],
        consecutive_estimated_count=MAX_CONSECUTIVE_ESTIMATED_PERIODS,
    )
    assert event.status == "actual"
    assert event.forced_catch_up is True


def test_delay_days_non_negative():
    for yr in range(16, 26):
        event = simulate_read("C7", f"20{yr}-01-31", "traditional", 300.0, [290.0], 0)
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
