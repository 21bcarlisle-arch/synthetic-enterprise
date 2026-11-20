**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Nothing on the live executor stops after three failed rounds at one item

This answers the "Also" items of the director's 20 Nov steer
(`docs/staging/advisor/done/DIRECTOR_STEER_GATES_JUDGE_FROM_THE_BASE_PROPERTY_TESTS_FOR_BILLING_AND_DIFF_TRIGGERED_CHECKS_2026-11-20.md`).
The source practice is: "a failing check after three rounds brings in a human". There are two
questions. Does the machine stop after three failed attempts and file it? Does anything retry a
check until it goes green? Both were measured on 2026-11-20 against the code at 9e7cf29d45 and the
live logs.

## 1. Three rounds, then stop: NOT so on the live path

Three stop mechanisms exist. None does what the steer describes where the work actually runs.

| Mechanism | Where | What it does | Live? |
|---|---|---|---|
| R3 two-strike halt | `background/executor_governor.py:55` (`MAX_CONSECUTIVE_FAILURES = 2`), `:523` | Stops the loop and alerts after two consecutive failed or error cycles | **No.** It runs inside `executor-daemon.service`, which is `inactive` (`systemctl --user is-active`, 20 Nov). |
| Pass ceiling | `tools/discovery_pass_ceiling.py:119,267` (5 harden, 10 build), applied in `background/supervisor.py:1393` | Drops a map atom from the core draw after N passes without a level move | Yes, for map atoms only. It counts *passes*, not failures, and files nothing. It **fails open**: when every candidate is over the ceiling, it keeps the full set (`supervisor.py:1464`). |
| Stale census attempts | `background/head_red_register.py:233-250` | Stops offering the red-HEAD register once the census has stopped observing | One source only. Added after that source was drawn about 300 times in twelve days. |

**The gap is the Lane-0 and continuation path, `background/seat_executor.py`.** After a turn,
`subject_moved` decides whether the bound paths moved (`:1131`). A turn that did not move them is
logged `LANDED NOTHING` and the item is **re-offered with no count** (`:1145-1156`). Nothing
records how many times in a row an id has come back empty, nothing stops it, and nothing files it.

**Measured on the live log** (`docs/observability/seat-executor-log.md`, 8,804 lines, 2 Sep to 20 Nov):

- 538 `LANDED NOTHING` lines across 324 ids.
- **34 ids had a run of 3 or more empty turns** with no `FINISHED` between them, and 21 had a run
  of 4 or more.
- Counting only each id's longest run, **89 turns came after a third empty turn.** That is a lower
  bound on what a three-round stop would have saved.
- The worst case: `the-provision-and-the-movers-final-bill-graded-on-one-run-at-head`, **43 empty
  turns** from 2026-10-11 18:15 to 2026-10-12 02:16 UTC (rc=1). Next come
  `skip1-is-graded-against-s12es-branches` with 14 (19 Nov) and
  `grade-level-dd-w1-w4-h1-h2-on-the-first-123df0734-book` with 11 (16-17 Nov).

**Not every empty turn is a failed fix.** Several of the worst runs are "grade X on the first book
after Y". Those are items drawn before their input existed: the `DO NOT DRAW BEFORE <path> EXISTS`
hold was missing or not honoured. Others are turns that landed but never bound the landing (the
log line names both causes and cannot tell them apart). **A three-round stop covers all of these
causes without needing to tell them apart,** and that is its virtue. The filed record should carry
the three `LANDED NOTHING` reasons, so the reader can tell which cause it was.

## 2. No retry-until-green: CONFIRMED

- No rerun plugin is installed: `pip list` shows no `pytest-rerunfailures`, `flaky`, `retry` or
  `hypothesis`. The tree has no `--reruns`, no `reruns_delay`, no `@pytest.mark.flaky` and no
  `addopts` that adds one. The only `mark.flaky` hits are prose in
  `docs/design/TEST_THROUGHPUT_MEASUREMENT_AND_PROPOSAL.md:266,456`, a quarantine proposal that
  was never built.
- **The only retry loop near a gate retries the race, not the verdict.** `tools/surgical_land.py:273`
  sets `DEFAULT_ATTEMPTS = 3`, and the loop at `:1555` re-runs only on `BaseMoved` (HEAD moved
  under the gate). Its docstring says a red gate is terminal: "retrying any of them is retrying
  until the world agrees with you." `PUBLISH_ADVANCE_ATTEMPTS = 3`
  (`background/process_run_complete.py:6575`) also retries a lost fast-forward race, not a check.
- No flaky test was found to root-cause or delete. The steer's rule is already held, by absence.

## Proposal (reversible harness work; built next, not waiting)

**Stop after three, then file.** In `seat_executor.run_once`, after a `LANDED NOTHING` verdict,
count that id's consecutive empty turns from the log the executor already writes (`ids_run_since`
already parses it, so no new store is needed). On the third:

1. stop re-offering the id: drop the continuation, or hold it in the draw;
2. write one staging finding naming the id and its three `LANDED NOTHING` reasons; and
3. raise it in `for_the_director` only if the reasons are not an un-honoured `DO NOT DRAW BEFORE`
   (that cause is machine-fixable).

A landed turn resets the count. The control is a mutation-proven test over the whole partition: a
third empty turn stops the id, a second does not, and a landing in between resets the count.

A pre-registration is filed before the build reads its own effect. Over the logged history, this
rule would have suppressed at least 89 turns, and it would have refused no id that later landed
within its next three turns. That second half is the claim to check.

Handed on as `three-empty-turns-stop-the-id-and-file-it`.
