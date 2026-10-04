"""PB6: the antecedent the world carries reaches the company, and changes what it believes.

PB4 made engagement recoverable IN THE WORLD. This is the other half: a trait that is learnable and
invisible at the wall satisfies the letter of R1's claim and none of its point.

Each test names the defect it exists to catch.
"""
from __future__ import annotations

import inspect

import pytest

from company.crm.enriched_churn_estimate import (
    enriched_churn_estimate,
    payment_method_engagement_factor,
)
from company.interfaces.sim_interface import LiveSimInterface, StubSimInterface


def test_the_seam_carries_the_payment_method_and_it_varies_by_household():
    """THE DEFECT: `sim_interface` carried no payment method at all, so the company could not see
    its own billing arrangement.

    Varying MATTERS as much as crossing: a seam that returned one method for every account would
    pass a "does it cross" test while making every downstream decision constant.
    """
    live = LiveSimInterface()
    methods = {live.get_payment_method(f"CUST{i:05d}") for i in range(400)}

    assert methods <= {"direct_debit", "standard_credit", "prepayment"}, methods
    assert len(methods) == 3, f"the seam must carry all three channels, saw {methods}"


def test_the_seam_agrees_with_the_world_rather_than_drawing_its_own():
    """A seam that redrew the trait would hand the company a household that does not exist.

    This is not hypothetical here: the tree already holds TWO independent draws of a household's
    payment method (`household_segments` and `payment_behaviour_source`) which agree on only 58.8%
    of households, exactly what chance gives. A third would have been worse than either.
    """
    from simulation.household_segments import payment_channel_for_customer

    live = LiveSimInterface()
    for i in range(200):
        cid = f"CUST{i:05d}"
        assert live.get_payment_method(cid) == payment_channel_for_customer(cid).value


def test_a_lookup_with_no_account_is_refused_by_name_and_not_booked_as_direct_debit():
    """PB6 EH-5. The old control asserted `get_payment_method(None) == "direct_debit"`. On the
    electricity leg `None` never reached the fallback: it drew as direct debit by chance, so the
    control stayed green with the fallback mutated to prepayment. Both fuels are asked here,
    because only the gas leg ever reached the except arm."""
    live = LiveSimInterface()
    for bad in (None, ""):
        for fuel in ("electricity", "gas"):
            with pytest.raises(ValueError, match="caller defect, not a CRM miss"):
                live.get_payment_method(bad, fuel)  # type: ignore[arg-type]


def test_every_id_shape_the_book_carries_resolves_without_the_refusal():
    """The refusal can fire, so it has to be shown not to fire on the ids a run actually passes:
    an electricity point, its gas leg, an I&C site, a successor after a home move, a drawn point."""
    from simulation.household_segments import payment_channel_for_customer

    live = LiveSimInterface()
    for cid in ("C1", "C1g", "C_IC1", "C1_2", "SYN-2021-001"):
        for fuel in ("electricity", "gas"):
            assert live.get_payment_method(cid, fuel) == payment_channel_for_customer(cid, fuel).value


def test_the_stub_can_be_made_to_vary_so_a_consumer_can_be_tested_at_all():
    stub = StubSimInterface()
    assert stub.get_payment_method("A") == "direct_debit"
    stub._payment_methods["A"] = "prepayment"
    assert stub.get_payment_method("A") == "prepayment"


def test_the_companys_churn_belief_actually_moves_with_the_observable():
    """DONE MEANS THE ANSWER CHANGED. An observable the company receives and does not use is the
    `no_caller_and_never_runs` class wearing a seam's clothes -- and this seam was built precisely
    because `vulnerability_index.assess_vulnerability` already takes a `has_ppm` argument and has
    no caller anywhere in the tree.

    IN A BOOK, NOT OUT OF ONE (re-keyed 2026-09-30). The prior is centred at 1.0, so outside a run
    scope the two channels read the same and it is the company's own leavers that move them apart.
    This book's prepayment customers leave at a third of its direct-debit customers' rate.
    """
    from company.crm.competitive_pressure import CompetitivePressureLedger, pressure_ledger_scope

    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    for method, n, losses in (("prepayment", 1000, 30), ("direct_debit", 4000, 360)):
        for _ in range(n):
            ledger.observe_renewal_decision(2018, 0.08, payment_method=method)
        for _ in range(losses):
            ledger.observe_competitive_loss(2018, payment_method=method)

    args = (100.0, 115.0, 2.0, 3000.0)
    with pressure_ledger_scope(ledger):
        dd = enriched_churn_estimate(*args, payment_method="direct_debit", renewal_year=2020)
        ppm = enriched_churn_estimate(*args, payment_method="prepayment", renewal_year=2020)

    assert ppm < dd * 0.75, (
        f"prepayment ({ppm:.4f}) must read as materially less likely to leave than direct debit "
        f"({dd:.4f}) on a book where it left at a third of the rate"
    )


def test_a_caller_that_does_not_pass_a_method_is_bit_for_bit_unchanged():
    """The other branch, and the one that protects every existing caller. Without it the factor
    could apply a blanket uplift to the whole book and the test above would still pass."""
    args = (100.0, 115.0, 2.0, 3000.0)

    assert payment_method_engagement_factor(None) == 1.0
    assert payment_method_engagement_factor("a method nobody has heard of") == 1.0
    assert enriched_churn_estimate(*args) == enriched_churn_estimate(*args, payment_method=None)


def test_the_company_reads_the_published_statistic_and_not_the_worlds_parameter():
    """THE WALL QUESTION, asked of the thing that would be easiest to get wrong here.

    The company is entitled to Ofgem's published CIM survey -- a regulator's public statistic is
    exactly what a real supplier reads. It is NOT entitled to `simulation.household_segments`'s own
    `CIM_SWITCH_RATE_BY_CHANNEL`, even though the two carry the same numbers from the same source:
    importing the world's copy would make the company's belief move whenever the WORLD's parameter
    moved, which is the company reading ground truth by a side channel.
    """
    source = inspect.getsource(
        __import__("company.crm.enriched_churn_estimate", fromlist=["x"])
    )
    assert "simulation" not in source and "from sim" not in source, (
        "the company's churn model must not reach into the world for this figure"
    )


def test_the_run_hands_the_company_its_payment_method_through_the_seam():
    """THE DEFECT: PB7 wired the run and resolved the method by importing the world's
    `payment_channel_for_customer` directly, so the only production route around the seam PB6
    built was the one every run took. Same value today; but anything the seam models that the
    world function does not would reach tests and never a run.

    Read from the AST, not the text, so the comment that names the old route cannot satisfy it.
    It also demands the assignment EXISTS: a run that stopped passing the method at all is PB6's
    original defect and must not read as compliance.
    """
    import ast
    from pathlib import Path

    tree = ast.parse(Path("simulation/run_phase2b.py").read_text(encoding="utf-8"))
    # Every value assigned except the `None` an I&C account keeps.
    routes = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "_company_payment_method" for t in node.targets)
        and not (isinstance(node.value, ast.Constant) and node.value.value is None)
    ]
    assert routes, "the run no longer hands the company a payment method at all"
    for value in routes:
        assert (isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute)
                and value.func.attr == "get_payment_method"), (
            f"the run resolves the company's payment method via {ast.unparse(value)}, "
            "not SimInterface.get_payment_method"
        )


def test_every_method_read_in_the_run_asks_on_the_accounts_own_fuel():
    """THE DEFECT: `_book_method_of`, the method register the own-book default belief learns over,
    asked `get_payment_method(cid, "electricity", ...)` of every resi account, gas legs and gas-only
    households included. The seam's gas branch finds a stop on the leg the run billed; asked on
    electricity, a gas account's own stop never reached the row its provisions were read on.

    Keyed to the property, not to today's call sites: no read of the method in the run may pin its
    fuel as a literal. It also demands the register's own read exists, so deleting it cannot pass.
    """
    import ast
    from pathlib import Path

    tree = ast.parse(Path("simulation/run_phase2b.py").read_text(encoding="utf-8"))
    register = [n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "_book_method_of"]
    assert register, "the run no longer holds the own-book method register at all"
    in_register = [n for n in ast.walk(register[0])
                   if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                   and n.func.attr == "get_payment_method"]
    assert in_register, "the own-book method register no longer reads the seam"
    reads = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "get_payment_method"]
    for call in reads:
        fuel = call.args[1] if len(call.args) > 1 else next(
            (k.value for k in call.keywords if k.arg == "fuel"), None)
        assert fuel is not None and not isinstance(fuel, ast.Constant), (
            f"{ast.unparse(call)} asks on a fixed fuel (or the seam's electricity default), "
            "not the account's own")
