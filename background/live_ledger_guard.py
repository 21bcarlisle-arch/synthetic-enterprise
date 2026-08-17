"""A TEST PROCESS MAY NOT WRITE A LIVE OBSERVABILITY LEDGER.

WHY THIS EXISTS (H27 Expert Hour #33, 2026-08-17, BLOCKING finding
`WORKER_FINDING_THE_ONLY_DOOR_PAIR_A_TEST_RUN_CAN_REPUBLISH_IS_THE_ONE_NOTHING_COMPARED_TO_ITS_LEDGER`).

One of the fourteen pairs the public Proof door serves --
`W2_11_payment_behaviour_source` -- has its ledger entry written as a SIDE EFFECT
of running the simulation: `simulation/run_phase2b.py` calls
`LivePaymentTriad.measure_and_write(...)` with `ledger_path` defaulted, so the
write lands in the real `docs/observability/coupled_gap_ledger.json`. **67**
test modules import `run_phase2b` -- counted 2026-08-17, not estimated; the
finding itself said "ten-plus". Each one, on every run, overwrote the live
belief-vs-truth measurement with its own fixture book. Measured on 2026-08-17: a
276-invoice fixture book replaced the 1600-invoice population and the regenerated
door published `gap` 0.0834 -> 0.0311, a **2.68x understatement of the company's
own payment belief-vs-truth gap**. The deployed payload was one broad-pathspec
commit away from carrying it.

THE FIX IS AT THE CHOKE POINT, NOT THE INSTANCE (R10). The instance fix -- pass a
scratch `ledger_path` at `run_phase2b.py:2448` -- closes ONE caller of ONE writer
and leaves the class open: every `tools/couple_*.py --write-ledger` main, and
every ledger added tomorrow, is the same shape and only escapes today because no
test happens to invoke it. So the refusal lives HERE, at the write, and the
writers call it. The subject is DERIVED, never hand-listed:

    a live ledger == any path resolving inside <PROJECT_DIR>/docs/observability/

so a ledger nobody thought to enumerate is covered on the day it is created.

WHAT IT DOES. Under a test process, a write whose resolved destination is a live
observability path RAISES `LiveLedgerWriteUnderTest`. Outside a test process it
is a no-op -- the real daemons, the real simulation runs and the real
`--write-ledger` invocations are untouched, which is the whole point: the
measurement of record must come from a real run over the real population.

THERE IS DELIBERATELY NO ESCAPE HATCH. An env var that re-permits the write is a
FAIL-OPEN door (R15) and would be set by exactly the process that must not have
it. A test that genuinely needs to exercise a write path passes
`ledger_path=tmp_path / "ledger.json"`, which every existing test already does.

FAIL-CLOSED IN BOTH DIRECTIONS (R15):
  * ambiguity about whether this is a test process resolves to REFUSE -- a
    wrongly-refused write costs one loud error in a run that catches it; a
    wrongly-permitted one costs a published figure.
  * the writers import this module at TOP LEVEL with no `try`. If the guard
    cannot be imported, the writer does not import either -- an unavailable
    check is a FAILED check, never a silently skipped one.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

# The published-record directory. Every ledger a public door, digest or gate
# derives from lives under here; that containment IS the definition, so this
# constant is the only thing that ever needs to be right.
LIVE_RECORD_DIR = PROJECT_DIR / "docs" / "observability"


class LiveLedgerWriteUnderTest(RuntimeError):
    """A test process tried to write a live observability ledger.

    Distinct from `ValueError`/`OSError` so a caller that wraps its measurement
    fail-safe (run_phase2b does) can still tell "the harness stopped me
    poisoning the record" apart from "the measurement itself broke"."""


def in_test_process() -> bool:
    """True when this interpreter is running a test.

    TWO independent signals, OR'd, because each alone has a hole:
      * `PYTEST_CURRENT_TEST` is set by pytest around setup/call/teardown, but
        NOT during collection or at module import -- a write at import time
        would slip past it.
      * `"pytest" in sys.modules` covers import and collection time, but would
        also be true inside a process that merely imported pytest for another
        reason.
    Fail-closed: EITHER is enough to refuse. The cost of a false positive is a
    refused write; the cost of a false negative is a published figure measured
    on a fixture."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return True
    return "pytest" in sys.modules


def is_live_record_path(path) -> bool:
    """True if `path` resolves INSIDE the published-record directory.

    Resolved on both sides before comparing, so a relative spelling, a `..`
    traversal or a symlink into the directory is the same subject as the
    absolute one -- the FAIL-OPEN hole a string prefix test would leave."""
    try:
        resolved = Path(path).resolve()
    except (OSError, RuntimeError, ValueError):
        # Unresolvable is not "outside". Fail closed.
        return True
    try:
        resolved.relative_to(LIVE_RECORD_DIR.resolve())
    except ValueError:
        return False
    return True


def guard_live_ledger_write(path, *, writer: str):
    """Refuse a test process's write to a live ledger. Returns `path` unchanged
    when the write is legitimate, so a caller can write
    `path = guard_live_ledger_write(path, writer=...)` inline and have the
    refusal be structurally impossible to forget.

    `writer` names the function being stopped -- the error has to say what to
    change, because whoever hits it is reading a traceback from a test they did
    not write."""
    if not in_test_process():
        return path
    if not is_live_record_path(path):
        return path
    raise LiveLedgerWriteUnderTest(
        f"{writer} refused: this is a test process and {path} is a LIVE "
        f"observability record under {LIVE_RECORD_DIR}. A test's fixture "
        "population must never become the measurement of record -- on "
        "2026-08-17 exactly this overwrote the coupled gap ledger with a "
        "276-invoice book and republished the public Proof door's payment "
        "belief-vs-truth gap 2.68x too low. Pass an explicit "
        "`ledger_path=tmp_path / \"ledger.json\"` instead. There is no env-var "
        "override by design."
    )
