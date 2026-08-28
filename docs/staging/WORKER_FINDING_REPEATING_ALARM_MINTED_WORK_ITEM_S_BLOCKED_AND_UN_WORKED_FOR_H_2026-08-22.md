**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [ACT] 2 minted work item(s) BLOCKED and un-worked for 2.2h (no forward-work commit) -- the machine is resting beside open mints, not working them. Escalate each (unblock / re-scope

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[ACT] 2 minted work item(s) BLOCKED and un-worked for 2.2h (no forward-work commit) -- the machine is resting beside open mints, not working them. Escalate each (unblock / re-scope / wall): PLANNER_MINTED_reversibility_action_and_act_2026-07-29.md -> clear ≠ director_level_up, levels are proposals), and record a one-line undo in; PLANNER_MINTED_ssp_negative_lift_cells_2026-07-24.md -> the merit-order / gas-first reconstruction has landed (sequenced with the VALUE_CHAIN work + the Spec 004 reconciliation), at which point the SAME per-cell lift…. A blocked batch is a reason to plan more or escalate, never a licence to rest (R17, EIGHTH CLASS 2026-07-27).
```

## What is known without diagnosing anything

- Signature: `deadman_open_mint` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-22T08:11:14+00:00
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

## Still live

- **Consolidated 2026-08-24.** This condition re-filed itself as a separate document on each of 2026-08-23, 2026-08-24. Those copies said the same thing about the same unchanged condition and are deleted, not archived — there was nothing in them this document does not carry. The mechanism that produced them is fixed in `background/alarm_repetition.py`: idempotence was keyed on a path containing the DATE, so an unchanged alarm refiled at every midnight. It is now keyed on the signature, and a continuing condition appends a line here instead.
- **2026-08-25** — still live. 3 repeats over 0.2h without the state changing. No second document filed: this condition already has one.
- **2026-08-26** — still live. 3 repeats over 0.2h without the state changing. No second document filed: this condition already has one.
- **2026-08-27** — still live. 3 repeats over 0.2h without the state changing. No second document filed: this condition already has one.
- **2026-08-28** — still live. 3 repeats over 0.2h without the state changing. No second document filed: this condition already has one.
