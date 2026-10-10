"""Controls on the move-out notice seam."""
from __future__ import annotations

import ast
import dataclasses
import datetime as dt
from pathlib import Path

from interface.contracts import move_out_notice_seam as seam
from interface.contracts.move_out_notice_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    OBSERVABLE_PAYLOAD_FIELDS,
    UNSOLICITED_PAYLOAD_TYPES,
    latest_notice_date,
)


def test_the_notice_carries_exactly_its_declared_fields_and_no_destination():
    """Defect: a field added without being declared observable, or the move's destination (which
    the household never told us) riding on the notice."""
    for t in UNSOLICITED_PAYLOAD_TYPES:
        fields = {f.name for f in dataclasses.fields(t)}
        assert fields == set(OBSERVABLE_PAYLOAD_FIELDS[t.__name__])
        assert not fields & set(FORBIDDEN_TRUTH_FIELDS)
        assert not [f for f in fields if "destination" in f or "arrive" in f]


def test_the_notice_is_dated_two_working_days_before_the_move():
    """Defect: a lead time other than SLC 24.1(a)'s latest on-time notice. A Thursday move is told
    on the Tuesday; a Monday move on the previous Thursday (the weekend is not Working Days); a
    Tuesday move on the previous Friday."""
    assert latest_notice_date(dt.date(2023, 3, 16)) == dt.date(2023, 3, 14)
    assert latest_notice_date(dt.date(2023, 3, 13)) == dt.date(2023, 3, 9)
    assert latest_notice_date(dt.date(2023, 3, 14)) == dt.date(2023, 3, 10)


def test_the_contract_imports_neither_side_of_the_wall():
    """Defect: the contract importing world or company code."""
    tops = set()
    for node in ast.walk(ast.parse(Path(seam.__file__).read_text())):
        if isinstance(node, ast.ImportFrom) and node.module:
            tops.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            tops |= {a.name.split(".")[0] for a in node.names}
    assert not tops & {"simulation", "sim", "company", "saas"}
