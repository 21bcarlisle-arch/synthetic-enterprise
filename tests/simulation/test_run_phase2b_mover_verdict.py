"""The relocation block rebinds a mover's fabric verdict through the named rule, not inline.

The rule is held in `test_fabric_demand_path_mover_verdict.py`. This holds the one call site to it:
inline, the verdict was left behind once (e71d5c1db) and only a fresh-seed run noticed.
"""
from __future__ import annotations

import ast
from pathlib import Path

RUN_PHASE2B = Path(__file__).resolve().parents[2] / "simulation" / "run_phase2b.py"


def test_the_relocation_block_rebinds_the_verdict_through_the_rule():
    tree = ast.parse(RUN_PHASE2B.read_text())
    blocks = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
        and isinstance(node.test.ops[0], ast.In)
        and isinstance(node.test.comparators[0], ast.Name)
        and node.test.comparators[0].id == "_relocation_pending"
    ]
    assert blocks, "run_phase2b has no `if ... in _relocation_pending:` block left to hold"
    [block] = blocks  # more than one relocation block is a shape this control was not written for
    calls = [
        n for n in ast.walk(block)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        and n.func.id == "rebind_fabric_verdict_to_new_home"
    ]
    assert calls, ("the relocation block no longer rebinds the mover's fabric verdict: a leg "
                   "moving across the legacy/fabric line will settle under its old home's verdict")
    # ...and nothing else in the block writes the trace map behind the rule's back.
    stray = [
        n for n in ast.walk(block)
        if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Store)
        and isinstance(n.value, ast.Name) and n.value.id == "fabric_series_by_customer"
    ]
    assert not stray, "the relocation block assigns fabric_series_by_customer outside the rule"
