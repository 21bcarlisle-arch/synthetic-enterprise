from __future__ import annotations
import random
from datetime import date
from simulation.household import IncomeStress
from simulation.payment_timing import generate_payment_record, stress_bad_debt_multiplier

DUE = date(2022, 3, 15)
AMOUNT = 120.00

def _make_rng(seed=42): return random.Random(seed)
def _gen_n(n, stress, seed=0):
    rng = random.Random(seed)
    return [generate_payment_record('C1', DUE, AMOUNT, stress, rng) for _ in range(n)]

def test_LOW_stress_delay_in_7_14_window():
    late = [r for r in _gen_n(200, IncomeStress.LOW, seed=1) if r['result'] == 'LATE']
    assert late
    for r in late: assert 7 <= (r['payment_date'] - DUE).days <= 14

def test_MODERATE_stress_delay_in_14_45_window():
    late = [r for r in _gen_n(200, IncomeStress.MODERATE, seed=2) if r['result'] == 'LATE']
    assert late
    for r in late: assert 14 <= (r['payment_date'] - DUE).days <= 45

def test_HIGH_stress_delay_in_30_90_window():
    late = [r for r in _gen_n(200, IncomeStress.HIGH, seed=3) if r['result'] == 'LATE']
    assert late
    for r in late: assert 30 <= (r['payment_date'] - DUE).days <= 90

def test_LOW_dd_failure_rare():
    assert sum(1 for r in _gen_n(100, IncomeStress.LOW, seed=10) if r['result'] == 'DD_FAILED') <= 10

def test_HIGH_dd_failure_common():
    assert sum(1 for r in _gen_n(100, IncomeStress.HIGH, seed=20) if r['result'] == 'DD_FAILED') >= 20

def test_generate_payment_record_fields_present():
    r = generate_payment_record('C1', DUE, AMOUNT, IncomeStress.LOW, _make_rng())
    for key in ('customer_id', 'due_date', 'result', 'payment_date', 'amount_gbp', 'amount_paid'): assert key in r

def test_dd_failed_has_no_payment_date():
    rng = random.Random(0)
    for _ in range(1000):
        r = generate_payment_record('C1', DUE, AMOUNT, IncomeStress.HIGH, rng)
        if r['result'] == 'DD_FAILED':
            assert r['payment_date'] is None; return
    raise AssertionError('No DD_FAILED')

def test_on_time_has_payment_date_not_none():
    rng = random.Random(0)
    for _ in range(1000):
        r = generate_payment_record('C1', DUE, AMOUNT, IncomeStress.LOW, rng)
        if r['result'] == 'ON_TIME':
            assert r['payment_date'] is not None; return
    raise AssertionError('No ON_TIME')

def test_late_payment_date_after_due_date():
    rng = random.Random(0)
    for _ in range(500):
        r = generate_payment_record('C1', DUE, AMOUNT, IncomeStress.HIGH, rng)
        if r['result'] == 'LATE':
            assert r['payment_date'] > DUE; return
    raise AssertionError('No LATE')

def test_stress_multiplier_LOW_is_1_0(): assert stress_bad_debt_multiplier(IncomeStress.LOW) == 1.0
def test_stress_multiplier_MODERATE_is_1_5(): assert stress_bad_debt_multiplier(IncomeStress.MODERATE) == 1.5
def test_stress_multiplier_HIGH_is_3_0(): assert stress_bad_debt_multiplier(IncomeStress.HIGH) == 3.0
def test_stress_multiplier_None_is_1_0(): assert stress_bad_debt_multiplier(None) == 1.0
def test_high_stress_bad_debt_higher_than_low_stress(): assert stress_bad_debt_multiplier(IncomeStress.HIGH) > stress_bad_debt_multiplier(IncomeStress.LOW)
def test_sme_customer_None_multiplier(): assert stress_bad_debt_multiplier(None) == 1.0

def test_payment_records_accumulate():
    rng = _make_rng(99)
    records = [generate_payment_record(f'C{i}', DUE, AMOUNT, IncomeStress.LOW, rng) for i in range(5)]
    assert len(records) == 5 and all('result' in r for r in records)

def test_seeded_rng_deterministic():
    r1 = generate_payment_record('C1', DUE, AMOUNT, IncomeStress.MODERATE, random.Random(7))
    r2 = generate_payment_record('C1', DUE, AMOUNT, IncomeStress.MODERATE, random.Random(7))
    assert r1['result'] == r2['result'] and r1['payment_date'] == r2['payment_date']

def test_income_stress_LOW_mostly_on_time():
    assert sum(1 for r in _gen_n(200, IncomeStress.LOW, seed=5) if r['result'] == 'ON_TIME') / 200 >= 0.85

def test_income_stress_HIGH_mostly_not_on_time():
    assert sum(1 for r in _gen_n(200, IncomeStress.HIGH, seed=6) if r['result'] in ('LATE', 'DD_FAILED')) / 200 >= 0.40

def test_MODERATE_between_LOW_and_HIGH_on_time_rate():
    low = sum(1 for r in _gen_n(300, IncomeStress.LOW, seed=7) if r['result'] == 'ON_TIME') / 300
    mod = sum(1 for r in _gen_n(300, IncomeStress.MODERATE, seed=7) if r['result'] == 'ON_TIME') / 300
    high = sum(1 for r in _gen_n(300, IncomeStress.HIGH, seed=7) if r['result'] == 'ON_TIME') / 300
    assert high <= mod <= low

def test_payment_date_is_date_type():
    rng = random.Random(0)
    for _ in range(500):
        r = generate_payment_record('C1', DUE, AMOUNT, IncomeStress.HIGH, rng)
        if r['result'] == 'LATE' and r['payment_date'] is not None:
            assert isinstance(r['payment_date'], date); return
    raise AssertionError('No LATE')

def test_amount_paid_zero_when_dd_failed():
    rng = random.Random(0)
    for _ in range(1000):
        r = generate_payment_record('C1', DUE, AMOUNT, IncomeStress.HIGH, rng)
        if r['result'] == 'DD_FAILED':
            assert r['amount_paid'] == 0.0; return
    raise AssertionError('No DD_FAILED')

def test_amount_paid_equals_due_when_not_partial():
    rng = random.Random(0)
    for _ in range(200):
        r = generate_payment_record('C1', DUE, AMOUNT, IncomeStress.LOW, rng)
        if r['result'] in ('ON_TIME', 'LATE'):
            assert r['amount_paid'] == AMOUNT; return
    raise AssertionError('No paid record')

def test_two_customers_independent():
    rng = random.Random(42)
    r1 = generate_payment_record('C1', DUE, AMOUNT, IncomeStress.HIGH, rng)
    r2 = generate_payment_record('C2', DUE, AMOUNT, IncomeStress.HIGH, rng)
    assert r1['customer_id'] == 'C1' and r2['customer_id'] == 'C2'
    assert isinstance(r1, dict) and isinstance(r2, dict)

def test_resi_job_loss_shows_payment_deterioration():
    from simulation.household import BoilerAge, BuildEra, HeatingSystem, Household, InsulationLevel, PropertyType
    from simulation.life_events import LifeEvent, apply_events
    hh = Household(
        customer_id='TEST1', property_type=PropertyType.TERRACED, build_era=BuildEra.ERA_1965_1980,
        epc_rating='D', bedrooms=3, heating_system=HeatingSystem.GAS_BOILER_COMBI,
        boiler_age=BoilerAge.MID, has_solar=False, solar_kwp=0.0, solar_install_year=None,
        has_battery=False, battery_kwh=0.0, has_ev=False, ev_charger_kw=0.0,
        has_smart_meter=False, smart_meter_install_year=None, insulation=InsulationLevel.PARTIAL,
        has_driveway=True, roof_aspect='south', income_stress=IncomeStress.LOW,
    )
    assert stress_bad_debt_multiplier(hh.income_stress) == 1.0
    hh2 = apply_events(hh, [LifeEvent(customer_id='TEST1', event_date='2020-03-01', event_type='job_loss', payload={})])
    assert hh2.income_stress == IncomeStress.HIGH
    assert stress_bad_debt_multiplier(hh2.income_stress) == 3.0
