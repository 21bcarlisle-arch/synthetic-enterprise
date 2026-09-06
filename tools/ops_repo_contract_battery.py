#!/usr/bin/env python3
"""R15 mutation battery for `background/ops_repo.py`, scored PER CALLER SUITE.

The fourth subject of the convergence-evidence sweep. This file is the SPEC --
the suites, the eight contracts, the reachability anchor and the null round. The
procedure lives in `tools/contract_battery.py`; what it guarantees and why is
documented there and deliberately not restated here.

PARAMETERISE OR COPY: ALREADY ANSWERED, BY THE TREE. The drawn direction asked
this turn to decide. `e383c6328` decided it one subject earlier and extracted
the engine, on the reasoning that a battery copied per subject would be the very
defect this sweep exists to find, committed by the instrument that finds it. So
there is nothing to re-decide: a fourth subject is a fourth `BatterySpec`, and
the fact that this file is 90 lines of data with no procedure in it is the
evidence the extraction was the right call.

WHY THIS SUBJECT IS THE ONE THAT SEPARATES THE TWO READINGS OF "SURVIVED".
`direction.py`'s fourth column was eight survivals in a suite that never reached
the module -- UNREACHABLE, not UNPROVED, and four turns of the column could not
tell. Here the opposite is established BEFORE the mutations run: all three
caller suites import their caller at module level and each caller imports this
module at module level, so the poison round should redden all three. A caller
column that survives entire is then reachable-and-unproved, which is a result
the sweep has not yet produced.

The reason it should survive: every caller suite patches `commit_and_push` BY
NAME in the caller's namespace, so the module object is real, the import is
real, and the function body is never entered.

Pre-registration, written and landed BEFORE this ran:
`docs/staging/SEAT_PREREG_DOES_A_CALLER_SUITE_THAT_REACHES_OPS_REPO_PROVE_ANYTHING_ABOUT_IT_2026-09-06.md`
The repair that gave this module its first suite at all:
`docs/staging/SEAT_FINDING_A_CONVERGED_HELPER_HAD_THREE_CALLERS_ZERO_TEST_IMPORTERS_AND_THE_REFUSAL_LEFT_BEHIND_AT_TWO_OF_THEM_2026-09-05.md`

Usage:
    python3 -m tools.ops_repo_contract_battery
    python3 -m tools.ops_repo_contract_battery --only M7 M8 --suites choke_point
"""
from __future__ import annotations

from tools.contract_battery import BatterySpec, run

#: The WHOLE caller population -- three, and there is no fourth. Unlike
#: `segment_vocabulary`, where ten of 265 reaching suites were graded and the
#: bound had to be declared, `survived_all` here is a statement about every
#: first-party caller this module has.
SUITES = (
    "tests/background/test_ntfy_mirror.py",
    "tests/background/test_director_input_log.py",
    "tests/background/test_backup_company_data.py",
)

#: Written 2026-09-05 AS THE REPAIR, and this module's first test of any kind.
#: Scored as its own column and never folded into `survived_all`: the
#: pre-registered question is what the CALLERS prove, and folding the repair in
#: would make that question unanswerable the moment the repair landed.
REPAIR_SUITE = "tests/background/test_the_ops_repo_push_had_no_refusal_at_the_choke_point.py"

#: No import path to the subject -- verified by importing each and checking
#: `background.ops_repo` is absent from `sys.modules`, the same check that
#: confirmed all three caller suites DO reach it. The poison round must leave
#: these green: a floor that reddens everything for a reason unrelated to the
#: subject reads exactly like total reachability, and would be most convincing
#: precisely when it was broken.
CONTROL_SUITES = (
    "tests/design/test_atom_notes_store.py",
    "tests/background/test_delivery_lane.py",
)

#: (id, the contract as the module states it, old, new). Each `old` appears
#: exactly once in the subject and the engine refuses the row if it does not.
MUTATIONS = (
    (
        "M1",
        "the write REFUSES under a test process at all -- before 2026-09-05 this call pushed",
        "    if in_test_process():",
        "    if False:",
    ),
    (
        "M2",
        "the refusal is the FIRST statement -- placed after the `git add` it has already staged "
        "a test's bytes in the real private repo",
        "    if in_test_process():\n        raise OpsRepoWriteUnderTest(",
        '    subprocess.run(["git", "-C", str(OPS_REPO_DIR), "add", *relpaths], check=True)\n'
        "    if in_test_process():\n        raise OpsRepoWriteUnderTest(",
    ),
    (
        "M3",
        "the refusal carries its OWN TYPE -- a caller must be able to tell 'the harness stopped "
        "me publishing' from 'the write itself broke'",
        "        raise OpsRepoWriteUnderTest(\n",
        "        raise RuntimeError(\n",
    ),
    (
        "M4",
        "ONLY a nothing-to-commit failure is swallowed -- every other commit failure raises",
        '        if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:',
        "        if True:",
    ),
    (
        "M5",
        "a nonzero commit return code is inspected at all",
        "    if result.returncode != 0:",
        "    if False:",
    ),
    (
        "M6",
        "the push actually happens -- a commit that never leaves the checkout is not a mirror",
        '        ["git", "-C", str(OPS_REPO_DIR), "push", "origin", "main"], check=True,',
        '        ["git", "-C", str(OPS_REPO_DIR), "status"], check=True,',
    ),
    (
        "M7",
        "the lock is EXCLUSIVE -- a shared lock admits every holder and excludes nobody",
        "                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)",
        "                fcntl.flock(fh, fcntl.LOCK_SH | fcntl.LOCK_NB)",
    ),
    (
        "M8",
        "the lock deadline is REACHABLE -- an unbounded wait is not a timeout. THIS IS THE "
        "MUTATION THAT HUNG on 2026-09-05 and took the restore step with it; the repair suite's "
        "lock leg now bounds the second acquirer with a thread join",
        "                if time.monotonic() >= deadline:",
        "                if False:",
    ),
)

#: THE REACHABILITY FLOOR. An import-time raise in front of the converged
#: function itself. Every caller imports this module at module level, so all
#: three caller suites should fail at COLLECTION -- and that is the point: it
#: proves the green cells above them were at risk, which is the one thing the
#: `direction.py` column could not say about its own.
POISON_OLD = "\ndef commit_and_push("
POISON_NEW = ('\nraise RuntimeError("POISON: ops_repo.py reachability floor")'
              "\n\n\ndef commit_and_push(")

#: THE NULL ROUND: a module-level no-op assignment. It changes the bytes and
#: adds an AST node and cannot change what any function does. A suite that
#: reddens under it is grading this file's TEXT rather than running it, and its
#: kills are not execution evidence. `tools/converged_contract_screen.py` reads
#: source files to build the very screen that selected this subject, so a
#: text-grading reader of `background/` is not hypothetical here -- it is the
#: tool that chose the subject. It is not in the suite list, but measuring that
#: none of these five behaves that way beats assuming it.
NULL_OLD = "class OpsLockTimeout(Exception):"
NULL_NEW = ("_NULL_ROUND_MARKER = None  # behaviour-preserving; tools/contract_battery.py\n"
            "\n\nclass OpsLockTimeout(Exception):")

SPEC = BatterySpec(
    name="ops_repo",
    subject="background/ops_repo.py",
    suites=SUITES,
    repair_suite=REPAIR_SUITE,
    mutations=MUTATIONS,
    poison_old=POISON_OLD,
    poison_new=POISON_NEW,
    control_suites=CONTROL_SUITES,
    null_old=NULL_OLD,
    null_new=NULL_NEW,
)


def main(argv: list[str] | None = None) -> int:
    return run(SPEC, argv)


if __name__ == "__main__":
    raise SystemExit(main())
