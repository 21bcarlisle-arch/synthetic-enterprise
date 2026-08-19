"""The door changed its signature; the caller did not. Can this control see that?

R15: a control that cannot fail is worse than none. Every test below except the first plants a
defect in a fixture tree and asserts `tools.seam_door_call_conformance` flags it -- and each
planted defect has a NULL CONTROL beside it (the same tree, repaired) asserting the checker goes
quiet again, so a checker that simply returned "stale" for everything would fail here too.

The first planted defect is the real one, verbatim: on 2026-08-19 the simulation runner failed
8 consecutive times over 0.7h with

    TypeError: replacement_cost_avoided_gbp() got an unexpected keyword argument 'counted_in_guard'

because KNIFE3 step 39 removed that keyword from `company/interfaces/growth_desk.py` and left
`simulation/run_phase2b.py` spelling it. Nothing in the tree could see it: the pre-commit gate
selects tests by filename stem, so the door's own seam test ran (and passed, having been updated
with it) while nothing under `simulation/` was selected at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.seam_door_call_conformance import ROOT, collect_doors, find_stale_calls

DOOR = '''
"""A fixture door."""


def replacement_cost_avoided_gbp(*, segment: str) -> float:
    return 150.0


def decide_acquisition(segment, commodity, *, term_start=None):
    return (segment, commodity, term_start)
'''


def _tree(tmp_path: Path, caller_source: str, door_source: str = DOOR) -> Path:
    """A minimal repo: one door module, one caller module."""
    doors = tmp_path / "company" / "interfaces"
    doors.mkdir(parents=True)
    (doors / "__init__.py").write_text("")
    (doors / "growth_desk.py").write_text(door_source)
    world = tmp_path / "simulation"
    world.mkdir()
    (world / "run_phase2b.py").write_text(caller_source)
    return tmp_path


def _findings(tmp_path: Path, caller_source: str, door_source: str = DOOR):
    return find_stale_calls(_tree(tmp_path, caller_source, door_source))


# ---------------------------------------------------------------------------
# THE LIVE TREE
# ---------------------------------------------------------------------------


def test_the_real_tree_has_no_stale_seam_call():
    """Every call to a `company/interfaces` door in this repo binds to it TODAY.

    Repo-wide on purpose: the file that breaks is never the file that was edited, so a scan
    scoped to the changed file is the one scan that cannot catch this class.
    """
    stale = find_stale_calls(ROOT)
    assert stale == [], "\n".join(call.render() for call in stale)


def test_the_real_tree_actually_has_doors_to_check():
    """A pass over zero doors is not a pass. Independence, stated as a number."""
    doors = collect_doors(ROOT)
    # 41 at the commit that introduced this file. The floor is set well below that so ordinary
    # seam work does not red it, and well above zero so a walk that stops finding the tree does.
    assert len(doors) > 30, f"only {len(doors)} doors found -- the scan is not reaching the seam"
    assert ("company.interfaces.growth_desk", "replacement_cost_avoided_gbp") in doors


# ---------------------------------------------------------------------------
# THE 2026-08-19 DEFECT, PLANTED
# ---------------------------------------------------------------------------

_REMOVED_KEYWORD = """
from company.interfaces.growth_desk import replacement_cost_avoided_gbp

def main(policy):
    return replacement_cost_avoided_gbp(
        segment="resi",
        counted_in_guard=policy.include_acq_cost_saved_in_guard,
    )
"""

_REPAIRED = """
from company.interfaces.growth_desk import replacement_cost_avoided_gbp

def main(policy):
    return replacement_cost_avoided_gbp(segment="resi")
"""


def test_a_caller_still_spelling_a_removed_keyword_is_flagged(tmp_path):
    stale = _findings(tmp_path, _REMOVED_KEYWORD)
    assert len(stale) == 1, [call.render() for call in stale]
    (call,) = stale
    assert call.path == "simulation/run_phase2b.py"
    assert call.door.name == "replacement_cost_avoided_gbp"
    assert "counted_in_guard" in call.reason
    # The finding points at BOTH ends of the disagreement, because a reader who only knows the
    # caller cannot tell a stale call from a door that should not have moved.
    assert call.door.path == "company/interfaces/growth_desk.py"


def test_the_repaired_caller_is_not_flagged(tmp_path):
    """NULL CONTROL for the test above: the door and the tree are identical, only the call moved."""
    assert _findings(tmp_path, _REPAIRED) == []


# ---------------------------------------------------------------------------
# THE OTHER SHAPES A CONTRACT CHANGE TAKES
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "call_source, expected_fragment",
    [
        # A parameter that became keyword-only, called positionally.
        ("replacement_cost_avoided_gbp('resi')", "positional"),
        # A required keyword the caller never learned about.
        ("replacement_cost_avoided_gbp()", "segment"),
        # A renamed parameter -- the caller spells the old name. `bind` reports the side it can
        # be certain of (the required name nothing supplied), which is enough to find the call.
        ("replacement_cost_avoided_gbp(sector='resi')", "segment"),
        # An extra positional after a parameter was deleted.
        ("decide_acquisition('resi', 'elec', 'extra')", "positional"),
    ],
)
def test_each_contract_change_shape_is_flagged(tmp_path, call_source, expected_fragment):
    source = (
        "from company.interfaces.growth_desk import "
        "decide_acquisition, replacement_cost_avoided_gbp\n"
        f"def main():\n    return {call_source}\n"
    )
    stale = _findings(tmp_path, source)
    assert len(stale) == 1, [call.render() for call in stale]
    assert expected_fragment in stale[0].reason


@pytest.mark.parametrize(
    "call_source",
    [
        "replacement_cost_avoided_gbp(segment='resi')",
        "decide_acquisition('resi', 'elec')",
        "decide_acquisition('resi', 'elec', term_start='2024-01-01')",
        "decide_acquisition(segment='resi', commodity='elec')",
        # A spread may supply the missing argument, so it is not decidable and not a finding.
        "decide_acquisition(*args)",
        "replacement_cost_avoided_gbp(**kwargs)",
    ],
)
def test_a_binding_call_is_never_flagged(tmp_path, call_source):
    """NULL CONTROL, widened: the checker must be quiet on every legal spelling."""
    source = (
        "from company.interfaces.growth_desk import "
        "decide_acquisition, replacement_cost_avoided_gbp\n"
        f"def main(args, kwargs):\n    return {call_source}\n"
    )
    assert _findings(tmp_path, source) == []


def test_a_spread_does_not_hide_an_unexpected_keyword_beside_it(tmp_path):
    """`*args` makes MISSING undecidable; it never makes OVER-supply undecidable."""
    source = (
        "from company.interfaces.growth_desk import decide_acquisition\n"
        "def main(args):\n    return decide_acquisition(*args, counted_in_guard=True)\n"
    )
    stale = _findings(tmp_path, source)
    assert len(stale) == 1
    assert "counted_in_guard" in stale[0].reason


# ---------------------------------------------------------------------------
# HOW THE CALL IS SPELLED
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "source",
    [
        # from company.interfaces.growth_desk import fn as alias
        "from company.interfaces.growth_desk import replacement_cost_avoided_gbp as rc\n"
        "def main():\n    return rc(segment='resi', counted_in_guard=True)\n",
        # from company.interfaces import growth_desk
        "from company.interfaces import growth_desk\n"
        "def main():\n"
        "    return growth_desk.replacement_cost_avoided_gbp(segment='r', counted_in_guard=1)\n",
        # from company.interfaces import growth_desk as gd
        "from company.interfaces import growth_desk as gd\n"
        "def main():\n"
        "    return gd.replacement_cost_avoided_gbp(segment='r', counted_in_guard=1)\n",
        # import company.interfaces.growth_desk
        "import company.interfaces.growth_desk\n"
        "def main():\n"
        "    return company.interfaces.growth_desk.replacement_cost_avoided_gbp(\n"
        "        segment='r', counted_in_guard=1)\n",
        # The import deferred INSIDE the function, which is how most of this repo spells it.
        "def main():\n"
        "    from company.interfaces.growth_desk import replacement_cost_avoided_gbp\n"
        "    return replacement_cost_avoided_gbp(segment='r', counted_in_guard=1)\n",
    ],
)
def test_every_import_spelling_resolves_to_the_same_door(tmp_path, source):
    stale = _findings(tmp_path, source)
    assert len(stale) == 1, [call.render() for call in stale]
    assert stale[0].door.name == "replacement_cost_avoided_gbp"


def test_a_same_named_function_from_elsewhere_is_not_attributed_to_the_door(tmp_path):
    """The door is resolved through the IMPORT, never by matching the name.

    Name-matching would over-attribute -- a local helper that happens to share a door's name is
    not a wall crossing, and reporting it would make the finding list unreadable exactly when it
    matters.
    """
    source = (
        "from saas.growth_mandate import replacement_cost_avoided_gbp\n"
        "def main():\n    return replacement_cost_avoided_gbp(segment='r', counted_in_guard=1)\n"
    )
    assert _findings(tmp_path, source) == []


# ---------------------------------------------------------------------------
# THE ONE EXEMPTION, AND ITS LIMIT
# ---------------------------------------------------------------------------


def test_a_call_asserted_to_raise_typeerror_is_not_a_stale_caller(tmp_path):
    """`company/interfaces/wall_protocol.py::encode_request` has exactly this test, and calling
    it a stale caller reads the control backwards: the mis-binding IS the assertion."""
    source = (
        "import pytest\n"
        "from company.interfaces.growth_desk import replacement_cost_avoided_gbp\n"
        "def test_it():\n"
        "    with pytest.raises(TypeError):\n"
        "        replacement_cost_avoided_gbp()\n"
    )
    assert _findings(tmp_path, source) == []


def test_the_exemption_does_not_extend_to_other_exceptions(tmp_path):
    """A mis-bound call under `pytest.raises(ValueError)` is still a finding -- that test claims
    something the interpreter will never let it reach."""
    source = (
        "import pytest\n"
        "from company.interfaces.growth_desk import replacement_cost_avoided_gbp\n"
        "def test_it():\n"
        "    with pytest.raises(ValueError):\n"
        "        replacement_cost_avoided_gbp(counted_in_guard=True)\n"
    )
    assert len(_findings(tmp_path, source)) == 1


def test_the_exemption_does_not_leak_to_calls_outside_the_block(tmp_path):
    source = (
        "import pytest\n"
        "from company.interfaces.growth_desk import replacement_cost_avoided_gbp\n"
        "def test_it():\n"
        "    with pytest.raises(TypeError):\n"
        "        replacement_cost_avoided_gbp()\n"
        "    replacement_cost_avoided_gbp(segment='r', counted_in_guard=True)\n"
    )
    stale = _findings(tmp_path, source)
    assert len(stale) == 1
    assert "counted_in_guard" in stale[0].reason
    assert stale[0].lineno == 6


# ---------------------------------------------------------------------------
# FAIL-CLOSED
# ---------------------------------------------------------------------------


def test_a_tree_with_no_doors_raises_rather_than_passing(tmp_path):
    """R15 FAIL-OPEN: zero findings over zero doors is a broken scan, not a clean tree."""
    (tmp_path / "company" / "interfaces").mkdir(parents=True)
    with pytest.raises(RuntimeError, match="zero doors"):
        find_stale_calls(tmp_path)


def test_a_missing_seam_raises(tmp_path):
    with pytest.raises(RuntimeError, match="does not exist"):
        find_stale_calls(tmp_path)


def test_an_unparseable_file_raises_rather_than_being_skipped(tmp_path):
    """An unscannable file is an UNCHECKED file. Skipping it is how a scan reports a clean tree
    it never read."""
    root = _tree(tmp_path, _REPAIRED)
    (root / "simulation" / "broken.py").write_text("def main(:\n")
    with pytest.raises(RuntimeError, match="cannot be scanned"):
        find_stale_calls(root)
