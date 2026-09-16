**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [ACT] 2 SELF-DRAWABLE mint(s) have sat UNDRAWN in in_progress/ for 2.6h with no forward-work commit -- the tick is supposed to DRAW these, so either the draw is wedged or it is res

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[ACT] 2 SELF-DRAWABLE mint(s) have sat UNDRAWN in in_progress/ for 2.6h with no forward-work commit -- the tick is supposed to DRAW these, so either the draw is wedged or it is resting beside drawable work. This page is an INDEPENDENT read of disk (LAW C), so it fires even if the tick's own enumeration reports the authorized set empty. Draw them or explain why they are stuck: PLANNER_MINTED_reversibility_action_and_act_2026-07-29.md ([PLANNER-MINTED] Action the proceed-at-risk class with recorded undos, and send ONE batched [ACT] (2026-07-29)); PLANNER_MINTED_value_chain_observation_window_cap_2026-07-24.md ([PLANNER-MINTED] VALUE_CHAIN: replace the static cap dict with real observation-window mechanics + MC-2 collateral death). (DIRECTOR_RULING_FAILURE_BIAS_LAWS LAW C, 2026-07-27.)
```

## What is known without diagnosing anything

- Signature: `deadman_drawable_undrawn` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-10T08:08:14+00:00
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
- `# self-drawable mint(s) have sat undrawn in in_progress/ for #h with no forward-work commit -- the tick is supposed to d` (first seen 2026-09-10)
