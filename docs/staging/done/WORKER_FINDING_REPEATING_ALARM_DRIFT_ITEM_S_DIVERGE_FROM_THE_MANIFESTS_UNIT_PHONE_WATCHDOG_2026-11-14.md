**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [RECONCILE] DRIFT — 17 item(s) diverge from the manifests:

<!-- counts:begin -->
**Filed automatically by `background/alarm_repetition.py`, not by a person.** This condition
has been **observed to hold on 1 separate day(s)**, on **2026-11-14**, and **1 member(s)** of
the family `auto:dbe2cc06073a6b28` have fired. Both counts are DERIVED from this document's own
dated lines every time the alarm fires again, so they age with the document rather than with
its first firing.

Separately, the observer that last filed reported **3 consecutive firing(s) without a state
change**, over **2.5h**. That is `notify()`'s streak counter, which resets; it is not a total
and does not combine with the two counts above.
<!-- counts:end -->

## The alarm, verbatim

```
[RECONCILE] DRIFT — 17 item(s) diverge from the manifests:
    ✗ [unit] phone-watchdog.service: UNDECLARED_UNIT
    ✗ [unit] token-proxy.service: UNDECLARED_UNIT
    ✗ [gap:stale] EP1_clv_three_horizon
    ✗ [gap:stale] PB3_book_growth_as_earned_outcome
    ✗ [gap:stale] W1_11_fabric_physics_core
    ✗ [gap:stale] W1_12_premise_trace_generator
    ✗ [gap:support_changed] W2_11_payment_behaviour_source
    … and 10 further gap-ledger entr(ies) — full set in the drift signature
```

## What is known without diagnosing anything

- Signature: `auto:dbe2cc06073a6b28` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-11-14T05:18:10+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS` = 3, applied by `notify()`)
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

A REPEATING FAILURE IS ONE OF THE THREE TRIGGERS FOR THE END-TO-END CHECK (director,
2026-10-04): before fixing the instance, write the section below -- the loop may be the world,
the maths, the canon or the frame, not the code that is alarming.

## End-to-end check

The alarm is not the world, the maths or the canon: it is two declaration gaps in the harness, and the alarm was right.

- **phone-watchdog.service / .timer**: installed 4 Nov by the director's watchdog ruling (0fa98c781a), with committed unit files under `background/`, but never given a row in `background/schedule_manifest.yaml`. Real drift: the dead-man's only path to the phone was invisible to the reconciler that is meant to see it.
- **token-proxy.service**: retired by the director on 27 Sep; its unit was stopped and disabled, and the file stayed installed. `_process_manifest_unit_names` counted only `owner: systemd` rows, so a retired row could not declare its own lingering file. The alarm was a false positive on that one, and the reconciler was wrong, not the box. Deleting the unit file would also have silenced it, but the file is the retirement's record, and `process_reconciler` already alarms `RETIRED_RUNNING` if it ever runs again.
- **The other 15 items** (stale, never_measured, never_landed, support_changed) are the gap ledger's measurement debts. They are a real backlog owned by `background/gap_ledger_reconciler.py`'s register, not this alarm's condition, and are not touched here. The signature will change now the unit half has cleared, so if those 15 keep it firing, it files as a fresh, gap-only episode, which is the right shape for them.

No concern for the director.

## Still live

## Instances seen
- `drift — # item(s) diverge from the manifests: ✗ [unit] phone-watchdog.service: undeclared_unit ✗ [unit] token-proxy.serv` (first seen 2026-11-14)

## Re-asked
- **2026-11-14** — re-asked: **still_holds**. observed 2026-11-14, within the 3-day bar.
- **2026-11-15** — re-asked: **still_holds**. observed 2026-11-14, within the 3-day bar.

## Done

*(worker tick, 15 Nov 2026)* Both unit items are fixed. The two phone-watchdog units are declared in `schedule_manifest.yaml`. `schedule_reconciler._process_manifest_unit_names` now also counts `state: retired` rows. Tests: `test_a_retired_process_row_declares_its_lingering_unit`, which keeps a live non-systemd row out so the partition has both sides, and `test_the_phone_watchdog_units_are_declared`. Mutation: reverting the reconciler line reds the first test (1 failed, 17 passed). Live: `python3 -m background.schedule_reconciler` reads 0 drift alarms, 25 OK. Reverse by deleting the two manifest rows and the `or ... retired` clause.
