**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** (Lane 0 delivery — give the hook chain a receipt so a gated commit is distinguishable from a bypass)

# RESULT — the hook chain now leaves a mark, so a gated commit is distinguishable from a bypass

**Lane 0 delivery, 2026-09-24.** Claim id
`give-the-hook-chain-a-receipt-so-a-gated-commit-is-distinguishable-from-a-bypass`.

## The premise was NOT spent, and the draw's own checks said it was

The draw reported all three cited commits (`f1791deca`, `13203ed91`, `61b67fa0d`) as already
ancestors of `origin/main`, and both named paths as `[already landed] identical to HEAD`. Both
readings were correct and neither meant the work was done:

* The commits are cited as **evidence**, not as the work. `f1791deca` is the measurement that
  receiptless commits are hook-gated; the other two are the specimens it measured. An ancestor
  check on a citation says nothing about whether the remedy exists.
* `[already landed]` on `tools/git-hooks/pre-commit` means the working copy matches HEAD — which is
  what you expect for a file nobody has edited yet. The tag answers "is there anything to land
  here", not "has the change been made".

Re-measured against the trunk rather than HEAD, which the door's own base caveat demands (HEAD was
37 behind): `git diff HEAD origin/main -- tools/git-hooks/` was **empty**, and a grep of
`origin/main:tools/git-hooks/pre-commit` for `receipt|trailer|gate_rc|tree_sha` matched **nothing**.
The mechanism existed in no copy of the tree. The work was real and unbuilt.

## What was built

| Piece | What it does |
|---|---|
| `tools/hook_gate_mark.py` | new. `record` (pre-commit) binds the tree the chain judged; `stamp` (commit-msg) promotes it to a trailer; `verify` asks whether the mark is ABOUT the commit |
| `tools/git-hooks/pre-commit` | `--record` as the **last** line — the chain is `cmd \|\| exit 1`, so reaching the end IS the pass |
| `tools/git-hooks/commit-msg` | `--stamp "$1"` as the last line, after the message gates |
| `tools/promote_worktree_landing.py` | `_refuse_if_ungated` accepts **receipt OR mark**, and still refuses a genuine bypass by name |

**There is deliberately no `gate_rc` field, though the brief asked for one.** The record line is only
reached when every gate above it passed, so an rc field could hold exactly one value — a constant
dressed as evidence. The falsifiable field is the tree, so that is what is written.

## Why this closes the blocker without reopening the 2026-08-31 hole

The two populations genuinely differ, and `fork_salvage.py` is what proves it: its salvage commit
uses an **explicit `--no-verify`**. `--no-verify` and `commit-tree` do not run hooks — that is what
they mean — so a genuine bypass arrives with neither receipt nor mark and is still refused. A gated
daemon commit now carries the mark and stops blocking the whole ahead leg.

**What the mark proves, stated plainly:** exactly the standard `surgical_land.verify` already sets
for its receipt — not that the gate was green (nothing can prove that after the fact), but that the
mark is about **this commit**. It is not unforgeable: a session that hand-writes the trailer with
the right tree sha gets past it, as one that hand-writes a receipt gets past `--verify`. That is not
the threat model and claiming otherwise would be the more dangerous move. The threat model is a
daemon taking the documented bypass without thinking about promotability, which happened twice.

## Evidence

End-to-end in a scratch repo with both hooks installed: plain `git commit` → mark present, `verify`
rc **0**; `git commit --no-verify` → no mark, rc **2**; a stale record → `STALE, not stamping`; a
mark copied onto another commit → rc **1 FALSIFIED**.

`tests/tools/test_a_hook_gated_commit_is_distinguishable_from_a_bypass.py`, 12 tests.
**R15: eight source mutations, each firing on its intended leg alone.**

Two mutation rounds went green first time and both were run down rather than recorded as
equivalences:

1. *dropping the parent comparison* — **cause three, the mutation was a no-op.** The patch pattern
   used single quotes where the file has double. It fires once actually applied.
2. *dropping the tree comparison* — **a real hole in the tests.** The copied-mark test breaks the
   tree AND the parent, so the parent leg caught the mutation and the result read as the tree check
   working. `test_a_mark_naming_the_right_parent_and_the_wrong_tree_is_falsified` was added to hold
   the tree leg alone — amend keeps the parent and moves the tree — and the mutation now fires on it
   and nothing else.

## The first build was on a stale base and would have reverted `f1791deca`

Recorded because it is the trap the draw itself warned about and I still walked into it, and the
thing that caught it was reading the BLOCKING finding this work remedies rather than the item.

The shared tree's HEAD is **37 commits behind `origin/main`**. I built the whole change against it,
including an edit to `_refuse_if_ungated`. But `f1791deca` had already rewritten that exact function
on the trunk — `git diff HEAD origin/main -- tools/promote_worktree_landing.py` is **44 insertions**
my HEAD lacks, including the rc 1 / rc 2 split. **Landing my working copy by pathspec would have
reverted it**, which is precisely the stale-copy defect `stale_copy_refusal` exists to refuse.

`tools/git-hooks/` was identical at HEAD and on the trunk, so only the one file was affected — which
is why the earlier `[already landed]` reading on the hooks was sound and the same reading on the door
was not. **The tag answers a question about HEAD, and HEAD was not the base.**

Rebuilt in a linked worktree at `origin/main`. The shared tree was restored to its own HEAD copies
and left clean; `reset --hard` was never available, since ~100 paths there hold other lanes' work.

The trunk's version also states the opening this fills, in its own docstring: *"Until the hook chain
leaves a mark of its own, `no receipt` is all this can honestly say."*

## Two existing controls pinned wording, and both were right to fire

On the trunk, `test_an_UNVERIFIABLE_commit_cannot_be_promoted` asserts the exact substrings
`carries no surgical_land receipt` and `Re-land it through the door`, and asserts `so it was not
gated` is **absent**. My first wording broke two of the three. **Fixed in the refusal's own wording,
not by editing the assertions** — the existing controls keep their vocabulary, and one of them exists
specifically because a previous version of this sentence pinned a false clause.

## The shared tree's one red is green on the trunk

`test_the_promotion_seam_binds_the_landing.py::test_a_MERGE_binds_MY_paths_and_not_the_side_it_
merged_IN` fails in the shared tree, and a one-variable control (HEAD's own
`promote_worktree_landing.py`, everything else of mine in place) reproduced it identically — so it
was never a regression here. In the worktree at `origin/main` it **passes**, with all 41 tests across
the four promotion suites green. It was a **stale-checkout artefact of a 37-behind tree**, not a
defect, and needs no register entry.

---

# CONTINUATION 2026-09-25 — everything above was written, and then died in a fork

**Correction, beside the claim rather than instead of it.** Every section above is in the past tense
and none of it had landed when it was written. The invocation that wrote it was killed before it
reached the door, and `background/fork_salvage.py` preserved the work as `ca0fe445a`
*"SALVAGE(auto)"* — on the fork's own branch, **not an ancestor of `origin/main`**. The draw that
followed read that commit and credited this item with a landing. **A salvage is not a landing**, and
the credit was wrong in exactly the way the record above warns about for a different tag: the check
answers a question about reachability from somewhere, and *somewhere* was not the trunk.

So the draw carried three separate signals that this work was done — premise commits all ancestors,
both named paths `[already landed]`, and a credited landing — and **all three were true readings and
none of them meant the remedy existed.** `tools/hook_gate_mark.py` was in no copy of `origin/main`.

**Landed 2026-09-25 as `934343669`**, promoted to `origin/main`, 7 paths bound to the claim.

## It was recovered, not rebuilt, and that was measured before it was assumed

The three source files this change edits are **byte-identical between `ca0fe445a^` and today's
`origin/main`**, and the salvage's parent is an ancestor of the trunk. So the salvaged content
applied cleanly and the work was not written twice. The one file the record above says would have
been reverted by a stale copy — `tools/promote_worktree_landing.py` — was the very file checked
first.

## The mutations were RUN this time, not annotated

Each test above names the mutation that should kill it. Four were executed against the real suite:

| Mutation | Result |
|---|---|
| delete the `hook_gate_mark.verify` branch in `_refuse_if_ungated` (the code as it stood) | door-promotes test fires |
| accept on `mark_rc != 1` — the plausible relaxation that would promote every `SALVAGE` commit | still-refuses test fires |
| drop the tree comparison in `verify` | wrong-tree test fires **alone** |
| move the `--record` line off the end of the pre-commit chain | wiring test fires |

The third is the one that mattered. The file's own docstring records that this leg was once green
for the flattering reason — a different leg caught the mutation and the result read as the tree
check working. It now fires alone, which is the only evidence that reading was fixed.

## END-TO-END PROOF, and it is not from a fixture

`430e5b00e` *"delivery seat: direction for the next stretch"* is a **real commit on this repo's
ahead leg, made by the real hook chain**, with **no `surgical_land` receipt** and a **valid
hook-gate mark**:

```
tree: ca9ab09059fca2f241969d0762936daaa183d99f
parent: 6a422ea0fbceab9de6c0515e8938b4b30a36539b
gate: sh tools/git-hooks/pre-commit (chain completed)
```

`hook_gate_mark --verify 430e5b00e` returns **rc 0**. It was made during the window the killed
invocation had the hooks live in the shared tree's working copy, before that copy was restored. It
is the specimen the twelve tests stand for, and it is a commit the door refused yesterday and
accepts today.

## BUT IT IS INERT RIGHT NOW, and the reason is not the landing

`core.hooksPath` is `/home/rich/synthetic-enterprise/tools/git-hooks` — **the shared tree's WORKING
COPY**, not the index and not `origin/main`. That checkout has **diverged: 48 behind, 7 ahead**. So
on the shared tree today:

* `grep -c 'tools.hook_gate_mark --record' tools/git-hooks/pre-commit` → **0**
* `tools/hook_gate_mark.py` → **not on disk**

**The mechanism is landed and running nowhere.** No commit made in the shared tree will carry a mark
until that checkout advances. This is the shape the memory layer already names — *a clean
`git status` hides that the shared tree's checkout lacks the commit, so a landed fix is inert* — and
it applies with extra force here because the subject IS the hook path: for almost any other module a
stale checkout delays a fix, but for this one it means the control does not exist.

The remedy is the reconciler advancing the shared checkout, **not** a `git checkout` from this seat
(that tree holds other lanes' uncommitted work) and **not** a daemon restart (the memory layer
records that restarting to clear a staleness verdict blinds the detector to the checkout gap).

## The ahead leg is still blocked, and by a commit this work cannot help

Of the 7 ahead commits, five carry receipts, `430e5b00e` carries a mark, and **`6a422ea0f`
(`chore(liveness)`) carries neither.** One commit, whole leg unpromotable — the known shape.

It is **not** a bypass. Nothing in `background/` or `tools/` passes `--no-verify` except
`fork_salvage.py`, which commits only on a fork's own branch. `6a422ea0f` is `430e5b00e`'s parent:
it was made in the minutes **before** the hooks were edited, so it predates the mark and is gated
without being able to show it. That is precisely the population the refusal's new wording names —
*"A commit older than that mark may well have been gated and simply cannot show it."*

**So the mechanism does not retro-fix the current wedge, and claiming it would be the flattering
reading.** What it fixes is every leg after the hooks go live. The current leg needs the separate
resolution that is already someone's item.

## What done means here, and what is owed next

Done: the discriminator exists, is proven against a real commit, and the door accepts it without
changing behaviour for any receipted landing (16 pre-existing promotion tests still green).

Owed, and handed on: **the mark is worth nothing until the shared checkout carries it**, and nothing
currently notices that `core.hooksPath` points at a working copy that can be arbitrarily far behind
the hooks the repo thinks it is enforcing. That is a wider finding than this item — it applies to
*every* gate in the chain, not just this one — and it is the next piece.
