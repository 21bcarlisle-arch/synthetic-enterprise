"""The fold must answer what a scan of the whole book would have answered — to the byte.

WHY THE EQUALITY IS THE TEST, AND NOT THE SPEED. `simulation/run_phase2b.py` filtered its whole
accumulated settlement book by `customer_id` from inside the term loop, twice, and that was the
run's only quadratic term (measured over two horizons: 30.2 customer-years → 13% of the run in
those two scans, 109.0 customer-years → 31%, an exponent of 2.05 while the rest of the run
scales at 1.19). Replacing a scan with a running total is worth nothing if it also, quietly,
answers a slightly different question — and one of the two questions here IS the point-in-time
blindfold, so "slightly different" would mean the company seeing consumption it had not yet
been billed for.

So these tests run BOTH implementations over the same records and assert they agree. The
reference implementations below are the pre-2026-08-24 code, copied verbatim; if the fold and
the scan ever disagree the test says which record made them disagree.

R15 — each mutation proven by reverting, not asserted:
  * make the window inclusive of `term_start` -> `test_the_window_is_half_open_like_the_blindfold`.
  * count records whose `consumption_kwh` is None as zero -> `test_a_period_with_no_reading_is
    _not_a_period_of_zero`.
  * drop the `+ 1` from the day span -> `test_the_day_span_is_inclusive_of_both_ends`.
  * let one customer's totals leak into another -> `test_customers_do_not_leak_into_each_other`.
  * feed the fold before the term is appended -> `test_the_fold_and_the_list_agree_at_every_
    point_in_the_run` (the ordering assertion).
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from simulation.run_phase2b import _company_eac_estimate, _derive_eac_from_settlement
from simulation.settlement_fold import SettlementFold

# ── the implementations this replaced, verbatim, as the oracle ──────────────────────────────

def _scan_company_eac(cid, term_start_str, all_records):
    term_start = date.fromisoformat(term_start_str)
    year_ago = term_start.replace(year=term_start.year - 1)
    return sum(
        r["consumption_kwh"]
        for r in all_records
        if r.get("customer_id") == cid
        and r.get("consumption_kwh") is not None
        and year_ago <= date.fromisoformat(r["settlement_date"]) < term_start
    )


def _scan_derive_eac(cid, all_records):
    recs = [r for r in all_records
            if r.get("customer_id") == cid and r.get("consumption_kwh") is not None]
    if not recs:
        return None
    dates = [r["settlement_date"] for r in recs]
    total_days = (date.fromisoformat(max(dates)) - date.fromisoformat(min(dates))).days + 1
    if total_days < 180:
        return None
    return sum(r["consumption_kwh"] for r in recs) / total_days * 365.25


def _book(customers=("C1", "C2"), start=date(2018, 1, 1), days=800, per_period=0.25):
    """A settled book of the real shape: every customer, every day, 48 periods."""
    out = []
    for i in range(days):
        d = (start + timedelta(days=i)).isoformat()
        for cid in customers:
            for p in range(1, 49):
                out.append({"customer_id": cid, "settlement_date": d, "settlement_period": p,
                            "consumption_kwh": per_period * (1 + 0.5 * (cid == "C2"))})
    return out


# ── the equality ────────────────────────────────────────────────────────────────────────────

def test_the_fold_answers_the_twelve_month_window_exactly_as_the_scan_did():
    records = _book()
    fold = SettlementFold()
    fold.add(records)

    for cid in ("C1", "C2"):
        for term_start in ("2019-01-01", "2019-06-15", "2020-01-01", "2018-03-01"):
            assert _company_eac_estimate(cid, term_start, fold, base_eac_override=0.0) == \
                pytest.approx(_scan_company_eac(cid, term_start, records)), (
                    "fold and scan disagree for {} at {}".format(cid, term_start))


def test_the_fold_answers_mean_annual_consumption_exactly_as_the_scan_did():
    records = _book()
    fold = SettlementFold()
    fold.add(records)

    for cid in ("C1", "C2"):
        assert _derive_eac_from_settlement(cid, fold) == \
            pytest.approx(_scan_derive_eac(cid, records))


def test_the_fold_and_the_list_agree_at_every_point_in_the_run():
    """THE ORDERING PROPERTY. `_company_eac_estimate` is called from inside the settlement loop,
    where the current term's records are NOT yet in the book. A fold fed any earlier than the
    line that extends the list would see records the scan did not, and the twelve-month window
    would silently widen — the company reading consumption it had not yet been billed for."""
    terms = [_book(days=120, start=date(2018, 1, 1)),
             _book(days=120, start=date(2018, 5, 1)),
             _book(days=120, start=date(2018, 9, 1))]
    accumulated, fold = [], SettlementFold()

    for term in terms:
        # asked BEFORE this term lands, exactly as the run asks
        for cid in ("C1", "C2"):
            assert _company_eac_estimate(cid, "2018-09-01", fold, base_eac_override=0.0) == \
                pytest.approx(_scan_company_eac(cid, "2018-09-01", accumulated))
        accumulated.extend(term)
        fold.add(term)

    for cid in ("C1", "C2"):
        assert _company_eac_estimate(cid, "2019-01-01", fold, base_eac_override=0.0) == \
            pytest.approx(_scan_company_eac(cid, "2019-01-01", accumulated))


# ── the four properties a shortcut would break ──────────────────────────────────────────────

def test_the_window_is_half_open_like_the_blindfold():
    """`[year_ago, term_start)`. The term's own start date is the future at the moment the
    question is asked, and including it is the blindfold leaking by one day."""
    fold = SettlementFold()
    fold.add([{"customer_id": "C1", "settlement_date": "2019-01-01", "consumption_kwh": 7.0},
              {"customer_id": "C1", "settlement_date": "2018-12-31", "consumption_kwh": 3.0}])

    assert fold.consumption_kwh_between("C1", "2018-01-01", "2019-01-01") == pytest.approx(3.0)
    assert fold.consumption_kwh_between("C1", "2018-01-01", "2019-01-02") == pytest.approx(10.0)


def test_a_period_with_no_reading_is_not_a_period_of_zero():
    """The scan filtered `consumption_kwh is not None`. Treating a missing reading as 0.0 would
    add days to the span while adding nothing to the total, dragging every annualised figure
    down — and it would do it silently, on exactly the estimated-read periods a real supplier
    has most of."""
    fold = SettlementFold()
    fold.add([{"customer_id": "C1", "settlement_date": "2019-01-01", "consumption_kwh": 5.0},
              {"customer_id": "C1", "settlement_date": "2019-06-01", "consumption_kwh": None}])

    assert fold.total_consumption_kwh("C1") == pytest.approx(5.0)
    assert fold.span_days("C1") == 1, "a period with no reading extended the span"
    assert fold.record_count == 1


def test_the_day_span_is_inclusive_of_both_ends():
    """`(max - min).days + 1`, as the function it replaces computes it. One day out here moves
    a published annualised consumption figure."""
    fold = SettlementFold()
    fold.add([{"customer_id": "C1", "settlement_date": "2019-01-01", "consumption_kwh": 1.0},
              {"customer_id": "C1", "settlement_date": "2019-01-31", "consumption_kwh": 1.0}])

    assert fold.span_days("C1") == 31


def test_customers_do_not_leak_into_each_other():
    fold = SettlementFold()
    fold.add([{"customer_id": "C1", "settlement_date": "2019-01-01", "consumption_kwh": 5.0},
              {"customer_id": "C2", "settlement_date": "2019-01-01", "consumption_kwh": 9.0}])

    assert fold.total_consumption_kwh("C1") == pytest.approx(5.0)
    assert fold.total_consumption_kwh("C2") == pytest.approx(9.0)
    assert fold.consumption_kwh_between("C1", "2018-01-01", "2020-01-01") == pytest.approx(5.0)


def test_an_unknown_customer_answers_absence_not_zero_consumption():
    """`has_records` is what the caller branches on, so it must distinguish "this customer has
    settled nothing" from "this customer settled nothing" — the first falls back to the declared
    EAC and the second would publish a zero."""
    fold = SettlementFold()
    assert fold.has_records("C9") is False
    assert fold.span_days("C9") == 0
    assert fold.consumption_kwh_between("C9", "2018-01-01", "2020-01-01") == 0.0


# ── the shim, which exists for these tests and must not be how the run works ────────────────

def test_the_helpers_still_accept_a_plain_list_of_records():
    """Existing tests hand these two functions a handful of hand-built records, which is the
    clearest way to state what they mean. That has to keep working."""
    records = _book(days=400)
    assert _derive_eac_from_settlement("C1", records) == \
        pytest.approx(_scan_derive_eac("C1", records))


def test_the_run_builds_exactly_one_fold_and_feeds_it_where_the_list_is_extended():
    """A second fold, or a feed at a different line, is the point-in-time drift this file is
    about. Asserted on the source because that is where the property lives."""
    from pathlib import Path

    import simulation.run_phase2b as p2b

    src = Path(p2b.__file__).read_text(encoding="utf-8")
    assert src.count("settled_fold = SettlementFold()") == 1, (
        "the run builds more than one fold")
    assert src.count("settled_fold.add(") == 1, "the fold is fed in more than one place"
    # The book is extended and the fold is fed in ONE block, with nothing between them that
    # could ask the fold a question. The line reads differently since the book began holding
    # daily rows (2026-08-24), so the property is asserted on the ORDER rather than on one
    # literal line: the registers and the fold both see the same term, and both see it only
    # after the loop has finished asking questions about the book as it stood before it.
    block = src.split("period_registers.add(settled_this_term")[1].split("\n\n")[0]
    assert "all_records.extend(fold_to_days(settled_this_term))" in block
    assert "settled_fold.add(settled_this_term)" in block
    assert src.index("settled_fold.add(settled_this_term)") > \
        src.index("all_records.extend(fold_to_days(settled_this_term))"), (
            "the fold is fed before the book is extended, which is the point-in-time drift "
            "this test exists to catch")
