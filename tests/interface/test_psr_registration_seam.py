"""Controls on the priority-services registration seam."""
from __future__ import annotations

import ast
import dataclasses
import datetime as dt
from pathlib import Path

from interface.contracts import psr_registration_seam as seam
from interface.contracts.psr_registration_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    OBSERVABLE_PAYLOAD_FIELDS,
    UNSOLICITED_PAYLOAD_TYPES,
    registration_observed_at,
)


def test_the_notice_carries_exactly_its_declared_fields_and_no_truth_name():
    """Defect: a field added to the notice without being declared observable, or a latent-state
    name (the world's PSR-type or financial flag) riding on it."""
    for t in UNSOLICITED_PAYLOAD_TYPES:
        fields = {f.name for f in dataclasses.fields(t)}
        assert fields == set(OBSERVABLE_PAYLOAD_FIELDS[t.__name__])
        assert not fields & set(FORBIDDEN_TRUTH_FIELDS)


def test_a_registration_is_observed_on_the_day_it_was_made():
    """Defect: a disclosure stamped with a later or earlier observation time than it was made,
    which would let the company know of it before the household spoke."""
    on = dt.date(2017, 5, 2)
    assert registration_observed_at(on) == dt.datetime(2017, 5, 2)


def test_the_contract_imports_neither_side_of_the_wall():
    """Defect: the contract importing world or company code."""
    tops = set()
    for node in ast.walk(ast.parse(Path(seam.__file__).read_text())):
        if isinstance(node, ast.ImportFrom) and node.module:
            tops.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            tops |= {a.name.split(".")[0] for a in node.names}
    assert not tops & {"simulation", "sim", "company", "saas"}
