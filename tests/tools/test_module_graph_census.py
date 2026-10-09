"""Controls for `tools/module_graph_census.py` -- the module-graph door's one census.

Each test names the defect it exists to catch.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tools import epistemic_wall as wall
from tools import module_graph_census as mg

REPO = Path(__file__).resolve().parents[2]


def _tree(tmp_path: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return tmp_path


# A tree in which every kind of edge, and both crossing directions, can be taken.
_BASE = {
    "company/__init__.py": "",
    "company/a.py": "from company import b\n",
    "company/b.py": "x = 1\n",
    "company/interfaces/__init__.py": "",
    "company/interfaces/seam.py": "from simulation import w\n",
    "simulation/__init__.py": "",
    "simulation/w.py": "y = 2\n",
    "simulation/reader.py": "from company.interfaces import seam\n",
    "tools/__init__.py": "",
    "tools/t.py": "import company.a\n",
}


def test_every_edge_kind_and_both_directions_can_be_taken(tmp_path):
    """Defect: a classifier that files every crossing as one kind passes every other test here.
    Over a tree built to contain each, every slot of the partition must be non-zero."""
    files = dict(_BASE, **{"simulation/legacy.py": "from company import b\n"})
    c = mg.census(_tree(tmp_path, files))
    kinds = {mg.EDGE_KINDS[k] for _s, _d, k in c["edge_list"]}
    assert kinds == set(mg.EDGE_KINDS), kinds
    x = c["crossings"]
    assert x["seam_company_reads_world"] and x["seam_world_reads_company"], x
    assert x["bypass_world_reads_company"] == 1, x
    assert x["seam"] + x["bypass"] == sum(1 for *_e, k in c["edge_list"] if k), x


def test_a_direct_company_to_simulation_import_reds_the_bypass_count(tmp_path):
    """Defect: the door shows zero bypasses because the census cannot see one. Add a direct
    company -> simulation import outside the seam and the forbidden-direction count must move."""
    clean = mg.census(_tree(tmp_path / "clean", _BASE))
    assert clean["crossings"]["bypass_company_reads_world"] == 0
    assert clean["crossings"]["bypass"] == 0

    dirty = dict(_BASE, **{"company/a.py": "from company import b\nfrom simulation import w\n"})
    c = mg.census(_tree(tmp_path / "dirty", dirty))
    assert c["crossings"]["bypass_company_reads_world"] == 1, c["crossings"]
    assert c["crossings"]["bypass"] == 1
    assert c["bypass_edges"] == [{"from": "company.a", "to": "simulation.w",
                                  "direction": "company_reads_world"}]


def test_a_test_module_is_not_a_node(tmp_path):
    """Defect: test files inflate the module count and their imports read as bypasses."""
    files = dict(_BASE, **{"company/test_probe.py": "from simulation import w\n",
                           "company/tests/probe.py": "from simulation import w\n"})
    c = mg.census(_tree(tmp_path, files))
    assert c["crossings"]["bypass"] == 0
    assert not any("probe" in n["module"] for n in c["nodes"])


def test_an_empty_tree_is_refused_not_reported_clean(tmp_path):
    """Defect: zero modules reads as zero bypasses -- a perfectly clean boundary for no code."""
    (tmp_path / "company").mkdir()
    with pytest.raises(RuntimeError):
        mg.census(tmp_path)


def test_the_census_and_the_wall_ratchet_name_the_same_bypassing_modules():
    """Defect: two instruments with two definitions of a crossing -- the door and the wall
    ratchet disagree about which modules go round the seam. Asked of HEAD by both."""
    mine = mg.census_at_head(REPO)
    by_wall = wall.crossings_at_head(wall.REPO_ROOT)
    assert {b["from"] for b in mine["bypass_edges"]} == {src for src, _dst in by_wall}
    assert mine["modules"] == len(mine["nodes"]) and mine["edges"] == len(mine["edge_list"])


def test_nothing_but_the_weekly_publish_reads_the_census():
    """Defect (R12): a diagnostic becomes a target the moment a gate, reward or draw reads it.
    The only production importer is the weekly publish step."""
    importers = set()
    for layer in mg.LAYERS:
        for path in (REPO / layer).rglob("*.py"):
            rel = path.relative_to(REPO).as_posix()
            if rel == "tools/module_graph_census.py" or mg._is_test(rel):
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module] + [f"{node.module}.{a.name}" for a in node.names]
                elif isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                if "tools.module_graph_census" in names:
                    importers.add(rel)
    assert importers == {"background/process_run_complete.py"}, importers
