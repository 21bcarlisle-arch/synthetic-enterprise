**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [WORKTREE UNDECLARED] 2 UNDECLARED worktree(s) (accretion, report-only): se-dd-salvage(detached), se-seat-executor(detached). Worktrees that are neither main nor a live fork -- acc

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[WORKTREE UNDECLARED] 2 UNDECLARED worktree(s) (accretion, report-only): se-dd-salvage(detached), se-seat-executor(detached). Worktrees that are neither main nor a live fork -- accretion the reconcile discipline covered for processes but not worktrees. REPORT-ONLY (never pruned by inference). Declare it or clean it up through the reconciler.
```

## What is known without diagnosing anything

- Signature: `deadman_worktree_undeclared` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-02T18:57:58+00:00
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
- **2026-09-03** — still live. 29 repeats over 2.5h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `# undeclared worktree(s) (accretion, report-only): se-dd-salvage(detached), se-seat-executor(detached). worktrees that a` (first seen 2026-09-02)
- `# undeclared worktree(s) (accretion, report-only): se-seat-executor(detached). worktrees that are neither main nor a liv` (first seen 2026-09-02)
- `# undeclared worktree(s) (accretion, report-only): se-dd-salvage(detached), se-dd-try(detached), se-seat-executor(detach` (first seen 2026-09-02)
- `# undeclared worktree(s) (accretion, report-only): se-exit-code-landing(detached), se-seat-executor(detached). worktrees` (first seen 2026-09-02)
