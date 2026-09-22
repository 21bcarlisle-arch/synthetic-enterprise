**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [ACT] 1 minted work item(s) BLOCKED and un-worked for 2.3h (no forward-work commit) -- the machine is resting beside open mints, not working them. Escalate each (unblock / re-scope

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[ACT] 1 minted work item(s) BLOCKED and un-worked for 2.3h (no forward-work commit) -- the machine is resting beside open mints, not working them. Escalate each (unblock / re-scope / wall): PLANNER_MINTED_ssp_negative_lift_cells_2026-07-24.md -> the merit-order / gas-first reconstruction has landed (sequenced with the VALUE_CHAIN work + the Spec 004 reconciliation), at which point the SAME per-cell lift…. A blocked batch is a reason to plan more or escalate, never a licence to rest (R17, EIGHTH CLASS 2026-07-27).
```

## What is known without diagnosing anything

- Signature: `deadman_open_mint` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-20T03:04:45+00:00
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
- `# minted work item(s) blocked and un-worked for #h (no forward-work commit) -- the machine is resting beside open mints,` (first seen 2026-09-20)
