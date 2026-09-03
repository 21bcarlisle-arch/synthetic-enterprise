**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [WORKTREE UNDECLARED] 3 UNDECLARED worktree(s) (accretion, report-only): agent-a7e53b3f1c77109b1(ORPHAN), gatecheck(detached), wedge-check-head(detached). Worktrees that are neithe

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[WORKTREE UNDECLARED] 3 UNDECLARED worktree(s) (accretion, report-only): agent-a7e53b3f1c77109b1(ORPHAN), gatecheck(detached), wedge-check-head(detached). Worktrees that are neither main nor a live fork -- accretion the reconcile discipline covered for processes but not worktrees. REPORT-ONLY (never pruned by inference). Declare it or clean it up through the reconciler.
```

## What is known without diagnosing anything

- Signature: `deadman_worktree_undeclared` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-26T06:15:28+00:00
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
- **2026-08-27** — still live. 32 repeats over 2.7h without the state changing. No second document filed: this condition already has one.
- **2026-08-28** — still live. 32 repeats over 2.8h without the state changing. No second document filed: this condition already has one.
- **2026-08-29** — still live. 76 repeats over 6.4h without the state changing. No second document filed: this condition already has one.
- **2026-08-30** — still live. 159 repeats over 14.3h without the state changing. No second document filed: this condition already has one.

---

## RESOLVED 2026-08-30 — and the repetition was the finding, exactly as this document said

**Discharged:** `tests/background/test_fork_reconciler.py::test_an_unpinned_unmerged_detached_head_is_refused_AND_reads_as_stranded`

**State now: `WORKTREE_CLEAN`, 1 declared worktree, none undeclared.** Four are gone.

### Why it repeated 159 times over 14.3 hours without converging

Not because nobody drew it. **The only sanctioned mechanism refused three of the four by
construction, and then scored its own refusal as success.**

`classify_worktree_reap` returned, for every detached worktree,
`"detached/no branch -- undetermined, never reaped"` — and `"detached/no branch"` was a member of
`_LIVE_REFUSALS`, the tuple that separates *the control correctly sparing something* from *the
control stuck on something*. So `refusal_is_stranded` scored three permanently-unreapable
directories as the reaper working properly.

That separation exists for precisely this failure. Its own comment says so: *"conflating these is
what let 26 worktrees accumulate over 16 days behind a green WORKTREE_REAP_CLEAN (H24,
2026-08-03)."* It was blind in the one population that was actually accumulating — a control
keyed to a structure that had moved, going quiet rather than loud.

The refusal was not paranoid; it was **incomplete**. "Undetermined" was true of the code, not of
the worktree. A detached HEAD is a commit, and a commit is determinable exactly as a branch tip
is.

### The repair

`classify_detached_head(head, reachable, salvage_tag)` — three states, same vocabulary as
`classify_branch`:

| state | meaning | outcome |
|---|---|---|
| `MERGED` | HEAD reachable from main | eligible — removing the directory touches no commit not already on main |
| `SALVAGED` | unmerged but pinned by a salvage tag | eligible — the directory is a redundant working copy |
| `ORPHAN` | unmerged and unpinned | **refused, and STRANDED** — reported loudly, never reaped |

`scan_worktrees` now parses the porcelain's `HEAD <sha>` line (every worktree has one; only some
have a branch). `salvage_detached_head` is the detached counterpart of `salvage_and_reap`, so the
route out of an `ORPHAN` refusal is a mechanism rather than a hand-typed `git tag` — *a refusal
with no door beside it is a stall wearing a control's clothes.* `"detached/no branch"` is out of
`_LIVE_REFUSALS`.

Threaded through **both** doors (`evaluate_worktree_reap` and `reap_one_worktree`) from one
helper, with a test that they cannot disagree: two doors with two answers is how a directory gets
removed by one and refused by the other.

### What was actually removed, and what it cost

Each was checked for lost work before anything was touched — all four were CLEAN (zero
uncommitted files):

| worktree | age | unique commits | disposition |
|---|---|---|---|
| `.claude/worktrees/agent-a7e53b3f1c77109b1` | 2026-08-18 | 1 salvage commit, 2 lines of `test_execution_log.jsonl` | branch ORPHAN + salvage tag — the pre-existing rule already covered it |
| `/tmp/tmp.c0ZK8EkOa1/head` | 2026-08-28 | **none** | detached `MERGED` — reachable from main |
| `/var/tmp/wedge-check-head` | 2026-08-20 | 1 salvage commit, 1 line of `test_execution_log.jsonl` | detached `ORPHAN` → tagged `salvage/detached-3a1c2e70a7e4` → eligible |
| `/tmp/gatecheck` | 2026-08-26 | 1 salvage commit, 76 files | detached `ORPHAN` → tagged `salvage/detached-e614a788616b` → eligible |

`/tmp/gatecheck` was the only one that could plausibly have held real work — the map-split of
2026-08-26 (`MAP_SPLIT_2026-08-26.md`, `tools/maturity_map_store.py`). **Checked rather than
assumed:** every one of its 76 files exists on main, the two headline files are byte-identical to
main, and every file where the salvage carried lines main lacks is a generated observability or
site-data artefact, or a source file where main is 18–249 lines ahead. It is a four-day-old
superseded snapshot. Both commits are pinned by verified salvage tags and are recoverable.

### The measurement, before and after

Before: 4 undeclared worktrees, of which the reaper could act on exactly **1**.
After: **4 of 4**, two of them via a deliberate, tagged salvage that leaves a ref behind.

Two existing tests pinned the old answer and were updated rather than deleted, each with the
reason recorded beside it: `test_scan_worktrees_parses_porcelain` (the `head` field) and
`test_refusal_is_stranded_splits_the_two_classes` (detached moves from `live` to `stuck`).

Nine new falsifiers, including the fail-closed case — a caller that determines nothing is refused
AND stranded, because "I did not check" must never read as "it is live".
