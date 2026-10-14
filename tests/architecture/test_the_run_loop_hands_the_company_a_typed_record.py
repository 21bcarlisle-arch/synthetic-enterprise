"""The run loop asks the renewal desk through ONE typed record, and that record carries nothing
world-only (director, 2026-10-11: "the supplier side reads only through the seam").

Four legs, each able to fail on its own defect, each with its mutation performed below:
  * WORLD IMPORT -- the record module imports from `sim/` or `simulation/`.
  * WIDENED RECORD -- a field joins that is not on the declared allow-list (the shape a world-only
    quantity would take on its way across).
  * DROPPED FIELD -- the desk adapter forgets to pass a field on, so the record declares an input
    the decision never receives.
  * BYPASSED RECORD -- the run loop goes back to handing the desk loose keywords.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect

import pytest

import company.interfaces.renewal_decision_inputs as record_module
import company.pricing.renewal_rate_chain as desk
import simulation.run_phase2b as run_loop
from company.interfaces import renewal_rate_chain as door
from company.interfaces.renewal_decision_inputs import RenewalDecisionInputs
from tools.python_code_text import imported_modules

#: The allow-list. Each is something the supplier holds (see the record's docstring). Adding a name
#: here is the act of declaring a new input company-observable, and should be argued in review.
ALLOWED_FIELDS = (
    "customer_id", "billing_account", "commodity", "term_start", "tariff_type", "term_index",
    "struck_unit_rate_per_mwh", "portfolio_margin_rates", "prior_term_margin", "prior_term_revenue",
    "is_domestic", "settled_records", "customer", "segment", "arrears_state", "receivable",
    "payment_method", "default_belief_rate", "own_default_tariff_inc_vat_per_mwh",
    # The company's own offer for the term: the floor its desk struck over (2026-10-12).
    "company_forward_per_mwh", "locked_policy_cost_per_mwh", "locked_network_cost_per_mwh",
    # What each term in its own margin history was priced to earn, off its own strike (2026-10-14).
    "portfolio_priced_for_rates",
)

WORLD_PACKAGES = ("sim", "simulation")


def world_imports(source: str) -> list[str]:
    modules = imported_modules(source)
    assert modules is not None, "the record module will not parse: a check that cannot look fails"
    return sorted(m for m in modules if m.split(".")[0] in WORLD_PACKAGES)


def declared_fields(source: str) -> list[str]:
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ClassDef) and node.name == "RenewalDecisionInputs":
            return [st.target.id for st in node.body
                    if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name)]
    raise AssertionError("RenewalDecisionInputs is not defined in the record module")


def loose_keyword_calls(source: str) -> list[int]:
    """Lines where the run loop calls the desk with loose keywords instead of the record."""
    out = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name == "decide_renewal_rate":
                out.append(node.lineno)
            elif name == "decide_renewal":
                arg = node.args[0] if node.args else None
                built = (isinstance(arg, ast.Call)
                         and getattr(arg.func, "id", None) == "RenewalDecisionInputs")
                if not built:
                    out.append(node.lineno)
    return out


def record_calls(source: str) -> int:
    return sum(1 for node in ast.walk(ast.parse(source))
               if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "decide_renewal")


RECORD_SOURCE = inspect.getsource(record_module)
RUN_LOOP_SOURCE = inspect.getsource(run_loop)


def test_the_record_imports_nothing_from_the_world():
    assert world_imports(RECORD_SOURCE) == []


def test_the_record_is_frozen_and_its_fields_are_the_allow_list():
    assert RenewalDecisionInputs.__dataclass_params__.frozen
    assert tuple(f.name for f in dataclasses.fields(RenewalDecisionInputs)) == ALLOWED_FIELDS
    assert tuple(declared_fields(RECORD_SOURCE)) == ALLOWED_FIELDS


def test_every_field_reaches_the_desk(monkeypatch):
    sentinels = {name: object() for name in ALLOWED_FIELDS}
    seen: dict = {}
    monkeypatch.setattr(desk, "decide_renewal_rate", lambda **kw: seen.update(kw) or "chain")
    assert door.decide_renewal(RenewalDecisionInputs(**sentinels)) == "chain"
    passed = {id(v) for v in seen.values()}
    missing = [n for n, v in sentinels.items() if id(v) not in passed]
    assert missing == [] and len(seen) == len(ALLOWED_FIELDS), missing


def test_the_run_loop_asks_through_the_record():
    # The branch must be reachable before its absence means anything: the loop DOES call the door.
    assert record_calls(RUN_LOOP_SOURCE) >= 1
    assert loose_keyword_calls(RUN_LOOP_SOURCE) == []


# ── mutations, performed ────────────────────────────────────────────────────────────────────────


def test_mutation_a_world_import_is_caught():
    mutated = RECORD_SOURCE.replace(
        "from dataclasses import dataclass\n",
        "from dataclasses import dataclass\n\nfrom simulation.household import household_of\n", 1)
    assert mutated != RECORD_SOURCE, "vacuity: the mutation did not apply"
    assert world_imports(mutated) == ["simulation", "simulation.household",
                                      "simulation.household.household_of"]


def test_mutation_a_world_only_field_is_caught():
    mutated = RECORD_SOURCE.replace(
        "    own_default_tariff_inc_vat_per_mwh: float | None = None\n",
        "    own_default_tariff_inc_vat_per_mwh: float | None = None\n"
        "    true_annual_kwh: float | None = None\n", 1)
    assert mutated != RECORD_SOURCE, "vacuity: the mutation did not apply"
    assert tuple(declared_fields(mutated)) != ALLOWED_FIELDS


def test_mutation_a_dropped_field_is_caught(monkeypatch):
    real = desk.decide_renewal_rate_from

    def drops_segment(inputs):
        return real(dataclasses.replace(inputs, segment=None))
    monkeypatch.setattr(desk, "decide_renewal_rate_from", drops_segment)
    with pytest.raises(AssertionError):
        test_every_field_reaches_the_desk(monkeypatch)


def test_mutation_a_bypassed_record_is_caught():
    mutated = RUN_LOOP_SOURCE.replace(
        "decide_renewal(RenewalDecisionInputs(", "decide_renewal(dict(", 1)
    assert mutated != RUN_LOOP_SOURCE, "vacuity: the mutation did not apply"
    assert loose_keyword_calls(mutated) != []
