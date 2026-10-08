"""Reloading `run_phase2b` re-binds the modules that took its book at import.

Defect this catches (2026-10-08): `serves_industrial_accounts` reloaded `run_phase2b` and nothing
else, so `run_phase4c_on_phase2b._PHASE2B_CUSTOMERS` kept the old list. In a serial session every
later test that asks the two modules for the same record then failed, which is how
`test_the_registry_eac_rewrite_reaches_the_dd_opening.py` stood red in the head-red census for five
runs while passing alone. Make `reload_with_binders` reload only `module` and this reds.
"""
from __future__ import annotations

import importlib
import sys

from tests.simulation.conftest import reload_with_binders


def test_a_module_that_bound_the_book_reads_the_new_book_after_the_reload():
    p2b = importlib.import_module("simulation.run_phase2b")
    importlib.import_module("simulation.run_phase4c_on_phase2b")
    old = p2b.CUSTOMERS
    reloaded = reload_with_binders(p2b)
    # The reload must have replaced the book, or the identity below holds without any re-binding.
    assert p2b.CUSTOMERS is not old
    p4c = sys.modules["simulation.run_phase4c_on_phase2b"]
    assert p4c._PHASE2B_CUSTOMERS is p2b.CUSTOMERS, reloaded
    # A scan keyed on something every module shares (`__builtins__`, an imported table) would
    # reload the whole session; the binders of a run's book are a handful.
    assert "simulation.run_phase4c_on_phase2b" in reloaded
    assert len(reloaded) < 20, reloaded
