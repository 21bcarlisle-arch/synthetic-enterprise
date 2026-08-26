**Severity:** LATENT · **Lane:** H_harness

# [WORKTREE UNDECLARED] 12 UNDECLARED worktree(s) (accretion, report-only): agent-a7e53b3f1c77109b1(ORPHAN), d30wt(detached), ep6-worktree(ORPHAN), ep6_land(detached), ep6clean-11850

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[WORKTREE UNDECLARED] 12 UNDECLARED worktree(s) (accretion, report-only): agent-a7e53b3f1c77109b1(ORPHAN), d30wt(detached), ep6-worktree(ORPHAN), ep6_land(detached), ep6clean-1185000(detached), ep6probe-1179182(detached). Worktrees that are neither main nor a live fork -- accretion the reconcile discipline covered for processes but not worktrees. REPORT-ONLY (never pruned by inference). Declare it or clean it up through the reconciler.
```

## What is known without diagnosing anything

- Signature: `deadman_worktree_undeclared` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-21T23:58:14+00:00
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
