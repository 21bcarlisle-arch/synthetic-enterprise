"""The reach instrument finds a world constant's readers through the bindings a run really uses.

Each test names the defect it catches. The instrument's errors are meant to run one way only --
a reached constant read as unreached -- so the controls below pin the routes that would otherwise
make a READ constant look dead: a `from` import under an alias, a derived module table, a default
argument.
"""
from __future__ import annotations

import ast
from pathlib import Path

from tools.world_constant_reach import _scaled_source, sites


def _tree(tmp_path: Path) -> Path:
    (tmp_path / "simulation").mkdir()
    (tmp_path / "simulation" / "__init__.py").write_text("")
    (tmp_path / "simulation" / "a.py").write_text(
        "SHARE = 0.4\n"
        "OTHER = 0.7\n"
        "ONLY_AT_IMPORT = 0.2\n"
        "TABLE = {'x': SHARE, 'y': OTHER}\n"
        "_CHECK = ONLY_AT_IMPORT * 2\n"
        "def f(p=OTHER):\n"
        "    return p\n"
    )
    (tmp_path / "simulation" / "b.py").write_text(
        "from simulation.a import TABLE as T\n"
        "def g():\n"
        "    return T['x']\n"
    )
    return tmp_path


def _function_sites(table, key):
    return [r for r in table[key] if r["kind"] in ("function", "default")]


def test_a_constant_read_only_through_a_derived_table_under_an_alias_is_followed_to_its_reader(tmp_path):
    """Defect: a derived table carrying only ITS FIRST source constant, or an aliased `from`
    import not followed, would put SHARE in the dead tier while `g()` reads it every call."""
    root = _tree(tmp_path)
    keys = {"simulation/a.py::SHARE", "simulation/a.py::OTHER", "simulation/a.py::ONLY_AT_IMPORT"}
    table = sites(root, keys)
    assert {"file": "simulation/b.py", "line": 3, "kind": "function"} in table["simulation/a.py::SHARE"]
    assert any(r["file"] == "simulation/b.py" for r in table["simulation/a.py::OTHER"])
    # the partition can be taken both ways: a constant read only at import has no function site
    assert not _function_sites(table, "simulation/a.py::ONLY_AT_IMPORT")
    assert _function_sites(table, "simulation/a.py::SHARE")


def test_a_default_argument_counts_at_the_functions_body(tmp_path):
    """Defect: a default is evaluated on the `def` line at import, so keying it there would
    count every default as reached the moment the module loads."""
    root = _tree(tmp_path)
    table = sites(root, {"simulation/a.py::OTHER"})
    assert {"file": "simulation/a.py", "line": 7, "kind": "default"} in table["simulation/a.py::OTHER"]


def _value(source: str, name: str):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and node.targets[0].id == name:
            return ast.literal_eval(node.value)
    raise KeyError(name)


def test_scaling_a_distribution_moves_mass_and_a_share_never_passes_one(tmp_path):
    """Defect: scaling every weight of a normalised distribution is a no-op arm that reads as
    'no impact'; scaling a 0.95 share by 1.1 is a refusal, not a sensitivity."""
    p = tmp_path / "m.py"
    p.write_text("W = {'a': 0.3, 'b': 0.45, 'c': 0.25}\nS = 0.95\nK = 2.5\n")
    out = _scaled_source(p, {"W", "S", "K"}, 1.1)
    w = _value(out, "W")
    assert abs(sum(w.values()) - 1.0) < 1e-9
    assert w["a"] > 0.3 and w["b"] < 0.45
    assert _value(out, "S") == 1.0
    assert abs(_value(out, "K") - 2.75) < 1e-9
    assert _value(_scaled_source(p, set(), 1.1), "W") == {"a": 0.3, "b": 0.45, "c": 0.25}
