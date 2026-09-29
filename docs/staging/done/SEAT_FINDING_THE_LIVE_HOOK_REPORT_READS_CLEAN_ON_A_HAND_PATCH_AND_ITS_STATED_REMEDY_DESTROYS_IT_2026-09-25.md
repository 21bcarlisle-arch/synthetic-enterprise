# The live-hook report reads CLEAN on a hand-patch, and the remedy it prints is what destroys it

*Filed 2026-09-25 by the delivery seat, from the drawn item
`the-shared-hooks-checkout-is-a-mixture-not-a-snapshot-and-its-ahead-leg-cannot-promote`.*

**Class:** `controls_that_cannot_fail` — the control is at its greenest in the condition it exists to
catch, because a hand-patch reproduces the reference bytes without changing the checkout.

**Lane:** `H_harness`

**Severity:** RECORDED. `tools/live_hook_drift.py` reports honestly about BYTES and is not
wrong about anything it claims. The defect is in what its verdict is read to MEAN, and in the
one fixed sentence it prints as the remedy.

---

## The item's premise was a diagnosis nobody had run the control for, and it is refuted

The item says the shared tree's `tools/git-hooks/` "is now a MIXTURE of revisions rather than a
snapshot of any commit", having gained `hook_gate_mark` "WITHOUT the checkout advancing", and asks
why. Measured on the shared tree at 2026-09-25, real bytes:

    git hash-object tools/git-hooks/pre-commit  -> 84a04326dd7770ddb870587b523654c28b77db1e
    git rev-parse HEAD:tools/git-hooks/pre-commit -> 84a04326dd7770ddb870587b523654c28b77db1e
    git ls-files -s tools/git-hooks/pre-commit    -> 84a04326dd7770ddb870587b523654c28b77db1e

Disk, index and HEAD are one blob. **It is not a mixture and it is a snapshot of exactly one
commit.** The ahead/behind figures the item quotes (7/49, then 8/50) are also gone: the shared tree
is 9 ahead and 2 behind, and `HEAD` is the merge `025b2793c` made at 01:46.

## Why the two files arrived, which is not a mystery and is written down

`git reflog` on the shared tree shows an ORDINARY `git commit` at 01:20:49 — `8e40bb205` — four
minutes after the hooks' mtime of 01:16. Its own commit body says what happened, in its author's
words:

> REMEDY, and why it was safe: the three paths were written from origin/main's blobs to disk with
> `git cat-file blob`, index untouched — not `git checkout -- <path>`. […] The hook files are
> deliberately NOT in this commit's pathspec […] They stand as working-copy changes that the
> checkout will reconcile when it advances.

So a lane **hand-forward-ported the hooks working copy from `origin/main`'s blobs** and left it
uncommitted on purpose. No daemon, no partial checkout, no corruption. The "mixture" reading was an
inherited diagnosis whose cause was never tested against the commit that made it.

## The actual defect, which is sharper than the one the item names

The hand-patch is invisible to the control that exists to watch this directory, in BOTH directions:

1. **While the patch is in place, `live_hook_drift` reports the chain is `origin/main`'s "byte for
   byte" — its cleanest possible verdict.** The patch is bytes from `origin/main`, so of course it
   matches. But the underlying condition — a checkout 49 behind, running gates only because a human
   pasted them in — is untouched, and the report has no way to say so. A control keyed to today's
   answer, exactly.

2. **The advance then silently reverts it, and the report recommends the advance.** `report()` ends
   with one fixed sentence: *"the remedy is the reconciler advancing the SHARED checkout."* When the
   live copy is a hand-patch AHEAD of `HEAD`, that advance is not the remedy — it is what throws the
   patch away. That is what happened here: patched 01:16, gone by 01:46, 30 minutes, and the only
   record anywhere is a paragraph in an unrelated commit's body.

A third state exists and is worse than both: bytes belonging to **no commit at all** (a real
hand-edit). No git operation reconciles that; the next checkout conflicts or clobbers, and the
report would call it "differs from origin/main" in the same words it uses for ordinary staleness.

**Three conditions, three opposite remedies, one verdict.** Telling them apart took three commands
this turn (`hash-object`, `rev-parse HEAD:`, and a `rev-list` scan for the blob) and no tool in the
tree does it.

## Pre-registration, written before the control was built

Filed before `live_provenance()` existed, so it can refute me:

* **P1.** Run over the shared tree today, the new leg returns `SNAPSHOT`, naming a commit that IS an
  ancestor of `HEAD` — because disk, index and HEAD are already one blob. A `MIXTURE` verdict here
  would mean my reading above was wrong.
* **P2.** The old report's fixed remedy sentence survives ONLY in the `SNAPSHOT`-of-`HEAD` case. In
  the other two the sentence must change, so any control pinned to the old literal goes red — and if
  none does, the sentence was never controlled and that is itself the finding.
* **P3.** The 01:16 state is reconstructible in a fixture: a hooks copy whose bytes are a commit NOT
  reachable from `HEAD`. If I cannot build that state, the second condition above is not real and
  this note is wrong.

## What is NOT fixed by this, and stays true

`6a422ea0f` carries neither a `surgical_land` receipt nor a hook-gate mark, and one receiptless
commit makes the whole 9-commit ahead leg unpromotable. Nothing in this turn changes that, and the
provenance leg does not pretend to. It is named here so the next reader does not re-derive it.

`tools/live_hook_drift.py` does not exist in the shared tree at all — `python3 -m
tools.live_hook_drift` there is `ModuleNotFoundError`. The reporter cannot run in the tree it
grades until the checkout advances the 2 commits. That is the honest shape of "MISSING
live_hook_drift": the reporter naming its own absence, and it is ordinary staleness, not the
mixture.

---

## Results, against the predictions above

**P1 — CONFIRMED, but only after the first draft was refuted.** Run over the shared tree the leg
returns `head`, naming `025b2793c`, which is the shared tree's own HEAD. The *first* draft returned
`behind`, naming `934343669`. Both readings were of the same bytes; the difference was that the
draft asked `HEAD` of **the caller's** tree. `core.hooksPath` is an absolute path into the shared
tree and resolves to it from every worktree, so a provenance leg rooted at the caller asks about
one checkout and answers about another's working copy — and it told this seat that `git status`
would show the path as modified, which was false in both trees at once. Caught by printing the
verdict from this worktree before writing the test, not by thinking about it.
`live_provenance` now redirects every git question to `owning_checkout(live_hook)`.

**P2 — CONFIRMED, twice.** Two assertions in `test_live_hook_drift.py` were pinned to literals from
the old fixed remedy sentence (`"reconciler" in text`, `"restart" in text`) and both went red the
moment the remedy became conditional — a control reddening because the code got *more* honest,
which is the wrong direction. Corrected in place, beside the claim: the first is now keyed to the
property (a fault is never published without something to do about it, and a path that cannot know
the remedy must say so), and the two never-dos moved to the differs branch, where they are true in
every provenance state rather than inside the one whose remedy happens to be the advance.

**P3 — CONFIRMED.** `_provenance_repo` builds all four states over one repo from three real
revisions, and `test_all_four_provenance_states_are_reachable_over_ONE_repo_and_none_collapse`
asserts the four labels are *four* rather than checking each one separately — a partition control
over the whole partition, because four per-state tests are all green against an implementation
where two of the states are one state.

## The second defect, found after the report was already right

`surgical_land`'s door — the one call site with a reader — returned early on `verdict.clean`. **A
working copy hand-patched from the trunk is clean by construction**, so the door printed *nothing
at all* in the condition the whole leg exists to surface. The qualification was reaching `report()`
and dying one frame above it. `Drift.needs_reader` replaces `clean` at that call site: only a
snapshot of HEAD is quiet.

## Mutation evidence, eight run, each red on the leg written for it

| Mutation | Red |
|---|---|
| collapse `PROV_OFF_HEAD` into `PROV_BEHIND` | the partition control |
| drop the `owning_checkout` redirect | the linked-worktree differential |
| drop the scan-budget check | the fail-closed control |
| drop `provenance_lines` from the byte-identical return | the hand-patch control |
| delete the two never-dos | the report control |
| `needs_reader` → `not self.clean` | the door-silence control |
| `needs_reader` → `True` | the door-silence control (the quiet arm) |
| the door asks `verdict.clean` again | the wiring control |

The two `needs_reader` mutations red the same test from opposite directions, which is why its quiet
case is asserted rather than trusted: a door that speaks on every landing is a door nobody reads,
and this module has already paid for that mistake once (`b0640e478`).
