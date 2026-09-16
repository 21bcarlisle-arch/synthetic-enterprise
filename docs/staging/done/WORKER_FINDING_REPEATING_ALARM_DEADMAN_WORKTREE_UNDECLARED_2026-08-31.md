**Severity:** LATENT · **Lane:** H_harness

# [WORKTREE UNDECLARED] 1 UNDECLARED worktree(s) (accretion, report-only): se-seat-executor(detached). Worktrees that are neither main nor a live fork -- accretion the reconcile disc

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[WORKTREE UNDECLARED] 1 UNDECLARED worktree(s) (accretion, report-only): se-seat-executor(detached). Worktrees that are neither main nor a live fork -- accretion the reconcile discipline covered for processes but not worktrees. REPORT-ONLY (never pruned by inference). Declare it or clean it up through the reconciler.
```

## What is known without diagnosing anything

- Signature: `deadman_worktree_undeclared` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-31T17:13:28+00:00
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
- **2026-09-01** — still live. 3 repeats over 0.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-02** — still live. 28 repeats over 2.4h without the state changing. No second document filed: this condition already has one.
- **2026-09-03** — still live. 3 repeats over 0.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-04** — still live. 7 repeats over 0.6h without the state changing. No second document filed: this condition already has one.
- **2026-09-05** — still live. 210 repeats over 19.1h without the state changing. No second document filed: this condition already has one.
- **2026-09-06** — still live. 12 repeats over 1.1h without the state changing. No second document filed: this condition already has one.
- **2026-09-07** — still live. 18 repeats over 1.5h without the state changing. No second document filed: this condition already has one.
- **2026-09-08** — still live. 50 repeats over 5.5h without the state changing. No second document filed: this condition already has one.
- **2026-09-09** — still live. 3 repeats over 0.6h without the state changing. No second document filed: this condition already has one.
- **2026-09-10** — still live. 3 repeats over 0.3h without the state changing. No second document filed: this condition already has one.
- **2026-09-11** — still live. 5 repeats over 0.3h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `# undeclared worktree(s) (accretion, report-only): se-seat-executor(detached). worktrees that are neither main nor a liv` (first seen 2026-09-02)
- `# undeclared worktree(s) (accretion, report-only): se-dd-salvage(detached), se-seat-executor(detached). worktrees that a` (first seen 2026-09-02)
- `# undeclared worktree(s) (accretion, report-only): mergecheck(detached), se-seat-executor(detached). worktrees that are ` (first seen 2026-09-03)
- `# undeclared worktree(s) (accretion, report-only): puretip(detached), se-seat-executor(detached). worktrees that are nei` (first seen 2026-09-03)
- `# undeclared worktree(s) (accretion, report-only): se-floorrun-#(detached), se-seat-executor(detached). worktrees that a` (first seen 2026-09-03)
- `# undeclared worktree(s) (accretion, report-only): wt(detached), se-floorrun-#(detached), se-seat-executor(detached). wo` (first seen 2026-09-03)
- `# undeclared worktree(s) (accretion, report-only): se-floorrun-#(detached), se-onevar-anchor(detached), se-seat-executor` (first seen 2026-09-04)
- `# undeclared worktree(s) (accretion, report-only): se-direction-battery(detached), se-floorrun-#(detached), se-seat-exec` (first seen 2026-09-05)
- `# undeclared worktree(s) (accretion, report-only): se-convergence-sweep(detached), se-direction-battery(detached), se-fl` (first seen 2026-09-05)
- `# undeclared worktree(s) (accretion, report-only): se-battery-supervisor(detached), se-direction-battery(detached), se-f` (first seen 2026-09-05)
- `# undeclared worktree(s) (accretion, report-only): se-battery-supervisor(detached), se-dircol-#(detached), se-dircol-#(d` (first seen 2026-09-05)
- `# undeclared worktree(s) (accretion, report-only): se-dircol-#(detached), se-dircol-#(detached), se-dircol-#(detached), ` (first seen 2026-09-05)
- `# undeclared worktree(s) (accretion, report-only): se-direction-battery(detached), se-floorrun-#(detached), se-gif-batte` (first seen 2026-09-06)
- `# undeclared worktree(s) (accretion, report-only): verifyx(detached), se-direction-battery(detached), se-floorrun-#(deta` (first seen 2026-09-06)
- `# undeclared worktree(s) (accretion, report-only): headext(detached), se-direction-battery(detached), se-floorrun-#(deta` (first seen 2026-09-06)
- `# undeclared worktree(s) (accretion, report-only): headext(detached), headext#(detached), headext#(detached), headext#(d` (first seen 2026-09-06)
- `# undeclared worktree(s) (accretion, report-only): headext#(detached), headext#(detached), headext#(detached), se-direct` (first seen 2026-09-06)
- `# undeclared worktree(s) (accretion, report-only): headchk(detached), se-direction-battery(detached), se-floorrun-#(deta` (first seen 2026-09-07)
- `# undeclared worktree(s) (accretion, report-only): ox(detached), se-direction-battery(detached), se-floorrun-#(detached)` (first seen 2026-09-07)
- `# undeclared worktree(s) (accretion, report-only): ox(detached), w#_extract(detached), w#_pristine(detached), se-directi` (first seen 2026-09-07)
- `# undeclared worktree(s) (accretion, report-only): headx(detached), ox(detached), w#_extract(detached), w#_pristine(deta` (first seen 2026-09-07)
- `# undeclared worktree(s) (accretion, report-only): headx(detached), w#_extract(detached), w#_pristine(detached), se-dire` (first seen 2026-09-07)
- `# undeclared worktree(s) (accretion, report-only): wedge_head(detached), se-direction-battery(detached), se-floorrun-#(d` (first seen 2026-09-07)
- `# undeclared worktree(s) (accretion, report-only): w#_#_headcheck(detached), se-direction-battery(detached), se-floorrun` (first seen 2026-09-07)
- `# undeclared worktree(s) (accretion, report-only): cm_headcheck(detached), se-direction-battery(detached), se-floorrun-#` (first seen 2026-09-07)
- `# undeclared worktree(s) (accretion, report-only): wt(detached), se-direction-battery(detached), se-floorrun-#(detached)` (first seen 2026-09-08)
- `# undeclared worktree(s) (accretion, report-only): wt(detached), head-extract-#(detached), se-direction-battery(detached` (first seen 2026-09-08)
- `# undeclared worktree(s) (accretion, report-only): head-extract-#(detached), se-direction-battery(detached), se-floorrun` (first seen 2026-09-08)
- `# undeclared worktree(s) (accretion, report-only): wt-merge(detached), se-direction-battery(detached), se-floorrun-#(det` (first seen 2026-09-08)
- `# undeclared worktree(s) (accretion, report-only): band_tree(detached), band_tree#(detached), se-direction-battery(detac` (first seen 2026-09-08)
- `# undeclared worktree(s) (accretion, report-only): band_tree#(detached), se-direction-battery(detached), se-floorrun-#(d` (first seen 2026-09-08)
- `# undeclared worktree(s) (accretion, report-only): ci_head(detached), se-direction-battery(detached), se-floorrun-#(deta` (first seen 2026-09-08)
- `# undeclared worktree(s) (accretion, report-only): headwt(detached), se-direction-battery(detached), se-floorrun-#(detac` (first seen 2026-09-08)
- `# undeclared worktree(s) (accretion, report-only): hx(detached), se-direction-battery(detached), se-floorrun-#(detached)` (first seen 2026-09-08)
- `# undeclared worktree(s) (accretion, report-only): w#_#_headcheck(detached), se-concordance-null-#(detached), se-directi` (first seen 2026-09-09)
- `# undeclared worktree(s) (accretion, report-only): headred_va(detached), se-concordance-null-#(detached), se-direction-b` (first seen 2026-09-09)
- `# undeclared worktree(s) (accretion, report-only): se-concordance-null-#(detached), se-direction-battery(detached), se-f` (first seen 2026-09-09)
- `# undeclared worktree(s) (accretion, report-only): pristm#dz(detached), w#z#a(detached), w#c#h#d(detached), se-concordan` (first seen 2026-09-09)
- `# undeclared worktree(s) (accretion, report-only): headwt#(detached), pristm#dz(detached), w#z#a(detached), w#c#h#d(deta` (first seen 2026-09-09)
- `# undeclared worktree(s) (accretion, report-only): headwt#(detached), head_extract_w#_#(detached), se-concordance-null-#` (first seen 2026-09-09)
- `# undeclared worktree(s) (accretion, report-only): headwt#(detached), se-concordance-null-#(detached), se-direction-batt` (first seen 2026-09-09)
- `# undeclared worktree(s) (accretion, report-only): wt_ceiling(detached), se-concordance-null-#(detached), se-direction-b` (first seen 2026-09-09)
- `# undeclared worktree(s) (accretion, report-only): llg_head_#(detached), se-concordance-null-#(detached), se-direction-b` (first seen 2026-09-10)
- `# undeclared worktree(s) (accretion, report-only): llg_base(detached), se-concordance-null-#(detached), se-direction-bat` (first seen 2026-09-10)
- `# undeclared worktree(s) (accretion, report-only): se-floorrun-#(detached), se-headcheck-#(detached), se-seat-executor(d` (first seen 2026-09-10)
- `# undeclared worktree(s) (accretion, report-only): se-floorrun-#(detached), se-lane#-merge-#(detached), se-seat-executor` (first seen 2026-09-11)
- `# undeclared worktree(s) (accretion, report-only): se-floorrun-#(detached), se-lane#-merge-#(detached), se-lane#-merge-#` (first seen 2026-09-11)
