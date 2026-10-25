"""The forward knowledge plan lists only the priority atoms no page names, and ranks a measured
constant module ahead of an unmeasured one however many constants the unmeasured one holds.

Defects this names: a plan that lists every priority atom (so writing a page moves nothing), and a
plan that sorts constants by count (so the 60-constant module nobody screened outranks the one the
screen showed moving revenue). Mutation recorded: dropping `if a not in has_page` in
`priority_rows` reds the first test; sorting `constant_rows` on count alone reds the second.
"""
from pathlib import Path

from tools import knowledge_plan as kp


def _root(tmp_path: Path) -> Path:
    (tmp_path / "docs/direction").mkdir(parents=True)
    (tmp_path / "docs/design").mkdir(parents=True)
    (tmp_path / "docs/direction/priority_order.yaml").write_text(
        "steps:\n  1: {name: knowledge, atoms: []}\n"
        "  2: {name: billing, atoms: [A1_led, A2_unled]}\n")
    (tmp_path / "docs/design/world_constant_anchor_register.txt").write_text(
        "# header\n" + "".join(f"simulation/big.py::C{i}\n" for i in range(60))
        + "simulation/screened.py::K\n")
    (tmp_path / "docs/design/world_constant_impact_ranking.md").write_text(
        "## The production-run screen, settlement loop (measured)\n\n"
        "| module | consts | gross | kWh | largest |\n|---|---|---|---|---|\n"
        "| `simulation/screened.py` | 1 | 0.40% | 0 | |\n\n## Next\n")
    return tmp_path


def test_a_priority_atom_a_page_names_leaves_the_plan(tmp_path):
    root = _root(tmp_path)
    rows = kp.priority_rows(root, has_page={"A1_led"})
    assert [r["subject"] for r in rows] == ["A2_unled"]
    # the partition can be taken both ways: with no page, both atoms are owed knowledge
    assert len(kp.priority_rows(root, has_page=set())) == 2


def test_a_screened_module_outranks_a_larger_unmeasured_one(tmp_path):
    rows = kp.constant_rows(_root(tmp_path))
    assert [r["subject"] for r in rows] == ["simulation/screened.py", "simulation/big.py"]
    assert rows[1]["count"] == 60 and "unmeasured" in rows[1]["why"]
