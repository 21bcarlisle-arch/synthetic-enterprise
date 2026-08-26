**Severity:** LATENT · **Lane:** H_harness

# [FORK ORPHANS] 2 orphaned fork branch(es) never merged home [ENFORCE (salvage+reap)]: salvage/ep6-wall-protocol-typing-20260819, worktree-agent-a7e53b3f1c77109b1; reaped 0/2. Fork 

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **1.5h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[FORK ORPHANS] 2 orphaned fork branch(es) never merged home [ENFORCE (salvage+reap)]: salvage/ep6-wall-protocol-typing-20260819, worktree-agent-a7e53b3f1c77109b1; reaped 0/2. Fork branches that built work and never merged home -- the fragmentation disease. Reap-only: each is salvage-tagged then reaped (enforce-mode) or flagged (report-first); a good orphan is recoverable from its salvage tag and re-runnable, never auto-landed unreviewed. Triage: docs/observability/ + salvage/* tags.
```

## What is known without diagnosing anything

- Signature: `deadman_fork_orphan` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-21T14:48:48+00:00
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
