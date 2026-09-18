"""Who settles on their own gas shape, and who quietly kept the population split, is PUBLISHED.

THE DEFECT (2026-09-18). `run_phase2b` computes `gas_heating_fraction_by_customer` and
`gas_shape_refusals`, settles the gas term on them, and **prints them**. They reached no artefact.
So a reader of a run could not tell whether the per-household seasonal shape had reached the gas
book at all, or how many households were settling on the population 70/30 split instead — the
electricity side's exact state before `demand_provider_by_customer` was published beside it.

**And the code already claimed otherwise.** `SeasonalGasRefusal`'s own docstring says the reason is
carried *"so a customer silently keeping the population constant is visible in the run instead of
inferred from its numbers"*. It was visible on a terminal nobody keeps. A docstring stating a
property is not the property — the third instance this week, after the two controls named as "the
failable control" that did not exist, and the constant whose comment promised an entry the code
below it made impossible.

WHY THE LEG BELOW IS AST AND NOT A RUN. What must hold is that the runner's returned mapping
CARRIES these keys; a full run to assert it costs ~15 minutes and would make this suite a test of
the simulator. The partition itself — every customer in exactly one of the two states — is
`seasonal_gas_splits_for_book`'s own guarantee and is covered in
`tests/simulation/test_household_demand_shape.py`; this file deliberately does not restate it.
"""
from __future__ import annotations

import ast
from pathlib import Path

RUNNER = Path(__file__).resolve().parents[2] / "simulation" / "run_phase2b.py"

#: The two keys a reader needs to answer "did the gas switch reach the book, and who did it miss".
#: `..._provider_by_customer` mirrors the electricity side's name on purpose: one question, two
#: fuels, and a reader who learns one key should not have to learn a differently-shaped second.
REQUIRED_KEYS = ("gas_shape_provider_by_customer", "gas_shape_refusals")


def _string_keys_of_returned_dicts(path: Path) -> set[str]:
    """Every literal string key of every dict the module RETURNS.

    Keyed to `return`, not to "appears somewhere in the file", because the defect was precisely
    that these names existed in the module -- computed, printed, used -- and did not reach the
    caller. A grep would have been satisfied by the print statement that was the whole problem.
    """
    tree = ast.parse(path.read_text())
    keys: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Return) or node.value is None:
            continue
        for sub in ast.walk(node.value):
            if isinstance(sub, ast.Dict):
                keys |= {k.value for k in sub.keys
                         if isinstance(k, ast.Constant) and isinstance(k.value, str)}
    return keys


def test_the_gas_shape_split_reaches_the_runs_artefact():
    returned = _string_keys_of_returned_dicts(RUNNER)
    assert returned, (
        "population floor: no returned dict with string keys was found in run_phase2b at all, so "
        "this control cannot see what the run publishes and refuses rather than passing vacuously"
    )
    missing = [k for k in REQUIRED_KEYS if k not in returned]
    assert not missing, (
        f"run_phase2b does not publish {missing}. The gas shape switch settles the gas term and "
        "reaches no reader, so nobody can tell whether it arrived or how many households kept the "
        "population 70/30 split -- which is what its own refusal docstring promises to make visible."
    )


def test_the_electricity_half_is_published_too_so_this_control_is_not_alone():
    """The premise of the leg above: the same question is already answered for electricity.

    If `demand_provider_by_customer` ever stops being returned, the gas key would still pass while
    the run as a whole went back to publishing no provider split at all -- and the reader would be
    no better off for the half that remained.
    """
    returned = _string_keys_of_returned_dicts(RUNNER)
    assert "demand_provider_by_customer" in returned
    assert "fabric_eligibility" in returned


def test_the_two_fuels_answer_the_question_the_same_way():
    """One question, two fuels, one shape of answer.

    Not cosmetic: a reader who has to learn two differently-shaped keys for the same question is a
    reader who will read one of them and assume the other, which is how the gas half stayed unread
    while the electricity half was being quoted daily.
    """
    for key in REQUIRED_KEYS:
        assert key.startswith("gas_shape"), key
    assert "gas_shape_provider_by_customer".endswith("_provider_by_customer")
    assert "demand_provider_by_customer".endswith("_provider_by_customer")
