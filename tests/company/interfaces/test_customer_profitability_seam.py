"""KNIFE pass 3, `A_composition_lift` step 22 (§3q) — the renewal-repricing door.

One crossing cut: `simulation.run_phase2b` no longer imports
`company.crm.customer_profitability`. It reports the renewal as it happened and
adds whatever `company/interfaces/customer_profitability.py` hands back.

The controls in this file, and what each can actually fail on:

1. READ DIRECTION (behavioural, not a grep) — run the company module in a clean
   interpreter and ask the import system which world modules it loaded. The
   mutation adds a lazy `simulation` import and the SAME detector reports it.
2. NO NUMBER MOVES — replay the pre-cut expression (the world's own `if`, then
   `compute_profitability_uplift`) against the door over a matrix of renewals
   that includes every eligibility arm, and compare the number. This is the
   control that would fail if the lift changed an answer.
3. THE INVITED DEFECT — FOUR BRANCHES BECAME FOUR FIELDS. This is the THIRD
   consecutive step to record this shape (§3o's branch-became-a-field, §3p's
   instrument field) and the recurrence is the point: a composition lift turns
   control flow the caller could not fake into data the caller supplies. Before
   the cut, applying the uplift to a gas or deemed term meant editing a visible
   `if`; now it means passing a wrong string, and every test that drives the
   door directly stays green because the door did what it was told. An AST check
   over the REAL call site in `simulation/run_phase2b.py` asserts that every
   argument is a variable the renewal loop computed and not a literal, with a
   vacuity guard on the count, and two mutations perform the defect.
4. THE GATE ACTUALLY GATES — each of the four eligibility arms is asserted to
   change the answer, and deleting one on a copy of the module is caught.

VACUITY. `test_the_matrix_is_not_degenerate` asserts that the fixture produces a
NON-ZERO uplift on the eligible arm and zero on each ineligible one — a matrix
where every case returned 0.0 would make controls 2 and 4 compare two zeroes.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import uuid

import pytest

from company.crm.customer_profitability import compute_profitability_uplift
from company.interfaces import customer_profitability as door

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
# CONTROL 3's SUBJECT MOVED, and the control moved with it. Step 22 cut this
# door with `simulation/run_phase2b.py` as the caller. KNIFE step 24 (§3s) put
# the whole renewal rate chain behind `company/interfaces/renewal_rate_chain.py`
# and the uplift is now called from the supplier's own chain, in order, rather
# than from the world's loop. Control 3 is about the CALL SITE — that literals
# never re-decide eligibility outside the door — so it follows the call site.
# Pointing it at run_phase2b.py after step 24 would make it a control over a
# call that is not there: a fail-open, caught here by its own vacuity guard.
CALLER_MODULE_PATH = os.path.join(REPO_ROOT, "company", "pricing", "renewal_rate_chain.py")
IMPL_PATH = os.path.join(REPO_ROOT, "company", "crm", "customer_profitability.py")

ACCOUNT = "C4"
TERM_START = "2019-04-01"

# The account's own settled book. The prior term (2018-04-01) ran at a loss on
# BOTH legs, so every eligible row of the matrix below returns the same non-zero
# uplift whichever book it is read from. That is deliberate for controls 2 and 4
# and USELESS for the threading question -- see SPLIT_SIGN_RECORDS.
SETTLED_RECORDS = [
    {
        "customer_id": ACCOUNT, "commodity": "electricity",
        "settlement_date": f"2018-{month:02d}-28", "term_start": "2018-04-01",
        "net_margin_gbp": -14.20,
    }
    for month in (5, 6, 7, 8)
] + [
    {
        "customer_id": ACCOUNT, "commodity": "gas",
        "settlement_date": f"2018-{month:02d}-28", "term_start": "2018-04-01",
        "net_margin_gbp": -31.00,
    }
    for month in (5, 6, 7, 8)
] + [
    # A SETTLED, LOSS-MAKING BOOK ON A FUEL THIS SUPPLIER DOES NOT SELL. Without
    # it the commodity gate's mutation is unkillable for the flattering reason:
    # delete the gate and 'hydrogen' passes into `estimate_prior_term_net_margin`,
    # which finds no hydrogen records, returns None, and the door answers 0.0 --
    # the same number the gate gives, so the control goes green on a gate that is
    # doing nothing. The gate's actual claim is "a fuel outside
    # `UPLIFTABLE_COMMODITIES` is refused EVEN WHERE THERE IS A BOOK TO REPRICE",
    # and only a populated book can put that claim at risk.
    {
        "customer_id": ACCOUNT, "commodity": "hydrogen",
        "settlement_date": f"2018-{month:02d}-28", "term_start": "2018-04-01",
        "net_margin_gbp": -22.50,
    }
    for month in (5, 6, 7, 8)
]

# THE SAME ACCOUNT WITH THE TWO LEGS ON OPPOSITE SIDES OF ZERO. `SETTLED_RECORDS`
# above cannot answer "which book did this renewal read", because both books say
# net-negative and the uplift is a flat constant -- reading the wrong one returns
# the right number. This fixture is the discriminator: electricity lost money and
# gas made it, so a gas renewal priced off the electricity leg is repriced when it
# should not be, and the two answers are 5.0 and 0.0 rather than 5.0 and 5.0.
#
# It is not hypothetical on this world's book: 87 of 164 settled accounts are dual
# fuel, so the account whose gas leg would be priced off its electricity leg is the
# MAJORITY case, and the wrong answer is a populated plausible one.
SPLIT_SIGN_RECORDS = [
    {
        "customer_id": ACCOUNT, "commodity": "electricity",
        "settlement_date": f"2018-{month:02d}-28", "term_start": "2018-04-01",
        "net_margin_gbp": -14.20,
    }
    for month in (5, 6, 7, 8)
] + [
    {
        "customer_id": ACCOUNT, "commodity": "gas",
        "settlement_date": f"2018-{month:02d}-28", "term_start": "2018-04-01",
        "net_margin_gbp": +31.00,
    }
    for month in (5, 6, 7, 8)
]

# (label, commodity, tariff_type, term_index, locked_unit_rate)
MATRIX = [
    ("eligible: renewed electricity fixed", "electricity", "fixed", 1, 142.5),
    ("eligible: renewed electricity pass-through", "electricity", "pass_through", 2, 155.0),
    # GAS IS AN ELIGIBLE ARM FROM 2026-09-07, not a refused one. It sat in the
    # refused block below on the ground that the arm's inputs had never been fitted
    # to it; every one of those inputs now takes the renewal's own commodity.
    ("eligible: renewed gas fixed", "gas", "fixed", 1, 42.0),
    ("acquisition term", "electricity", "fixed", 0, 142.5),
    # THE COMMODITY GATE'S REMAINING SUBJECT. `UPLIFTABLE_COMMODITIES` is a set of
    # the fuels this supplier sells, so the arm this gate refuses is a fuel it does
    # not -- which is what keeps the gate reachable now that gas passes it.
    ("unsupported commodity", "hydrogen", "fixed", 1, 42.0),
    ("deemed", "electricity", "deemed", 1, 142.5),
    ("flex", "electricity", "flex", 1, 142.5),
    ("no locked rate", "electricity", "fixed", 1, None),
    ("no tariff type at all", "electricity", None, 1, 142.5),
]
ELIGIBLE_LABELS = {MATRIX[0][0], MATRIX[1][0], MATRIX[2][0]}


def _pre_cut(commodity, tariff_type, term_index, locked_unit_rate, records=None):
    """The eligibility rule spelled with LITERALS, outside the door.

    This began as the exact expression `run_phase2b.py::main()` ran before step
    22, and control 2's job was that the composition lift moved no number. The
    rule it restates has since been CHANGED on purpose -- gas admitted, 2026-09-07
    -- so the literal `commodity == "electricity"` was updated with it rather than
    left to fail. Every other arm is untouched, so the lift is still what this
    comparison proves on the rows that did not move.

    It passes `commodity=` down for the same reason the door does: a restatement
    that read one book for both fuels would agree with a door that did the same,
    and control 2 would go green on the defect it exists to catch.
    """
    if (locked_unit_rate is not None and term_index >= 1
            and commodity in ("electricity", "gas")
            and tariff_type in ("fixed", "pass_through")):
        return compute_profitability_uplift(
            ACCOUNT, TERM_START, records if records is not None else SETTLED_RECORDS,
            commodity=commodity)
    return 0.0


def _door(commodity, tariff_type, term_index, locked_unit_rate, module=door, records=None):
    return module.renewal_unit_rate_uplift(
        account_id=ACCOUNT,
        commodity=commodity,
        tariff_type=tariff_type,
        term_index=term_index,
        term_start=TERM_START,
        locked_unit_rate=locked_unit_rate,
        settled_records=records if records is not None else SETTLED_RECORDS,
    )


def _impl_source() -> str:
    with open(IMPL_PATH) as fh:
        return fh.read()


def _load_mutated_impl(source: str):
    modname = f"_knife3_step22_pnl_mutant_{uuid.uuid4().hex}"
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, modname + ".py")
        with open(path, "w") as fh:
            fh.write(source)
        spec = importlib.util.spec_from_file_location(modname, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[modname] = module
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(modname, None)
    return module


# ---------------------------------------------------------------------------
# VACUITY — the matrix must be able to fail the controls that read it.
# ---------------------------------------------------------------------------


def test_the_matrix_is_not_degenerate():
    for label, commodity, tariff_type, term_index, rate in MATRIX:
        got = _door(commodity, tariff_type, term_index, rate)
        if label in ELIGIBLE_LABELS:
            assert got > 0.0, f"{label!r} returned no uplift — controls 2 and 4 cannot fail"
        else:
            assert got == 0.0, f"{label!r} was repriced — it is not an ineligible arm"


# ---------------------------------------------------------------------------
# CONTROL 1 — the company module must not reach back into the world.
# ---------------------------------------------------------------------------

_PROBE = textwrap.dedent(
    """
    import json, sys
    sys.path.insert(0, {repo!r})
    sys.path.insert(0, {pkgdir!r})
    import {modname} as m

    m.renewal_unit_rate_uplift(
        account_id="C4", commodity="electricity", tariff_type="fixed",
        term_index=1, term_start="2019-04-01", locked_unit_rate=142.5,
        settled_records=[
            {{"customer_id": "C4", "commodity": "electricity",
              "settlement_date": "2018-05-28", "term_start": "2018-04-01",
              "net_margin_gbp": -14.2}},
        ],
    )

    walled = sorted(
        n for n in sys.modules
        if n in ("sim", "simulation") or n.startswith(("sim.", "simulation."))
    )
    print("WALLED_MODULES=" + json.dumps(walled))
    """
)


def _walled_modules_loaded_by(source: str) -> list[str]:
    """THE detector, used unchanged by both the real test and its mutation."""
    with tempfile.TemporaryDirectory() as pkgdir:
        modname = "_knife3_step22_pnl_subject"
        with open(os.path.join(pkgdir, modname + ".py"), "w") as fh:
            fh.write(source)
        probe = _PROBE.format(repo=REPO_ROOT, pkgdir=pkgdir, modname=modname)
        proc = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=pkgdir, capture_output=True, text=True, timeout=300,
        )
    assert proc.returncode == 0, (
        f"the probe itself failed — an unavailable check is a FAILED check, "
        f"never a skip.\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    marker = [ln for ln in proc.stdout.splitlines() if ln.startswith("WALLED_MODULES=")]
    assert len(marker) == 1, f"probe produced no verdict line:\n{proc.stdout}"
    return json.loads(marker[0].split("=", 1)[1])


def test_deciding_the_uplift_loads_no_world_module():
    assert _walled_modules_loaded_by(_impl_source()) == []


def test_mutation_a_lazy_world_import_is_caught_by_the_same_detector():
    mutated = _impl_source()
    anchor = "    if locked_unit_rate is None:"
    assert anchor in mutated, "anchor moved — this mutation is no longer the defect"
    mutated = mutated.replace(
        anchor,
        "    from simulation.policy_costs import get_gas_ccl_per_mwh  # noqa: F401  <-- the defect\n"
        + anchor,
        1,
    )
    assert "simulation.policy_costs" in _walled_modules_loaded_by(mutated), (
        "the mutation did not take — control 1 is not testing what it claims"
    )


# ---------------------------------------------------------------------------
# CONTROL 2 — NO NUMBER MOVES, on every arm of the eligibility rule.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "label,commodity,tariff_type,term_index,rate",
    MATRIX,
    ids=[m[0] for m in MATRIX],
)
def test_the_door_reproduces_the_pre_cut_uplift(label, commodity, tariff_type, term_index, rate):
    assert _door(commodity, tariff_type, term_index, rate) == _pre_cut(
        commodity, tariff_type, term_index, rate
    )


def test_the_uplift_is_the_supplier_s_own_constant():
    from company.crm.customer_profitability import NET_NEGATIVE_UPLIFT_GBP_PER_MWH

    assert _door("electricity", "fixed", 1, 142.5) == NET_NEGATIVE_UPLIFT_GBP_PER_MWH


# ---------------------------------------------------------------------------
# CONTROL 3 — the invited defect, at the REAL call site.
# ---------------------------------------------------------------------------


def _uplift_callsites(source: str) -> list[ast.Call]:
    return [
        node for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "renewal_unit_rate_uplift"
    ]


def _literal_kwargs(call: ast.Call) -> set[str]:
    """Which arguments were typed at the call site rather than observed."""
    return {kw.arg for kw in call.keywords if isinstance(kw.value, ast.Constant)}


def test_the_world_passes_what_it_observed_and_never_a_literal():
    with open(CALLER_MODULE_PATH) as fh:
        source = fh.read()
    calls = _uplift_callsites(source)
    # VACUITY GUARD — a source with no such call would make the loop below pass
    # over an empty set.
    assert len(calls) == 1, (
        f"expected exactly one renewal_unit_rate_uplift call in "
        f"{os.path.basename(CALLER_MODULE_PATH)}, found {len(calls)} — control 3 "
        "is examining the wrong thing"
    )
    call = calls[0]
    assert not call.args, "the call must be keyword-only so the arguments are named"
    assert {kw.arg for kw in call.keywords} == {
        "account_id", "commodity", "tariff_type", "term_index",
        "term_start", "locked_unit_rate", "settled_records",
    }
    assert _literal_kwargs(call) == set(), (
        "an argument to the repricing door is a literal at the call site: "
        f"{sorted(_literal_kwargs(call))}. The eligibility branches this cut "
        "moved behind the door became FIELDS; a literal here re-decides "
        "eligibility in the world and hides it from the door."
    )


@pytest.mark.parametrize(
    "defect,expected",
    [
        ('commodity=commodity,', 'commodity="electricity",'),
        ('tariff_type=tariff_type,', 'tariff_type="fixed",'),
    ],
    ids=["hardcoded commodity", "hardcoded tariff type"],
)
def test_mutation_a_hardcoded_argument_is_caught(defect, expected):
    """Perform the defect on a COPY of the caller's source — never on the repo
    file, which would corrupt `inspect.getsource` for a concurrent run."""
    with open(CALLER_MODULE_PATH) as fh:
        source = fh.read()
    assert defect in source, "anchor moved — this mutation is no longer the defect"
    mutated = source.replace(defect, expected, 1)
    calls = _uplift_callsites(mutated)
    assert len(calls) == 1
    assert _literal_kwargs(calls[0]), (
        "the same detector did not fire on the hardcoded argument — control 3 "
        "cannot catch the defect it was written for"
    )


def test_the_defect_this_control_guards_would_change_a_real_answer():
    """Not hypothetical, and the defect it names MOVED when gas was admitted.

    Until 2026-09-07 a hardcoded `commodity="electricity"` at the call site made
    the door reprice a gas renewal it should have refused, and this asserted the
    refusal. Gas is eligible now, so the refusal is gone and the SAME literal
    causes the deeper version of the same error: the gas renewal is priced, off
    the account's ELECTRICITY book. `SPLIT_SIGN_RECORDS` puts the two legs on
    opposite sides of zero so the two readings give different answers.
    """
    assert _door("gas", "fixed", 1, 42.0, records=SPLIT_SIGN_RECORDS) == 0.0, (
        "the gas leg made money in this fixture, so a gas renewal read off its OWN "
        "book carries no unprofitability uplift"
    )
    assert _door("electricity", "fixed", 1, 42.0, records=SPLIT_SIGN_RECORDS) > 0.0, (
        "the electricity leg lost money, so the hardcoded literal this control "
        "guards would have handed the gas renewal a repricing it has not earned"
    )
    # AND THE COMMODITY IS NOT MERELY ACCEPTED, IT IS SPENT. A door that took the
    # argument and dropped it before `compute_profitability_uplift` would pass
    # every assertion above only if the two readings agreed -- they do not.
    assert _door("gas", "fixed", 1, 42.0, records=SPLIT_SIGN_RECORDS) != _door(
        "electricity", "fixed", 1, 42.0, records=SPLIT_SIGN_RECORDS)


# ---------------------------------------------------------------------------
# CONTROL 4 — the gate actually gates.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "arm,gate",
    [
        ("acquisition term", "    if term_index < MIN_TERM_INDEX_FOR_UPLIFT:\n        return 0.0\n"),
        ("unsupported commodity",
         "    if commodity not in UPLIFTABLE_COMMODITIES:\n        return 0.0\n"),
        ("deemed", "    if tariff_type not in UPLIFTABLE_TARIFF_TYPES:\n        return 0.0\n"),
    ],
)
def test_mutation_deleting_an_eligibility_gate_is_caught(arm, gate):
    source = _impl_source()
    assert gate in source, "anchor moved — this mutation is no longer the defect"
    mutant = _load_mutated_impl(source.replace(gate, "", 1))
    label, commodity, tariff_type, term_index, rate = next(m for m in MATRIX if m[0] == arm)
    assert _door(commodity, tariff_type, term_index, rate) == 0.0
    assert _door(commodity, tariff_type, term_index, rate, module=mutant) > 0.0, (
        f"deleting the {arm!r} gate did not reprice the {arm!r} renewal — the "
        "gate is not what this control says it is"
    )
