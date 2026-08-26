**Severity:** LATENT · **Lane:** H_harness

# [BLOCKED] Dead-man's switch: 62 min since the last git COMMIT, and 115 unprocessed staging file(s) (CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md, CLASS_MEASUREMENTS_THAT_MIRROR_20

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **6.1h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[BLOCKED] Dead-man's switch: 62 min since the last git COMMIT, and 115 unprocessed staging file(s) (CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md, CLASS_MEASUREMENTS_THAT_MIRROR_2026-08-12.md, CLASS_NO_CALLER_AND_NEVER_RUNS_2026-08-12.md...). The supervisor/tmux stack or the main session may be stuck (e.g. a jammed input box refusing turn grants) -- check the session directly.
```

## What is known without diagnosing anything

- Signature: `deadman_commit` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-21T13:33:36+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. Re-escalation is not
suppressed by this file: a NEW episode on a later day files a new document, so a condition
that returns next week is not silently absorbed into today's record.
