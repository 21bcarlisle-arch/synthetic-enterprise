"""The publisher's declared budget, read FRESH FROM DISK on every call.

WHY THIS IS NOT AN IMPORT (2026-08-22, observed — the wedge that ran 00:55Z–02:38Z).

Both callers that spawn `process_run_complete.py` already derived their deadline from the
publisher's own declared budget rather than restating it, and
`test_publisher_deadline_exceeds_its_gate.py` pinned that derivation over the whole
population of callers. The derivation was correct. It was also, in a long-lived daemon,
FROZEN — and both helpers' docstrings asserted the opposite in as many words:

    Imported lazily and at CALL time (not bound at import) ... a constant snapshotted at
    import would go stale

A lazy import is still a ONE-TIME import. `from background import process_run_complete`
returns the object already in `sys.modules` after the first call, so the constant read off
it is the value that was on disk when THAT PROCESS first made the call — not the value on
disk now. "Call time" was true of the import statement and false of the number.

WHAT IT COST. `GATE_SUITE_TIMEOUT_SECONDS` was 300 for 78 minutes on 2026-08-21 (16:10–17:28,
commit 8d6f4a2b4, while the gate was being narrowed in scope). `sim_runner` started at
16:45:22, inside that window, and cached `PUBLISH_PATH_TIMEOUT_SECONDS = 300 + 900 = 1200`.
The constant was corrected to 3400 at 17:28 and 3800 at 18:32; the running daemon went on
killing every publish at 1200s for the next ten hours. Four consecutive cycles died that way
(docs/observability/sim-runner-log.md, "Auto-process timed out after 1200s"), all four
recorded as `deadline_kill` against a gate that was never allowed to answer — `total_red: 0`,
`blocking_tests: []`. `background_worker`, started at 17:28:59, froze 4300 in the same way
and its own log says 4300 in the same words. Two daemons, two different frozen values, one
mechanism — which is what makes it a class rather than a bug.

WHY AST AND NOT A SUBPROCESS. The first version of this module shelled out to a fresh
interpreter (`python3 -c "import ...; print(...)"`), which is the obvious way to get an
uncached read. It cost 45ms and broke ten sibling tests instantly: every test that stubs
`subprocess.run` to fake a publisher spawn also intercepted the probe, because the probe had
put itself on the same seam the publisher spawn uses. Reading the source with `ast` needs no
seam at all, has no import side effects, cannot execute publisher code, and costs ~2ms. The
tests that broke were the signal — a probe should not be reachable through the machinery it
exists to measure.

FAIL-LONG, NEVER FAIL-SHORT. Every failure mode here resolves upward: this module RAISES and
the caller applies `FALLBACK_SECONDS`. A deadline that is too long delays one cycle's
diagnosis; a deadline that is too short decides the inner gate's verdict by stopwatch, which
is the entire defect this module exists to end.
"""
from __future__ import annotations

import ast
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

PUBLISHER_SOURCE = PROJECT_DIR / "background" / "process_run_complete.py"

# The name the publisher declares its total publish-path budget under.
BUDGET_CONSTANT = "PUBLISH_PATH_TIMEOUT_SECONDS"

# The answer when the publisher will not declare its budget at all. It must exceed the
# LARGEST budget the publisher can currently declare, or the fallback re-creates the bug it
# exists to avoid. That maximum is bounded by the ratchet
# (`PUBLISH_GATE_CEILING_RATCHET_SECONDS + PUBLISH_PATH_ALLOWANCE_SECONDS` = 4700s today, and
# the ratchet may only FALL), so this is checked against the ratchet and not against today's
# value. The 3600 that stood in both callers until 2026-08-22 was BELOW the 4700 the publisher
# declares — the same constant-frozen-while-its-subject-grew shape, one layer down, in the
# very fallback whose comment claimed it was "deliberately larger than any bound the publisher
# currently declares".
FALLBACK_SECONDS = 2 * 60 * 60


class BudgetUnreadable(RuntimeError):
    """The publisher did not state a budget this module could read. Never a value."""


def _evaluate_int(node, known):
    """Integer arithmetic over already-known module constants, and nothing else.

    Deliberately not `eval`: this module reads a file that the publish path executes, so it
    must not be able to run anything it reads. Anything outside int literals, names already
    resolved above it, and + - * // is refused rather than guessed at."""
    if isinstance(node, ast.Constant) and isinstance(node.value, int) \
            and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.Name) and node.id in known:
        return known[node.id]
    if isinstance(node, ast.BinOp):
        left = _evaluate_int(node.left, known)
        right = _evaluate_int(node.right, known)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.FloorDiv):
            return left // right
    raise BudgetUnreadable(
        "not integer arithmetic over module constants: {}".format(ast.dump(node)[:200])
    )


def _module_int_constants(source):
    """Every module-level name bound to an integer expression, in declaration order.

    Order matters: `PUBLISH_PATH_TIMEOUT_SECONDS` is a sum of two constants declared above
    it, so names resolve against what has already been seen — the same order Python itself
    would bind them in."""
    known = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target.id] if node.value is not None else []
        else:
            continue
        if not targets:
            continue
        try:
            value = _evaluate_int(node.value, known)
        except BudgetUnreadable:
            continue
        for name in targets:
            known[name] = value
    return known


def declared_publisher_budget_seconds():
    """The publisher's declared total publish-path budget, as it is on disk RIGHT NOW.

    Raises `BudgetUnreadable` on any failure — callers own the fail-long fallback, because
    only they can log it against the run it affects. This function never returns a value it
    did not read out of the publisher's source.
    """
    source = PUBLISHER_SOURCE.read_text(encoding="utf-8")
    constants = _module_int_constants(source)
    if BUDGET_CONSTANT not in constants:
        raise BudgetUnreadable(
            "{} declares no readable {} — the publish path's budget is not a module-level "
            "integer any more, and a caller must fall back long rather than guess".format(
                PUBLISHER_SOURCE, BUDGET_CONSTANT
            )
        )
    return constants[BUDGET_CONSTANT]
