"""The two per-renewal readers ask the book's index, and the index answers as the scan did.

What it cost: `estimate_prior_term_net_margin` and `households_own_records` each scanned the whole
settled book once per renewal (157 s and 56 s of one census fixture arm under cProfile,
2026-10-21). `RecordTable.rows_grouped` indexes the book once and catches up over appended rows.
The defects this names: an index that is not caught up after `extend` (a renewal blind to the term
just settled), one that survives a rewrite of the column it groups (a row billed to the wrong
account), and a reader that never takes the index at all (the cost back, every test green).
"""

import random

import company.crm.customer_profitability as cp
import simulation.customer_events as ce
from simulation.household import household_of
from simulation.record_table import RecordTable


def _rows(rng, n, start_day):
    ids = ["C1", "C1g", "C2", "C3g", "C3", "C10", "C1_2"]
    out = []
    for k in range(n):
        d = start_day + k
        out.append({
            "customer_id": rng.choice(ids),
            "commodity": rng.choice(["electricity", "gas"]),
            "settlement_date": f"20{17 + d // 360:02d}-{1 + (d // 30) % 12:02d}-{1 + d % 28:02d}",
            "term_start": f"20{17 + d // 360:02d}-01-01",
            "net_margin_gbp": rng.uniform(-3.0, 2.0),
        })
    return out


def _scan_margin(cid, term_start, rows, commodity):
    # The plain-list path IS the whole-book scan: no `rows_grouped` on a list.
    return cp.estimate_prior_term_net_margin(cid, term_start, list(rows), commodity=commodity)


def _ask_everything(table):
    for cid in ("C1", "C2", "C3", "C10", "C1_2", "nobody"):
        for commodity in ("electricity", "gas"):
            for term_start in ("2018-01-01", "2019-06-01", "2021-01-01"):
                assert cp.estimate_prior_term_net_margin(
                    cid, term_start, table, commodity=commodity
                ) == _scan_margin(cid, term_start, table, commodity), (cid, commodity, term_start)
        got = ce.households_own_records(cid, table)
        want = [r for r in table if household_of(r.get("customer_id", "")) == cid]
        assert [r.to_dict() for r in got] == [r.to_dict() for r in want], cid


def test_the_index_answers_as_the_scan_as_the_book_grows_and_is_rewritten():
    rng = random.Random(7)
    table = RecordTable(_rows(rng, 400, 0))
    _ask_everything(table)
    # The book grows after the index exists: the next renewal must see the new term.
    table.extend(_rows(rng, 400, 400))
    _ask_everything(table)
    # A row's account is rewritten in place, then a row is replaced wholesale.
    table[3]["customer_id"] = "C2"
    table[5] = {**table[5].to_dict(), "customer_id": "C10"}
    _ask_everything(table)
    del table[7]["customer_id"]
    _ask_everything(table)


def test_both_readers_take_the_index_on_the_runs_book(monkeypatch):
    """The fast path CAN be taken: a reader that ignores it is the cost back with every answer equal."""
    table = RecordTable(_rows(random.Random(3), 200, 0))
    asked = []
    real = RecordTable.rows_grouped

    def spy(self, column, key_fn, default=""):
        asked.append(key_fn)
        return real(self, column, key_fn, default)

    monkeypatch.setattr(RecordTable, "rows_grouped", spy)
    cp.estimate_prior_term_net_margin("C1", "2021-01-01", table)
    ce.households_own_records("C1", table)
    assert asked == [cp._billing_key, household_of]


def test_the_index_is_built_once_and_caught_up_not_rebuilt():
    table = RecordTable(_rows(random.Random(5), 100, 0))
    calls = []

    def key(v):
        calls.append(v)
        return v

    table.rows_grouped("customer_id", key)
    table.rows_grouped("customer_id", key)
    assert len(calls) == 100
    table.extend(_rows(random.Random(6), 30, 100))
    table.rows_grouped("customer_id", key)
    assert len(calls) == 130


def test_a_write_to_another_column_keeps_the_index():
    column = "customer_id"
    table = RecordTable(_rows(random.Random(9), 50, 0))
    calls = []
    table.rows_grouped(column, lambda v, c=calls: c.append(v) or v)
    key = next(iter(table._groups))[1]
    table[0]["net_margin_gbp"] = 1.0
    table.rows_grouped(column, key)
    assert len(calls) == 50
    table[0][column] = "C2"
    table.rows_grouped(column, key)
    assert len(calls) == 100
