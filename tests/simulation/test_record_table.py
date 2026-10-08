"""The settled book as typed columns (`simulation.record_table`) reads back as the dicts it was.

Each test names the defect it exists to catch. The book's readers were written against a list of
dicts, so the failure that matters is SILENT: a value coming back as a different type, a missing
key coming back present, a correction landing in a detached copy, or a reader that gated on
`isinstance(x, dict)` skipping every row.
"""

from __future__ import annotations

import copy
import json
import math
import pickle
from collections.abc import Mapping, Sequence

import numpy as np

from simulation.record_table import RecordTable, Row, json_default

#: Every value shape a settled record carries, plus the ones that would expose a coercion: an int
#: and a float under ONE key, a bool (an int subclass), a 2**70 int (past int64), a numpy scalar,
#: -0.0 and NaN (exact only if the float column is IEEE-exact), None, and nested containers.
SOURCE = [
    {"customer_id": "SYN-2016-001", "settlement_date": "2016-01-01", "margin_gbp": 1.25,
     "settlement_periods_folded": 48, "is_estimated": True, "bad_debt_gbp": 0,
     "note": None, "tags": ["a", "b"], "nested": {"k": 1.5}},
    {"settlement_date": "2016-01-02", "customer_id": "SYN-2016-001g", "margin_gbp": -0.0,
     "settlement_periods_folded": 47, "is_estimated": False, "bad_debt_gbp": 0.5,
     "huge": 2 ** 70, "np_value": np.float64(3.5)},
    {"customer_id": "SYN-2016-002", "margin_gbp": float("nan"), "settlement_periods_folded": 46},
]


def _same(a, b) -> bool:
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b and type(a) is type(b)


def test_a_row_round_trips_every_field_type_exactly_including_missing_keys_and_none():
    """DEFECT: a column coerces a value -- the int 0 read back as 0.0, True as 1, a numpy scalar
    as a Python float, 2**70 wrapped -- or a key one record lacks reads back present (a filler
    0.0 where the dict had no key), or key ORDER changes so a dump without sort_keys differs."""
    table = RecordTable(SOURCE)
    assert len(table) == len(SOURCE)
    for row, src in zip(table, SOURCE):
        out = row.to_dict()
        assert list(out) == list(src), "key order or key presence changed"
        for key in src:
            assert _same(out[key], src[key]), (key, out[key], src[key])
            assert _same(row[key], src[key]), key
    assert "note" in table[0] and table[0]["note"] is None, "a present None must stay present"
    assert "note" not in table[1] and table[1].get("note", "absent") == "absent"
    assert "huge" not in table[0] and table[0].get("huge") is None


def test_the_typed_path_is_taken_when_a_column_is_homogeneous():
    """DEFECT: every column silently falls to the object list. Every exactness test above still
    passes and the table saves nothing -- the memory claim is the reason this module exists."""
    table = RecordTable(SOURCE)
    kinds = table.column_kinds()
    assert kinds["settlement_periods_folded"] == "i"
    assert kinds["is_estimated"] == "b"
    assert kinds["bad_debt_gbp"] == "o", "an int and a float under one key must not share a float64"
    floats = RecordTable([{"x": float(i), "y": i} for i in range(1000)])
    assert floats.column_kinds() == {"x": "f", "y": "i"}
    assert floats.nbytes() < 1000 * 24, floats.nbytes()


def test_a_row_is_a_mapping_and_every_conversion_yields_the_source_dict():
    """DEFECT: the row view is not a Mapping (so `isinstance(r, Mapping)` readers drop it), or a
    conversion -- `dict(r)`, `{**r}`, `r.copy()`, `copy.deepcopy`, pickle, `json.dumps` via
    `json_default` -- yields something other than the dict it was built from."""
    table = RecordTable(SOURCE[:1])
    row, src = table[0], SOURCE[0]
    assert isinstance(row, Mapping) and isinstance(table, Sequence)
    assert not isinstance(row, dict), "a dict subclass would present EMPTY C storage to json"
    for converted in (dict(row), {**row}, row.copy(), copy.deepcopy(row), pickle.loads(pickle.dumps(row))):
        assert type(converted) is dict and converted == src and list(converted) == list(src)
    assert row == src and src == row
    assert json.dumps(row, default=json_default) == json.dumps(src)
    assert json.dumps({"all_records": table}, default=json_default) == json.dumps({"all_records": [src]})
    assert pickle.loads(pickle.dumps(table)) == table and copy.deepcopy(table) == table


def test_json_default_refuses_what_json_refuses():
    """DEFECT: `json_default` becomes a `default=str` in disguise and stringifies an unknown type
    instead of refusing it, masking a type change in a published artefact."""
    import datetime
    import functools

    # The `default=str` dump (simulation/run_scenario.py) keeps its str for everything else, and the
    # book still dumps as rows -- under a bare `default=str` it was the table's one-line repr.
    with_str = functools.partial(json_default, fallback=str)
    table = RecordTable(SOURCE[:1])
    dumped = json.loads(json.dumps({"all_records": table, "on": datetime.date(2016, 1, 1)},
                                   default=with_str))
    assert dumped == {"all_records": [SOURCE[0]], "on": "2016-01-01"}
    try:
        json.dumps({"x": object()}, default=json_default)
    except TypeError:
        return
    raise AssertionError("json_default serialised an object json itself refuses")


def test_a_consumer_that_gated_on_dict_now_reads_rows():
    """DEFECT: `_bridge_one_arm` skipped every record that was not a `dict` (`continue`), so a
    columnar book bridged to zero with no error. Its gates now read Mapping/Sequence."""
    from tools.run_value_cycle_ab import _bridge_one_arm

    rows = [{"customer_id": "C1", "settlement_date": "2016-01-01", "margin_gbp": 10.0,
             "net_margin_gbp": 7.0, "revenue_gbp": 30.0, "wholesale_cost_gbp": 20.0,
             "consumption_kwh": 100.0},
            {"customer_id": "C1", "settlement_date": "2016-01-02", "margin_gbp": 5.0,
             "net_margin_gbp": 2.0, "revenue_gbp": 15.0, "wholesale_cost_gbp": 10.0,
             "consumption_kwh": 50.0}]
    as_dicts = _bridge_one_arm({"phase2b": {"all_records": rows}})
    as_table = _bridge_one_arm({"phase2b": {"all_records": RecordTable(rows)}})
    assert as_table["gross_margin_gbp"] == 15.0
    assert as_table == as_dicts


def test_an_arrears_correction_writes_through_to_the_stored_column():
    """DEFECT: a correction after the commit lands on a detached copy -- the arrears engine's
    `rec[...] = ...` updates an object nobody reads, and the published bad debt is the provision
    the correction was meant to replace."""
    from simulation.arrears_engine import apply_emergent_bad_debt

    table = RecordTable([
        {"customer_id": "C1", "settlement_date": "2016-06-01", "bad_debt_gbp": 1.0,
         "net_margin_gbp": 10.0, "treasury_cash_balance_gbp": 100.0},
        {"customer_id": "C1", "settlement_date": "2016-07-01", "bad_debt_gbp": 1.0,
         "net_margin_gbp": 10.0, "treasury_cash_balance_gbp": 110.0},
    ])
    apply_emergent_bad_debt(table, {("C1", 2016): 5.0})
    _kind, store = table._cols["bad_debt_gbp"]
    assert store[1] == 4.0, "the stored column did not change"
    assert table[1]["bad_debt_gbp"] == 4.0 and table[1]["net_margin_gbp"] == 7.0
    assert table[1]["treasury_cash_balance_gbp"] == 107.0
    assert table[0]["bad_debt_gbp"] == 1.0


def test_a_new_key_set_after_the_commit_is_present_only_on_that_row():
    """DEFECT: setting a key on one row makes it appear (as a filler) on every row, or deleting
    it leaves it readable."""
    table = RecordTable([{"a": 1.0}, {"a": 2.0}])
    table[0]["late"] = "x"
    assert table[0]["late"] == "x" and "late" not in table[1] and list(table[0]) == ["a", "late"]
    del table[0]["late"]
    assert "late" not in table[0]
    table[1]["a"] = 3  # an int into a float column must come back an int, not 3.0
    assert type(table[1]["a"]) is int and type(table[0]["a"]) is float
    assert isinstance(table[-1], Row) and table[-1]["a"] == 3
