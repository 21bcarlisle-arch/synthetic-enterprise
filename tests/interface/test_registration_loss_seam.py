"""Controls on the registration-loss seam (REC Schedule 23 Secured Inactive notice)."""
from __future__ import annotations

import ast
import dataclasses
import datetime as dt
import typing
from pathlib import Path

from interface.contracts import registration_loss_seam as seam
from interface.contracts.registration_loss_seam import (
    CSS_GO_LIVE,
    FORBIDDEN_TRUTH_FIELDS,
    NONE_MEANS,
    OBSERVABLE_PAYLOAD_FIELDS,
    UNSOLICITED_PAYLOAD_TYPES,
    is_css,
    loss_notice_observed_at,
    loss_notice_sender,
)

_SOURCE = Path(seam.__file__).read_text()


def test_every_payload_carries_exactly_its_declared_observable_fields():
    """Defect guarded: a field added to the notice without being declared observable."""
    assert set(OBSERVABLE_PAYLOAD_FIELDS) == {t.__name__ for t in UNSOLICITED_PAYLOAD_TYPES}
    for t in UNSOLICITED_PAYLOAD_TYPES:
        assert {f.name for f in dataclasses.fields(t)} == set(OBSERVABLE_PAYLOAD_FIELDS[t.__name__])


def test_no_field_is_optional_unless_the_contract_says_why():
    """Defect guarded: a None-able field (e.g. a gaining supplier added 'just in case')
    that asserts the real notice carries it. Today none may be None."""
    optional = {
        f"{t.__name__}.{name}"
        for t in UNSOLICITED_PAYLOAD_TYPES
        for name, hint in typing.get_type_hints(t).items()
        if type(None) in typing.get_args(hint)
    }
    assert optional == set(NONE_MEANS)


def test_no_notice_carries_a_forbidden_truth_name():
    """Defect guarded: a world-side departure label riding on the notice."""
    for t in UNSOLICITED_PAYLOAD_TYPES:
        assert not {f.name for f in dataclasses.fields(t)} & set(FORBIDDEN_TRUTH_FIELDS)


def test_the_contract_imports_neither_side_of_the_wall():
    """Defect guarded: the contract importing world or company code."""
    imported = set()
    for node in ast.walk(ast.parse(_SOURCE)):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
    assert not imported & {"sim", "simulation", "company", "saas"}


def test_both_regimes_are_reachable_and_each_keeps_its_own_clock():
    """Defect guarded: the CSS clock (17:00 the day before the effective date,
    Schedule 23 para 1.4(d)) applied to a pre-CSS switch, or the pre-CSS
    no-advance timing applied to a CSS one. Both branches asserted taken."""
    css_day, pre_day = dt.date(2023, 3, 1), dt.date(2017, 2, 21)
    assert is_css(css_day) and not is_css(pre_day)
    assert loss_notice_observed_at(css_day) == dt.datetime(2023, 2, 28, 17, 0)
    assert loss_notice_observed_at(pre_day) == dt.datetime(2017, 2, 21, 0, 0)
    for day in (css_day, pre_day):
        assert loss_notice_observed_at(day).date() <= day


def test_the_regime_turns_at_go_live():
    """Defect guarded: go-live moved off the date Schedule 23's change history
    records (v1.0, 18 July 2022) or the boundary computed on the wrong clock."""
    assert CSS_GO_LIVE == dt.date(2022, 7, 18)
    assert not is_css(CSS_GO_LIVE)  # its Secured Active moment is 17 July
    assert is_css(CSS_GO_LIVE + dt.timedelta(days=1))


def test_the_sender_is_the_registration_service_of_that_regime_and_fuel():
    """Defect guarded: a pre-CSS gas loss reported by MPAS (the electricity
    service), or a CSS-era loss reported by either pre-CSS service."""
    pre, css = dt.date(2017, 2, 21), dt.date(2023, 3, 1)
    assert loss_notice_sender(pre, "electricity") == seam.PRE_CSS_ELECTRICITY_SENDER
    assert loss_notice_sender(pre, "gas") == seam.PRE_CSS_GAS_SENDER
    assert loss_notice_sender(css, "electricity") == seam.CSS_SENDER
    assert loss_notice_sender(css, "gas") == seam.CSS_SENDER


def _every_day(first: dt.date, last: dt.date):
    day = first
    while day <= last:
        yield day
        day += dt.timedelta(days=1)


def test_a_pending_notice_arrives_at_or_before_secured_inactive_and_never_after_the_switch():
    """Defect guarded: an Invitation to Intervene dated after the Secured Inactive notice it
    precedes (a loser told a switch is cancellable once it is not), or after the switch itself.
    Over every effective date from go-live to the end of the record, so a weekday the rule
    mishandles cannot hide. The partition is asserted first: both a CSS date that is sent a
    Pending notice and a go-live-edge date that is not."""
    days = list(_every_day(CSS_GO_LIVE, dt.date(2025, 12, 31)))
    sent = [d for d in days if seam.emits_pending_notice(d)]
    assert sent and len(sent) < len(days)
    for day in sent:
        observed = seam.pending_notice_observed_at(day)
        assert observed <= seam.secured_active_at(day), day
        assert observed < dt.datetime.combine(day, dt.time(0)), day
        assert seam.latest_submission_date(day) >= CSS_GO_LIVE


def test_the_submission_date_is_the_latest_the_one_working_day_rule_allows():
    """Defect guarded: a submission date with less than one complete Working Day before the
    effective date (para 2.5: unlawful, so a warning no real loser could get), or one earlier
    than the rule requires (a warning longer than the ASAP floor, which flatters a save)."""
    def complete_working_days_between(submitted: dt.date, effective: dt.date) -> int:
        return sum(
            1 for d in _every_day(submitted + dt.timedelta(days=1), effective - dt.timedelta(days=1))
            if d.weekday() < 5
        )

    for day in _every_day(dt.date(2023, 3, 1), dt.date(2023, 3, 31)):
        submitted = seam.latest_submission_date(day)
        assert complete_working_days_between(submitted, day) >= 1, day
        assert complete_working_days_between(submitted + dt.timedelta(days=1), day) == 0, day
    # A Wednesday switch: submitted Monday, told at the start of Tuesday, 17 hours before
    # Secured Inactive at 17:00 Tuesday.
    assert seam.pending_notice_observed_at(dt.date(2023, 3, 1)) == dt.datetime(2023, 2, 28, 0, 0)
