"""`sim.forward_curve.records_in_window` must return exactly what the parse-every-date scan
returned -- the same records in the same order -- because it replaced that scan on the run's
hottest price paths (2026-10-09) on the promise that no answer moves.

Each test names the defect it catches.
"""
import random
from datetime import date, timedelta

from sim.forward_curve import records_in_window


def _scan(records, first, last):
    return [r for r in records if first <= date.fromisoformat(r["settlementDate"]) <= last]


def _records(n, seed):
    rng = random.Random(seed)
    start = date(2016, 1, 1)
    out = [{"settlementDate": (start + timedelta(days=rng.randrange(0, 900))).isoformat(),
            "systemSellPrice": rng.random() * 100} for _ in range(n)]
    return out  # deliberately NOT sorted: callers' lists are not guaranteed to be


def test_every_window_returns_the_scans_records_in_the_scans_order():
    """Fires on: an off-by-one at either bound, or returning the records in date order rather
    than the list's own order (the forward curve's daily buckets and pstdev both read order)."""
    records = _records(3000, 1)
    rng = random.Random(2)
    for _ in range(200):
        a = date(2016, 1, 1) + timedelta(days=rng.randrange(-30, 930))
        b = a + timedelta(days=rng.randrange(0, 400))
        assert records_in_window(records, a, b) == _scan(records, a, b)


def test_an_appended_record_is_seen_by_the_next_call():
    """Fires on: a stale index served after the list grew -- a price published today and
    invisible to every later window."""
    records = _records(500, 3)
    first, last = date(2016, 1, 1), date(2018, 12, 31)
    records_in_window(records, first, last)
    records.append({"settlementDate": "2017-06-15", "systemSellPrice": 999.0})
    got = records_in_window(records, first, last)
    assert got == _scan(records, first, last)
    assert got[-1]["systemSellPrice"] == 999.0


def test_a_list_with_a_date_that_is_not_plain_iso_takes_the_scan():
    """Fires on: string-ordering a date form whose string order is not its date order
    (`20170102` sorts after `2017-12-31`), which would drop it from windows it belongs in."""
    records = _records(200, 4) + [{"settlementDate": "20170102", "systemSellPrice": 5.0}]
    first, last = date(2016, 12, 1), date(2017, 2, 1)
    got = records_in_window(records, first, last)
    assert got == _scan(records, first, last)
    assert any(r["settlementDate"] == "20170102" for r in got)


def test_neither_caller_sees_a_price_dated_on_or_after_its_own_date():
    """Fires on: the index returning a record dated on or after the run's own date to either
    caller -- a look-ahead the scan never made. Seeds a wild price on each of the reference date
    and the day after and asserts neither answer moves. (sigma_recent's documented bootstrap
    window, taken only when NO prior record exists, is not exercised: history is present here.)"""
    from sim.forward_curve import generate_forward_price
    from sim.risk_engine import calculate_sigma_recent

    records = _records(3000, 5)
    as_of = date(2017, 9, 1)
    assert records_in_window(records, as_of - timedelta(days=90), as_of - timedelta(days=1))
    sigma, forward = calculate_sigma_recent(as_of.isoformat(), records), \
        generate_forward_price(as_of.isoformat(), records)
    for d in (as_of, as_of + timedelta(days=1)):
        records.append({"settlementDate": d.isoformat(), "systemSellPrice": 1e6})
    assert calculate_sigma_recent(as_of.isoformat(), records) == sigma
    assert generate_forward_price(as_of.isoformat(), records) == forward
