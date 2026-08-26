**Severity:** LATENT · **Lane:** H_harness

# [RECONCILE] DRIFT — 7 item(s) diverge from the manifests:

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.7h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[RECONCILE] DRIFT — 7 item(s) diverge from the manifests:
    ✗ [unit] edge-traffic-capture.service: UNDECLARED_UNIT
    ✗ [gap:stale] W1_11_fabric_physics_core
    ✗ [gap:stale] W1_12_premise_trace_generator
    ✗ [gap:measured_not_landed] W2_11_payment_behaviour_source
    ✗ [gap:stale] W2_2_population_draw
    ✗ [gap:never_landed] tools/couple_clv.py
    … and 1 further gap-ledger entr(ies) — full set in the drift signature
```

## What is known without diagnosing anything

- Signature: `auto:1514707144891176` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-20T14:29:29+00:00
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
