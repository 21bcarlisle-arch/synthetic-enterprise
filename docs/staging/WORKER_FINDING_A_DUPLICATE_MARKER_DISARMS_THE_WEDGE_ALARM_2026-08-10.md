# [WORKER-FINDING] A duplicate marker reports gate SUCCESS — the wedge alarm was disarmed 188 times today while publishing stayed wedged for 31 hours (2026-08-10)

**Severity:** BLOCKING · **Lane:** H_harness

**Found:** testing the one suspicion left open by the breathing watch — whether "Publish gate
recovered" keeps firing without the content ever advancing. It does, and this is why.

**Impact:** this is the mechanism that kept the 25-hour staleness *invisible*. The directive
BUILD_THE_BREATHING was written about a site that was frozen and silent; the freezing had a cause
per cycle, but the **silence** had this one cause, and it survived every one of the ~18 fixes because
nothing was looking at it.

## Observed, with evidence

```
"Publish gate recovered -- cleared wedge state, re-armed alarm."   188 today
"Already archived at <bucket> (duplicate run): ..."                 43 today
content publishes (commits touching site/data/dashboard.json)        0 today
verification_state on the live site                    paused since 2026-08-09T14:30:09Z (~31h)
```

Recoveries fire on a ~64-minute rhythm (16:50, 17:55, 18:59, 20:03, 21:08, 22:12) — a cadence, not
an event.

The path, `background/process_run_complete.py`:

```python
archived = staging_archive_policy.locate(...)
if archived is not None:
    log("Already archived at {} (duplicate run): {}".format(...))
    return 0                      # <-- routed to record_publish_gate_success()
```

`record_publish_gate_success()` then wipes `failures`, `alerted_at`, `wedge_since`,
`episode_failures`, `suspects`, and resolves the `action_needed` item that is the director's
"publishing is wedged" signal.

A red gate is **not** the bug: it correctly `return 1`s and is recorded as a failure. The bug is that
a marker which was *never processed at all* reports the gate healthy.

## This is a sibling of an already-fixed defect, and the fix stopped one door short

The same file already documents this exact class, in `main`'s own docstring:

> *"a lock-skip below returns EXIT_LOCK_SKIPPED (75), a THIRD outcome distinct from both 'ran to
> completion' (0) and 'a real processing error' (1). It used to return 0 … and `background_worker`'s
> sweep therefore fed rc==0 into `record_publish_gate_success()`, wiping the H15 wedge streak for a
> marker it had never published (fail-open: the detector disarmed by its own input)."*

And the router says it outright: a lock-skip is *"evidence of NOTHING about the gate's health — so it
records NEITHER a success NOR a failure."* **A duplicate is evidence of exactly as little.** The
2026-07-29 fix gave the lock-skip its own exit code and left its sibling returning 0
(cf. `feedback_audit_sibling_half_for_hardened_class`).

## Why it fired so hard today, specifically

~34 stale `run_complete_*` markers from 2026-08-09 sit in staging. Every sweep re-globs them, finds
each already archived, and returns 0 — so the alarm is cleared several times an hour by markers
nobody published. The backlog and the blindness are the same fact.

## Proposed atom (queued, not built — SELF_INTERRUPT_DISCIPLINE)

**`OPS_duplicate_marker_is_not_a_success`** — give the already-archived path its own third outcome
alongside `EXIT_LOCK_SKIPPED`, and have the router record neither success nor failure for it, exactly
as the lock-skip does now. Then **close the class rather than the instance** (R10): every `return 0`
in `main`/`_process` must be reachable only from a path that actually gated something, asserted by a
test that enumerates them — a new no-op path added later must fail by name instead of quietly
joining the class.

R15 both ways: mutation — restore `return 0` on the duplicate path and a driven duplicate must clear
a live wedge state (test reds); and a genuine green publish must still clear it.

**Recommendation: P1, above the drain.** It is small, and until it lands every wedge alarm this
machine raises can be silently cancelled by a stale marker — which makes the alarm unciteable as
evidence that publishing is healthy. It also means today's "gate recovered" lines, including the one
at 22:12 I was about to read as progress, say nothing at all.
