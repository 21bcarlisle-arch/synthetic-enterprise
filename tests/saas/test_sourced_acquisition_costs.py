"""THE CONTROL: an unsourced money constant may not re-enter the acquisition path.

WHY (2026-08-28, WORKER_FINDING_THE_SOURCED_ACQUISITION_MODEL_IS_UNWIRED_AND_THE_INVENTED_
ONE_IS_LIVE.md). `saas/growth_mandate.py` carried `COST_PER_ACQUISITION = {"resi": 150.0,
"SME": 400.0}` for months. Nothing was wrong with the code; what was wrong was that two
numbers with no source behind them were what the live campaign spent, while the researched
model sat in `saas/opex_ledger.py` with no caller. Deleting the table fixes the instance. R10
says an absurdity-class defect may not be closed with an instance fix, so this is the class
control: a money constant appearing at module scope on this path must carry a citation, and
the test FAILS if one appears without.

R15 — THIS CONTROL CAN FAIL, AND PROVES IT HERE. `test_the_detector_fires_on_an_uncited_
constant` runs the same detector over a synthetic module that reintroduces exactly the
deleted defect and asserts it is caught; `test_the_detector_passes_a_cited_constant` asserts
the detector is not simply always-red. Neither reads the real tree, so the pair stays a real
mutation proof rather than a restatement of today's source.

NOT FAIL-OPEN: `test_the_detector_has_a_non_empty_subject` asserts each scanned file actually
yielded constants, so a rename or a move that empties the scan is a failure and not a pass.

SCOPE. `company/analytics/counterfactual_retention.py` is NOT in `_SCANNED`, and after R3 it
never will be. This docstring used to say "R3's commit adds the path" -- that was written
before the repair and the repair took a different route. R3 did not CITE
`RESI_OFFER_COST_GBP = 50.0` and `IC_OFFER_COST_GBP = 200.0`; it DELETED them, because a
retention offer is a price and its cost is `discount_pct x that customer's term revenue`, a
quantity with no constant in it at all. The module now holds no money constant for this
detector to find, and adding it to `_SCANNED` would fail
`test_the_detector_has_a_non_empty_subject` -- correctly, since an empty scan is a blind one.
A file with nothing to cite is out of scope, not covered.

THE OTHER HALF OF THE PAIR, so nobody builds a third control for it.
`tests/architecture/test_a_cited_constant_has_a_caller.py` is the complement of this file and
they divide the director's sentence between them: *"a sourced number that exists and isn't
wired should not be able to sit quietly beside an unsourced one that is."* This file catches
the UNSOURCED-AND-LIVE half on a named path. That one catches the SOURCED-AND-UNREACHED half
repo-wide, by AST, with no list to maintain -- and it is the half that had no other symptom,
since being unreached is invisible while being unsourced at least shows up in the numbers.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]

# Files whose module-scope money constants must be cited.
_SCANNED = ("saas/growth_mandate.py", "saas/opex_ledger.py")

# A name that denominates money or a rate paid. Deliberately broad -- a constant that slips
# past this is a constant that does not look like a price, and the cost of a false positive
# is one citation comment.
_MONEY_NAME = re.compile(
    r"(GBP|_COST|COST_|_FEE|FEE_|_PRICE|PRICE_|CAC|COMMISSION|_SPEND|SPEND_|ALLOWANCE|CHARGE)"
)

# What counts as a citation: a research file, a named published source, or an explicit
# statement that the value is structural rather than measured. Checked against the comment
# block and docstring attached to the constant, never against the constant's own name -- a
# name cannot cite itself (R15 TAUTOLOGY).
_CITATION = re.compile(
    r"(docs/market_research/|Ofgem|CMA|Elexon|NESO|BEIS|DESNZ|rate card|Appendix|"
    r"structural zero|STRUCTURAL zero|no one-off)",
    re.IGNORECASE,
)


def _money_constants(source: str) -> dict[str, str]:
    """{constant_name: the prose attached to it} for module-scope numeric constants whose
    name denominates money.

    The attached prose is COMMENT TEXT ONLY -- the run of comment lines immediately above the
    assignment, plus any inline comments within it. The constant's own name and value are
    deliberately excluded: this control's first draft searched the whole assignment and so
    passed `OFGEM_CAC_COST_GBP = 90.0`, which cites nothing and merely says "Ofgem" in its
    name. That is R15's TAUTOLOGY shape (the checked value derived from the same source it
    checks) and `test_the_detector_is_not_satisfied_by_the_constants_own_name` holds the line.

    Read from the SOURCE TEXT rather than from the imported module, so the control sees what
    is written rather than what happens to evaluate.
    """
    tree = ast.parse(source)
    lines = source.splitlines()
    found: dict[str, str] = {}

    for node in tree.body:
        targets = (
            [node.target] if isinstance(node, ast.AnnAssign)
            else node.targets if isinstance(node, ast.Assign)
            else []
        )
        names = [t.id for t in targets if isinstance(t, ast.Name)]
        if not names:
            continue
        if not any(_MONEY_NAME.search(n) for n in names):
            continue
        if not _holds_a_number(node.value):
            continue

        start = node.lineno - 1
        comments = []
        i = start - 1
        while i >= 0 and (lines[i].lstrip().startswith("#") or not lines[i].strip()):
            if lines[i].lstrip().startswith("#"):
                comments.append(lines[i].split("#", 1)[1])
            i -= 1
        for line in lines[start: node.end_lineno]:
            if "#" in line:
                comments.append(line.split("#", 1)[1])
        for name in names:
            found[name] = "\n".join(comments)

    return found


def _holds_a_number(value) -> bool:
    """True if the assigned value is, or contains, a numeric literal."""
    if value is None:
        return False
    for sub in ast.walk(value):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, (int, float)):
            if not isinstance(sub.value, bool):
                return True
    return False


def _uncited(source: str) -> list[str]:
    return [
        name for name, prose in _money_constants(source).items()
        if not _CITATION.search(prose)
    ]


# --- the control, against the real tree -------------------------------------------------

# THE DEBT REGISTER, and the only way past this control. A constant here is one this repo
# KNOWS is unsourced and has not yet been able to source; listing it makes the debt visible and
# countable instead of invisible, and anything NOT listed still fails. Adding a line here is a
# deliberate, reviewable act -- which is exactly what silently typing `150.0` was not.
#
# `FIXED_COST_MONTHLY` (saas/growth_mandate.py): £50/month company-wide overhead, comment reads
# "calibrate to match overhead ratio" -- an admitted placeholder, named as such in
# WORKER_FINDING_THE_SOURCED_ACQUISITION_MODEL_IS_UNWIRED_AND_THE_INVENTED_ONE_IS_LIVE.md §4.
# Ofgem's 2017 efficient operating-cost benchmark (£78/customer/year electricity, £89 gas) is a
# PER-CUSTOMER figure and this is a company-wide one, so it cannot be substituted without also
# deciding how overhead scales with the book -- a separate change to a separate cost line, and
# not one to smuggle into the acquisition repair. Registered 2026-08-28, still open.
_KNOWN_UNSOURCED: dict[str, tuple[str, ...]] = {
    "saas/growth_mandate.py": ("FIXED_COST_MONTHLY",),
    "saas/opex_ledger.py": (),
}


@pytest.mark.parametrize("relpath", _SCANNED)
def test_every_money_constant_on_the_acquisition_path_cites_a_source(relpath):
    uncited = [
        name for name in _uncited((_ROOT / relpath).read_text())
        if name not in _KNOWN_UNSOURCED[relpath]
    ]
    assert not uncited, (
        f"{relpath} declares money constant(s) with no cited source: {uncited}. "
        "This is how COST_PER_ACQUISITION = {'resi': 150.0, 'SME': 400.0} got into the live "
        "campaign. Cite the source in a comment above it (a docs/market_research/ path, or a "
        "named regulator/published rate card), or state that the value is a structural zero."
    )


@pytest.mark.parametrize("relpath", _SCANNED)
def test_the_debt_register_cannot_outlive_its_debt(relpath):
    """A stale exemption is a fail-open hole: if `FIXED_COST_MONTHLY` is later cited or
    renamed, its entry here would silently go on excusing whatever next takes that name. So
    every registered name must STILL exist and STILL be uncited -- clearing the debt forces
    the line out of the register in the same commit."""
    source = (_ROOT / relpath).read_text()
    still_uncited = set(_uncited(source))
    present = set(_money_constants(source))
    for name in _KNOWN_UNSOURCED[relpath]:
        assert name in present, f"{relpath}: {name} is registered as unsourced but is gone"
        assert name in still_uncited, (
            f"{relpath}: {name} now cites a source -- delete its line from _KNOWN_UNSOURCED."
        )


@pytest.mark.parametrize("relpath", _SCANNED)
def test_the_detector_has_a_non_empty_subject(relpath):
    """FAIL-OPEN guard: a green result must mean 'constants found and all cited', never
    'nothing matched'. If a rename empties the scan, this fails rather than passing."""
    assert _money_constants((_ROOT / relpath).read_text()), (
        f"{relpath} yielded zero money constants -- the control above is passing vacuously."
    )


def test_the_invented_table_is_gone_and_not_merely_shadowed():
    """The named defect: the constants must be DELETED, not re-pointed. A module still
    exporting `COST_PER_ACQUISITION` would let a caller reach an unsourced figure through the
    old name even if today's value came from the research."""
    import saas.growth_mandate as gm

    assert not hasattr(gm, "COST_PER_ACQUISITION")

    # And no assignment to that name survives anywhere in the file. Checked against the AST
    # rather than the text, because the comment that records WHAT WAS DELETED necessarily
    # names it, and a text search would fire on the tombstone instead of on a resurrection.
    source = (_ROOT / "saas/growth_mandate.py").read_text()
    assigned = {
        t.id
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for t in (node.targets if isinstance(node, ast.Assign) else [node.target])
        if isinstance(t, ast.Name)
    }
    assert "COST_PER_ACQUISITION" not in assigned


def test_the_live_path_spends_the_sourced_figure():
    """R1, at the seam the campaign actually reaches: the door's budget is the research's
    PCS commission, not the deleted £150."""
    from company.interfaces.growth_desk import decide_acquisition
    from saas.opex_ledger import CAC_ONE_OFF_GBP_PER_SINGLE_FUEL_CUSTOMER

    decision = decide_acquisition(
        segment="resi", commodity="gas",
        company_fwd_gbp_per_mwh=40.0, term_start="2019-01-01",
    )
    assert decision.budget_gbp == CAC_ONE_OFF_GBP_PER_SINGLE_FUEL_CUSTOMER["pcs_aggregator"]
    assert decision.budget_gbp != 150.0


def test_business_pays_no_one_off_because_it_pays_a_trail():
    """R2's pairing, asserted on BOTH sides so a future edit cannot delete one and keep the
    other: a broker-acquired segment costs 0.0 at signup AND accrues a non-zero trail on
    billed volume. Zeroing the one-off without the trail would make the book cheaper for
    free, which is the failure this pairing exists to catch."""
    from company.interfaces.growth_desk import broker_commission_schedule
    from saas.growth_mandate import _BROKER_ACQUIRED_SEGMENTS, cost_per_acquisition_gbp

    records = [
        {"customer_id": "B1", "settlement_date": "2019-03-04", "consumption_kwh": 10_000.0},
        {"customer_id": "R1", "settlement_date": "2019-03-04", "consumption_kwh": 10_000.0},
    ]
    customers = [
        {"customer_id": "B1", "segment": "SME"},
        {"customer_id": "R1", "segment": "resi"},
    ]

    for segment in _BROKER_ACQUIRED_SEGMENTS:
        assert cost_per_acquisition_gbp(segment) == 0.0

    schedule = broker_commission_schedule(settled_records=records, customers=customers)
    assert schedule, "a book with business volume must accrue a trail"
    # 10,000 kWh at the sourced 1.25p/kWh SME midpoint -- the resi account contributes £0.
    assert schedule == [{"month": "2019-03", "amount_gbp": 125.0}]


def test_the_trail_reaches_the_pnl_as_acquisition_cost():
    """R11-in-miniature: the schedule is not the claim, the posted account is. The trail must
    land in 6300 (Customer Acquisition and Retention) -- the same account the £400 one-off it
    replaced landed in -- so the P&L shows the cost moving shape, not disappearing."""
    from company.finance.double_entry import to_journal_entry
    from saas.ledger import make_broker_commission_event

    entry = to_journal_entry(make_broker_commission_event("2019-03", 125.0))
    assert entry is not None, "an unrouted event posts nowhere and silently costs nothing"
    assert entry["debit_account"] == "6300"
    assert entry["amount_gbp"] == 125.0


# --- R15: the detector's own mutation proof ---------------------------------------------

_UNCITED_MUTANT = '''
COST_PER_ACQUISITION: dict[str, float] = {
    "resi": 150.0,
    "SME": 400.0,
}
'''

_CITED_CONTROL = '''
# Midpoint of the £50-£60 dual-fuel PCS commission -- sourced, CMA Energy market
# investigation Appendix 8.3.
CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER: dict[str, float] = {"pcs_aggregator": 55.0}
'''


def test_the_detector_fires_on_an_uncited_constant():
    """The mutation is the real, deleted defect, restored verbatim."""
    assert _uncited(_UNCITED_MUTANT) == ["COST_PER_ACQUISITION"]


def test_the_detector_passes_a_cited_constant():
    """And is not always-red: the same detector, the same shape of constant, one citation."""
    assert _uncited(_CITED_CONTROL) == []


def test_the_detector_is_not_satisfied_by_the_constants_own_name():
    """TAUTOLOGY guard: a constant named after a source does not thereby cite one."""
    named_only = 'OFGEM_CAC_COST_GBP = 90.0\n'
    assert _uncited(named_only) == ["OFGEM_CAC_COST_GBP"]
