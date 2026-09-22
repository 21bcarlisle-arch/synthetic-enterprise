**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [LAUNCH FINISHED] 1 detached run(s) completed: onevar-width-4e7938f673. Now wrong: docs/staging/WORKER_RESULT_THE_ONE_VARIABLE_WIDTH_RUN_DIED_WITH_THE_TICK_THAT_LAUNCHED_IT_AND_ITS

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **2.7h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[LAUNCH FINISHED] 1 detached run(s) completed: onevar-width-4e7938f673. Now wrong: docs/staging/WORKER_RESULT_THE_ONE_VARIABLE_WIDTH_RUN_DIED_WITH_THE_TICK_THAT_LAUNCHED_IT_AND_ITS_RECORDED_COMMAND_CANNOT_PARSE_AT_THE_INSTRUMENT_IT_NAMES_2026-09-18.md
```

## What is known without diagnosing anything

- Signature: `deadman_launch_liveness_done` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-18T21:11:34+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

## Still live

## Instances seen
- `# detached run(s) completed: onevar-width-#. now wrong: docs/staging/worker_result_the_one_variable_width_run_died_with_` (first seen 2026-09-18)
