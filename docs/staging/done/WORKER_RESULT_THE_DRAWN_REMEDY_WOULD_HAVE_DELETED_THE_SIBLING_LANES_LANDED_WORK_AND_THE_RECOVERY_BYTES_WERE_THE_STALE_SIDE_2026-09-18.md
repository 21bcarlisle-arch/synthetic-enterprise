**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The drawn remedy would have deleted 143 lines of the lane that landed twenty minutes earlier, and the recovery bytes it named were the stale side

**Claim id:** `land-the-publisher-comment-repair-and-run-the-one-variable-width-check`
**Measured on:** local `HEAD` = `origin/main` = `5167f1281`, 2026-09-18 ~12:0x UTC.

---

## The headline

The item's remedy was: *"The bytes are recoverable three ways: commit `f690a6407`, ... Use
`surgical_land --content` so a rival's in-place edits are not read."*

All three recovery sources are **byte-identical** (md5 `077f4765...`) — and all three are the
**stale side of a fork**. `f690a6407` is **NOT an ancestor of `HEAD`**. Landing its bytes whole,
exactly as instructed, would have **deleted 143 lines** of `tools/generate_value_arms_data.py`.

| question | answer |
|---|---|
| `git merge-base --is-ancestor f690a6407 HEAD` | **NO** |
| merge base | `bcc42b47a` |
| `git diff --stat HEAD f690a6407` on the file | **46 insertions, 143 deletions** |
| what landed on HEAD since the fork | `5167f1281`, 2026-09-18 13:00:13 +0100 |

## What the 143 lines were

`5167f1281` — *"nine controls keyed to today's answer are re-keyed to their property"* — is the
**sibling lane's** work, landed under claim `republish-the-arms-decomposition-over-one-priced-book`
roughly twenty minutes before this item was drawn. It carries, in this same file:

- the staleness answer threaded into `_leg_over_its_own_family` as a **required** parameter (the
  thing that item was explicitly told not to make defaulted, because a defaulted one is the
  unreachable-mutation shape);
- `THE MEMBERSHIP CLAUSE IS READ BACK OFF THE PUBLISHED KEY`, which stops the summariser
  re-deciding a question its own block already answered;
- `TWO REASONS A SIDE IS WITHHELD, AND THEY READ NOTHING ALIKE`, which stops the page telling a
  reader that 5.1 errors from zero is "short of" a bar of 2.11.

`--content` writes **whole-file bytes**. The flag the item reached for *to protect against a rival's
in-place edits* is precisely the flag that would have destroyed that rival's **landed** work. The
protection it offers is against the working tree; it offers none against a stale source.

## The reusable class

**A recovery source named by an item is an un-re-asked prediction that it is AHEAD of HEAD, and
`--content` is the one landing route that cannot notice it is BEHIND.**

The pathspec route reads the working tree, which at least a human diff would catch. `--merge`
computes a real merge and would have conflicted or combined. `--content` is the only door that
takes bytes on trust — which is exactly why it is the right door for a contested file, and exactly
why the bytes handed to it must be re-based on HEAD first, never used as recovered.

This is the known *stale-and-holder-at-once* shape arriving through a new door: previously a
**working copy** was stale and holder at once. Here a **commit** is, and the item presented it as a
"real object, shared across worktrees" — which is true, and says nothing about its ancestry.

## What was actually landed

`HEAD`'s bytes with **only the three comment hunks** re-applied
(`~/.cache/se_next12/publisher_comment_repair.patch` applies to HEAD cleanly — `git apply --check`
passes). Verified before landing: all three repairs present, all three of `5167f1281`'s blocks
still present, module parses. The diff is 35 lines and **every one is a comment**; no executable
line changes.

The repair itself: `AUC_FAMILY_FLOOR_PATH` claimed to be `THE ONLY FAMILY IN THIS REPOSITORY`
carrying the per-seed discrimination AUC. `value_cycle_ab_s1_noise_floor_next12_20260917.json`,
landed in `8abbe4f2d`, carries `discrimination_auc` on all twelve of its seeds, so that sentence
had been **false on origin/main** since that commit. Narrowed to `ON THIS PAGE` — the claim the
constant actually needs, and one a later artefact cannot falsify.

## The one-variable run is launched, and the item's own framing of it was too narrow

Pre-registered in `PREREG_THE_ONE_VARIABLE_WIDTH_CHECK_SEPARATES_THE_INSTRUMENT_FROM_THE_SEED_SET_2026-09-18.md`
**before** launch. Seeds `3100001..3100012` at `4e7938f673`, running in
`/var/tmp/se-floorrun-20260910` — already checked out at that commit, `tools/run_value_cycle_ab.py`
byte-identical to it (md5 `9bd6cb02...`), and the same checkout the nine-seed `20260910` family was
drawn in. PID 2799364, launched 2026-09-18 ~12:07 UTC, ~16h expected.

**Why a worktree and not the shared tree:** the shared working copy of `tools/run_value_cycle_ab.py`
is **168 insertions / 468 deletions** from `HEAD` — still the stale-and-holder shape that
`WORKER_FINDING_THE_ROSTER_RUN_WOULD_HAVE_BEEN_INERT...` filed this morning, still unrepaired. A run
launched from the shared tree executes that copy. Separately, `producing_commit()` resolves
`git rev-parse HEAD` **at process start**, so only a checkout actually at `4e7938f673` stamps the
artefact honestly — a `git archive` extract would have stamped "cannot name its code".

**The item said the run separates instrument from seed set. Against the PUBLISHED 18 it does not,
because that family has no single instrument** — `folded18_single_arm_20260917` declares **no**
`producing_commit` at all and is spliced across three (`c066c114`, `4e7938f673`, `9f0ab066`). The
clean one-variable contrast this run buys is against the **nine** of `20260910` (n=9, mean -1749.47,
sd 1840.39), which is the only family that IS single-valued at `4e7938f673`. Stated here because the
result must not be read as grading the published 18 directly.
