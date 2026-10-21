"""The forward price reads its window through a per-day index, and the index never changes an answer.

`CompanyTariffEngine.get_forward_price` used to walk the whole price history seven times per call
(37M `date.fromisoformat` calls to price one household's terms). The index replaced the walk. The
walk is kept as the fallback for any list the index cannot represent exactly, and as the oracle
here. Each control would red if the indexed path drifted from the scan, or if one branch became
unreachable.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

import pytest

from company.pricing import tariff_engine as te


def _records(days: int = 700, start: date = date(2020, 1, 1), seed: int = 7) -> list[dict]:
    rng = random.Random(seed)
    out, level = [], 40.0
    for i in range(days):
        level = max(5.0, level * (1.0 + rng.gauss(0.002 if i > days // 2 else 0.0, 0.04)))
        key = (start + timedelta(days=i)).isoformat()
        for _ in range(rng.choice((1, 3, 48))):
            out.append({"settlementDate": key, "systemSellPrice": level + rng.gauss(0, 6)})
    return out


def _price(records, delivery, fuel="electricity", term_months=12):
    try:
        return te.CompanyTariffEngine().get_forward_price(
            fuel, delivery, records, term_months=term_months)
    except ValueError as exc:
        return ("refused", str(exc))


def _deliveries(records):
    first = date.fromisoformat(records[0]["settlementDate"])
    return [(first + timedelta(days=d)).isoformat() for d in range(-5, 760, 23)]


def test_the_index_and_the_scan_give_the_same_price_and_both_branches_are_taken(monkeypatch):
    records = _records()
    assert te._daily_index(records) is not None, "a sorted canonical list must take the index"
    indexed = {(d, f, t): _price(records, d, f, t)
               for d in _deliveries(records) for f in ("electricity", "gas") for t in (12, 24)}
    assert any(isinstance(v, float) for v in indexed.values())
    assert any(isinstance(v, tuple) for v in indexed.values()), (
        "no delivery date fell before the history, so the refusal count is untested")

    monkeypatch.setattr(te, "_daily_index", lambda records: None)
    scanned = {k: _price(records, *k) for k in indexed}
    assert indexed == scanned


@pytest.mark.parametrize("spoil", ["shuffled", "not_canonical"])
def test_a_list_the_index_cannot_represent_exactly_takes_the_scan(spoil):
    records = _records(days=200)
    if spoil == "shuffled":
        random.Random(3).shuffle(records)
    else:
        records = [dict(r, settlementDate=r["settlementDate"].replace("-", "")) for r in records]
    assert te._daily_index(records) is None
    assert isinstance(_price(records, "2020-06-20"), float)


def test_a_list_that_grew_after_it_was_indexed_is_indexed_again():
    records = _records(days=200)
    before = _price(records, "2020-07-25")
    records.extend(
        {"settlementDate": (date(2020, 7, 19) + timedelta(days=i)).isoformat(),
         "systemSellPrice": 900.0}
        for i in range(5))
    after = _price(records, "2020-07-25")
    assert after != before and after == _price(list(records), "2020-07-25")


def test_a_record_inserted_inside_an_indexed_list_is_seen():
    # Both ends unchanged, so only the length says the index is stale.
    records = _records(days=200)
    before = _price(records, "2020-06-25")
    at = next(i for i, r in enumerate(records) if r["settlementDate"] == "2020-06-20")
    records[at:at] = [{"settlementDate": "2020-06-20", "systemSellPrice": 5000.0}]
    after = _price(records, "2020-06-25")
    assert after != before and after == _price(list(records), "2020-06-25")
