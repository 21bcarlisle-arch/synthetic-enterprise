"""The basics' gate opens only when every gate atom is at target, and a line's state is read from
the tree and the map, not typed. Defect named: a check that says "not yet" for ever (or "done" for
ever) passes every test of one verdict, so the partition is asserted reachable first."""

from __future__ import annotations

from tools import the_basics

DEF = {"gate": ["A", "B"],
       "lines": [{"basic": "x", "line": "has a test", "tests": ["real.py"]},
                 {"basic": "x", "line": "missing test", "tests": ["gone.py"]},
                 {"basic": "x", "line": "no test", "tests": []},
                 {"basic": "x", "line": "atom short", "atom": "B", "tests": ["real.py"]},
                 {"basic": "x", "line": "atom unmapped", "atom": "Z", "tests": ["real.py"]}]}


def _atoms(a: int, b: int) -> list[dict]:
    return [{"id": "A", "level_current": a, "level_target": 2},
            {"id": "B", "level_current": b, "level_target": 3}]


def test_both_verdicts_and_every_line_state_are_reachable(tmp_path):
    (tmp_path / "real.py").write_text("")
    shut = the_basics.grade(DEF, _atoms(2, 2), tmp_path)
    open_ = the_basics.grade(DEF, _atoms(2, 3), tmp_path)
    assert not shut["ready"] and open_["ready"]
    states = {x["line"]: x["state"] for x in shut["lines"]}
    assert states == {"has a test": "done", "missing test": "absent", "no test": "absent",
                      "atom short": "partial", "atom unmapped": "partial"}
    assert {x["line"]: x["state"] for x in open_["lines"]}["atom short"] == "done"


def test_an_atom_missing_from_the_map_holds_the_gate_shut(tmp_path):
    result = the_basics.grade({"gate": ["A", "GONE"]}, _atoms(2, 3), tmp_path)
    assert not result["ready"]
    assert [g["met"] for g in result["gate"]] == [True, False]
    assert "not on the map" in the_basics.render(result)


def test_an_empty_gate_is_not_done(tmp_path):
    assert not the_basics.grade({"gate": [], "lines": []}, [], tmp_path)["ready"]


def test_the_real_definition_names_dual_fuel_and_every_gate_atom_is_on_the_map():
    from tools.maturity_map_store import load_atoms
    definition = the_basics.load_definition()
    ids = {a["id"] for a in load_atoms()}
    assert definition["gate"], "step 6 lost its starts_when"
    assert set(definition["gate"]) <= ids, set(definition["gate"]) - ids
    assert any(x["basic"] == "dual fuel" for x in definition["lines"])
