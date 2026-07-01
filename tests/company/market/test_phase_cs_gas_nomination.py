"""Phase CS: Gas Nomination Register tests (UNC)."""
import pytest
from datetime import date
from company.market.gas_nomination_register import (
    GasNominationRegister, NominationStatus, ImbalanceDirection,
    GasNominationRecord,
)

_D = date(2022, 1, 10)


def _settled_reg(nominated=100_000, actual=100_000):
    r = GasNominationRegister()
    r.nominate(_D, nominated)
    r.settle(_D, actual)
    return r


# 1. nominate creates INITIAL status record
def test_nominate_initial():
    r = GasNominationRegister()
    rec = r.nominate(_D, 50_000)
    assert rec.status == NominationStatus.INITIAL
    assert rec.nominated_kwh == 50_000


# 2. revise updates effective_nominated_kwh
def test_revise_updates():
    r = GasNominationRegister()
    r.nominate(_D, 50_000)
    rec = r.revise(_D, 60_000)
    assert rec.effective_nominated_kwh == 60_000
    assert rec.status == NominationStatus.REVISED


# 3. settle records actual and SETTLED status
def test_settle():
    r = GasNominationRegister()
    r.nominate(_D, 100_000)
    rec = r.settle(_D, 95_000)
    assert rec.actual_consumed_kwh == 95_000
    assert rec.status == NominationStatus.SETTLED


# 4. imbalance_kwh = nominated - actual
def test_imbalance_kwh():
    r, rec = GasNominationRegister(), None
    r.nominate(_D, 100_000)
    rec = r.settle(_D, 90_000)
    rec2 = r.settled_records[0]
    assert rec2.imbalance_kwh == 10_000  # long by 10k


# 5. direction BALANCED within tolerance
def test_direction_balanced():
    r = _settled_reg(100_000, 97_000)  # -3% within ±5%
    assert r.settled_records[0].direction == ImbalanceDirection.BALANCED


# 6. direction SHORT when under-nominated
def test_direction_short():
    r = _settled_reg(100_000, 120_000)  # nominated < actual → SHORT
    assert r.settled_records[0].direction == ImbalanceDirection.SHORT


# 7. direction LONG when over-nominated
def test_direction_long():
    r = _settled_reg(120_000, 100_000)  # nominated > actual → LONG
    assert r.settled_records[0].direction == ImbalanceDirection.LONG


# 8. out_of_tolerance_days filters correctly
def test_out_of_tolerance():
    r = GasNominationRegister()
    r.nominate(date(2022, 1, 1), 100_000)
    r.settle(date(2022, 1, 1), 100_000)   # balanced
    r.nominate(date(2022, 1, 2), 100_000)
    r.settle(date(2022, 1, 2), 150_000)   # SHORT -33%
    assert len(r.out_of_tolerance_days) == 1


# 9. short_days and long_days filtered
def test_short_long_filtered():
    r = GasNominationRegister()
    r.nominate(date(2022, 1, 1), 100_000); r.settle(date(2022, 1, 1), 150_000)  # SHORT
    r.nominate(date(2022, 1, 2), 150_000); r.settle(date(2022, 1, 2), 100_000)  # LONG
    assert len(r.short_days) == 1
    assert len(r.long_days) == 1


# 10. mean_imbalance_pct returns None for empty
def test_mean_imbalance_empty():
    r = GasNominationRegister()
    assert r.mean_imbalance_pct is None


# 11. mean_imbalance_pct average calculation
def test_mean_imbalance_calc():
    r = GasNominationRegister()
    r.nominate(date(2022, 1, 1), 110_000); r.settle(date(2022, 1, 1), 100_000)  # +10%
    r.nominate(date(2022, 1, 2), 90_000); r.settle(date(2022, 1, 2), 100_000)   # -10%
    mean = r.mean_imbalance_pct
    assert abs(mean - 0.0) < 0.01


# 12. nomination_summary contains key fields
def test_nomination_summary():
    r = _settled_reg(150_000, 100_000)  # LONG out of tolerance
    summary = r.nomination_summary()
    assert "Gas Nomination" in summary
    assert "UNC" in summary
    assert "1" in summary   # out of tolerance


# --- Phase LZ depth tests ---

def test_gas_day_stored():
    from datetime import date as _date
    reg = GasNominationRegister('P1')
    d = _date(2022, 3, 15)
    rec = reg.nominate(d, 10000.0)
    assert rec.gas_day == d


def test_portfolio_id_stored():
    reg = GasNominationRegister('PORT1')
    rec = reg.nominate(date(2022, 3, 15), 10000.0)
    assert rec.portfolio_id == 'PORT1'


def test_nominated_kwh_stored():
    reg = GasNominationRegister()
    rec = reg.nominate(date(2022, 3, 15), 50000.0)
    assert rec.nominated_kwh == pytest.approx(50000.0)


def test_actual_consumed_none_before_settle():
    reg = GasNominationRegister()
    rec = reg.nominate(date(2022, 3, 15), 10000.0)
    assert rec.actual_consumed_kwh is None


def test_status_default_initial():
    reg = GasNominationRegister()
    rec = reg.nominate(date(2022, 3, 15), 10000.0)
    assert rec.status == NominationStatus.INITIAL


def test_revised_nominated_none_before_revise():
    reg = GasNominationRegister()
    rec = reg.nominate(date(2022, 3, 15), 10000.0)
    assert rec.revised_nominated_kwh is None


def test_imbalance_none_before_settle():
    reg = GasNominationRegister()
    rec = reg.nominate(date(2022, 3, 15), 10000.0)
    assert rec.imbalance_kwh is None


def test_direction_none_before_settle():
    reg = GasNominationRegister()
    rec = reg.nominate(date(2022, 3, 15), 10000.0)
    assert rec.direction is None


def test_is_in_tolerance_none_before_settle():
    reg = GasNominationRegister()
    rec = reg.nominate(date(2022, 3, 15), 10000.0)
    assert rec.is_in_tolerance is None


def test_nominate_returns_gas_nomination_record():
    reg = GasNominationRegister()
    result = reg.nominate(date(2022, 3, 15), 10000.0)
    assert isinstance(result, GasNominationRecord)
