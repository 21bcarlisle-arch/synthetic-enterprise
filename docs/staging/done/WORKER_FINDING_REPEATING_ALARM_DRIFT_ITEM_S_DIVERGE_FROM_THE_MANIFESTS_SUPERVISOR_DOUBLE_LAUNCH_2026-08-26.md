**Severity:** LATENT · **Lane:** H_harness

# [RECONCILE] DRIFT — 10 item(s) diverge from the manifests:

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **1.0h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[RECONCILE] DRIFT — 10 item(s) diverge from the manifests:
    ✗ supervisor: DOUBLE_LAUNCH
    ✗ [gap:stale] W1_11_fabric_physics_core
    ✗ [gap:stale] W1_12_premise_trace_generator
    ✗ [gap:support_changed] W2_11_payment_behaviour_source
    ✗ [gap:stale] W2_2_population_draw
    ✗ [gap:never_measured] W1_6b_merit_order_reconstruction
    … and 4 further gap-ledger entr(ies) — full set in the drift signature
```

## What is known without diagnosing anything

- Signature: `auto:7da6cf2aaa887aa0` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-26T04:37:19+00:00
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
