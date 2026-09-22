**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [WORKTREE UNDECLARED] 5 UNDECLARED worktree(s) (accretion, report-only): se-floorrun-20260910(detached), se-lane0-merge-20260911(detached), se-lane0-merge-20260911b(detached), se-l

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **5 times without its state changing**, over **95.9h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 5th page does not.

## The alarm, verbatim

```
[WORKTREE UNDECLARED] 5 UNDECLARED worktree(s) (accretion, report-only): se-floorrun-20260910(detached), se-lane0-merge-20260911(detached), se-lane0-merge-20260911b(detached), se-lane0-merge-20260911c(detached), se-seat-executor(detached). Worktrees that are neither main nor a live fork -- accretion the reconcile discipline covered for processes but not worktrees. REPORT-ONLY (never pruned by inference). Declare it or clean it up through the reconciler.
```

## What is known without diagnosing anything

- Signature: `deadman_worktree_undeclared` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-11T07:29:33+00:00
- Repeats before escalation: 5 (threshold `ESCALATE_AFTER_REPEATS`)
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
- **2026-09-16** — still live. 3 repeats over 0.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-17** — still live. 22 repeats over 2.1h without the state changing. No second document filed: this condition already has one.
- **2026-09-18** — still live. 51 repeats over 5.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-19** — still live. 70 repeats over 6.8h without the state changing. No second document filed: this condition already has one.
- **2026-09-20** — still live. 106 repeats over 10.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-21** — still live. 298 repeats over 42.0h without the state changing. No second document filed: this condition already has one.
- **2026-09-22** — still live. 3 repeats over 0.1h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `# undeclared worktree(s) (accretion, report-only): se-floorrun-#(detached), se-lane#-merge-#(detached), se-lane#-merge-#` (first seen 2026-09-15)
- `# undeclared worktree(s) (accretion, report-only): se-floorrun-#(detached), se-forkmerge-#(detached), se-lane#-merge-#(d` (first seen 2026-09-15)
- `# undeclared worktree(s) (accretion, report-only): se_verify_env(detached), se-floorrun-#(detached), se-forkmerge-#(deta` (first seen 2026-09-15)
- `# undeclared worktree(s) (accretion, report-only): envelope-remerge-#(detached), se-floorrun-#(detached), se-forkmerge-#` (first seen 2026-09-15)
- `# undeclared worktree(s) (accretion, report-only): lane#_merge_regen(detached), se-floorrun-#(detached), se-forkmerge-#(` (first seen 2026-09-16)
- `# undeclared worktree(s) (accretion, report-only): se-floorrun-#(detached), se-floorrun-#(detached), se-forkmerge-#(deta` (first seen 2026-09-17)
- `# undeclared worktree(s) (accretion, report-only): se-floorrun-#(detached), se-floorrun-head-#(detached), se-forkmerge-#` (first seen 2026-09-18)
- `# undeclared worktree(s) (accretion, report-only): feed-regen-#db#fu(detached), regen_wt(detached), se-floorrun-#(detach` (first seen 2026-09-19)
- `# undeclared worktree(s) (accretion, report-only): feed-regen-n#ivvmun(detached), regen_wt(detached), se-floorrun-#(deta` (first seen 2026-09-19)
- `# undeclared worktree(s) (accretion, report-only): roster-wt(detached), se-floorrun-#(detached), se-floorrun-head-#(deta` (first seen 2026-09-19)
