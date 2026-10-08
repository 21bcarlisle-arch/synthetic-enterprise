"""Shared fixtures for the simulation suite.

`serves_industrial_accounts` exists because of the shape of one module-level line.
`simulation/run_phase2b.py` binds

    CUSTOMERS = live_population()

at IMPORT time, and `live_population()` applies the director's segment suspension
(`docs/design/curriculum/served_segments.json`). So the served book is frozen the first
time anything in a pytest session imports that module, and a test that sets
`SE_SERVED_SEGMENTS` in its own body sets it far too late to matter.

That matters for the I&C CAPABILITY tests -- the ones that run a whole sim and assert
C_IC1 or C_IC3g produced settlement records. The curriculum rules their case explicitly:
*"a supplier that has never onboarded an I&C customer still has to be able to"*, and it
names keeping these running as the difference between suspending a segment and deleting
one. With I&C suspended and no override they assert nothing, because the account they look
for is not in any run.
"""
from __future__ import annotations

import importlib
import os
import sys

import pytest


def reload_with_binders(module) -> list:
    """Reload `module`, then every loaded module still holding a container the reload replaced.

    `run_phase4c_on_phase2b` binds `CUSTOMERS = _PHASE2B_CUSTOMERS` at import, so reloading
    `run_phase2b` alone leaves it reading the old book while `run_phase2b` serves a new one. Every
    serial session that ran `test_phase24a_ic_customer.py` before
    `test_the_registry_eac_rewrite_reaches_the_dd_opening.py` therefore failed the latter on
    identity: it was the head-red census's longest-standing red (2026-10-02 to 2026-10-08), green
    in isolation. The scan asks identity, not names, so a new binder needs no entry here.

    Only containers the reload REPLACED count: an object `module` imported from elsewhere survives
    the reload, and every module that imports it too would otherwise be dragged in (dunders are
    skipped for the same reason: `__builtins__` is one dict shared by every module).
    """
    before = {k: v for k, v in vars(module).items()
              if not k.startswith("__") and isinstance(v, (list, dict, set))}
    importlib.reload(module)
    after = vars(module)
    replaced = [v for k, v in before.items() if after.get(k) is not v]
    replaced_ids = {id(v) for v in replaced}  # `replaced` stays alive, so no id is reused
    reloaded = []
    for name, other in list(sys.modules.items()):
        if other is None or other is module or name == __name__:
            continue
        try:
            values = [v for k, v in vars(other).items() if not k.startswith("__")]
        except TypeError:
            continue
        if any(id(v) in replaced_ids for v in values):
            importlib.reload(other)
            reloaded.append(name)
    return reloaded


@pytest.fixture(scope="module")
def serves_industrial_accounts():
    """Run the sim against a book that INCLUDES I&C, then put the module back.

    Sets the override and RELOADS `simulation.run_phase2b`, because the env var alone
    cannot move a module-level binding that has already run.

    MODULE-SCOPED, and that is a cost decision with a measured reason. Function scope
    reloads `run_phase2b` twice per test, and each reload re-resolves the book -- on files
    whose tests already run full decade simulations (7 of 28 completed in 32 minutes when
    this was function-scoped) that is pure added wall clock on the slowest suite in the
    repo, which is the same publish-cadence problem this seat is separately trying to
    shrink. Every test in these files wants the same book, so the module is the right unit.

    THE TEARDOWN RELOAD IS NOT TIDINESS. `sys.modules` is shared for the whole session, so
    leaving the reloaded module in place would hand every later test file a `CUSTOMERS`
    that still serves I&C -- this fixture would then be silently changing the book for
    tests that never asked for it, which is precisely the shared-state defect it exists to
    work around. Restoring the previous env value rather than deleting it is the same
    discipline one level down: `del` assumes the variable was unset on the way in.
    """
    prior = os.environ.get("SE_SERVED_SEGMENTS")
    os.environ["SE_SERVED_SEGMENTS"] = "resi,SME,I&C"
    module = importlib.import_module("simulation.run_phase2b")
    reload_with_binders(module)
    try:
        yield module
    finally:
        if prior is None:
            os.environ.pop("SE_SERVED_SEGMENTS", None)
        else:
            os.environ["SE_SERVED_SEGMENTS"] = prior
        reload_with_binders(module)
