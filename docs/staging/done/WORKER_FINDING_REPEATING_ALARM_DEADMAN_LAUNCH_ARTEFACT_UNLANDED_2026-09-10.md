**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [LAUNCH UNLANDED] 1 file(s) a finished run wrote into this tree are in no commit: value-cycle-ab-20260910 [artefact]: UNTRACKED -- the job finished and wrote `docs/observability/va

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **1.1h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[LAUNCH UNLANDED] 1 file(s) a finished run wrote into this tree are in no commit: value-cycle-ab-20260910 [artefact]: UNTRACKED -- the job finished and wrote `docs/observability/value_cycle_ab_s1_three_arm_20260910.json` (its `artefact`), and that file is in no commit and not even staged. The register says this work is done; git says it does not exist. Land it, or say on the record why it is not landable The register says the work is done and git has never seen it. Land them, or record why they are not landable.
```

## What is known without diagnosing anything

- Signature: `deadman_launch_artefact_unlanded` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-10T13:27:39+00:00
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
- **2026-09-11** — still live. 26 repeats over 2.4h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `# file(s) a finished run wrote into this tree are in no commit: value-cycle-ab-# [artefact]: untracked -- the job finish` (first seen 2026-09-10)
- `# file(s) a finished run wrote into this tree are in no commit: arms-rerun-# [artefact]: untracked -- the job finished a` (first seen 2026-09-10)
