"""THE DEFECT: `simulation/run_phase1b_weather_pull.py` was the design the director refused,
and it stayed executable and silent about it for six days across four staging notes
(2026-09-16, 2026-09-20, and twice on 2026-09-21), each declining to touch it. It looped the
LIVE supply book writing one CSV per customer, and on 2026-09-06 it wrote 125-byte header-only
CSVs over ten years of real archive and exited 0.

TWO LEGS, and the second is the load-bearing one.

1. `main()` refuses, with a reason a reader can act on and the successor named. A refusal that
   does not say why cannot be discovered to be wrong.
2. THE MODULE HOLDS NO ROUTE TO THE NETWORK OR TO THE SUPPLY BOOK AT ALL. Leg 1 alone is
   satisfied by a `main()` that raises while an inner function still pulls and truncates —
   which is most of the danger, because the 2026-09-06 incident was a loop over the live book,
   not a call to `main`. So this leg reads the module's own syntax tree and asserts the pull
   and book symbols are neither imported nor called anywhere in the file. Re-add the pull and
   this reds, wherever in the file it is added and whether or not `main` reaches it.

Both legs are asserted against the REAL module — nothing here stubs its own subject, because a
control that stubs `main` would prove the stub refuses.
"""

import ast
from pathlib import Path

import pytest

from simulation import run_phase1b_weather_pull as runner

MODULE_PATH = Path(runner.__file__)

# The symbols that ARE the hazard: the two that compose into data loss over a real archive,
# and the live roster that decides which archives get overwritten.
PULL_SYMBOLS = frozenset({
    "get_daily_weather",
    "write_weather_csv",
    "registered_supply_points",
})

# The modules those symbols live in. Named separately because an `import sim.weather_ingestor`
# followed by an attribute call is a route that a bare-name scan for PULL_SYMBOLS would miss.
PULL_MODULES = frozenset({
    "sim.weather_ingestor",
    "company.interfaces.supply_book",
})


def test_the_refused_pull_refuses_and_names_both_its_reason_and_its_successor():
    """Leg 1. The refusal fires from the real `main()`, and its message is actionable."""
    with pytest.raises(runner.RefusedDesign) as raised:
        runner.main()

    message = str(raised.value)

    # It says it was refused, and it says what to use instead. A refusal naming only the
    # successor reads as a deprecation; one naming only the refusal leaves the reader stuck.
    assert "REFUSED" in message, message
    assert "refused" in message.lower(), message
    assert "build_weather_world" in message, (
        "the refusal must name the successor that actually serves every premise, or the "
        f"reader has nowhere to go: {message}"
    )
    # The incident is what makes this a refusal rather than a comment, so it stays in the text.
    assert "2026-09-06" in message, message

    # A distinct type, so a control can tell this refusal from an unrelated breakage.
    assert isinstance(raised.value, RuntimeError)
    assert type(raised.value) is not RuntimeError


def test_the_refused_pull_holds_no_route_to_the_network_or_the_live_supply_book():
    """Leg 2. No import of, and no call to, the pull or the roster — anywhere in the file.

    This is the leg that survives someone keeping a working pull behind the refusing `main`.
    """
    tree = ast.parse(MODULE_PATH.read_text())

    imported_modules = set()
    imported_names = set()
    called_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module)
            for alias in node.names:
                imported_names.add(alias.name)
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                called_names.add(func.id)
            elif isinstance(func, ast.Attribute):
                called_names.add(func.attr)

    assert not (imported_modules & PULL_MODULES), (
        "the refused runner imports a module that can reach the network or the live supply "
        f"book: {sorted(imported_modules & PULL_MODULES)}"
    )
    assert not (imported_names & PULL_SYMBOLS), (
        f"the refused runner imports a pull symbol: {sorted(imported_names & PULL_SYMBOLS)}"
    )
    assert not (called_names & PULL_SYMBOLS), (
        f"the refused runner still CALLS a pull symbol: {sorted(called_names & PULL_SYMBOLS)}"
    )


def test_the_scan_in_leg_2_can_actually_find_a_pull_route():
    """Leg 2 would pass over any file it cannot read. This proves the scan CAN fire.

    A structural absence check is the classic control that cannot fail: it passes on an empty
    parse, a renamed symbol set, or a walk that visits nothing. So run the identical scan over
    a file that DOES hold the route -- the module the hazard came from -- and require a hit.
    """
    ingestor = Path(runner.__file__).parent.parent / "sim" / "weather_ingestor.py"
    tree = ast.parse(ingestor.read_text())

    defined = {
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }

    assert defined & PULL_SYMBOLS, (
        "the scan found none of the pull symbols in the module that defines them, so its "
        "clean verdict on the refused runner means nothing"
    )
