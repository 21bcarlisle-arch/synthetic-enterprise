**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the PROJECT_DIR-as-git-cwd census) · **Class:** controls_that_cannot_fail

# PRE-REGISTRATION — which `PROJECT_DIR`-as-git-cwd callsites actually ask the wrong tree

**Written 2026-09-09, before any callsite was classified.** The population below is already
measured and is stated as fact. Everything under "predictions" is filed so the classification can
refute it.

Commissioned by the Lane 0 delivery item
`promote-the-09-08b-value-arms-pair-once-its-floor-lands`, whose "ALSO OWED" clause reads:

> 29 modules in `background/` and `tools/` run git with PROJECT_DIR as cwd while only 6 carry the
> `shared_tree`/`shared_tree_dir` fix. `seat_continuation` learned it on 2026-09-04 and
> `origin_reconcile` was missed until today, which is one legal rule with 29 implementations and
> two of them right. A census of which of those 29 are ever invoked from a linked worktree AND ask
> a question about the shared tree is the next instance of the VAT shape.

---

## What is already measured (fact, not prediction)

**The item's "29" does not reproduce, and it is an UNDERCOUNT.** An AST scan over `background/`
and `tools/` for `subprocess`-family calls carrying `cwd=<module-root constant>` — where the root
constant is any module-level name bound to a `Path(__file__)…parent` chain (`PROJECT_DIR`,
`PROJECT`, `ROOT`, `REPO_ROOT`, `_REPO_ROOT`) — returns:

- **44 modules, 79 callsites.**

My own first scan returned **11 modules**, and it was wrong in the way this project keeps being
wrong: it split the `cwd=` expression on `.` and `/` and so matched `PROJECT_DIR` but was blind to
`str(PROJECT_DIR)`, which is the majority spelling. That is
[the aimed-left shape](../../docs/staging/) again — a scope regex matching the concept as *one*
spelling is blind to the same concept spelled another way. Recording it because the 11 would have
been published as the population if I had not widened it.

## The correction that matters to the classification

**In a linked worktree, most of git is ALREADY shared.** The object store and the ordinary refs
live in the *common* dir, so `git log origin/main`, `git rev-list origin/main` and `git cat-file`
return the *same answer* from a linked worktree as from the main tree. What is per-worktree is
narrow and specific: `HEAD`, the index, the working tree, and per-worktree refs.

So "asks a question about the shared tree" is not the discriminator. The discriminator is:

> Does this callsite read **per-worktree state** (`status`, `diff`, `add`, `commit`, `stash`,
> `ls-files`, `rev-parse HEAD`) while the question it is *actually asking* has the **main worktree**
> as its true subject?

A gate that runs `git status` to gate *the commit being made here* is **correct** and must not be
counted — `pre_commit_test_gate` is the clearest case. `origin_reconcile` was a defect because its
question ("is the publisher behind?") is about a tree it was not running in.

## Predictions

Filed before classifying. Scored in the result document.

1. **Most callsites are per-worktree readers.** I predict **more than 50 of the 79** issue a
   subcommand whose answer differs between a linked worktree and the main tree.
2. **The hazard class is much smaller than the population.** I predict **fewer than 15 callsites**
   are both (a) per-worktree readers and (b) in a module reachable from a linked worktree whose
   question's true subject is the main tree.
3. **At least one NEW live defect of the `origin_reconcile` class exists** — a module that today
   reports about the wrong tree from a worktree, not yet known and not yet fixed.
4. **The "only 6 carry the fix" figure will not reproduce either**, because two of the six are
   `shared_tree` (fails closed to `None`) and `shared_tree_dir` (fails **open** to `project_dir`)
   — two implementations with *opposite* failure semantics, each locally correct. I predict the
   count of modules that genuinely resolve the main tree is **fewer than 6**.
5. **The correct remedy is NOT to fix all 44.** I predict the majority are correct as written and
   that a blanket `shared_tree()` sweep would introduce defects rather than remove them.

## What would refute each

1 is refuted by 50 or fewer per-worktree readers. 2 is refuted by 15 or more in the hazard class.
3 is refuted by every per-worktree reader in the hazard class turning out to be already-fixed or
already-correct. 4 is refuted by six or more modules resolving the main tree. 5 is refuted by a
sweep being safe — i.e. by no callsite existing whose correct subject is its *own* tree.

## What this does NOT claim

It does not claim the 44 are defects. It does not claim the hazard class is currently *firing*.
Reachability from a linked worktree is asserted per module in the result and not assumed from the
fact that a worktree exists.
