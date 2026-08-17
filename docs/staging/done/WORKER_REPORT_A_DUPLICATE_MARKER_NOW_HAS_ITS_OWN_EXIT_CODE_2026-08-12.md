# [WORKER-REPORT] A duplicate marker now says so in its exit code, and the sweep stopped calling it progress (2026-08-12)

**Severity:** RECORDED · **Lane:** H_harness

**Drawn as:** rung-1c BLOCKING finding in `H_harness`, member of `CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`.
The instance: `WORKER_FINDING_A_DUPLICATE_MARKER_DISARMS_THE_WEDGE_ALARM_2026-08-10.md` (BLOCKING,
filed 2026-08-10, queued under SELF_INTERRUPT_DISCIPLINE with its atom and its R15 plan already
written — the diagnosis was paid for two days ago and this tick spent it).

## What the finding said, and what was still true this morning

`process_run_complete._process()` returned **0** when the marker it was handed had already been
archived by a concurrent publisher. Zero is the code that means "this process published". So a
duplicate — a marker this process never opened, for a run somebody else published — was
indistinguishable, to every caller, from a completed publish. It is the exact sibling of the
lock-skip fail-open closed on 2026-07-29, which was given its own exit code and left this
neighbouring door returning 0.

**Half of it had already been defended, and I checked before building** (`feedback_a_severity_
header_states_what_the_hour_found_not_what_it_left`). Since 2026-08-11 the outcome router refuses
to clear a wedge on rc=0 without a suite PASS recorded for the marker's own commit, and a
duplicate has no parseable commit, so it lands in "unproven" rather than clearing the alarm. That
guard is real. But it defends **by accident here** — it reads "unknown hash", not "nothing was
published" — and it was the only thing between a duplicate and `record_publish_gate_success()`.

**The half that was still live, and is what this repair actually fixes:** `background_worker`'s
sweep logged `Processed <marker>` for a duplicate and called `_record_marker_published()`, which
is PW4's **one evidenced close condition** for the zero-progress episode. So a marker that another
process archived milliseconds earlier silently closed the alarm whose whole job is to say the
backlog is not moving. `sim_runner`, meanwhile, logged the same duplicate as
`Auto-process failed (rc=76)`-shaped noise — a false red in the first log a reader opens when
diagnosing a wedge. 43 duplicate lines were logged on 2026-08-10 alone.

## What landed

- `background/process_run_complete.py` — `EXIT_NOTHING_PUBLISHED = 76` beside the lock-skip's 75,
  and `NO_PUBLISH_EXIT_CODES` as the register callers switch on. The already-archived path returns
  it. The shared outcome router records **neither** success nor failure for either code, because
  "I published nothing" is one fact, not two.
- `background/background_worker.py` — the mirror constant (pinned equal, same as the lock-skip's),
  a duplicate branch that logs the truth without claiming progress, and an entry in the
  oldest-outcome label table: without one, a duplicate fell to the default and was reported to the
  alarm as "publisher ran and FAILED", the opposite of what happened.
- `background/sim_runner.py` — the steady-state publisher's own log line for the same outcome.

## R10 — the class, not the instance

The finding asked for it and it is the second test: `_process()`'s zero-returning exits are
AST-enumerated and pinned against a declared register, keyed on each site's **guard condition**
rather than a line number so the pin survives ordinary edits and moves only when control flow
genuinely does. Two sites are declared, each with one line saying why it may claim a publish (the
change-detection gate retired the marker and refreshed liveness; the tail ran the publish path).
A new no-op `return 0` fails **by name**, printing the offending guard and the two choices.

## R15, both ways, three mutations run

| mutation | expected | observed |
|---|---|---|
| restore `return 0` on the already-archived path | red | **red** — 3 tests, including the end-to-end one, and the class test named the offending guard `archived is not None` exactly |
| make the sweep's duplicate branch claim a publish | red | **red** — 3 tests |
| delete the sweep's duplicate branch outright | red | **GREEN — the control was weaker than I claimed** |

**That third row is the finding inside this repair.** My first branch-contract test asserted the
sweep does not close the episode on a duplicate — and it passed with the branch deleted, because
rc=76 then falls through to the *failure* branch, which is wrong about the log but still does not
close the episode. Both sides of the seam were mocked, so each half could pass while the pair was
broken — which is precisely how the sibling lock-skip fix landed on one door and left this one
open. The repair for that is `test_the_publishers_verdict_reaches_the_sweep_end_to_end`: the
sweep's subprocess **really** calls `_process`, the race is reproduced as observed (present at
glob, archived before the open), and no return code is mocked. It reds under the publisher-side
mutation. The weaker test is kept, with its docstring now stating exactly which mutation it does
and does not catch.

## Evidence

- `tests/background/test_a_duplicate_marker_is_not_a_publish.py` — 12 tests, all passing; each
  docstring names the mutation that reds it.
- The four coupled suites together: **111 passed** (`test_a_duplicate_marker_is_not_a_publish`,
  `test_background_worker`, `test_sim_runner_publish_gate_outcome`, `test_process_run_complete`).
- Discharge recorded in the finding's own header and **checked** by `background/finding_severity.py`
  (`RELEASED`); `python3 -m background.finding_classes --render` re-derived the class document,
  which moved the instance BLOCKING → RECORDED and its lane's owed count **4 → 3**. `--check`
  PASS, 0 failures.

## What is NOT claimed

The router's "unproven" guard is untouched and still the thing that stops a duplicate clearing a
wedge; this repair makes that outcome *designed* rather than incidental. Three BLOCKING instances
remain owed in this class (`A_BRANCHS_GATE_AUDITED_THE_NEIGHBOURING_BRANCHS_PROMISE`,
`A_REPAIR_DOWNSTREAM_OF_ITS_OWN_GATE_CANNOT_LAND`, `THE_GATE_WAS_THE_BRANCHS_OWN_ADMISSION_TICKET`),
so the class document stays BLOCKING and the lane stays gated.
