"""A first term's 90-day price lookback is complete, or short with its record's declared reason --
never silently short. For gas, a silently short (empty) lookback turned out to be a point-in-time
leak: the fallback priced the term off the 90 days AFTER its start (removed in b8808f4ad). The
electricity record cannot reach back far enough (P305, `sim.system_prices_history.RECORD_START`), so
its short window is flagged, not filled.
"""

import datetime as dt
import json
from pathlib import Path

import pytest

from sim import gas_prices_history, system_prices_history
from sim.forward_curve import generate_forward_price, short_first_term_lookbacks
from simulation.live_population import FOUNDER_ACQUISITION_YEAR

LOOKBACK_DAYS = 90
FIRST_DAY = dt.date(FOUNDER_ACQUISITION_YEAR, 1, 1)
RECORDS = {
    "electricity": (system_prices_history.RECORD_START, system_prices_history.SHORT_RECORD_REASON),
    "gas": (gas_prices_history.RECORD_START, gas_prices_history.SHORT_RECORD_REASON),
}


def _founder(day: dt.date, cid: str = "C1") -> dict:
    return {"customer_id": cid, "acquisition_date": day.isoformat()}


@pytest.mark.parametrize("fuel", sorted(RECORDS))
def test_a_day_one_first_term_lookback_is_complete_or_flagged(fuel):
    """THE CONTROL, over both fuels: keyed to the founders' own first day and each record's declared
    start, so a world that starts earlier, or a record that moves, re-asks the question."""
    record_start, reason = RECORDS[fuel]
    complete = dt.date.fromisoformat(record_start) <= FIRST_DAY - dt.timedelta(days=LOOKBACK_DAYS)
    assert complete or reason, (
        f"a day-one {fuel} founder prices off a lookback the {fuel} record ({record_start}) "
        f"only partly fills, and the record declares no reason: silently short")
    # The guard the run calls agrees, and does not refuse the production record.
    rows = short_first_term_lookbacks([_founder(FIRST_DAY)], record_start, reason, fuel)
    assert bool(rows) == (not complete)


def test_the_guard_refuses_a_silently_short_lookback_and_passes_the_other_two_states():
    """All three branches can be taken: complete (no row), short and declared (a row carrying the
    reason), short and undeclared (refused, naming the customer)."""
    start = system_prices_history.RECORD_START
    late = dt.date.fromisoformat(start) + dt.timedelta(days=LOOKBACK_DAYS)
    assert short_first_term_lookbacks([_founder(late)], start, None, "electricity") == []
    rows = short_first_term_lookbacks([_founder(FIRST_DAY)], start, "why", "electricity")
    assert rows == [{"customer_id": "C1", "fuel": "electricity",
                     "acquisition_date": FIRST_DAY.isoformat(),
                     "lookback_days_covered": (FIRST_DAY - dt.date.fromisoformat(start)).days,
                     "reason": "why"}]
    with pytest.raises(ValueError, match="C1.*no reason"):
        short_first_term_lookbacks([_founder(FIRST_DAY)], start, None, "electricity")


def test_a_short_electricity_lookback_reads_nothing_on_or_after_its_start():
    """The gas defect's second half, asked of electricity: the short window must not be topped up
    from after the start. A record of distinct, rising prices from the electricity record's first
    day: the day-one price from the whole record equals the price from only the days before it."""
    start = dt.date.fromisoformat(system_prices_history.RECORD_START)
    records = [{"settlementDate": (start + dt.timedelta(days=i)).isoformat(),
                "settlementPeriod": 1, "systemSellPrice": 30.0 + i}
               for i in range(200)]
    before = [r for r in records if r["settlementDate"] < FIRST_DAY.isoformat()]
    assert len(before) < LOOKBACK_DAYS, "the window is not short, so this asks nothing"
    assert generate_forward_price(FIRST_DAY.isoformat(), records) == generate_forward_price(
        FIRST_DAY.isoformat(), before)


def test_the_declared_electricity_start_is_the_cached_records_start():
    """The declaration against the record itself. The cache is gitignored, so this runs where the
    record has been fetched; the start was re-probed against Elexon on 2026-10-06 (see the constant)."""
    cache = Path(__file__).resolve().parents[2] / "sim" / "cache" / "elexon_ssp_full.json"
    if not cache.exists():
        pytest.skip("no fetched electricity record in this tree")
    first = min(r["settlementDate"] for r in json.loads(cache.read_text()))
    assert first == system_prices_history.RECORD_START
