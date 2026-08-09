# Surgical landing — why hook-bypass is a wall, and what the legal move is

**Atom:** `OPS4_surgical_landing_tool` · **Tool:** `tools/surgical_land.py` ·
**Contract:** `tests/tools/test_surgical_land.py` ·
**Ruling:** `docs/staging/done/DIRECTOR_RULING_HOOK_BYPASS_IS_A_WALL_2026-08-09.md`

---

## The rule

**`--no-verify`, `git commit-tree` by hand, and every other form of stepping past the
pre-commit hook is a WALL. Never a judgment call, whatever the merge shape.**

Not because bypassing is always wrong in the abstract, but because *deciding* it is
right requires exactly the judgement that is hardest to make well at 21:00 on a wedged
tree, and the record of this project is unambiguous about what happens next: every rule
that survived here was a mechanism, and every rule that decayed was an exhortation
(`MAKE_IT_STICK`). A wall you can always obey is a mechanism. A wall you sometimes
cannot obey is an exhortation with extra steps.

## Why a rule alone would not have held

On 2026-08-09 the acting seat was landing an orphan lane's residue and had **two sins and
no third option**:

* `git merge` — correct in form, but 35 paths of *other lanes'* staged work sat in the
  shared index, and the merge commit would have swept them into an unreviewed commit.
* a `git commit-tree` construction — surgical in scope, but it stepped past the hook.

It chose the second, disclosed it in the commit message, gated both parents
independently, kept the content docs-only, and asked for the rule. The ruling retroactively
sanctioned exactly that shape as a **single interim exception** (all four conditions
required together) and then said the important part: **the class closes by mechanism, not
by exception.**

The bypass was a **missing tool**, not a discipline failure. Issuing the rule without the
tool would have left no legal move on a dirty shared tree — and a rule with no legal move
does not get obeyed, it gets forgotten.

## The second defect, closed in the same move

`tools/pre_commit_test_gate.py` **selects** tests from the index (`git diff --cached`) and
**runs** them in the **working tree**. Those two scopes are equal except in one case — a
partial commit — and a partial commit is the *routine* case here, because CLAUDE.md's own
recommended discipline on this shared tree is to stage a precise pathspec
(`git commit -- <paths>`).

The cost, measured the same day: HEAD asserted an epistemic wall that HEAD's own code
violated. The allowlist shrink (one test file, cheap to stage) landed; the seventeen files
that made the shrink *true* did not. The working tree was green in both directions, the
gate admitted the commit, and the publish gate wedged for ~112 minutes on a tree no test
had ever been run against
(`WORKER_FINDING_THE_PRECOMMIT_GATE_VALIDATES_THE_TREE_NOT_THE_COMMIT_2026-08-09.md`).

So the subject of the gate here is **neither the index nor the working tree**. It is a
clean extract of the **resulting tree** — the tree HEAD would become if exactly the named
paths were committed. Selection and execution finally share one scope.

## The legal move

```
python3 -m tools.surgical_land -m "<message>" -- <path> [<path> ...]
python3 -m tools.surgical_land --verify <commit-ish>
```

What it does, in order:

1. **A throwaway index** (`GIT_INDEX_FILE`), seeded `read-tree HEAD`, then `git add` for
   the named paths only. The caller's real index is never opened, so another lane's staged
   work cannot be read, moved, or swept in.
2. **`git write-tree`** on it → the resulting tree sha. This is the thing being judged.
3. **A standalone extract** of that tree: `git archive | tar -x`, then `git init`, an
   `objects/info/alternates` line lending the real object store read-only, `.git/HEAD` set
   to the parent, `read-tree` of the parent, and `git add` of the named paths. The result is
   a repo where `git diff --cached` is exactly this commit and the working tree is exactly
   the resulting tree.
4. **The repo's own `tools/git-hooks/pre-commit`**, run in that extract with `GIT_*`
   scrubbed. Not a re-implementation and not a subset: the same test gate, level-promotion
   gate, site-lane gate, coherence gate, archive-question gate, consolidation rhythm and
   size ratchet a `git commit` would face — against the right tree this time.
5. On green, under `tree_lock`, a **compare-and-swap**: refuse if HEAD moved while the gate
   ran, else `commit-tree` + `update-ref HEAD <new> <parent>`, then refresh the real index
   for exactly the landed paths.
6. **A receipt** in the commit message naming the parent, the tree, the path list, the gate
   command and its rc.

## Design notes worth not re-litigating

**Why the tool is allowed to `commit-tree` when the rule forbids it.** The wall is against
committing *ungated*. This tool's `commit-tree` is preceded by the whole hook, run against
the exact tree being committed — which is strictly *stronger* than what the hook itself
checks, because the hook checks the working tree. "Bypass" ceases to exist as a concept
not because the rule got sterner but because the check now always runs.

**Why `git archive` and not `git worktree add`.** A registered worktree survives this
process being SIGKILLed (rc=-9 is a known outcome here) and leaves state in the real repo.
The archive form leaves nothing: deleting the tmpdir deletes every trace.

**Why the extract is a real repo and not a bare file tree.** A checkout with no `.git`
fails every history-reading test with `fatal: not a git repository` — a failure about the
harness, not the code, arriving at the same exit code as a real red. That R10 lesson was
already paid for once in the publish gate; this ports the fix rather than re-learning it.

**Why the real index is refreshed for the landed paths.** Not doing so is not neutrality,
it is corruption: the index would still hold the *parent's* content for those paths, so
`git status` would show the landing as a staged revert and the next commit would undo it.
The post-state is exactly what `git commit -- <paths>` leaves. Every entry outside the
landed set — including another lane's staged work — is byte-identical, and the contract
asserts that at the blob level rather than asserting it in prose.

**Why the compare-and-swap.** On a tree with several concurrent writers, HEAD can move
while the gate runs, and a commit whose parent moved was gated against a tree that no
longer exists. It refuses and says so; it does not guess.

## Fail-closed, everywhere

No commit is created if the hook is missing or unreadable, the extract cannot be built or
made a real repo, tmp has less free space than the extract needs, the hook exits non-zero,
HEAD moved, or the resulting tree is identical to HEAD's. **An unavailable check is a
FAILED check** (R15) — and here that direction is the one that matters: a landing tool that
quietly commits when its own gate is missing launders an ungated commit as a gated one,
which is *worse* than the bypass it replaces.

## What the receipt can and cannot prove

Three claims in the receipt are independently re-derivable from the object store — the
tree sha, the parent sha, and the exact set of files the commit changes — so
`--verify` can **falsify** a receipt hand-written onto a commit it does not describe, or
one understating what its commit carried. Exit codes: `0` consistent, `1` **falsified**,
`2` no receipt (deliberately distinct — "not made with the tool" and "lying about it" are
different facts and must not collapse into one code).

It does **not** prove the gate was green at the time; nothing can, after the fact. It
proves the receipt is *about this commit*, which is what makes the claim falsifiable
rather than merely present.

## R15 — the control can fail, and it is proven to

`tests/tools/test_surgical_land.py` runs against a real throwaway git repo (a mocked git
would prove nothing about index isolation, tree construction, or ref CAS, which is what
every property here is). Ten named source mutations, each killed by its own test:

| mutation | caught by |
|---|---|
| gate rc ignored | red-gate and partial-landing refusals |
| missing hook returns green | `test_a_missing_gate_refuses_rather_than_landing_ungated` |
| no compare-and-swap | `test_head_moving_under_the_gate_refuses...` |
| index not refreshed for landed paths | `..._so_the_next_commit_does_not_revert_them` |
| overlay symlinked before staging | `test_the_untracked_overlay_is_symlinked_AFTER_staging...` |
| extract not made a real repo | `test_the_gate_runs_in_a_real_repo...` |
| `verify` ignores tree / parent / path set | three single-lie forgery tests |
| no-receipt collapsed into falsified | `test_verify_reports_no_receipt_distinctly...` |

The centrepiece is
`test_a_partial_landing_is_gated_on_the_commit_not_the_working_tree`: the 2026-08-09 wedge
in miniature — a two-part change whose committed half is red and whose working tree is
green. It asserts its own premise (the working tree *is* green) before asserting the
refusal, so it cannot pass vacuously, and it is the one test a tool that merely shelled out
to `git commit -- <paths>` would fail.

**Two edits that survived mutation and are documented as equivalent rather than claimed as
controls** (R15's tautology direction, applied to this tool's own tests): dropping `-A`
from the throwaway-index `git add`, and dropping the pathspec from the extract's `git add`.
A pathspec'd `git add` has covered removals since git 2.0, and the extract's index is the
parent while its working tree is the resulting tree, so `add -A` there stages the same set
either way. Both are written for the reader, not for the machine, and say so in the source.

## Retirement of the interim shape

The ruling's sanctioned interim bypass (`d6f894b6e`, four conditions required together)
expires with this tool. That retirement — and the CLAUDE.md wording that goes with it — is
`OPS5_retire_the_interim_bypass_shape`, deliberately a separate atom so this one does not
edit the rulebook it is the mechanism for.
