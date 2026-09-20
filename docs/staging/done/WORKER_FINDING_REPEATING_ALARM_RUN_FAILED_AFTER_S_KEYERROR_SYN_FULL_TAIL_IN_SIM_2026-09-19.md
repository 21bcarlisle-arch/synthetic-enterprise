**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `does-minting-arrivals-widen-the-scored-decision-population`

# [SIM] Run FAILED after 989s — KeyError: 'SYN-2016-008' (full tail in sim-runner-log.md)

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.7h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[SIM] Run FAILED after 989s — KeyError: 'SYN-2016-008' (full tail in sim-runner-log.md)
```

## What is known without diagnosing anything

- Signature: `auto:1c699a83ecb45075` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-19T11:09:21+00:00
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
- `run failed after #s — keyerror: 'syn-#-#' (full tail in sim-runner-log.md)` (first seen 2026-09-19)

---

## RESOLVED 2026-09-20 — the cause, the repair, and the measurement that closes it

**The severity above was wrong while this was live, and is corrected here rather than quietly.**
It was filed `LATENT · Atom: unminted` — "real defect; does not invalidate anything published or
any control's verdict". It invalidated every value-arm measurement taken while it stood: the world
that mints arrivals could not complete a single pass, so the arms book was confined to the
pre-producer population by a crash with no recorded cause. That is `BLOCKING` by the definition in
`background/finding_severity.py`. It reads `RECORDED` now because the condition is resolved and no
work is owed — not because it was ever latent.

**The cause.** A registration/advance pairing in `simulation/run_phase2b.py::_main`, inside the
decision-leg block. The churn-journey REGISTRATION sat inside `if old_decision_leg_rate is not
None:`; the `advance` sat outside it. The pairing therefore held only while every account's decision
leg opened on a product that strikes a rate. **An account that opens on the DEFAULT TARIFF never
strikes one**, reaches its first in-window term unregistered, and raises `KeyError` at
`churn_journey.py:218`. The defect predates the C6 arrival producer; the producer created the first
account that could reach it — a branch that was not merely untested but *unreachable* until a world
change made it reachable, and then fatal rather than wrong.

**Why it looked causeless.** This alarm first fired at 11:09Z, about five hours BEFORE the arrival
producer was committed (`7bff15179`, 16:24 BST). Every reader who checked the log against the commit
history concluded the producer could not be responsible. The producer was live in a working tree and
being run before it was committed — the ordinary case in this tree — so the commit clock was the
wrong clock to ask.

**The repair: `3a8d15185`** (2026-09-19 18:08:35 +0100). The registration guard is repeated
immediately above the `advance`, and `tenure_for_est` is hoisted out of the
`old_decision_leg_rate is not None` branch so both sites share one expression. Verified present in
the working copy the runner daemon actually executes, not merely in the commit —
`simulation/run_phase2b.py:2599` and `:2308`.

**The measurement that closes it**, from the daemon's own log (`docs/observability/sim-runner-log.md`),
straddling the repair:

| window | runs | outcome |
|---|---:|---|
| 14:57–16:40 UTC, before the repair | 6 | **all `Run FAILED`**, each at 915–980s |
| after the repair | 4 | **all `Run complete`**, 1,465–1,535s |

Zero `Run FAILED` and zero occurrences of `SYN-2016-008` anywhere in the log after 16:40 UTC. The
arrivals-ON value-arm leg — the pass this defect made impossible — also ran to completion in 1,491s
and its artefact landed at `db00d334c`.

*The honest caveat on that table:* the first completion (17:10 UTC) belongs to a run that STARTED at
16:45 UTC, before the repair commit landed at 17:08 UTC, so the log alone cannot say whether it
imported the repaired module. The three later runs (started 19:00, 21:15 and 23:31 UTC) are
unambiguously post-repair and all completed. The attribution does not rest on the first one.

**Not fixed here, and not claimed:** whether any OTHER route into that `advance` exists for an
account with no struck rate. The pairing is repaired; the class is not. A survey of every
`advance`-like call whose registration sits inside a narrower branch is a separate pass.

Diagnosis and repair:
`docs/staging/SEAT_RESULT_THE_WORLD_THAT_MINTS_ARRIVALS_CANNOT_FINISH_A_VALUE_ARM_PASS_AND_THE_ALARM_THAT_SAID_SO_HAD_NO_CAUSE_2026-09-19.md`.
Result of the pass it unblocked:
`docs/staging/SEAT_RESULT_MINTING_ARRIVALS_ADDS_SEVEN_DECISIONS_AND_ONE_PERCENT_OF_NULL_WIDTH_AND_MY_OWN_PREDICTION_WAS_REFUTED_2026-09-19.md`.
