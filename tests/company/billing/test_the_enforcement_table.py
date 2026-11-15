"""ONE control over the whole enforcement table (C32, 2026-11-15).

Rows: every action the company can take on a domestic debt, the debt objection on switching
included (ninth pass, item 12). Columns: every protection ground.
`winter_moratorium.ENFORCEMENT_TABLE` says which cells bar the action (COVERED); this engages each
ground on a case the gate otherwise permits and asserts that exactly the COVERED cells refuse,
naming their ground. It fails if a cell is listed and not enforced, enforced where the table says
it does not apply, if the gate refuses everything (the permit leg), or if the published table in
the commons says something different from the code's.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import re
from pathlib import Path

import pytest

from company.billing.winter_moratorium import (
    COVERED,
    ENFORCEMENT_TABLE,
    GAP,
    NOT_APPLICABLE,
    PROTECTION_GROUNDS,
    EnforcementAction,
    EnforcementCase,
    may_take,
)
from company.regulatory.priority_services_register import (
    HouseholdComposition,
    PSRCategory,
    PSRRecord,
)

JULY, JANUARY = dt.date(2024, 7, 15), dt.date(2024, 1, 15)

#: A case on which every precondition is met and nothing protective is held, in a summer month.
BASE = EnforcementCase(account_id="H", as_of=JULY, categories=(), arrangement_offered=True,
                       suitability=True, self_disconnection_watched=True, ppm_route_exhausted=True,
                       involuntary_preconditions_recorded=True)

_POST_HOSPITAL = PSRRecord(account_id="H", categories=(), services_enrolled=(),
                           registration_date=dt.date(2024, 1, 1),
                           review_due_date=dt.date(2026, 1, 1), needs_codes=(33,))

#: How to engage each ground, alone, on BASE. None: no published content to engage (GAP everywhere).
ENGAGE = {
    "slc_27_5_to_27_8_ability_to_pay": dict(arrangement_offered=False),
    "slc_27_6_a_iii_safe_and_practicable": dict(suitability=None),
    "slc_27_9_ppm_before_disconnection": dict(ppm_route_exhausted=False),
    "slc_27_10_winter_pensionable": dict(as_of=JANUARY, categories=(PSRCategory.PENSIONABLE_AGE,),
                                         household=HouseholdComposition.LIVES_ALONE),
    "slc_27_11_winter_reasonable_steps": dict(as_of=JANUARY, categories=(PSRCategory.DISABILITY,)),
    "slc_27_11a_ascertain": dict(as_of=JANUARY),
    "slc_27a_self_disconnection": dict(self_disconnection_watched=False),
    "slc_28_15_proportionate": None,
    "slc_28b_involuntary_ppm": dict(involuntary_preconditions_recorded=False),
    "own_hold_winter_moratorium": dict(own_hold=True),
    "energy_uk_safety_net": dict(categories=(PSRCategory.DISABILITY,)),
    "psr_needs_codes": dict(categories=None, record=_POST_HOSPITAL),
    "breathing_space": dict(breathing_space=True),
}


def test_every_cell_refuses_exactly_where_the_table_says_it_bars():
    assert set(ENGAGE) == set(PROTECTION_GROUNDS), "a ground with no engagement is untested"
    assert set(ENFORCEMENT_TABLE) == set(EnforcementAction)
    states = {s for row in ENFORCEMENT_TABLE.values() for s in row.values()}
    assert states <= {COVERED, GAP, NOT_APPLICABLE}, "an 'absent' cell is what the table removes"
    # The permit leg first: a gate that refuses everything passes every refusal below.
    permitted = {a: may_take(a, BASE).permitted for a in EnforcementAction}
    assert all(permitted.values()), {a: may_take(a, BASE).reason for a in EnforcementAction}
    for ground, engage in ENGAGE.items():
        check = PROTECTION_GROUNDS[ground][1]
        if engage is None:
            assert all(row[ground] != COVERED for row in ENFORCEMENT_TABLE.values()), ground
            continue
        case = dataclasses.replace(BASE, **engage)
        for action, row in ENFORCEMENT_TABLE.items():
            answer = may_take(action, case)
            refusing = {PROTECTION_GROUNDS[g][1] for g, _r in answer.refusals}
            if row[ground] == COVERED:
                assert check in refusing, f"{action.value} x {ground}: permitted, table bars it"
            else:  # another listed ground may refuse the same facts; this one's check may not
                assert check not in refusing or any(
                    row[g] == COVERED and PROTECTION_GROUNDS[g][1] == check for g in row), (
                    f"{action.value} x {ground} is {row[ground]} but its check refused: "
                    f"{answer.reason}")


def test_support_for_a_self_disconnecting_household_is_never_refused():
    """Support is not a step to collect: engaging every ground at once leaves it permitted, and
    leaves every other action refused."""
    everything = {}
    for engage in ENGAGE.values():
        everything.update(engage or {})
    case = dataclasses.replace(BASE, **everything)
    for action in EnforcementAction:
        answer = may_take(action, case)
        assert answer.permitted is (action is EnforcementAction.SELF_DISCONNECTION_SUPPORT), action


def test_an_action_that_reads_the_household_refuses_to_guess_its_needs():
    with pytest.raises(TypeError, match="categories"):
        may_take(EnforcementAction.DISCONNECTION, dataclasses.replace(BASE, categories=None))


def test_the_published_table_is_the_codes_table():
    """The commons s.5 table and ENFORCEMENT_TABLE agree cell by cell (state only)."""
    text = (Path(__file__).resolve().parents[3] / "docs" / "domain_artefact_library" / "regulatory"
            / "psr_eligibility_and_disconnection_protection.md").read_text(encoding="utf-8")
    section = text[text.index("## 5. Every enforcement action"):]
    rows = [r for r in section.splitlines() if r.startswith("| `")]
    header = next(r for r in section.splitlines() if r.startswith("| action |"))
    grounds = [c.strip().strip("`") for c in header.strip("|").split("|")][1:]
    assert grounds == list(PROTECTION_GROUNDS)
    published = {}
    for r in rows:
        cells = [c.strip() for c in r.strip("|").split("|")]
        action = EnforcementAction(cells[0].strip("`"))
        published[action] = {g: re.match(r"\*{0,2}(covered|GAP|n/a)", c).group(1)
                             for g, c in zip(grounds, cells[1:])}
    assert published == ENFORCEMENT_TABLE


#: Names of calls that take an enforcement action (or ask the world to), and names a route that
#: would. A function in company/ or saas/ calling one must also call `may_take` (ninth pass, item 16).
_ACTS = re.compile(r"request_prepayment_move|raise_objection|disconnect_supply|de_?energi[sz]e\w*|\w*warrant_install\w*|"
                   r"\w*remote_switch\w*|\w*switch_to_prepay\w*|\w*(?:hand_?off|assign)_to_agency\w*")


def _called(node) -> list:
    import ast
    names = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            f = sub.func
            names.append(f.id if isinstance(f, ast.Name) else getattr(f, "attr", ""))
    return names


def _bypasses(tree) -> list:
    """(function, [action calls]) for every function that calls an action and not `may_take`.
    Read from the parsed tree: a comment or docstring naming an action is not a call."""
    import ast
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            calls = _called(node)
            acts = [c for c in calls if _ACTS.fullmatch(c)]
            if acts and "may_take" not in calls:
                out.append((node.name, acts))
    return out


def test_no_company_route_takes_an_enforcement_action_without_the_gate():
    """Every function that takes an action in the table asks `may_take` first. Keyed to the
    property, not to today's single route: a route added later that skips the gate reds this."""
    import ast
    root = Path(__file__).resolve().parents[3]
    routes, offenders = 0, {}
    for top in ("company", "saas"):
        for path in (root / top).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            routes += sum(1 for c in _called(tree) if _ACTS.fullmatch(c))
            bad = _bypasses(tree)
            if bad:
                offenders[str(path.relative_to(root))] = bad
    assert routes, "no enforcement route found at all: the name pattern has stopped matching the desk"
    assert offenders == {}, offenders
    # The check can fail: the live route with its gate call renamed is a bypass.
    desk = ast.parse((root / "company/billing/collections_journey.py").read_text(encoding="utf-8"))
    for node in ast.walk(desk):
        if isinstance(node, ast.Attribute) and node.attr == "may_take":
            node.attr = "ungated"
    assert _bypasses(desk), "the bypass check cannot fire"
    objector = ast.parse((root / "company/market/transfer_objection_register.py").read_text(
        encoding="utf-8"))
    for node in ast.walk(objector):
        if isinstance(node, ast.Name) and node.id == "may_take":
            node.id = "ungated"
    assert _bypasses(objector), "the objection route's gate call is not what the check reads"
