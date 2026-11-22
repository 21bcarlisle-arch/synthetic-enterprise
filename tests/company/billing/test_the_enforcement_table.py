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
    CLAUSE_IN_FORCE,
    CONTACT_ATTEMPTS,
    COVERED,
    DEBT_STEP_CENSUS,
    ENFORCEMENT_TABLE,
    GAP,
    NOT_APPLICABLE,
    PROTECTION_GROUNDS,
    SAFE_AND_PRACTICABLE,
    SELF_DISCONNECTION_WATCH,
    SLC28B_PRECONDITIONS,
    UNROUTED_ACTIONS,
    EnforcementAction,
    EnforcementCase,
    may_take,
)
from company.regulatory.priority_services_register import (
    HouseholdComposition,
    ProtectionRecord,
    PSRCategory,
    PSRRecord,
    do_not_install_check,
)

JULY, JANUARY = dt.date(2024, 7, 15), dt.date(2024, 1, 15)
LEARNED, LAPSES = dt.date(2024, 6, 1), dt.date(2024, 9, 1)


def _record(kind, learned=LEARNED, lapses=LAPSES, **kw):
    if kind == CONTACT_ATTEMPTS and "evidence" not in kw:
        kw["evidence"] = tuple(dt.date(2024, 6, d) for d in range(1, 11))
    if kind == do_not_install_check(LEARNED, LAPSES, over_75_without_support=False,
                                    child_under_2=False).kind:
        return do_not_install_check(learned, lapses, over_75_without_support=False,
                                    child_under_2=False) if not kw else ProtectionRecord(
            kind, learned, lapses, **kw)
    return ProtectionRecord(kind, learned, lapses, **kw)


_28B = tuple(_record(k) for k in SLC28B_PRECONDITIONS)
_WATCH = _record(SELF_DISCONNECTION_WATCH)
_SRP = _record(SAFE_AND_PRACTICABLE)


def _28b_with(kind, record):
    """28B's records with one replaced (None: that one dropped), the other three in effect."""
    return tuple(r for r in _28B if r.kind != kind) + (() if record is None else (record,))


#: A case on which every precondition is met and nothing protective is held, in a summer month.
BASE = EnforcementCase(account_id="H", as_of=JULY, categories=(), arrangement_offered=True,
                       suitability=_SRP, self_disconnection_watch=_WATCH, ppm_route_exhausted=True,
                       involuntary_preconditions=_28B, on_prepayment=False)

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
    "slc_27a_self_disconnection": dict(self_disconnection_watch=None),
    "slc_28_15_proportionate": None,
    "slc_28b_involuntary_ppm": dict(involuntary_preconditions=()),
    "own_hold_winter_moratorium": dict(own_hold=True),
    "energy_uk_safety_net": dict(categories=(PSRCategory.DISABILITY,)),
    "psr_needs_codes": dict(categories=None, record=_POST_HOSPITAL),
    "breathing_space": dict(breathing_space=True),
    "already_on_prepayment": dict(on_prepayment=True),
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


#: Each dated record's ways of failing, ALONE, on BASE: absent, not yet learned, lapsed, carrying
#: no lapse, and (where it has one) its own finding.
def _record_engagements():
    out = {}
    for kind in SLC28B_PRECONDITIONS:
        out[(kind, "absent")] = dict(involuntary_preconditions=_28b_with(kind, None))
        out[(kind, "not yet learned")] = dict(involuntary_preconditions=_28b_with(
            kind, _record(kind, learned=dt.date(2024, 7, 16))))
        out[(kind, "lapsed")] = dict(involuntary_preconditions=_28b_with(
            kind, _record(kind, lapses=JULY)))
        out[(kind, "no lapse date")] = dict(involuntary_preconditions=_28b_with(
            kind, _record(kind, lapses=None)))
    out[(CONTACT_ATTEMPTS, "nine attempts")] = dict(involuntary_preconditions=_28b_with(
        CONTACT_ATTEMPTS, _record(CONTACT_ATTEMPTS, evidence=_record(CONTACT_ATTEMPTS).evidence[:9])))
    dni = SLC28B_PRECONDITIONS[-1]
    out[(dni, "a child under 2")] = dict(involuntary_preconditions=_28b_with(
        dni, do_not_install_check(LEARNED, LAPSES, over_75_without_support=False,
                                  child_under_2=True)))
    out[(dni, "unasked")] = dict(involuntary_preconditions=_28b_with(
        dni, do_not_install_check(LEARNED, LAPSES, over_75_without_support=None,
                                  child_under_2=False)))
    for how, watch in (("absent", None), ("not yet learned", _record(
            SELF_DISCONNECTION_WATCH, learned=dt.date(2024, 7, 16))),
            ("lapsed", _record(SELF_DISCONNECTION_WATCH, lapses=JULY)),
            ("no lapse date", _record(SELF_DISCONNECTION_WATCH, lapses=None))):
        out[(SELF_DISCONNECTION_WATCH, how)] = dict(self_disconnection_watch=watch)
    return out


def test_each_dated_record_alone_refuses_and_the_permit_leg_is_taken():
    """Ninth pass, items 3 and 6. ONE control over the partition: the permit leg (every record in
    effect) is taken for every action whose row reads 27A or 28B, and each record failing alone,
    in each way it can, refuses exactly those actions and names that record."""
    reads = {a for a, row in ENFORCEMENT_TABLE.items()
             if COVERED in (row["slc_27a_self_disconnection"], row["slc_28b_involuntary_ppm"])}
    assert reads, "no action reads a dated record: the partition is empty"
    seen = {"permit": all(may_take(a, BASE).permitted for a in reads)}
    for (kind, how), engage in _record_engagements().items():
        case = dataclasses.replace(BASE, **engage)
        column = ("slc_27a_self_disconnection" if kind == SELF_DISCONNECTION_WATCH
                  else "slc_28b_involuntary_ppm")
        for action in reads:
            answer = may_take(action, case)
            if ENFORCEMENT_TABLE[action][column] == COVERED:
                assert not answer.permitted and kind in answer.reason or (
                    kind == SELF_DISCONNECTION_WATCH and how == "absent"
                    and "self-disconnection" in answer.reason), (kind, how, action, answer.reason)
                seen[(kind, how)] = True
            else:
                assert answer.permitted, (kind, how, action, answer.reason)
    assert all(seen.values()) and len(seen) == 1 + len(_record_engagements()), seen


def test_a_dated_clause_names_its_standing_and_still_refuses_before_it_was_in_force():
    """Before 27A (15 Dec 2020) and 28B (8 Nov 2023) were in force the gate still refuses, as the
    supplier's own policy, and says which it is. Both standings are reached."""
    standings = set()
    for ground, start in CLAUSE_IN_FORCE.items():
        engage = ENGAGE[ground]
        action = next(a for a, row in ENFORCEMENT_TABLE.items() if row[ground] == COVERED)
        for on in (start - dt.timedelta(days=1), start):
            case = dataclasses.replace(BASE, as_of=on, **engage)
            reason = may_take(action, case).reason
            assert reason, (ground, on)
            standings.add("policy" if "own policy" in reason else
                          "licence" if f"in force from {start}" in reason else reason)
    assert standings == {"policy", "licence"}, standings


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


ROOT = Path(__file__).resolve().parents[3]


def _attr_calls_on(tree, handle: str) -> set:
    """Every method called on `self.<handle>` in a parsed module."""
    import ast
    return {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Attribute)
            and n.func.value.attr == handle}


def derived_census() -> set:
    """The names under which the company acts on a domestic debt, read from the code, not listed:
    the domestic desk's stages, every call through the desk's world door, the world-asked
    objection door, and every write to the objection register made anywhere in company/ or saas/."""
    import ast

    import company.interfaces.transfer_objection as door
    from company.billing.collections_journey import lawful_successors
    from company.crm.account_hierarchy import Segment
    from company.market.transfer_objection_register import TransferObjectionRegister
    table = lawful_successors(Segment.RESIDENTIAL)
    names = {s for k, v in table.items() for s in (k, *v) if s is not None}
    desk = ast.parse((ROOT / "company/billing/collections_journey.py").read_text(encoding="utf-8"))
    names |= _attr_calls_on(desk, "_plan_offers")
    names |= {n for n in door.__all__ if not n.startswith("open_")}
    writers = {m for m in vars(TransferObjectionRegister) if m.startswith("raise_")}
    for top in ("company", "saas"):
        for path in (ROOT / top).rglob("*.py"):
            names |= {c for c in _called(ast.parse(path.read_text(encoding="utf-8")))
                      if c in writers}
    return names


def test_the_census_is_the_code_and_every_step_to_collect_has_a_row_or_a_named_home():
    """Ninth pass, item 12: the missing row came from a hand-listed row set. The census is read off
    the code; a stage, door call or register write added later that the census does not place reds
    here, and so does a census name the code no longer has."""
    found = derived_census()
    assert found == set(DEBT_STEP_CENSUS), (sorted(found - set(DEBT_STEP_CENSUS)),
                                            sorted(set(DEBT_STEP_CENSUS) - found))
    for name, home in DEBT_STEP_CENSUS.items():
        assert isinstance(home, EnforcementAction) or (isinstance(home, str) and home.strip()), name
    # Every routed row is reached by some census name: a row nothing in the code takes is unrouted.
    routed = {h for h in DEBT_STEP_CENSUS.values() if isinstance(h, EnforcementAction)}
    assert routed | UNROUTED_ACTIONS | {EnforcementAction.SELF_DISCONNECTION_SUPPORT} == set(
        EnforcementAction), set(EnforcementAction) - routed - UNROUTED_ACTIONS
    assert not routed & UNROUTED_ACTIONS, routed & UNROUTED_ACTIONS
    # The derivation can fail: a stage the desk gains is a name the census does not place.
    from company.billing import collections_journey as cj
    real = cj.lawful_successors
    cj.lawful_successors = lambda seg: {**real(seg), "court_claim": frozenset()}
    try:
        assert "court_claim" in derived_census() - set(DEBT_STEP_CENSUS)
    finally:
        cj.lawful_successors = real


#: The calls that take a routed row's action: the census's call names that map to a row (read from
#: the census, not listed). Plus names a route built later for an UNROUTED row would carry, which no
#: code has yet and so cannot be read off it.
_ROUTED_CALLS = {n for n, h in DEBT_STEP_CENSUS.items()
                 if isinstance(h, EnforcementAction) and h not in UNROUTED_ACTIONS
                 and n.islower() and ("request_" in n or "raise_" in n)}
_ACTS = re.compile("|".join(sorted(_ROUTED_CALLS)) + r"|disconnect_supply|de_?energi[sz]e\w*|"
                   r"\w*warrant_install\w*|\w*remote_switch\w*|\w*switch_to_prepay\w*|"
                   r"\w*(?:hand_?off|assign)_to_agency\w*|\w*suspend_deduction\w*")


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
    root = ROOT
    assert _ROUTED_CALLS, "the census names no call that takes a routed row's action"
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
