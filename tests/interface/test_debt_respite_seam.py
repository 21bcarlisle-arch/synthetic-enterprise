"""Controls on the debt-respite seam (Breathing Space notices, SI 2020/1311)."""
from __future__ import annotations

import ast
import dataclasses
import datetime as dt
import typing
from pathlib import Path

from interface.contracts import debt_respite_seam as seam
from interface.contracts.debt_respite_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    NONE_MEANS,
    OBSERVABLE_PAYLOAD_FIELDS,
    SCHEMA_VERSION,
    UNSOLICITED_PAYLOAD_TYPES,
    MoratoriumStartNotice,
    MoratoriumType,
    NotifiedDebt,
)
from interface.contracts.wall_envelope import WallNotification

_PAYLOADS = (NotifiedDebt, *UNSOLICITED_PAYLOAD_TYPES)
_SOURCE = Path(seam.__file__).read_text()


def test_every_payload_carries_exactly_its_declared_observable_fields():
    """Defect guarded: a field added to a notice without being declared
    observable (or a declaration left behind after a field is removed)."""
    assert set(OBSERVABLE_PAYLOAD_FIELDS) == {t.__name__ for t in _PAYLOADS}
    for t in _PAYLOADS:
        assert {f.name for f in dataclasses.fields(t)} == set(
            OBSERVABLE_PAYLOAD_FIELDS[t.__name__]
        ), t.__name__


def test_every_field_that_may_be_None_says_why_and_both_kinds_exist():
    """Defect guarded: an optional field with no stated reason (a silent hole
    that will be read as 'the notice never says'), or a reason left on a field
    that is no longer optional. Both partitions are asserted non-empty first,
    so an all-optional or all-required contract cannot pass."""
    optional, required = set(), set()
    for t in _PAYLOADS:
        for name, hint in typing.get_type_hints(t).items():
            key = f"{t.__name__}.{name}"
            (optional if type(None) in typing.get_args(hint) else required).add(key)
    assert optional and required
    assert set(NONE_MEANS) == optional
    assert all(reason.strip() for reason in NONE_MEANS.values())


def test_no_notice_carries_a_forbidden_truth_name():
    """Defect guarded: a world-side truth label riding on a notice."""
    for t in _PAYLOADS:
        leaked = {f.name for f in dataclasses.fields(t)} & set(FORBIDDEN_TRUTH_FIELDS)
        assert not leaked, (t.__name__, leaked)


def test_the_moratorium_types_are_the_ones_the_company_register_reads():
    """Defect guarded: the notice's type vocabulary drifting from the one the
    company's breathing-space register (the consumer-to-be) is keyed on, so
    the first producer would land on a mapping nobody wrote."""
    from company.billing.breathing_space_register import BreathingSpaceType

    assert {m.value for m in MoratoriumType} == {m.value for m in BreathingSpaceType}


def test_the_seam_is_unsolicited_only_and_imports_no_world_or_company_code():
    """Defect guarded: a request/response leg declared for a stream the
    company never asks for (it would read as an exchange this build cannot
    hold), or the contract importing either side of the wall."""
    tree = ast.parse(_SOURCE)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
            if node.module == "interface.contracts.wall_envelope":
                assert {a.name for a in node.names} == {"WallNotification"}
        elif isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
    assert not imported & {"sim", "simulation", "company", "saas"}


def test_a_start_notice_crosses_in_the_notification_envelope():
    """Defect guarded: a notice shape the envelope refuses (the contract would
    describe a message that cannot be sent)."""
    notice = MoratoriumStartNotice(
        register_entry_ref="REG-1",
        moratorium_type=MoratoriumType.STANDARD,
        start_date=dt.date(2026, 6, 2),
        debtor_full_name=None,
        debtor_date_of_birth=None,
        debtor_address=None,
        debts=(NotifiedDebt(creditor_account_ref="ACC-1"),),
    )
    env = WallNotification(
        notification_id="n-1",
        notification_type=seam.MORATORIUM_START_NOTIFICATION_TYPE,
        schema_version=SCHEMA_VERSION,
        sender="INSOLVENCY-SERVICE-REGISTER",
        sequence=1,
        observed_at=dt.datetime(2026, 6, 2, 9, 0),
        valid_time=dt.date(2026, 6, 2),
        payload=notice,
    )
    assert env.payload.debts[0].creditor_account_ref == "ACC-1"
