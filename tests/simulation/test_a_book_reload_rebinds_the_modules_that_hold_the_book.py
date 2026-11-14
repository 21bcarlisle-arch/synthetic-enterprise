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


def test_a_kept_book_holds_the_reloaded_records_after_the_reload():
    """The supply book is KEPT across the reload, so only its elements can go stale.

    Defect this catches (2026-11-14, H40 L2): `register_drawn_points` is idempotent by
    `customer_id`, so the re-import left `supply_book.DRAWN_CUSTOMERS` on the old dicts and 9 of
    576 electricity legs answered `get_customer` with their roster dict. The split book hid one
    stray journey of a real red. Drop `_swap_old_records_in_kept_books` from `reload_with_binders`
    and this reds.
    """
    p2b = importlib.import_module("simulation.run_phase2b")
    old = list(p2b.ELEC_CUSTOMERS)
    reload_with_binders(p2b)
    # Records must have been replaced, or identity below holds without any swap. (Some legs come
    # from the static roster and survive the reload as the same object, so not all of them.)
    assert any(a is not b for a, b in zip(old, p2b.ELEC_CUSTOMERS))
    split = [c["customer_id"] for c in p2b.ELEC_CUSTOMERS if p2b.get_customer(c["customer_id"]) is not c]
    assert not split, f"{len(split)} of {len(p2b.ELEC_CUSTOMERS)} legs read an old record: {split[:5]}"
