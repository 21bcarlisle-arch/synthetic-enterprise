"""The cause of a departure is ground truth, and the company has no observable for it.

C2 puts a `departure_cause` and its factor decomposition on the world's lifecycle-event dict. That
dict is passed whole into `company/analytics/**`, so the fields are one attribute lookup away from
company code -- which is exactly the leak pre-registration P3 names:

    *"If `churn_estimate_error_pct` NARROWS, something has leaked -- the most likely leak being a
    cause label reaching a company module. That would be a wall breach and the change would be
    reverted, not kept."*

A real supplier knows THAT a customer left and can guess why. It cannot read the reason off the
world. If a company module could, every downstream inference result would be measuring the label
rather than the inference, and P3 would invert for a reason that has nothing to do with modelling.

Same enforcement pattern as `engagement_level`, which carries the same "MUST NEVER be read by
company/** decision code" note at its emission site in `simulation/customer_events.py`.
"""
import ast
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent.parent
COMPANY = PROJECT / "company"

#: Ground-truth fields C2 emits on the lifecycle event. Kept in sync with the emission site by
#: `test_the_guarded_names_are_the_ones_actually_emitted` below, so this list cannot silently fall
#: behind the code it guards -- a scope that shrinks while the control stays green is the
#: parametrised-control failure this repository has hit before.
C2_GROUND_TRUTH_FIELDS = frozenset({
    "departure_cause",
    "sim_bill_shock_base",
    "sim_market_opportunity",
    "sim_price_response",
    "sim_action_propensity",
    "sim_dissatisfaction_response",
    # The year's departure LEVEL, added 2026-08-30 with the level anchor. It belongs here for a
    # sharper reason than the others: it is the published GB switching rate divided by the world's
    # own factor population, so a company module reading it would know exactly how many of its
    # accounts are going to leave this year before any of them did. No real supplier has that.
    # The guard below is what put this line here -- it went red on the new name the same commit
    # the name appeared, which is the whole point of reading the emission site back.
    "sim_level_anchor",
})


def _company_sources() -> list[Path]:
    return sorted(p for p in COMPANY.rglob("*.py") if "__pycache__" not in p.parts)


def test_no_company_module_reads_a_departure_cause_or_its_decomposition():
    """DEFECT: a company module reading the world's own answer instead of inferring it."""
    sources = _company_sources()
    # FAIL CLOSED. A scan that finds no files to scan reports "clean" and means nothing -- the
    # failure mode `test_no_tree_scan_passes_on_an_empty_population` exists for.
    assert len(sources) > 20, f"only {len(sources)} company modules found -- the scan lost its subject"

    offenders = []
    for path in sources:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            # `evt["departure_cause"]` and `evt.get("departure_cause")` are the two shapes the
            # existing readers of this dict actually use.
            if isinstance(node, ast.Constant) and node.value in C2_GROUND_TRUTH_FIELDS:
                offenders.append(f"{path.relative_to(PROJECT)}:{node.lineno} -> {node.value!r}")
            elif isinstance(node, ast.Attribute) and node.attr in C2_GROUND_TRUTH_FIELDS:
                offenders.append(f"{path.relative_to(PROJECT)}:{node.lineno} -> .{node.attr}")

    assert not offenders, (
        "company/** reads the world's departure ground truth -- epistemic wall breach:\n  "
        + "\n  ".join(offenders)
    )


def test_the_guarded_names_are_the_ones_actually_emitted():
    """DEFECT, and it is the one that makes the control above rot silently: a field renamed or a
    new cause field added at the emission site while this guard keeps checking the old names.

    The guard would stay green while guarding nothing. So the emitted set is read back out of
    `simulation/customer_events.py` and compared, rather than trusted to have been kept in step.
    """
    source = (PROJECT / "simulation" / "customer_events.py").read_text()
    tree = ast.parse(source)
    emitted = {
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and (node.value.startswith("sim_") or node.value == "departure_cause")
    }
    assert emitted, "no C2 ground-truth fields found at the emission site -- has it been renamed?"
    missing = emitted - C2_GROUND_TRUTH_FIELDS
    assert not missing, (
        f"customer_events.py emits ground-truth fields this guard does not cover: {sorted(missing)}"
    )


@pytest.mark.parametrize("field", sorted(C2_GROUND_TRUTH_FIELDS))
def test_the_guard_can_see_each_field_individually(field, tmp_path):
    """DEFECT: a guard that only catches one of the names it claims to cover.

    Parametrised over the guarded set with a synthetic offender, because parametrising over the
    real tree would make every case pass by finding nothing -- a control drawing its cases from the
    thing it checks cannot see its own scope shrink.
    """
    tree = ast.parse(f'def f(evt):\n    return evt["{field}"]\n')
    hits = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and n.value in C2_GROUND_TRUTH_FIELDS
    ]
    assert hits, f"the guard's matcher does not detect a read of {field!r}"
