"""The desk-belief log is an instrument: the run writes it and never reads it.

Value test s.9 (candidate A) grades the desk's churn belief per renewal against who left. The
pre-registration says adding the log leaves every other output of a run byte-identical. That holds
only while nothing in the run loop reads the log back, so this test reads the loop's source: the
name may appear at its definition, its one append and the results dict, and nowhere else. The
defect it names: a later edit that branches on, counts or mutates the log, turning an instrument
into an input.
"""
import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "simulation" / "run_phase2b.py"


def _uses(tree=None):
    tree = tree or ast.parse(SRC.read_text(encoding="utf-8"))
    return [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == "desk_belief_log"]


def test_the_log_exists_so_the_control_can_fail():
    assert _uses(), "desk_belief_log is gone from run_phase2b; the s.9 sidecar has no source"


def test_the_log_is_written_once_and_returned_and_read_nowhere_else():
    tree = ast.parse(SRC.read_text(encoding="utf-8"))
    parents = {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}
    kinds = []
    for n in _uses(tree):
        p = parents[n]
        if isinstance(n.ctx, ast.Store):
            kinds.append("define")
        elif isinstance(p, ast.Attribute) and p.attr == "append":
            kinds.append("append")
        elif isinstance(p, ast.Dict):
            kinds.append("return")
        else:
            kinds.append(f"read@{n.lineno}")
    assert sorted(kinds) == ["append", "define", "return"], kinds
