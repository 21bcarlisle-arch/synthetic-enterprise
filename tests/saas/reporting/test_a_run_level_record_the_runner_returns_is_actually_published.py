"""A record the runner returns has to reach the artefact, and a whitelist is where they stop.

THE DEFECT, FOUR TIMES (2026-09-23, and the dict's own comment counted the first three).
`annual_report`'s run-level dict is a WHITELIST: it names the keys it forwards from `run_phase2b`'s
result, and anything the runner returns that is not named here is dropped silently. Its own comment
says so — *"that guarantee is false while this whitelist drops them... Third recorded instance of
the silent-drop class in this dict."*

The fourth was mine, and the way I missed it is the point. On 2026-09-18 I taught `run_phase2b` to
return `gas_shape_provider_by_customer` and `gas_shape_refusals` — who settles on their own seasonal
gas shape and who keeps the population 70/30 split — and wrote a control asserting the runner
**returns** them. It does. The run of 2026-09-23T10:15Z carried that code and published neither key.

**Returned is not published, and a control keyed to the return cannot see the whitelist.** That is
the structural gap this file closes: instead of checking one key, it checks that every per-customer
PROVIDER or ELIGIBILITY record the runner exposes is forwarded. Instance five would have to add a
key the runner returns and not add it here, and that is exactly what this fails on.

WHY THE RULE IS "PROVIDER OR ELIGIBILITY RECORD" AND NOT "EVERY KEY". A whitelist is a legitimate
design — the runner's result carries per-account traces and ledgers far too large for a published
artefact, and forwarding everything would be a different defect. What must not be droppable is the
class of record that answers *which mechanism settled this account, and why not the other one*,
because that is the question a reader of a run whose margin moved needs first and cannot reconstruct
from the numbers.
"""
from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path

from saas.reporting import annual_report

REPORT_MODULE = Path(inspect.getfile(annual_report))
RUNNER_MODULE = REPORT_MODULE.parents[2] / "simulation" / "run_phase2b.py"

#: A run-level record naming which mechanism settled each account, or why one was refused. The
#: pattern is deliberately about the SHAPE of the name rather than a list of today's keys: a list
#: would have to be updated by the same person who forgot the whitelist.
RECORD_PATTERN = re.compile(r"(provider_by_customer|_eligibility|_refusals)$")


def _returned_keys(path: Path) -> set[str]:
    """Literal string keys of every dict the module RETURNS."""
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


def _forwarded_keys(path: Path) -> set[str]:
    """Keys this module forwards out of the runner's result.

    Matched on the CALL -- `phase2b.get("name", ...)` -- rather than on the key appearing in the
    file, because the failure being caught is precisely a key that exists everywhere except in the
    forwarding dict.
    """
    tree = ast.parse(path.read_text())
    keys: set[str] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get" and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            target = node.func.value
            if isinstance(target, ast.Name) and target.id == "phase2b":
                keys.add(node.args[0].value)
    return keys


def test_every_settlement_record_the_runner_returns_is_forwarded():
    """The structural leg. Adding a provider record to the runner and not here fails HERE."""
    returned = _returned_keys(RUNNER_MODULE)
    assert returned, (
        "population floor: no returned dict with string keys was found in run_phase2b, so this "
        "control cannot see what the runner exposes and refuses rather than passing vacuously"
    )
    records = {k for k in returned if RECORD_PATTERN.search(k)}
    assert records, (
        "population floor: the runner returns no provider/eligibility/refusal record at all. Either "
        f"the naming convention moved (pattern {RECORD_PATTERN.pattern!r}) and this control is now "
        "blind, or the run stopped recording which mechanism settled each account."
    )
    forwarded = _forwarded_keys(REPORT_MODULE)
    assert forwarded, "population floor: the report forwards nothing from phase2b"

    dropped = sorted(records - forwarded)
    assert not dropped, (
        f"run_phase2b returns {dropped} and the annual report's whitelist does not forward them, so "
        "they reach no artefact and no reader. This is the silent-drop class the dict's own comment "
        "has already counted three times; returned is not published."
    )


def test_the_electricity_records_are_forwarded_so_this_control_is_not_vacuous():
    """The premise of the leg above: these were the ones that DID reach a reader.

    If they ever stop being forwarded, the leg above still passes for the gas half while the run as
    a whole goes back to publishing no provider split -- and a reader is no better off for the half
    that survived.
    """
    forwarded = _forwarded_keys(REPORT_MODULE)
    for key in ("demand_provider_by_customer", "fabric_eligibility"):
        assert key in forwarded, f"{key} is no longer forwarded out of the runner's result"


def test_the_gas_half_is_forwarded_by_name():
    """The fourth instance, pinned by name as well as by rule.

    The rule above is what stops instance five; this is what records that instance four was closed,
    so a reader of this file can tell the general guard from the specific repair.
    """
    forwarded = _forwarded_keys(REPORT_MODULE)
    assert "gas_shape_provider_by_customer" in forwarded
    assert "gas_shape_refusals" in forwarded
