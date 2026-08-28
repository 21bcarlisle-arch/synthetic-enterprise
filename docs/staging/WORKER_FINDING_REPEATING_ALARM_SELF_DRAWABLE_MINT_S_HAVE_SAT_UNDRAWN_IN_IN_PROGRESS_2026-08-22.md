**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [ACT] 3 SELF-DRAWABLE mint(s) have sat UNDRAWN in in_progress/ for 2.2h with no forward-work commit -- the tick is supposed to DRAW these, so either the draw is wedged or it is res

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[ACT] 3 SELF-DRAWABLE mint(s) have sat UNDRAWN in in_progress/ for 2.2h with no forward-work commit -- the tick is supposed to DRAW these, so either the draw is wedged or it is resting beside drawable work. This page is an INDEPENDENT read of disk (LAW C), so it fires even if the tick's own enumeration reports the authorized set empty. Draw them or explain why they are stuck: PLANNER_MINTED_generator_draw_wiring_2026-07-24.md ([PLANNER-MINTED] Ship the population-generator DRAW-WIRING (2026-07-24)); PLANNER_MINTED_one_node_to_depth_with_charts_2026-07-28.md ([PLANNER-MINTED] One node filled to full depth, with charts (ruling's pilot output) (2026-07-28)); PLANNER_MINTED_value_chain_observation_window_cap_2026-07-24.md ([PLANNER-MINTED] VALUE_CHAIN: replace the static cap dict with real observation-window mechanics + MC-2 collateral death). (DIRECTOR_RULING_FAILURE_BIAS_LAWS LAW C, 2026-07-27.)
```

## What is known without diagnosing anything

- Signature: `deadman_drawable_undrawn` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-22T08:11:18+00:00
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
