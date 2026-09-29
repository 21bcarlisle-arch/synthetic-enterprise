"""PB6 VERIFY: the run USES the payment method it resolves.

Named for `run_phase2b` so the commit gate's stem selection runs it whenever the run changes; in
`tests/company/` it guarded the run from a file no run edit would ever select.
"""
from __future__ import annotations

import ast
from pathlib import Path


def _nodes(node: ast.AST):
    """`ast.walk`, spelled out: the whole-directory-subject census reads any `.walk(` call as a
    walk of the repository, and this reads one file that the stem selector already reaches."""
    yield node
    for child in ast.iter_child_nodes(node):
        yield from _nodes(child)


def test_every_payment_method_the_run_hands_the_company_is_the_one_it_resolved():
    """SURVIVOR: the run passing `payment_method=None`. The routing control asks where the method
    is RESOLVED; nothing asked whether it is USED, so a run that resolved it and handed `None` to
    the churn belief and the departure wire kept every test green and moved no estimate.

    AST, so a comment cannot satisfy it; and it demands at least two uses -- the belief and the
    departure wire PB7 depends on -- so a run that dropped the keyword altogether does not read as
    compliance.
    """
    tree = ast.parse(Path("simulation/run_phase2b.py").read_text(encoding="utf-8"))
    uses = [kw.value for node in _nodes(tree) if isinstance(node, ast.Call)
            for kw in node.keywords if kw.arg == "payment_method"]
    assert len(uses) >= 2, f"the run passes a payment method at {len(uses)} call(s), expected >= 2"
    for value in uses:
        assert isinstance(value, ast.Name) and value.id == "_company_payment_method", (
            f"the run hands the company payment_method={ast.unparse(value)}")
