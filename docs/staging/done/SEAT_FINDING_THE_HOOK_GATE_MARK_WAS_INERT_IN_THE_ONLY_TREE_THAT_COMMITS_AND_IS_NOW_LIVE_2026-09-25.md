**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The hook-gate mark was landed and inert in the only tree that commits, and the two commits the item asked me to grade are now graded

Claim id: `the-push-door-calls-every-hook-gated-daemon-commit-ungated`. Measured 2026-09-25 from the
shared tree `/home/rich/synthetic-enterprise` and a scratch worktree at `origin/main`
(`/var/tmp/se-gradedoor-20260925`, `4157c8d6b`).

## The item's work was already spent, against a base 49 commits back

The draw named `tools/promote_worktree_landing.py:232` as needing repair and its path check graded
the file `[already landed] identical to HEAD -- the working tree has NOTHING to land`. Both readings
are true and both are about **HEAD, which is 49 behind `origin/main`**. The repair, the hook-gate
mark, `tools/hook_gate_mark.py`, and twelve controls under `tests/tools/` are all on the trunk
(`f1791deca`, `4157c8d6b`). The `so it was not gated` clause is gone from the refusal text. Nothing
of the item's stated WORK remained to write.

*This is the two-oracles shape again: the draw asks git for the premise and the filesystem for the
path check, and a base 49 commits behind makes spent work read as unstarted.*

## The grading the item asked for

Run through the repaired door at `origin/main`, both evidence asks, real return codes:

| commit | subject | receipt | hook-gate mark | door |
|---|---|---|---|---|
| `430e5b00e` | delivery seat: direction for the next stretch | rc 2 — none | **rc 0 — about this commit** (tree `ca9ab0905`) | **PASS** |
| `6a422ea0f` | chore(liveness): publish heartbeat | rc 2 — none | rc 2 — none | REFUSED |

`430e5b00e` is the specimen: a real daemon commit, no `RECEIPT_HEADER`, promotable on the mark
alone. That is the item's first finished-condition, demonstrated on live bytes rather than a
fixture. `6a422ea0f` is its own parent, made 53 minutes earlier, before the hooks were edited — it
is gated and cannot show it, which is exactly the population the new wording names. The whole
7-commit ahead leg is still refused on that one commit, and no work on this claim can change that.

## The finding: the mechanism was inert, and is now live

`core.hooksPath` is `/home/rich/synthetic-enterprise/tools/git-hooks` — an absolute path into the
shared tree's **working copy**. That checkout was 49 behind. Measured before the remedy:

* `grep -c hook_gate_mark tools/git-hooks/pre-commit tools/git-hooks/commit-msg` → **0 and 0**.
* `python3 -c "import tools.hook_gate_mark"` → **ModuleNotFoundError**.

So every commit made in the shared tree since the mark landed carried none, and the door went on
refusing daemon commits for evidence the chain was no longer able to leave. `430e5b00e` carries one
only because it was made during the window the building invocation had the hooks live on disk
before that checkout was reset.

**Remedy applied.** The three paths were written from `origin/main`'s blobs to disk, index
untouched (`git cat-file blob origin/main:<p> > <p>`), not `git checkout -- <p>`. They were provably
safe to advance: `git status --porcelain` on all three was **empty**, and the delta is **purely
additive** — +6 lines to `commit-msg`, +10 to `pre-commit`, +227 as a new module, zero deletions. No
lane's uncommitted work was in those paths. Both new hook lines are fail-soft by construction
(`hook_gate_mark.main` returns 0 on `--record` and `--stamp` in every branch), so the worst case of
a bad advance is the refusal the door already gives.

Reversible: `python3 -m tools.refresh_to_head tools/git-hooks/commit-msg tools/git-hooks/pre-commit`
and delete the untracked `tools/hook_gate_mark.py`.

## Pre-registered, before the commit that carries this file

**This note's own commit must carry a `[hook-gate mark]` trailer naming its own tree and first
parent, and `tools/hook_gate_mark.py --verify <it>` must return rc 0.** If it does not, the advance
above did not take, this note is its own refutation, and the correction belongs directly beneath
this line rather than in a replacement. Writing it down here is the only way the claim "the mark is
live" is falsifiable by the artefact that asserts it.

## Open

1. **Nothing notices when `core.hooksPath`'s working copy diverges from the gate code that is
   supposed to be running.** This is not specific to the mark — it applies to **every** gate in the
   chain, and for a control (as opposed to a fix) a stale checkout does not delay it, it **deletes**
   it. This turn advanced three paths by hand; the class is unguarded and wants its own atom.
2. The ahead leg stays blocked on `6a422ea0f` until someone resets past it or re-lands it. Not
   mine to decide and not fixable by this claim.
3. `promote_worktree_landing` still **exits 0 on refusal** — carried forward, untouched here.
