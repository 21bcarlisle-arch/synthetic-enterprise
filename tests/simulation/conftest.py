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

import pytest


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
    importlib.reload(module)
    try:
        yield module
    finally:
        if prior is None:
            os.environ.pop("SE_SERVED_SEGMENTS", None)
        else:
            os.environ["SE_SERVED_SEGMENTS"] = prior
        importlib.reload(module)
