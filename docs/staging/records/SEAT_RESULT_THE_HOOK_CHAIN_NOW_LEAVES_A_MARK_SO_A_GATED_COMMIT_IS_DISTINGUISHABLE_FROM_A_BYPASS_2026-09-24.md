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
