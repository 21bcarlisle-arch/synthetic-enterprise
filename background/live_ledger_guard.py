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

TWO SUBJECTS, ONE DOCTRINE. `guard_live_ledger_write` refuses at the WRITE, which
is possible because every ledger writer takes a `path`. `guard_site_publish_pipeline`
(below) refuses at the ENTRY POINT, because the site publish pipeline has no such
seam -- 92 modules resolve their own output root at import and no argument can
redirect them. Same `in_test_process()`, same no-escape-hatch argument, different
place to stand. Read the second one's docstring for why the seam decides the shape.
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


# The published feed directories. Everything the public site reads at runtime is under
# one of these, so the containment IS the definition -- a feed added tomorrow is covered
# on the day it is created.
PUBLISHED_FEED_DIRS = (
    PROJECT_DIR / "site" / "data",
    PROJECT_DIR / "site" / "state",
    PROJECT_DIR / "docs" / "state",
)


class SitePublishUnderTest(RuntimeError):
    """A test process tried to run the live site publish pipeline."""


def guard_site_publish_pipeline(*, entry_point: str) -> None:
    """Refuse a test process's invocation of the site publish pipeline.

    WHY THE ENTRY POINT AND NOT THE WRITE (2026-09-09, LATENT finding `SEAT_FINDING_A_TEST_
    REWROTE_TWENTY_SIX_LIVE_FEEDS_INTO_A_DEGRADED_PUBLISH_STATE_AND_THE_ONLY_THING_THAT_
    NOTICED_BLAMED_THE_WRITER`).

    `guard_live_ledger_write` above guards at the WRITE because every ledger writer takes
    a `path` it can be handed a `tmp_path` for. **The site pipeline has no such seam.**
    `process_run_complete.generate_dashboard_json`, its only caller, runs ~40 generators; 92 modules under
    `tools/` and `background/` reference `site/data`, and each resolves its own root as
    `Path(__file__).resolve().parents[1]` at IMPORT time. There is nothing a caller can
    pass to redirect them, so the only place the refusal can be both real and honest is
    before the pipeline starts.

    WHAT WAS MEASURED. One test -- `test_website_integrity_fix.py::test_generate_dashboard_
    json_returns_gate_status` -- called this pipeline for real. It left 27 paths dirty (26
    tracked feeds plus one NEW untracked feed) and rewrote `site/data/publish_steps.json`
    from (degraded false, run_stamp `c440337ad`, 0 failing) to (**degraded true, run_stamp
    `"unknown"`, 6 failing**), every failure naming a pytest tmpdir. The test passed; the
    site suite passed afterwards; `degraded: true` is a state the ledger is designed to
    hold. The only thing that noticed was `promote_worktree_landing`, and it told the
    writer they had left work uncommitted -- sending them to add `site/data/` to a pathspec
    and publish a unit test's exhaust as a run.

    WHY THERE IS NO `dest_root` PARAMETER, WHICH WAS THE OBVIOUS FIX. A parameter accepted
    and not honoured is worse than none: it reads as containment at every call site while
    92 import-time roots ignore it -- a fake more permissive than its subject, which turns
    a fail-open into a green suite (R15). Threading a real destination root through those
    92 modules is the correct fix and is NOT done; it is recorded as a named gap, not
    filled with a placeholder that looks like an answer.

    WHY IT DOES NOT COST THE SUITE ANYTHING. Censused before landing: of the four tests
    that reach this entry point, **three already monkeypatch it away**, one saying why in
    its own comment -- *"generate_dashboard_json writes to the REAL site/data/dashboard.json
    (hardcoded path inside generate_dashboard_data.py) -- mock it to avoid corrupting the
    live dashboard"*. The class was known and solved three times as an instance (R10).

    IT LIVES HERE NOW, BESIDE ITS TWIN (2026-09-09, second pass). Same doctrine, same
    `in_test_process()` -- called directly rather than imported, because this is that
    module. It was written here, spent one commit exiled in `process_run_complete.py`
    because `test_live_ledger_guard.py::test_the_narrowing_to_measurement_ledgers_is_
    measured_not_assumed` was RED AT HEAD (86 unguarded observability writers against a
    bound of 74) and the commit gate selects any test that NAMES a staged path -- so
    editing this file would have refused that landing on two-week-old drift belonging to
    nobody. The bound was NOT raised to 86. The writers were guarded instead: 30 of them,
    across 17 modules, taking the census 86 -> 56, below the 74 it was frozen at on
    2026-08-26. The exile is the cost that drift charged a lane that had nothing to do
    with it, and it is recorded here because it is the only evidence of what a
    silently-breached ratchet actually costs.

    THOSE FIGURES ARE FROM A CLEAN HEAD EXTRACT AT 8c53c35e5 carrying this lane's hunks and
    nothing else. The same census run in the shared working tree reads 87 -> 57, because
    that tree holds four other lanes' uncommitted modules -- and a floor frozen against
    work no other lane can see is a floor no other lane can meet.

    NO ESCAPE HATCH: the process that must not have the override is exactly the one able to
    set it (`live_ledger_guard`'s own argument, and it applies unchanged here).
    """
    if not in_test_process():
        return
    raise SitePublishUnderTest(
        f"{entry_point} refused: this is a test process, and this pipeline publishes into "
        f"{', '.join(str(d) for d in PUBLISHED_FEED_DIRS)} through ~40 generators that "
        "resolve their own output root at import and cannot be redirected by any argument "
        "you can pass. On 2026-09-09 one test that called it rewrote 26 tracked feeds and "
        "flipped publish_steps.json to degraded with run_stamp 'unknown' and 6 pytest-tmpdir "
        "errors. Mock this entry point, as the three other tests that reach it already do. "
        "There is no env-var override by design."
    )
