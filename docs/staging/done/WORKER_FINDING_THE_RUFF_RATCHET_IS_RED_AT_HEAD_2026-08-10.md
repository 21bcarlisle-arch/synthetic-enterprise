# WORKER FINDING — the static-quality ratchet is RED at HEAD, and not because of any working-tree dirt

**Found:** 2026-08-10, during KNIFE3 step 11 (`A_composition_lift`, bill-assembly cut).
**Queued, not fixed on sight** (SELF_INTERRUPT_DISCIPLINE): the machine is not blocked by it,
the fix belongs to whoever owns the two files, and the supply of harness findings is infinite.

## The observation, measured

`tests/architecture/test_static_quality_ratchet.py` has two failing tests:

```
test_ruff_no_rule_exceeds_baseline    I001: baseline 1384, now 1386
test_ruff_baseline_matches_frozen_census   changed: {'I001': (1384, 1386)}
```

The obvious reading is "some lane left uncommitted imports unsorted" — this repo has a recorded
class for exactly that (`feedback_ruff_baseline_is_calibrated_to_uncommitted_work`, and the
working tree carried 256 modified files at the time). **That reading is wrong here, and it was
checked rather than assumed:**

```
$ git archive HEAD | tar -x -C /tmp/headchk
$ cd /tmp/headchk && ruff check . --select I001 | grep -c I001
1386
```

A CLEAN CHECKOUT OF HEAD, with no working tree involved at all, carries 1386. The frozen baseline
is 1384. **The ratchet is red on the committed tree.** Nothing uncommitted is implicated.

Per-file confirmation that step 11 is not the cause: every `.py` file step 11 touched or created
was compared against its own HEAD text, and none moved its I001 count. The two files step 11
created (`company/billing/monthly_bill_assembly.py`, `company/interfaces/bill_assembly.py`)
contribute **zero** I001 — one was fixed at source when ruff first flagged it, never by raising a
baseline. The count is 1386 with step 11's changes and 1386 without them.

## Why this matters more than two unsorted import blocks

This is the `a control committed without its mechanism reds HEAD` class again, and the same
`the record can outrun the code` shape: a frozen census was committed that does not describe the
tree it was committed against. While that is true:

- The control **cannot fail on its own defect** in the R15 sense — it is red for a reason nobody
  introduced, so a genuinely NEW I001 regression raises 1386 to 1387 and lands in a test that was
  already failing. An always-red detector is as ignored as a blind one
  (`feedback_always_red_detector_is_as_ignored_as_a_blind_one`).
- Anyone reading the failure will reach for the recorded uncommitted-work explanation, which is
  the wrong diagnosis and will send them to check a working tree that is innocent. That is why the
  clean-checkout measurement is written down here rather than just the count.

## What the fix is NOT

**Do not raise the baseline to 1386.** The standing rule from step 8 is "Ruff I001 fixed at source,
never by raising the frozen baseline". Raising it would ratify whatever drifted and permanently
lose the two violations.

## The work

1. Identify the two blocks: diff the per-file I001 census of a clean HEAD checkout against the
   frozen census's provenance commit (baseline frozen 2026-08-06) to find which files gained them.
2. Fix those two import blocks at source (`ruff check --fix` on those files only).
3. Re-run `tests/architecture/test_static_quality_ratchet.py` — expect the census to match 1384
   again with no baseline edit in the diff.
4. Worth asking as part of the same draw, since this is the second frozen-census-outruns-the-tree
   finding: what would have caught the drift at the commit that caused it? The census test exists
   and did not stop it landing, which is the actual control question.

---

## CLOSED — 2026-08-10, scheduled worker tick (episode-4 wedge draw)

**Landed:** `750cdff15` (pushed; `origin/main` == `750cdff15`).

Steps 1-3 of "The work" above, done as written:

**1. The two blocks, named by measurement not inference.** The frozen census's provenance commit
is `c98707b91` (found by `git log -S'1384' -- tests/architecture/test_static_quality_ratchet.py`),
not the 2026-08-06 freeze date the header assumed — the entry has been re-frozen twice since
(1386 -> 1385 -> 1384) as the ratchet's own history block records. Per-file I001 census of a
`git archive` extraction of `c98707b91` diffed against one of HEAD `702b2a8fe`, both counted with
the real config (`python3 -m ruff check . --output-format=json`, no `--select` — a bare
`--select I001` reports 1387 because it discards the configured per-file-ignores, which is itself
worth knowing before anyone re-measures this):

```
TOTAL 1384 -> TOTAL 1386
+ 1 tests/background/test_rest_ladder_isolation.py
+ 1 tests/tools/test_measure_publish_gate_subject_cost.py
```

Exactly two gainers, one violation each, and no other file moved.

**2. Fixed at source, baseline untouched.** `ruff check --select I001 --fix` on those two paths
only. The whole diff is one blank line and one swapped `import time`/`import types` pair. The
frozen census is NOT in the commit — grep the diff and there is no `1386`.

**3. Green.** `tests/architecture/test_static_quality_ratchet.py` — 13 passed. Both named tests
(`test_ruff_no_rule_exceeds_baseline`, `test_ruff_baseline_matches_frozen_census`) pass, and so
does `test_ruff_no_stale_baseline_entries`, so this is a real return to 1384 rather than a
sideways drop left unrecorded — the 2026-08-09 episode-3 failure mode.

**Both files were UNMODIFIED in the working tree.** `git status --porcelain` on the two paths was
empty before the fix. The finding's central claim — that a 270-file dirty tree was innocent and
the committed tree was the offender — reproduces exactly.

### Step 4 is NOT closed here, and that is deliberate

"What would have caught the drift at the commit that caused it?" has an answer, and it is already
filed as its own atom rather than being answered inline: this is the same tree-vs-commit gap as
`WORKER_FINDING_THE_PRECOMMIT_GATE_VALIDATES_THE_TREE_NOT_THE_COMMIT_2026-08-09`. The ratchet is
green in a tree where the offending file is either absent or already fixed by in-flight work, so
it passes at commit time and reds at HEAD. `tools/surgical_land` — which gates the tree the commit
WOULD create, and which landed this very fix — is the built half of that answer; what is missing
is that nothing REQUIRES its use. Left queued as the control question, not marked answered.

### Wedge status after this fix

This closes ONE red at HEAD. It does NOT on its own prove the gate green: the gate runs `-x`, and
`tests/architecture/` sorts near the front of collection, so this failure has been masking
everything behind it for the whole 123-failure episode. A full gate run against a clean checkout
of `750cdff15` is the only thing that settles it, and its result is recorded separately.
